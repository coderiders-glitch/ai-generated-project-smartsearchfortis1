import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import json

logger = logging.getLogger(__name__)


@dataclass
class GroundTruthRecord:
    """Represents a ground truth record for evaluation."""
    query: str
    expected_result: Dict[str, Any]
    category: str
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any]
    record_id: Optional[str] = None


class GroundTruthManager:
    """Manages ground truth data for semantic evaluation."""

    def __init__(self, storage_path: str = "./ground_truth_data.json"):
        """
        Initialize the ground truth manager.
        
        Args:
            storage_path: Path to store ground truth records
        """
        self.storage_path = storage_path
        self.records: Dict[str, GroundTruthRecord] = {}
        self._load_records()
        logger.info(f"Initialized GroundTruthManager with storage at {storage_path}")

    def add_record(
        self,
        query: str,
        expected_result: Dict[str, Any],
        category: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Add a new ground truth record.
        
        Args:
            query: Search query
            expected_result: Expected search result
            category: Category of the query (e.g., 'doctor', 'service', 'specialty')
            metadata: Additional metadata
            
        Returns:
            Record ID
        """
        try:
            record_id = self._generate_record_id()
            record = GroundTruthRecord(
                query=query,
                expected_result=expected_result,
                category=category,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                metadata=metadata or {},
                record_id=record_id,
            )
            self.records[record_id] = record
            self._save_records()
            logger.info(f"Added ground truth record: {record_id}")
            return record_id
        except Exception as e:
            logger.error(f"Failed to add ground truth record: {e}")
            raise

    def get_record(self, record_id: str) -> Optional[GroundTruthRecord]:
        """
        Retrieve a ground truth record by ID.
        
        Args:
            record_id: Record ID
            
        Returns:
            GroundTruthRecord or None if not found
        """
        return self.records.get(record_id)

    def get_records_by_category(self, category: str) -> List[GroundTruthRecord]:
        """
        Retrieve all ground truth records for a specific category.
        
        Args:
            category: Category name
            
        Returns:
            List of GroundTruthRecord objects
        """
        return [r for r in self.records.values() if r.category == category]

    def get_all_records(self) -> List[GroundTruthRecord]:
        """
        Retrieve all ground truth records.
        
        Returns:
            List of all GroundTruthRecord objects
        """
        return list(self.records.values())

    def update_record(
        self,
        record_id: str,
        expected_result: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Update an existing ground truth record.
        
        Args:
            record_id: Record ID
            expected_result: Updated expected result
            metadata: Updated metadata
            
        Returns:
            True if update successful, False if record not found
        """
        try:
            if record_id not in self.records:
                logger.warning(f"Record not found: {record_id}")
                return False
            
            record = self.records[record_id]
            if expected_result is not None:
                record.expected_result = expected_result
            if metadata is not None:
                record.metadata.update(metadata)
            record.updated_at = datetime.utcnow()
            
            self._save_records()
            logger.info(f"Updated ground truth record: {record_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to update ground truth record: {e}")
            raise

    def delete_record(self, record_id: str) -> bool:
        """
        Delete a ground truth record.
        
        Args:
            record_id: Record ID
            
        Returns:
            True if deletion successful, False if record not found
        """
        try:
            if record_id not in self.records:
                logger.warning(f"Record not found: {record_id}")
                return False
            
            del self.records[record_id]
            self._save_records()
            logger.info(f"Deleted ground truth record: {record_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete ground truth record: {e}")
            raise

    def _load_records(self) -> None:
        """
        Load ground truth records from storage.
        """
        try:
            if not os.path.exists(self.storage_path):
                logger.info(f"Storage file not found: {self.storage_path}")
                return
            
            with open(self.storage_path, "r") as f:
                data = json.load(f)
            
            for record_id, record_data in data.items():
                record_data["created_at"] = datetime.fromisoformat(record_data["created_at"])
                record_data["updated_at"] = datetime.fromisoformat(record_data["updated_at"])
                self.records[record_id] = GroundTruthRecord(**record_data)
            
            logger.info(f"Loaded {len(self.records)} ground truth records")
        except Exception as e:
            logger.error(f"Failed to load ground truth records: {e}")

    def _save_records(self) -> None:
        """
        Save ground truth records to storage.
        """
        try:
            data = {}
            for record_id, record in self.records.items():
                record_dict = asdict(record)
                record_dict["created_at"] = record_dict["created_at"].isoformat()
                record_dict["updated_at"] = record_dict["updated_at"].isoformat()
                data[record_id] = record_dict
            
            with open(self.storage_path, "w") as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Saved {len(self.records)} ground truth records")
        except Exception as e:
            logger.error(f"Failed to save ground truth records: {e}")
            raise

    @staticmethod
    def _generate_record_id() -> str:
        """
        Generate a unique record ID.
        
        Returns:
            Unique record ID
        """
        import uuid
        return f"gt_{uuid.uuid4().hex[:12]}"


import os