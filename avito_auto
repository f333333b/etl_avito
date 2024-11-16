import argparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from argparse import *

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("ids", type=str)
    return parser.parse_args()

def format_ids(ids):
    # text = input("Введите ID объявлений через запятую: ").split(',')
    link = 'https://www.avito.ru/items/'
    new_list = [link + i.strip() for i in ids.split(',')]
    return new_list

def open_and_click(ids):
    options = Options()
    options.add_argument("user-data-dir=C:/Users/user/AppData/Local/Google/Chrome/User Data")
    options.add_argument("profile-directory=Profile 1")
    options.add_argument("--headless")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    total = 0
    links = format_ids(args.ids)
    for url in links:
        driver.get(url)
        if "Вы удалили объявление" in driver.page_source or "Объявление заблокировано" in driver.page_source:
            print(f"Объявление на {url} удалено, переход к следующей ссылке.")
            continue
        try:
            link_button = driver.find_element(By.CSS_SELECTOR, "a[data-marker='activate-item-button']")
            link_button.click()
            if "Объявление опубликовано" in driver.page_source:
                total += 1
        except Exception as e:
            print(f"Не удалось нажать кнопку на странице {url}")
    print(f'Всего успешно опубликовано {total} объявлений!')
    driver.quit()

args = parse_args()
open_and_click(args)

# можно улучшить логирование при ошибках и пропусках объявлений
