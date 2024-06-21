import logging

from peewee import IntegrityError, DoesNotExist

from tg_bot_for_bank.db.models import *

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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
