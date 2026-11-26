import os

from dotenv import load_dotenv
from google import genai

from utils.config import (
    LIBRARY_DATA,
    SYSTEM_PROMPT,
    get_recommendations,
    manage_reading_list,
    search_books,
    track_reading,
)
from utils.parser import parse_array_parameter, parse_function_call


load_dotenv()

VALID_GENRES = {
    "fiction",
    "non_fiction",
    "mystery",
    "romance",
    "sci_fi",
    "biography",
    "history",
}
VALID_ACTIONS = {"add", "remove", "view"}
VALID_STATUSES = {"reading", "completed", "paused", "abandoned"}


def _integer_parameter(value, name):
    """Convert an integer-like parameter to an integer or raise a clear error."""
    if isinstance(value, bool):
        raise ValueError(f"{name} must be an integer")
    try:
        converted = int(value)
    except (TypeError, ValueError) as error:
        raise ValueError(f"{name} must be an integer") from error
    if isinstance(value, float) and not value.is_integer():
        raise ValueError(f"{name} must be an integer")
    return converted


def _format_book(book, book_id=None):
    genre = book["genre"].replace("_", " ").title()
    details = (
        f"{book['title']} by {book['author']}\n"
        f"Genre: {genre}, Pages: {book['pages']}, Rating: {book['rating']}/5"
    )
    if book_id is not None:
        details += f"\nID: {book_id}"
    return details


class LibraryAssistant:
    def __init__(self, api_key=None):
        self.api_key = api_key if api_key is not None else os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables.")

        self.client = genai.Client(api_key=self.api_key)
        self.model = "gemini-2.5-flash"

    def handle_function_call(self, function_name, parameters):
        """Validate and execute a parsed library function call."""
        if function_name == "search_books":
            query = parameters.get("query")
            if not isinstance(query, str) or not query.strip():
                return "Search query is required"

            genre = parameters.get("genre")
            if genre is not None:
                genre = str(genre).strip().lower()
                if genre not in VALID_GENRES:
                    return (
                        "Invalid genre. Valid genres: fiction, non_fiction, mystery, "
                        "romance, sci_fi, biography, history"
                    )

            try:
                max_results = _integer_parameter(
                    parameters.get("max_results", 10), "max_results"
                )
            except ValueError:
                return "max_results must be an integer between 1 and 20"
            if not 1 <= max_results <= 20:
                return "max_results must be between 1 and 20"

            result = search_books(query.strip(), genre, max_results)
            books = result["books"]
            if not books:
                return "No books found."
            details = []
            for book in books:
                book_id = book["book_id"]
                details.append(_format_book(LIBRARY_DATA["books"][book_id], book_id))
            return f"Found {result['count']} book(s):\n\n" + "\n\n".join(details)

        if function_name == "manage_reading_list":
            action = parameters.get("action")
            action = action.strip().lower() if isinstance(action, str) else ""
            if action not in VALID_ACTIONS:
                return "Invalid action. Valid actions: add, remove, view"

            book_id = parameters.get("book_id")
            book_title = parameters.get("book_title")
            if book_id is not None:
                book_id = str(book_id).strip()
            if book_title is not None:
                book_title = str(book_title).strip()
            if action in {"add", "remove"} and not (book_id or book_title):
                return f"Book ID or title required for {action} action"

            result = manage_reading_list(action, book_id or None, book_title or None)
            if action != "view":
                return result["message"]
            if not result["books"]:
                return "Your reading list is empty."

            books = []
            for book in result["books"]:
                books.append(_format_book(book))
            return f"Your reading list ({result['count']} book(s)):\n\n" + "\n\n".join(books)

        if function_name == "get_recommendations":
            raw_genres = parameters.get("genres")
            if raw_genres is None:
                return "At least one genre is required for recommendations"
            try:
                genres = parse_array_parameter(raw_genres)
            except ValueError:
                return "Genres must be a JSON-style array of strings"
            genres = [genre.strip().lower() for genre in genres]
            if not genres:
                return "At least one genre is required for recommendations"

            invalid_genres = sorted(set(genres) - VALID_GENRES)
            if invalid_genres:
                return f"Invalid genres: {', '.join(invalid_genres)}"

            favorite_authors = parameters.get("favorite_authors")
            if favorite_authors is not None:
                try:
                    favorite_authors = parse_array_parameter(favorite_authors)
                except ValueError:
                    return "favorite_authors must be a JSON-style array of strings"

            try:
                count = _integer_parameter(parameters.get("count", 5), "count")
            except ValueError:
                return "count must be an integer between 1 and 10"
            if not 1 <= count <= 10:
                return "count must be between 1 and 10"

            result = get_recommendations(genres, favorite_authors, count)
            if not result["recommendations"]:
                return "No recommendations found for those preferences."
            details = []
            for recommendation in result["recommendations"]:
                book_id = recommendation["book_id"]
                details.append(
                    _format_book(LIBRARY_DATA["books"][book_id], book_id)
                )
            return (
                f"Book recommendations ({result['count']}):\n\n"
                + "\n\n".join(details)
            )

        if function_name == "track_reading":
            book_id = parameters.get("book_id")
            if book_id is None or not str(book_id).strip():
                return "Book ID is required for tracking"
            book_id = str(book_id).strip()

            status = parameters.get("status")
            status = status.strip().lower() if isinstance(status, str) else ""
            if not status:
                return "Reading status is required"
            if status not in VALID_STATUSES:
                return "Invalid status. Valid statuses: reading, completed, paused, abandoned"

            rating = parameters.get("rating")
            if rating is not None:
                if status != "completed":
                    return "Rating can only be provided when status is completed"
                try:
                    rating = _integer_parameter(rating, "rating")
                except ValueError:
                    return "Rating must be between 1 and 5 stars"
                if not 1 <= rating <= 5:
                    return "Rating must be between 1 and 5 stars"

            pages_read = parameters.get("pages_read")
            if pages_read is not None:
                try:
                    pages_read = _integer_parameter(pages_read, "pages_read")
                except ValueError:
                    return "pages_read must be a non-negative integer"
                book = LIBRARY_DATA["books"].get(book_id)
                if pages_read < 0 or (book is not None and pages_read > book["pages"]):
                    return "pages_read must be between 0 and the book's total pages"

            result = track_reading(book_id, status, pages_read, rating)
            return result["message"]

        return f"Unknown function: {function_name}"

    def chat(self, user_input):
        """Ask Gemini for a function call or a conversational response."""
        fullprompt = f"{SYSTEM_PROMPT}\n\nUser: {user_input}\n\nAssistant:"
        try:
            response = self.client.models.generate_content(
                model=self.model, contents=fullprompt
            )
            response_text = response.text if response is not None else None
            if response_text is None or not response_text.strip():
                return "I didn't receive a valid response. Please try again."

            function_name, parameters = parse_function_call(response_text)
            if function_name is None:
                return response_text.strip()
            return self.handle_function_call(function_name, parameters)
        except Exception as error:
            return f"Sorry, I encountered an error: {error}"


def answer_library_query(query, assistant=None):
    """Convenient wrapper function for library queries."""
    try:
        if assistant is None:
            assistant = LibraryAssistant()
        return assistant.chat(query)
    except Exception as error:
        return f"Sorry, I encountered an error: {error}"


def main():
    """Main function to demonstrate the library assistant."""
    print("Book Library Assistant - Intermediate Function Calling")
    print("Type 'quit' to exit")
    print("=" * 55)

    sample_queries = [
        "Find me some mystery books",
        "Add The Great Gatsby to my reading list",
        "Recommend me some fiction and sci-fi books",
        "I finished reading book B001, give it 4 stars",
        "Hello! How can you help me?",
        "What makes a good book?",
    ]

    try:
        assistant = LibraryAssistant()
    except ValueError as error:
        print(error)
        return

    print("\n--- Sample Queries ---")
    for query in sample_queries:
        print(f"\nUser: {query}")
        print(f"Library: {answer_library_query(query, assistant)}")


if __name__ == "__main__":
    main()
