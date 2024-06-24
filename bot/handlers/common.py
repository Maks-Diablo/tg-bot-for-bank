from aiogram import F, Router
from aiogram.filters import Command
from aiogram.filters import StateFilter

from bot.db.database_handler import add_user, get_user_role_from_db
from bot.filters.name_filter import IsFIO
from bot.filters.user_exists_filter import UserExist
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove
from bot.keyboards.simple_row import make_row_keyboard, contact_keyboard, sup_admin_keyboard
from bot.services.message_deleter import delete_messages
from bot.services.sender import send_to_admin
from bot.qr.conversion import convert_filename_to_name
from bot.handlers.auth_user import cmd_start as auth_user_start

common_router = Router()


@common_router.message(
    Command(commands=["start"]),
)
async def cmd_start(message: Message, state: FSMContext):
    if await UserExist(False)(message):
        await auth_user_start(message, state)
    else:
        role = await get_user_role_from_db(message.from_user.id)
        await message.reply(f"Приветствую.\nВаша роль - <i>{role}</i>.", parse_mode='HTML')
        await message.answer("Выберите действие 👇",
                            reply_markup=sup_admin_keyboard(),
                             disable_notification=True)
# @common_router.message(UserExist(user_exist=True))
# async def name_entry_incorrectly(message: Message):
#     await message.reply("Приветствую.\nВы уже авторизованный пользователь.")
