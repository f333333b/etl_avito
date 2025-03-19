import argparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("ids", type=str)
    return parser.parse_args()

def format_ids(ids):
    link = 'https://www.avito.ru/items/'
    new_list = [link + i.strip() for i in ids.split(',')]
    return new_list

def open_and_click(ids):
    options = Options()
    options.add_argument("user-data-dir=C:/Users/user/AppData/Local/Google/Chrome/User Data")
    options.add_argument("profile-directory=Profile 1")
    #options.add_argument("--headless")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    total = 0
    links = format_ids(args)
    for url in links:
        #time.sleep(1)
        driver.get(url)
        if "Вы удалили объявление" in driver.page_source or "Объявление заблокировано" in driver.page_source:
            print(f"Объявление на {url} удалено, переход к следующей ссылке")
        elif "Статистика за неделю" in driver.page_source:
            print(f"Объявление на {url} уже активно, переход к следующей ссылке")
        else:
            try:
                link_button = driver.find_element(By.CSS_SELECTOR, 'a[data-marker="activate-item-button"]')
                link_button.click()
                time.sleep(1)
                if "Расширьте географию показа" in driver.page_source:
                    try:
                        time.sleep(1)
                        link_button_activate = driver.find_element(By.CSS_SELECTOR, 'button[data-marker="submit-button"]')
                        link_button_activate.click()
                        if "Объявление опубликовано" in driver.page_source or "Объявление скоро станет активным" in driver.page_source:
                            print(f"Кнопка 'Активировать' удачно нажата, объявление {url} успешно активировано")
                            total += 1
                        else:
                            print(f"После нажатия кнопки 'Активировать' не удалось получить информацию об удачной активации объявления {url}")
                    except:
                        print(f"Не удалось нажать кнопку 'Активировать' на странице {url}")
                elif "Объявление опубликовано" in driver.page_source:
                    print(f"Объявление {url} успешно активировано без нажатия кнопки 'Активировать'")
                    total += 1
                else:
                    print(f'Ключевая фраза "Расширьте географию показа" не найдена на странице для объявления {url}')
            except:
                print(f"Не удалось нажать кнопку 'Опубликовать' на странице {url}")
    print(f'Всего успешно опубликовано {total} объявлений!')

with open('input_05.03.2025.txt', 'r') as file:
    args = file.read()
open_and_click(args)
time.sleep(30)
