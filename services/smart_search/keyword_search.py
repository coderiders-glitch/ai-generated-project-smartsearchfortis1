import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class KeywordSearchEngine:
    """Full-text keyword search engine for healthcare entities."""

    def __init__(self):
        self.mock_data = self._initialize_mock_data()
        logger.info("KeywordSearchEngine initialized")

    def _initialize_mock_data(self) -> Dict[str, List[Dict[str, Any]]]:
        """Initialize mock data for demonstration."""
        return {
            "doctors": [
                {
                    "id": "doc_001",
                    "name": "Dr. Sarah Johnson",
                    "specialty": "Cardiology",
                    "rating": 4.8,
                    "latitude": 40.7128,
                    "longitude": -74.0060,
                    "services": ["Heart Checkup", "ECG", "Stress Test"]
                },
                {
                    "id": "doc_002",
                    "name": "Dr. Michael Chen",
                    "specialty": "Neurology",
                    "rating": 4.6,
                    "latitude": 40.7580,
                    "longitude": -73.9855,
                    "services": ["Neurological Exam", "EEG", "MRI Consultation"]
                }
            ],
            "services": [
                {
                    "id": "svc_001",
                    "name": "Heart Checkup",
                    "description": "Comprehensive cardiovascular assessment",
                    "specialty": "Cardiology",
                    "latitude": 40.7128,
                    "longitude": -74.0060
                },
                {
                    "id": "svc_002",
                    "name": "Neurological Exam",
                    "description": "Complete neurological evaluation",
                    "specialty": "Neurology",
                    "latitude": 40.7580,
                    "longitude": -73.9855
                }
            ],
            "specialties": [
                {"id": "spec_001", "name": "Cardiology", "description": "Heart and cardiovascular diseases"},
                {"id": "spec_002", "name": "Neurology", "description": "Nervous system disorders"}
            ],
            "packages": [
                {
                    "id": "pkg_001",
                    "name": "Cardiac Health Package",
                    "description": "Complete heart health assessment",
                    "price": 500.0,
                    "specialty": "Cardiology",
                    "services": ["Heart Checkup", "ECG", "Stress Test"]
                }
            ]
        }

    def search(self, query: str, entity_type: str) -> List[Dict[str, Any]]:
        """Perform keyword search on specified entity type."""
        try:
            if entity_type not in self.mock_data:
                logger.warning(f"Unknown entity type: {entity_type}")
                return []
            
            query_lower = query.lower()
            results = []
            
            for item in self.mock_data[entity_type]:
                if self._matches_query(item, query_lower):
                    results.append(item)
            
            logger.info(f"Keyword search for '{query}' in {entity_type}: {len(results)} results")
            return results
        except Exception as error:
            logger.error(f"Keyword search error: {str(error)}")
            return []

    def get_all(self, entity_type: str) -> List[Dict[str, Any]]:
        """Retrieve all entities of a given type."""
        try:
            if entity_type not in self.mock_data:
                logger.warning(f"Unknown entity type: {entity_type}")
                return []
            return self.mock_data[entity_type]
        except Exception as error:
            logger.error(f"Get all error: {str(error)}")
            return []

    def search_appointments(
        self,
        doctor_id: Optional[str] = None,
        specialty: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Search appointments with multiple filters."""
        try:
            mock_appointments = [
                {
                    "id": "apt_001",
                    "doctor_id": "doc_001",
                    "specialty": "Cardiology",
                    "date": "2024-02-15",
                    "time": "10:00",
                    "status": "available"
                },
                {
                    "id": "apt_002",
                    "doctor_id": "doc_002",
                    "specialty": "Neurology",
                    "date": "2024-02-16",
                    "time": "14:00",
                    "status": "available"
                }
            ]
            
            results = mock_appointments
            
            if doctor_id:
                results = [a for a in results if a.get("doctor_id") == doctor_id]
            if specialty:
                results = [a for a in results if a.get("specialty", "").lower() == specialty.lower()]
            if status:
                results = [a for a in results if a.get("status", "").lower() == status.lower()]
            
            logger.info(f"Appointment search: {len(results)} results")
            return results
        except Exception as error:
            logger.error(f"Appointment search error: {str(error)}")
            return []

    def _matches_query(self, item: Dict[str, Any], query_lower: str) -> bool:
        """Check if item matches query string."""
        searchable_fields = ["name", "description", "specialty"]
        for field in searchable_fields:
            if field in item:
                field_value = str(item[field]).lower()
                if query_lower in field_value:
                    return True
        return False