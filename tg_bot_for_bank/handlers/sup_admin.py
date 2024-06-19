from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.filters import StateFilter

from tg_bot_for_bank.db.database_handler import add_user
from tg_bot_for_bank.filters.name_filter import IsFIO
from tg_bot_for_bank.filters.user_exists_filter import UserExist
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove
from tg_bot_for_bank.keyboards.simple_row import make_row_keyboard, contact_keyboard
from tg_bot_for_bank.sender import send_to_admin

sup_admin_router = Router()

@sup_admin_router.message(Command("start"))
async def cmd_start(message: types.Message):
    kb = [
        [types.KeyboardButton(text='Text1'), types.KeyboardButton(text='Text2')]
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Выбери кнопку"
    )
    await message.answer("Hello!", reply_markup=keyboard)


@sup_admin_router.message(Command(commands=["cancel"]))
@sup_admin_router.message(F.text.lower() == "отмена")
async def cmd_cancel(message: Message, state: FSMContext):
    # if EntryState.name_entry:
    #     await state.clear()
    #     await message.answer(
    #         text="Действие отменено",
    #     )
    # else:
    #     await message.answer(
    #         text="Нечего отменять",
    #     )
    pass

@sup_admin_router.message(UserExist(user_exist=True))
async def name_entry_incorrectly(message: Message):
    await message.reply("Приветствую.\nВы уже авторизованный пользователь.")


@sup_admin_router.message(StateFilter("EntryState:name_entry", "EntryState:name_entry_2"))
async def name_entry_incorrectly(message: Message):
    await message.reply("Сообщение не соответствует формату 'Фамилия Имя Отчество'.")
