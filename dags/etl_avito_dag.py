from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator

from etl.config import PATH_VARS, REQUIRED_ENV_VARS, load_config
from etl.main import main as run_etl_pipeline


def etl_wrapper():
    config = load_config(REQUIRED_ENV_VARS, PATH_VARS)
    run_etl_pipeline(**config)


with DAG(
    dag_id="etl_avito_dag",
    start_date=datetime(2024, 1, 1),
    schedule="@daily",
    catchup=False,
    tags=["avito", "etl"],
    description="DAG для ежедневного запуска ETL пайплайна Avito",
) as dag:

    run_pipeline = PythonOperator(task_id="run_etl_pipeline", python_callable=run_etl_pipeline)

    run_pipeline
