import qrcode
from conversion import convert_name_to_filename, convert_filename_to_name

# Данные сотрудников
employees = [
    {"name": "Иванов Иван Иванович", "phone": "71234567890"},
    {"name": "Петров Петр Петрович", "phone": "79876543210"},
]

# Конвертация данных сотрудников и добавление их в список
employees_conv = []
for emp in employees:
    converted_name = convert_name_to_filename(emp["name"])
    converted_phone = emp["phone"]
    employees_conv.append({"name": converted_name, "phone": converted_phone})


# Функция для генерации URL с данными сотрудника
def generate_url(employee):
    base_url = "https://t.me/for_bank_tg_bot?start="
    employee_data = f"{employee['name']}_{employee['phone']}"
    print(f"Ссылка для {employee['name']}: {base_url}{employee_data}")
    return f"{base_url}{employee_data}"


# Генерация QR-кода для каждого сотрудника и сохранение его в файл
for employee in employees_conv:
    url = generate_url(employee)

    # Создание объекта QR-кода
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )

    # Добавление данных в QR-код и сохранение изображения
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill='black', back_color='white')
    img_filename = f"qr_{employee['name']}.png"
    img.save(img_filename)

    print(f"QR код для {employee['name']} сохранён как {img_filename}")

# Пример обратной конвертации для проверки
for emp in employees_conv:
    original_name = convert_filename_to_name(emp["name"])
    print(f"Обратно конвертированное имя для {emp['name']}: {original_name}")
