from zipfile import ZipFile

def convert_bytes(size):
    """Конвертер байт в большие единицы"""
    if size < 1000:
        return f'{size} B'
    elif 1000 <= size < 1000000:
        return f'{round(size / 1024)} KB'
    elif 1000000 <= size < 1000000000:
        return f'{round(size / 1048576)} MB'
    else:
        return f'{round(size / 1073741824)} GB'

with ZipFile('desktop.zip', 'r') as zip_file:
    info = zip_file.infolist()
    name = zip_file.namelist()
    # get = zip_file.getinfo()
    # print(*info, sep='\n')
    # print()
    print(*name, sep='\n')
    # print()
    # print(get)
    for i in range(len(info)):
        ident = '  '
        if info[i].is_dir():
            amount = info[i].filename.count('/')
            # print(amount)
            print(ident * (amount - 1) + info[i].filename)
        else:
            print(ident * info[i].filename.count('//') + info[i].filename + ' ' + convert_bytes(info[i].file_size))