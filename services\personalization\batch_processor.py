import logging
from typing import List, Dict, Any, Optional
import json
from datetime import datetime

logger = logging.getLogger(__name__)


class BatchProcessor:
    """Processes persona classification for multiple users in batch."""

    def __init__(self, persona_engine):
        """
        Initialize batch processor.

        Args:
            persona_engine: PersonaEngine instance
        """
        self.persona_engine = persona_engine
        logger.info("BatchProcessor initialized")

    def process_batch(self, user_data_map: Dict[str, Dict[str, Any]], batch_size: int = 100) -> Dict[str, Any]:
        """
        Process persona classification for a batch of users.

        Args:
            user_data_map: Mapping of user_id to user data
            batch_size: Number of users to process per batch

        Returns:
            Dictionary with processing results and statistics
        """
        try:
            logger.info(f"Starting batch processing for {len(user_data_map)} users")
            start_time = datetime.utcnow()

            results = []
            errors = []
            user_ids = list(user_data_map.keys())

            for i in range(0, len(user_ids), batch_size):
                batch_user_ids = user_ids[i:i + batch_size]
                batch_results = self._process_batch_chunk(batch_user_ids, user_data_map)
                results.extend(batch_results["results"])
                errors.extend(batch_results["errors"])
                logger.info(f"Processed batch {i // batch_size + 1}: {len(batch_results['results'])} successful, {len(batch_results['errors'])} errors")

            end_time = datetime.utcnow()
            processing_time = (end_time - start_time).total_seconds()

            summary = {
                "total_users": len(user_data_map),
                "successful_classifications": len(results),
                "failed_classifications": len(errors),
                "processing_time_seconds": processing_time,
                "average_time_per_user": processing_time / len(user_data_map) if user_data_map else 0,
                "results": results,
                "errors": errors,
                "persona_distribution": self._calculate_distribution(results),
                "timestamp": datetime.utcnow().isoformat()
            }

            logger.info(f"Batch processing completed: {summary['successful_classifications']} successful, {summary['failed_classifications']} failed")
            return summary

        except Exception as e:
            logger.error(f"Error in batch processing: {str(e)}", exc_info=True)
            return {
                "total_users": len(user_data_map),
                "successful_classifications": 0,
                "failed_classifications": len(user_data_map),
                "processing_time_seconds": 0,
                "average_time_per_user": 0,
                "results": [],
                "errors": [{"user_id": uid, "error": str(e)} for uid in user_data_map.keys()],
                "persona_distribution": {},
                "timestamp": datetime.utcnow().isoformat()
            }

    def _process_batch_chunk(self, user_ids: List[str], user_data_map: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Process a chunk of users.

        Args:
            user_ids: List of user identifiers
            user_data_map: Mapping of user_id to user data

        Returns:
            Dictionary with results and errors
        """
        results = []
        errors = []

        for user_id in user_ids:
            try:
                if user_id not in user_data_map:
                    errors.append({"user_id": user_id, "error": "User data not found"})
                    continue

                profile = self.persona_engine.classify_user(user_id, user_data_map[user_id])

                if profile:
                    results.append({
                        "user_id": profile.user_id,
                        "persona_name": profile.persona_name,
                        "confidence_score": profile.confidence_score,
                        "classification_timestamp": profile.classification_timestamp.isoformat(),
                        "recommended_actions": profile.recommended_actions
                    })
                else:
                    errors.append({"user_id": user_id, "error": "Classification returned None"})

            except Exception as e:
                logger.error(f"Error processing user {user_id}: {str(e)}")
                errors.append({"user_id": user_id, "error": str(e)})

        return {"results": results, "errors": errors}

    def _calculate_distribution(self, results: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Calculate persona distribution from results.

        Args:
            results: List of classification results

        Returns:
            Dictionary with persona counts
        """
        distribution = {
            "Frequent Visitor": 0,
            "Preventive Health Seeker": 0,
            "Chronic Condition Manager": 0,
            "Lapsed User": 0
        }

        for result in results:
            persona = result.get("persona_name")
            if persona in distribution:
                distribution[persona] += 1

        return distribution

    def export_results(self, results: Dict[str, Any], output_path: str) -> bool:
        """
        Export batch processing results to JSON file.

        Args:
            results: Batch processing results
            output_path: Path to output file

        Returns:
            True if successful, False otherwise
        """
        try:
            with open(output_path, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            logger.info(f"Results exported to {output_path}")
            return True
        except Exception as e:
            logger.error(f"Error exporting results to {output_path}: {str(e)}")
            return False