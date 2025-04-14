'''Набор функций для выполнения запросов к API Avito'''

import os
import requests
from dotenv import load_dotenv
import json
import argparse
from datetime import datetime

load_dotenv()
client_id = os.getenv('CLIENT_ID')
client_secret = os.getenv('CLIENT_SECRET')
user_id = os.getenv('USER_ID')

def main():
    token = get_token()
    parser = argparse.ArgumentParser(description="Avito API утилита")
    parser.add_argument('--action', choices=['get_balance', 'get_info', 'update_price', 'get_tarif'], required=True, help='Какое действие выполнить')
    parser.add_argument('--ids', help='Список ID через запятую (для update_price или get_info)')
    parser.add_argument('--price', type=int, help='Новая цена (для update_price)')
    args = parser.parse_args()
    if args.action == 'get_balance':
        result = get_balance(token)
        print(pretty_json(result))
    elif args.action == 'get_info':
        if not args.ids:
            print("[ERROR] Не передан --ids для get_info")
            return
        for item_id in args.ids.split(','):
            print(pretty_json(get_info(token, item_id)))
    elif args.action == 'update_price':
        if not args.ids or args.price is None:
            print("[ERROR] Требуются --ids и --price для update_price")
            return
        item_ids = args.ids.split(',')
        results = get_update_price(token, item_ids, args.price)
        print(pretty_json({"results": results}))
    elif args.action == 'get_tarif':
        tarif_info = get_tarif_info(token)
        tarif_info = format_tarif_times(tarif_info)
        print(pretty_json(tarif_info))

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

def get_info(token, item_id):
    url = f'https://api.avito.ru/core/v1/accounts/{user_id}/items/{item_id}/'
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"[ERROR] Ошибка при получении информации по ID {item_id}: {e}")
        return {}

def get_update_price(token: str, item_ids: list, new_price: int) -> list[dict]:
    """Обновление цен по списку ID"""
    results = []
    for item_id in item_ids:
        url = f"https://api.avito.ru/core/v1/items/{int(item_id)}/update_price"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        data = {"price": new_price}

        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            result_data = response.json()
            results.append(result_data)
        except Exception as e:
            print(f"[ERROR] Не удалось обновить цену для ID {item_id}: {e}")
            if response is not None:
                print(response.text)
            results.append({"id": item_id, "error": str(e)})
    return results

def get_tarif_info(token: str) -> dict:
    """Информация о тарифе"""
    url = 'https://api.avito.ru/tariff/info/1'
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"[ERROR] Ошибка при получении тарифа: {e}")
        return {}

def get_balance(token: str) -> dict:
    """Проверка баланса"""
    url = f'https://api.avito.ru/core/v1/accounts/{user_id}/balance/'
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"[ERROR] Ошибка при получении баланса: {e}")
        return {}

def format_tarif_times(data: dict) -> dict:
    """Преобразует timestamp в читаемые даты"""
    for section in ["current", "scheduled"]:
        if section in data:
            for time_key in ["startTime", "closeTime"]:
                ts = data[section].get(time_key)
                if isinstance(ts, int):
                    formatted = datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")
                    data[section][f"{time_key}_readable"] = formatted
    return data

def pretty_json(data: dict) -> str:
    """Форматированный JSON-вывод"""
    return json.dumps(data, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    main()