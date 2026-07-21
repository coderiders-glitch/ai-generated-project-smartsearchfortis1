import logging
from typing import List, Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class ContentPrioritizer:
    """
    Prioritizes content items based on user profile, persona, and engagement history.
    """

    def __init__(self):
        self.logger = logger

    def prioritize(
        self,
        user_id: str,
        content_items: List[Dict[str, Any]],
        persona_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Prioritize content items for a user based on their persona and preferences.

        Args:
            user_id: Unique user identifier
            content_items: List of content items to prioritize
            persona_id: Optional persona ID for the user

        Returns:
            Prioritized list of content items
        """
        try:
            if not content_items:
                return []

            scored_items = []
            for item in content_items:
                score = self._calculate_priority_score(
                    user_id=user_id,
                    item=item,
                    persona_id=persona_id
                )
                scored_items.append({
                    **item,
                    "priority_score": score
                })

            prioritized = sorted(
                scored_items,
                key=lambda x: x["priority_score"],
                reverse=True
            )

            self.logger.info(
                f"Prioritized {len(prioritized)} content items for user {user_id}"
            )
            return prioritized

        except Exception as error:
            self.logger.error(
                f"Error prioritizing content for user {user_id}: {error}"
            )
            raise

    def _calculate_priority_score(
        self,
        user_id: str,
        item: Dict[str, Any],
        persona_id: Optional[str] = None
    ) -> float:
        """
        Calculate priority score for a content item.

        Args:
            user_id: User identifier
            item: Content item to score
            persona_id: Optional persona ID

        Returns:
            Priority score (0-100)
        """
        base_score = 50.0

        if "relevance_score" in item:
            base_score += item["relevance_score"] * 0.3

        if "engagement_score" in item:
            base_score += item["engagement_score"] * 0.2

        if "recency_score" in item:
            base_score += item["recency_score"] * 0.15

        if persona_id and "persona_affinity" in item:
            base_score += item["persona_affinity"] * 0.35

        return min(100.0, max(0.0, base_score))

    def get_top_content(
        self,
        user_id: str,
        content_items: List[Dict[str, Any]],
        limit: int = 10,
        persona_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get top N prioritized content items for a user.

        Args:
            user_id: User identifier
            content_items: List of content items
            limit: Maximum number of items to return
            persona_id: Optional persona ID

        Returns:
            Top N prioritized content items
        """
        prioritized = self.prioritize(
            user_id=user_id,
            content_items=content_items,
            persona_id=persona_id
        )
        return prioritized[:limit]