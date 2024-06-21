from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from tg_bot_for_bank.db.database_handler import update_position_id
from tg_bot_for_bank.services.message_deleter import delete_messages
from tg_bot_for_bank.services.sender import send_to

sup_admin_router = Router()


@sup_admin_router.callback_query(lambda c: c.data and c.data.startswith(('accept_', 'reject_')))
async def process_callback(callback: types.CallbackQuery):
    action, tg_id, lastname, firstname, patronymic = callback.data.split('_')
    if action == 'accept':
        # Логика для принятия пользователя
        await update_position_id(tg_id, 'Employee')

        await send_to(tg_id, 'Администратор одобрил Вам авторизацию.\nВаш текущий статус - <b>Сотрудник</b>')

        message_ids_to_delete = [callback.message.message_id - i for i in range(0, 2)]
        await delete_messages(callback.message.chat.id, message_ids_to_delete)

        await callback.message.answer(f"Запрос от <b>{lastname} {firstname} {patronymic}</b> принят.",
                                      parse_mode='HTML')
    elif action == 'reject':
        # Логика для отказа пользователю
        await update_position_id(tg_id, 'DEACTIVE')
        await send_to(tg_id, 'Администратор отказал Вам в авторизации.')

        message_ids_to_delete = [callback.message.message_id - i for i in range(0, 2)]
        await delete_messages(callback.message.chat.id, message_ids_to_delete)

        await callback.message.answer(f"Запрос от <b>{lastname} {firstname} {patronymic}</b> отклонён.",
                                      parse_mode='HTML')

    await callback.answer()


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
