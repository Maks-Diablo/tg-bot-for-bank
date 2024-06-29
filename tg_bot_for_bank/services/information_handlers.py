from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from tg_bot_for_bank.db.database_handler import get_all_employees_from_db
from tg_bot_for_bank.handlers.common import start_message_main_sup_admin
from tg_bot_for_bank.keyboards.simple_row import make_row_inline_keyboard_mutiple, make_row_keyboard_mutiple, \
    sup_admin_keyboard, make_row_keyboard
from tg_bot_for_bank.services.message_deleter import delete_messages, bot
from tg_bot_for_bank.services.sender import send_to


async def information_message_admin(message: Message, state: FSMContext, ActionState):
    await state.set_state(ActionState.inf_msg_entr)

    message_ids_to_delete = [message.message_id - i for i in range(2)]
    await delete_messages(message.chat.id, message_ids_to_delete)

    await message.answer(
        text="Введите сообщение для отправки сотрудникам 👇",
        reply_markup=make_row_keyboard(["❌ Отмена"])
    )


async def information_message_entry(message: Message, state: FSMContext, ActionState):
    await state.update_data(
        inf_msg=message.text
    )

    data = await state.get_data()
    inf_msg = data.get('inf_msg')

    message_ids_to_delete = [message.message_id - i for i in range(2)]
    await delete_messages(message.chat.id, message_ids_to_delete)

    await message.answer(
        text=f"Вы собираетесь отправить сообщение:\n\n<i>{inf_msg}</i>\n\nВсё верно?",
        parse_mode='HTML',
        reply_markup=make_row_keyboard_mutiple([
            ["✅ Подтвердить", "🔄 Изменить"],
            ["❌ Отмена"]]
        )
    )

    await state.set_state(ActionState.inf_msg_success)


async def information_message_success(message: Message, state: FSMContext, ActionState):
    data = await state.get_data()
    inf_msg = data.get('inf_msg')

    message_ids_to_delete = [message.message_id - i for i in range(2)]
    await delete_messages(message.chat.id, message_ids_to_delete)

    await message.answer(
        text="Сообщение отправлено.",
        reply_markup=sup_admin_keyboard()
    )

    employees = await get_all_employees_from_db()

    for employee in employees:
        await send_to(employee.tg_id, inf_msg)

    await state.set_state(ActionState.start_state)
    await start_message_main_sup_admin(message)
