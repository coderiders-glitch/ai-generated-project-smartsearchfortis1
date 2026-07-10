import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from profile_manager import ProfileManager
from preference_manager import PreferenceManager
from history_manager import HistoryManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="User Profile Service", version="1.0.0")

allowed_origins = [
    "http://localhost:3000",
    "http://localhost:8000",
    "https://*.fortis.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Request-ID", "X-User-ID"]
)

profile_manager = ProfileManager()
preference_manager = PreferenceManager()
history_manager = HistoryManager()

@app.get("/health")
async def health_check():
    """Health check endpoint for user profile service."""
    return {"status": "healthy", "service": "user_profile_service"}

@app.get("/users/{user_id}/profile")
async def get_user_profile(user_id: str):
    """Retrieve user profile by user ID."""
    try:
        profile = profile_manager.get_profile(user_id)
        if not profile:
            return {"error": "User profile not found"}, 404
        return profile, 200
    except Exception as error:
        logger.error(f"Error retrieving profile for user {user_id}: {error}")
        return {"error": "Internal server error"}, 500

@app.post("/users")
async def create_user(request_data: dict):
    """Create a new user profile."""
    try:
        user_id = profile_manager.create_profile(request_data)
        return {"user_id": user_id, "message": "User profile created"}, 201
    except ValueError as error:
        logger.warning(f"Validation error creating user: {error}")
        return {"error": str(error)}, 400
    except Exception as error:
        logger.error(f"Error creating user profile: {error}")
        return {"error": "Internal server error"}, 500

@app.put("/users/{user_id}")
async def update_user_profile(user_id: str, request_data: dict):
    """Update an existing user profile."""
    try:
        updated_profile = profile_manager.update_profile(user_id, request_data)
        if not updated_profile:
            return {"error": "User profile not found"}, 404
        return updated_profile, 200
    except ValueError as error:
        logger.warning(f"Validation error updating user {user_id}: {error}")
        return {"error": str(error)}, 400
    except Exception as error:
        logger.error(f"Error updating profile for user {user_id}: {error}")
        return {"error": "Internal server error"}, 500

@app.get("/users/{user_id}/preferences")
async def get_user_preferences(user_id: str):
    """Retrieve user preferences."""
    try:
        preferences = preference_manager.get_preferences(user_id)
        if not preferences:
            return {"error": "User preferences not found"}, 404
        return preferences, 200
    except Exception as error:
        logger.error(f"Error retrieving preferences for user {user_id}: {error}")
        return {"error": "Internal server error"}, 500

@app.put("/users/{user_id}/preferences")
async def update_user_preferences(user_id: str, request_data: dict):
    """Update user preferences."""
    try:
        updated_preferences = preference_manager.update_preferences(user_id, request_data)
        if not updated_preferences:
            return {"error": "User preferences not found"}, 404
        return updated_preferences, 200
    except ValueError as error:
        logger.warning(f"Validation error updating preferences for user {user_id}: {error}")
        return {"error": str(error)}, 400
    except Exception as error:
        logger.error(f"Error updating preferences for user {user_id}: {error}")
        return {"error": "Internal server error"}, 500

@app.get("/users/{user_id}/search-history")
async def get_search_history(user_id: str):
    """Retrieve user search history."""
    try:
        search_history = history_manager.get_search_history(user_id)
        return {"search_history": search_history}, 200
    except Exception as error:
        logger.error(f"Error retrieving search history for user {user_id}: {error}")
        return {"error": "Internal server error"}, 500

@app.post("/users/{user_id}/search-history")
async def add_search_history(user_id: str, request_data: dict):
    """Add entry to user search history."""
    try:
        history_manager.add_search_history(user_id, request_data)
        return {"message": "Search history entry added"}, 201
    except ValueError as error:
        logger.warning(f"Validation error adding search history for user {user_id}: {error}")
        return {"error": str(error)}, 400
    except Exception as error:
        logger.error(f"Error adding search history for user {user_id}: {error}")
        return {"error": "Internal server error"}, 500

@app.get("/users/{user_id}/booking-history")
async def get_booking_history(user_id: str):
    """Retrieve user booking history."""
    try:
        booking_history = history_manager.get_booking_history(user_id)
        return {"booking_history": booking_history}, 200
    except Exception as error:
        logger.error(f"Error retrieving booking history for user {user_id}: {error}")
        return {"error": "Internal server error"}, 500

@app.post("/users/{user_id}/booking-history")
async def add_booking_history(user_id: str, request_data: dict):
    """Add entry to user booking history."""
    try:
        history_manager.add_booking_history(user_id, request_data)
        return {"message": "Booking history entry added"}, 201
    except ValueError as error:
        logger.warning(f"Validation error adding booking history for user {user_id}: {error}")
        return {"error": str(error)}, 400
    except Exception as error:
        logger.error(f"Error adding booking history for user {user_id}: {error}")
        return {"error": "Internal server error"}, 500

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)