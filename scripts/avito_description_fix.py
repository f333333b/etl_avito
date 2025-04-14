import re
from bs4 import BeautifulSoup
import os
import pandas as pd
(pd.set_option('display.max_columns', 3))

# функция для создания HTML-тега и добавления в BeautifulSoup
def create_tag(soup, tag_name='', text='', is_html=None):
    tag_to_add = soup.new_tag(tag_name)
    if text:
        if is_html:
            tag_to_add = BeautifulSoup(text, 'html.parser')
        else:
            tag_to_add.string = text
    soup.append(tag_to_add)

# функция обработки строк таблицы
def process_row(row, search_words, keywords, text_sample, end_text_part1, end_text_part2):
    title = row['Title']
    description = row['Description'].upper()
    vehicle_type = row['VehicleType']
    match_tech = re.search(search_words, description, re.IGNORECASE)  # поиск тех.характеристик
    tech_text = get_tech(match_tech, description)
    soup = BeautifulSoup('', 'html.parser')
    create_tag(soup, 'b', title)
    create_tag(soup, 'br')
    create_tag(soup, text=text_sample, is_html=True)
    if tech_text:
        create_tag(soup, 'p')
        create_tag(soup, 'strong', text='Характеристики:')
        create_tag(soup, text=tech_text, is_html=True)
    create_tag(soup, 'p', text=end_text_part1)
    create_tag(soup, 'p', text=end_text_part2)
    create_tag(soup, 'p', text=keywords.get(vehicle_type, ''))
    result = str(soup)
    result_list.append(result)

# функция обработки технических характеристик
def get_tech(match, description):
    if match:
        tech_index = match.end()
        tech = description[tech_index:].strip(':\"')
        # обрезка тех.характеристик до черты из знаков '='
        try:
            equals_index = tech.index('==')
            tech_result = tech[:equals_index].strip(':\"')
        except:
            tech_result = tech.strip(':')
        duplicates_removed_temp = 0
        # удаление дублирующей строки с ключ-словами (если есть)
        for value in keywords.values():
            if value.upper() in tech_result:
                duplicates_removed_temp += 1
                tech_result = tech_result.replace(value.upper(), '')
                print(tech_result)
        return tech_result
    return ''

# словарь для ключ-слов
keywords = {
    'Квадроциклы': 'квaдрoциклы квaдрoцикл квaдрик бензинoвый квaдрoцикл квaдрoцикл ATV',
    'Снегоходы': 'снегоход гусеничный снегоход лыжный снегоход снегоходная техника',
    'Мотоциклы': 'мотоциклы питбайк экдуро мотоцикл кроссовый мотоцикл мотобайк мото техника mоtо техника',
    'Мопеды и скутеры': 'мотоциклы питбайк экдуро мотоцикл кроссовый мотоцикл мотобайк мото техника moto техника скутер мопед',
    'Моторные лодки и моторы': 'лодочные моторы лодочный мотор мотор для лодки подвесной мотор для лодки плм лодочный двигатель для лодки'
}

# основной шаблон описания
with open('../avito_description_fix_sample_text.txt', 'r', encoding='utf-8') as file_sample_text:
    text_sample = file_sample_text.read()

# текст после технических характеристик
end_text_part1 = '''Не упустите возможность приобрести технику, которая станет вашим надежным помощником в любых условиях! Мы приглашаем посетить наш салон, где вы сможете ознакомиться с полным ассортиментом и получить профессиональную консультацию от наших специалистов'''
end_text_part2 = '''Готовы к новым приключениям? Свяжитесь с нами прямо сейчас и выберите свою идеальную мототехнику!'''

# регулярные выражения для поиска тех.характеристик
search_words = r"ТЕХНИЧЕСКИЕ ХАРАКТЕРИСТИКИ|ТEXНИЧECКИE XAPAКТEPИCТИКИ|ХАРАКТЕРИСТИКИ"

# основной код

# ввод имени файла с таблицей, создание копии файла
input_file = input("Введите имя файла с таблицей:")
output_file = 'Copy of ' + input_file
counter = 0
while os.path.isfile(output_file):
    counter += 1
    output_file = f"Copy of {os.path.splitext(input_file)[0]}_{counter}{os.path.splitext(input_file)[1]}"

# чтение файла, обработка таблицы, запись результатов в DataFrame переменную
table = pd.read_excel(input_file) # nrows=5
table.to_excel(output_file, engine='openpyxl', index=False)
result_list = []
table.apply(process_row, axis=1, args=(search_words, keywords, text_sample, end_text_part1, end_text_part2))
result_dict = {'Description': result_list}
result_df = pd.DataFrame(result_dict)

# запись данных в копию таблицы
with pd.ExcelWriter(output_file, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
    existing_df = pd.read_excel(output_file)
    existing_df['Description'] = result_df['Description']
    existing_df.to_excel(writer, index=False)