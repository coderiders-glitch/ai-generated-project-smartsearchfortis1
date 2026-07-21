import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime
import os
import json

logger = logging.getLogger(__name__)


@dataclass
class RetrainingTriggerConfig:
    """Configuration for model retraining triggers."""
    min_evaluation_count: int
    relevance_threshold: float
    min_f1_score: float
    min_precision: float
    min_recall: float
    check_interval_seconds: int


class ModelRetrainingTrigger:
    """Triggers model retraining based on evaluation metrics."""

    def __init__(
        self,
        config: Optional[RetrainingTriggerConfig] = None,
    ):
        """
        Initialize the model retraining trigger.
        
        Args:
            config: Retraining trigger configuration
        """
        self.config = config or self._default_config()
        self.trigger_history: List[Dict[str, Any]] = []
        logger.info("Initialized ModelRetrainingTrigger")

    def should_trigger_retraining(
        self,
        metrics: Dict[str, float],
        evaluation_count: int,
    ) -> bool:
        """
        Determine if model retraining should be triggered based on metrics.
        
        Args:
            metrics: Evaluation metrics dictionary
            evaluation_count: Total number of evaluations performed
            
        Returns:
            True if retraining should be triggered, False otherwise
        """
        try:
            if evaluation_count < self.config.min_evaluation_count:
                logger.info(
                    f"Insufficient evaluations: {evaluation_count} < "
                    f"{self.config.min_evaluation_count}"
                )
                return False
            
            f1_score = metrics.get("f1_score", 0.0)
            precision = metrics.get("precision", 0.0)
            recall = metrics.get("recall", 0.0)
            
            should_retrain = (
                f1_score < self.config.min_f1_score
                or precision < self.config.min_precision
                or recall < self.config.min_recall
            )
            
            if should_retrain:
                logger.warning(
                    f"Retraining triggered: f1={f1_score:.3f}, "
                    f"precision={precision:.3f}, recall={recall:.3f}"
                )
            else:
                logger.info(
                    f"Retraining not needed: f1={f1_score:.3f}, "
                    f"precision={precision:.3f}, recall={recall:.3f}"
                )
            
            return should_retrain
        except Exception as e:
            logger.error(f"Failed to determine retraining trigger: {e}")
            raise

    def record_trigger_event(
        self,
        triggered: bool,
        metrics: Dict[str, float],
        evaluation_count: int,
        reason: Optional[str] = None,
    ) -> None:
        """
        Record a trigger event for audit and analysis.
        
        Args:
            triggered: Whether retraining was triggered
            metrics: Evaluation metrics
            evaluation_count: Total evaluations
            reason: Optional reason for trigger decision
        """
        try:
            event = {
                "timestamp": datetime.utcnow().isoformat(),
                "triggered": triggered,
                "metrics": metrics,
                "evaluation_count": evaluation_count,
                "reason": reason,
            }
            self.trigger_history.append(event)
            logger.info(f"Recorded trigger event: {event}")
        except Exception as e:
            logger.error(f"Failed to record trigger event: {e}")

    def get_trigger_history(self) -> List[Dict[str, Any]]:
        """
        Retrieve the trigger event history.
        
        Returns:
            List of trigger events
        """
        return self.trigger_history.copy()

    def get_last_trigger_event(self) -> Optional[Dict[str, Any]]:
        """
        Get the most recent trigger event.
        
        Returns:
            Last trigger event or None if no events recorded
        """
        return self.trigger_history[-1] if self.trigger_history else None

    def export_trigger_history(self, output_path: str) -> None:
        """
        Export trigger history to a JSON file.
        
        Args:
            output_path: Path to export trigger history
        """
        try:
            with open(output_path, "w") as f:
                json.dump(self.trigger_history, f, indent=2)
            logger.info(f"Exported trigger history to {output_path}")
        except Exception as e:
            logger.error(f"Failed to export trigger history: {e}")
            raise

    def reset_trigger_history(self) -> None:
        """
        Clear the trigger event history.
        """
        self.trigger_history = []
        logger.info("Reset trigger history")

    @staticmethod
    def _default_config() -> RetrainingTriggerConfig:
        """
        Create default retraining trigger configuration.
        
        Returns:
            Default RetrainingTriggerConfig
        """
        return RetrainingTriggerConfig(
            min_evaluation_count=int(os.getenv("MIN_EVALUATION_COUNT", "100")),
            relevance_threshold=float(os.getenv("RELEVANCE_THRESHOLD", "0.7")),
            min_f1_score=float(os.getenv("MIN_F1_SCORE", "0.75")),
            min_precision=float(os.getenv("MIN_PRECISION", "0.75")),
            min_recall=float(os.getenv("MIN_RECALL", "0.75")),
            check_interval_seconds=int(os.getenv("CHECK_INTERVAL_SECONDS", "3600")),
        )