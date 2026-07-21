import logging
from typing import Dict, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class AppointmentReminderHandler:
    """Handles appointment reminder notifications."""

    def __init__(self):
        """Initialize appointment reminder handler."""
        self.notification_type = "appointment_reminder"

    async def build_notification(
        self, user_id: str, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Build appointment reminder notification.
        
        Args:
            user_id: Target user ID
            data: Appointment data including appointment_id, doctor_name, appointment_time
            
        Returns:
            Notification payload ready for delivery
        """
        logger.info(f"Building appointment reminder for user {user_id}")

        appointment_id = data.get("appointment_id")
        doctor_name = data.get("doctor_name", "Your Doctor")
        appointment_time = data.get("appointment_time")
        appointment_type = data.get("appointment_type", "appointment")
        location = data.get("location", "")

        try:
            time_until_appointment = self._calculate_time_until(
                appointment_time
            )
            reminder_message = self._generate_reminder_message(
                doctor_name, appointment_type, time_until_appointment, location
            )

            notification_payload = {
                "notification_type": self.notification_type,
                "user_id": user_id,
                "title": "Appointment Reminder",
                "message": reminder_message,
                "data": {
                    "appointment_id": appointment_id,
                    "doctor_name": doctor_name,
                    "appointment_time": appointment_time,
                    "appointment_type": appointment_type,
                    "location": location,
                },
                "priority": "high",
                "action_url": f"/appointments/{appointment_id}",
                "created_at": datetime.utcnow().isoformat(),
            }

            return notification_payload

        except Exception as error:
            logger.error(f"Error building appointment reminder: {str(error)}")
            raise

    def _calculate_time_until(self, appointment_time: str) -> str:
        """
        Calculate human-readable time until appointment.
        
        Args:
            appointment_time: ISO8601 appointment time
            
        Returns:
            Human-readable time string
        """
        try:
            appointment_dt = datetime.fromisoformat(
                appointment_time.replace("Z", "+00:00")
            )
            now = datetime.utcnow()
            delta = appointment_dt - now

            if delta.days > 0:
                return f"in {delta.days} day(s)"
            elif delta.seconds >= 3600:
                hours = delta.seconds // 3600
                return f"in {hours} hour(s)"
            else:
                minutes = delta.seconds // 60
                return f"in {minutes} minute(s)"
        except Exception as error:
            logger.error(f"Error calculating time until appointment: {str(error)}")
            return "soon"

    def _generate_reminder_message(
        self,
        doctor_name: str,
        appointment_type: str,
        time_until: str,
        location: str,
    ) -> str:
        """
        Generate personalized reminder message.
        
        Args:
            doctor_name: Name of the doctor
            appointment_type: Type of appointment
            time_until: Time until appointment
            location: Appointment location
            
        Returns:
            Formatted reminder message
        """
        message = f"Your {appointment_type} with {doctor_name} is {time_until}"
        if location:
            message += f" at {location}"
        message += ". Please arrive 10 minutes early."
        return message