import json
import logging
import time
from datetime import datetime
from typing import Any, Dict, Optional
from functools import wraps

import boto3
from pythonjsonlogger import jsonlogger

logger = logging.getLogger(__name__)


class MetricsCollector:
    """Collects and publishes metrics to CloudWatch."""

    def __init__(self, namespace: str = "LLMMonitoring", region: str = "us-east-1"):
        self.namespace = namespace
        self.cloudwatch_client = boto3.client("cloudwatch", region_name=region)
        self.metrics_buffer: list[Dict[str, Any]] = []
        self.buffer_size = 20

    def put_metric(
        self,
        metric_name: str,
        value: float,
        unit: str = "None",
        dimensions: Optional[Dict[str, str]] = None,
    ) -> None:
        """Put a single metric to CloudWatch."""
        try:
            metric_data = {
                "MetricName": metric_name,
                "Value": value,
                "Unit": unit,
                "Timestamp": datetime.utcnow(),
            }
            if dimensions:
                metric_data["Dimensions"] = [
                    {"Name": k, "Value": v} for k, v in dimensions.items()
                ]
            self.metrics_buffer.append(metric_data)
            if len(self.metrics_buffer) >= self.buffer_size:
                self.flush_metrics()
        except Exception as error:
            logger.error(f"Error putting metric {metric_name}: {error}")

    def flush_metrics(self) -> None:
        """Flush buffered metrics to CloudWatch."""
        if not self.metrics_buffer:
            return
        try:
            self.cloudwatch_client.put_metric_data(
                Namespace=self.namespace, MetricData=self.metrics_buffer
            )
            logger.info(f"Flushed {len(self.metrics_buffer)} metrics to CloudWatch")
            self.metrics_buffer = []
        except Exception as error:
            logger.error(f"Error flushing metrics: {error}")

    def record_latency(
        self,
        operation_name: str,
        latency_ms: float,
        dimensions: Optional[Dict[str, str]] = None,
    ) -> None:
        """Record operation latency."""
        dims = dimensions or {}
        dims["Operation"] = operation_name
        self.put_metric(
            "RequestLatency", latency_ms, unit="Milliseconds", dimensions=dims
        )

    def record_token_count(
        self,
        token_count: int,
        model_name: str,
        dimensions: Optional[Dict[str, str]] = None,
    ) -> None:
        """Record token usage."""
        dims = dimensions or {}
        dims["Model"] = model_name
        self.put_metric(
            "TokenCount", float(token_count), unit="Count", dimensions=dims
        )

    def record_error(
        self,
        error_type: str,
        service_name: str,
        dimensions: Optional[Dict[str, str]] = None,
    ) -> None:
        """Record error occurrence."""
        dims = dimensions or {}
        dims["ErrorType"] = error_type
        dims["Service"] = service_name
        self.put_metric("ErrorCount", 1.0, unit="Count", dimensions=dims)

    def record_cache_hit(
        self,
        is_hit: bool,
        cache_type: str,
        dimensions: Optional[Dict[str, str]] = None,
    ) -> None:
        """Record cache hit/miss."""
        dims = dimensions or {}
        dims["CacheType"] = cache_type
        value = 1.0 if is_hit else 0.0
        self.put_metric("CacheHit", value, unit="None", dimensions=dims)


class StructuredLogger:
    """Provides structured logging with JSON format."""

    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self._setup_json_logging()

    def _setup_json_logging(self) -> None:
        """Configure JSON logging format."""
        handler = logging.StreamHandler()
        formatter = jsonlogger.JsonFormatter(
            "%(timestamp)s %(level)s %(name)s %(message)s"
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def log_request(
        self,
        request_id: str,
        service_name: str,
        endpoint: str,
        method: str,
        user_id: Optional[str] = None,
    ) -> None:
        """Log incoming request."""
        self.logger.info(
            "Request received",
            extra={
                "request_id": request_id,
                "service_name": service_name,
                "endpoint": endpoint,
                "method": method,
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat(),
            },
        )

    def log_response(
        self,
        request_id: str,
        service_name: str,
        status_code: int,
        latency_ms: float,
        token_count: Optional[int] = None,
    ) -> None:
        """Log response completion."""
        self.logger.info(
            "Response sent",
            extra={
                "request_id": request_id,
                "service_name": service_name,
                "status_code": status_code,
                "latency_ms": latency_ms,
                "token_count": token_count,
                "timestamp": datetime.utcnow().isoformat(),
            },
        )

    def log_error(
        self,
        request_id: str,
        service_name: str,
        error_message: str,
        error_type: str,
        stack_trace: Optional[str] = None,
    ) -> None:
        """Log error occurrence."""
        self.logger.error(
            "Error occurred",
            extra={
                "request_id": request_id,
                "service_name": service_name,
                "error_message": error_message,
                "error_type": error_type,
                "stack_trace": stack_trace,
                "timestamp": datetime.utcnow().isoformat(),
            },
        )

    def log_llm_call(
        self,
        request_id: str,
        model_name: str,
        prompt_tokens: int,
        completion_tokens: int,
        latency_ms: float,
        temperature: float,
    ) -> None:
        """Log LLM API call details."""
        self.logger.info(
            "LLM call executed",
            extra={
                "request_id": request_id,
                "model_name": model_name,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens,
                "latency_ms": latency_ms,
                "temperature": temperature,
                "timestamp": datetime.utcnow().isoformat(),
            },
        )


def monitor_performance(
    metrics_collector: MetricsCollector, structured_logger: StructuredLogger
):
    """Decorator to monitor function performance and log execution."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            request_id = kwargs.get("request_id", "unknown")
            service_name = kwargs.get("service_name", func.__module__)
            start_time = time.time()
            status_code = 500
            error_message = None
            result = None

            try:
                result = func(*args, **kwargs)
                status_code = 200
                return result
            except Exception as error:
                status_code = 500
                error_message = str(error)
                error_type = type(error).__name__
                structured_logger.log_error(
                    request_id=request_id,
                    service_name=service_name,
                    error_message=error_message,
                    error_type=error_type,
                )
                metrics_collector.record_error(
                    error_type=error_type, service_name=service_name
                )
                raise
            finally:
                latency_ms = (time.time() - start_time) * 1000
                metrics_collector.record_latency(
                    operation_name=func.__name__, latency_ms=latency_ms
                )
                structured_logger.log_response(
                    request_id=request_id,
                    service_name=service_name,
                    status_code=status_code,
                    latency_ms=latency_ms,
                )

        return wrapper

    return decorator