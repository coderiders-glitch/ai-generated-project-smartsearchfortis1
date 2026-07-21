import logging
from typing import List, Dict, Any, Optional

from keyword_search import KeywordSearchEngine
from semantic_search import SemanticSearchEngine
from location_filter import LocationFilter
from result_categorizer import ResultCategorizer
from doctor_ranker import DoctorRanker
from guardrails import SecurityGuardrails

logger = logging.getLogger(__name__)


class SearchHandler:
    """Orchestrates all search operations with security and ranking."""

    def __init__(self):
        self.keyword_engine = KeywordSearchEngine()
        self.semantic_engine = SemanticSearchEngine()
        self.location_filter = LocationFilter()
        self.categorizer = ResultCategorizer()
        self.ranker = DoctorRanker()
        self.guardrails = SecurityGuardrails()
        logger.info("SearchHandler initialized")

    async def search_doctors(
        self,
        query: Optional[str] = None,
        specialty: Optional[str] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        radius_km: Optional[float] = None,
        min_rating: Optional[float] = None,
        sort_by: str = "relevance"
    ) -> List[Dict[str, Any]]:
        """Search doctors with keyword, semantic, location, and ranking filters."""
        try:
            self.guardrails.validate_search_input(query, specialty)
            
            results = []
            
            if query:
                keyword_results = self.keyword_engine.search(query, "doctors")
                semantic_results = await self.semantic_engine.search(query, "doctors")
                results = self._merge_results(keyword_results, semantic_results)
            elif specialty:
                results = self.keyword_engine.search(specialty, "doctors")
            else:
                results = self.keyword_engine.get_all("doctors")
            
            if latitude is not None and longitude is not None:
                results = self.location_filter.filter_by_location(
                    results, latitude, longitude, radius_km or 10.0
                )
            
            if min_rating is not None:
                results = [r for r in results if r.get("rating", 0) >= min_rating]
            
            results = self.ranker.rank_doctors(results, sort_by)
            
            return results
        except Exception as error:
            logger.error(f"Doctor search failed: {str(error)}")
            raise

    async def search_services(
        self,
        query: Optional[str] = None,
        specialty: Optional[str] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        radius_km: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """Search healthcare services with location filtering."""
        try:
            self.guardrails.validate_search_input(query, specialty)
            
            results = []
            
            if query:
                keyword_results = self.keyword_engine.search(query, "services")
                semantic_results = await self.semantic_engine.search(query, "services")
                results = self._merge_results(keyword_results, semantic_results)
            elif specialty:
                results = self.keyword_engine.search(specialty, "services")
            else:
                results = self.keyword_engine.get_all("services")
            
            if latitude is not None and longitude is not None:
                results = self.location_filter.filter_by_location(
                    results, latitude, longitude, radius_km or 10.0
                )
            
            return results
        except Exception as error:
            logger.error(f"Service search failed: {str(error)}")
            raise

    async def search_specialties(self, query: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search medical specialties."""
        try:
            self.guardrails.validate_search_input(query, None)
            
            if query:
                keyword_results = self.keyword_engine.search(query, "specialties")
                semantic_results = await self.semantic_engine.search(query, "specialties")
                results = self._merge_results(keyword_results, semantic_results)
            else:
                results = self.keyword_engine.get_all("specialties")
            
            return results
        except Exception as error:
            logger.error(f"Specialty search failed: {str(error)}")
            raise

    async def search_packages(
        self,
        query: Optional[str] = None,
        specialty: Optional[str] = None,
        max_price: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """Search healthcare packages with price filtering."""
        try:
            self.guardrails.validate_search_input(query, specialty)
            
            results = []
            
            if query:
                keyword_results = self.keyword_engine.search(query, "packages")
                semantic_results = await self.semantic_engine.search(query, "packages")
                results = self._merge_results(keyword_results, semantic_results)
            elif specialty:
                results = self.keyword_engine.search(specialty, "packages")
            else:
                results = self.keyword_engine.get_all("packages")
            
            if max_price is not None:
                results = [r for r in results if r.get("price", float('inf')) <= max_price]
            
            return results
        except Exception as error:
            logger.error(f"Package search failed: {str(error)}")
            raise

    async def search_appointments(
        self,
        doctor_id: Optional[str] = None,
        specialty: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Search appointments with filtering."""
        try:
            results = self.keyword_engine.search_appointments(
                doctor_id=doctor_id,
                specialty=specialty,
                date_from=date_from,
                date_to=date_to,
                status=status
            )
            return results
        except Exception as error:
            logger.error(f"Appointment search failed: {str(error)}")
            raise

    def _merge_results(
        self,
        keyword_results: List[Dict[str, Any]],
        semantic_results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Merge keyword and semantic search results, deduplicating by ID."""
        seen_ids = set()
        merged = []
        
        for result in keyword_results:
            result_id = result.get("id")
            if result_id not in seen_ids:
                result["search_type"] = "keyword"
                merged.append(result)
                seen_ids.add(result_id)
        
        for result in semantic_results:
            result_id = result.get("id")
            if result_id not in seen_ids:
                result["search_type"] = "semantic"
                merged.append(result)
                seen_ids.add(result_id)
        
        return merged