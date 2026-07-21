import logging
from typing import Optional

logger = logging.getLogger(__name__)


class SecurityGuardrails:
    """Security and validation guardrails for search operations."""

    def __init__(self):
        self.max_query_length = 500
        self.max_results = 1000
        self.blocked_keywords = ["drop", "delete", "truncate", "exec", "script"]
        logger.info("SecurityGuardrails initialized")

    def validate_search_input(
        self,
        query: Optional[str] = None,
        specialty: Optional[str] = None
    ) -> bool:
        """Validate search input for security and sanity."""
        try:
            if query:
                if len(query) > self.max_query_length:
                    logger.warning(f"Query exceeds max length: {len(query)}")
                    raise ValueError(f"Query too long (max {self.max_query_length} characters)")
                
                if self._contains_blocked_keywords(query):
                    logger.warning(f"Query contains blocked keywords: {query}")
                    raise ValueError("Query contains invalid keywords")
            
            if specialty:
                if len(specialty) > 100:
                    logger.warning(f"Specialty exceeds max length: {len(specialty)}")
                    raise ValueError("Specialty too long")
                
                if self._contains_blocked_keywords(specialty):
                    logger.warning(f"Specialty contains blocked keywords: {specialty}")
                    raise ValueError("Specialty contains invalid keywords")
            
            logger.info("Search input validation passed")
            return True
        except Exception as error:
            logger.error(f"Input validation error: {str(error)}")
            raise

    def validate_location_input(
        self,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        radius_km: Optional[float] = None
    ) -> bool:
        """Validate location input parameters."""
        try:
            if latitude is not None:
                if not -90 <= latitude <= 90:
                    raise ValueError("Latitude must be between -90 and 90")
            
            if longitude is not None:
                if not -180 <= longitude <= 180:
                    raise ValueError("Longitude must be between -180 and 180")
            
            if radius_km is not None:
                if radius_km <= 0 or radius_km > 500:
                    raise ValueError("Radius must be between 0 and 500 km")
            
            logger.info("Location input validation passed")
            return True
        except Exception as error:
            logger.error(f"Location validation error: {str(error)}")
            raise

    def _contains_blocked_keywords(self, text: str) -> bool:
        """Check if text contains blocked keywords."""
        text_lower = text.lower()
        for keyword in self.blocked_keywords:
            if keyword in text_lower:
                return True
        return False