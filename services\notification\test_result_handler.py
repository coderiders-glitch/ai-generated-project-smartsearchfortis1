import logging
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class TestResultHandler:
    """Handles test result notifications."""

    def __init__(self):
        """Initialize test result handler."""
        self.notification_type = "test_result"

    async def build_notification(
        self, user_id: str, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Build test result notification.
        
        Args:
            user_id: Target user ID
            data: Test data including test_name, result_status, test_id, doctor_name
            
        Returns:
            Notification payload ready for delivery
        """
        logger.info(f"Building test result notification for user {user_id}")

        test_id = data.get("test_id")
        test_name = data.get("test_name", "Lab Test")
        result_status = data.get("result_status", "completed")
        doctor_name = data.get("doctor_name", "Your Doctor")
        result_summary = data.get("result_summary", "")
        requires_action = data.get("requires_action", False)

        try:
            result_message = self._generate_result_message(
                test_name, result_status, result_summary, requires_action
            )
            priority = "high" if requires_action else "medium"

            notification_payload = {
                "notification_type": self.notification_type,
                "user_id": user_id,
                "title": "Test Results Available",
                "message": result_message,
                "data": {
                    "test_id": test_id,
                    "test_name": test_name,
                    "result_status": result_status,
                    "doctor_name": doctor_name,
                    "result_summary": result_summary,
                    "requires_action": requires_action,
                },
                "priority": priority,
                "action_url": f"/tests/{test_id}/results",
                "created_at": datetime.utcnow().isoformat(),
            }

            return notification_payload

        except Exception as error:
            logger.error(f"Error building test result notification: {str(error)}")
            raise

    def _generate_result_message(
        self,
        test_name: str,
        result_status: str,
        result_summary: str,
        requires_action: bool,
    ) -> str:
        """
        Generate personalized test result message.
        
        Args:
            test_name: Name of the test
            result_status: Status of results (completed, abnormal, normal)
            result_summary: Summary of results
            requires_action: Whether action is required
            
        Returns:
            Formatted result message
        """
        if result_status == "abnormal":
            message = f"Your {test_name} results are ready and show abnormal values. Please contact your doctor for interpretation."
        elif result_status == "normal":
            message = f"Your {test_name} results are ready and within normal range."
        else:
            message = f"Your {test_name} results are now available. Please review them."

        if result_summary:
            message += f" {result_summary}"

        if requires_action:
            message += " Action required - please schedule a follow-up appointment."

        return message