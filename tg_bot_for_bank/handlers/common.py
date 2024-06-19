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

router = Router()


class EntryState(StatesGroup):
    name_entr = State()
    name_entry = State()
    name_entry_2 = State()
    name_success = State()


@router.message(
    Command(commands=["start"]),
    UserExist(user_exist=False)
)
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()

    full_text = message.text
    command, *args = full_text.split()

    await message.answer(
        text="Приветствую.\n"
             "Для продолжения предоставьте свой номер телефона.",
        reply_markup=await contact_keyboard(),
        request_contact=True
    )

    if args:
        arguments = args[0].split('_')

        await state.update_data(
            tg_id=message.from_user.id,
            lastname=arguments[0],
            firstname=arguments[1],
            patronymic=arguments[2],
            contact_start=arguments[3]
        )

        await state.set_state(EntryState.name_entry)
    else:
        await state.set_state(EntryState.name_entr)
    # else:
    #     await message.reply('Для начала работы с ботом нажмите /start.')
    # await state.set_state(None) с сохранением


@router.message(EntryState.name_entr)
async def name_entr(message: Message, state: FSMContext):
    await message.answer(
        text="Введите ФИО в формате 'Фамилия Имя Отчество'.",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(EntryState.name_entry_2)


@router.message(
    EntryState.name_entry,
    F.contact,
)
async def name_entry(message: Message, state: FSMContext):
    user_data = await state.get_data()
    user_name = f"{user_data.get('lastname')} {user_data.get('firstname')} {user_data.get('patronymic')}"

    await message.answer(
        text=f"Данные введены верно?\n<i>{user_name}</i>",
        parse_mode='HTML',
        reply_markup=make_row_keyboard(
            ["Да", "Нет"]
        )
    )
    await state.update_data(
        contact=message.contact
    )
    await state.set_state(EntryState.name_success)


@router.message(
    EntryState.name_entry_2,
    IsFIO(is_fio=True)
)
async def name_entry_2(message: Message, state: FSMContext):
    await message.answer(
        text=f"Данные введены верно?\n<i>{message.text}</i>",
        parse_mode='HTML',
        reply_markup=make_row_keyboard(
            ["Да", "Нет"]
        )
    )
    name = message.text.split()

    user_data = await state.get_data()
    update_data = {
        'tg_id': message.from_user.id,
        'lastname': name[0],
        'firstname': name[1],
        'patronymic': name[2]
    }

    if user_data.get('contact'):
        update_data['contact'] = user_data['contact']

    await state.update_data(**update_data)

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

    user_data = await state.get_data()
    # создание записи в бд
    #add_user(user_data)
    # отправка данных
    await send_to_admin(user_data)

    await state.clear()


@router.message(
    EntryState.name_success,
    F.text == "Нет"
)
async def name_entry_not_success(message: Message, state: FSMContext):
    # await state.clear()
    # await message.answer(
    #     text="Обратитесь к администратору.",
    #     reply_markup=ReplyKeyboardRemove()
    # )
    # await state.clear()
    await message.answer(
        text="Повторите ввод ФИО.\n"
             "(Ввод в формате: Иванов Иван Иванович).",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(EntryState.name_entry_2)


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


@router.message(UserExist(user_exist=True))
async def name_entry_incorrectly(message: Message):
    await message.reply("Приветствую.\nВы уже авторизованный пользователь.")


@router.message(StateFilter("EntryState:name_entry", "EntryState:name_entry_2"))
async def name_entry_incorrectly(message: Message):
    await message.reply("Сообщение не соответствует формату 'Фамилия Имя Отчество'.")
