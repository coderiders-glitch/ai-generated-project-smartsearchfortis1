import re
import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import yaml
import os

logger = logging.getLogger(__name__)


@dataclass
class InjectionDetection:
    """Represents a detected injection attempt."""
    injection_type: str
    detected_pattern: str
    risk_level: str
    position: int
    message: str


class PromptInjectionFilter:
    """Detects and filters prompt injection attempts."""

    def __init__(self, config_path: str = "security/guardrails_config.yaml"):
        """Initialize prompt injection filter.

        Args:
            config_path: Path to guardrails configuration file
        """
        self.config = self._load_config(config_path)
        self.blocked_patterns: List[str] = []
        self.blocked_keywords: List[str] = []
        self._load_filters()

    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file.

        Args:
            config_path: Path to configuration file

        Returns:
            Configuration dictionary
        """
        if not os.path.exists(config_path):
            logger.warning(f"Config file not found: {config_path}. Using defaults.")
            return {"prompt_injection": {"enabled": True, "blocked_patterns": []}}

        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
        return config

    def _load_filters(self) -> None:
        """Load injection filters from configuration."""
        injection_config = self.config.get("prompt_injection", {})
        self.blocked_patterns = injection_config.get("blocked_patterns", [])
        self.blocked_keywords = injection_config.get("blocked_keywords", [])

    def detect_injection(self, text: str) -> List[InjectionDetection]:
        """Detect injection attempts in text.

        Args:
            text: Text to scan for injection attempts

        Returns:
            List of detected injection attempts
        """
        if not self.config.get("prompt_injection", {}).get("enabled", False):
            return []

        detections: List[InjectionDetection] = []
        text_lower = text.lower()

        for pattern in self.blocked_patterns:
            if pattern.lower() in text_lower:
                position = text_lower.find(pattern.lower())
                detection = InjectionDetection(
                    injection_type="blocked_pattern",
                    detected_pattern=pattern,
                    risk_level="high",
                    position=position,
                    message=f"Blocked pattern detected: {pattern}",
                )
                detections.append(detection)
                logger.warning(f"Injection attempt detected: {pattern} at position {position}")

        for keyword in self.blocked_keywords:
            if keyword.lower() in text_lower:
                position = text_lower.find(keyword.lower())
                detection = InjectionDetection(
                    injection_type="blocked_keyword",
                    detected_pattern=keyword,
                    risk_level="critical",
                    position=position,
                    message=f"Blocked keyword detected: {keyword}",
                )
                detections.append(detection)
                logger.warning(f"Injection attempt detected: {keyword} at position {position}")

        detections.extend(self._check_length_limits(text))
        detections.extend(self._check_special_char_patterns(text))

        return detections

    def _check_length_limits(self, text: str) -> List[InjectionDetection]:
        """Check if text exceeds length limits.

        Args:
            text: Text to check

        Returns:
            List of length violation detections
        """
        detections: List[InjectionDetection] = []
        max_length = self.config.get("prompt_injection", {}).get("max_prompt_length", 10000)

        if len(text) > max_length:
            detection = InjectionDetection(
                injection_type="length_violation",
                detected_pattern=f"Text length {len(text)}",
                risk_level="medium",
                position=0,
                message=f"Text exceeds maximum length of {max_length}",
            )
            detections.append(detection)
            logger.warning(f"Text length violation: {len(text)} > {max_length}")

        return detections

    def _check_special_char_patterns(self, text: str) -> List[InjectionDetection]:
        """Check for suspicious special character patterns.

        Args:
            text: Text to check

        Returns:
            List of special character pattern detections
        """
        detections: List[InjectionDetection] = []
        max_consecutive = self.config.get("prompt_injection", {}).get(
            "max_consecutive_special_chars", 5
        )

        special_char_pattern = r"[!@#$%^&*()_+=\[\]{};:'\",.<>?/\\|`~-]{" + str(max_consecutive + 1) + ",}"
        matches = re.finditer(special_char_pattern, text)

        for match in matches:
            detection = InjectionDetection(
                injection_type="suspicious_special_chars",
                detected_pattern=match.group(),
                risk_level="low",
                position=match.start(),
                message=f"Suspicious special character sequence detected",
            )
            detections.append(detection)
            logger.warning(
                f"Suspicious special characters at position {match.start()}: {match.group()}"
            )

        return detections

    def is_safe(self, text: str) -> bool:
        """Check if text is safe from injection attempts.

        Args:
            text: Text to check

        Returns:
            True if text is safe
        """
        detections = self.detect_injection(text)
        return len(detections) == 0

    def sanitize(self, text: str) -> str:
        """Sanitize text by removing/escaping suspicious content.

        Args:
            text: Text to sanitize

        Returns:
            Sanitized text
        """
        sanitized = text

        for pattern in self.blocked_patterns:
            sanitized = re.sub(re.escape(pattern), "", sanitized, flags=re.IGNORECASE)

        for keyword in self.blocked_keywords:
            sanitized = re.sub(re.escape(keyword), "", sanitized, flags=re.IGNORECASE)

        return sanitized.strip()

    def get_risk_score(self, text: str) -> float:
        """Calculate risk score for text (0.0 to 1.0).

        Args:
            text: Text to analyze

        Returns:
            Risk score between 0.0 (safe) and 1.0 (dangerous)
        """
        detections = self.detect_injection(text)
        if not detections:
            return 0.0

        risk_weights = {"critical": 1.0, "high": 0.7, "medium": 0.4, "low": 0.1}
        total_risk = sum(risk_weights.get(d.risk_level, 0.0) for d in detections)
        max_possible_risk = len(detections) * 1.0

        return min(total_risk / max(max_possible_risk, 1.0), 1.0)