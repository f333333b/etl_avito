import logging
import sys
from typing import Any, Callable, Dict

import pandas as pd
import yaml

from config import PATH_VARS, REQUIRED_ENV_VARS, load_config
from data.reference_data import autoload_allowed_values, dealerships
from etl.extract import read_excel_file
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
)
from etl.validation import validate_data

logger = logging.getLogger(__name__)
logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format=(
        "%(asctime)s | %(levelname)-8s| %(name)-15s| %(lineno)-4d| " "%(funcName)-28s| %(message)s"
    ),
)

TRANSFORM_FUNCTIONS: dict[str, Callable[[pd.DataFrame], pd.DataFrame]] = {
    "clean_raw_data": clean_raw_data,
    "convert_data_types": lambda df: convert_data_types(df, autoload_allowed_values),
    "normalize_columns_to_constants": normalize_columns_to_constants,
    "normalize_addresses_column": normalize_addresses_column,
    "remove_invalid_dealerships": remove_invalid_dealerships,
    "remove_duplicates_keep_latest": remove_duplicates_keep_latest,
    "normalize_group_by_latest": normalize_group_by_latest,
    "fill_missing_cities": lambda df: fill_missing_cities(df, dealerships),
}


def load_pipeline_config(config_path: str = "pipeline_config.yaml") -> Any:
    """Функция загрузки конфигурации пайплайна из YAML-файла"""
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except FileNotFoundError as e:
        logger.error(f"Конфигурационный YAML-файл не найден: {config_path}. Ошибка {e}")
        raise
    except yaml.YAMLError as e:
        logger.error(f"Ошибка парсинга YAML-файла: {e}")
        raise


def transform_pipeline(df: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
    """Функция трансформации согласно конфигурации."""
    transformations = config.get("transformations", [])
    for transform_name in transformations:
        if transform_name not in TRANSFORM_FUNCTIONS:
            logger.error(f"Неизвестная трансформация: {transform_name}")
            raise ValueError(f"Неизвестная трансформация: {transform_name}")
        df = TRANSFORM_FUNCTIONS[transform_name](df)
        # logger.info(f"После выполнения функции {transform_name} количество строк: {len(df)} шт.")
    return df


def run_etl() -> None:
    """Функция запуска ETL-пайплайна."""
    config = load_config(REQUIRED_ENV_VARS, PATH_VARS)
    pipeline_config = load_pipeline_config()

    try:
        logger.info("=== EXCTRACT ===")
        df = read_excel_file(config["INPUT_PATH"])

        # print(df['ContactPhone'].head())

        logger.info("=== TRANSFORM ===")
        df = transform_pipeline(df, pipeline_config)

        logger.info("=== VALIDATION ===")
        validate_data(df)

        logger.info("=== LOAD ===")
        load(df, config)

    except FileNotFoundError as e:
        logger.error(f"Ошибка доступа к файлу: {e}")
        raise
    except ValueError as e:
        logger.error(f"Ошибка валидации или трансформации: {e}")
        raise
    except Exception as e:
        logger.exception(f"Непредвиденная ошибка: {e}")
        raise


def main() -> None:
    try:
        run_etl()
    except (FileNotFoundError, ValueError) as e:
        logger.critical(f"Критическая ошибка: {e}")
        raise
    except Exception as e:
        logger.critical(f"Непредвиденная критическая ошибка: {e}")
        raise


if __name__ == "__main__":
    main()
