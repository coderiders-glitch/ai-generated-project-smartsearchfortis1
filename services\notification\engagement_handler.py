import logging
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class EngagementHandler:
    """Handles engagement and reactivation notifications."""

    def __init__(self):
        """Initialize engagement handler."""
        self.notification_type = "engagement"

    async def build_notification(
        self, user_id: str, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Build engagement/reactivation notification.
        
        Args:
            user_id: Target user ID
            data: Engagement data including engagement_type, days_inactive, incentive
            
        Returns:
            Notification payload ready for delivery
        """
        logger.info(f"Building engagement notification for user {user_id}")

        engagement_type = data.get("engagement_type", "reactivation")
        days_inactive = data.get("days_inactive", 0)
        incentive = data.get("incentive", "")
        call_to_action = data.get("call_to_action", "")
        feature_highlight = data.get("feature_highlight", "")

        try:
            engagement_message = self._generate_engagement_message(
                engagement_type, days_inactive, incentive, feature_highlight
            )

            notification_payload = {
                "notification_type": self.notification_type,
                "user_id": user_id,
                "title": self._get_engagement_title(engagement_type),
                "message": engagement_message,
                "data": {
                    "engagement_type": engagement_type,
                    "days_inactive": days_inactive,
                    "incentive": incentive,
                    "call_to_action": call_to_action,
                    "feature_highlight": feature_highlight,
                },
                "priority": "medium",
                "action_url": call_to_action or "/home",
                "created_at": datetime.utcnow().isoformat(),
            }

            return notification_payload

        except Exception as error:
            logger.error(f"Error building engagement notification: {str(error)}")
            raise

    def _get_engagement_title(self, engagement_type: str) -> str:
        """
        Get notification title based on engagement type.
        
        Args:
            engagement_type: Type of engagement
            
        Returns:
            Notification title
        """
        titles = {
            "reactivation": "We Miss You!",
            "feature_announcement": "New Feature Available",
            "special_offer": "Special Offer for You",
            "milestone": "Congratulations!",
            "survey": "Your Feedback Matters",
        }
        return titles.get(engagement_type, "Special Message")

    def _generate_engagement_message(
        self,
        engagement_type: str,
        days_inactive: int,
        incentive: str,
        feature_highlight: str,
    ) -> str:
        """
        Generate personalized engagement message.
        
        Args:
            engagement_type: Type of engagement
            days_inactive: Days since last activity
            incentive: Incentive or offer
            feature_highlight: Feature to highlight
            
        Returns:
            Formatted engagement message
        """
        if engagement_type == "reactivation":
            message = f"We haven't seen you in {days_inactive} days. Come back and continue managing your health."
            if incentive:
                message += f" {incentive}"
        elif engagement_type == "feature_announcement":
            message = f"Check out our new feature: {feature_highlight}. It can help you better manage your health."
        elif engagement_type == "special_offer":
            message = f"Special offer just for you: {incentive}"
        elif engagement_type == "milestone":
            message = f"Great job! {incentive}"
        elif engagement_type == "survey":
            message = "We'd love to hear your feedback. Take a quick survey to help us improve."
        else:
            message = f"We have something special for you: {incentive}"

        return message