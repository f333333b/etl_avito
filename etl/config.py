import os
from dotenv import load_dotenv
import logging
from typing import Dict, Tuple

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_config(required_vars: list[str], input_path: str, output_path: str) -> Tuple[Dict[str, str], bool]:
    """Функция загрузки и валидации конфигурации, включая переменные окружения и пути к файлам"""

    load_dotenv()
    env_vars = {}
    missing_vars = []

    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing_vars.append(var)
        else:
            env_vars[var] = value

    if missing_vars:
        error_msg = f"Отсутствуют обязательные переменные окружения: {', '.join(missing_vars)}"
        logger.error(error_msg)
        raise EnvironmentError(error_msg)

    if not os.path.isfile(input_path):
        error_msg = f"Входной файл не существует: {input_path}"
        logger.error(error_msg)
        raise FileNotFoundError(error_msg)

    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.isdir(output_dir):
        error_msg = f"Выходная директория не существует: {output_dir}"
        logger.error(error_msg)
        raise FileNotFoundError(error_msg)

    api_flag = False
    logger.info("Конфигурация успешно загружена и проверена.")
    return env_vars, api_flag

REQUIRED_ENV_VARS = ['CLIENT_ID', 'CLIENT_SECRET', 'USER_ID', 'YANDEX_TOKEN', 'EMAIL']
INPUT_PATH: str = r"C:\Users\fgkh\Desktop\sample.xlsx"
OUTPUT_PATH: str = r"C:\Users\fgkh\Desktop\123.xlsx"

try:
    env_vars, API_FLAG = load_config(REQUIRED_ENV_VARS, INPUT_PATH, OUTPUT_PATH)
    CLIENT_ID: str = env_vars['CLIENT_ID']
    CLIENT_SECRET: str = env_vars['CLIENT_SECRET']
    USER_ID: str = env_vars['USER_ID']
    YANDEX_TOKEN: str = env_vars['YANDEX_TOKEN']
    EMAIL: str = env_vars['EMAIL']
except (EnvironmentError, FileNotFoundError) as e:
    logger.error(f"Ошибка конфигурации: {str(e)}")
    raise