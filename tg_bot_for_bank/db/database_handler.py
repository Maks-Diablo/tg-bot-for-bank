import logging

from peewee import IntegrityError, DoesNotExist

from tg_bot_for_bank.db.models import *

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def get_old_requests_from_db():
    try:
        # Handle the case where no requests are found
        query = (Requests
                 .select()
                 .join(Employees, on=(Requests.user_id == Employees.tg_id))
                 .join(Positions, on=(Employees.position_id == Positions.id))
                 .where(Positions.title == 'UNKNOW'))

        result = [(request.user_id, request.msg_id, request.msg_c_id) for request in query]
        logger.info(f"Возврат пользователей.")
        return result
    except DoesNotExist:
        logger.error(f"Ошибка возврата пользователей.")
        return None


async def un_block_empolyee(FIO, type):
    FIO = FIO.split()
    if type == 'block':
        position = 6
    else:
        position = 3
    try:
        try:
            employee = Employees.get(Employees.lastname == FIO[0], Employees.firstname == FIO[1],
                                     Employees.patronymic == FIO[2])
            employee.position_id = position
            employee.save()

            logger.info(f"Пользователь {FIO} успешно заблокирован.")
            return True
        except DoesNotExist:
            logger.error(f"Пользователь {FIO} не заблокирован (возможно не найден).")
            return False
    except Exception as ex:
        logger.error(f"Ошибка при разблокировании\блокировании пользователя {FIO}: {ex}")
        return False


async def get_all_employees_from_db():
    try:
        employees = Employees.select().join(Positions).where(Positions.title.in_(["Administrator", "Employee"]))
        return employees
    except DoesNotExist:
        return None


async def get_all_employees_list_from_db(positions):
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


async def get_user_tg_id_from_db(fio: str):
    fio = fio.split()
    try:
        employee = Employees.get(Employees.firstname == fio[1], Employees.lastname == fio[0],
                                 Employees.patronymic == fio[2])
        tg_id = employee.tg_id
        return tg_id
    except DoesNotExist:
        return ''


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


async def add_user_msg_request(tg_id, msg_id, msg_c_id):
    Requests.create(
        msg_id=msg_id,
        msg_c_id=msg_c_id,
        user_id=tg_id
    )


async def update_position_id(tg_id, position_title):
    try:
        position = Positions.get(Positions.title == position_title)
        user = Employees.get(Employees.tg_id == tg_id)

        user.position_id = position.id
        user.save()

        logger.info(f"Position пользователя {tg_id} успешно обновлён на '{position}'.")

        return True
    except DoesNotExist:
        logger.error(f"Пользователь с TG_ID {tg_id} не найден.")
        return False
