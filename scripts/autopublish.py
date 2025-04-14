'''Скрипт для опубликования неактивных объявлений на Avito через Selenium'''

import argparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
from pathlib import Path
import os

def find_chrome_windows():
    '''Функция для нахождения пути к файлу chrome.exe'''
    for var in ["%LocalAppData%", "%ProgramFiles%", "%ProgramFiles(x86)%"]:
        path = os.path.expandvars(f"{var}\\Google\\Chrome\\Application\\chrome.exe")
        if Path(path).exists():
            return path
    return None

def parse_args() -> str:
    '''Функция обработки аргументов командной строки'''
    parser = argparse.ArgumentParser()
    parser.add_argument("ids", type=str)
    return parser.parse_args()

def format_ids(ids: list) -> list:
    '''Функция формирования списка с URL объявлений по их ID'''
    link = 'https://www.avito.ru/items/'
    return [link + i.strip() for i in ids.split(',')]

def open_and_click(ids: list):
    '''Функция выполнения активации объявлений'''
    chrome_path = find_chrome_windows()
    print(chrome_path)
    if not chrome_path:
        raise RuntimeError("Chrome не найден")

    options = Options()
    options.binary_location = chrome_path
    options.add_argument("user-data-dir=C:/Users/user/AppData/Local/Google/Chrome/User Data")
    options.add_argument("profile-directory=Profile 1")
    # options.add_argument("--headless")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    total = 0
    links = format_ids(ids)

    for url in links:
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
    driver.quit()

def main():
    args = parse_args()
    with open(args.ids, 'r', encoding='utf-8') as file:
        raw_ids = file.read()
    open_and_click(raw_ids)
    input("Нажмите Enter для выхода...")

if __name__ == "__main__":
    main()