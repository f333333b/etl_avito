from __future__ import annotations

import logging
import os

import pandas as pd

logger = logging.getLogger(__name__)


def read_input_file(path: str) -> pd.DataFrame:
    """Функция чтения входных данных"""

    if not os.path.isfile(path):
        logger.error(f"Файл не найден: {path}")
        raise FileNotFoundError(f"Файл не найден: {path}")

    file_size = os.path.getsize(path)
    ext = os.path.splitext(path)[1].lower()

    try:
        if ext in [".xls", ".xlsx"]:
            df = pd.read_excel(path)
        elif ext == ".csv":
            df = pd.read_csv(path, encoding="utf-8")
        else:
            error_msg = f"Неподдерживаемый формат файла: {ext}"
            logger.error(error_msg)
            raise ValueError(error_msg)
    except Exception as e:
        logger.exception(f"Ошибка при чтении файла {path}: {e}")
        raise

    logger.info(f"Файл успешно прочитан: {path}")
    logger.info(f"Размер файла: {file_size / (1024 ** 2):.2f} МБ. Количество строк: {len(df)}")

    required_columns = [
        "Id",
        "Address",
        "Category",
        "Title",
        "Description",
        "VehicleType",
        "Make",
        "Model",
        "Type",
        "Year",
        "Availability",
        "Condition",
    ]
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        error_msg = f"Отсутствуют обязательные колонки: {', '.join(missing_columns)}"
        logger.error(error_msg)
        raise ValueError(error_msg)

    return df
