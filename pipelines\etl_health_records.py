import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import os
import json

import psycopg2
from psycopg2.extras import execute_values

logger = logging.getLogger(__name__)


class HealthRecordsETL:
    """ETL pipeline for ingesting and transforming health records data."""

    def __init__(
        self,
        host: str = os.getenv("DB_HOST", "localhost"),
        port: int = int(os.getenv("DB_PORT", "5432")),
        database: str = os.getenv("DB_NAME", "fortis_db"),
        user: str = os.getenv("DB_USER", "postgres"),
        password: str = os.getenv("DB_PASSWORD", ""),
    ):
        """Initialize database connection parameters."""
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.connection = None

    def connect(self) -> None:
        """Establish database connection."""
        try:
            self.connection = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password,
            )
            logger.info("Database connection established")
        except psycopg2.Error as error:
            logger.error(f"Failed to connect to database: {error}")
            raise

    def disconnect(self) -> None:
        """Close database connection."""
        if self.connection:
            self.connection.close()
            logger.info("Database connection closed")

    def extract_raw_health_records(self, days_back: int = 30) -> List[Dict[str, Any]]:
        """Extract raw health records from source system."""
        if not self.connection:
            self.connect()

        try:
            cursor = self.connection.cursor()
            cutoff_date = datetime.now() - timedelta(days=days_back)

            query = """
                SELECT id, user_id, record_type, medical_history, allergies, medications, conditions, created_at
                FROM health_records
                WHERE created_at >= %s
                ORDER BY created_at DESC
            """

            cursor.execute(query, (cutoff_date,))
            records = cursor.fetchall()
            cursor.close()

            result = [
                {
                    "id": record[0],
                    "user_id": record[1],
                    "record_type": record[2],
                    "medical_history": record[3],
                    "allergies": record[4],
                    "medications": record[5],
                    "conditions": record[6],
                    "created_at": record[7],
                }
                for record in records
            ]

            logger.info(f"Extracted {len(result)} health records")
            return result
        except psycopg2.Error as error:
            logger.error(f"Error extracting health records: {error}")
            raise

    def transform_health_records(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Transform and validate health records data."""
        transformed_data = []

        for record in raw_data:
            try:
                medical_history = record["medical_history"]
                if isinstance(medical_history, str):
                    medical_history = json.loads(medical_history)

                allergies = record["allergies"]
                if isinstance(allergies, str):
                    allergies = json.loads(allergies)

                medications = record["medications"]
                if isinstance(medications, str):
                    medications = json.loads(medications)

                conditions = record["conditions"]
                if isinstance(conditions, str):
                    conditions = json.loads(conditions)

                transformed_record = {
                    "id": record["id"],
                    "user_id": record["user_id"],
                    "record_type": record["record_type"].lower(),
                    "medical_history": medical_history,
                    "allergies": allergies,
                    "medications": medications,
                    "conditions": conditions,
                    "created_at": record["created_at"],
                    "processed_at": datetime.now(),
                    "has_chronic_conditions": len(conditions) > 0 if conditions else False,
                }
                transformed_data.append(transformed_record)
            except (KeyError, json.JSONDecodeError, AttributeError, TypeError) as error:
                logger.warning(f"Skipping malformed record: {error}")
                continue

        logger.info(f"Transformed {len(transformed_data)} health records")
        return transformed_data

    def load_health_records(self, data: List[Dict[str, Any]]) -> int:
        """Load transformed health records into database."""
        if not self.connection:
            self.connect()

        if not data:
            logger.info("No data to load")
            return 0

        try:
            cursor = self.connection.cursor()

            records_to_insert = [
                (
                    record["id"],
                    record["user_id"],
                    record["record_type"],
                    json.dumps(record["medical_history"]),
                    json.dumps(record["allergies"]),
                    json.dumps(record["medications"]),
                    json.dumps(record["conditions"]),
                    record["created_at"],
                    record["processed_at"],
                    record["has_chronic_conditions"],
                )
                for record in data
            ]

            query = """
                INSERT INTO health_records (id, user_id, record_type, medical_history, allergies, medications, conditions, created_at, processed_at, has_chronic_conditions)
                VALUES %s
                ON CONFLICT (id) DO UPDATE SET processed_at = EXCLUDED.processed_at
            """

            execute_values(cursor, query, records_to_insert)
            self.connection.commit()
            rows_affected = cursor.rowcount
            cursor.close()

            logger.info(f"Loaded {rows_affected} health records")
            return rows_affected
        except psycopg2.Error as error:
            self.connection.rollback()
            logger.error(f"Error loading health records: {error}")
            raise

    def run_etl(self, days_back: int = 30) -> Dict[str, Any]:
        """Execute full ETL pipeline for health records."""
        try:
            self.connect()
            raw_data = self.extract_raw_health_records(days_back=days_back)
            transformed_data = self.transform_health_records(raw_data)
            rows_loaded = self.load_health_records(transformed_data)

            result = {
                "status": "success",
                "records_extracted": len(raw_data),
                "records_transformed": len(transformed_data),
                "records_loaded": rows_loaded,
                "timestamp": datetime.now().isoformat(),
            }
            logger.info(f"ETL pipeline completed: {result}")
            return result
        except Exception as error:
            logger.error(f"ETL pipeline failed: {error}")
            return {
                "status": "failed",
                "error": str(error),
                "timestamp": datetime.now().isoformat(),
            }
        finally:
            self.disconnect()