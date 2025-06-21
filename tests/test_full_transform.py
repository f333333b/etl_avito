import pandas as pd
import pytest
from main import transform_pipeline

# Мокаем необходимые справочники для monkeypatch, если функции их используют
CITIES = ['Москва', 'Пермь']
CITY_TO_FULL_ADDRESS = {'Москва': 'Москва, улица Ленина', 'Пермь': 'Пермь, улица Карла Маркса'}
DEALERSHIPS = {'Honda': ['Москва'], 'Yamaha': ['Пермь']}

FULL_CONFIG = {
    "transformations": [
        "clean_raw_data",
        "normalize_group_by_latest",
        "normalize_addresses_column",
        "remove_invalid_dealerships",
        "fill_missing_cities",
        "normalize_columns_to_constants",
        "convert_data_types"
    ]
}

def test_transform_pipeline_full(monkeypatch):
    # Monkeypatching справочники
    monkeypatch.setattr("etl.transform.cities", CITIES)
    monkeypatch.setattr("etl.transform.city_to_full_address", CITY_TO_FULL_ADDRESS)
    monkeypatch.setattr("etl.transform.dealerships", DEALERSHIPS)

    df = pd.DataFrame({
        'AvitoId': [1, 1, 2, None],
        'Id': ['a', 'a', 'b', None],
        'Other': [' x ', ' x ', 'y ', None],
        'Title': ['Bike1', 'Bike1', 'Bike2', None],
        'AvitoDateEnd': ['2024-01-01', '2025-01-01', '2024-06-01', None],
        'Price': [100, 200, 300, None],
        'Address': ['Москва', 'Москва', 'Пермь', None],
        'AvitoStatus': ['Активно', 'Архив', 'Архив', None],
        'Make': ['Honda', 'Honda', 'Yamaha', None],
        'Condition': ['Новый', 'Б/у', 'Б/у', None],
        'Year': [2020, 2024, 2023, None],
        'Kilometrage': [0, 5, 1000, None],
        'DisplayAreas': ['abc', '', '', None],
    })

    result = transform_pipeline(df.copy(), FULL_CONFIG)
    print(result[['Title', 'AvitoDateEnd', 'AvitoStatus']])
    # Проверяем, что остались только уникальные и последние записи
    assert result.shape[0] == 2
    assert set(result['Title']) == {'Bike1', 'Bike2'}

    # Проверяем нормализацию адресов
    assert result.loc[result['Title'] == 'Bike1', 'Address'].iloc[0] == 'Москва, улица Ленина'
    assert result.loc[result['Title'] == 'Bike2', 'Address'].iloc[0] == 'Пермь, улица Карла Маркса'

    assert set(result['Title'].tolist()) == {'Bike1', 'Bike2'}
    assert result.loc[result['Title'] == 'Bike1', 'AvitoDateEnd'].iloc[0] == '2025-01-01'
    assert result.loc[result['Title'] == 'Bike2', 'AvitoDateEnd'].iloc[0] == '2024-06-01'

    # Проверяем типы данных
    assert result['AvitoId'].dtype.name.startswith("Int")
    assert result['Price'].dtype.name in ('int64', 'Int64', 'float64')

    # Проверяем нормализацию Condition и прочих полей
    assert all(result['Condition'] == 'Б/у')
    assert all(result['Kilometrage'] == 5)
    assert all(result['DisplayAreas'] == '')

def test_transform_pipeline_partial(monkeypatch):
    # Только часть трансформаций
    df = pd.DataFrame({
        'AvitoId': [1, 1],
        'Id': ['a', 'a'],
        'Other': [' x ', 'x ']
    })
    config = {"transformations": ["clean_raw_data"]}
    result = transform_pipeline(df, config)
    assert result.shape[0] == 1
    assert result.iloc[0]['Other'] == 'x'

def test_transform_pipeline_unknown_transform():
    df = pd.DataFrame({'AvitoId': [1], 'Id': ['a']})
    config = {"transformations": ["unknown_transform"]}
    with pytest.raises(ValueError):
        transform_pipeline(df, config)

def test_transform_pipeline_no_transformations():
    df = pd.DataFrame({'AvitoId': [1], 'Id': ['a']})
    config = {}
    result = transform_pipeline(df, config)
    pd.testing.assert_frame_equal(result, df)