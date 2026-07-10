import logging
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class DemographicAnalyzer:
    """Extracts demographic signals from user profile data."""

    def __init__(self):
        """
        Initialize demographic analyzer.
        """
        logger.info("DemographicAnalyzer initialized")

    def extract_signals(self, user_id: str, user_data: Dict[str, Any]) -> Dict[str, float]:
        """
        Extract demographic signals from user profile.

        Args:
            user_id: User identifier
            user_data: Dictionary containing user profile information

        Returns:
            Dictionary of demographic signals with scores 0.0-1.0
        """
        try:
            profile = user_data.get("profile", {})

            signals = {
                "age_factor_score": self._calculate_age_factor(profile),
                "gender_factor_score": self._calculate_gender_factor(profile),
                "location_factor_score": self._calculate_location_factor(profile),
                "income_factor_score": self._calculate_income_factor(profile),
                "education_factor_score": self._calculate_education_factor(profile)
            }

            logger.debug(f"Demographic signals extracted for user {user_id}")
            return signals

        except Exception as e:
            logger.error(f"Error extracting demographic signals for user {user_id}: {str(e)}")
            return {
                "age_factor_score": 0.0,
                "gender_factor_score": 0.0,
                "location_factor_score": 0.0,
                "income_factor_score": 0.0,
                "education_factor_score": 0.0
            }

    def _calculate_age_factor(self, profile: Dict[str, Any]) -> float:
        """
        Calculate age factor score.
        Older users (50+) score higher for chronic condition management.
        Younger users (18-40) score higher for preventive health.
        """
        date_of_birth = profile.get("date_of_birth")
        if not date_of_birth:
            return 0.5

        try:
            if isinstance(date_of_birth, str):
                dob = datetime.fromisoformat(date_of_birth.replace('Z', '+00:00'))
            else:
                dob = date_of_birth

            age = (datetime.utcnow() - dob).days / 365.25

            if age < 18:
                return 0.1
            elif age < 30:
                return 0.3
            elif age < 40:
                return 0.5
            elif age < 50:
                return 0.7
            elif age < 60:
                return 0.9
            else:
                return 1.0

        except (ValueError, TypeError, AttributeError):
            return 0.5

    def _calculate_gender_factor(self, profile: Dict[str, Any]) -> float:
        """
        Calculate gender factor score.
        Returns neutral score as gender alone doesn't determine persona.
        """
        return 0.5

    def _calculate_location_factor(self, profile: Dict[str, Any]) -> float:
        """
        Calculate location factor score.
        Urban areas may have better healthcare access.
        """
        location = profile.get("location", {})
        if not location:
            return 0.5

        area_type = location.get("area_type", "").lower()
        if area_type == "urban":
            return 0.8
        elif area_type == "suburban":
            return 0.6
        elif area_type == "rural":
            return 0.4
        else:
            return 0.5

    def _calculate_income_factor(self, profile: Dict[str, Any]) -> float:
        """
        Calculate income factor score.
        Higher income may correlate with preventive health seeking.
        """
        income_bracket = profile.get("income_bracket", "").lower()
        if not income_bracket:
            return 0.5

        if "high" in income_bracket or "upper" in income_bracket:
            return 0.8
        elif "middle" in income_bracket or "medium" in income_bracket:
            return 0.6
        elif "low" in income_bracket or "lower" in income_bracket:
            return 0.4
        else:
            return 0.5

    def _calculate_education_factor(self, profile: Dict[str, Any]) -> float:
        """
        Calculate education factor score.
        Higher education may correlate with preventive health awareness.
        """
        education = profile.get("education_level", "").lower()
        if not education:
            return 0.5

        if "phd" in education or "doctorate" in education:
            return 1.0
        elif "master" in education or "graduate" in education:
            return 0.85
        elif "bachelor" in education or "degree" in education:
            return 0.7
        elif "high school" in education or "secondary" in education:
            return 0.5
        elif "primary" in education or "elementary" in education:
            return 0.3
        else:
            return 0.5