import logging
import pandas as pd
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.log.logging_mixin import LoggingMixin

from etl.config import PATH_VARS, REQUIRED_ENV_VARS, load_config, load_pipeline_config
from etl.data.reference_data import autoload_allowed_values, dealerships
from etl.extract import read_input_file
from etl.load import load
from etl.transform import (
    clean_raw_data,
    convert_data_types,
    fill_missing_cities,
    normalize_addresses_column,
    normalize_columns_to_constants,
    normalize_group_by_latest,
    remove_duplicates_keep_latest,
    remove_invalid_dealerships,
    transform_pipeline
)
from etl.validation import validate_data

DATA_PATH = "/opt/airflow/etl/data/avito_data.parquet"

logger = LoggingMixin().log

def extract() -> None:
    """Функция извлечения данных"""
    config = load_config(REQUIRED_ENV_VARS, PATH_VARS)
    logger.info("=== EXTRACT ===")
    df = read_input_file(config["INPUT_PATH"])
    df.to_parquet(DATA_PATH, index=False)

def transform() -> None:
    """Функция трансформации данных"""
    logger.info("=== TRANSFORM ===")
    pipeline_config = load_pipeline_config()
    df = pd.read_parquet(DATA_PATH)
    df = transform_pipeline(df, pipeline_config)
    df.to_parquet(DATA_PATH, index=False)

def validate() -> None:
    """Функция валидации данных"""
    logger.info("=== VALIDATION ===")
    df = pd.read_parquet(DATA_PATH)
    validate_data(df)

def load_data() -> None:
    """Функция выгрузки обработанных данных"""
    logger.info("=== LOAD ===")
    config = load_config(REQUIRED_ENV_VARS, PATH_VARS)
    df = pd.read_parquet(DATA_PATH)
    load(df, config)


default_args = {
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="etl_avito_dag",
    start_date=datetime(2025, 6, 6),
    schedule="@daily",
    catchup=False,
    default_args=default_args,
    tags=["avito", "etl"],
    description="DAG для ежедневного запуска ETL пайплайна Avito",
) as dag:
    t_extract = PythonOperator(
        task_id="extract",
        python_callable=extract,
    )

    t_transform = PythonOperator(
        task_id="transform",
        python_callable=transform,
    )

    t_validate = PythonOperator(
        task_id="validate",
        python_callable=validate,
    )

    t_load_data = PythonOperator(
        task_id="load_data",
        python_callable=load_data,
    )

    t_extract >> t_transform >> t_validate >> t_load_data
