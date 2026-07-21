import re
import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import yaml
import os

logger = logging.getLogger(__name__)


class SeverityLevel(Enum):
    """Severity levels for PII detection."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class PIIMatch:
    """Represents a detected PII match."""
    pattern_name: str
    matched_text: str
    severity: SeverityLevel
    start_position: int
    end_position: int
    description: str


class PIIDetector:
    """Detects personally identifiable information in text."""

    def __init__(self, config_path: str = "security/guardrails_config.yaml"):
        """Initialize PII detector with configuration.

        Args:
            config_path: Path to guardrails configuration file
        """
        self.config = self._load_config(config_path)
        self.patterns: Dict[str, Dict] = {}
        self.compiled_patterns: Dict[str, re.Pattern] = {}
        self._compile_patterns()

    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file.

        Args:
            config_path: Path to configuration file

        Returns:
            Configuration dictionary
        """
        if not os.path.exists(config_path):
            logger.warning(f"Config file not found: {config_path}. Using defaults.")
            return {"pii_detection": {"enabled": True, "patterns": {}}}

        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
        return config

    def _compile_patterns(self) -> None:
        """Compile regex patterns from configuration."""
        pii_config = self.config.get("pii_detection", {})
        patterns = pii_config.get("patterns", {})

        for pattern_name, pattern_config in patterns.items():
            regex = pattern_config.get("regex")
            if regex:
                try:
                    self.compiled_patterns[pattern_name] = re.compile(
                        regex, re.IGNORECASE
                    )
                    self.patterns[pattern_name] = pattern_config
                except re.error as e:
                    logger.error(f"Invalid regex for {pattern_name}: {e}")

    def detect(self, text: str) -> List[PIIMatch]:
        """Detect PII in text.

        Args:
            text: Text to scan for PII

        Returns:
            List of detected PII matches
        """
        if not self.config.get("pii_detection", {}).get("enabled", False):
            return []

        matches: List[PIIMatch] = []

        for pattern_name, compiled_pattern in self.compiled_patterns.items():
            pattern_config = self.patterns[pattern_name]
            severity_str = pattern_config.get("severity", "low")
            severity = SeverityLevel(severity_str)
            description = pattern_config.get("description", "")

            for match in compiled_pattern.finditer(text):
                pii_match = PIIMatch(
                    pattern_name=pattern_name,
                    matched_text=match.group(),
                    severity=severity,
                    start_position=match.start(),
                    end_position=match.end(),
                    description=description,
                )
                matches.append(pii_match)
                logger.warning(
                    f"PII detected: {pattern_name} ({severity.value}) at "
                    f"position {match.start()}-{match.end()}"
                )

        return matches

    def has_critical_pii(self, text: str) -> bool:
        """Check if text contains critical PII.

        Args:
            text: Text to scan

        Returns:
            True if critical PII is found
        """
        matches = self.detect(text)
        return any(m.severity == SeverityLevel.CRITICAL for m in matches)

    def has_high_pii(self, text: str) -> bool:
        """Check if text contains high-severity PII.

        Args:
            text: Text to scan

        Returns:
            True if high-severity PII is found
        """
        matches = self.detect(text)
        return any(m.severity in [SeverityLevel.CRITICAL, SeverityLevel.HIGH] for m in matches)

    def mask_pii(self, text: str, mask_char: str = "*") -> str:
        """Mask detected PII in text.

        Args:
            text: Text to mask
            mask_char: Character to use for masking

        Returns:
            Text with PII masked
        """
        matches = self.detect(text)
        if not matches:
            return text

        matches_sorted = sorted(matches, key=lambda m: m.start_position, reverse=True)
        result = text

        for match in matches_sorted:
            mask_length = match.end_position - match.start_position
            masked = mask_char * mask_length
            result = (
                result[: match.start_position]
                + masked
                + result[match.end_position :]
            )

        return result

    def get_summary(self, text: str) -> Dict:
        """Get summary of PII detection results.

        Args:
            text: Text to analyze

        Returns:
            Summary dictionary with counts by severity
        """
        matches = self.detect(text)
        summary = {
            "total_matches": len(matches),
            "critical_count": sum(1 for m in matches if m.severity == SeverityLevel.CRITICAL),
            "high_count": sum(1 for m in matches if m.severity == SeverityLevel.HIGH),
            "medium_count": sum(1 for m in matches if m.severity == SeverityLevel.MEDIUM),
            "low_count": sum(1 for m in matches if m.severity == SeverityLevel.LOW),
            "patterns_detected": list(set(m.pattern_name for m in matches)),
        }
        return summary