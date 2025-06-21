import os
import logging
import pandas as pd
import requests
import yadisk
from datetime import datetime
from typing import Dict

from contextlib import contextmanager

logger = logging.getLogger(__name__)

@contextmanager
def excel_writer(filename: str):
    """Функция - контекстный менеджер для записи Excel-файла"""
    try:
        yield filename
    except Exception as e:
        logger.error(f"Ошибка при записи файла {filename}: {e}")
        raise

def load(df: pd.DataFrame, config: Dict) -> None:
    api_flag = str(config['API_FLAG']).lower() == "true"
    if api_flag:
        autoload_api_main(df, config)
    else:
        save_to_excel(df, config)


def save_to_excel(df: pd.DataFrame, config: Dict) -> str:
    df = df.copy()
    path = config['OUTPUT_PATH']
    folder = os.path.dirname(path)

    if folder and not os.path.isdir(folder):
        logging.error(f"Папка не существует: {folder}")
        raise FileNotFoundError(f"Папка не существует: {folder}")
    for col in df.select_dtypes(include=["datetimetz"]).columns:
        df[col] = df[col].dt.tz_localize(None)
    with excel_writer(path) as fname:
        df.to_excel(fname, index=False)
        logging.info(f"Excel-файл сохранён: {fname}")
    return path

def autoload_api_main(df: pd.DataFrame, config: Dict) -> None:
    email = config['EMAIL']
    yandex_token = config['YANDEX_TOKEN']
    token = get_token(config)
    saved_file = save_to_excel(df, config)
    public_url = yandex_upload(saved_file, yandex_token)
    update_avito_autoload_profile(
    access_token=token,
    upload_url=public_url,
    report_email=email,
    schedule=None,
    agreement=True,
    autoload_enabled=False
    )

def get_token(config: Dict) -> str:
    client_id = config['CLIENT_ID']
    client_secret = config['CLIENT_SECRET']
    url = "https://api.avito.ru/token/"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret
    }

    try:
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()
        result = response.json().get("access_token")
        return result
    except requests.RequestException as e:
        logging.error(f"Не удалось получить токен: {e}")
        logging.info(f'{response.text}')
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
    schedule: list = None,
    agreement: bool = True,
    autoload_enabled: bool = True
):
    """Функция обновления профиля автозагрузки в Авито"""
    if schedule is None:
        schedule = [
            {
                "rate": 100000,
                "time_slots": [9, 10],
                "weekdays": [0, 1, 2, 3, 4]
            }
        ]
    url = "https://api.avito.ru/autoload/v1/profile"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    payload = {
        "agreement": agreement,
        "autoload_enabled": autoload_enabled,
        "report_email": report_email,
        "schedule": schedule,
        "upload_url": upload_url
    }
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        logging.info("Профиль автозагрузки успешно обновлен")
    else:
        logging.error(f"Ошибка при обновлении профиля: {response.status_code}, {response.text}")
    return response