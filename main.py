import logging
import pandas as pd
import yaml
from typing import Dict, Callable
from etl.extract import read_excel_file
from etl.transform import (
    clean_raw_data, normalize_group_by_latest, normalize_addresses_column, remove_invalid_dealerships,
    fill_missing_cities, normalize_columns_to_constants, convert_data_types
)
from etl.validation import validate_data
from etl.dealerships import dealerships
from etl.config import load_config, REQUIRED_ENV_VARS, PATH_VARS
from etl.load import load

logger = logging.getLogger(__name__)

TRANSFORM_FUNCTIONS: Dict[str, Callable[[pd.DataFrame], pd.DataFrame]] = {
    'clean_raw_data': clean_raw_data,
    'normalize_group_by_latest': normalize_group_by_latest,
    'normalize_addresses_column': normalize_addresses_column,
    'remove_invalid_dealerships': remove_invalid_dealerships,
    'fill_missing_cities': lambda df: fill_missing_cities(df, dealerships),
    'normalize_columns_to_constants': normalize_columns_to_constants,
    'convert_data_types': convert_data_types
}

def load_pipeline_config(config_path: str = 'pipeline_config.yaml') -> Dict:
    """Функция загрузки конфигурации пайплайна из YAML-файла"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except FileNotFoundError as e:
        logger.error(f"Конфигурационный YAML-файл не найден: {config_path}. Ошибка {e}")
        raise
    except yaml.YAMLError as e:
        logger.error(f"Ошибка парсинга YAML-файла: {e}")
        raise

def transform_pipeline(df: pd.DataFrame, config: Dict) -> pd.DataFrame:
    """Функция трансформации согласно конфигурации"""
    transformations = config.get('transformations', [])
    for transform_name in transformations:
        if transform_name not in TRANSFORM_FUNCTIONS:
            logger.error(f"Неизвестная трансформация: {transform_name}")
            raise ValueError(f"Неизвестная трансформация: {transform_name}")
        logger.info(f"Выполняется {transform_name}: {TRANSFORM_FUNCTIONS[transform_name].__doc__}")
        df = TRANSFORM_FUNCTIONS[transform_name](df)
    return df

def run_etl():
    """Функция запуска ETL-пайплайна"""
    config = load_config(REQUIRED_ENV_VARS, PATH_VARS)
    pipeline_config = load_pipeline_config()

    try:
        df = read_excel_file(config['INPUT_PATH'])

        # валидация
        is_valid, errors = validate_data(df)
        print(errors)
        if not is_valid:
            logger.error(f"Валидация не пройдена: {'; '.join(errors)}")
            raise ValueError("Валидация не пройдена")
        else:
            logger.info("Валидация пройдена успешно")

        # трансформация
        df = transform_pipeline(df, pipeline_config)

        # загрузка
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

def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    try:
        run_etl()
    except (FileNotFoundError, ValueError) as e:
        logger.critical(f"Критическая ошибка: {e}")
        raise
    except Exception as e:
        logger.critical(f"Непредвиденная ошибка: {e}")
        raise

if __name__ == "__main__":
    main()