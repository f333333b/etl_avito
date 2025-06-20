import pandas as pd
import os
from contextlib import contextmanager
import pytest
import requests
from unittest.mock import Mock, patch, MagicMock
from etl.validation import check_url

from etl.validation import (get_duplicated_values, get_duplicated_rows, save_duplicates_to_excel, validate_uniqueness,
                            validate_urls, validate_required_fields, validate_format_fields, validate_data)

# тесты для get_duplicated_values
def test_multiple_duplicates():
    series = pd.Series([1, 2, 2, 3, 3, 3, 4])
    result = get_duplicated_values(series)
    assert set(result) == {2, 3}
    assert len(result) == 2

def test_no_duplicates():
    series = pd.Series([10, 20, 30])
    result = get_duplicated_values(series)
    assert len(result) == 0

def test_single_duplicate():
    series = pd.Series(['a', 'b', 'c', 'a'])
    result = get_duplicated_values(series)
    assert list(result) == ['a']

def test_with_nans():
    series = pd.Series([1, 2, 2, None, None, 3])
    result = get_duplicated_values(series)
    has_nan = any(pd.isna(val) for val in result)
    has_2 = 2 in result
    assert has_2, "Ожидался дубликат значения 2"
    assert has_nan, "Ожидался дубликат значения NaN"

def test_empty_series():
    series = pd.Series([], dtype='float64')
    result = get_duplicated_values(series)
    assert len(result) == 0

# тесты для get_duplicated_rows
def test_get_duplicated_rows_basic():
    df = pd.DataFrame({
        'Id': [1, 2, 2, 3, 4, 4],
        'Value': ['a', 'b', 'b', 'c', 'd', 'd']
    })
    result = get_duplicated_rows(df, column='Id')
    assert len(result) == 4
    assert set(result['Id']) == {2, 4}

def test_get_duplicated_rows_with_skip_empty_true():
    df = pd.DataFrame({
        'Id': [None, 2, 2, 3, None],
    })
    result = get_duplicated_rows(df, column='Id', skip_empty=True)
    assert len(result) == 2
    assert (result['Id'] == 2).all()

def test_get_duplicated_rows_with_skip_empty_false():
    df = pd.DataFrame({
        'Id': [None, None, 1, 2, 2],
    })
    result = get_duplicated_rows(df, column='Id', skip_empty=False)
    assert set(result['Id'].dropna()) == {2}
    assert result['Id'].isna().sum() == 2
    assert len(result) == 4

def test_get_duplicated_rows_no_duplicates():
    df = pd.DataFrame({
        'Id': [1, 2, 3, 4]
    })
    result = get_duplicated_rows(df, column='Id')
    assert result.empty

def test_get_duplicated_rows_all_nulls():
    df = pd.DataFrame({
        'Id': [None, None, None]
    })
    result = get_duplicated_rows(df, column='Id', skip_empty=False)
    assert len(result) == 3

# тесты для save_duplicates_to_excel
@contextmanager
def excel_writer(filename):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        yield writer

def test_save_duplicates_to_excel_valid_dataframe(tmp_path):
    df = pd.DataFrame({
        'Id': ['qlz_93', 'qlz_93', '09052025sg012'],
        'AvitoId': [3647586848, 3647586848, 7326489345],
        'Title': ['Motor 1', 'Motor 1', 'Moped']
    })
    column = 'Id'
    os.chdir(tmp_path)
    with patch('etl.validation.excel_writer', excel_writer):
        result = save_duplicates_to_excel(df, column)
    assert result.startswith('./validation_logs/duplicates_Id_')
    assert result.endswith('.xlsx')
    assert os.path.exists(result)
    saved_df = pd.read_excel(result)
    pd.testing.assert_frame_equal(saved_df, df)

def test_save_duplicates_to_excel_empty_dataframe(tmp_path):
    df = pd.DataFrame(columns=['Id', 'AvitoId', 'Title'])
    column = 'Id'
    os.chdir(tmp_path)
    with patch('etl.validation.excel_writer', excel_writer):
        result = save_duplicates_to_excel(df, column)
    assert result.startswith('./validation_logs/duplicates_Id_')
    assert result.endswith('.xlsx')
    assert os.path.exists(result)
    saved_df = pd.read_excel(result)
    assert saved_df.empty
    assert list(saved_df.columns) == ['Id', 'AvitoId', 'Title']

def test_save_duplicates_to_excel_filename_format(tmp_path):
    df = pd.DataFrame({'Id': ['qlz_93'], 'AvitoId': [3647586848]})
    column = 'AvitoId'

    os.chdir(tmp_path)
    with patch('etl.validation.excel_writer', excel_writer), \
         patch('etl.validation.datetime') as mock_datetime:
        mock_datetime.now.return_value.strftime.return_value = '2025-06-20_20-27-00'
        result = save_duplicates_to_excel(df, column)
    assert result == './validation_logs/duplicates_AvitoId_2025-06-20_20-27-00.xlsx'

def test_save_duplicates_to_excel_directory_creation(tmp_path):
    df = pd.DataFrame({'Id': ['qlz_93'], 'AvitoId': [3647586848]})
    column = 'Id'

    os.chdir(tmp_path)
    with patch('etl.validation.excel_writer', excel_writer):
        result = save_duplicates_to_excel(df, column)
    assert os.path.exists(tmp_path / 'validation_logs')

def test_save_duplicates_to_excel_error_handling(tmp_path, caplog):
    df = pd.DataFrame({'Id': ['qlz_93'], 'AvitoId': [3647586848]})
    column = 'Id'

    os.chdir(tmp_path)
    with patch('etl.validation.excel_writer') as mock_writer:
        mock_writer.side_effect = Exception("Write error")
        with pytest.raises(Exception, match="Write error"):
            save_duplicates_to_excel(df, column)

# тесты для validate_uniqueness
@pytest.fixture
def mock_logger():
    with patch('etl.validation.logger') as mock:
        yield mock


@pytest.fixture
def mock_get_duplicated_rows():
    with patch('etl.validation.get_duplicated_rows') as mock:
        yield mock


@pytest.fixture
def mock_save_duplicates_to_excel():
    with patch('etl.validation.save_duplicates_to_excel') as mock:
        yield mock


def test_validate_uniqueness_no_duplicates(mock_logger, mock_get_duplicated_rows):
    df = pd.DataFrame({
        'Id': ['qlz_93', '09052025sg012'],
        'AvitoId': [3647586848, 7326489345]
    })
    mock_get_duplicated_rows.return_value = pd.DataFrame(columns=['Id', 'AvitoId'])

    result, errors = validate_uniqueness(df)

    assert result is True
    assert errors == []
    assert mock_logger.info.call_count == 2
    mock_get_duplicated_rows.assert_any_call(df, 'AvitoId', True)
    mock_get_duplicated_rows.assert_any_call(df, 'Id', False)


def test_validate_uniqueness_with_duplicates(tmp_path, mock_logger, mock_get_duplicated_rows, mock_save_duplicates_to_excel):
    df = pd.DataFrame({
        'Id': ['qlz_93', 'qlz_93', '09052025sg012'],
        'AvitoId': [3647586848, 3647586848, 7326489345]
    })
    duplicated_avito = pd.DataFrame({
        'Id': ['qlz_93', 'qlz_93'],
        'AvitoId': [3647586848, 3647586848]
    }, index=[0, 1])
    duplicated_id = pd.DataFrame({
        'Id': ['qlz_93', 'qlz_93'],
        'AvitoId': [3647586848, 3647586848]
    }, index=[0, 1])
    mock_get_duplicated_rows.side_effect = [duplicated_avito, duplicated_id]
    mock_save_duplicates_to_excel.side_effect = [
        './validation_logs/duplicates_AvitoId_2025-06-20.xlsx',
        './validation_logs/duplicates_Id_2025-06-20.xlsx'
    ]
    os.chdir(tmp_path)
    result, errors = validate_uniqueness(df)
    assert result is False
    assert len(errors) == 2
    assert errors[0].startswith("Найдены дубликаты в 'AvitoId'")
    assert errors[1].startswith("Найдены дубликаты в 'Id'")
    called_args = mock_save_duplicates_to_excel.call_args_list
    called_df_1, called_col_1 = called_args[0][0]
    pd.testing.assert_frame_equal(called_df_1.reset_index(drop=True), duplicated_avito.reset_index(drop=True))
    assert called_col_1 == 'AvitoId'
    called_df_2, called_col_2 = called_args[1][0]
    pd.testing.assert_frame_equal(called_df_2.reset_index(drop=True), duplicated_id.reset_index(drop=True))
    assert called_col_2 == 'Id'

def test_validate_uniqueness_empty_dataframe(mock_logger, mock_get_duplicated_rows):
    df = pd.DataFrame(columns=['Id', 'AvitoId'])
    mock_get_duplicated_rows.return_value = pd.DataFrame(columns=['Id', 'AvitoId'])
    result, errors = validate_uniqueness(df)
    assert result is True
    assert errors == []
    assert mock_logger.info.call_count == 2


def test_validate_uniqueness_missing_columns(mock_logger):
    df = pd.DataFrame({'Other': [1, 2]})
    with pytest.raises(KeyError):
        validate_uniqueness(df)
    assert mock_logger.info.call_count == 0

def test_validate_uniqueness_partial_duplicates(tmp_path, mock_logger, mock_get_duplicated_rows, mock_save_duplicates_to_excel):
    df = pd.DataFrame({
        'Id': ['qlz_93', 'qlz_93', '09052025sg012'],
        'AvitoId': [3647586848, 7326489345, 4351388919]
    })
    duplicated_id = pd.DataFrame({
        'Id': ['qlz_93', 'qlz_93'],
        'AvitoId': [3647586848, 7326489345]
    })
    mock_get_duplicated_rows.side_effect = [pd.DataFrame(columns=['Id', 'AvitoId']), duplicated_id]
    mock_save_duplicates_to_excel.return_value = './validation_logs/duplicates_Id_2025-06-20.xlsx'
    os.chdir(tmp_path)
    result, errors = validate_uniqueness(df)
    assert result is False
    assert len(errors) == 1
    assert errors[0].startswith("Найдены дубликаты в 'Id' (всего: 1). Сохранено в:")
    mock_save_duplicates_to_excel.assert_called_once_with(duplicated_id, 'Id')
    mock_logger.info.assert_called_once_with("Проверка 'AvitoId' на уникальность пройдена")

# тесты для check_url
@pytest.fixture
def mock_session():
    return Mock(spec=requests.Session)

@patch('time.sleep', return_value=None)
@patch('random.uniform', return_value=0.3)
def test_check_url_valid(mock_uniform, mock_sleep, mock_session):
    mock_session.head.return_value.status_code = 200
    result = check_url(mock_session, '123', 'https://example.com')
    assert result is None
    mock_session.head.assert_called_once_with('https://example.com', timeout=5, allow_redirects=True)

@patch('time.sleep', return_value=None)
@patch('random.uniform', return_value=0.3)
def test_check_url_invalid_status(mock_uniform, mock_sleep, mock_session):
    mock_session.head.return_value.status_code = 404
    result = check_url(mock_session, '456', 'https://example.com/404')
    assert result == "URL https://example.com/404 в строке с Id 456 вернул статус 404"

@patch('time.sleep', return_value=None)
@patch('random.uniform', return_value=0.3)
def test_check_url_exception(mock_uniform, mock_sleep, mock_session):
    mock_session.head.side_effect = requests.RequestException("Timeout")
    result = check_url(mock_session, '789', 'https://example.com/timeout')
    assert "Ошибка при HEAD-запросе к https://example.com/timeout в строке с Id 789" in result

def test_check_url_invalid_format():
    result = check_url(None, '001', 'ftp://example.com')
    assert result == "Некорректный формат URL в строке с Id 001: ftp://example.com"

def test_check_url_empty():
    assert check_url(None, '002', '') is None
    assert check_url(None, '003', '   ') is None
    assert check_url(None, '004', None) is None

# тесты для validate_urls
@patch('etl.validation.check_url')
@patch('etl.validation.requests.Session')
def test_validate_urls_all_valid(mock_session_cls, mock_check_url):
    df = pd.DataFrame({
        'VideoURL': ['https://valid1.com'],
        'VideoFilesURL': ['https://valid2.com'],
        'ImageUrls': ['https://img1.com|https://img2.com']
    })
    mock_check_url.return_value = None
    mock_session = MagicMock()
    mock_session_cls.return_value.__enter__.return_value = mock_session

    result, errors = validate_urls(df)
    assert result is True
    assert errors == []
    assert mock_check_url.call_count == 3

@patch('etl.validation.check_url')
@patch('etl.validation.requests.Session')
def test_validate_urls_some_invalid(mock_session_cls, mock_check_url):
    df = pd.DataFrame({
        'VideoURL': ['https://valid.com'],
        'VideoFilesURL': ['https://bad.com'],
        'ImageUrls': ['https://img1.com|https://img2.com']
    })
    mock_check_url.side_effect = [None, 'error1', None]
    mock_session = MagicMock()
    mock_session_cls.return_value.__enter__.return_value = mock_session

    result, errors = validate_urls(df)
    assert result is False
    assert errors == ['error1']
    assert mock_check_url.call_count == 3

@patch('etl.validation.check_url')
@patch('etl.validation.requests.Session')
def test_validate_urls_missing_columns(mock_session_cls, mock_check_url, caplog):
    df = pd.DataFrame({
        'SomeOtherColumn': ['value']
    })
    mock_session = MagicMock()
    mock_session_cls.return_value.__enter__.return_value = mock_session

    result, errors = validate_urls(df)
    assert result is True
    assert errors == []
    assert mock_check_url.call_count == 0

@patch('etl.validation.check_url')
@patch('etl.validation.requests.Session')
def test_validate_urls_imageurls_multiple_urls(mock_session_cls, mock_check_url):
    df = pd.DataFrame({
        'ImageUrls': ['https://img1.com|https://img2.com|https://img3.com']
    })
    mock_check_url.return_value = None
    mock_session = MagicMock()
    mock_session_cls.return_value.__enter__.return_value = mock_session

    result, errors = validate_urls(df)
    assert result is True
    assert errors == []
    mock_check_url.assert_called_once_with(session=mock_session, id=0, url='https://img1.com')

# тесты для validate_required_fields
def test_validate_required_fields_all_valid():
    df = pd.DataFrame([{
        'Id': '1', 'Address': 'Город', 'Category': 'Мото',
        'Title': 'Test', 'Description': 'desc', 'VehicleType': 'Мотоциклы', 'Make': 'Yamaha', 'Model': 'YZF',
        'Type': 'Спорт', 'Year': 2020, 'Availability': 'В наличии', 'Condition': 'Б/у',
        'EngineType': 'Бензиновый', 'Power': 100, 'EngineCapacity': 600, 'Kilometrage': 10000,
        'ImageUrls': 'https://img.com', 'ImageNames': ''
    }])
    valid, errors = validate_required_fields(df)
    assert valid is True
    assert errors == []

def test_validate_required_fields_base_missing():
    df = pd.DataFrame([{
        'Id': '', 'Address': ' ', 'Category': None,
        'Title': '', 'Description': '', 'VehicleType': '', 'Make': '', 'Model': '',
        'Type': '', 'Year': '', 'Availability': '', 'Condition': '',
        'ImageUrls': '', 'ImageNames': ''
    }])
    valid, errors = validate_required_fields(df)
    assert not valid
    assert any("Строка 0" in e for e in errors)

def test_validate_required_fields_moto_missing():
    df = pd.DataFrame([{
        'Id': '1', 'Address': 'A', 'Category': 'Мото', 'Title': 'T', 'Description': 'D',
        'VehicleType': 'Мотоциклы', 'Make': 'Honda', 'Model': 'X',
        'Type': 'Кросс', 'Year': 2023, 'Availability': 'Да', 'Condition': 'Б/у',
        'ImageUrls': '', 'ImageNames': '',
        'EngineType': '', 'Power': '', 'EngineCapacity': '', 'Kilometrage': ''
    }])
    valid, errors = validate_required_fields(df)
    assert not valid
    assert "EngineType" in errors[0]

def test_validate_required_fields_quadro_missing():
    df = pd.DataFrame([{
        'Id': '1', 'Address': 'A', 'Category': 'ATV', 'Title': 'T', 'Description': 'D',
        'VehicleType': 'Квадроциклы', 'Make': 'CFMOTO', 'Model': 'Z10',
        'Type': 'UTV', 'Year': 2023, 'Availability': 'Да', 'Condition': 'Б/у',
        'ImageUrls': '', 'ImageNames': '',
        'EngineType': '', 'Power': '', 'EngineCapacity': '', 'Kilometrage': '', 'PersonCapacity': ''
    }])
    valid, errors = validate_required_fields(df)
    assert not valid
    assert "PersonCapacity" in errors[0]

def test_validate_required_fields_boat_motor_missing():
    df = pd.DataFrame([{
        'Id': '1', 'Address': 'A', 'Category': 'Лодки', 'Title': 'T', 'Description': 'D',
        'VehicleType': 'Моторные лодки и моторы', 'Make': 'Yamaha', 'Model': 'M15',
        'Type': 'Лодочный мотор', 'Year': 2022, 'Availability': 'Да', 'Condition': 'Б/у',
        'ImageUrls': '', 'ImageNames': '',
        'EngineType': '', 'Power': ''
    }])
    valid, errors = validate_required_fields(df)
    assert not valid
    assert "EngineType" in errors[0]

def test_validate_required_fields_boat_body_missing():
    df = pd.DataFrame([{
        'Id': '1', 'Address': 'A', 'Category': 'Лодки', 'Title': 'T', 'Description': 'D',
        'VehicleType': 'Моторные лодки и моторы', 'Make': 'Yamaha', 'Model': 'RX',
        'Type': 'Лодка ПВХ (надувная)', 'Year': 2022, 'Availability': 'Да', 'Condition': 'Б/у',
        'ImageUrls': '', 'ImageNames': '',
        'FloorType': '', 'Length': '', 'Width': '', 'SeatingCapacity': '', 'MaxPower': '',
        'TrailerIncluded': '', 'EngineIncluded': ''
    }])
    valid, errors = validate_required_fields(df)
    assert not valid
    assert "FloorType" in errors[0]

def test_validate_required_fields_images_only():
    df = pd.DataFrame([{
        'Id': '1', 'Address': 'A', 'Category': 'C', 'Title': 'T', 'Description': 'D',
        'VehicleType': 'Мотоциклы', 'Make': 'Suzuki', 'Model': 'S',
        'Type': 'Спорт', 'Year': 2023, 'Availability': 'Да', 'Condition': 'Б/у',
        'EngineType': 'Тип', 'Power': 50, 'EngineCapacity': 500, 'Kilometrage': 10000,
        'ImageUrls': '', 'ImageNames': ''
    }])
    valid, errors = validate_required_fields(df)
    assert not valid
    assert "ImageUrls or ImageNames" in errors[0]

def test_validate_required_fields_missing_columns_structure():
    df = pd.DataFrame([{
        'Id': '1', 'VehicleType': 'Квадроциклы', 'Type': 'UTV'
    }])
    valid, errors = validate_required_fields(df)
    assert not valid
    assert errors[0].startswith("Отсутствуют обязательные колонки:")

# тесты для validate_data
@pytest.fixture
def sample_df_valid():
    return pd.DataFrame([{
        'Id': '1', 'AvitoId': 1001, 'Address': 'A', 'Category': 'C', 'Title': 'T',
        'Description': 'D', 'VehicleType': 'Мотоциклы', 'Make': 'Yamaha', 'Model': 'YZ',
        'Type': 'Спорт', 'Year': 2023, 'Availability': 'В наличии', 'Condition': 'Б/у',
        'EngineType': 'Бензин', 'Power': 100, 'EngineCapacity': 600, 'Kilometrage': 1000,
        'ImageUrls': 'https://img.com', 'ImageNames': ''
    }])

@patch('etl.validation.validate_uniqueness')
@patch('etl.validation.validate_required_fields')
def test_validate_data_all_valid(mock_required, mock_unique, sample_df_valid):
    mock_unique.return_value = (True, [])
    mock_required.return_value = (True, [])
    result, errors = validate_data(sample_df_valid)
    assert result is True
    assert errors == []
    mock_unique.assert_called_once()
    mock_required.assert_called_once()

@patch('etl.validation.validate_uniqueness')
@patch('etl.validation.validate_required_fields')
def test_validate_data_with_uniqueness_errors(mock_required, mock_unique, sample_df_valid):
    mock_unique.return_value = (False, ['дубликаты по Id'])
    mock_required.return_value = (True, [])
    result, errors = validate_data(sample_df_valid)
    assert result is False
    assert 'дубликаты по Id' in errors

@patch('etl.validation.validate_uniqueness')
@patch('etl.validation.validate_required_fields')
def test_validate_data_with_required_errors(mock_required, mock_unique, sample_df_valid):
    mock_unique.return_value = (True, [])
    mock_required.return_value = (False, ['пропущены поля'])
    result, errors = validate_data(sample_df_valid)
    assert result is False
    assert 'пропущены поля' in errors

@patch('etl.validation.validate_uniqueness')
@patch('etl.validation.validate_required_fields')
def test_validate_data_multiple_errors(mock_required, mock_unique, sample_df_valid):
    mock_unique.return_value = (False, ['дубликаты по Id'])
    mock_required.return_value = (False, ['пропущены поля'])
    result, errors = validate_data(sample_df_valid)
    assert result is False
    assert len(errors) == 2
    assert 'дубликаты по Id' in errors
    assert 'пропущены поля' in errors

# тесты для validate_format_fields
def test_valid_data():
    df = pd.DataFrame({
        'EMail': ['test@example.com'],
        'ContactPhone': ['79991234567'],
        'Id': ['abc123'],
        'AvitoId': ['123456']
    })
    is_valid, errors = validate_format_fields(df)
    assert is_valid is True
    assert errors == []


def test_invalid_email():
    df = pd.DataFrame({'EMail': ['invalid_email']})
    is_valid, errors = validate_format_fields(df)
    assert not is_valid
    assert "Некорректные email" in errors[0]


def test_invalid_phone():
    df = pd.DataFrame({'ContactPhone': ['89991234567']})
    is_valid, errors = validate_format_fields(df)
    assert not is_valid
    assert "Некорректные номера телефонов" in errors[0]


def test_invalid_id():
    df = pd.DataFrame({'Id': ['abc_123']})  # подчёркивание недопустимо
    is_valid, errors = validate_format_fields(df)
    assert not is_valid
    assert "Некорректные Id" in errors[0]


def test_invalid_avito_id():
    df = pd.DataFrame({'AvitoId': ['12a34']})
    is_valid, errors = validate_format_fields(df)
    assert not is_valid
    assert "Некорректные AvitoId" in errors[0]


def test_multiple_invalid():
    df = pd.DataFrame({
        'EMail': ['invalid'],
        'ContactPhone': ['123'],
        'Id': ['$$$'],
        'AvitoId': ['abc']
    })
    is_valid, errors = validate_format_fields(df)
    assert not is_valid
    assert len(errors) == 4