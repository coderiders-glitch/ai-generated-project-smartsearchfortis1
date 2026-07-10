import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class ResultCategorizer:
    """Categorize and organize search results."""

    def __init__(self):
        logger.info("ResultCategorizer initialized")

    def categorize_results(
        self,
        results: List[Dict[str, Any]],
        entity_type: str
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Organize results into categories."""
        try:
            if entity_type == "doctors":
                return self._categorize_doctors(results)
            elif entity_type == "services":
                return self._categorize_services(results)
            elif entity_type == "packages":
                return self._categorize_packages(results)
            else:
                return {"uncategorized": results}
        except Exception as error:
            logger.error(f"Categorization error: {str(error)}")
            return {"uncategorized": results}

    def _categorize_doctors(self, results: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Categorize doctors by specialty and rating."""
        categories = {}
        
        for doctor in results:
            specialty = doctor.get("specialty", "Unknown")
            if specialty not in categories:
                categories[specialty] = []
            categories[specialty].append(doctor)
        
        for specialty in categories:
            categories[specialty].sort(key=lambda x: x.get("rating", 0), reverse=True)
        
        logger.info(f"Categorized {len(results)} doctors into {len(categories)} specialties")
        return categories

    def _categorize_services(self, results: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Categorize services by specialty."""
        categories = {}
        
        for service in results:
            specialty = service.get("specialty", "General")
            if specialty not in categories:
                categories[specialty] = []
            categories[specialty].append(service)
        
        logger.info(f"Categorized {len(results)} services into {len(categories)} specialties")
        return categories

    def _categorize_packages(self, results: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Categorize packages by price range."""
        categories = {
            "budget": [],
            "standard": [],
            "premium": []
        }
        
        for package in results:
            price = package.get("price", 0)
            if price < 300:
                categories["budget"].append(package)
            elif price < 800:
                categories["standard"].append(package)
            else:
                categories["premium"].append(package)
        
        logger.info(f"Categorized {len(results)} packages into price ranges")
        return categories