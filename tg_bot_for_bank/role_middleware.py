from aiogram import types
from aiogram.dispatcher.middlewares.base import BaseMiddleware
from peewee import DoesNotExist

from tg_bot_for_bank.db.models import Employees

class RoleMiddleware(BaseMiddleware):
    async def on_process_message(self, message: types.Message, data: dict):
        # Здесь предполагается, что в базе данных есть функция get_user_role, которая возвращает роль пользователя
        user_role = get_user_role_from_db(message.from_user.id)

        if user_role == 'admin':
            data['user_role'] = 'admin'
        else:
            data['user_role'] = 'employee'

async def get_user_role_from_db(user_id: int) -> str:
    try:
        employee = Employees.get(Employees.tg_id == user_id)
        position = employee.position_id
        return position.title
    except DoesNotExist:
        return 'Guest'
