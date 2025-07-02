import os
from datetime import datetime, timedelta

import glob
import pandas as pd
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.log.logging_mixin import LoggingMixin

from etl.config import PATH_VARS, REQUIRED_ENV_VARS, load_config, load_pipeline_config
from etl.extract import extract_files
from etl.load import load
from etl.transform import transform_pipeline
from etl.validation import validate_data

DATA_PATH = "/opt/airflow/etl/data/"

logger = LoggingMixin().log


def extract() -> None:
    """Функция извлечения данных"""
    config = load_config(REQUIRED_ENV_VARS, PATH_VARS)
    logger.info("=== EXTRACT ===")

    extracted = extract_files(config["INPUT_PATH"])

    if not extracted:
        logger.warning("EXTRACT завершён: файлов для обработки не найдено.")
        return

    os.makedirs(DATA_PATH, exist_ok=True)

    for i, (file_name, df) in enumerate(extracted, start=1):
        parquet_name = f"avito_data_{file_name}.parquet"
        output_path = os.path.join(DATA_PATH, parquet_name)

        df.to_parquet(output_path, index=False)
        logger.info(f"[{i}] Файл сохранен: {output_path}, строк: {len(df)}")


def transform() -> None:
    """Функция трансформации данных"""

    logger.info("=== TRANSFORM ===")
    pipeline_config = load_pipeline_config()
    parquet_files = glob.glob(os.path.join(DATA_PATH, "avito_data_account_*.parquet"))
    for parquet_file in parquet_files:
        logger.info(f"Трансформация стартует для файла: {parquet_file}")

        df = pd.read_parquet(parquet_file)
        df = transform_pipeline(df, pipeline_config)
        df.to_parquet(parquet_file, index=False)

        logger.info(f"Трансформация завершена для файла: {parquet_file}")


def validate() -> None:
    """Функция валидации данных"""
    logger.info("=== VALIDATION ===")

    parquet_files = glob.glob(os.path.join(DATA_PATH, "avito_data_account_*.parquet"))

    for parquet_file in parquet_files:
        logger.info(f"Валидация стартует для файла: {parquet_file}")

        df = pd.read_parquet(parquet_file)
        validate_data(df)

        logger.info(f"Валидация завершена для файла: {parquet_file}")


def load_data() -> None:
    """Функция выгрузки обработанных данных"""

    logger.info("=== LOAD ===")
    config = load_config(REQUIRED_ENV_VARS, PATH_VARS)
    parquet_files = glob.glob(os.path.join(DATA_PATH, "avito_data_account_*.parquet"))

    for parquet_file in parquet_files:
        logger.info(f"Загрузка стартует для файла: {parquet_file}")

        df = pd.read_parquet(parquet_file)
        load(df, config)

        os.remove(parquet_file)
        logger.info(f"Загрузка завершена для файла: {parquet_file}")


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
