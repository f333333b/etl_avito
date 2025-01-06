import re
from bs4 import BeautifulSoup as bs
import os
import pandas as pd
(pd.set_option('display.max_columns', 3))

# функция обработки строк таблицы
def process_row(row, search_words, keywords, text_sample, end_text):
    title = row['Title']
    description = row['Description'].upper()
    vehicle_type = row['VehicleType']
    match_tech = re.search(search_words, description, re.IGNORECASE)  # поиск тех.характеристик
    tech_text = get_tech(match_tech, description)
    soup = bs('', 'html.parser')
    bold_tag = soup.new_tag('b')
    bold_tag.string = title
    soup.append(bold_tag)
    br_tag = soup.new_tag('br')  # Создание тега <br />
    soup.append(br_tag)
    soup.append(bs(text_sample, 'html.parser'))
    if tech_text:
        p_tag = soup.new_tag('p')
        strong_tag = soup.new_tag('strong')
        strong_tag.string = "Характеристики:"
        p_tag.append(strong_tag)
        tech_text_soup = bs(tech_text, 'html.parser')
        p_tag.append(tech_text_soup)
        soup.append(p_tag)
    soup.append(bs(end_text, 'html.parser'))
    keywords_tag = soup.new_tag('p')
    keywords_tag.string = keywords.get(vehicle_type, '')
    soup.append(keywords_tag)
    result = str(soup)
    result_list.append(result)

# функция обработки технических характеристик
def get_tech(match, description):
    if match:
        tech_index = match.end()
        tech = description[tech_index:].strip(':\"')
        try:
            equals_index = tech.index('==')  # обрезка тех.характеристик до черты из знаков '='
            tech_result = tech[:equals_index].strip(':\"')
        except:
            tech_result = tech.strip(':')
        duplicates_removed_temp = 0
        for value in keywords.values():  # удаление дублирующей строки с ключ-словами (если есть)
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
with open('avito_description_fix_sample_text.txt', 'r', encoding='utf-8') as file_sample_text:
    text_sample = file_sample_text.read()

# текст после технических характеристик
end_text = '''<p>Не упустите возможность приобрести технику, которая станет вашим надежным помощником в любых условиях! Мы приглашаем посетить наш салон, где вы сможете ознакомиться с полным ассортиментом и получить профессиональную консультацию от наших специалистов.</p>
<p>Готовы к новым приключениям? Свяжитесь с нами прямо сейчас и выберите свою идеальную мототехнику!</p>
<p>&nbsp;</p>'''

# регулярные выражения для поиска тех.характеристик
search_words = r"ТЕХНИЧЕСКИЕ ХАРАКТЕРИСТИКИ|ТEXНИЧECКИE XAPAКТEPИCТИКИ|ХАРАКТЕРИСТИКИ"

# основной код
input_file = input("Введите имя файла с таблицей:")
output_file = 'Copy of ' + input_file
counter = 0
while os.path.isfile(output_file):
    counter += 1
    output_file = f"Copy of {os.path.splitext(input_file)[0]}_{counter}{os.path.splitext(input_file)[1]}"

table = pd.read_excel(input_file, nrows=5)
table.to_excel(output_file, engine='openpyxl', index=False)
result_list = []
table.apply(process_row, axis=1, args=(search_words, keywords, text_sample, end_text))
result_dict = {'Description': result_list}
result_df = pd.DataFrame(result_dict)

# запись данных в копию таблицы
with pd.ExcelWriter(output_file, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
    existing_df = pd.read_excel(output_file)
    existing_df['Description'] = result_df['Description']
    existing_df.to_excel(writer, index=False)