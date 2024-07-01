from aiogram import Router
from aiogram.filters import Command

from tg_bot_for_bank.db.database_handler import get_user_role_from_db
from tg_bot_for_bank.filters.user_exists_filter import UserExist
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove
from tg_bot_for_bank.keyboards.simple_row import sup_admin_keyboard, employee_keyboard, admin_keyboard
from tg_bot_for_bank.handlers.auth_user import cmd_start as auth_user_start
from tg_bot_for_bank.services.message_deleter import delete_messages

common_router = Router()


@common_router.message(
    Command(commands=["start"]),
)
async def cmd_start(message: Message, state: FSMContext):
    if await UserExist(False)(message):
        await auth_user_start(message, state)
    else:
        role = await get_user_role_from_db(message.from_user.id)

        if role == 'Super-Administrator':
            keyboard = sup_admin_keyboard()
        elif role == 'Employee':
            keyboard = employee_keyboard()
        elif role == 'Administrator':
            keyboard = admin_keyboard()
        else:
            keyboard = ReplyKeyboardRemove()

        await message.reply(f"Приветствую.\nВаша роль - <i>{role}</i>.", parse_mode='HTML')
        await message.answer("Выберите действие 👇",
                             reply_markup=keyboard,
                             disable_notification=True)


async def handle_unhandled_message(message: Message):
    message_ids_to_delete = [message.message_id - i for i in range(1)]
    await delete_messages(message.chat.id, message_ids_to_delete)


async def start_message_main_employee(message: Message):
    await message.answer(
        text=f"Вы находитесь в <b>Главном меню</b>.\nВыберите действие 👇",
        parse_mode='HTML',
        reply_markup=employee_keyboard()
    )


async def start_message_main_admin(message: Message):
    await message.answer(
        text=f"Вы находитесь в <b>Главном меню</b>.\nВыберите действие 👇",
        parse_mode='HTML',
        reply_markup=admin_keyboard()
    )


async def start_message_main_sup_admin(message: Message):
    # await state.clear()
    await message.answer(
        text=f"Вы находитесь в <b>Главном меню</b>.\nВыберите действие 👇",
        parse_mode='HTML',
        reply_markup=sup_admin_keyboard()
    )
