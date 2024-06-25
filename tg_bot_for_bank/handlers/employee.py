import asyncio

from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message
from aiogram.utils.chat_action import ChatActionSender

from tg_bot_for_bank.keyboards.simple_row import employee_keyboard, make_row_keyboard, make_row_inline_keyboard_mutiple
from tg_bot_for_bank.services.message_deleter import delete_messages
from tg_bot_for_bank.services.search_parser import search_belarusbank

employee_router = Router()


class ActionState(StatesGroup):
    start_state = State()

    search_state = State()
    search_entr_state = State()
    search_right_state = State()
    search_left_state = State()

@employee_router.message(ActionState.start_state)
async def start_message_main(message: Message, state: FSMContext):
    await message.answer(
        text=f"Вы находитесь в <b>Главном меню</b>.\nВыберите действие 👇",
        parse_mode='HTML',
        reply_markup=employee_keyboard()
    )

# Обработка кнопки "Поиск по Базе Знаний"
@employee_router.message(F.text.lower() == "🔍 поиск по базе знаний")
async def base_search(message: Message, state: FSMContext):
    await state.clear()

    await state.set_state(ActionState.search_state)

    message_ids_to_delete = [message.message_id - i for i in range(2)]
    await delete_messages(message.chat.id, message_ids_to_delete)

    await message.answer(
        text="Введите запрос для поиска в Базе Знаний 👇",
        reply_markup=make_row_keyboard(["❌ Отмена"])
    )

@employee_router.message(
    F.text.lower() == "❌ отмена",
    ActionState.search_state
)
async def cancle_buttons(message: Message, state: FSMContext):
    message_ids_to_delete = [message.message_id - i for i in range(0, 2)]
    await delete_messages(message.chat.id, message_ids_to_delete)

    await start_message_main(message, state)


@employee_router.message(
    F.text,
    ActionState.search_state,
    flags={"long_operation": "typing"}
)
async def base_search_entr(message: Message, state: FSMContext):
    current_state = await state.get_state()

    if current_state != ActionState.search_right_state and current_state != ActionState.search_left_state:
        query = message.text
        await state.update_data(query=query)

        # Статус "typing" начинается до выполнения долгой операции
        async with ChatActionSender(action="typing", chat_id=message.chat.id, bot=message.bot):
            result_query = await search_belarusbank(query)
            await state.update_data(result_query=result_query)

        await state.update_data(results_page=0)
        await state.update_data(results_page_max=len(result_query) - 1)

    # Статус "typing" начинается до выполнения долгой операции
    async with ChatActionSender(action="typing", chat_id=message.chat.id, bot=message.bot):

        data = await state.get_data()
        results_page_max = data.get('results_page_max')
        results_page = data.get('results_page')
        result_query = data.get('result_query')
        query = data.get('query')

        message_ids_to_delete = [message.message_id - i for i in range(1)]
        await delete_messages(message.chat.id, message_ids_to_delete)

        if len(result_query) > 1:
            keyboard_items = [
                [{'text': '👈',
                  'callback_data': "getLeftResults"},
                 {'text': f'📄 {results_page+1} / {results_page_max+1} 📄'},
                 {'text': '👉',
                  'callback_data': "getRightResults"}]
            ]

            await message.answer(
                text=f"Результат поиска по запросу <b>{query}</b>:\n\n"
                     f"{result_query[results_page]}",
                parse_mode='HTML',
                disable_web_page_preview=True,
                reply_markup=make_row_inline_keyboard_mutiple(keyboard_items)
            )
        else:
            await message.answer(
                text=f"Результат поиска по запросу <b>{query}</b>:\n\n"
                     f"{result_query[0]}",
                parse_mode='HTML',
                disable_web_page_preview=True,
                #reply_markup=make_row_inline_keyboard_mutiple([keyboard_items])
            )

    await state.set_state(ActionState.search_entr_state)
    message_ids_to_delete = [message.message_id - i for i in range(1, 2)]
    await delete_messages(message.chat.id, message_ids_to_delete)

    await start_message_main(message, state)

@employee_router.callback_query(F.data == "getRightResults")
async def base_search_entr_callback_Right(callback: types.CallbackQuery, state: FSMContext):
    message_ids_to_delete = [callback.message.message_id - i for i in range(2)]
    await delete_messages(callback.message.chat.id, message_ids_to_delete)

    data = await state.get_data()
    results_page = data.get('results_page') + 1
    if results_page > data.get('results_page_max'):
        results_page = 0
    await state.update_data(results_page=results_page)

    await state.set_state(ActionState.search_right_state)

    await base_search_entr(callback.message, state)


@employee_router.callback_query(F.data == "getLeftResults")
async def base_search_entr_callback_Right(callback: types.CallbackQuery, state: FSMContext):
    message_ids_to_delete = [callback.message.message_id - i for i in range(2)]
    await delete_messages(callback.message.chat.id, message_ids_to_delete)

    data = await state.get_data()
    results_page = data.get('results_page') - 1
    if results_page < 0:
        results_page = data.get('results_page_max')
    await state.update_data(results_page=results_page)

    await state.set_state(ActionState.search_left_state)

    await base_search_entr(callback.message, state)
