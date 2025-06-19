import os
import logging
import pandas as pd
import requests
from dotenv import load_dotenv
import json
import argparse
from main import client_id, client_secret

def save_to_excel(df: pd.DataFrame, path: str) -> None:
    df = df.copy()
    folder = os.path.dirname(path)
    if folder and not os.path.isdir(folder):
        logging.error(f"Папка не существует: {folder}")
        raise FileNotFoundError(f"Папка не существует: {folder}")
    for col in df.select_dtypes(include=["datetimetz"]).columns:
        df[col] = df[col].dt.tz_localize(None)
    df.to_excel(path, index=False)

def api_autoload(df: pd.DataFrame) -> None:
    ...

def main():
    token = get_token()
    #parser = argparse.ArgumentParser(description="Avito API утилита")
    #parser.add_argument('--action', choices=['get_balance', 'get_info', 'update_price', 'get_tarif'], required=True, help='Какое действие выполнить')
    #parser.add_argument('--ids', help='Список ID через запятую (для update_price или get_info)')
    #parser.add_argument('--price', type=int, help='Новая цена (для update_price)')
    #args = parser.parse_args()

def get_token() -> str:
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
        print(f"[ERROR] Не удалось получить токен: {e}")
        print(response.text)
        return ""