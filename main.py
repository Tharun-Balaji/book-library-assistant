import os
from dotenv import load_dotenv
from google import genai
# TODO: Import SYSTEM_PROMPT, search_books, manage_reading_list, get_recommendations, track_reading from utils.config
# TODO: Import parse_function_call, parse_array_parameter from utils.parser

# TODO: Load environment variables using load_dotenv()

class LibraryAssistant:
    
    def __init__(self, api_key=None):
        # TODO: Initialize API key from parameter or env var GEMINI_API_KEY
        
        # TODO: Raise ValueError if no key found with message: "GEMINI_API_KEY not found in environment variables."
        
        # TODO: Initialize Gemini client using genai.Client(api_key=self.api_key)
        
        # TODO: Set model name to "gemini-2.5-flash"
        pass
    
    def handle_function_call(self, function_name, parameters):
        """Handle library function call execution"""
        # TODO: Handle search_books function:
        # - Parse query parameter. If missing, return error: "Search query is required"
        # - Parse optional genre parameter. If provided and invalid, return error: "Invalid genre. Valid genres: fiction, non_fiction, mystery, romance, sci_fi, biography, history"
        # - Parse optional max_results parameter. Validate range (1-20, default 10)
        # - Call search_books(query, genre, max_results) and return formatted response
        
        # TODO: Handle manage_reading_list function:
        # - Parse action parameter (add, remove, view). If missing or invalid, return error: "Invalid action. Valid actions: add, remove, view"
        # - For add/remove actions, ensure book_id OR book_title is provided. If missing, return error: "Book ID or title required for <action> action"
        # - Call manage_reading_list(action, book_id, book_title) and return formatted response
        
        # TODO: Handle get_recommendations function:
        # - Parse genres array parameter. If missing, return error: "At least one genre is required for recommendations"
        # - Validate genres against valid list. If invalid genres found, return error: "Invalid genres: ..."
        # - Parse optional favorite_authors array parameter
        # - Parse optional count parameter. Validate range (1-10, default 5)
        # - Call get_recommendations(genres, favorite_authors, count) and return formatted response
        
        # TODO: Handle track_reading function:
        # - Parse book_id parameter. If missing, return error: "Book ID is required for tracking"
        # - Parse status parameter. If missing, return error: "Reading status is required"
        # - Validate status against valid list (reading, completed, paused, abandoned). If invalid, return error: "Invalid status. Valid statuses: ..."
        # - Parse optional rating parameter. If provided and not between 1 and 5, return error: "Rating must be between 1 and 5 stars"
        # - Call track_reading(book_id, status, pages_read, rating) and return formatted response
        
        # TODO: Handle unknown functions gracefully by returning: "Unknown function: <function_name>"
        pass
    
    def chat(self, user_input):
        """Main chat function that handles user input and decides whether to call functions"""
        # TODO: Prepare the conversation context formatted with system prompt and user input:
        # "<SYSTEM_PROMPT>\n\nUser: <user_input>\n\nAssistant:"
        
        # TODO: Call Gemini API using self.client.models.generate_content() with self.model and conversation context
        
        # TODO: If the API response text is None or empty/blank, return message: "I didn't receive a valid response. Please try again."
        
        # TODO: Use parse_function_call() to check if response contains CALL_FUNCTION pattern
        
        # TODO: If function call detected, parse and execute it using handle_function_call()
        
        # TODO: If no function call, return the conversational response text
        
        # TODO: Handle exceptions and return the error in this format: "Sorry, I encountered an error: <error_message>"
        pass

def answer_library_query(query, assistant=None):
    """Convenient wrapper function for library queries"""
    # TODO: Create LibraryAssistant instance if not provided
    # TODO: Call assistant.chat(query) and return the response
    # TODO: Handle exceptions and return the error in this format: "Sorry, I encountered an error: <error_message>"
    pass

def main():
    """Main function to demonstrate the library assistant."""
    print("Book Library Assistant - Intermediate Function Calling")
    print("Type 'quit' to exit")
    print("=" * 55)
    
    # Sample test queries
    sample_queries = [
        "Find me some mystery books",
        "Add The Great Gatsby to my reading list",
        "Recommend me some fiction and sci-fi books",
        "I finished reading book B001, give it 4 stars",
        "Hello! How can you help me?",
        "What makes a good book?"
    ]
    
    # TODO: Initialize assistant
    assistant = None
    
    print("\n--- Sample Queries ---")
    for query in sample_queries:
        print(f"\nUser: {query}")
        response = answer_library_query(query, assistant)
        print(f"Library: {response}")

if __name__ == "__main__":
    main()