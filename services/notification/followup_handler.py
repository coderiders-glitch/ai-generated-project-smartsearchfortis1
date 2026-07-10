import logging
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class FollowupHandler:
    """Handles follow-up prompt notifications."""

    def __init__(self):
        """Initialize follow-up handler."""
        self.notification_type = "followup"

    async def build_notification(
        self, user_id: str, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Build follow-up notification.
        
        Args:
            user_id: Target user ID
            data: Follow-up data including appointment_id, doctor_name, followup_type
            
        Returns:
            Notification payload ready for delivery
        """
        logger.info(f"Building follow-up notification for user {user_id}")

        appointment_id = data.get("appointment_id")
        doctor_name = data.get("doctor_name", "Your Doctor")
        followup_type = data.get("followup_type", "general")
        days_since_appointment = data.get("days_since_appointment", 3)
        instructions = data.get("instructions", "")

        try:
            followup_message = self._generate_followup_message(
                doctor_name, followup_type, days_since_appointment, instructions
            )

            notification_payload = {
                "notification_type": self.notification_type,
                "user_id": user_id,
                "title": "Follow-up Required",
                "message": followup_message,
                "data": {
                    "appointment_id": appointment_id,
                    "doctor_name": doctor_name,
                    "followup_type": followup_type,
                    "days_since_appointment": days_since_appointment,
                    "instructions": instructions,
                },
                "priority": "medium",
                "action_url": f"/appointments/{appointment_id}/followup",
                "created_at": datetime.utcnow().isoformat(),
            }

            return notification_payload

        except Exception as error:
            logger.error(f"Error building follow-up notification: {str(error)}")
            raise

    def _generate_followup_message(
        self,
        doctor_name: str,
        followup_type: str,
        days_since: int,
        instructions: str,
    ) -> str:
        """
        Generate personalized follow-up message.
        
        Args:
            doctor_name: Name of the doctor
            followup_type: Type of follow-up (general, medication, test, etc.)
            days_since: Days since original appointment
            instructions: Specific instructions for follow-up
            
        Returns:
            Formatted follow-up message
        """
        if followup_type == "medication":
            message = f"It's been {days_since} days since your appointment with {doctor_name}. Please ensure you're taking your prescribed medications as directed."
        elif followup_type == "test":
            message = f"It's been {days_since} days since your appointment with {doctor_name}. Please complete your recommended tests."
        elif followup_type == "symptoms":
            message = f"How are you feeling after your appointment with {doctor_name}? Please report any new symptoms."
        else:
            message = f"Follow-up check-in: It's been {days_since} days since your appointment with {doctor_name}."

        if instructions:
            message += f" {instructions}"

        return message