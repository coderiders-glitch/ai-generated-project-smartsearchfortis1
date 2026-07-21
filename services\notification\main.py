import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from notification_orchestrator import NotificationOrchestrator

app = FastAPI(title="Notification Service", version="1.0.0")

logger = logging.getLogger(__name__)

allowed_origins = [
    "http://localhost:3000",
    "http://localhost:8000",
    "https://*.fortis.com"
]

allowed_methods = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]

allowed_headers = [
    "Content-Type",
    "Authorization",
    "X-Request-ID",
    "X-User-ID"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=allowed_methods,
    allow_headers=allowed_headers,
)

orchestrator = NotificationOrchestrator()


@app.get("/health")
async def health_check():
    """Health check endpoint for notification service."""
    return {"status": "healthy", "service": "notification_service"}


@app.post("/notifications/send")
async def send_notification(request: dict):
    """
    Send a notification based on type and recipient.
    
    Request body:
    {
        "notification_type": "appointment_reminder|followup|health_awareness|test_result|engagement|contextual",
        "user_id": "string",
        "data": {...}
    }
    """
    try:
        result = await orchestrator.process_notification(request)
        return {"status": "success", "data": result}
    except Exception as error:
        logger.error(f"Error sending notification: {str(error)}")
        return {"status": "error", "error_message": str(error)}, 500


@app.post("/notifications/batch")
async def send_batch_notifications(request: dict):
    """
    Send notifications to multiple users.
    
    Request body:
    {
        "notification_type": "string",
        "user_ids": ["user_id1", "user_id2"],
        "data": {...}
    }
    """
    try:
        result = await orchestrator.process_batch_notifications(request)
        return {"status": "success", "data": result}
    except Exception as error:
        logger.error(f"Error sending batch notifications: {str(error)}")
        return {"status": "error", "error_message": str(error)}, 500


@app.post("/notifications/schedule")
async def schedule_notification(request: dict):
    """
    Schedule a notification for future delivery.
    
    Request body:
    {
        "notification_type": "string",
        "user_id": "string",
        "scheduled_time": "ISO8601 datetime",
        "data": {...}
    }
    """
    try:
        result = await orchestrator.schedule_notification(request)
        return {"status": "success", "data": result}
    except Exception as error:
        logger.error(f"Error scheduling notification: {str(error)}")
        return {"status": "error", "error_message": str(error)}, 500


@app.get("/notifications/audience-cohort")
async def get_audience_cohort(cohort_type: str, filters: dict = None):
    """
    Get audience cohort for targeted notifications.
    
    Query parameters:
    - cohort_type: appointment_due|followup_due|health_check_due|test_result_pending|inactive_users|contextual_match
    - filters: optional JSON filters
    """
    try:
        result = await orchestrator.get_audience_cohort(cohort_type, filters)
        return {"status": "success", "data": result}
    except Exception as error:
        logger.error(f"Error retrieving audience cohort: {str(error)}")
        return {"status": "error", "error_message": str(error)}, 500


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)