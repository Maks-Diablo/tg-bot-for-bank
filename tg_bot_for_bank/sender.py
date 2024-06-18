import logging
from aiogram import Bot

from tg_bot_for_bank.config_reader import config
from tg_bot_for_bank.db.models import Employees

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(config.bot_token.get_secret_value())

async def send_to_admin(user_data: dict):
    ADMIN_CHAT_ID = Employees.select().where(Employees.position_id == 2).get().tg_id

    try:
        message = (
            "Новые данные от пользователя:\n"
            f"Имя: {user_data.get('name')}\n"
        )
        await bot.send_message(chat_id=ADMIN_CHAT_ID, text=message)
        await bot.send_contact(
            chat_id=ADMIN_CHAT_ID,
            first_name=user_data.get('contact').first_name,
            phone_number=user_data.get('contact').phone_number
        )

        logger.info("Сообщение отправлено администратору.")
    except Exception as e:
        logger.error(f"Ошибка при отправке сообщения администратору: {e}")

