import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import os
import json

import psycopg2
from psycopg2.extras import execute_values

logger = logging.getLogger(__name__)


class UserDemographicsETL:
    """ETL pipeline for ingesting and transforming user demographics data."""

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

    def extract_raw_users(self, days_back: int = 90) -> List[Dict[str, Any]]:
        """Extract raw user records from source system."""
        if not self.connection:
            self.connect()

        try:
            cursor = self.connection.cursor()
            cutoff_date = datetime.now() - timedelta(days=days_back)

            query = """
                SELECT id, username, email, first_name, last_name, age, gender, location, created_at, updated_at
                FROM users
                WHERE created_at >= %s OR updated_at >= %s
                ORDER BY updated_at DESC
            """

            cursor.execute(query, (cutoff_date, cutoff_date))
            records = cursor.fetchall()
            cursor.close()

            result = [
                {
                    "id": record[0],
                    "username": record[1],
                    "email": record[2],
                    "first_name": record[3],
                    "last_name": record[4],
                    "age": record[5],
                    "gender": record[6],
                    "location": record[7],
                    "created_at": record[8],
                    "updated_at": record[9],
                }
                for record in records
            ]

            logger.info(f"Extracted {len(result)} user records")
            return result
        except psycopg2.Error as error:
            logger.error(f"Error extracting users: {error}")
            raise

    def transform_users(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Transform and validate user demographics data."""
        transformed_data = []

        for record in raw_data:
            try:
                age = record["age"]
                age_group = self._classify_age_group(age)

                transformed_record = {
                    "id": record["id"],
                    "username": record["username"],
                    "email": record["email"].lower(),
                    "first_name": record["first_name"],
                    "last_name": record["last_name"],
                    "age": age,
                    "age_group": age_group,
                    "gender": record["gender"].lower() if record["gender"] else None,
                    "location": record["location"],
                    "created_at": record["created_at"],
                    "updated_at": record["updated_at"],
                    "processed_at": datetime.now(),
                }
                transformed_data.append(transformed_record)
            except (KeyError, AttributeError, TypeError) as error:
                logger.warning(f"Skipping malformed record: {error}")
                continue

        logger.info(f"Transformed {len(transformed_data)} user records")
        return transformed_data

    def _classify_age_group(self, age: Optional[int]) -> Optional[str]:
        """Classify age into demographic groups."""
        if age is None:
            return None
        if age < 18:
            return "under_18"
        elif age < 25:
            return "18_24"
        elif age < 35:
            return "25_34"
        elif age < 45:
            return "35_44"
        elif age < 55:
            return "45_54"
        elif age < 65:
            return "55_64"
        else:
            return "65_plus"

    def load_users(self, data: List[Dict[str, Any]]) -> int:
        """Load transformed user demographics into database."""
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
                    record["username"],
                    record["email"],
                    record["first_name"],
                    record["last_name"],
                    record["age"],
                    record["age_group"],
                    record["gender"],
                    record["location"],
                    record["created_at"],
                    record["updated_at"],
                    record["processed_at"],
                )
                for record in data
            ]

            query = """
                INSERT INTO users (id, username, email, first_name, last_name, age, age_group, gender, location, created_at, updated_at, processed_at)
                VALUES %s
                ON CONFLICT (id) DO UPDATE SET updated_at = EXCLUDED.updated_at, processed_at = EXCLUDED.processed_at
            """

            execute_values(cursor, query, records_to_insert)
            self.connection.commit()
            rows_affected = cursor.rowcount
            cursor.close()

            logger.info(f"Loaded {rows_affected} user records")
            return rows_affected
        except psycopg2.Error as error:
            self.connection.rollback()
            logger.error(f"Error loading users: {error}")
            raise

    def run_etl(self, days_back: int = 90) -> Dict[str, Any]:
        """Execute full ETL pipeline for user demographics."""
        try:
            self.connect()
            raw_data = self.extract_raw_users(days_back=days_back)
            transformed_data = self.transform_users(raw_data)
            rows_loaded = self.load_users(transformed_data)

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