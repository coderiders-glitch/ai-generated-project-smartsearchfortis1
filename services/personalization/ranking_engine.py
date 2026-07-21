import logging
from typing import List, Optional, Dict, Any
from enum import Enum

logger = logging.getLogger(__name__)


class ResultType(str, Enum):
    """Supported search result types."""
    DOCTOR = "doctor"
    SERVICE = "service"
    SPECIALTY = "specialty"
    PACKAGE = "package"
    APPOINTMENT = "appointment"


class RankingEngine:
    """
    Ranks search results based on user persona, preferences, and relevance signals.
    """

    def __init__(self):
        self.logger = logger
        self.result_type_weights = {
            ResultType.DOCTOR: {"relevance": 0.35, "rating": 0.25, "availability": 0.2, "distance": 0.2},
            ResultType.SERVICE: {"relevance": 0.4, "rating": 0.3, "price": 0.2, "availability": 0.1},
            ResultType.SPECIALTY: {"relevance": 0.5, "popularity": 0.3, "rating": 0.2},
            ResultType.PACKAGE: {"relevance": 0.35, "value": 0.3, "rating": 0.2, "price": 0.15},
            ResultType.APPOINTMENT: {"relevance": 0.3, "availability": 0.4, "distance": 0.2, "price": 0.1}
        }

    def rank(
        self,
        user_id: str,
        results: List[Dict[str, Any]],
        result_type: str,
        persona_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Rank search results based on user context and result type.

        Args:
            user_id: User identifier
            results: List of search results to rank
            result_type: Type of results (doctor, service, specialty, package, appointment)
            persona_id: Optional persona ID

        Returns:
            Ranked list of results
        """
        try:
            if not results:
                return []

            result_type_enum = ResultType(result_type.lower())
            weights = self.result_type_weights.get(
                result_type_enum,
                {"relevance": 1.0}
            )

            scored_results = []
            for result in results:
                score = self._calculate_ranking_score(
                    user_id=user_id,
                    result=result,
                    result_type=result_type_enum,
                    weights=weights,
                    persona_id=persona_id
                )
                scored_results.append({
                    **result,
                    "ranking_score": score
                })

            ranked = sorted(
                scored_results,
                key=lambda x: x["ranking_score"],
                reverse=True
            )

            self.logger.info(
                f"Ranked {len(ranked)} {result_type} results for user {user_id}"
            )
            return ranked

        except ValueError as error:
            self.logger.error(f"Invalid result type: {result_type}")
            raise
        except Exception as error:
            self.logger.error(
                f"Error ranking {result_type} results for user {user_id}: {error}"
            )
            raise

    def _calculate_ranking_score(
        self,
        user_id: str,
        result: Dict[str, Any],
        result_type: ResultType,
        weights: Dict[str, float],
        persona_id: Optional[str] = None
    ) -> float:
        """
        Calculate ranking score for a single result.

        Args:
            user_id: User identifier
            result: Result item to score
            result_type: Type of result
            weights: Scoring weights for this result type
            persona_id: Optional persona ID

        Returns:
            Ranking score (0-100)
        """
        score = 0.0

        if "relevance_score" in result and "relevance" in weights:
            score += result["relevance_score"] * weights["relevance"]

        if "rating" in result and "rating" in weights:
            normalized_rating = (result["rating"] / 5.0) * 100
            score += normalized_rating * weights["rating"]

        if "availability" in result and "availability" in weights:
            availability_score = 100 if result["availability"] else 0
            score += availability_score * weights["availability"]

        if "distance" in result and "distance" in weights:
            distance_score = max(0, 100 - (result["distance"] / 10.0))
            score += distance_score * weights["distance"]

        if "price" in result and "price" in weights:
            price_score = max(0, 100 - (result["price"] / 1000.0))
            score += price_score * weights["price"]

        if "value" in result and "value" in weights:
            score += result["value"] * weights["value"]

        if "popularity" in result and "popularity" in weights:
            score += result["popularity"] * weights["popularity"]

        if persona_id and "persona_match_score" in result:
            score += result["persona_match_score"] * 0.15

        return min(100.0, max(0.0, score))