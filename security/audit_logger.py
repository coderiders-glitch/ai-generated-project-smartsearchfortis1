import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path
import os
import yaml
from logging.handlers import RotatingFileHandler


class AuditLogger:
    """Handles audit logging for security and compliance events."""

    def __init__(self, config_path: str = "security/guardrails_config.yaml"):
        """Initialize audit logger.

        Args:
            config_path: Path to guardrails configuration file
        """
        self.config = self._load_config(config_path)
        self.logger = self._setup_logger()
        self.events_to_log = self.config.get("audit_logging", {}).get(
            "events_to_log", []
        )

    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file.

        Args:
            config_path: Path to configuration file

        Returns:
            Configuration dictionary
        """
        if not os.path.exists(config_path):
            return {"audit_logging": {"enabled": True, "log_level": "INFO"}}

        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
        return config

    def _setup_logger(self) -> logging.Logger:
        """Set up rotating file logger for audit events.

        Returns:
            Configured logger instance
        """
        audit_config = self.config.get("audit_logging", {})
        log_level = audit_config.get("log_level", "INFO")
        log_dir = "logs"

        Path(log_dir).mkdir(exist_ok=True)

        logger = logging.getLogger("audit")
        logger.setLevel(getattr(logging, log_level))

        handler = RotatingFileHandler(
            os.path.join(log_dir, "audit.log"),
            maxBytes=10485760,
            backupCount=10,
        )
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        return logger

    def log_event(
        self,
        event_type: str,
        user_id: Optional[str] = None,
        resource: Optional[str] = None,
        action: Optional[str] = None,
        status: str = "success",
        details: Optional[Dict[str, Any]] = None,
        request_headers: Optional[Dict[str, str]] = None,
        response_status: Optional[int] = None,
    ) -> None:
        """Log an audit event.

        Args:
            event_type: Type of event (e.g., 'user_login', 'data_access')
            user_id: ID of user performing action
            resource: Resource being accessed/modified
            action: Action being performed
            status: Status of action (success/failure)
            details: Additional event details
            request_headers: Request headers to log
            response_status: HTTP response status code
        """
        if not self.config.get("audit_logging", {}).get("enabled", False):
            return

        if event_type not in self.events_to_log:
            return

        audit_config = self.config.get("audit_logging", {})
        event_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "user_id": user_id,
            "resource": resource,
            "action": action,
            "status": status,
            "details": details or {},
        }

        if audit_config.get("include_request_headers", False) and request_headers:
            event_data["request_headers"] = self._mask_sensitive_headers(
                request_headers
            )

        if audit_config.get("include_response_status", False) and response_status:
            event_data["response_status"] = response_status

        if audit_config.get("mask_sensitive_data", False):
            event_data = self._mask_sensitive_fields(event_data)

        log_message = json.dumps(event_data)
        self.logger.info(log_message)

    def log_pii_detection(
        self,
        user_id: Optional[str],
        pii_type: str,
        severity: str,
        context: Optional[str] = None,
    ) -> None:
        """Log PII detection event.

        Args:
            user_id: ID of user whose data contained PII
            pii_type: Type of PII detected
            severity: Severity level
            context: Additional context
        """
        self.log_event(
            event_type="pii_detection",
            user_id=user_id,
            action="pii_detected",
            details={
                "pii_type": pii_type,
                "severity": severity,
                "context": context,
            },
        )

    def log_injection_attempt(
        self,
        user_id: Optional[str],
        injection_type: str,
        detected_pattern: str,
        risk_level: str,
    ) -> None:
        """Log injection attempt event.

        Args:
            user_id: ID of user attempting injection
            injection_type: Type of injection attempt
            detected_pattern: Pattern that was detected
            risk_level: Risk level of attempt
        """
        self.log_event(
            event_type="injection_attempt",
            user_id=user_id,
            action="injection_blocked",
            status="blocked",
            details={
                "injection_type": injection_type,
                "detected_pattern": detected_pattern,
                "risk_level": risk_level,
            },
        )

    def log_data_access(
        self,
        user_id: str,
        resource: str,
        action: str = "read",
        status: str = "success",
    ) -> None:
        """Log data access event.

        Args:
            user_id: ID of user accessing data
            resource: Resource being accessed
            action: Type of access (read/write/delete)
            status: Status of access
        """
        self.log_event(
            event_type="data_access",
            user_id=user_id,
            resource=resource,
            action=action,
            status=status,
        )

    def log_authentication(
        self,
        user_id: str,
        event_type: str = "user_login",
        status: str = "success",
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Log authentication event.

        Args:
            user_id: ID of user
            event_type: Type of auth event (user_login/user_logout)
            status: Status of authentication
            details: Additional details
        """
        self.log_event(
            event_type=event_type,
            user_id=user_id,
            action="authentication",
            status=status,
            details=details,
        )

    def _mask_sensitive_headers(self, headers: Dict[str, str]) -> Dict[str, str]:
        """Mask sensitive information in headers.

        Args:
            headers: Request headers

        Returns:
            Headers with sensitive data masked
        """
        sensitive_keys = ["authorization", "x-api-key", "cookie", "x-auth-token"]
        masked_headers = {}

        for key, value in headers.items():
            if key.lower() in sensitive_keys:
                masked_headers[key] = "***MASKED***"
            else:
                masked_headers[key] = value

        return masked_headers

    def _mask_sensitive_fields(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Mask sensitive fields in event data.

        Args:
            data: Event data

        Returns:
            Data with sensitive fields masked
        """
        sensitive_fields = [
            "password",
            "api_key",
            "token",
            "secret",
            "ssn",
            "credit_card",
        ]
        masked_data = data.copy()

        if "details" in masked_data and isinstance(masked_data["details"], dict):
            for key in masked_data["details"]:
                if key.lower() in sensitive_fields:
                    masked_data["details"][key] = "***MASKED***"

        return masked_data