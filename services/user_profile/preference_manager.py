import logging
from typing import Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class PreferenceManager:
    """Manages user preferences including notification settings and personalization options."""

    def __init__(self):
        """Initialize PreferenceManager with in-memory storage."""
        self.preferences: Dict[str, Dict[str, Any]] = {}

    def get_preferences(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve user preferences.
        
        Args:
            user_id: The ID of the user
            
        Returns:
            Dictionary containing user preferences or None if not found
        """
        preferences = self.preferences.get(user_id)
        if preferences:
            logger.info(f"User preferences retrieved: {user_id}")
        else:
            logger.warning(f"User preferences not found: {user_id}")
        return preferences

    def create_preferences(self, user_id: str, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create default preferences for a new user.
        
        Args:
            user_id: The ID of the user
            request_data: Dictionary containing preference data
            
        Returns:
            Dictionary containing created preferences
        """
        preferences = {
            "user_id": user_id,
            "notification_email": request_data.get("notification_email", True),
            "notification_sms": request_data.get("notification_sms", False),
            "notification_push": request_data.get("notification_push", True),
            "notification_appointment_reminder": request_data.get("notification_appointment_reminder", True),
            "notification_health_tips": request_data.get("notification_health_tips", True),
            "notification_promotions": request_data.get("notification_promotions", False),
            "language": request_data.get("language", "en"),
            "timezone": request_data.get("timezone", "UTC"),
            "theme": request_data.get("theme", "light"),
            "privacy_level": request_data.get("privacy_level", "private"),
            "share_health_data": request_data.get("share_health_data", False),
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        self.preferences[user_id] = preferences
        logger.info(f"User preferences created: {user_id}")
        return preferences

    def update_preferences(self, user_id: str, request_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update user preferences.
        
        Args:
            user_id: The ID of the user
            request_data: Dictionary containing fields to update
            
        Returns:
            Updated preferences dictionary or None if user preferences not found
            
        Raises:
            ValueError: If invalid preference values are provided
        """
        if user_id not in self.preferences:
            logger.warning(f"Attempted to update non-existent preferences for user: {user_id}")
            return None

        valid_languages = ["en", "es", "fr", "de", "zh", "ja"]
        if "language" in request_data and request_data["language"] not in valid_languages:
            raise ValueError(f"Invalid language. Supported: {valid_languages}")

        valid_themes = ["light", "dark"]
        if "theme" in request_data and request_data["theme"] not in valid_themes:
            raise ValueError(f"Invalid theme. Supported: {valid_themes}")

        valid_privacy_levels = ["public", "private", "friends_only"]
        if "privacy_level" in request_data and request_data["privacy_level"] not in valid_privacy_levels:
            raise ValueError(f"Invalid privacy level. Supported: {valid_privacy_levels}")

        preferences = self.preferences[user_id]
        updatable_fields = [
            "notification_email", "notification_sms", "notification_push",
            "notification_appointment_reminder", "notification_health_tips",
            "notification_promotions", "language", "timezone", "theme",
            "privacy_level", "share_health_data"
        ]

        for field in updatable_fields:
            if field in request_data:
                preferences[field] = request_data[field]

        preferences["updated_at"] = datetime.utcnow().isoformat()
        logger.info(f"User preferences updated: {user_id}")
        return preferences

    def delete_preferences(self, user_id: str) -> bool:
        """Delete user preferences.
        
        Args:
            user_id: The ID of the user
            
        Returns:
            True if preferences were deleted, False if not found
        """
        if user_id in self.preferences:
            del self.preferences[user_id]
            logger.info(f"User preferences deleted: {user_id}")
            return True
        logger.warning(f"Attempted to delete non-existent preferences for user: {user_id}")
        return False