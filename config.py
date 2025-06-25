import logging
import os
from typing import Any, Dict, List

from dotenv import load_dotenv

logger = logging.getLogger(__name__)

REQUIRED_ENV_VARS = [
    "CLIENT_ID",
    "CLIENT_SECRET",
    "YANDEX_TOKEN",
    "EMAIL",
    "USER_ID",
    "API_FLAG",
]

PATH_VARS = [
    "INPUT_PATH",
    "OUTPUT_PATH",
]


def load_config(required_vars: list[str], path_vars: list[str]) -> Dict[str, Any]:
    """Функция загрузки и валидации конфигурации, включая переменные окружения и пути к файлам"""

    load_dotenv()
    config: Dict[str, Any] = {}
    missing_vars: List[Any] = []

    for var in required_vars + path_vars:
        value = os.getenv(var)
        if not value:
            missing_vars.append(var)
        else:
            config[var] = value

    if missing_vars:
        error_msg = "Отсутствуют обязательные переменные окружения: " + ", ".join(missing_vars)
        logger.error(error_msg)
        raise EnvironmentError(error_msg)

    if not os.path.isfile(config["INPUT_PATH"]):
        error_msg = f"Входной файл не существует: {config['INPUT_PATH']}"
        logger.error(error_msg)
        raise FileNotFoundError(error_msg)

    output_dir = os.path.dirname(config["OUTPUT_PATH"])
    if output_dir and not os.path.isdir(output_dir):
        error_msg = f"Выходная директория не существует: {output_dir}"
        logger.error(error_msg)
        raise FileNotFoundError(error_msg)

    logger.info("Конфигурация успешно загружена и проверена.")

    return config
