# Словарь для замены кириллических символов на английские эквиваленты
conversion_dict = {
    "А": "F", "Б": "1", "В": "D", "Г": "U", "Д": "L", "Е": "T", "Ё": "2", "Ж": "3", "З": "P", "И": "B",
    "Й": "Q", "К": "R", "Л": "K", "М": "V", "Н": "Y", "О": "J", "П": "G", "Р": "H", "С": "C", "Т": "N",
    "У": "E", "Ф": "A", "Х": "4", "Ц": "W", "Ч": "X", "Ш": "I", "Щ": "O", "Ъ": "5", "Ы": "S", "Ь": "M",
    "Э": "5", "Ю": "6", "Я": "Z"
}

# Словарь для обратной конвертации
reverse_conversion_dict = {v: k for k, v in conversion_dict.items()}

# Функция для конвертации имени в формат Фамилия_Имя_Отчество
def convert_name_to_filename(name):
    converted = []
    parts = name.split()
    if len(parts) >= 3:
        surname = parts[0]
        firstname = parts[1]
        middlename = parts[2]
        converted.append(convert_string(surname, conversion_dict))
        converted.append(convert_string(firstname, conversion_dict))
        converted.append(convert_string(middlename, conversion_dict))
    return '_'.join(converted)

# Функция для обратной конвертации Фамилия_Имя_Отчество в Фамилия Имя Отчество
def convert_filename_to_name(filename):
    parts = filename.split('_')
    if len(parts) >= 3:
        surname = reverse_convert_string(parts[0], reverse_conversion_dict)
        firstname = reverse_convert_string(parts[1], reverse_conversion_dict)
        middlename = reverse_convert_string(parts[2], reverse_conversion_dict)
        return format_name(f"{surname} {firstname} {middlename}")
    return filename

# Функция для конвертации строки по заданному словарю
def convert_string(s, conversion_dict):
    converted = []
    for char in s:
        if char.upper() in conversion_dict:
            converted.append(conversion_dict[char.upper()])
        else:
            converted.append(char)
    return ''.join(converted)

# Функция для обратной конвертации строки
def reverse_convert_string(s, reverse_conversion_dict):
    converted = []
    for char in s:
        if char.upper() in reverse_conversion_dict:
            converted.append(reverse_conversion_dict[char.upper()])
        else:
            converted.append(char)
    return ''.join(converted)


def format_name(full_name):
    # Разбиваем полное имя на компоненты: фамилия, имя, отчество
    parts = full_name.split()

    # Если в строке меньше трех слов, возвращаем исходную строку
    if len(parts) < 3:
        return full_name

    # Преобразуем каждое слово: первую букву в верхний регистр, остальные - в нижний
    formatted_parts = [part.capitalize() for part in parts]

    # Возвращаем объединенную строку
    return ' '.join(formatted_parts)

