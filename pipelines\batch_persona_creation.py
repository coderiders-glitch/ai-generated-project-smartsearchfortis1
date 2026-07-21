import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
import os
import json

import psycopg2
from psycopg2.extras import execute_values

logger = logging.getLogger(__name__)


class BatchPersonaCreation:
    """Batch processor for creating personas from user data (100K+ users daily)."""

    def __init__(
        self,
        host: str = os.getenv("DB_HOST", "localhost"),
        port: int = int(os.getenv("DB_PORT", "5432")),
        database: str = os.getenv("DB_NAME", "fortis_db"),
        user: str = os.getenv("DB_USER", "postgres"),
        password: str = os.getenv("DB_PASSWORD", ""),
        batch_size: int = 1000,
    ):
        """Initialize batch processor with database connection parameters."""
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.batch_size = batch_size
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

    def extract_users_for_persona_creation(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Extract user data for persona creation."""
        if not self.connection:
            self.connect()

        try:
            cursor = self.connection.cursor()

            query = """
                SELECT u.id, u.age_group, u.gender, u.location,
                       COUNT(DISTINCT a.id) as appointment_count,
                       COUNT(DISTINCT sq.id) as search_count,
                       MAX(a.appointment_date) as last_appointment_date
                FROM users u
                LEFT JOIN appointments a ON u.id = a.user_id
                LEFT JOIN search_queries sq ON u.id = sq.user_id
                GROUP BY u.id, u.age_group, u.gender, u.location
            """

            if limit:
                query += f" LIMIT {limit}"

            cursor.execute(query)
            records = cursor.fetchall()
            cursor.close()

            result = [
                {
                    "user_id": record[0],
                    "age_group": record[1],
                    "gender": record[2],
                    "location": record[3],
                    "appointment_count": record[4],
                    "search_count": record[5],
                    "last_appointment_date": record[6],
                }
                for record in records
            ]

            logger.info(f"Extracted {len(result)} users for persona creation")
            return result
        except psycopg2.Error as error:
            logger.error(f"Error extracting users: {error}")
            raise

    def classify_user_persona(self, user_data: Dict[str, Any]) -> str:
        """Classify user into persona based on behavioral and demographic signals."""
        appointment_count = user_data.get("appointment_count", 0)
        search_count = user_data.get("search_count", 0)
        age_group = user_data.get("age_group", "unknown")

        engagement_score = (appointment_count * 0.6) + (search_count * 0.4)

        if engagement_score > 10:
            return "power_user"
        elif engagement_score > 5:
            return "active_user"
        elif engagement_score > 1:
            return "casual_user"
        else:
            return "inactive_user"

    def process_batch(self, users: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process a batch of users and assign personas."""
        personas = []

        for user in users:
            try:
                persona_type = self.classify_user_persona(user)
                persona_record = {
                    "user_id": user["user_id"],
                    "persona_type": persona_type,
                    "age_group": user["age_group"],
                    "gender": user["gender"],
                    "location": user["location"],
                    "appointment_count": user["appointment_count"],
                    "search_count": user["search_count"],
                    "last_appointment_date": user["last_appointment_date"],
                    "created_at": datetime.now(),
                }
                personas.append(persona_record)
            except Exception as error:
                logger.warning(f"Error processing user {user.get('user_id')}: {error}")
                continue

        logger.info(f"Processed {len(personas)} personas from batch")
        return personas

    def load_personas(self, personas: List[Dict[str, Any]]) -> int:
        """Load persona assignments into database."""
        if not self.connection:
            self.connect()

        if not personas:
            logger.info("No personas to load")
            return 0

        try:
            cursor = self.connection.cursor()

            records_to_insert = [
                (
                    persona["user_id"],
                    persona["persona_type"],
                    json.dumps({
                        "age_group": persona["age_group"],
                        "gender": persona["gender"],
                        "location": persona["location"],
                        "appointment_count": persona["appointment_count"],
                        "search_count": persona["search_count"],
                    }),
                    persona["created_at"],
                )
                for persona in personas
            ]

            query = """
                INSERT INTO user_personas (user_id, persona_type, attributes, created_at)
                VALUES %s
                ON CONFLICT (user_id) DO UPDATE SET persona_type = EXCLUDED.persona_type, attributes = EXCLUDED.attributes
            """

            execute_values(cursor, query, records_to_insert)
            self.connection.commit()
            rows_affected = cursor.rowcount
            cursor.close()

            logger.info(f"Loaded {rows_affected} persona assignments")
            return rows_affected
        except psycopg2.Error as error:
            self.connection.rollback()
            logger.error(f"Error loading personas: {error}")
            raise

    def run_batch_processing(self, total_users: Optional[int] = None) -> Dict[str, Any]:
        """Execute batch persona creation for large user populations."""
        try:
            self.connect()
            users = self.extract_users_for_persona_creation(limit=total_users)

            total_processed = 0
            total_loaded = 0

            for i in range(0, len(users), self.batch_size):
                batch = users[i : i + self.batch_size]
                personas = self.process_batch(batch)
                rows_loaded = self.load_personas(personas)
                total_processed += len(batch)
                total_loaded += rows_loaded
                logger.info(f"Batch {i // self.batch_size + 1}: processed {len(batch)}, loaded {rows_loaded}")

            result = {
                "status": "success",
                "total_users_processed": total_processed,
                "total_personas_created": total_loaded,
                "batch_size": self.batch_size,
                "timestamp": datetime.now().isoformat(),
            }
            logger.info(f"Batch persona creation completed: {result}")
            return result
        except Exception as error:
            logger.error(f"Batch persona creation failed: {error}")
            return {
                "status": "failed",
                "error": str(error),
                "timestamp": datetime.now().isoformat(),
            }
        finally:
            self.disconnect()