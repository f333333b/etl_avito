import os
import requests
from dotenv import load_dotenv
import json

load_dotenv()

client_id = os.getenv('CLIENT_ID')
client_secret = os.getenv('CLIENT_SECRET')
user_id = os.getenv('USER_ID')

def get_token():
    url = "https://api.avito.ru/token/"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret
    }

    response = requests.post(url, headers=headers, data=data)
    return response.json().get("access_token")

def update_price(token, item_ids: list, new_price: int):
    """Функция обновления цены объявлений по списку ID"""
    for item_id in item_ids:
        updated_price_url = f"https://api.avito.ru/core/v1/items/{int(item_id)}/update_price"

        headers = {
            "grant_type": "client_credentials",
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        data = {
            "price": new_price
        }

        update_price_response = requests.post(updated_price_url, headers=headers, json=data)
        update_price_data = update_price_response.json()
        print(json.dumps(update_price_data, indent=4))

def get_info(token, item_id):
    """Функция получения информации по объявлению"""
    get_info_url = f'https://api.avito.ru/core/v1/accounts/{user_id}/items/{item_id}/'
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    get_info_response = requests.get(get_info_url, headers=headers)
    get_info_data = get_info_response.json()
    return json.dumps(get_info_data, indent=4)

def tarif_info():
    """Функция для получения информации по тарифу пользователя"""
    tarif_info_url = f'https://api.avito.ru/tariff/info/1'
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    tarif_info_response = requests.get(tarif_info_url, headers=headers)
    tarif_info_data = tarif_info_response.json()

    # проверяет тариф активен
    #is_active = tarif_info_data.get("current", 0).get("isActive", 0)
    all_info = json.dumps(tarif_info_data, indent=4)
    return all_info

def get_balance():
    """Функция для проверки баланса пользователя"""
    balance_url = f'https://api.avito.ru/core/v1/accounts/{user_id}/balance/'
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    balance_response = requests.get(balance_url, headers=headers)
    balance_data = balance_response.json()
    return balance_data

# вызов функций
token = get_token()

print(get_balance())
#update_price_id_list = []
#new_price = 123
#update_price(token, item_ids=update_price_id_list, new_price=new_price)