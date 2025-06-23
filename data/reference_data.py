from datetime import datetime

cities = [
    "Архангельск", "Барнаул", "Балашиха", "Волгоград", "Екатеринбург", "Иркутск", "Краснодар", "Красноярск",
    "Нижний Новгород", "Новосибирск", "Оренбург", "Пермь", "Самара", "Саратов", "Санкт-Петербург", "Сургут",
    "Тюмень", "Уфа", "Челябинск", "Нижневартовск", "Ноябрьск", "Тобольск", "Ханты-Мансийск"
]

dealerships = {
    'AODES': [
    "Оренбург", "Тобольск", "Новосибирск", "Красноярск", "Челябинск", "Сургут",
    "Ноябрьск", "Тюмень", "Екатеринбург", "Нижневартовск", "Иркутск"
],
    'Stels': cities,
    'Русская механика': ['Сургут', 'Нижневартовск', 'Ноябрьск'],
    'VOGE': ['Тюмень', 'Тобольск']
}

city_to_full_address = {
    "Архангельск": "Архангельская обл., Архангельск, ул. Смольный Буян",
    "Барнаул": "Алтайский край, Барнаул, пл. Советов",
    "Балашиха": "Московская область, Балашиха, проспект Ленина",
    "Волгоград": "Волгоградская обл., Волгоград, ул. Рокоссовского",
    "Екатеринбург": "Свердловская обл., Екатеринбург, Селькоровская ул.",
    "Иркутск": "Иркутская обл., Иркутск, ул. Рабочего Штаба",
    "Краснодар": "Краснодарский край, Краснодар, Новороссийская ул.",
    "Красноярск": "Красноярский край, Красноярск, Караульная ул.",
    "Нижневартовск": "Ханты-Мансийский автономный округ, Нижневартовск, Северная ул.",
    "Нижний Новгород": "Нижегородская обл., Нижний Новгород, ул. Лейтенанта Шмидта",
    "Новосибирск": "Новосибирская обл., Новосибирск, ул. Немировича-Данченко",
    "Ноябрьск": "Ямало-Ненецкий автономный округ, Ноябрьск, мкр-н П-6",
    "Оренбург": "Оренбургская обл., Оренбург, ул. Монтажников",
    "Пермь": "Пермский край, Пермь, ул. Лифанова",
    "Самара": "Самарская обл., Самара, Алма-Атинская ул.",
    "Саратов": "Саратовская обл., Саратов, Большая Долинная ул.",
    "Санкт-Петербург": "Санкт-Петербург, пр-т Большевиков",
    "Сургут": "Ханты-Мансийский автономный округ, Сургут, Быстринская ул.",
    "Тобольск": "Тюменская обл., Тобольск, 2-й квартал",
    "Тюмень": "Тюменская обл., Тюмень, ул. Тимофея Чаркова",
    "Уфа": "Республика Башкортостан, Уфа",
    "Ханты-Мансийск": "Ханты-Мансийский автономный округ, Ханты-Мансийск, ул. Энгельса",
    "Челябинск": "Челябинская обл., Челябинск, Троицкий тракт"
}

autoload_allowed_values = {
    'Id': {
        'allowed_values': None,
        'required_parameter': True,
        'data_type': str
    },
    'DateBegin': {
        'allowed_values': None,
        'required_parameter': False,
        'data_type': datetime
    },
    'DateEnd': {
        'allowed_values': None,
        'required_parameter': False,
        'data_type': datetime
    },
    'ListingFee': {
        'allowed_values': ['Package', 'PackageSingle', 'Single'],
        'required_parameter': False,
        'data_type': str
    },
    'AdStatus': {
        'allowed_values': ['Free', 'Highlight', 'XL', 'x2_1', 'x2_7', 'x5_1', 'x5_7', 'x10_1', 'x10_7', 'x15_1',
                           'x15_7', 'x20_1', 'x20_7'],
        'required_parameter': False,
        'data_type': str
    },
    'AvitoId': {
        'allowed_values': None,
        'required_parameter': False,
        'data_type': int
    },
    'ManagerName': {
        'allowed_values': None,
        'required_parameter': False,
        'data_type': str
    },
    'ContactPhone': {
        'allowed_values': None,
        'required_parameter': False,
        'data_type': str
    },
    'Address': {
        'allowed_values': None,
        'required_parameter': True,
        'data_type': str
    },
    'Latitude': {
        'allowed_values': None,
        'required_parameter': False,
        'data_type': float
    },
    'Longitude': {
        'allowed_values': None,
        'required_parameter': False,
        'data_type': float
    },
    'ContactMethod': {
        'allowed_values': ['По телефону и в сообщениях', 'По телефону', 'В сообщениях'],
        'required_parameter': False,
        'data_type': str
    },
    'InternetCalls': {
        'allowed_values': ['Да', 'Нет'],
        'required_parameter': False,
        'data_type': str
    },
    'CallsDevices': {
        'allowed_values': None,
        'required_parameter': False,
        'data_type': str
    },
    'Delivery': {
        'allowed_values': ['Выключена', 'ПВЗ', 'Курьер', 'Постамат', 'Свой курьер', 'Свой партнер СДЭК',
                           'Свой партнер Деловые Линии', 'Свой партнер DPD', 'Свой партнер ПЭК',
                           'Свой партнер Почта России', 'Свой партнер Boxberry', 'Свой партнер СДЭК курьер',
                           'Самовывоз с онлайн-оплатой'],
        'required_parameter': False,
        'data_type': str
    },
    'WeightForDelivery': {
        'allowed_values': None,
        'required_parameter': False,
        'data_type': float
    },
    'LengthForDelivery': {
        'allowed_values': None,
        'required_parameter': False,
        'data_type': int
    },
    'HeightForDelivery': {
        'allowed_values': None,
        'required_parameter': False,
        'data_type': int
    },
    'WidthForDelivery': {
        'allowed_values': None,
        'required_parameter': False,
        'data_type': int
    },
    'Category': {
        'allowed_values': ['Мотоциклы и мототехника', 'Водный транспорт'],
        'required_parameter': True,
        'data_type': str
    },
    'Title': {
        'allowed_values': None,
        'required_parameter': True,
        'data_type': str
    },
    'Description': {
        'allowed_values': None,
        'required_parameter': True,
        'data_type': str
    },
    'Price': {
        'allowed_values': None,
        'required_parameter': False,
        'data_type': int
    },
    'VehicleType': {
        'allowed_values': ['Мопеды и скутеры', 'Квадроциклы', 'Мотоциклы', 'Снегоходы', 'Моторные лодки и моторы'],
        'required_parameter': True,
        'data_type': str
    },
    'Make': {
        'allowed_values': None,
        'required_parameter': True,
        'data_type': str
    },
    'Model': {
        'allowed_values': None,
        'required_parameter': True,
        'data_type': str
    },
    'Type': {
        'allowed_values': ['Скутер', 'Макси-скутер', 'Мопед', 'Минибайк', 'Багги', 'Утилитарный', 'Спортивный',
                            'Туристический', 'Детский', 'Круизер или чоппер', 'Спортбайк', 'Туристический',
                           'Спорт-турист', 'Тур-эндуро', 'Трицикл', 'Naked bike', 'Мотард', 'Эндуро', 'Кроссовый',
                           'Питбайк', 'Триал', 'Детский', 'Кастом', 'Утилитарный', 'Спортивный или горный',
                           'Туристический', 'Детский', 'Мотобуксировщик', 'Лодка ПВХ (надувная)',
                           'Лодка RIB (комбинированная)', 'Лодка с жестким корпусом', 'Лодочный мотор'],
        'required_parameter': True,
        'data_type': str
    },
    'EngineType': {
        'allowed_values': ['Бензин', 'Дизель', 'Электро', 'Болотоход', 'Водомёт'],
        'required_parameter': True,
        'data_type': str
    },
    'Power': {
        'allowed_values': None,
        'required_parameter': True,
        'data_type': float
    },
    'EngineCapacity': {
        'allowed_values': None,
        'required_parameter': False,
        'data_type': int
    },
    'FuelFeed': {
        'allowed_values': ['Карбюратор', 'Инжектор'],
        'required_parameter': False,
        'data_type': str
    },
    'DriveType': {
        'allowed_values': ['Цепь', 'Ремень', 'Кардан'],
        'required_parameter': False,
        'data_type': str
    },
    'Stroke': {
        'allowed_values': [2, 4],
        'required_parameter': False,
        'data_type': str
    },
    'Transmission': {
        'allowed_values': ['Механика', 'Автомат', 'Робот', 'Вариатор'],
        'required_parameter': False,
        'data_type': str
    },
    'NumberOfGears': {
        'allowed_values': ['3', '4', '5', '6'],
        'required_parameter': False,
        'data_type': str
    },
    'EngineCooling': {
        'allowed_values': ['Воздушное', 'Жидкостное'],
        'required_parameter': False,
        'data_type': str
    },
    'Cylinders': {
        'allowed_values': ['1', '2', '3', '4', '6'],
        'required_parameter': False,
        'data_type': str
    },
    'CylindersPosition': {
        'allowed_values': ['V-образное', 'Оппозитное', 'Рядное'],
        'required_parameter': False,
        'data_type': str
    },
    'TopSpeed': {
        'allowed_values': None,
        'required_parameter': False,
        'data_type': int
    },
    'BatteryCapacity': {
        'allowed_values': None,
        'required_parameter': False,
        'data_type': int
    },
    'ElectricRange': {
        'allowed_values': None,
        'required_parameter': False,
        'data_type': int
    },
    'ChargingTime': {
        'allowed_values': None,
        'required_parameter': False,
        'data_type': int
    },
    'PersonCapacity': {
        'allowed_values': None,
        'required_parameter': False,
        'data_type': int
    },
    'TrackWidth': {
        'allowed_values': None,
        'required_parameter': False,
        'data_type': int
    },
    'FloorType': {
        'allowed_values': ['Натяжное', 'Надувное', 'Реечное', 'С жесткими пайолами', 'Килевое',
                            'С жесткими пайолами и килем', 'С надувным килем', 'Реечное с надувным килем',
                            'Килевое с надувным дном низкого давления', 'С надувным дном высокого давления',
                            'С надувным дном низкого давления', 'Стеклопластиковое', 'Алюминиевое', 'Другое'],
        'required_parameter': False,
        'data_type': str
        },
    'Length': {
        'allowed_values': None,
        'required_parameter': False,
        'data_type': float
    },
    'Width': {
        'allowed_values': None,
        'required_parameter': False,
        'data_type': float
    },
    'TransomHeight': {
        'allowed_values': None,
        'required_parameter': False,
        'data_type': int
    },
    'Weight': {
        'allowed_values': None,
        'required_parameter': False,
        'data_type': int
    },
    'SeatingCapacity': {
        'allowed_values': None,
        'required_parameter': False,
        'data_type': int
    },
    'MaxPower': {
        'allowed_values': None,
        'required_parameter': False,
        'data_type': int
    },
    'Material': {
        'allowed_values': ['Алюминий', 'Дюралюминий', 'Сталь', 'Пластик', 'Стеклопластик', 'Дерево', 'Кевлар', 'Алюминий и стеклопластик', 'Другое'],
        'required_parameter': False,
        'data_type': str
    },
    'TrailerIncluded': {
        'allowed_values': ['Нет', 'Да'],
        'required_parameter': False,
        'data_type': str
    },
    'EngineIncluded': {
        'allowed_values': ['Нет', 'Да'],
        'required_parameter': False,
        'data_type': str
    },
    'EngineMake': {
        'allowed_values': None,
        'required_parameter': False,
        'data_type': str
    },
    'EngineYear': {
        'allowed_values': None,
        'required_parameter': False,
        'data_type': int
    },
    'EngineWeight': {
        'allowed_values': None,
        'required_parameter': False,
        'data_type': int
    },
    'ShaftLength': {
        'allowed_values': None,
        'required_parameter': False,
        'data_type': int
    },
    'Control': {
        'allowed_values': ['Дистанционное', 'Румпельное', 'Румпельно-дистанционное'],
        'required_parameter': False,
        'data_type': str
    },
    'StartingSystem': {
        'allowed_values': ['Ручной', 'Электростартер', 'Ручной и электростартер'],
        'required_parameter': False,
        'data_type': str
    },
    'Availability': {
        'allowed_values': ['В наличии', 'Под заказ'],
        'required_parameter': True,
        'data_type': str
    },
    'Condition': {
        'allowed_values': ['Новое', 'Б/у', 'На запчасти'],
        'required_parameter': True,
        'data_type': str
    },
    'Kilometrage': {
        'allowed_values': None,
        'required_parameter': False,
        'data_type': int
    },
    'TechnicalPassport': {
        'allowed_values': ['Оригинал', 'Дубликат', 'Электронный', 'Нет'],
        'required_parameter': False,
        'data_type': str
    },
    'Owners': {
        'allowed_values': ['1', '2', '3', '4+'],
        'required_parameter': False,
        'data_type': str
    },
    'VIN': {
        'allowed_values': None,
        'required_parameter': False,
        'data_type': str
    },
    'AdditionalOptions': {
        'allowed_values': ['Электростартер', 'Антиблокировочная система (ABS)', 'Трэкшн-контроль (TCS)', 'Система «старт-стоп»', 'Ветровое стекло', 'Кофр'],
        'required_parameter': False,
        'data_type': str
    },
    'ImageUrls': {
        'allowed_values': None,
        'required_parameter': False,
        'data_type': str
    },
    'ImageNames': {
        'allowed_values': None,
        'required_parameter': False,
        'data_type': str
    },
    'VideoFileURL': {
        'allowed_values': None,
        'required_parameter': False,
        'data_type': str
    },
    'VideoURL': {
        'allowed_values': None,
        'required_parameter': False,
        'data_type': str
    }
}















