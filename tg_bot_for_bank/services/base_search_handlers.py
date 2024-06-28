from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from tg_bot_for_bank.keyboards.simple_row import make_row_inline_keyboard_mutiple
from tg_bot_for_bank.services.message_deleter import delete_messages, bot
from aiogram.utils.chat_action import ChatActionSender

from tg_bot_for_bank.services.search_parser import search_belarusbank


async def base_search_entr_handler(message: Message, state: FSMContext, ActionState, start_message_main):
    current_state = await state.get_state()

    if current_state != ActionState.search_right_state and current_state != ActionState.search_left_state and current_state != ActionState.search_right_old_state and current_state != ActionState.search_left_old_state:
        message_ids_to_delete = [message.message_id - i for i in range(2)]
        await delete_messages(message.chat.id, message_ids_to_delete)

        query = message.text
        await state.update_data(query=query)

        async with ChatActionSender(action="typing", chat_id=message.chat.id, bot=message.bot):
            result_query = await search_belarusbank(query)
            await state.update_data(result_query=result_query)

        await state.update_data(results_page=0)
        await state.update_data(results_page_max=len(result_query) - 1)

    if current_state == ActionState.search_right_old_state or current_state == ActionState.search_left_old_state:
        data = await state.get_data()
        query = data.get('query')
        page = data.get('results_page')

        async with ChatActionSender(action="typing", chat_id=message.chat.id, bot=message.bot):
            result_query = await search_belarusbank(query)
            await state.update_data(result_query=result_query)

        await state.update_data(results_page=page)
        await state.update_data(results_page_max=len(result_query) - 1)

    async with ChatActionSender(action="typing", chat_id=message.chat.id, bot=message.bot):
        data = await state.get_data()
        results_page_max = int(data.get('results_page_max'))
        results_page = int(data.get('results_page'))
        result_query = data.get('result_query')
        query = data.get('query')
        message_id_list = data.get('message_id_list')

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
                await start_message_main(message)
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


async def base_search_entr_callback_right_handler(callback: types.CallbackQuery, state: FSMContext, ActionState, start_message_main):
    action, query_callback, page, page_max, m_id = callback.data.split('_')
    data = await state.get_data()
    query = data.get('query')
    if query_callback == query:
        data = await state.get_data()
        results_page = int(data.get('results_page')) + 1
        if results_page > data.get('results_page_max'):
            results_page = 0
        await state.update_data(results_page=results_page)
        await state.update_data(message_id_list=callback.message.message_id)

        await state.set_state(ActionState.search_right_state)

        await base_search_entr_handler(callback.message, state, ActionState, start_message_main)
    else:
        page = int(page)
        page += 1
        if page > int(page_max):
            page = 0
        await state.update_data(query=query_callback)
        await state.update_data(results_page=page)
        await state.update_data(message_id_list=callback.message.message_id)

        await state.set_state(ActionState.search_right_old_state)

        await base_search_entr_handler(callback.message, state, ActionState, start_message_main)

async def base_search_entr_callback_left_handler(callback: types.CallbackQuery, state: FSMContext, ActionState, start_message_main):
    action, query_callback, page, page_max, m_id = callback.data.split('_')
    data = await state.get_data()
    query = data.get('query')

    if query_callback == query:
        data = await state.get_data()
        results_page = int(data.get('results_page')) - 1
        if results_page < 0:
            results_page = data.get('results_page_max')
        await state.update_data(results_page=results_page)
        await state.update_data(message_id_list=callback.message.message_id)

        await state.set_state(ActionState.search_left_state)

        await base_search_entr_handler(callback.message, state, ActionState, start_message_main)
    else:
        page = int(page)
        page -= 1
        if page < 0:
            page = page_max
        await state.update_data(query=query_callback)
        await state.update_data(results_page=page)
        await state.update_data(message_id_list=callback.message.message_id)

        await state.set_state(ActionState.search_left_old_state)

        await base_search_entr_handler(callback.message, state, ActionState, start_message_main)
