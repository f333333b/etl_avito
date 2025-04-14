'''
Скрипт для замены ссылки на фото в строках с объявлениями Excel-таблицы
- открывает Excel-файл
- находит нужные строки по определенным условиям
- проверяет, является ли вторая ссылка на фото в столбце 'ImageUrls' баннером
- заменяет фото техники на картинку с баннером
'''

import pandas as pd
import requests
from PIL import Image
import pytesseract
from io import BytesIO
from urllib.parse import unquote
import time
from dotenv import load_dotenv
import os
import shutil
import argparse
from datetime import datetime

def find_tesseract_path():
    '''Функция нахождения пути к файлу tesseract.exe'''
    tesseract_path = shutil.which("tesseract")
    if tesseract_path:
        print(f"Tesseract найден по пути: {tesseract_path}")
    else:
        print("Tesseract не найден в PATH")
    return tesseract_path

def main():
    load_dotenv()
    tesseract_path = find_tesseract_path()
    BANNER_URL = os.getenv('BANNER_URL')
    if not BANNER_URL:
        print("BANNER_URL не задан в .env")
        exit(1)
    pytesseract.pytesseract.tesseract_cmd = tesseract_path
    banner_url = BANNER_URL

    # обработка аргументов
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    args = parser.parse_args()

    # формирование пути к файлу
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    input_path = os.path.join(desktop_path, args.input)

    # загрузка таблицы
    df = pd.read_excel(input_path)

    # текст, наличие которого проверяется в распознанном изображении
    text_to_detect_in_banner = 'MX280'

    #условия фильтрации таблицы
    price = df['Price'] < 200000
    type_cross_enduro = df['Type'].isin(['Кроссовый', 'Эндуро'])
    title_cross = df['Title'].str.lower().str.contains('кроссовый')

    filtered_items = df[price & (type_cross_enduro | title_cross)]
    id_and_photo = list(zip(filtered_items['ImageUrls'].str.split('|').apply(lambda x: x[2].strip()).tolist(), filtered_items['AvitoId'].tolist()))
    id_total = len(id_and_photo)

    print(f'Всего объявлений для обработки: {id_total}')
    ids_processed = collect_ids(df, banner_url, id_and_photo, text_to_detect_in_banner)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_file = os.path.join(desktop_path, f"file_updated_{timestamp}.xlsx")
    df.to_excel(output_file, index=False)
    print(f'ID объявлений, в которых заменено третье фото: {ids_processed}')
    print(f'Всего отредактировано {len(ids_processed)} объявлений')

def collect_ids(df, banner_url, id_and_photo, text_to_detect_in_banner):
    '''Функция поиска ID объявлений, в которых нужно изменить баннер'''
    ids_processed = []
    for item in id_and_photo:
        try:
            pic = unquote(item[0])
            print(item)
            if len(item) > 1:
                if not pd.isna(item[1]):
                    id = int(item[1])
                else:
                    id = 0
                    print(f'Нет ID объявления')
            response = requests.get(pic, timeout=10, allow_redirects=True)
            response.raise_for_status()
            if 'image' not in response.headers.get('Content-Type', ''):
                print(f"Не изображение: {pic}")
                continue
            img = Image.open(BytesIO(response.content))
            text = pytesseract.image_to_string(img)
            if text_to_detect_in_banner in text:
                print("Картинка - баннер со сравнениями. Пропуск.")
            else:
                ids_processed.append(process_id(df, banner_url, id))
                print(f"Картинка - фото, ID объявления: {id}.")
        except requests.exceptions.RequestException as e:
            print(f"Ошибка запроса для {pic}: {e}")
        except Exception as e:
            print(f"Ошибка обработки {pic}: {e}")
        time.sleep(2)
    return ids_processed

def process_id(df, banner_url, id):
    '''Функция замены третьего фото в столбце ImageUrls'''
    img_urls = df.loc[df['AvitoId'] == id, 'ImageUrls'].iloc[0].split('|')
    img_urls[2] = banner_url
    edited_img_urls = '|'.join(img_urls)
    #print(edited_img_urls)
    df.loc[df['AvitoId'] == id, 'ImageUrls'] = edited_img_urls
    print(f'Для объявления с ID {id} третье фото успешно заменено на баннер')
    return id

if __name__ == '__main__':
    main()