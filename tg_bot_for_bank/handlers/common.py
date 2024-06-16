from aiogram import F, Router
from aiogram.filters import Command
from aiogram.filters import StateFilter
from filters.NameFilter import IsFIO
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove

router = Router()


class EntryState(StatesGroup):
    name_entry = State()


@router.message(Command(commands=["start"]))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        text="Приветствую.\n"
             "Введите своё ФИО и ожидайте одобрения администратором.\n\n"
             "(Ввод в формате: Иванов Иван Иванович).",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(EntryState.name_entry)


@router.message(
    EntryState.name_entry,
    IsFIO(is_fio=True)
)
async def name_entry(message: Message, state: FSMContext):
    await message.reply(
        text="Спасибо. Ожидайте ответ администартора.",
    )
    await state.clear()


@router.message(Command(commands=["cancel"]))
@router.message(F.text.lower() == "отмена")
async def cmd_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        text="Действие отменено",
    )


@router.message(StateFilter("EntryState:name_entry"))
async def name_entry_incorrectly(message: Message):
    await message.reply("Сообщение не соответствует формату 'Фамилия Имя Отчество'.")