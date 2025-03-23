import pandas as pd
import requests
from PIL import Image
import pytesseract
from io import BytesIO
from urllib.parse import unquote
import time
from dotenv import load_dotenv
import os

def main():
    load_dotenv()
    TESSERACT_PATH = os.getenv('TESSERACT_PATH')
    BANNER_URL = os.getenv('BANNER_URL')
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
    banner_url = BANNER_URL
    df = pd.read_excel(r'table.xlsx')

    #условия фильтрации таблицы
    price = df['Price'] < 200000
    type_cross_enduro = df['Type'].isin(['Кроссовый', 'Эндуро'])
    title_cross = df['Title'].str.lower().str.contains('кроссовый')

    filtered_items = df[price & (type_cross_enduro | title_cross)]
    id_and_photo = list(zip(filtered_items['ImageUrls'].str.split('|').apply(lambda x: x[2].strip()).tolist(), filtered_items['AvitoId'].tolist()))
    id_total = len(id_and_photo)

    print(f'Всего объявлений для обработки: {id_total}')
    total_ids_processed = collect_ids(df, banner_url, id_and_photo)
    print(f'Всего объявлений, в которых заменено третье фото: {total_ids_processed}')
    df.to_excel(r'table_updated.xlsx', index=False)

def collect_ids(df, banner_url, id_and_photo):
    '''Функция поиска ID объявлений, в которых нужно изменить баннер'''
    total_ids_processed = 0
    for item in id_and_photo:
        try:
            pic = unquote(item[0])
            id = int(item[1])
            print(f"Обработка: {repr(pic)}")
            response = requests.get(pic, timeout=10, allow_redirects=True)
            response.raise_for_status()
            if 'image' not in response.headers.get('Content-Type', ''):
                print(f"Не изображение: {pic}")
                continue
            img = Image.open(BytesIO(response.content))
            text = pytesseract.image_to_string(img)
            if 'MX280' in text:
                print("Картинка - баннер со сравнениями. Пропуск.")
            else:
                total_ids_processed += process_id(df, banner_url, id)
                print(f"Картинка - фото, ID объявления: {id}.")
        except requests.exceptions.RequestException as e:
            print(f"Ошибка запроса для {pic}: {e}")
        except Exception as e:
            print(f"Ошибка обработки {pic}: {e}")
        time.sleep(3)
    return total_ids_processed

def process_id(df, banner_url, id):
    '''Функция замены третьего фото в столбце ImageUrls'''
    img_urls = df.loc[df['AvitoId'] == id, 'ImageUrls'].iloc[0].split('|')
    img_urls[2] = banner_url
    edited_img_urls = '|'.join(img_urls)
    #print(edited_img_urls)
    df.loc[df['AvitoId'] == id, 'ImageUrls'] = edited_img_urls
    print(f'Для объявления с ID {id} третье фото успешно заменено на баннер')
    return 1

if __name__ == '__main__':
    main()