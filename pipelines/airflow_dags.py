import logging
from datetime import datetime, timedelta
from typing import Dict, Any

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago

from pipelines.etl_appointment_data import AppointmentETL
from pipelines.etl_search_clickstream import SearchClickstreamETL
from pipelines.etl_health_records import HealthRecordsETL
from pipelines.etl_user_demographics import UserDemographicsETL
from pipelines.batch_persona_creation import BatchPersonaCreation

logger = logging.getLogger(__name__)

default_args = {
    "owner": "data_engineering",
    "depends_on_past": False,
    "start_date": days_ago(1),
    "email_on_failure": True,
    "email_on_retry": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}


def run_appointment_etl() -> Dict[str, Any]:
    """Execute appointment ETL pipeline."""
    etl = AppointmentETL()
    result = etl.run_etl(days_back=7)
    return result


def run_search_clickstream_etl() -> Dict[str, Any]:
    """Execute search clickstream ETL pipeline."""
    etl = SearchClickstreamETL()
    result = etl.run_etl(days_back=7)
    return result


def run_health_records_etl() -> Dict[str, Any]:
    """Execute health records ETL pipeline."""
    etl = HealthRecordsETL()
    result = etl.run_etl(days_back=30)
    return result


def run_user_demographics_etl() -> Dict[str, Any]:
    """Execute user demographics ETL pipeline."""
    etl = UserDemographicsETL()
    result = etl.run_etl(days_back=90)
    return result


def run_batch_persona_creation() -> Dict[str, Any]:
    """Execute batch persona creation for 100K+ users."""
    processor = BatchPersonaCreation(batch_size=5000)
    result = processor.run_batch_processing(total_users=None)
    return result


dag = DAG(
    "fortis_data_pipeline",
    default_args=default_args,
    description="ETL and batch processing pipeline for Fortis health platform",
    schedule_interval="0 2 * * *",
    catchup=False,
)

task_appointment_etl = PythonOperator(
    task_id="appointment_etl",
    python_callable=run_appointment_etl,
    dag=dag,
)

task_search_clickstream_etl = PythonOperator(
    task_id="search_clickstream_etl",
    python_callable=run_search_clickstream_etl,
    dag=dag,
)

task_health_records_etl = PythonOperator(
    task_id="health_records_etl",
    python_callable=run_health_records_etl,
    dag=dag,
)

task_user_demographics_etl = PythonOperator(
    task_id="user_demographics_etl",
    python_callable=run_user_demographics_etl,
    dag=dag,
)

task_batch_persona_creation = PythonOperator(
    task_id="batch_persona_creation",
    python_callable=run_batch_persona_creation,
    dag=dag,
)

task_appointment_etl >> task_batch_persona_creation
task_search_clickstream_etl >> task_batch_persona_creation
task_health_records_etl >> task_batch_persona_creation
task_user_demographics_etl >> task_batch_persona_creation