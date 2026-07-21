import logging
from typing import List, Optional, Dict, Any

logger = logging.getLogger(__name__)


class DoctorReranker:
    """
    Reranks doctor search results based on user persona, preferences, and medical history.
    """

    def __init__(self):
        self.logger = logger

    def rerank(
        self,
        user_id: str,
        doctors: List[Dict[str, Any]],
        persona_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Rerank doctor search results for a user.

        Args:
            user_id: User identifier
            doctors: List of doctor search results
            persona_id: Optional persona ID

        Returns:
            Reranked list of doctors
        """
        try:
            if not doctors:
                return []

            scored_doctors = []
            for doctor in doctors:
                score = self._calculate_doctor_score(
                    user_id=user_id,
                    doctor=doctor,
                    persona_id=persona_id
                )
                scored_doctors.append({
                    **doctor,
                    "rerank_score": score
                })

            reranked = sorted(
                scored_doctors,
                key=lambda x: x["rerank_score"],
                reverse=True
            )

            self.logger.info(
                f"Reranked {len(reranked)} doctors for user {user_id}"
            )
            return reranked

        except Exception as error:
            self.logger.error(
                f"Error reranking doctors for user {user_id}: {error}"
            )
            raise

    def _calculate_doctor_score(
        self,
        user_id: str,
        doctor: Dict[str, Any],
        persona_id: Optional[str] = None
    ) -> float:
        """
        Calculate rerank score for a doctor.

        Args:
            user_id: User identifier
            doctor: Doctor information
            persona_id: Optional persona ID

        Returns:
            Rerank score (0-100)
        """
        score = 50.0

        if "rating" in doctor:
            normalized_rating = (doctor["rating"] / 5.0) * 100
            score += normalized_rating * 0.25

        if "experience_years" in doctor:
            experience_score = min(100, doctor["experience_years"] * 2)
            score += experience_score * 0.15

        if "availability" in doctor:
            availability_score = 100 if doctor["availability"] else 0
            score += availability_score * 0.2

        if "distance" in doctor:
            distance_score = max(0, 100 - (doctor["distance"] / 10.0))
            score += distance_score * 0.15

        if "consultation_fee" in doctor:
            fee_score = max(0, 100 - (doctor["consultation_fee"] / 500.0))
            score += fee_score * 0.1

        if "specialization" in doctor and persona_id:
            score += self._calculate_specialization_match(
                doctor["specialization"],
                persona_id
            ) * 0.15

        if "patient_reviews_count" in doctor:
            review_score = min(100, doctor["patient_reviews_count"] / 10.0)
            score += review_score * 0.1

        return min(100.0, max(0.0, score))

    def _calculate_specialization_match(
        self,
        specialization: str,
        persona_id: str
    ) -> float:
        """
        Calculate match score between doctor specialization and user persona.

        Args:
            specialization: Doctor's specialization
            persona_id: User's persona ID

        Returns:
            Match score (0-100)
        """
        persona_specialization_map = {
            "cardiology_patient": ["cardiology", "cardiac", "heart"],
            "diabetes_patient": ["endocrinology", "diabetes", "metabolic"],
            "orthopedic_patient": ["orthopedics", "orthopedic", "bone"],
            "mental_health_patient": ["psychiatry", "psychology", "mental"],
            "pediatric_patient": ["pediatrics", "pediatric", "child"],
            "geriatric_patient": ["geriatrics", "geriatric", "elderly"],
            "general_health": ["general", "family", "internal"]
        }

        specializations = persona_specialization_map.get(persona_id, [])
        specialization_lower = specialization.lower()

        for spec in specializations:
            if spec in specialization_lower:
                return 100.0

        return 30.0

    def get_top_doctors(
        self,
        user_id: str,
        doctors: List[Dict[str, Any]],
        limit: int = 5,
        persona_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get top N reranked doctors for a user.

        Args:
            user_id: User identifier
            doctors: List of doctor results
            limit: Maximum number of doctors to return
            persona_id: Optional persona ID

        Returns:
            Top N reranked doctors
        """
        reranked = self.rerank(
            user_id=user_id,
            doctors=doctors,
            persona_id=persona_id
        )
        return reranked[:limit]