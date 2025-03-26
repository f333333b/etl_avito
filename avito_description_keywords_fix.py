import pandas as pd

def main():
    table_path = r'table.xlsx'
    df = pd.read_excel(table_path)
    total_processed = 0
    key_dict = {
        'full': (
            "<p><strong>Лодочные моторы: PROMAX, MARLIN PROLINE, TOYAMA(PARSUN).</strong></p> "
            "<p><strong>Надувные лодки: MISHIMO, Драккар, Аква, Sibriver, Gladiator, SMARINE.</strong></p> "
            "<p><strong>Квадроциклы: GBM, PROMAX, FAIDET.</strong></p> "
            "<p><strong>Мотоциклы: PROMAX, FRATELI, FAIDET, X-MOTORS.</strong></p> "
            "<p><strong>Снегоходы: PROMAX, IKUDZO, IRBIS, AODES, РМ, STELS.</strong></p> "
            "<p><strong>Мотобуксировщики: IKUDZO, PROMAX, OPTI MAX, SNOW DOG, IRBIS, SNOWBEAR, "
            "БУРЛАК, МУЖИК</strong></p>"
        ),
        'Моторные лодки и моторы': (
            "<p><strong>Лодочные моторы: PROMAX, MARLIN PROLINE, TOYAMA(PARSUN).</strong></p> "
            "<p><strong>Надувные лодки: MISHIMO, Драккар, Аква, Sibriver, Gladiator, SMARINE.</strong></p> "
        ),
        'Квадроциклы': (
            "<p><strong>Квадроциклы: GBM, PROMAX, FAIDET.</strong></p> "
        ),
        'Мопеды и скутеры': (
            "<p><strong>Мотоциклы: PROMAX, FRATELI, FAIDET, X-MOTORS.</strong></p> "
        ),
        'Мотоциклы': (
            "<p><strong>Мотоциклы: PROMAX, FRATELI, FAIDET, X-MOTORS.</strong></p> "
        ),
        'Снегоходы': (
            "<p><strong>Снегоходы: PROMAX, IKUDZO, IRBIS, AODES, РМ, STELS.</strong></p> "
            "<p><strong>Мотобуксировщики: IKUDZO, PROMAX, OPTI MAX, SNOW DOG, IRBIS, SNOWBEAR, "
            "БУРЛАК, МУЖИК</strong></p>"
        )
    }
    cell_list = list(zip(df['AvitoId'].tolist(), df['Description'].tolist(), df['VehicleType'].tolist()))
    cell_total = len(cell_list)
    print(f'Всего объявлений для обработки: {cell_total}')
    for cell in cell_list:
        total_processed += process_cell(df, key_dict, cell)
        print(total_processed)
    df.to_excel(r'table_updated_delete.xlsx', index=False)
    print(f'Всего обработано: {total_processed}')

def process_cell(df, key_dict, cell):
    '''Функция обработки ячейки Description'''
    id, description, type = cell
    id = int(id) if pd.notna(id) else None
    description_str = df.loc[df['AvitoId'] == id, 'Description'].dropna().values
    if description_str.size > 0 and isinstance(description_str[0], str):
        description_list = list(description_str[0].partition(key_dict['full']))
        try:
            description_list[1] = key_dict[type]
            fixed_description = ''.join(description_list)
            df.loc[df['AvitoId'] == id, 'Description'] = fixed_description
            return 1
        except:
            return 0
    return 0

if __name__ == "__main__":
    main()