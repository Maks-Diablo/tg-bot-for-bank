import logging
from aiogram import Bot

from bot.config_reader import config
from bot.db.models import Employees
from bot.keyboards.simple_row import make_row_inline_keyboard

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(config.bot_token.get_secret_value())


async def send_to_admin(user_data: dict):
    ADMIN_CHAT_ID = Employees.select().where(Employees.position_id == 2).get().tg_id

    keyboard_items = [
        {'text': 'Принять',
         'callback_data': f"accept_{user_data.get('tg_id')}"},
        {'text': 'Отказать',
         'callback_data': f"reject_{user_data.get('tg_id')}"},
    ]

    try:
        message = (
            "Новый запрос на авторизацию:\n"
            f"<b>{user_data.get('lastname')} {user_data.get('firstname')} {user_data.get('patronymic')}</b>"
        )
        await bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            parse_mode='HTML',
            text=message,
        )
        await bot.send_contact(
            chat_id=ADMIN_CHAT_ID,
            first_name=user_data.get('contact').first_name,
            phone_number=user_data.get('contact').phone_number,
            reply_markup=make_row_inline_keyboard(keyboard_items),
            disable_notification=True
        )

        logger.info("Сообщение отправлено администратору.")
    except Exception as e:
        logger.error(f"Ошибка при отправке сообщения администратору: {e}")


async def send_to(tg_id, message):
    try:
        await bot.send_message(
            chat_id=tg_id,
            parse_mode='HTML',
            text=message,
        )

        logger.info("Сообщение отправлено пользователю.")
    except Exception as e:
        logger.error(f"Ошибка при отправке сообщения пользователю: {e}")
