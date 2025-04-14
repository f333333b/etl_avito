"""
Скрипт обрабатывает Excel-файл с объявлениями Avito:
- Извлекает технические характеристики из описания
- Формирует HTML-описание на основе шаблона
- Записывает результат в копию исходного файла
"""

import re
from bs4 import BeautifulSoup
import os
import pandas as pd
import argparse

KEYWORDS = {
    'Квадроциклы': 'квaдрoциклы квaдрoцикл квaдрик бензинoвый квaдрoцикл квaдрoцикл ATV',
    'Снегоходы': 'снегоход гусеничный снегоход лыжный снегоход снегоходная техника',
    'Мотоциклы': 'мотоциклы питбайк экдуро мотоцикл кроссовый мотоцикл мотобайк мото техника mоtо техника',
    'Мопеды и скутеры': 'мотоциклы питбайк экдуро мотоцикл кроссовый мотоцикл мотобайк мото техника moto техника скутер мопед',
    'Моторные лодки и моторы': 'лодочные моторы лодочный мотор мотор для лодки подвесной мотор для лодки плм лодочный двигатель для лодки'
}

SEARCH_REGEX = r"ТЕХНИЧЕСКИЕ ХАРАКТЕРИСТИКИ|ТEXНИЧECКИE XAPAКТEPИCТИКИ|ХАРАКТЕРИСТИКИ"

TEXT_PART_1 = ("Не упустите возможность приобрести технику, которая станет вашим надежным помощником в любых условиях! "
               "Мы приглашаем посетить наш салон, где вы сможете ознакомиться с полным ассортиментом и получить профессиональную консультацию от наших специалистов")
TEXT_PART_2 = "Готовы к новым приключениям? Свяжитесь с нами прямо сейчас и выберите свою идеальную мототехнику!"


def load_template(path='template.txt'):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def create_tag(soup, tag_name='', text='', is_html=None):
    if text:
        tag_to_add = BeautifulSoup(text, 'html.parser') if is_html else soup.new_tag(tag_name)
        if not is_html:
            tag_to_add.string = text
        soup.append(tag_to_add)

def extract_tech(match, description):
    if not match:
        return ''
    tech_text = description[match.end():].strip(':"')
    try:
        tech_text = tech_text[:tech_text.index('==')].strip()
    except ValueError:
        tech_text = tech_text.strip()
    for value in KEYWORDS.values():
        tech_text = tech_text.replace(value.upper(), '')
    return tech_text

def generate_html(row, text_sample):
    description = row['Description'].upper()
    match = re.search(SEARCH_REGEX, description, re.IGNORECASE)
    tech_text = extract_tech(match, description)
    soup = BeautifulSoup('', 'html.parser')
    create_tag(soup, 'b', row['Title'])
    create_tag(soup, 'br')
    create_tag(soup, text=text_sample, is_html=True)
    if tech_text:
        create_tag(soup, 'p')
        create_tag(soup, 'strong', text='Характеристики:')
        create_tag(soup, text=tech_text, is_html=True)
    create_tag(soup, 'p', text=TEXT_PART_1)
    create_tag(soup, 'p', text=TEXT_PART_2)
    create_tag(soup, 'p', text=KEYWORDS.get(row['VehicleType'], ''))
    return str(soup)

def generate_copy_name(input_file):
    base, ext = os.path.splitext(input_file)
    counter = 0
    output_file = f"Copy of {base}{ext}"
    while os.path.exists(output_file):
        counter += 1
        output_file = f"Copy of {base}_{counter}{ext}"
    return output_file

def process_excel(input_file, template_path='template.txt'):
    output_file = generate_copy_name(input_file)
    df = pd.read_excel(input_file)
    sample_text = load_template(template_path)
    df['Description'] = df.apply(lambda row: generate_html(row, sample_text), axis=1)
    df.to_excel(output_file, engine='openpyxl', index=False)
    print(f"Готово. Результат сохранен в: {output_file}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Редактирование описаний Avito.')
    parser.add_argument('--input', required=True, help='Путь к Excel-файлу объявлений')
    parser.add_argument('--template', default='template_text.txt', help='Путь к HTML-шаблону')
    args = parser.parse_args()
    process_excel(args.input, args.template)
