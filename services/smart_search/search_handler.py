from fastapi import HTTPException


def search_doctors(query: str = None, specialty: str = None):
    """
    Searches for doctors based on a query string or specialty.
    """
    if query:
        # Logic for query-based search
        return [f"Results for query: {query}"]
    elif specialty:
        # Logic for specialty-based search
        return [f"Results for specialty: {specialty}"]
    else:
        # Handle edge case where both are None
        raise HTTPException(
            status_code=400,
            detail="A search query or specialty is required."
        )