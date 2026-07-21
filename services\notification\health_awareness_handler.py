import logging
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class HealthAwarenessHandler:
    """Handles health awareness and preventive care notifications."""

    def __init__(self):
        """Initialize health awareness handler."""
        self.notification_type = "health_awareness"

    async def build_notification(
        self, user_id: str, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Build health awareness notification.
        
        Args:
            user_id: Target user ID
            data: Health data including awareness_type, health_topic, recommendation
            
        Returns:
            Notification payload ready for delivery
        """
        logger.info(f"Building health awareness notification for user {user_id}")

        awareness_type = data.get("awareness_type", "general")
        health_topic = data.get("health_topic", "")
        recommendation = data.get("recommendation", "")
        urgency = data.get("urgency", "low")
        resource_url = data.get("resource_url", "")

        try:
            awareness_message = self._generate_awareness_message(
                awareness_type, health_topic, recommendation, urgency
            )

            notification_payload = {
                "notification_type": self.notification_type,
                "user_id": user_id,
                "title": self._get_awareness_title(awareness_type),
                "message": awareness_message,
                "data": {
                    "awareness_type": awareness_type,
                    "health_topic": health_topic,
                    "recommendation": recommendation,
                    "urgency": urgency,
                    "resource_url": resource_url,
                },
                "priority": "high" if urgency == "high" else "medium",
                "action_url": resource_url or "/health/awareness",
                "created_at": datetime.utcnow().isoformat(),
            }

            return notification_payload

        except Exception as error:
            logger.error(f"Error building health awareness notification: {str(error)}")
            raise

    def _get_awareness_title(self, awareness_type: str) -> str:
        """
        Get notification title based on awareness type.
        
        Args:
            awareness_type: Type of health awareness
            
        Returns:
            Notification title
        """
        titles = {
            "vaccination": "Vaccination Reminder",
            "screening": "Health Screening Due",
            "checkup": "Annual Checkup Reminder",
            "lifestyle": "Health Tip",
            "prevention": "Preventive Care Recommendation",
            "general": "Health Awareness",
        }
        return titles.get(awareness_type, "Health Awareness")

    def _generate_awareness_message(
        self,
        awareness_type: str,
        health_topic: str,
        recommendation: str,
        urgency: str,
    ) -> str:
        """
        Generate personalized health awareness message.
        
        Args:
            awareness_type: Type of awareness
            health_topic: Health topic
            recommendation: Specific recommendation
            urgency: Urgency level
            
        Returns:
            Formatted awareness message
        """
        if awareness_type == "vaccination":
            message = f"It's time to update your {health_topic} vaccination. Schedule an appointment with your healthcare provider."
        elif awareness_type == "screening":
            message = f"You may be due for a {health_topic} screening. Consult with your doctor about scheduling."
        elif awareness_type == "checkup":
            message = f"It's time for your annual {health_topic} checkup. Book an appointment today."
        elif awareness_type == "lifestyle":
            message = f"Health Tip: {recommendation}"
        elif awareness_type == "prevention":
            message = f"Preventive Care: {recommendation}"
        else:
            message = f"Health Alert: {health_topic}. {recommendation}"

        if urgency == "high":
            message += " Please prioritize this."

        return message