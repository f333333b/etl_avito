import pandas as pd

def main():
    table_path = r'C:/users/fgkh/Desktop/test.xlsx'
    df = pd.read_excel(table_path)
    sep_words = '<p>лодочные моторы'

    # условия фильтрации таблицы
    vehicle_type = df['VehicleType'] == 'Моторные лодки и моторы'

    # фильтрация таблицы
    filtered_items = df[vehicle_type]
    cell_list = list(zip(filtered_items['AvitoId'].tolist(), filtered_items['Description'].tolist(), filtered_items['Type'].tolist()))
    cell_total = len(cell_list)
    print(f'Всего объявлений для обработки: {cell_total}')
    for cell in cell_list:
        process_cell(df, sep_words, cell)
    df.to_excel(r'table_updated.xlsx', index=False)

def process_cell(df, sep_words, cell):
    '''Функция обработки ячейки Description'''
    separator = '-' * 40 + '<br>'
    key_words_boats = '''ЛОДКИ: MISHIMO/МИШИМО, SMARINE-X-MOTORS-EDITION/СМАРИН ЭДИШЕН, OMOLON/ОМОЛОН, GLADIATOR/ГЛАДИАТОР, ДРАККАР, SMARINE/СМАРИН, GLADIATOR/ГЛАДИАТОР, SEA-PRO/СИА ПРО, GLADIATOR-X-MOTORS-EDITION/ГЛАДИАТОР ЭДИШЕН, ROGER/РОГЕР, АДМИРАЛ, SOLAR/СОЛАР, SIBRIVER/СИБРИВЕР, РАКЕТА, РИВЬЕРА, ТАЙМЕНЬ, ФРЕГАТ, X-RIVER/ ИКСРИВЕР, REEF/РИФ, APACHE/АПАЧИ, PELICAN/ПЕЛИКАН'''
    key_words_engines = '''ЛОДОЧНЫЕ МОТОРЫ: MARLIN/МАРЛИН, PROMAX/ПРОМАКС, MARLIN PROLINE/МАРЛИН ПРОЛАЙН, BREEZE-YAMAHA/БРИЗ
ЯМАХА, CONDOR/КОНДОР, STELS/СТЕЛС, TAKATSU/ТАХАЦУ, GLADIATOR/ГЛАДИАТОР, YAMAHA/ЯМАХА, MERCURY/МЕРКУРИ, HONDA/ХОНДА, HANGKAI/ХАНГАЙ, HDX, HIDEA/ХИДЕА, SEA-PRO/СИАПРО, PARSUN/ПАРСУН, TOHATSU/ТОХАЦУ'''
    id, description, type = cell
    id = int(id) if pd.notna(id) else None
    s = df.loc[df['AvitoId'] == id, 'Description'].dropna().values
    print()
    s = s[0].split(sep_words) if s.size > 0 and isinstance(s[0], str) else []
    result = s + [separator] + [key_words_engines] if type == 'Лодочный мотор' else s + [separator] + [key_words_boats]
    result_str = ''.join(result)
    print()
    print(f'result_str={result_str}')
    df.loc[df['AvitoId'] == id, 'Description'] = result_str

if __name__ == "__main__":
    main()