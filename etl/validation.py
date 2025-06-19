import pandas as pd
import requests
import logging
from datetime import datetime
from typing import Tuple, List
from contextlib import contextmanager
import os

logger = logging.getLogger(__name__)


@contextmanager
def excel_writer(filename: str):
    """Контекстный менеджер для записи Excel-файла."""
    try:
        yield filename
    except Exception as e:
        logger.error(f"Ошибка при записи файла {filename}: {e}")
        raise


def validate_uniqueness(df: pd.DataFrame) -> Tuple[bool, List[str]]:
    """Функция валидации уникальности колонок 'AvitoId' и 'Id'"""
    errors = []
    for column, skip_empty in [('AvitoId', True), ('Id', False)]:
        filled_ids = df[column].dropna() if skip_empty else df[column]
        duplicated = filled_ids[filled_ids.duplicated()].unique()
        if len(duplicated) > 0:
            filename = f"duplicates_{column}_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.xlsx"
            with excel_writer(filename) as fname:
                df[df[column].isin(duplicated)].to_excel(fname, index=False)
            errors.append(f"Найдены дубликаты в '{column}' (всего: {len(duplicated)}). Сохранено в: {filename}")
        else:
            logger.info(f"Проверка '{column}' на уникальность пройдена")
    return (len(errors) == 0, errors)


def validate_urls(df: pd.DataFrame) -> Tuple[bool, List[str]]:
    """Функция валидации значений колонок VideoURL и VideoFilesURL"""
    errors = []
    url_columns = ['VideoURL', 'VideoFilesURL']
    with requests.Session() as session:
        for col in url_columns:
            if col not in df.columns:
                errors.append(f"Колонка {col} отсутствует")
                continue
            for url in df[col].astype(str):
                if not url.startswith(('http://', 'https://')):
                    errors.append(f"Некорректный формат URL в колонке {col}: {url}")
                    continue
                try:
                    response = session.head(url, timeout=5, allow_redirects=True)
                    if response.status_code != 200:
                        errors.append(f"URL {url} в колонке {col} вернул статус {response.status_code}")
                except requests.RequestException as e:
                    errors.append(f"Ошибка при HEAD-запросе к {url} в колонке {col}: {e}")
    if not errors:
        logger.info("Проверка URL пройдена")
    return (len(errors) == 0, errors)


def validate_required_fields(df: pd.DataFrame) -> Tuple[bool, List[str]]:
    """Функция валидации заполнения обязательных колонок"""
    errors = []
    base_columns = ['Id', 'Address', 'Category', 'Title', 'Description', 'VehicleType', 'Make', 'Model',
                    'Type', 'Year', 'Availability', 'Condition']
    moto_columns = ['EngineType', 'Power', 'EngineCapacity', 'Kilometrage']
    quadro_columns = moto_columns + ['PersonCapacity']
    boat_engines_columns = ['EngineType', 'Power']
    boats_columns = ['FloorType', 'Length', 'Width', 'SeatingCapacity', 'MaxPower', 'TrailerIncluded', 'EngineIncluded']

    # Проверка наличия базовых колонок
    missing_columns = [col for col in base_columns if col not in df.columns]
    if missing_columns:
        errors.append(f"Отсутствуют обязательные колонки: {', '.join(missing_columns)}")

    def check_row(row):
        missing = []
        for col in base_columns:
            val = row.get(col)
            if pd.isna(val) or str(val).strip() == "":
                missing.append(col)
        vt = row.get("VehicleType")
        tp = row.get("Type")
        additional = []
        if vt in ["Мопеды и скутеры", "Мотоциклы"]:
            additional = moto_columns
        elif vt == "Квадроциклы":
            additional = quadro_columns
        elif vt == "Моторные лодки и моторы":
            if tp == "Лодочный мотор":
                additional = boat_engines_columns
            elif tp in ["Лодка ПВХ (надувная)", "Лодка RIB (комбинированная)", "Лодка с жестким корпусом"]:
                additional = boats_columns
        for col in additional:
            val = row.get(col)
            if pd.isna(val) or str(val).strip() == "":
                missing.append(col)
        image_urls_empty = pd.isna(row.get("ImageUrls")) or str(row["ImageUrls"]).strip() == ""
        image_names_empty = pd.isna(row.get("ImageNames")) or str(row["ImageNames"]).strip() == ""
        if image_urls_empty and image_names_empty:
            missing.append("ImageUrls or ImageNames")
        if missing:
            return f"Строка {row.name}: пропущены обязательные поля: {', '.join(missing)}"
        return None

    row_errors = df.apply(check_row, axis=1).dropna().tolist()
    errors.extend(row_errors)

    if not errors:
        logger.info("Проверка обязательных полей пройдена")
    return (len(errors) == 0, errors)


def validate_data(df: pd.DataFrame) -> Tuple[bool, List[str]]:
    """Общая функция валидации данных."""
    errors = []
    is_valid = True

    # валидация уникальности
    valid, uniq_errors = validate_uniqueness(df)
    errors.extend(uniq_errors)
    is_valid &= valid

    # валидация обязательных полей
    valid, req_errors = validate_required_fields(df)
    errors.extend(req_errors)
    is_valid &= valid

    # валидация URL
    valid, url_errors = validate_urls(df)
    errors.extend(url_errors)
    is_valid &= valid

    if is_valid:
        logger.info("Все проверки валидации пройдены успешно")
    else:
        logger.error(f"Валидация не пройдена: {'; '.join(errors)}")

    return (is_valid, errors)