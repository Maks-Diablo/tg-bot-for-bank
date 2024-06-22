import logging

from peewee import IntegrityError, DoesNotExist

from tg_bot_for_bank.db.models import *

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def get_all_employees_from_db(positions):
    try:
        query = Employees.select().join(Positions).where(Positions.title.in_(positions))
        # Выполнение запроса и вывод результатов
        employees = query.execute()
        employees_list = ''
        employees_arr = []

        for index, employee in enumerate(employees, start=1):
            if employee.tg_username:
                # Формируем ссылку, если tg_firstname не null
                employees_list += f"<a href='https://t.me/{employee.tg_username}'>{index}. {employee.lastname} {employee.firstname} {employee.patronymic}</a>\n"
            else:
                # Если tg_firstname отсутствует, просто выводим текст без ссылки
                employees_list += f"{index}. {employee.lastname} {employee.firstname} {employee.patronymic}\n"

            if index % 20 == 0:
                employees_arr.append(employees_list)
                employees_list = ''

        # Добавляем оставшиеся элементы, если они есть
        if employees_list:
            employees_arr.append(employees_list)

        return employees_arr
    except DoesNotExist:
        return ["Список пуст."]


async def get_user_FIO_from_db(user_id: int):
    try:
        employee = Employees.get(Employees.tg_id == user_id)
        lastname = employee.lastname
        firstname = employee.firstname
        patronymic = employee.patronymic
        return lastname, firstname, patronymic
    except DoesNotExist:
        return ''


async def get_user_role_from_db(user_id: int) -> str:
    try:
        employee = Employees.get(Employees.tg_id == user_id)
        position = employee.position_id
        return position.title
    except DoesNotExist:
        return 'Guest'


async def add_user(user_data):
    try:
        user = Employees.create(
            tg_id=user_data.get('tg_id'),
            tg_username=user_data.get('tg_username'),
            position_id=5,
            lastname=user_data.get('lastname'),
            firstname=user_data.get('firstname'),
            patronymic=user_data.get('patronymic')
        )
        logger.info(f"Пользователь {user.tg_id} успешно добавлен.")
        return user
    except IntegrityError:
        logger.error(f"Пользователь {user_data.get('tg_id')} уже существует.")
        return None


async def update_position_id(tg_id, position_title):
    try:
        position = Positions.get(Positions.title == position_title)
        user = Employees.get(Employees.tg_id == tg_id)

        user.position_id = position.id
        user.save()

        logger.info(f"Position пользователя {tg_id} успешно обновлён на '{position}'.")
    except DoesNotExist:
        logger.error(f"Пользователь с TG_ID {tg_id} не найден.")
