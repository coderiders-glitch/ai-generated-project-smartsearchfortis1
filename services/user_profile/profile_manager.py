import logging
from typing import Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class ProfileManager:
    """Manages user profile operations including creation, retrieval, and updates."""

    def __init__(self):
        """Initialize ProfileManager with in-memory storage."""
        self.profiles: Dict[str, Dict[str, Any]] = {}
        self.profile_counter = 0

    def create_profile(self, request_data: Dict[str, Any]) -> str:
        """Create a new user profile.
        
        Args:
            request_data: Dictionary containing user profile data
            
        Returns:
            user_id: The ID of the newly created user
            
        Raises:
            ValueError: If required fields are missing
        """
        required_fields = ["username", "email"]
        for field in required_fields:
            if field not in request_data or not request_data[field]:
                raise ValueError(f"Missing required field: {field}")

        self.profile_counter += 1
        user_id = f"user_{self.profile_counter}"

        profile = {
            "user_id": user_id,
            "username": request_data.get("username"),
            "email": request_data.get("email"),
            "first_name": request_data.get("first_name", ""),
            "last_name": request_data.get("last_name", ""),
            "phone": request_data.get("phone", ""),
            "date_of_birth": request_data.get("date_of_birth", ""),
            "gender": request_data.get("gender", ""),
            "address": request_data.get("address", ""),
            "city": request_data.get("city", ""),
            "state": request_data.get("state", ""),
            "postal_code": request_data.get("postal_code", ""),
            "country": request_data.get("country", ""),
            "is_active": True,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }

        self.profiles[user_id] = profile
        logger.info(f"User profile created: {user_id}")
        return user_id

    def get_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a user profile by user ID.
        
        Args:
            user_id: The ID of the user
            
        Returns:
            Dictionary containing user profile data or None if not found
        """
        profile = self.profiles.get(user_id)
        if profile:
            logger.info(f"User profile retrieved: {user_id}")
        else:
            logger.warning(f"User profile not found: {user_id}")
        return profile

    def update_profile(self, user_id: str, request_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update an existing user profile.
        
        Args:
            user_id: The ID of the user
            request_data: Dictionary containing fields to update
            
        Returns:
            Updated profile dictionary or None if user not found
            
        Raises:
            ValueError: If email format is invalid
        """
        if user_id not in self.profiles:
            logger.warning(f"Attempted to update non-existent user: {user_id}")
            return None

        if "email" in request_data and request_data["email"]:
            if "@" not in request_data["email"]:
                raise ValueError("Invalid email format")

        profile = self.profiles[user_id]
        updatable_fields = [
            "username", "email", "first_name", "last_name", "phone",
            "date_of_birth", "gender", "address", "city", "state",
            "postal_code", "country", "is_active"
        ]

        for field in updatable_fields:
            if field in request_data:
                profile[field] = request_data[field]

        profile["updated_at"] = datetime.utcnow().isoformat()
        logger.info(f"User profile updated: {user_id}")
        return profile

    def delete_profile(self, user_id: str) -> bool:
        """Delete a user profile.
        
        Args:
            user_id: The ID of the user
            
        Returns:
            True if profile was deleted, False if not found
        """
        if user_id in self.profiles:
            del self.profiles[user_id]
            logger.info(f"User profile deleted: {user_id}")
            return True
        logger.warning(f"Attempted to delete non-existent user: {user_id}")
        return False