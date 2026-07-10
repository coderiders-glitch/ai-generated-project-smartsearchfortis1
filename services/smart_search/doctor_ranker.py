import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class DoctorRanker:
    """Rank and sort search results."""

    def __init__(self):
        logger.info("DoctorRanker initialized")

    def rank_doctors(
        self,
        results: List[Dict[str, Any]],
        sort_by: str = "relevance"
    ) -> List[Dict[str, Any]]:
        """Rank doctors based on specified criteria."""
        try:
            if sort_by == "rating":
                return sorted(results, key=lambda x: x.get("rating", 0), reverse=True)
            elif sort_by == "distance":
                return sorted(results, key=lambda x: x.get("distance_km", float('inf')))
            elif sort_by == "name":
                return sorted(results, key=lambda x: x.get("name", ""))
            else:
                return sorted(
                    results,
                    key=lambda x: (
                        x.get("semantic_score", 0),
                        x.get("rating", 0)
                    ),
                    reverse=True
                )
        except Exception as error:
            logger.error(f"Ranking error: {str(error)}")
            return results

    def rank_results(
        self,
        results: List[Dict[str, Any]],
        sort_by: str = "relevance"
    ) -> List[Dict[str, Any]]:
        """Generic ranking for any result type."""
        try:
            if sort_by == "price":
                return sorted(results, key=lambda x: x.get("price", float('inf')))
            elif sort_by == "name":
                return sorted(results, key=lambda x: x.get("name", ""))
            else:
                return sorted(
                    results,
                    key=lambda x: x.get("semantic_score", 0),
                    reverse=True
                )
        except Exception as error:
            logger.error(f"Ranking error: {str(error)}")
            return results