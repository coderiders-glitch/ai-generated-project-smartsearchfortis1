import os
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from search_handler import SearchHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = None
search_handler = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global search_handler
    search_handler = SearchHandler()
    logger.info("Smart Search Service initialized")
    yield
    logger.info("Smart Search Service shutdown")


app = FastAPI(
    title="Smart Search Service",
    description="Microservice for keyword, semantic, and location-aware search",
    version="1.0.0",
    lifespan=lifespan
)

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


@app.get("/health")
async def health_check():
    """Health check endpoint for Smart Search Service."""
    return {"status": "healthy", "service": "smart_search"}


@app.get("/search/doctors")
async def search_doctors(
    query: str = None,
    specialty: str = None,
    latitude: float = None,
    longitude: float = None,
    radius_km: float = None,
    min_rating: float = None,
    sort_by: str = "relevance"
):
    """
    Search doctors by name, specialty, or services using full-text and semantic search.
    Supports location-aware filtering and doctor ranking.
    """
    try:
        if not search_handler:
            raise HTTPException(status_code=503, detail="Search service not initialized")
        
        results = await search_handler.search_doctors(
            query=query,
            specialty=specialty,
            latitude=latitude,
            longitude=longitude,
            radius_km=radius_km,
            min_rating=min_rating,
            sort_by=sort_by
        )
        return {"results": results, "count": len(results)}
    except Exception as error:
        logger.error(f"Doctor search error: {str(error)}")
        raise HTTPException(status_code=500, detail="Search failed")


@app.get("/search/services")
async def search_services(
    query: str = None,
    specialty: str = None,
    latitude: float = None,
    longitude: float = None,
    radius_km: float = None
):
    """
    Search healthcare services by name, description, or specialty.
    Supports location-aware filtering.
    """
    try:
        if not search_handler:
            raise HTTPException(status_code=503, detail="Search service not initialized")
        
        results = await search_handler.search_services(
            query=query,
            specialty=specialty,
            latitude=latitude,
            longitude=longitude,
            radius_km=radius_km
        )
        return {"results": results, "count": len(results)}
    except Exception as error:
        logger.error(f"Service search error: {str(error)}")
        raise HTTPException(status_code=500, detail="Search failed")


@app.get("/search/specialties")
async def search_specialties(query: str = None):
    """
    Search medical specialties by name or description.
    """
    try:
        if not search_handler:
            raise HTTPException(status_code=503, detail="Search service not initialized")
        
        results = await search_handler.search_specialties(query=query)
        return {"results": results, "count": len(results)}
    except Exception as error:
        logger.error(f"Specialty search error: {str(error)}")
        raise HTTPException(status_code=500, detail="Search failed")


@app.get("/search/packages")
async def search_packages(
    query: str = None,
    specialty: str = None,
    max_price: float = None
):
    """
    Search healthcare packages by name, description, or included services.
    """
    try:
        if not search_handler:
            raise HTTPException(status_code=503, detail="Search service not initialized")
        
        results = await search_handler.search_packages(
            query=query,
            specialty=specialty,
            max_price=max_price
        )
        return {"results": results, "count": len(results)}
    except Exception as error:
        logger.error(f"Package search error: {str(error)}")
        raise HTTPException(status_code=500, detail="Search failed")


@app.get("/search/appointments")
async def search_appointments(
    doctor_id: str = None,
    specialty: str = None,
    date_from: str = None,
    date_to: str = None,
    status: str = None
):
    """
    Search appointments by doctor, specialty, date, or status.
    """
    try:
        if not search_handler:
            raise HTTPException(status_code=503, detail="Search service not initialized")
        
        results = await search_handler.search_appointments(
            doctor_id=doctor_id,
            specialty=specialty,
            date_from=date_from,
            date_to=date_to,
            status=status
        )
        return {"results": results, "count": len(results)}
    except Exception as error:
        logger.error(f"Appointment search error: {str(error)}")
        raise HTTPException(status_code=500, detail="Search failed")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)