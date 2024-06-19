import logging

from peewee import IntegrityError, DoesNotExist

from tg_bot_for_bank.db.models import *

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Класс для операций с базой данных
def add_user(user_data):
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


class DatabaseManager:
    pass

    # def update_email(self, username, new_email):
    #     try:
    #         user = Employees.get(Employees.username == username)
    #         user.email = new_email
    #         user.save()
    #         print(f"Email пользователя {username} успешно обновлён.")
    #         return user
    #     except DoesNotExist:
    #         print(f"Пользователь с именем {username} не найден.")
    #         logger.error(f"Ошибка при отправке сообщения администратору: {e}")
    #         return None
