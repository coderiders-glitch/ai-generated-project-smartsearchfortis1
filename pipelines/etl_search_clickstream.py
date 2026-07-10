import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import os
import json

import psycopg2
from psycopg2.extras import execute_values

logger = logging.getLogger(__name__)


class SearchClickstreamETL:
    """ETL pipeline for ingesting and transforming search clickstream data."""

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

    def extract_raw_search_queries(self, days_back: int = 7) -> List[Dict[str, Any]]:
        """Extract raw search query records from source system."""
        if not self.connection:
            self.connect()

        try:
            cursor = self.connection.cursor()
            cutoff_date = datetime.now() - timedelta(days=days_back)

            query = """
                SELECT id, user_id, query_text, filters, results_count, clicked_result_id, created_at
                FROM search_queries
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
                    "query_text": record[2],
                    "filters": record[3],
                    "results_count": record[4],
                    "clicked_result_id": record[5],
                    "created_at": record[6],
                }
                for record in records
            ]

            logger.info(f"Extracted {len(result)} search query records")
            return result
        except psycopg2.Error as error:
            logger.error(f"Error extracting search queries: {error}")
            raise

    def transform_search_queries(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Transform and validate search query data."""
        transformed_data = []

        for record in raw_data:
            try:
                filters = record["filters"]
                if isinstance(filters, str):
                    filters = json.loads(filters)

                transformed_record = {
                    "id": record["id"],
                    "user_id": record["user_id"],
                    "query_text": record["query_text"].strip().lower(),
                    "filters": filters,
                    "results_count": record["results_count"],
                    "clicked_result_id": record["clicked_result_id"],
                    "created_at": record["created_at"],
                    "processed_at": datetime.now(),
                    "has_click": record["clicked_result_id"] is not None,
                }
                transformed_data.append(transformed_record)
            except (KeyError, json.JSONDecodeError, AttributeError) as error:
                logger.warning(f"Skipping malformed record: {error}")
                continue

        logger.info(f"Transformed {len(transformed_data)} search query records")
        return transformed_data

    def load_search_queries(self, data: List[Dict[str, Any]]) -> int:
        """Load transformed search query data into database."""
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
                    record["query_text"],
                    json.dumps(record["filters"]),
                    record["results_count"],
                    record["clicked_result_id"],
                    record["created_at"],
                    record["processed_at"],
                    record["has_click"],
                )
                for record in data
            ]

            query = """
                INSERT INTO search_queries (id, user_id, query_text, filters, results_count, clicked_result_id, created_at, processed_at, has_click)
                VALUES %s
                ON CONFLICT (id) DO UPDATE SET processed_at = EXCLUDED.processed_at
            """

            execute_values(cursor, query, records_to_insert)
            self.connection.commit()
            rows_affected = cursor.rowcount
            cursor.close()

            logger.info(f"Loaded {rows_affected} search query records")
            return rows_affected
        except psycopg2.Error as error:
            self.connection.rollback()
            logger.error(f"Error loading search queries: {error}")
            raise

    def run_etl(self, days_back: int = 7) -> Dict[str, Any]:
        """Execute full ETL pipeline for search clickstream."""
        try:
            self.connect()
            raw_data = self.extract_raw_search_queries(days_back=days_back)
            transformed_data = self.transform_search_queries(raw_data)
            rows_loaded = self.load_search_queries(transformed_data)

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