import os
import logging
import pandas as pd
import requests
import yadisk
from datetime import datetime

from etl.config import YANDEX_TOKEN, EMAIL

def load(df: pd.DataFrame, output_path: str, api_flag=False) -> None:
    if api_flag:
        autoload_api_main(df, output_path)
    else:
        save_to_excel(df, output_path)

def save_to_excel(df: pd.DataFrame, path: str) -> str:
    df = df.copy()
    folder = os.path.dirname(path)
    if folder and not os.path.isdir(folder):
        logging.error(f"Папка не существует: {folder}")
        raise FileNotFoundError(f"Папка не существует: {folder}")
    for col in df.select_dtypes(include=["datetimetz"]).columns:
        df[col] = df[col].dt.tz_localize(None)
    df.to_excel(path, index=False)
    logging.info(f"Excel-файл сохранён: {path}")
    return path

def autoload_api_main(df: pd.DataFrame, path: str) -> None:
    token = get_token()
    saved_file = save_to_excel(df, path)
    public_url = yandex_upload(saved_file)
    update_avito_autoload_profile(
    access_token=token,
    upload_url=public_url,
    report_email=EMAIL,
    schedule=None,
    agreement=True,
    autoload_enabled=False
    )

def get_token(client_id, client_secret) -> str:
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


def yandex_upload(saved_file: str) -> str:
    y = yadisk.YaDisk(token=YANDEX_TOKEN)
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
    """
    Функция обновления профиля автозагрузки в Авито.
    access_token: OAuth2 токен с правами на autoload
    upload_url: Прямая ссылка на фид-файл (XML/CSV)
    report_email: Почта для получения отчётов
    schedule: Список расписаний, например: [{"start_hour": 9, "end_hour": 10, "limit": 1000}]
    agreement: Согласие с правилами (обязательно при первом создании)
    autoload_enabled: Вкл/выкл автозагрузку
    """
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