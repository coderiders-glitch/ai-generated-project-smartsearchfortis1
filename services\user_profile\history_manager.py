import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)

class HistoryManager:
    """Manages user search history and booking history."""

    def __init__(self):
        """Initialize HistoryManager with in-memory storage."""
        self.search_history: Dict[str, List[Dict[str, Any]]] = {}
        self.booking_history: Dict[str, List[Dict[str, Any]]] = {}

    def get_search_history(self, user_id: str) -> List[Dict[str, Any]]:
        """Retrieve user search history.
        
        Args:
            user_id: The ID of the user
            
        Returns:
            List of search history entries
        """
        history = self.search_history.get(user_id, [])
        logger.info(f"Search history retrieved for user: {user_id}")
        return history

    def add_search_history(self, user_id: str, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add entry to user search history.
        
        Args:
            user_id: The ID of the user
            request_data: Dictionary containing search data
            
        Returns:
            Dictionary containing the added search history entry
            
        Raises:
            ValueError: If required fields are missing
        """
        if "query" not in request_data or not request_data["query"]:
            raise ValueError("Missing required field: query")

        if user_id not in self.search_history:
            self.search_history[user_id] = []

        search_entry = {
            "query": request_data.get("query"),
            "search_type": request_data.get("search_type", "general"),
            "filters": request_data.get("filters", {}),
            "results_count": request_data.get("results_count", 0),
            "timestamp": datetime.utcnow().isoformat()
        }

        self.search_history[user_id].append(search_entry)
        logger.info(f"Search history entry added for user: {user_id}")
        return search_entry

    def clear_search_history(self, user_id: str) -> bool:
        """Clear all search history for a user.
        
        Args:
            user_id: The ID of the user
            
        Returns:
            True if history was cleared, False if user has no history
        """
        if user_id in self.search_history:
            self.search_history[user_id] = []
            logger.info(f"Search history cleared for user: {user_id}")
            return True
        logger.warning(f"No search history found for user: {user_id}")
        return False

    def get_booking_history(self, user_id: str) -> List[Dict[str, Any]]:
        """Retrieve user booking history.
        
        Args:
            user_id: The ID of the user
            
        Returns:
            List of booking history entries
        """
        history = self.booking_history.get(user_id, [])
        logger.info(f"Booking history retrieved for user: {user_id}")
        return history

    def add_booking_history(self, user_id: str, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add entry to user booking history.
        
        Args:
            user_id: The ID of the user
            request_data: Dictionary containing booking data
            
        Returns:
            Dictionary containing the added booking history entry
            
        Raises:
            ValueError: If required fields are missing
        """
        required_fields = ["doctor_id", "appointment_date"]
        for field in required_fields:
            if field not in request_data or not request_data[field]:
                raise ValueError(f"Missing required field: {field}")

        if user_id not in self.booking_history:
            self.booking_history[user_id] = []

        booking_entry = {
            "booking_id": f"booking_{len(self.booking_history[user_id]) + 1}",
            "doctor_id": request_data.get("doctor_id"),
            "appointment_date": request_data.get("appointment_date"),
            "appointment_time": request_data.get("appointment_time", ""),
            "specialty": request_data.get("specialty", ""),
            "service": request_data.get("service", ""),
            "status": request_data.get("status", "confirmed"),
            "notes": request_data.get("notes", ""),
            "created_at": datetime.utcnow().isoformat()
        }

        self.booking_history[user_id].append(booking_entry)
        logger.info(f"Booking history entry added for user: {user_id}")
        return booking_entry

    def update_booking_status(self, user_id: str, booking_id: str, status: str) -> Optional[Dict[str, Any]]:
        """Update the status of a booking.
        
        Args:
            user_id: The ID of the user
            booking_id: The ID of the booking
            status: The new status
            
        Returns:
            Updated booking entry or None if not found
        """
        if user_id not in self.booking_history:
            logger.warning(f"No booking history found for user: {user_id}")
            return None

        for booking in self.booking_history[user_id]:
            if booking.get("booking_id") == booking_id:
                booking["status"] = status
                logger.info(f"Booking status updated: {booking_id}")
                return booking

        logger.warning(f"Booking not found: {booking_id}")
        return None

    def clear_booking_history(self, user_id: str) -> bool:
        """Clear all booking history for a user.
        
        Args:
            user_id: The ID of the user
            
        Returns:
            True if history was cleared, False if user has no history
        """
        if user_id in self.booking_history:
            self.booking_history[user_id] = []
            logger.info(f"Booking history cleared for user: {user_id}")
            return True
        logger.warning(f"No booking history found for user: {user_id}")
        return False