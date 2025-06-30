from __future__ import annotations

import logging
import os
from pathlib import Path

import pandas as pd

from etl.data.reference_data import autoload_allowed_values

logger = logging.getLogger(__name__)


def extract_files(path: str, is_single_path: bool) -> pd.DataFrame:
    """Функция запуска чтения файла/файлов"""
    if is_single_path:
        extension = os.path.splitext(path)[1].lower()
        result = read_input_file(path, extension)
    else:
        dfs = []
        for file_name in Path(path).rglob("*"):
            if file_name.suffix.lower() in [".csv", ".xls", ".xlsx"]:
                extension = file_name.suffix.lower()
                df = read_input_file(str(file_name), extension)
                dfs.append(df)
        result = pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()

    logger.info(f"Общее количество строк: {len(result)}")
    return result


def read_input_file(file_path: str, extension: str) -> pd.DataFrame:
    """Функция чтения входных данных"""

    try:
        if extension in [".xls", ".xlsx"]:
            df = pd.read_excel(file_path)
        elif extension == ".csv":
            df = pd.read_csv(file_path, encoding="utf-8")
        else:
            error_msg = f"Неподдерживаемый формат файла: {extension}"
            logger.error(error_msg)
            raise ValueError(error_msg)
    except Exception as e:
        logger.exception(f"Ошибка при чтении файла {file_path}: {e}")
        raise

    file_size = os.path.getsize(file_path) / (1024 * 1024)
    logger.info(f"Файл успешно прочитан: {file_path}")
    logger.info(f"Размер файла: {file_size:.2f} MB")

    required_columns = [
        key for key, value in autoload_allowed_values.items() if value["required_parameter"]
    ]

    if df.empty:
        logger.warning(f"Файл пустой: {file_path}. Размер файла: {file_size:.2f} MB")
    else:
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            error_msg = f"Отсутствуют обязательные колонки: {', '.join(missing_columns)}"
            logger.error(error_msg)
            raise ValueError(error_msg)

    return df
