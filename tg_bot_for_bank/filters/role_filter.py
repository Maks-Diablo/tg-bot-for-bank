from typing import Any

from aiogram import Dispatcher, types
from aiogram.filters import BaseFilter

from tg_bot_for_bank.db.models import Employees, Positions  # Assuming models are defined elsewhere


class RoleFilter(BaseFilter):
    key = 'is_role'

    def __init__(self, role):  # Add an __init__ method to accept the role argument
        self.role = role  # Store the role for later use

    async def __call__(self, message: types.Message, **kwargs) -> str | bool | Any:
        user_id = message.from_user.id

        # Fetch user's position from the database
        try:
            employee = Employees.get(Employees.tg_id == user_id)
            position_title = employee.position_id.title  # Access position title
        except Employees.DoesNotExist:
            position_title = "Guest"
            return position_title  # User not found in database

        # Check if the user's position matches the required role
        return position_title == self.role
