import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import os

import psycopg2
from psycopg2.extras import execute_values

logger = logging.getLogger(__name__)


class AppointmentETL:
    """ETL pipeline for ingesting and transforming appointment data."""

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

    def extract_raw_appointments(self, days_back: int = 7) -> List[Dict[str, Any]]:
        """Extract raw appointment records from source system."""
        if not self.connection:
            self.connect()

        try:
            cursor = self.connection.cursor()
            cutoff_date = datetime.now() - timedelta(days=days_back)

            query = """
                SELECT id, user_id, doctor_id, appointment_date, status, created_at
                FROM appointments
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
                    "doctor_id": record[2],
                    "appointment_date": record[3],
                    "status": record[4],
                    "created_at": record[5],
                }
                for record in records
            ]

            logger.info(f"Extracted {len(result)} appointment records")
            return result
        except psycopg2.Error as error:
            logger.error(f"Error extracting appointments: {error}")
            raise

    def transform_appointments(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Transform and validate appointment data."""
        transformed_data = []

        for record in raw_data:
            try:
                transformed_record = {
                    "id": record["id"],
                    "user_id": record["user_id"],
                    "doctor_id": record["doctor_id"],
                    "appointment_date": record["appointment_date"],
                    "status": record["status"].lower(),
                    "created_at": record["created_at"],
                    "processed_at": datetime.now(),
                }
                transformed_data.append(transformed_record)
            except (KeyError, AttributeError) as error:
                logger.warning(f"Skipping malformed record: {error}")
                continue

        logger.info(f"Transformed {len(transformed_data)} appointment records")
        return transformed_data

    def load_appointments(self, data: List[Dict[str, Any]]) -> int:
        """Load transformed appointment data into database."""
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
                    record["doctor_id"],
                    record["appointment_date"],
                    record["status"],
                    record["created_at"],
                    record["processed_at"],
                )
                for record in data
            ]

            query = """
                INSERT INTO appointments (id, user_id, doctor_id, appointment_date, status, created_at, processed_at)
                VALUES %s
                ON CONFLICT (id) DO UPDATE SET status = EXCLUDED.status, processed_at = EXCLUDED.processed_at
            """

            execute_values(cursor, query, records_to_insert)
            self.connection.commit()
            rows_affected = cursor.rowcount
            cursor.close()

            logger.info(f"Loaded {rows_affected} appointment records")
            return rows_affected
        except psycopg2.Error as error:
            self.connection.rollback()
            logger.error(f"Error loading appointments: {error}")
            raise

    def run_etl(self, days_back: int = 7) -> Dict[str, Any]:
        """Execute full ETL pipeline for appointments."""
        try:
            self.connect()
            raw_data = self.extract_raw_appointments(days_back=days_back)
            transformed_data = self.transform_appointments(raw_data)
            rows_loaded = self.load_appointments(transformed_data)

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