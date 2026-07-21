import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class ClinicalAnalyzer:
    """Extracts clinical signals from health records and medical history."""

    def __init__(self):
        """
        Initialize clinical analyzer.
        """
        self.chronic_conditions = [
            "diabetes", "hypertension", "asthma", "copd",
            "heart disease", "arthritis", "thyroid", "kidney disease",
            "liver disease", "cancer", "depression", "anxiety"
        ]
        logger.info("ClinicalAnalyzer initialized")

    def extract_signals(self, user_id: str, user_data: Dict[str, Any]) -> Dict[str, float]:
        """
        Extract clinical signals from health records.

        Args:
            user_id: User identifier
            user_data: Dictionary containing health records and medical history

        Returns:
            Dictionary of clinical signals with scores 0.0-1.0
        """
        try:
            health_records = user_data.get("health_records", [])
            medical_history = user_data.get("medical_history", {})

            signals = {
                "chronic_condition_score": self._calculate_chronic_condition_score(
                    health_records, medical_history
                ),
                "specialist_visit_score": self._calculate_specialist_visit_score(health_records),
                "health_record_update_score": self._calculate_health_record_update_score(health_records),
                "medication_count_score": self._calculate_medication_count_score(medical_history),
                "comorbidity_score": self._calculate_comorbidity_score(medical_history)
            }

            logger.debug(f"Clinical signals extracted for user {user_id}")
            return signals

        except Exception as e:
            logger.error(f"Error extracting clinical signals for user {user_id}: {str(e)}")
            return {
                "chronic_condition_score": 0.0,
                "specialist_visit_score": 0.0,
                "health_record_update_score": 0.0,
                "medication_count_score": 0.0,
                "comorbidity_score": 0.0
            }

    def _calculate_chronic_condition_score(self, health_records: List[Dict], medical_history: Dict) -> float:
        """
        Calculate score based on presence of chronic conditions.
        """
        conditions = medical_history.get("conditions", [])
        if not conditions:
            return 0.0

        chronic_count = 0
        for condition in conditions:
            condition_name = condition.get("name", "").lower() if isinstance(condition, dict) else str(condition).lower()
            if any(chronic in condition_name for chronic in self.chronic_conditions):
                chronic_count += 1

        return min(chronic_count / 4.0, 1.0)

    def _calculate_specialist_visit_score(self, health_records: List[Dict]) -> float:
        """
        Calculate score based on specialist visit frequency.
        """
        if not health_records:
            return 0.0

        specialist_visits = [
            r for r in health_records
            if r.get("visit_type", "").lower() == "specialist"
        ]

        specialist_ratio = len(specialist_visits) / len(health_records)
        return min(specialist_ratio * 2.0, 1.0)

    def _calculate_health_record_update_score(self, health_records: List[Dict]) -> float:
        """
        Calculate score based on frequency of health record updates.
        """
        if not health_records:
            return 0.0

        return min(len(health_records) / 10.0, 1.0)

    def _calculate_medication_count_score(self, medical_history: Dict) -> float:
        """
        Calculate score based on number of current medications.
        """
        medications = medical_history.get("medications", [])
        if not medications:
            return 0.0

        return min(len(medications) / 5.0, 1.0)

    def _calculate_comorbidity_score(self, medical_history: Dict) -> float:
        """
        Calculate score based on presence of multiple conditions (comorbidity).
        """
        conditions = medical_history.get("conditions", [])
        if not conditions:
            return 0.0

        return min(len(conditions) / 4.0, 1.0)