import logging
from aiogram import Bot

from tg_bot_for_bank.config_reader import config
from tg_bot_for_bank.db.database_handler import add_user_msg_request
from tg_bot_for_bank.db.models import Employees
from tg_bot_for_bank.keyboards.simple_row import make_row_inline_keyboard

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
        message_text = (
            "Новый запрос на авторизацию:\n"
            f"<b>{user_data.get('lastname')} {user_data.get('firstname')} {user_data.get('patronymic')}</b>"
        )
        message = await bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            parse_mode='HTML',
            text=message_text,
        )
        c_message = await bot.send_contact(
            chat_id=ADMIN_CHAT_ID,
            first_name=user_data.get('contact').first_name,
            phone_number=user_data.get('contact').phone_number,
            reply_markup=make_row_inline_keyboard(keyboard_items),
            disable_notification=True
        )

        msg_id = message.message_id
        msg_c_id = c_message.message_id
        tg_id = user_data.get('tg_id')
        await add_user_msg_request(tg_id, msg_id, msg_c_id)

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
