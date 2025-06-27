from __future__ import annotations

import logging
import re
from datetime import datetime
from typing import Any, Dict, List, Tuple

import pandas as pd

from etl.data.reference_data import cities, city_to_full_address, dealerships, autoload_allowed_values

logger = logging.getLogger(__name__)

def clean_raw_data(df: pd.DataFrame) -> pd.DataFrame:
    """Функция для удаления мусорных/пустых строк"""

    # стрип строковых ячеек
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

    # удаление полностью пустых строк
    df_cleaned = df.dropna(how="all")

    # удаление дублей по колонкам
    df_cleaned = df_cleaned.drop_duplicates(subset=["AvitoId", "Id"])

    # подсчет количества удаленных строк
    removed = len(df) - len(df_cleaned)
    logger.info(f"Удалено мусорных/пустых строк: {removed} шт.")

    return df_cleaned


def normalize_group_by_latest(df: pd.DataFrame) -> pd.DataFrame:
    """Функция для нормализации строк, сгруппированных по Title"""

    # logger.info(f"Перед нормализацией по Title: {df.shape[0]} строк")

    df["AvitoDateEnd"] = df["AvitoDateEnd"].astype(str)
    df["AvitoDateEnd"] = pd.to_datetime(df["AvitoDateEnd"], errors="coerce")
    df["StatusPriority"] = df["AvitoStatus"].apply(lambda x: 1 if x == "Активно" else 0)

    df_sorted = (
        df.sort_values(["Title", "AvitoDateEnd", "StatusPriority"], ascending=[True, False, False])
        .drop_duplicates(subset=["Title", "Address"], keep="first")
        .reset_index(drop=True)
    )

    df_sorted["AvitoDateEnd"] = df_sorted["AvitoDateEnd"].dt.strftime("%Y-%m-%d")
    df_sorted = df_sorted.drop(columns="StatusPriority")

    # logger.info(f"Количество нормализованных строк по колонке 'Title': {df_sorted.shape[0]}.")
    # logger.info(f"После нормализации по Title: {df_sorted.shape[0]} строк")
    logger.info(f"Удалено дубликатов по 'Title+Address': {len(df) - len(df_sorted)} шт.")

    return df_sorted


def normalize_addresses(raw_address: str, id: str) -> Tuple[bool, str]:
    """Вспомогательная функция для нормализации написания адресов в колонке Address"""

    for city, full_address in city_to_full_address.items():
        if re.search(rf"\b{re.escape(city)}\b", raw_address, re.IGNORECASE):
            return True, full_address
    return False, f"AvitoId: {id}, адрес: {raw_address}"


def remove_invalid_dealerships(df: pd.DataFrame) -> pd.DataFrame:
    """Функция удаления строк, нарушающих дилерство по брендам и городам"""

    invalid_ids = []

    def is_allowed(row: pd.Series) -> bool:
        brand = str(row["Make"]).strip()
        address = str(row["Address"]).strip()
        allowed_cities = dealerships.get(brand)
        if allowed_cities is None:
            return True
        for city in allowed_cities:
            if city.lower() in address.lower():
                return True
        invalid_ids.append(row["AvitoId"])
        return False

    result_df = df[df.apply(is_allowed, axis=1)]
    if invalid_ids:
        logger.info(f"Удалены строки с нарушением дилерства: {len(invalid_ids)} шт.")
        # invalid_list = [int(avito_id) for avito_id in invalid_ids]
        # logger.info(f"Список AvitoId удаленных строк:")
        # logger.info(invalid_list)
    else:
        logger.info("Нарушений дилерства не обнаружено")
    return result_df


def fill_missing_cities(df: pd.DataFrame, dealerships: Dict) -> pd.DataFrame:
    """Функция проверки размещения по всем городам согласно Title и Make"""

    id_counter = 1
    new_rows = []
    for (title, make), group in df.groupby(["Title", "Make"]):
        allowed_cities = dealerships.get(make, cities)
        existing_cities = set()
        for _, row in group.iterrows():
            if str(row["AvitoStatus"]).strip().lower() != "активно":
                continue
            address = str(row["Address"])
            for city in allowed_cities:
                if city.lower() in address.lower():
                    existing_cities.add(city)
                    break
        missing_cities = set(allowed_cities) - existing_cities
        if missing_cities:
            template_row = group.iloc[0].copy()
            for city in sorted(missing_cities):
                new_row = template_row.copy()
                new_row["Address"] = f"{city}"
                new_row["AvitoId"] = ""
                new_row["AvitoDateEnd"] = ""
                new_row["AvitoStatus"] = "Активно"
                new_row["Id"] = f"{datetime.now().strftime('%d%m%Y')}{id_counter:06d}"
                id_counter += 1
                new_rows.append(new_row)
            # logger.info(f"Объявление '{title}': добавлено строк: {len(missing_cities)} шт.")
    if new_rows:
        df = pd.concat([df, pd.DataFrame(new_rows)], ignore_index=True)
        # отнимаем 1 - строку с названиями колонок
        logger.info(
            f"Проверка на размещение по городам. Добавлено новых строк: {len(new_rows)} шт."
        )
    else:
        logger.info("Все товары размещены в нужных городах. Новые строки не добавлялись.")
    # logger.info(df.tail(5))
    # logger.info(f"Размер итогового DataFrame: {df.shape}")
    return df


def normalize_columns_to_constants(df: pd.DataFrame) -> pd.DataFrame:
    """Функция нормализации (приведение к единым значениям)"""

    current_year = datetime.now().year
    df["AvitoStatus"] = "Активно"
    df.loc[df["Year"] != current_year, "Year"] = current_year
    if "Condition" in df.columns:
        df.loc[df["Condition"] != "Б/у", "Condition"] = "Б/у"
    if "Kilometrage" in df.columns:
        df.loc[df["Kilometrage"] != 5, "Kilometrage"] = 5
    if "DisplayAreas" in df.columns:
        df["DisplayAreas"] = df["DisplayAreas"].astype(str)
        df.loc[df["DisplayAreas"] != "", "DisplayAreas"] = ""
    return df


def normalize_addresses_column(df: pd.DataFrame) -> pd.DataFrame:
    """Функция нормализации адресов + удаление ненормализованных"""

    original_len = len(df)
    normalized_addresses = []
    error_messages: List = []

    for _, row in df.iterrows():
        is_valid, result = normalize_addresses(row["Address"], row["AvitoId"])
        if is_valid:
            normalized_addresses.append(result)
            error_messages.append(None)
        else:
            normalized_addresses.append(None)
            error_messages.append(result)

    df["Address"] = normalized_addresses
    df["address_error"] = error_messages

    df = df[df["Address"].notna()].reset_index(drop=True)
    removed = original_len - len(df)

    if removed > 0:
        logger.info(f"Удалено строк с ненормализованным адресом: {removed} шт.")

        # logger.info(f"Список ненормализованных адресов:")
        # for msg in filter(None, error_messages):
        #    logger.info(msg)

    df.drop(columns="address_error", inplace=True)
    return df


def convert_data_types(df: pd.DataFrame, autoload_allowed_values: dict) -> pd.DataFrame:
    """Функция приведения типов данных колонок из справочника"""
    df = df.copy()
    errors = []
    total_trimmed_rows = 0

    for column, props in autoload_allowed_values.items():
        if column not in df.columns:
            continue

        target_type = props.get("data_type")
        try:
            if target_type is str:
                max_length = props.get("max_length")
                if column == "ContactPhone":
                    df[column] = df[column].apply(lambda x: str(int(x)) if pd.notna(x) else "")
                else:
                    df[column] = df[column].astype(str).fillna("")
                if max_length:
                    original_lengths = df[column].str.len()
                    df[column] = df[column].str.slice(0, max_length)
                    trimmed = (original_lengths > max_length).sum()
                    total_trimmed_rows += trimmed
            elif target_type is int:
                df[column] = pd.to_numeric(df[column], errors="coerce")
                df[column] = df[column].astype("Int64")
            elif target_type is float:
                df[column] = pd.to_numeric(df[column], errors="coerce")
            elif target_type is datetime:
                df[column] = pd.to_datetime(df[column], errors="coerce")
            else:
                raise ValueError(f"Неизвестный тип {target_type} для колонки {column}")
        except Exception as e:
            error_msg = f"Ошибка при приведении {column} к {target_type}: {e}"
            logger.error(error_msg)
            errors.append(error_msg)

    if total_trimmed_rows > 0:
        logger.info(f"Всего обрезано строк по длине: {total_trimmed_rows} шт.")
    if errors:
        logger.info(f"Обнаружено {len(errors)} ошибок при приведении типов")

    return df


def remove_duplicates_keep_latest(df: pd.DataFrame) -> pd.DataFrame:
    """Функция удаления дубликатов"""
    df = df.copy()

    for column in ["AvitoId", "Id"]:
        df = df.sort_values("AvitoDateEnd", ascending=False)
        df = df.drop_duplicates(subset=column, keep="first").reset_index(drop=True)

    return df


def exceeds_length(val: Any, max_length: int) -> bool:
    if max_length is None or not isinstance(val, str):
        return False
    return len(val) > max_length

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

def transform_pipeline(df: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
    """Функция трансформации согласно конфигурации"""
    transformations = config.get("transformations", [])
    for transform_name in transformations:
        if transform_name not in TRANSFORM_FUNCTIONS:
            logger.error(f"Неизвестная трансформация: {transform_name}")
            raise ValueError(f"Неизвестная трансформация: {transform_name}")
        df = TRANSFORM_FUNCTIONS[transform_name](df)
    return df