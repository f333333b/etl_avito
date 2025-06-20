import pandas as pd
from datetime import datetime
from etl.transform import (
    clean_raw_data, normalize_group_by_latest, normalize_addresses,
    remove_invalid_dealerships, fill_missing_cities,
    normalize_columns_to_constants, normalize_addresses_column,
    convert_data_types
)

cities = ['Москва', 'Пермь']
city_to_full_address = {'Москва': 'Москва, улица Ленина', 'Пермь': 'Пермь, улица Карла Маркса'}
dealerships = {'Honda': ['Москва'], 'Yamaha': ['Пермь']}


def test_clean_raw_data():
    df = pd.DataFrame({
        'AvitoId': [1, 1, None],
        'Id': ['a', 'a', None],
        'Other': [' x ', ' x ', None]
    })
    cleaned = clean_raw_data(df)
    assert cleaned.shape[0] == 1
    assert cleaned.iloc[0]['Other'] == 'x'


def test_normalize_group_by_latest():
    df = pd.DataFrame({
        'Title': ['Bike1', 'Bike1'],
        'AvitoDateEnd': ['2024-01-01', '2025-01-01'],
        'Price': [100, 200],
        'Address': ['Москва', 'Москва'],
        'AvitoStatus': ['Активно', 'Архив']
    })
    result = normalize_group_by_latest(df)
    assert result.shape[0] == 1
    assert result.iloc[0]['Price'] == 200
    assert result.iloc[0]['AvitoDateEnd'] == '2025-01-01'


def test_normalize_addresses(monkeypatch):
    monkeypatch.setattr("etl.transform.city_to_full_address", {
        'Москва': 'Москва, улица Ленина',
        'Пермь': 'Пермь, улица Карла Маркса'
    })
    assert normalize_addresses("Москва", "123") == "Москва, улица Ленина"
    assert normalize_addresses("Казань", "123") == "Казань"


def test_remove_invalid_dealerships(monkeypatch):
    df = pd.DataFrame({
        'Make': ['Honda', 'Yamaha', 'Yamaha'],
        'Address': ['Москва', 'Пермь', 'Москва'],
        'AvitoId': ['1', '2', '3']
    })
    monkeypatch.setattr("etl.transform.dealerships", dealerships)
    result = remove_invalid_dealerships(df)
    assert result.shape[0] == 2
    assert '3' not in result['AvitoId'].values


def test_fill_missing_cities(monkeypatch):
    df = pd.DataFrame({
        'Title': ['Мотоцикл X'],
        'Make': ['Honda'],
        'Address': ['Москва'],
        'AvitoStatus': ['Активно'],
        'Id': ['0001']
    })
    monkeypatch.setattr("etl.transform.dealerships", dealerships)
    monkeypatch.setattr("etl.transform.cities", cities)
    result = fill_missing_cities(df, dealerships)
    assert result.shape[0] >= 1  # может быть больше, если города отсутствовали
    assert 'Пермь' not in result['Address'].values  # для Honda только Москва


def test_normalize_columns_to_constants():
    year = datetime.now().year
    df = pd.DataFrame({
        'Condition': ['Новый', 'Б/у'],
        'Year': [2020, year],
        'Kilometrage': [0, 5],
        'DisplayAreas': ['abc', '']
    })
    result = normalize_columns_to_constants(df.copy())
    assert all(result['Condition'] == 'Б/у')
    assert all(result['Year'] == year)
    assert all(result['Kilometrage'] == 5)
    assert all(result['DisplayAreas'] == '')


def test_normalize_addresses_column(monkeypatch):
    df = pd.DataFrame({
        'Address': ['Москва', 'Казань'],
        'AvitoId': ['1', '2']
    })
    monkeypatch.setattr("etl.transform.city_to_full_address", city_to_full_address)
    result = normalize_addresses_column(df.copy())
    assert result.loc[0, 'Address'] == 'Москва, улица Ленина'
    assert result.loc[1, 'Address'] == 'Казань'


def test_convert_data_types():
    df = pd.DataFrame({
        'AvitoId': ['1', '2'],
        'Price': ['1000', 'invalid'],
        'Id': [123, 456],
        'Title': [789, 'Name'],
    })
    result = convert_data_types(df.copy())
    assert result['AvitoId'].dtype.name.startswith("Int")
    assert result['Price'].isnull().iloc[1]  # invalid converted to NaN
    assert result['Id'].dtype.name == 'string'
    assert result['Title'].dtype.name == 'string'
