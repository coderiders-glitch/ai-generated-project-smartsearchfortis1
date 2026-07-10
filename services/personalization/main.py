import os
from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
import logging

from content_prioritizer import ContentPrioritizer
from ranking_engine import RankingEngine
from doctor_reranker import DoctorReranker
from home_screen_personalizer import HomeScreenPersonalizer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Personalization Service", version="1.0.0")

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

content_prioritizer = ContentPrioritizer()
ranking_engine = RankingEngine()
doctor_reranker = DoctorReranker()
home_screen_personalizer = HomeScreenPersonalizer()


@app.get("/health")
async def health_check():
    """Health check endpoint for personalization service."""
    return {"status": "healthy", "service": "personalization"}


@app.post("/personalize/content")
async def personalize_content(
    user_id: str = Query(..., description="User ID"),
    content_items: List[dict] = Query(..., description="Content items to prioritize"),
    persona_id: Optional[str] = Query(None, description="User persona ID")
):
    """
    Prioritize content based on user profile and persona.
    """
    try:
        prioritized_content = content_prioritizer.prioritize(
            user_id=user_id,
            content_items=content_items,
            persona_id=persona_id
        )
        return {"status": "success", "data": prioritized_content}
    except Exception as error:
        logger.error(f"Error prioritizing content: {error}")
        raise HTTPException(status_code=500, detail=str(error))


@app.post("/search/doctors/rerank")
async def rerank_doctors(
    user_id: str = Query(..., description="User ID"),
    doctors: List[dict] = Query(..., description="Doctor search results"),
    persona_id: Optional[str] = Query(None, description="User persona ID")
):
    """
    Rerank doctor search results based on user persona and preferences.
    """
    try:
        reranked_doctors = doctor_reranker.rerank(
            user_id=user_id,
            doctors=doctors,
            persona_id=persona_id
        )
        return {"status": "success", "data": reranked_doctors}
    except Exception as error:
        logger.error(f"Error reranking doctors: {error}")
        raise HTTPException(status_code=500, detail=str(error))


@app.post("/search/rank")
async def rank_search_results(
    user_id: str = Query(..., description="User ID"),
    results: List[dict] = Query(..., description="Search results to rank"),
    result_type: str = Query(..., description="Type of results: doctor, service, specialty, package, appointment"),
    persona_id: Optional[str] = Query(None, description="User persona ID")
):
    """
    Rank search results using the ranking engine.
    """
    try:
        ranked_results = ranking_engine.rank(
            user_id=user_id,
            results=results,
            result_type=result_type,
            persona_id=persona_id
        )
        return {"status": "success", "data": ranked_results}
    except Exception as error:
        logger.error(f"Error ranking results: {error}")
        raise HTTPException(status_code=500, detail=str(error))


@app.get("/home-screen/personalize")
async def personalize_home_screen(
    user_id: str = Query(..., description="User ID"),
    persona_id: Optional[str] = Query(None, description="User persona ID")
):
    """
    Generate personalized home screen content for a user.
    """
    try:
        home_screen_data = home_screen_personalizer.generate(
            user_id=user_id,
            persona_id=persona_id
        )
        return {"status": "success", "data": home_screen_data}
    except Exception as error:
        logger.error(f"Error personalizing home screen: {error}")
        raise HTTPException(status_code=500, detail=str(error))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.getenv("APP_PORT", 8000))
    )