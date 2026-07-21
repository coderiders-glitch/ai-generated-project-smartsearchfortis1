import logging
from typing import Optional, Dict, List, Any
from dataclasses import dataclass
from datetime import datetime
import os

logger = logging.getLogger(__name__)


@dataclass
class PersonaProfile:
    """Represents a classified user persona."""
    user_id: str
    persona_name: str
    confidence_score: float
    classification_timestamp: datetime
    behavior_signals: Dict[str, Any]
    demographic_signals: Dict[str, Any]
    clinical_signals: Dict[str, Any]
    recommended_actions: List[str]

    def to_dict(self) -> Dict[str, Any]:
        """Convert PersonaProfile to a dictionary with ISO-formatted datetime fields."""
        return {
            "user_id": self.user_id,
            "persona_name": self.persona_name,
            "confidence_score": self.confidence_score,
            "classification_timestamp": self.classification_timestamp.isoformat(),
            "behavior_signals": self.behavior_signals,
            "demographic_signals": self.demographic_signals,
            "clinical_signals": self.clinical_signals,
            "recommended_actions": self.recommended_actions
        }


class PersonaEngine:
    """Main orchestrator for persona classification."""

    PERSONA_TYPES = [
        "Frequent Visitor",
        "Preventive Health Seeker",
        "Chronic Condition Manager",
        "Lapsed User"
    ]

    def __init__(self, behavior_analyzer, demographic_analyzer, clinical_analyzer, classifier):
        """
        Initialize persona engine with analyzer and classifier dependencies.

        Args:
            behavior_analyzer: BehaviorAnalyzer instance
            demographic_analyzer: DemographicAnalyzer instance
            clinical_analyzer: ClinicalAnalyzer instance
            classifier: PersonaClassifier instance
        """
        self.behavior_analyzer = behavior_analyzer
        self.demographic_analyzer = demographic_analyzer
        self.clinical_analyzer = clinical_analyzer
        self.classifier = classifier
        logger.info("PersonaEngine initialized")

    def classify_user(self, user_id: str, user_data: Dict[str, Any]) -> Optional[PersonaProfile]:
        """
        Classify a single user into a persona.

        Args:
            user_id: Unique user identifier
            user_data: Dictionary containing user profile, appointments, health records

        Returns:
            PersonaProfile with classification results or None if classification fails
        """
        try:
            logger.info(f"Classifying user: {user_id}")

            behavior_signals = self.behavior_analyzer.extract_signals(user_id, user_data)
            demographic_signals = self.demographic_analyzer.extract_signals(user_id, user_data)
            clinical_signals = self.clinical_analyzer.extract_signals(user_id, user_data)

            combined_signals = {
                "behavior": behavior_signals,
                "demographic": demographic_signals,
                "clinical": clinical_signals
            }

            persona_name, confidence_score = self.classifier.classify(combined_signals)

            recommended_actions = self._generate_actions(persona_name, combined_signals)

            profile = PersonaProfile(
                user_id=user_id,
                persona_name=persona_name,
                confidence_score=confidence_score,
                classification_timestamp=datetime.utcnow(),
                behavior_signals=behavior_signals,
                demographic_signals=demographic_signals,
                clinical_signals=clinical_signals,
                recommended_actions=recommended_actions
            )

            logger.info(f"User {user_id} classified as {persona_name} (confidence: {confidence_score:.2f})")
            return profile

        except Exception as e:
            logger.error(f"Error classifying user {user_id}: {str(e)}", exc_info=True)
            return None

    def _generate_actions(self, persona_name: str, signals: Dict[str, Any]) -> List[str]:
        """
        Generate recommended actions based on persona and signals.

        Args:
            persona_name: Classified persona type
            signals: Combined behavior, demographic, and clinical signals

        Returns:
            List of recommended actions
        """
        actions = []

        if persona_name == "Frequent Visitor":
            actions.append("Offer loyalty rewards program")
            actions.append("Provide premium appointment scheduling")
            actions.append("Send personalized health tips")

        elif persona_name == "Preventive Health Seeker":
            actions.append("Recommend preventive screening packages")
            actions.append("Send wellness reminders")
            actions.append("Offer health education content")

        elif persona_name == "Chronic Condition Manager":
            actions.append("Enable appointment reminders")
            actions.append("Provide condition-specific resources")
            actions.append("Recommend specialist consultations")
            actions.append("Send medication adherence reminders")

        elif persona_name == "Lapsed User":
            actions.append("Send re-engagement campaign")
            actions.append("Offer special incentives")
            actions.append("Provide health status check-in")

        return actions

    def get_persona_distribution(self, user_ids: List[str], user_data_map: Dict[str, Dict[str, Any]]) -> Dict[str, int]:
        """
        Get distribution of personas across multiple users.

        Args:
            user_ids: List of user identifiers
            user_data_map: Mapping of user_id to user data

        Returns:
            Dictionary with persona counts
        """
        distribution = {persona: 0 for persona in self.PERSONA_TYPES}

        for user_id in user_ids:
            if user_id in user_data_map:
                profile = self.classify_user(user_id, user_data_map[user_id])
                if profile:
                    distribution[profile.persona_name] += 1

        return distribution