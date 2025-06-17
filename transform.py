import re
import pandas as pd
import logging
from datetime import datetime
from dealerships import cities, dealerships, city_to_full_address

unmatched_addresses = set()
id_counter = 1

def clean_raw_data(df: pd.DataFrame) -> pd.DataFrame:
    """Функция для удаления мусорных/пустых строк"""

    # стрип строковых ячеек
    df = df.map(lambda x: x.strip() if isinstance(x, str) else x)

    # удаление полностью пустых строк
    df_cleaned = df.dropna(how='all')

    # удаление дублей по столбцам
    df_cleaned = df_cleaned.drop_duplicates(subset=['AvitoId', 'Id'])

    # подсчет количества удаленных строк
    removed = len(df) - len(df_cleaned)
    logging.info(f'Удалено мусорных/пустых строк: {removed}')

    return df_cleaned

def check_uniqueness(df: pd.DataFrame, column: str, skip_empty: bool) -> bool:
    """
    Функция проверки уникальности строк по столбцу.
    Если skip_empty=True — пропускает пустые значения (например, для AvitoId).
    Если skip_empty=False — считает все значения, включая пустые (например, для Id).
    Возвращает True, если всё ок.
    Возвращает False и логирует ошибку, если найдены дубликаты
    """

    if skip_empty:
        filled_ids = df[column].dropna()
    else:
        filled_ids = df[column]

    duplicated = filled_ids[filled_ids.duplicated()].unique()

    if len(duplicated) > 0:
        filename = f"duplicates_{column}_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.xlsx"
        df[df[column].isin(duplicated)].to_excel(filename, index=False)
        logging.error(f"Найдены дубликаты в '{column}' (всего: {len(duplicated)}). Сохранено в: {filename}")
        return False

    logging.info(f"Проверка '{column}' на уникальность успешно пройдена, дубликатов нет")
    return True

def normalize_group(group: pd.DataFrame, columns_to_normalize: list) -> pd.DataFrame:
    if group['AvitoDateEnd'].notna().any():
        idx = group['AvitoDateEnd'].idxmax()
    else:
        idx = group.index[0]
    ref_row = group.loc[idx, columns_to_normalize]
    for col in columns_to_normalize:
        group[col] = ref_row[col]
    return group

def normalize_group_by_latest(df: pd.DataFrame) -> pd.DataFrame:
    exclude_cols = ['AvitoStatus', 'AvitoDateEnd', 'Address']
    cols_to_normalize = [col for col in df.columns if col not in exclude_cols]
    df['AvitoDateEnd'] = pd.to_datetime(df['AvitoDateEnd'], errors='coerce', utc=True)
    normalized_df = df.groupby('Title', group_keys=False).apply(
        lambda group: normalize_group(group, cols_to_normalize)
    ).reset_index(drop=True)
    logging.info(f"Количество нормализованных строк по столбцу 'Title': {normalized_df.shape[0]}.")
    return normalized_df

def normalize_addresses(raw_address: str, id: str) -> str:
    """Функция для нормализации написания адресов в столбце Address"""
    for city, full_address in city_to_full_address.items():
        if re.search(fr"\b{re.escape(city)}\b", raw_address, re.IGNORECASE):
            return full_address
    unmatched_addresses.add((id, raw_address))
    return raw_address

def remove_invalid_dealerships(df: pd.DataFrame) -> pd.DataFrame:
    """
    Функция удаления строк, нарушающих дилерство по брендам и городам.
    Логирует AvitoId удалённых строк.
    """
    invalid_ids = []
    def is_allowed(row):
        brand = str(row['Make']).strip()
        address = str(row['Address']).strip()
        allowed_cities = dealerships.get(brand)
        if allowed_cities is None:
            return True
        for city in allowed_cities:
            if city.lower() in address.lower():
                return True
        invalid_ids.append(row['AvitoId'])
        return False
    result_df = df[df.apply(is_allowed, axis=1)]
    if invalid_ids:
        logging.warning(f"Удалены строки с нарушением дилерства: {len(invalid_ids)} шт.")
        invalid_list = [int(avito_id) for avito_id in invalid_ids]
        logging.warning(f"Список AvitoId удаленных строк:\n{invalid_list}")
    else:
        logging.info("Нарушений дилерства не обнаружено.")
    return result_df


def fill_missing_cities(df: pd.DataFrame, dealerships: dict) -> pd.DataFrame:
    """
    Проверка по каждой паре Title + Make: размещён ли товар во всех нужных городах.
    Если нет — добавляем недостающие строки.
    """
    global id_counter
    new_rows = []
    for (title, make), group in df.groupby(['Title', 'Make']):
        allowed_cities = dealerships.get(make, cities)
        source = "списка дилерства" if make in dealerships else "общего списка городов"
        existing_cities = set()
        for _, row in group.iterrows():
            if str(row['AvitoStatus']).strip().lower() != 'активно':
                continue
            address = str(row['Address'])
            for city in allowed_cities:
                if city.lower() in address.lower():
                    existing_cities.add(city)
                    break
        missing_cities = set(allowed_cities) - existing_cities
        if missing_cities:
            template_row = group.iloc[0].copy()
            for city in sorted(missing_cities):
                new_row = template_row.copy()
                new_row['Address'] = f"{city}"
                new_row['AvitoId'] = ''
                new_row['AvitoDateEnd'] = ''
                new_row['AvitoStatus'] = 'Активно'
                new_row['Id'] = f"{datetime.now().strftime('%d%m%Y')}{id_counter:06d}"
                id_counter += 1
                new_rows.append(new_row)
            logging.warning(f"Для товара '{title}' (бренд: {make}) из {source} добавлены строки в количестве {len(missing_cities)} шт.")
    if new_rows:
        df = pd.concat([df, pd.DataFrame(new_rows)], ignore_index=True)
        logging.info(f"Всего добавлено строк: {len(new_rows)}")
    else:
        logging.info("Все товары размещены в нужных городах. Новые строки не добавлялись.")
    return df