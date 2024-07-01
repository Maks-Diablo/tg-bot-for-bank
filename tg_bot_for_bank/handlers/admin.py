from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message

from tg_bot_for_bank.handlers.common import start_message_main_admin, handle_unhandled_message
from tg_bot_for_bank.keyboards.simple_row import make_row_keyboard
from tg_bot_for_bank.services.base_search_handlers import base_search_entr_handler, \
    base_search_entr_callback_right_handler, base_search_entr_callback_left_handler
from tg_bot_for_bank.services.information_handlers import information_message_admin, information_message_entry, \
    information_message_success
from tg_bot_for_bank.services.message_deleter import delete_messages

admin_router = Router()


class ActionState(StatesGroup):
    start_state = State()

    inf_msg = State()
    inf_msg_entr = State()
    inf_msg_success = State()

    search_state = State()
    search_entr_state = State()
    search_right_state = State()
    search_right_old_state = State()
    search_left_state = State()
    search_left_old_state = State()


@admin_router.message(ActionState.start_state)
async def start_message_main(message: Message):
    await start_message_main_admin(message)


# Нажатие Информирование
@admin_router.message(F.text.lower() == "📢 информирование")
async def information_message(message: Message, state: FSMContext):
    await information_message_admin(message, state, ActionState)


@admin_router.message(
    F.text.lower() == "❌ отмена",
    ActionState.inf_msg_entr
)
@admin_router.message(
    F.text.lower() == "❌ отмена",
    ActionState.inf_msg_success
)
async def information_message_cancel(message: Message, state: FSMContext):
    await state.clear()
    message_ids_to_delete = [message.message_id - i for i in range(2)]
    await delete_messages(message.chat.id, message_ids_to_delete)

    await start_message_main_admin(message)


@admin_router.message(ActionState.inf_msg_entr, F.text)
async def admin_information_message_entry(message: Message, state: FSMContext):
    await information_message_entry(message, state, ActionState)


@admin_router.message(ActionState.inf_msg_success, F.text.lower() == "✅ подтвердить")
async def admin_information_message_success(message: Message, state: FSMContext):
    await information_message_success(message, state, ActionState)


@admin_router.message(ActionState.inf_msg_success, F.text.lower() == "🔄 изменить")
async def admin_information_message_re_enter(message: Message, state: FSMContext):
    await information_message(message, state)


# Обработка кнопки "Поиск по Базе Знаний"
@admin_router.message(F.text.lower() == "🔍 поиск по базе знаний")
async def base_search(message: Message, state: FSMContext):
    await state.clear()

    await state.set_state(ActionState.search_state)

    message_ids_to_delete = [message.message_id - i for i in range(2)]
    await delete_messages(message.chat.id, message_ids_to_delete)

    await message.answer(
        text="Введите запрос для поиска в Базе Знаний 👇",
        reply_markup=make_row_keyboard(["❌ Отмена"])
    )


@admin_router.message(
    F.text,
    ActionState.search_state,
    flags={"long_operation": "typing"}
)
async def admin_base_search_entr(message: Message, state: FSMContext):
    await base_search_entr_handler(message, state, ActionState, start_message_main)


@admin_router.callback_query(lambda c: c.data and c.data.startswith('getRightResults_'))
async def admin_base_search_entr_callback_right(callback: types.CallbackQuery, state: FSMContext):
    await base_search_entr_callback_right_handler(callback, state, ActionState, start_message_main)


@admin_router.callback_query(lambda c: c.data and c.data.startswith('getLeftResults_'))
async def admin_base_search_entr_callback_left(callback: types.CallbackQuery, state: FSMContext):
    await base_search_entr_callback_left_handler(callback, state, ActionState, start_message_main)


# Обработчик необработанных сообщений
@admin_router.message()
async def admin_handle_unhandled_message(message: types.Message):
    await handle_unhandled_message(message)
