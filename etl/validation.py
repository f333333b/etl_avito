import re
import os
import pandas as pd
import requests
import logging
import time
import random
from datetime import datetime
from typing import List, Optional, Tuple

from etl.load import excel_writer
from data.reference_data import autoload_allowed_values
from utils import ensure_dir_created

logger = logging.getLogger(__name__)

def get_duplicated_values(series: pd.Series) -> pd.Series:
    """Вспомогательная функция, которая возвращает уникальные значения, дублирующиеся в серии"""
    return series[series.duplicated()].unique()

def get_duplicated_rows(df: pd.DataFrame, column: str, skip_empty: bool = True) -> pd.DataFrame:
    """Вспомогательная функция, которая возвращает строки, содержащие дублирующиеся значения в заданной колонке"""
    if skip_empty:
        mask = df[column].notna()
    else:
        mask = pd.Series([True] * len(df))
    filtered = df[mask]
    return filtered[filtered[column].duplicated(keep=False)]

def save_duplicates_to_excel(df: pd.DataFrame, column: str) -> str:
    """Вспомогательная функция для сохранения дубликатов в Excel-файл"""

    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    project_root = os.path.dirname(os.path.abspath(__file__))
    folder = f"{project_root}\\validation_logs"
    ensure_dir_created(folder)
    filename = f"{folder}\\duplicates_{column}_{timestamp}.xlsx"
    with excel_writer(filename) as fname:
        df.to_excel(fname, index=False)
    logger.info(f"Дубликаты сохранены в файл: {filename}")
    return filename

def validate_uniqueness(df: pd.DataFrame) -> tuple[bool, List[str]]:
    """Функция валидации уникальности колонок AvitoId и Id"""
    errors = []
    for column, skip_empty in [('AvitoId', True), ('Id', False)]:
        duplicated_df = get_duplicated_rows(df, column, skip_empty)
        if not duplicated_df.empty and duplicated_df[column].nunique() > 0:
            file_path = save_duplicates_to_excel(duplicated_df, column)
            errors.append(
                f"Найдены дубликаты в '{column}' (всего: {duplicated_df[column].nunique()}). Сохранено в: {file_path}"
            )
    return len(errors) == 0, errors

def check_url(session: requests.Session, id: str, url: str, delay_range=(0.2, 0.5)) -> Optional[str]:
    """Вспомогательная функция для проверки одного URL"""
    if pd.isna(url) or str(url).strip() == '':
        return None
    if not url.startswith(('http://', 'https://')):
        return f"Некорректный формат URL в строке с Id {id}: {url}"
    try:
        time.sleep(random.uniform(*delay_range))
        response = session.head(url, timeout=5, allow_redirects=True)
        if response.status_code != 200:
            return f"URL {url} в строке с Id {id} вернул статус {response.status_code}"
    except requests.RequestException as e:
        return f"Ошибка при HEAD-запросе к {url} в строке с Id {id}: {e}"
    return None

def validate_urls(df: pd.DataFrame) -> tuple[bool, List[str]]:
    """Функция валидации значений колонок VideoURL и VideoFilesURL"""

    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/123.0.0.0 Safari/537.36"
        )
    }
    errors = []
    url_columns = ['VideoURL', 'VideoFilesURL', 'ImageUrls']
    total_checked = 0
    with requests.Session() as session:
        session.headers.update(HEADERS)
        for col in url_columns:
            if col not in df.columns:
                logger.warning(f"Колонка {col} отсутствует, проверка пропущена")
                continue
            # отключить, потому что нужно проработать, как обойти ограничение авито на частые запросы (to do)
            if col == 'ImageUrls':
                for row_id, image_urls in df[col].astype(str).items():
                    if image_urls.strip():
                        first_image_url = image_urls.split('|')[0]
                        total_checked += 1
                        check_result = check_url(session=session, id=row_id, url=first_image_url.strip())
                        time.sleep(2)
                        if check_result:
                            errors.append(check_result)
            else:
                for row_id, url in df[col].items():
                    total_checked += 1
                    check_result = check_url(session=session, id=row_id, url=url)
                    if check_result:
                        errors.append(check_result)
    if not errors:
        logger.info("Проверка URL пройдена успешно")
    logger.info(f"Всего URL проверено: {total_checked}, найдено ошибок: {len(errors)}")
    return len(errors) == 0, errors

def validate_required_fields(df: pd.DataFrame) -> Tuple[bool, List[str]]:
    """Функция валидации обязательных колонок: наличие, заполненность, допустимые значения, тип данных"""

    errors = []
    required_columns = [key for key, val in autoload_allowed_values.items() if val['required_parameter']]

    # валидация наличия колонок
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        errors.append(f"Отсутствуют обязательные колонки: {', '.join(missing_columns)}")

    present_required = [col for col in required_columns if col in df.columns]

    def check_row(row: pd.Series) -> Optional[str]:
        missing = []
        invalid = []
        wrong_type = []

        for col in present_required:
            val = row[col]

            if pd.isna(val) or str(val).strip() == "":
                missing.append(col)
                continue

            allowed = autoload_allowed_values[col].get('allowed_values')
            if allowed is not None and val not in allowed:
                invalid.append(col)

            expected_type = autoload_allowed_values[col].get('data_type')
            if expected_type and not isinstance(val, expected_type):
                wrong_type.append(col)

        messages = []
        if missing:
            plural_missing = "заполнен" if len(missing) == 1 else "заполнены"
            messages.append(f"не {plural_missing}: {', '.join(missing)}")
        if invalid:
            messages.append(f"недопустимые значения: {', '.join(invalid)}")
        if wrong_type:
            plural_wrong_type = "колонки" if len(wrong_type) == 1 else "колонок"
            messages.append(f"неверный тип данных у {plural_wrong_type}: {', '.join(wrong_type)}")

        if messages:
            return f"Строка {row.name}: " + "; ".join(messages)
        return None

    errors.extend(df.apply(check_row, axis=1).dropna().tolist())
    return len(errors) == 0, errors

def validate_format_fields(df: pd.DataFrame) -> tuple[bool, List[str]]:
    """Функция валидации формата данных в соответствии с требованиями каждой колонки"""
    errors = []
    is_valid = True

    if 'EMail' in df.columns:
        invalid_emails = df[~df['EMail'].fillna('').astype(str).str.match(r"[^@]+@[^@]+\.[^@]+")]
        if not invalid_emails.empty:
            is_valid = False
            errors.append(f"Некорректные email: {len(invalid_emails)} строк")

    if 'ContactPhone' in df.columns:
        invalid_phones = df[~df['ContactPhone'].fillna('').astype(str).str.fullmatch(r"7\d{10}")]
        if not invalid_phones.empty:
            is_valid = False
            errors.append(f"Некорректные номера телефонов: {len(invalid_phones)} строк")

    if 'Id' in df.columns:
        invalid_ids = df[~df['Id'].fillna('').astype(str).str.fullmatch(r"[A-Za-z0-9]+")]
        if not invalid_ids.empty:
            is_valid = False
            errors.append(f"Некорректные Id: {len(invalid_ids)} строк")

    if 'AvitoId' in df.columns:
        invalid_avito_ids = df[~df['AvitoId'].astype(str).str.fullmatch(r"\d+")]
        if not invalid_avito_ids.empty:
            is_valid = False
            errors.append(f"Некорректные AvitoId: {len(invalid_avito_ids)} строк")

    return is_valid, errors

def validate_data(df: pd.DataFrame) -> tuple[bool, List[str]]:
    """Общая функция валидации данных"""
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
    #valid, url_errors = validate_urls(df)
    #errors.extend(url_errors)
    #is_valid &= valid

    # валидация форматов
    valid, format_errors = validate_format_fields(df)
    errors.extend(format_errors)
    is_valid &= valid

    if is_valid:
        logger.info("Все проверки валидации пройдены успешно")
    else:
        logger.critical("!!! Валидация не пройдена !!!")
        for error in errors:
            logger.critical(error)

    return is_valid, errors