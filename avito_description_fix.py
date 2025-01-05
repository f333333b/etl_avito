import re
import logging
#from bs4 import BeautifulSoup
import pandas as pd
(pd.set_option('display.max_columns', 3))

# функция обработки строк таблицы
def process_row(row, search_words, keywords, text_sample, end_text):
    title = row['Title']
    description = row['Description'].upper()
    vehicle_type = row['VehicleType']
    match_tech = re.search(search_words, description, re.IGNORECASE)  # поиск тех.характеристик
    tech_text = get_tech(match_tech, description)
    keywords_text = keywords.get(vehicle_type, '')
    result = f'<b>{title}</b><br />{text_sample}{tech_text}{end_text}{keywords_text}<br />'
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
        return f'<p><strong>Характеристики:</strong></p>{tech_result}'
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
input_file = input()
output_file = 'Copy of ' + input_file
table = pd.read_excel(input_file)
table.to_excel(output_file, engine='openpyxl', index=False)
result_list = []
table.apply(process_row, axis=1, args=(search_words, keywords, text_sample, end_text))
result_dict = {'Description': result_list}
result_df = pd.DataFrame(result_dict)
# # логирование
# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s - %(levelname)s - %(message)s",
#     handlers=[
#         logging.FileHandler("avito_description_fix_log.log"),  # Логи пишутся в файл
#         logging.StreamHandler()  # Логи выводятся в консоль
#     ]
# )
# tech_found = 0
# duplicates_removed = 0
# logging.info(f"Общее количество объявлений: {ids_amount}")
# logging.info(f"Обработано объявлений с характеристиками: {tech_found}")
# logging.info(f"Удалено дублирующих ключевых слов: {duplicates_removed}")

# запись данных в копию таблицы
with pd.ExcelWriter(output_file, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
    existing_df = pd.read_excel(output_file)
    existing_df['Description'] = result_df['Description']
    existing_df.to_excel(writer, index=False)

