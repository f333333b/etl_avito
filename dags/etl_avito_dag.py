import logging
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

from etl.main import run_etl


def etl_wrapper():
    logging.info("Starting ETL pipeline...")
    run_etl()


default_args = {
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="etl_avito_dag",
    start_date=datetime(2024, 1, 1),
    schedule="@daily",
    catchup=False,
    default_args=default_args,
    tags=["avito", "etl"],
    description="DAG для ежедневного запуска ETL пайплайна Avito",
) as dag:

    run_pipeline = PythonOperator(task_id="run_avito_etl_pipeline", python_callable=etl_wrapper)

    run_pipeline
