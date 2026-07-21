class KeywordSearch:
    def __init__(self):
        # Initialize with mock data
        self.mock_data = [
            {"id": 1, "title": "Smart Search Basics", "content": "Introduction to smart search functionality."},
            {"id": 2, "title": "Advanced Techniques", "content": "Deep dive into search algorithms."},
            {"id": 3, "title": "Keyword Optimization", "content": "How to optimize keywords for better results."}
        ]

    def search(self, query):
        """
        Searches the mock data for entries matching the query.

        Args:
            query (str): The search term.

        Returns:
            list: A list of matching dictionaries.

        Raises:
            ValueError: If the query is None or an empty string.
        """
        if not query:
            raise ValueError("Search query cannot be empty or None.")

        results = []
        for item in self.mock_data:
            # Simple case-insensitive search on title and content
            if query.lower() in item["title"].lower() or query.lower() in item["content"].lower():
                results.append(item)

        return results