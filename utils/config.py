from pathlib import Path

def load_system_prompt():
    """Load the system prompt from prompt.txt file."""
    prompt_path = Path(__file__).resolve().parent.parent / "prompt.txt"
    try:
        return prompt_path.read_text(encoding="utf-8").strip()
    except FileNotFoundError as error:
        raise FileNotFoundError(
            "prompt.txt file not found. Please ensure it exists in the project directory"
        ) from error
    except Exception as error:
        raise RuntimeError(f"Error loading prompt.txt: {error}") from error

def get_system_prompt():
    """Get the system prompt for the library assistant."""
    return load_system_prompt()

# Mock library database for demonstration
LIBRARY_DATA = {
    "books": {
        "B001": {
            "title": "The Great Gatsby",
            "author": "F. Scott Fitzgerald",
            "genre": "fiction",
            "pages": 180,
            "rating": 4.2,
            "description": "Classic American novel about the Jazz Age"
        },
        "B002": {
            "title": "To Kill a Mockingbird",
            "author": "Harper Lee",
            "genre": "fiction",
            "pages": 281,
            "rating": 4.5,
            "description": "A coming-of-age story set in the American South"
        },
        "B003": {
            "title": "The Murder on the Orient Express",
            "author": "Agatha Christie",
            "genre": "mystery",
            "pages": 256,
            "rating": 4.3,
            "description": "Classic mystery novel featuring Hercule Poirot"
        },
        "B004": {
            "title": "Dune",
            "author": "Frank Herbert",
            "genre": "sci_fi",
            "pages": 688,
            "rating": 4.4,
            "description": "Epic science fiction novel about politics and ecology"
        },
        "B005": {
            "title": "Pride and Prejudice",
            "author": "Jane Austen",
            "genre": "romance",
            "pages": 432,
            "rating": 4.6,
            "description": "Classic romance novel about Elizabeth Bennet and Mr. Darcy"
        }
    },
    "reading_lists": {},
    "reading_progress": {}
}

# Library function implementations for demonstration
def search_books(query, genre=None, max_results=10):
    """Function to search books"""
    results = []
    query_lower = query.lower().replace("_", " ")
    
    for book_id, book in LIBRARY_DATA["books"].items():
        # Check if query matches title, author, or description
        if (query_lower in book["title"].lower() or 
            query_lower in book["author"].lower() or 
            query_lower in book["description"].lower() or
            query_lower in book["genre"].lower().replace("_", " ")):
            
            # Filter by genre if specified
            if genre is None or book["genre"] == genre:
                results.append({
                    "book_id": book_id,
                    "title": book["title"],
                    "author": book["author"],
                    "genre": book["genre"],
                    "pages": book["pages"],
                    "rating": book["rating"]
                })
    
    # Limit results
    return {"books": results[:max_results], "count": len(results[:max_results])}

def manage_reading_list(action, book_id=None, book_title=None):
    """Function to manage reading list"""
    if action == "add":
        if book_id:
            if book_id in LIBRARY_DATA["books"]:
                LIBRARY_DATA["reading_lists"][book_id] = LIBRARY_DATA["books"][book_id]
                return {"success": True, "message": f"Added '{LIBRARY_DATA['books'][book_id]['title']}' to reading list"}
            else:
                return {"success": False, "message": "Book not found"}
        elif book_title:
            # Find book by title
            for bid, book in LIBRARY_DATA["books"].items():
                if book_title.lower() in book["title"].lower():
                    LIBRARY_DATA["reading_lists"][bid] = book
                    return {"success": True, "message": f"Added '{book['title']}' to reading list"}
            return {"success": False, "message": f"Book '{book_title}' not found"}
        else:
            return {"success": False, "message": "Book ID or title required"}
    
    elif action == "remove":
        if book_id and book_id in LIBRARY_DATA["reading_lists"]:
            del LIBRARY_DATA["reading_lists"][book_id]
            title = LIBRARY_DATA["books"][book_id]["title"]
            return {"success": True, "message": f"Removed '{title}' from reading list"}
        if book_title:
            for bid, book in LIBRARY_DATA["reading_lists"].items():
                if book_title.lower() in book["title"].lower():
                    del LIBRARY_DATA["reading_lists"][bid]
                    return {"success": True, "message": f"Removed '{book['title']}' from reading list"}
        return {"success": False, "message": "Book not found in reading list"}
    
    elif action == "view":
        books = list(LIBRARY_DATA["reading_lists"].values())
        return {"books": books, "count": len(books)}
    
    return {"success": False, "message": "Invalid action"}

def get_recommendations(genres, favorite_authors=None, count=5):
    """Function to get book recommendations"""
    recommendations = []
    
    for book_id, book in LIBRARY_DATA["books"].items():
        # Filter by genre
        if book["genre"] in genres:
            # Boost score if author is in favorites
            score = book["rating"]
            if favorite_authors and book["author"] in favorite_authors:
                score += 0.5
            
            recommendations.append({
                "book_id": book_id,
                "title": book["title"],
                "author": book["author"],
                "genre": book["genre"],
                "rating": book["rating"],
                "score": score
            })
    
    # Sort by score and limit
    recommendations.sort(key=lambda x: x["score"], reverse=True)
    return {"recommendations": recommendations[:count], "count": len(recommendations[:count])}

def track_reading(book_id, status, pages_read=None, rating=None):
    """Function to track reading progress"""
    if book_id not in LIBRARY_DATA["books"]:
        return {"success": False, "message": "Book not found"}
    
    # Update reading progress
    LIBRARY_DATA["reading_progress"][book_id] = {
        "status": status,
        "pages_read": pages_read,
        "rating": rating
    }
    
    book_title = LIBRARY_DATA["books"][book_id]["title"]
    
    if status == "completed":
        message = f"Marked '{book_title}' as completed"
        if rating:
            message += f" with {rating} stars"
    else:
        message = f"Updated '{book_title}' status to {status}"
        if pages_read is not None:
            total_pages = LIBRARY_DATA["books"][book_id]["pages"]
            progress = (pages_read / total_pages) * 100
            message += f" ({pages_read}/{total_pages} pages, {progress:.1f}% complete)"
    
    return {"success": True, "message": message}

# Export the system prompt
SYSTEM_PROMPT = get_system_prompt()