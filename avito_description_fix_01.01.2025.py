import re
import logging
from openpyxl import load_workbook
import pandas as pd
(pd.set_option('display.max_columns', 3))

def get_tech(match, tech_found, duplicates_removed): # функция для обработки тех. характеристик
    if match:  # поиск и добавление тех.характеристик
        tech_found_temp = 1
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
        return [f'<p><strong>Характеристики:</strong></p>{tech_result}', tech_found_temp, duplicates_removed_temp]
    return ['', 0, 0]

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

# текст после тех.характеристик
end_text = '''<p>Не упустите возможность приобрести технику, которая станет вашим надежным помощником в любых условиях! Мы приглашаем посетить наш салон, где вы сможете ознакомиться с полным ассортиментом и получить профессиональную консультацию от наших специалистов.</p>
<p>Готовы к новым приключениям? Свяжитесь с нами прямо сейчас и выберите свою идеальную мототехнику!</p>
<p>&nbsp;</p>'''

# основной код
table = pd.read_excel('186615585_2024-12-30T13_47_01Z.xlsx') # чтение excel-файла (аргумент nrows=500)
selected_columns = ['Title', 'Description', 'VehicleType'] # выбор нужных колонок в таблице
table = table[selected_columns] # отфильтрованная таблица с нужными столбцами
ids_amount = table.shape[0] # переменная с количеством объявлений
search_words = r"ТЕХНИЧЕСКИЕ ХАРАКТЕРИСТИКИ|ТEXНИЧECКИE XAPAКТEPИCТИКИ|ХАРАКТЕРИСТИКИ" # регулярные выражения для поиска тех.характеристик
#stats = {'tech_found': 0, 'duplicates_removed': 0}

# логирование
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("avito_description_fix_log.log"),  # Логи пишутся в файл
        logging.StreamHandler()  # Логи выводятся в консоль
    ]
)
tech_found = 0
duplicates_removed = 0
result_list = []
for i in range(ids_amount):
    title = table.loc[i, 'Title'] # название техники
    description = table.loc[i, 'Description'].upper() # описание
    vehicle_type = table.loc[i, 'VehicleType'] # вид техники
    match_tech = re.search(search_words, description, re.IGNORECASE) # поиск тех.характеристик
    get_tech_result = get_tech(match_tech, tech_found, duplicates_removed)
    tech_text = get_tech_result[0]
    tech_found += get_tech_result[1]
    duplicates_removed += get_tech_result[2]
    keywords_text = keywords[vehicle_type]
    result = '<b>{title}</b><br />{text_sample}{tech_text}{end_text}{keywords_text}<br />'.format(
        title=title, text_sample=text_sample, tech_text=tech_text, end_text=end_text, keywords_text=keywords_text)
    result_list.append(result)

logging.info(f"Общее количество объявлений: {ids_amount}")
logging.info(f"Обработано объявлений с характеристиками: {tech_found}")
logging.info(f"Удалено дублирующих ключевых слов: {duplicates_removed}")

result_dict = {'Description': result_list}
result_df = pd.DataFrame(result_dict)

# запись данных в копию таблицы
with pd.ExcelWriter('186615585_2024-12-30T13_47_01Z — копия.xlsx', engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
    existing_df = pd.read_excel('186615585_2024-12-30T13_47_01Z — копия.xlsx', sheet_name='Объявления')
    existing_df['Description'] = result_df['Description']
    existing_df.to_excel(writer, sheet_name='Объявления', index=False)

