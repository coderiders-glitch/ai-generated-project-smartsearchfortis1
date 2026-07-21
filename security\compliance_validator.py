import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import yaml
import os

logger = logging.getLogger(__name__)


@dataclass
class ComplianceViolation:
    """Represents a compliance violation."""
    framework: str
    requirement: str
    violation_type: str
    severity: str
    message: str
    remediation: str


class ComplianceValidator:
    """Validates compliance with HIPAA, GDPR, and CCPA requirements."""

    def __init__(self, config_path: str = "security/guardrails_config.yaml"):
        """Initialize compliance validator.

        Args:
            config_path: Path to guardrails configuration file
        """
        self.config = self._load_config(config_path)
        self.violations: List[ComplianceViolation] = []

    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file.

        Args:
            config_path: Path to configuration file

        Returns:
            Configuration dictionary
        """
        if not os.path.exists(config_path):
            return {"compliance": {"hipaa": {"enabled": True}}}

        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
        return config

    def validate_hipaa(self, data: Dict) -> List[ComplianceViolation]:
        """Validate HIPAA compliance requirements.

        Args:
            data: Data to validate

        Returns:
            List of HIPAA violations found
        """
        hipaa_config = self.config.get("compliance", {}).get("hipaa", {})
        if not hipaa_config.get("enabled", False):
            return []

        violations: List[ComplianceViolation] = []

        if hipaa_config.get("require_encryption", False):
            if not self._check_encryption(data):
                violations.append(
                    ComplianceViolation(
                        framework="HIPAA",
                        requirement="Encryption",
                        violation_type="missing_encryption",
                        severity="critical",
                        message="Protected Health Information (PHI) must be encrypted",
                        remediation="Enable encryption for all PHI data",
                    )
                )

        if hipaa_config.get("require_audit_logging", False):
            if not self._check_audit_logging():
                violations.append(
                    ComplianceViolation(
                        framework="HIPAA",
                        requirement="Audit Logging",
                        violation_type="missing_audit_logging",
                        severity="critical",
                        message="All access to PHI must be logged",
                        remediation="Enable comprehensive audit logging",
                    )
                )

        if hipaa_config.get("require_access_controls", False):
            if not self._check_access_controls(data):
                violations.append(
                    ComplianceViolation(
                        framework="HIPAA",
                        requirement="Access Controls",
                        violation_type="missing_access_controls",
                        severity="critical",
                        message="Access to PHI must be restricted to authorized users",
                        remediation="Implement role-based access controls (RBAC)",
                    )
                )

        if hipaa_config.get("require_authentication", False):
            if not self._check_authentication(data):
                violations.append(
                    ComplianceViolation(
                        framework="HIPAA",
                        requirement="Authentication",
                        violation_type="missing_authentication",
                        severity="critical",
                        message="Users must be authenticated before accessing PHI",
                        remediation="Implement strong authentication mechanisms",
                    )
                )

        return violations

    def validate_gdpr(self, data: Dict) -> List[ComplianceViolation]:
        """Validate GDPR compliance requirements.

        Args:
            data: Data to validate

        Returns:
            List of GDPR violations found
        """
        gdpr_config = self.config.get("compliance", {}).get("gdpr", {})
        if not gdpr_config.get("enabled", False):
            return []

        violations: List[ComplianceViolation] = []

        if gdpr_config.get("require_consent", False):
            if not self._check_consent(data):
                violations.append(
                    ComplianceViolation(
                        framework="GDPR",
                        requirement="Consent",
                        violation_type="missing_consent",
                        severity="critical",
                        message="Explicit consent required for personal data processing",
                        remediation="Obtain and document user consent",
                    )
                )

        if gdpr_config.get("require_data_minimization", False):
            if not self._check_data_minimization(data):
                violations.append(
                    ComplianceViolation(
                        framework="GDPR",
                        requirement="Data Minimization",
                        violation_type="excessive_data_collection",
                        severity="high",
                        message="Only necessary personal data should be collected",
                        remediation="Review and reduce collected data to minimum required",
                    )
                )

        if gdpr_config.get("require_storage_limitation", False):
            retention_days = gdpr_config.get("data_retention_days", 2555)
            if not self._check_storage_limitation(data, retention_days):
                violations.append(
                    ComplianceViolation(
                        framework="GDPR",
                        requirement="Storage Limitation",
                        violation_type="excessive_retention",
                        severity="high",
                        message=f"Personal data must not be retained longer than {retention_days} days",
                        remediation="Implement data retention and deletion policies",
                    )
                )

        return violations

    def validate_ccpa(self, data: Dict) -> List[ComplianceViolation]:
        """Validate CCPA compliance requirements.

        Args:
            data: Data to validate

        Returns:
            List of CCPA violations found
        """
        ccpa_config = self.config.get("compliance", {}).get("ccpa", {})
        if not ccpa_config.get("enabled", False):
            return []

        violations: List[ComplianceViolation] = []

        if ccpa_config.get("require_opt_out", False):
            if not self._check_opt_out(data):
                violations.append(
                    ComplianceViolation(
                        framework="CCPA",
                        requirement="Opt-Out",
                        violation_type="missing_opt_out",
                        severity="high",
                        message="Users must have right to opt-out of data sale",
                        remediation="Implement opt-out mechanism for data sales",
                    )
                )

        return violations

    def validate_all(self, data: Dict) -> Dict[str, List[ComplianceViolation]]:
        """Validate all enabled compliance frameworks.

        Args:
            data: Data to validate

        Returns:
            Dictionary mapping framework names to violation lists
        """
        results = {
            "hipaa": self.validate_hipaa(data),
            "gdpr": self.validate_gdpr(data),
            "ccpa": self.validate_ccpa(data),
        }
        return results

    def _check_encryption(self, data: Dict) -> bool:
        """Check if data is encrypted.

        Args:
            data: Data to check

        Returns:
            True if encryption is present
        """
        return data.get("encrypted", False) is True

    def _check_audit_logging(self) -> bool:
        """Check if audit logging is enabled.

        Returns:
            True if audit logging is enabled
        """
        return self.config.get("audit_logging", {}).get("enabled", False)

    def _check_access_controls(self, data: Dict) -> bool:
        """Check if access controls are in place.

        Args:
            data: Data to check

        Returns:
            True if access controls are present
        """
        return "user_id" in data or "role" in data

    def _check_authentication(self, data: Dict) -> bool:
        """Check if authentication is present.

        Args:
            data: Data to check

        Returns:
            True if authentication is present
        """
        return "user_id" in data or "authenticated" in data

    def _check_consent(self, data: Dict) -> bool:
        """Check if consent is documented.

        Args:
            data: Data to check

        Returns:
            True if consent is present
        """
        return data.get("consent_given", False) is True

    def _check_data_minimization(self, data: Dict) -> bool:
        """Check if data minimization is followed.

        Args:
            data: Data to check

        Returns:
            True if data minimization is followed
        """
        return len(data) <= 20

    def _check_storage_limitation(self, data: Dict, retention_days: int) -> bool:
        """Check if storage limitation is followed.

        Args:
            data: Data to check
            retention_days: Maximum retention days

        Returns:
            True if storage limitation is followed
        """
        if "created_at" not in data:
            return True

        try:
            created_at = datetime.fromisoformat(data["created_at"])
            expiration = created_at + timedelta(days=retention_days)
            return datetime.utcnow() < expiration
        except (ValueError, TypeError):
            return True

    def _check_opt_out(self, data: Dict) -> bool:
        """Check if opt-out mechanism is available.

        Args:
            data: Data to check

        Returns:
            True if opt-out is available
        """
        return data.get("opt_out_available", False) is True

    def get_violation_summary(self, violations: List[ComplianceViolation]) -> Dict:
        """Get summary of compliance violations.

        Args:
            violations: List of violations

        Returns:
            Summary dictionary
        """
        summary = {
            "total_violations": len(violations),
            "critical_count": sum(1 for v in violations if v.severity == "critical"),
            "high_count": sum(1 for v in violations if v.severity == "high"),
            "medium_count": sum(1 for v in violations if v.severity == "medium"),
            "frameworks_affected": list(set(v.framework for v in violations)),
        }
        return summary