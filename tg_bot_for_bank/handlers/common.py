from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.filters import StateFilter
from tg_bot_for_bank.filters.NameFilter import IsFIO
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove
from tg_bot_for_bank.keyboards.simple_row import make_row_keyboard, contact_keyboard
from tg_bot_for_bank.sender import send_to_admin

router = Router()


class EntryState(StatesGroup):
    name_entry = State()
    name_success = State()


@router.message(Command(commands=["start"]))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        text="Приветствую.\n"
             "Для продолжения предоставьте свой номер телефона.",
        reply_markup=await contact_keyboard(),
        request_contact=True
    )
    await state.set_state(EntryState.name_entry)
    # await state.set_state(None) с сохранением


@router.message(
    EntryState.name_entry,
    F.contact,
    #IsFIO(is_fio=True)
)
async def name_entry(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        text=f"Данные введены верно?\n<i>{message.text}</i>",
        parse_mode='HTML',
        reply_markup=make_row_keyboard(
            ["Да", "Нет"]
        )
    )
    await state.update_data(
        name=message.text,
        contact=message.contact
    )
    await state.set_state(EntryState.name_success)


@router.message(
    EntryState.name_success,
    F.text == "Да"
)
async def name_entry_success(message: Message, state: FSMContext):
    await message.answer(
        text="Спасибо. Ожидайте ответ администартора.",
        reply_markup=ReplyKeyboardRemove()
    )
    # отправка данных
    user_data = await state.get_data()
    await send_to_admin(user_data)
    print(user_data)

    await state.clear()


@router.message(
    EntryState.name_success,
    F.text == "Нет"
)
async def name_entry_not_success(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        text="Обратитесь к администратору.",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.clear()


@router.message(Command(commands=["cancel"]))
@router.message(F.text.lower() == "отмена")
async def cmd_cancel(message: Message, state: FSMContext):
    if EntryState.name_entry:
        await state.clear()
        await message.answer(
            text="Действие отменено",
        )
    else:
        await message.answer(
            text="Нечего отменять",
        )


@router.message(StateFilter("EntryState:name_entry"))
async def name_entry_incorrectly(message: Message):
    await message.reply("Сообщение не соответствует формату 'Фамилия Имя Отчество'.")
