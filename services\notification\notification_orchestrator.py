import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from appointment_reminder_handler import AppointmentReminderHandler
from followup_handler import FollowupHandler
from health_awareness_handler import HealthAwarenessHandler
from test_result_handler import TestResultHandler
from engagement_handler import EngagementHandler
from contextual_handler import ContextualHandler
from delivery_manager import DeliveryManager
from audience_cohort_builder import AudienceCohortBuilder

logger = logging.getLogger(__name__)


class NotificationOrchestrator:
    """Orchestrates notification routing and delivery across all notification types."""

    def __init__(self):
        """Initialize all notification handlers and managers."""
        self.appointment_reminder_handler = AppointmentReminderHandler()
        self.followup_handler = FollowupHandler()
        self.health_awareness_handler = HealthAwarenessHandler()
        self.test_result_handler = TestResultHandler()
        self.engagement_handler = EngagementHandler()
        self.contextual_handler = ContextualHandler()
        self.delivery_manager = DeliveryManager()
        self.audience_cohort_builder = AudienceCohortBuilder()

    async def process_notification(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Route notification to appropriate handler based on type.
        
        Args:
            request: Notification request with type, user_id, and data
            
        Returns:
            Notification processing result
        """
        notification_type = request.get("notification_type")
        user_id = request.get("user_id")
        data = request.get("data", {})

        logger.info(f"Processing {notification_type} notification for user {user_id}")

        try:
            if notification_type == "appointment_reminder":
                notification_payload = await self.appointment_reminder_handler.build_notification(
                    user_id, data
                )
            elif notification_type == "followup":
                notification_payload = await self.followup_handler.build_notification(
                    user_id, data
                )
            elif notification_type == "health_awareness":
                notification_payload = await self.health_awareness_handler.build_notification(
                    user_id, data
                )
            elif notification_type == "test_result":
                notification_payload = await self.test_result_handler.build_notification(
                    user_id, data
                )
            elif notification_type == "engagement":
                notification_payload = await self.engagement_handler.build_notification(
                    user_id, data
                )
            elif notification_type == "contextual":
                notification_payload = await self.contextual_handler.build_notification(
                    user_id, data
                )
            else:
                raise ValueError(f"Unknown notification type: {notification_type}")

            delivery_result = await self.delivery_manager.deliver(
                user_id, notification_payload
            )
            return delivery_result

        except Exception as error:
            logger.error(f"Error processing notification: {str(error)}")
            raise

    async def process_batch_notifications(
        self, request: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Send notifications to multiple users.
        
        Args:
            request: Batch notification request with type, user_ids, and data
            
        Returns:
            Batch processing result with success/failure counts
        """
        notification_type = request.get("notification_type")
        user_ids = request.get("user_ids", [])
        data = request.get("data", {})

        logger.info(
            f"Processing batch {notification_type} notifications for {len(user_ids)} users"
        )

        results = {
            "total": len(user_ids),
            "successful": 0,
            "failed": 0,
            "failures": [],
        }

        for user_id in user_ids:
            try:
                await self.process_notification(
                    {
                        "notification_type": notification_type,
                        "user_id": user_id,
                        "data": data,
                    }
                )
                results["successful"] += 1
            except Exception as error:
                logger.error(f"Failed to send notification to {user_id}: {str(error)}")
                results["failed"] += 1
                results["failures"].append({"user_id": user_id, "error": str(error)})

        return results

    async def schedule_notification(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Schedule a notification for future delivery.
        
        Args:
            request: Schedule request with type, user_id, scheduled_time, and data
            
        Returns:
            Schedule confirmation with notification_id
        """
        notification_type = request.get("notification_type")
        user_id = request.get("user_id")
        scheduled_time = request.get("scheduled_time")
        data = request.get("data", {})

        logger.info(
            f"Scheduling {notification_type} notification for user {user_id} at {scheduled_time}"
        )

        try:
            schedule_result = await self.delivery_manager.schedule(
                user_id, notification_type, data, scheduled_time
            )
            return schedule_result
        except Exception as error:
            logger.error(f"Error scheduling notification: {str(error)}")
            raise

    async def get_audience_cohort(
        self, cohort_type: str, filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get audience cohort for targeted notifications.
        
        Args:
            cohort_type: Type of cohort to retrieve
            filters: Optional filters for cohort selection
            
        Returns:
            Cohort data with user_ids and metadata
        """
        logger.info(f"Building audience cohort: {cohort_type}")

        try:
            cohort_data = await self.audience_cohort_builder.build_cohort(
                cohort_type, filters
            )
            return cohort_data
        except Exception as error:
            logger.error(f"Error building audience cohort: {str(error)}")
            raise