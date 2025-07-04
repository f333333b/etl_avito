from __future__ import annotations

import logging
import os
from contextlib import contextmanager
from datetime import datetime
from typing import Any, Dict, Optional

import pandas as pd
import requests
import yadisk

from etl.utils import ensure_dir_created

logger = logging.getLogger(__name__)


@contextmanager
def excel_writer(filename: str) -> None:
    """Функция - контекстный менеджер для записи Excel-файла"""
    try:
        yield filename
    except Exception as e:
        logger.error(f"Ошибка при записи файла {filename}: {e}")
        raise


# пробная версия кастомного контекстного менеджера с подсчетом времени работы
# class ExcelWriter:
#     def __init__(self, df: pd.DataFrame, filename: str, log: bool = True, **kwargs):
#         self.df = df
#         self.filename = filename
#         self.log = log
#         self.start_time = None
#         self.kwargs = kwargs
#
#     def __enter__(self):
#         if self.log:
#             logger.info(f"Начало записи: {self.filename}")
#         os.makedirs(os.path.dirname(self.filename), exist_ok=True)
#         self.start_time = time.perf_counter()
#         return self
#
#     def __exit__(self, exc_type, exc_val, exc_tb):
#         duration = time.perf_counter() - self.start_time
#         if exc_type:
#             logger.error(f"Ошибка при записи {self.filename}: {exc_val}")
#         else:
#             logger.info(
#                 f"Файл записан: {self.filename} "
#                 f"(строк: {len(self.df)}, время: {duration:.2f} сек)"
#             )
#         return False
#
#     def save(self):
#         self.df.to_excel(self.filename, index=False, **self.kwargs)


def load(df: pd.DataFrame, config: Dict) -> None:
    api_flag = str(config["API_FLAG"]).lower() == "true"
    if api_flag:
        autoload_api_main(df, config)
    else:
        save_dataframe(df, config)
    to_db(df)


def save_dataframe(df: pd.DataFrame, config: Dict) -> str:
    """Функция сохранения обработанного файла (Excel или CSV)"""
    df = df.copy()
    path = config["OUTPUT_PATH"]
    ext = os.path.splitext(path)[1].lower()
    folder = os.path.dirname(path)
    ensure_dir_created(folder)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    dir_name, file_name = os.path.split(path)
    name, ext = os.path.splitext(file_name)
    path = os.path.join(dir_name, f"{name}_{timestamp}{ext}")

    for col in df.select_dtypes(include=["datetimetz"]).columns:
        df[col] = df[col].dt.tz_localize(None)

    try:
        if ext in [".xlsx", ".xls"]:
            with excel_writer(path) as fname:
                df.to_excel(fname, index=False)
        elif ext == ".csv":
            df.to_csv(path, index=False, encoding="utf-8-sig")
        else:
            raise ValueError(f"Неподдерживаемое расширение файла: {ext}")

        logger.info(f"Файл успешно сохранён: {path}")
    except PermissionError as e:
        logger.error(f"Не удалось записать файл {path}: {e}")
        raise

    file_size = os.path.getsize(path)
    logger.info(f"Размер файла: {file_size / (1024 ** 2):.2f} МБ. Количество строк: {len(df)}")

    return path


def autoload_api_main(df: pd.DataFrame, config: Dict) -> None:
    email = config["EMAIL"]
    yandex_token = config["YANDEX_TOKEN"]
    token = get_token(config)
    saved_file = save_dataframe(df, config)
    public_url = yandex_upload(saved_file, yandex_token)
    update_avito_autoload_profile(
        access_token=token,
        upload_url=public_url,
        report_email=email,
        schedule=[],
        agreement=True,
        autoload_enabled=False,
    )


def get_token(config: Dict) -> str:
    client_id = config["CLIENT_ID"]
    client_secret = config["CLIENT_SECRET"]
    url = "https://api.avito.ru/token/"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
    }

    try:
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()
        result = response.json().get("access_token")
        return result
    except requests.RequestException as e:
        logger.error(f"Не удалось получить токен: {e}")
        logger.info(f"{response.text}")
        return ""


def yandex_upload(saved_file: str, yandex_token: str) -> str:
    y = yadisk.YaDisk(token=yandex_token)
    today_str = datetime.now().strftime("%Y-%m-%d")
    remote_path = f"/autoupload/{today_str}.xlsx"
    y.upload(saved_file, remote_path, overwrite=True)
    if not y.is_public(remote_path):
        y.publish(remote_path)
    return y.get_public_url(remote_path)


def update_avito_autoload_profile(
    access_token: str,
    upload_url: str,
    report_email: str,
    schedule: Optional[list[dict[str, Any]]] = None,
    agreement: bool = True,
    autoload_enabled: bool = True,
) -> requests.Response:
    """Функция обновления профиля автозагрузки в Авито"""

    if schedule is None:
        schedule = [{"rate": 100000, "time_slots": [9, 10], "weekdays": [0, 1, 2, 3, 4]}]
    url = "https://api.avito.ru/autoload/v1/profile"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    payload = {
        "agreement": agreement,
        "autoload_enabled": autoload_enabled,
        "report_email": report_email,
        "schedule": schedule,
        "upload_url": upload_url,
    }
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        logger.info("Профиль автозагрузки успешно обновлен")
    else:
        logger.error(f"Ошибка при обновлении профиля: {response.status_code}, {response.text}")
    return response

def to_db(df: pd.DataFrame) -> None:
    """Функция создания реляционной БД из DataFrame"""

    engine = create_engine("postgresql+psycopg2://airflow:airflow@postgres/airflow")
    df.to_sql(
        name="avito_table",
        con=engine,
        if_exists="replace",
        index=False
    )