import logging
from typing import Tuple, Dict, Any
import json

logger = logging.getLogger(__name__)


class PersonaClassifier:
    """Classifies users into personas based on combined signals."""

    def __init__(self):
        """
        Initialize classifier with persona thresholds and weights.
        """
        self.persona_weights = {
            "Frequent Visitor": {
                "appointment_frequency": 0.35,
                "appointment_recency": 0.25,
                "service_diversity": 0.20,
                "age_factor": 0.10,
                "chronic_conditions": 0.10
            },
            "Preventive Health Seeker": {
                "preventive_searches": 0.30,
                "wellness_interest": 0.25,
                "appointment_regularity": 0.20,
                "age_factor": 0.15,
                "chronic_conditions": 0.10
            },
            "Chronic Condition Manager": {
                "chronic_conditions": 0.35,
                "appointment_frequency": 0.25,
                "specialist_visits": 0.20,
                "health_record_updates": 0.15,
                "age_factor": 0.05
            },
            "Lapsed User": {
                "days_since_last_appointment": 0.40,
                "appointment_frequency_decline": 0.30,
                "engagement_drop": 0.20,
                "search_activity_decline": 0.10
            }
        }
        logger.info("PersonaClassifier initialized")

    def classify(self, signals: Dict[str, Any]) -> Tuple[str, float]:
        """
        Classify user into persona based on combined signals.

        Args:
            signals: Dictionary with 'behavior', 'demographic', 'clinical' keys

        Returns:
            Tuple of (persona_name, confidence_score)
        """
        try:
            behavior_signals = signals.get("behavior", {})
            demographic_signals = signals.get("demographic", {})
            clinical_signals = signals.get("clinical", {})

            if not behavior_signals and not demographic_signals and not clinical_signals:
                logger.warning("No signals provided for classification")
                raise ValueError("Empty signals dictionary")

            scores = {}

            scores["Frequent Visitor"] = self._calculate_frequent_visitor_score(
                behavior_signals, demographic_signals, clinical_signals
            )

            scores["Preventive Health Seeker"] = self._calculate_preventive_seeker_score(
                behavior_signals, demographic_signals, clinical_signals
            )

            scores["Chronic Condition Manager"] = self._calculate_chronic_manager_score(
                behavior_signals, demographic_signals, clinical_signals
            )

            scores["Lapsed User"] = self._calculate_lapsed_user_score(
                behavior_signals, demographic_signals, clinical_signals
            )

            persona_name = max(scores, key=scores.get)
            confidence_score = scores[persona_name]

            logger.debug(f"Classification scores: {json.dumps(scores, indent=2)}")
            return persona_name, confidence_score

        except ValueError as e:
            logger.error(f"Validation error in classification: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in classification: {str(e)}", exc_info=True)
            raise

    def _calculate_frequent_visitor_score(self, behavior: Dict, demographic: Dict, clinical: Dict) -> float:
        """
        Calculate score for Frequent Visitor persona.
        """
        score = 0.0
        weights = self.persona_weights["Frequent Visitor"]

        appointment_frequency = behavior.get("appointment_frequency_score", 0.0)
        score += appointment_frequency * weights["appointment_frequency"]

        appointment_recency = behavior.get("appointment_recency_score", 0.0)
        score += appointment_recency * weights["appointment_recency"]

        service_diversity = behavior.get("service_diversity_score", 0.0)
        score += service_diversity * weights["service_diversity"]

        age_factor = demographic.get("age_factor_score", 0.0)
        score += age_factor * weights["age_factor"]

        chronic_factor = 1.0 - clinical.get("chronic_condition_score", 0.0)
        score += chronic_factor * weights["chronic_conditions"]

        return min(score, 1.0)

    def _calculate_preventive_seeker_score(self, behavior: Dict, demographic: Dict, clinical: Dict) -> float:
        """
        Calculate score for Preventive Health Seeker persona.
        """
        score = 0.0
        weights = self.persona_weights["Preventive Health Seeker"]

        preventive_searches = behavior.get("preventive_search_score", 0.0)
        score += preventive_searches * weights["preventive_searches"]

        wellness_interest = behavior.get("wellness_interest_score", 0.0)
        score += wellness_interest * weights["wellness_interest"]

        appointment_regularity = behavior.get("appointment_regularity_score", 0.0)
        score += appointment_regularity * weights["appointment_regularity"]

        age_factor = demographic.get("age_factor_score", 0.0)
        score += age_factor * weights["age_factor"]

        chronic_factor = 1.0 - clinical.get("chronic_condition_score", 0.0)
        score += chronic_factor * weights["chronic_conditions"]

        return min(score, 1.0)

    def _calculate_chronic_manager_score(self, behavior: Dict, demographic: Dict, clinical: Dict) -> float:
        """
        Calculate score for Chronic Condition Manager persona.
        """
        score = 0.0
        weights = self.persona_weights["Chronic Condition Manager"]

        chronic_conditions = clinical.get("chronic_condition_score", 0.0)
        score += chronic_conditions * weights["chronic_conditions"]

        appointment_frequency = behavior.get("appointment_frequency_score", 0.0)
        score += appointment_frequency * weights["appointment_frequency"]

        specialist_visits = clinical.get("specialist_visit_score", 0.0)
        score += specialist_visits * weights["specialist_visits"]

        health_record_updates = clinical.get("health_record_update_score", 0.0)
        score += health_record_updates * weights["health_record_updates"]

        age_factor = demographic.get("age_factor_score", 0.0)
        score += age_factor * weights["age_factor"]

        return min(score, 1.0)

    def _calculate_lapsed_user_score(self, behavior: Dict, demographic: Dict, clinical: Dict) -> float:
        """
        Calculate score for Lapsed User persona.
        """
        score = 0.0
        weights = self.persona_weights["Lapsed User"]

        days_since_appointment = behavior.get("days_since_last_appointment_score", 0.0)
        score += days_since_appointment * weights["days_since_last_appointment"]

        frequency_decline = behavior.get("appointment_frequency_decline_score", 0.0)
        score += frequency_decline * weights["appointment_frequency_decline"]

        engagement_drop = behavior.get("engagement_drop_score", 0.0)
        score += engagement_drop * weights["engagement_drop"]

        search_decline = behavior.get("search_activity_decline_score", 0.0)
        score += search_decline * weights["search_activity_decline"]

        return min(score, 1.0)