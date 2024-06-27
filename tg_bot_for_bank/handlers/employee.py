import asyncio

from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message
from aiogram.utils.chat_action import ChatActionSender

from tg_bot_for_bank.keyboards.simple_row import employee_keyboard, make_row_keyboard, make_row_inline_keyboard_mutiple
from tg_bot_for_bank.services.message_deleter import delete_messages, bot
from tg_bot_for_bank.services.search_parser import search_belarusbank

employee_router = Router()


class ActionState(StatesGroup):
    start_state = State()

    search_state = State()
    search_entr_state = State()
    search_right_state = State()
    search_right_old_state = State()
    search_left_state = State()
    search_left_old_state = State()

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

    if current_state != ActionState.search_right_state and current_state != ActionState.search_left_state and current_state != ActionState.search_right_old_state and current_state != ActionState.search_left_old_state:
        message_ids_to_delete = [message.message_id - i for i in range(2)]
        await delete_messages(message.chat.id, message_ids_to_delete)

        query = message.text
        await state.update_data(query=query)

        # Статус "typing" начинается до выполнения долгой операции
        async with ChatActionSender(action="typing", chat_id=message.chat.id, bot=message.bot):
            result_query = await search_belarusbank(query)
            await state.update_data(result_query=result_query)

        await state.update_data(results_page=0)
        await state.update_data(results_page_max=len(result_query) - 1)

    if current_state == ActionState.search_right_old_state or current_state == ActionState.search_left_old_state:
        data = await state.get_data()
        query = data.get('query')
        page = data.get('results_page')

        # Статус "typing" начинается до выполнения долгой операции
        async with ChatActionSender(action="typing", chat_id=message.chat.id, bot=message.bot):
            result_query = await search_belarusbank(query)
            await state.update_data(result_query=result_query)

        await state.update_data(results_page=page)
        await state.update_data(results_page_max=len(result_query) - 1)

    # Статус "typing" начинается до выполнения долгой операции
    async with ChatActionSender(action="typing", chat_id=message.chat.id, bot=message.bot):

        data = await state.get_data()
        results_page_max = int(data.get('results_page_max'))
        results_page = int(data.get('results_page'))
        result_query = data.get('result_query')
        query = data.get('query')
        message_id_list = data.get('message_id_list')
        #message_ids_to_delete = [message.message_id - i for i in range(1)]
        #await delete_messages(message.chat.id, message_ids_to_delete)

        if len(result_query) > 1:
            keyboard_items = [
                [{'text': '👈',
                  'callback_data': f"getLeftResults_{query}_{results_page}_{results_page_max}_{message_id_list}"},
                 {'text': f'📄 {int(results_page)+1} / {int(results_page_max)+1} 📄'},
                 {'text': '👉',
                  'callback_data': f"getRightResults_{query}_{results_page}_{results_page_max}_{message_id_list}"}]
            ]

            if current_state != ActionState.search_right_state and current_state != ActionState.search_left_state and current_state != ActionState.search_left_old_state:
                await message.answer(
                    text=f"Результат поиска по запросу <b>{query}</b>:\n\n{result_query[results_page]}",
                    parse_mode='HTML',
                    disable_web_page_preview=True,
                    reply_markup=make_row_inline_keyboard_mutiple(keyboard_items)
                )
                await start_message_main(message, state)

            else:
                await bot.edit_message_text(
                    f"Результат поиска по запросу <b>{query}</b>:\n\n{result_query[results_page]}",
                    message.chat.id,
                    message_id_list,
                    parse_mode='HTML',
                    disable_web_page_preview=True,
                    reply_markup=make_row_inline_keyboard_mutiple(keyboard_items))


        else:
            await message.answer(
                text=f"Результат поиска по запросу <b>{query}</b>:\n\n"
                     f"{result_query[0]}",
                parse_mode='HTML',
                disable_web_page_preview=True,
            )

    await state.set_state(ActionState.search_entr_state)
    #message_ids_to_delete = [message.message_id - i for i in range(1)]
    #await delete_messages(message.chat.id, message_ids_to_delete)


#@employee_router.callback_query(F.data == "getRightResults")
@employee_router.callback_query(lambda c: c.data and c.data.startswith(('getRightResults_')))
async def base_search_entr_callback_right(callback: types.CallbackQuery, state: FSMContext):
    action, query_callback, page, page_max, m_id = callback.data.split('_')
    data = await state.get_data()
    query = data.get('query')
    if query_callback == query:
        #message_ids_to_delete = [callback.message.message_id - i for i in range(2)]
        #await delete_messages(callback.message.chat.id , message_ids_to_delete)

        data = await state.get_data()
        results_page = int(data.get('results_page')) + 1
        if results_page > data.get('results_page_max'):
            results_page = 0
        await state.update_data(results_page=results_page)
        await state.update_data(message_id_list=callback.message.message_id)

        await state.set_state(ActionState.search_right_state)

        await base_search_entr(callback.message, state)
    else:
        page = int(page)
        page += 1
        if page > int(page_max):
            page = 0
        await state.update_data(query=query_callback)
        await state.update_data(results_page=page)
        await state.update_data(message_id_list=callback.message.message_id)

        await state.set_state(ActionState.search_right_old_state)

        await base_search_entr(callback.message, state)


#@employee_router.callback_query(F.data == "getLeftResults")
@employee_router.callback_query(lambda c: c.data and c.data.startswith(('getLeftResults_')))
async def base_search_entr_callback_left(callback: types.CallbackQuery, state: FSMContext):
    #message_ids_to_delete = [callback.message.message_id - i for i in range(2)]
    # delete_messages(callback.message.chat.id, message_ids_to_delete)
    action, query_callback, page, page_max, m_id = callback.data.split('_')
    data = await state.get_data()
    query = data.get('query')

    if query_callback == query:
        #message_ids_to_delete = [callback.message.message_id - i for i in range(2)]
        #await delete_messages(callback.message.chat.id , message_ids_to_delete)

        data = await state.get_data()
        results_page = int(data.get('results_page')) - 1
        if results_page < 0:
            results_page = data.get('results_page_max')
        await state.update_data(results_page=results_page)
        await state.update_data(message_id_list=callback.message.message_id)

        await state.set_state(ActionState.search_left_state)

        await base_search_entr(callback.message, state)
    else:
        page = int(page)
        page -= 1
        if page < 0:
            page = page_max
        await state.update_data(query=query_callback)
        await state.update_data(results_page=page)
        await state.update_data(message_id_list=callback.message.message_id)

        await state.set_state(ActionState.search_left_old_state)

        await base_search_entr(callback.message, state)
