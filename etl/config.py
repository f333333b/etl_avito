import logging
import os
from typing import Any, Dict, List, Optional

import yaml
from airflow.models import Variable
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

REQUIRED_ENV_VARS = [
    "CLIENT_ID",
    "CLIENT_SECRET",
    "YANDEX_TOKEN",
    "EMAIL",
    "USER_ID",
    "API_FLAG",
    "IS_SINGLE_FILE",
]

PATH_VARS = ["INPUT_PATH", "OUTPUT_PATH", "PIPELINE_CONFIG"]


def load_pipeline_config(config_path: Optional[str] = None) -> Any:
    """Функция загрузки конфигурации пайплайна из YAML-файла"""
    path = config_path or os.environ.get("PIPELINE_CONFIG", "/opt/airflow/etl/pipeline_config.yaml")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except FileNotFoundError as e:
        logger.error(f"Конфигурационный YAML-файл не найден: {path}. Ошибка {e}")
        raise
    except yaml.YAMLError as e:
        logger.error(f"Ошибка парсинга YAML-файла: {e}")
        raise


def load_config(required_vars: List[str], path_vars: List[str]) -> Dict[str, Any]:
    load_dotenv()

    config: Dict[str, Any] = {}
    missing_vars: List[Any] = []

    for var in required_vars + path_vars:
        value = Variable.get(var, default_var=os.environ.get(var, None))

        if not value:
            missing_vars.append(var)
        else:
            config[var] = value

    if missing_vars:
        error_msg = "Отсутствуют обязательные переменные окружения: " + ", ".join(missing_vars)
        logger.error(error_msg)
        raise EnvironmentError(error_msg)

    if "IS_SINGLE_FILE" in config:
        config["IS_SINGLE_FILE"] = str(config["IS_SINGLE_FILE"]).strip().lower() == "true"

    if "INPUT_PATH" in config:
        path = config["INPUT_PATH"]

        if config.get("IS_SINGLE_FILE", False):
            if not os.path.isfile(path):
                error_msg = f"Входной файл не существует: {path}"
                logger.error(error_msg)
                raise FileNotFoundError(error_msg)
        else:
            if not os.path.isdir(path):
                error_msg = f"Входная директория не существует: {path}"
                logger.error(error_msg)
                raise FileNotFoundError(error_msg)

    if "OUTPUT_PATH" in config:
        output_dir = os.path.dirname(config["OUTPUT_PATH"])
        if output_dir and not os.path.isdir(output_dir):
            error_msg = f"Выходная директория не существует: {output_dir}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)

    logger.info("Конфигурация успешно загружена и проверена.")

    return config
