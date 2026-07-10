import logging
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class ContextualHandler:
    """Handles contextual notifications based on user behavior and context."""

    def __init__(self):
        """Initialize contextual handler."""
        self.notification_type = "contextual"

    async def build_notification(
        self, user_id: str, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Build contextual notification.
        
        Args:
            user_id: Target user ID
            data: Contextual data including context_type, trigger, recommendation
            
        Returns:
            Notification payload ready for delivery
        """
        logger.info(f"Building contextual notification for user {user_id}")

        context_type = data.get("context_type", "general")
        trigger = data.get("trigger", "")
        recommendation = data.get("recommendation", "")
        related_entity_id = data.get("related_entity_id", "")
        related_entity_type = data.get("related_entity_type", "")

        try:
            contextual_message = self._generate_contextual_message(
                context_type, trigger, recommendation
            )

            notification_payload = {
                "notification_type": self.notification_type,
                "user_id": user_id,
                "title": self._get_contextual_title(context_type),
                "message": contextual_message,
                "data": {
                    "context_type": context_type,
                    "trigger": trigger,
                    "recommendation": recommendation,
                    "related_entity_id": related_entity_id,
                    "related_entity_type": related_entity_type,
                },
                "priority": "medium",
                "action_url": self._build_action_url(
                    related_entity_type, related_entity_id
                ),
                "created_at": datetime.utcnow().isoformat(),
            }

            return notification_payload

        except Exception as error:
            logger.error(f"Error building contextual notification: {str(error)}")
            raise

    def _get_contextual_title(self, context_type: str) -> str:
        """
        Get notification title based on context type.
        
        Args:
            context_type: Type of context
            
        Returns:
            Notification title
        """
        titles = {
            "doctor_recommendation": "Recommended Doctor",
            "service_suggestion": "Suggested Service",
            "package_offer": "Recommended Package",
            "appointment_available": "Appointment Available",
            "location_based": "Nearby Healthcare",
            "time_based": "Timely Reminder",
        }
        return titles.get(context_type, "Personalized Suggestion")

    def _generate_contextual_message(
        self, context_type: str, trigger: str, recommendation: str
    ) -> str:
        """
        Generate personalized contextual message.
        
        Args:
            context_type: Type of context
            trigger: What triggered the notification
            recommendation: Specific recommendation
            
        Returns:
            Formatted contextual message
        """
        if context_type == "doctor_recommendation":
            message = f"Based on your health profile, we recommend: {recommendation}"
        elif context_type == "service_suggestion":
            message = f"We think you might benefit from: {recommendation}"
        elif context_type == "package_offer":
            message = f"Check out this health package: {recommendation}"
        elif context_type == "appointment_available":
            message = f"An appointment slot just became available: {recommendation}"
        elif context_type == "location_based":
            message = f"Healthcare services near you: {recommendation}"
        elif context_type == "time_based":
            message = f"It's a good time to: {recommendation}"
        else:
            message = f"Personalized suggestion: {recommendation}"

        return message

    def _build_action_url(
        self, related_entity_type: str, related_entity_id: str
    ) -> str:
        """
        Build action URL based on entity type.
        
        Args:
            related_entity_type: Type of related entity
            related_entity_id: ID of related entity
            
        Returns:
            Action URL
        """
        if related_entity_type == "doctor":
            return f"/doctors/{related_entity_id}"
        elif related_entity_type == "service":
            return f"/services/{related_entity_id}"
        elif related_entity_type == "package":
            return f"/packages/{related_entity_id}"
        elif related_entity_type == "appointment":
            return f"/appointments/{related_entity_id}"
        else:
            return "/home"