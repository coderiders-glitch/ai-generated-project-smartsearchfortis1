import logging
from typing import Dict, Any, Optional, Union
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class BehaviorAnalyzer:
    """Extracts behavior signals from user appointment and search history."""

    def __init__(self, lookback_days: int = 365):
        """
        Initialize behavior analyzer.

        Args:
            lookback_days: Number of days to analyze historical behavior
        """
        self.lookback_days = lookback_days
        logger.info(f"BehaviorAnalyzer initialized with {lookback_days} day lookback")

    def _parse_date(self, date_value: Union[str, datetime, None]) -> Optional[datetime]:
        """
        Parse date from ISO string or datetime object.

        Args:
            date_value: Date as ISO string, datetime object, or None

        Returns:
            Parsed datetime object or None if input is None

        Raises:
            ValueError: If date string cannot be parsed
        """
        if date_value is None:
            return None
        if isinstance(date_value, datetime):
            return date_value
        if isinstance(date_value, str):
            try:
                return datetime.fromisoformat(date_value.replace('Z', '+00:00'))
            except (ValueError, AttributeError) as e:
                logger.warning(f"Failed to parse date '{date_value}': {e}")
                raise ValueError(f"Invalid date format: {date_value}") from e
        logger.warning(f"Unexpected date type: {type(date_value)}")
        return None

    def extract_signals(self, user_id: str, user_data: Dict[str, Any]) -> Dict[str, float]:
        """
        Extract behavior signals from user data.

        Args:
            user_id: User identifier
            user_data: Dictionary containing appointments and search queries

        Returns:
            Dictionary of behavior signals with scores 0.0-1.0
        """
        try:
            appointments = user_data.get("appointments", [])
            search_queries = user_data.get("search_queries", [])

            signals = {
                "appointment_frequency_score": self._calculate_appointment_frequency(appointments),
                "appointment_recency_score": self._calculate_appointment_recency(appointments),
                "service_diversity_score": self._calculate_service_diversity(appointments),
                "preventive_search_score": self._calculate_preventive_search_score(search_queries),
                "wellness_interest_score": self._calculate_wellness_interest(search_queries),
                "appointment_regularity_score": self._calculate_appointment_regularity(appointments),
                "days_since_last_appointment_score": self._calculate_days_since_last_appointment(appointments),
                "appointment_frequency_decline_score": self._calculate_frequency_decline(appointments),
                "engagement_drop_score": self._calculate_engagement_drop(appointments, search_queries),
                "search_activity_decline_score": self._calculate_search_decline(search_queries)
            }

            logger.debug(f"Behavior signals extracted for user {user_id}")
            return signals

        except Exception as e:
            logger.error(f"Error extracting behavior signals for user {user_id}: {str(e)}")
            return {
                "appointment_frequency_score": 0.0,
                "appointment_recency_score": 0.0,
                "service_diversity_score": 0.0,
                "preventive_search_score": 0.0,
                "wellness_interest_score": 0.0,
                "appointment_regularity_score": 0.0,
                "days_since_last_appointment_score": 0.0,
                "appointment_frequency_decline_score": 0.0,
                "engagement_drop_score": 0.0,
                "search_activity_decline_score": 0.0
            }

    def _calculate_appointment_frequency(self, appointments: list) -> float:
        """
        Calculate appointment frequency score (appointments per month).
        """
        if not appointments:
            return 0.0

        now = datetime.utcnow()
        cutoff_date = now - timedelta(days=self.lookback_days)
        recent_appointments = [
            a for a in appointments
            if self._parse_date(a.get("appointment_date")) and self._parse_date(a.get("appointment_date")) >= cutoff_date
        ]

        if not recent_appointments:
            return 0.0

        months = self.lookback_days / 30.0
        frequency = len(recent_appointments) / months
        return min(frequency / 4.0, 1.0)

    def _calculate_appointment_recency(self, appointments: list) -> float:
        """
        Calculate recency score (how recent was last appointment).
        """
        if not appointments:
            return 0.0

        parsed_dates = [self._parse_date(a.get("appointment_date")) for a in appointments]
        parsed_dates = [d for d in parsed_dates if d is not None]

        if not parsed_dates:
            return 0.0

        last_appointment_date = max(parsed_dates)
        days_ago = (datetime.utcnow() - last_appointment_date).days

        if days_ago <= 0:
            return 1.0
        elif days_ago >= 365:
            return 0.0
        else:
            return 1.0 - (days_ago / 365.0)

    def _calculate_service_diversity(self, appointments: list) -> float:
        """
        Calculate diversity of services used.
        """
        if not appointments:
            return 0.0

        services = set(a.get("service_id") for a in appointments if a.get("service_id"))
        return min(len(services) / 5.0, 1.0)

    def _calculate_preventive_search_score(self, search_queries: list) -> float:
        """
        Calculate score for preventive health searches.
        """
        if not search_queries:
            return 0.0

        preventive_keywords = [
            "screening", "checkup", "vaccination", "prevention",
            "wellness", "health check", "physical exam", "preventive"
        ]

        preventive_searches = [
            q for q in search_queries
            if any(keyword in q.get("query_text", "").lower() for keyword in preventive_keywords)
        ]

        return min(len(preventive_searches) / len(search_queries), 1.0)

    def _calculate_wellness_interest(self, search_queries: list) -> float:
        """
        Calculate score for wellness-related searches.
        """
        if not search_queries:
            return 0.0

        wellness_keywords = [
            "fitness", "nutrition", "diet", "exercise", "yoga",
            "meditation", "mental health", "stress", "sleep"
        ]

        wellness_searches = [
            q for q in search_queries
            if any(keyword in q.get("query_text", "").lower() for keyword in wellness_keywords)
        ]

        return min(len(wellness_searches) / len(search_queries), 1.0)

    def _calculate_appointment_regularity(self, appointments: list) -> float:
        """
        Calculate regularity of appointments (consistency over time).
        """
        if len(appointments) < 2:
            return 0.0

        now = datetime.utcnow()
        cutoff_date = now - timedelta(days=self.lookback_days)
        recent_appointments = [
            self._parse_date(a.get("appointment_date"))
            for a in appointments
            if self._parse_date(a.get("appointment_date")) and self._parse_date(a.get("appointment_date")) >= cutoff_date
        ]
        recent_appointments = [d for d in recent_appointments if d is not None]

        if len(recent_appointments) < 2:
            return 0.0

        recent_appointments.sort()
        intervals = [
            (recent_appointments[i+1] - recent_appointments[i]).days
            for i in range(len(recent_appointments) - 1)
        ]

        if not intervals:
            return 0.0

        avg_interval = sum(intervals) / len(intervals)
        std_dev = (sum((x - avg_interval) ** 2 for x in intervals) / len(intervals)) ** 0.5

        regularity = 1.0 - min(std_dev / 90.0, 1.0)
        return max(regularity, 0.0)

    def _calculate_days_since_last_appointment(self, appointments: list) -> float:
        """
        Calculate score based on days since last appointment.
        Returns 1.0 (high lapsed score) if no appointments, 0.0 if recent.
        """
        if not appointments:
            return 1.0

        parsed_dates = [self._parse_date(a.get("appointment_date")) for a in appointments]
        parsed_dates = [d for d in parsed_dates if d is not None]

        if not parsed_dates:
            return 1.0

        last_appointment_date = max(parsed_dates)
        days_ago = (datetime.utcnow() - last_appointment_date).days

        if days_ago <= 0:
            return 0.0
        elif days_ago >= 365:
            return 1.0
        else:
            return days_ago / 365.0

    def _calculate_frequency_decline(self, appointments: list) -> float:
        """
        Calculate score for declining appointment frequency.
        Compares recent 6 months to prior 6 months.
        """
        if len(appointments) < 4:
            return 0.0

        now = datetime.utcnow()
        six_months_ago = now - timedelta(days=180)
        year_ago = now - timedelta(days=365)

        recent_count = len([
            a for a in appointments
            if self._parse_date(a.get("appointment_date")) and self._parse_date(a.get("appointment_date")) >= six_months_ago
        ])
        older_count = len([
            a for a in appointments
            if self._parse_date(a.get("appointment_date")) and year_ago <= self._parse_date(a.get("appointment_date")) < six_months_ago
        ])

        if older_count == 0:
            return 0.0

        decline_ratio = 1.0 - (recent_count / older_count)
        return max(min(decline_ratio, 1.0), 0.0)

    def _calculate_engagement_drop(self, appointments: list, search_queries: list) -> float:
        """
        Calculate overall engagement drop score.
        Checks if there is any activity in the last 3 months.
        """
        now = datetime.utcnow()
        three_months_ago = now - timedelta(days=90)

        recent_appointments = len([
            a for a in appointments
            if self._parse_date(a.get("appointment_date")) and self._parse_date(a.get("appointment_date")) >= three_months_ago
        ])
        recent_searches = len([
            q for q in search_queries
            if self._parse_date(q.get("created_at")) and self._parse_date(q.get("created_at")) >= three_months_ago
        ])

        total_recent_activity = recent_appointments + recent_searches
        return 1.0 if total_recent_activity == 0 else 0.0

    def _calculate_search_decline(self, search_queries: list) -> float:
        """
        Calculate score for declining search activity.
        Compares recent 3 months to prior 3 months.
        """
        if len(search_queries) < 2:
            return 0.0

        now = datetime.utcnow()
        three_months_ago = now - timedelta(days=90)
        six_months_ago = now - timedelta(days=180)

        recent_searches = len([
            q for q in search_queries
            if self._parse_date(q.get("created_at")) and self._parse_date(q.get("created_at")) >= three_months_ago
        ])
        older_searches = len([
            q for q in search_queries
            if self._parse_date(q.get("created_at")) and six_months_ago <= self._parse_date(q.get("created_at")) < three_months_ago
        ])

        if older_searches == 0:
            return 0.0

        decline_ratio = 1.0 - (recent_searches / older_searches)
        return max(min(decline_ratio, 1.0), 0.0)