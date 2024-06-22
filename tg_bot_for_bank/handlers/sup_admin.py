from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message

from tg_bot_for_bank.db.database_handler import update_position_id, get_all_employees_from_db, get_user_FIO_from_db
from tg_bot_for_bank.keyboards.simple_row import make_row_inline_keyboard
from tg_bot_for_bank.services.message_deleter import delete_messages
from tg_bot_for_bank.services.sender import send_to

sup_admin_router = Router()


class ActionState(StatesGroup):
    employee_list_state = State()
    admin_list_state = State()


@sup_admin_router.message(F.text.lower() == "2")
async def emlist2(message: Message, state: FSMContext):
    message_ids_to_delete = [message.message_id - i for i in range(1, 2)]
    await delete_messages(message.chat.id, message_ids_to_delete)


@sup_admin_router.message(F.text.lower() == "3")
async def emlist(message: Message, state: FSMContext):
    await message.answer(
        text="[Список сотрудников](tg://user?id=743040577)",
        parse_mode='MarkdownV2'
    )


# Обработка нажатия "Пользователи"
@sup_admin_router.callback_query(F.data == "getLeftAdminList")
async def admin_list_callback_Left(callback: types.CallbackQuery, state: FSMContext):
    message_ids_to_delete = [callback.message.message_id - i for i in range(2)]
    await delete_messages(callback.message.chat.id, message_ids_to_delete)

    data = await state.get_data()
    list_page = data.get('admin_list_page') - 1
    if list_page < 0:
        list_page = data.get('admin_list_page_max')
    await state.update_data(admin_list_page=list_page)

    await admin_list_callback(callback, state)


@sup_admin_router.callback_query(F.data == "getRightAdminList")
async def admin_list_callback_Right(callback: types.CallbackQuery, state: FSMContext):
    message_ids_to_delete = [callback.message.message_id - i for i in range(2)]
    await delete_messages(callback.message.chat.id, message_ids_to_delete)

    data = await state.get_data()
    list_page = data.get('admin_list_page') + 1
    if list_page > data.get('admin_list_page_max'):
        list_page = 0
    await state.update_data(admin_list_page=list_page)

    await admin_list_callback(callback, state)


@sup_admin_router.callback_query(F.data == "getLeftEmployeeList")
async def emloyees_list_callback_Left(callback: types.CallbackQuery, state: FSMContext):
    message_ids_to_delete = [callback.message.message_id - i for i in range(2)]
    await delete_messages(callback.message.chat.id, message_ids_to_delete)

    data = await state.get_data()
    list_page = data.get('list_page') - 1
    if list_page < 0:
        list_page = data.get('list_page_max')
    await state.update_data(list_page=list_page)

    await emloyees_list_callback(callback, state)


@sup_admin_router.callback_query(F.data == "getRightEmployeeList")
async def emloyees_list_callback_Right(callback: types.CallbackQuery, state: FSMContext):
    message_ids_to_delete = [callback.message.message_id - i for i in range(2)]
    await delete_messages(callback.message.chat.id, message_ids_to_delete)

    data = await state.get_data()
    list_page = data.get('list_page') + 1
    if list_page > data.get('list_page_max'):
        list_page = 0
    await state.update_data(list_page=list_page)

    await emloyees_list_callback(callback, state)


@sup_admin_router.callback_query(F.data == "getEmployeesList")
async def emloyees_list_callback(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(ActionState.employee_list_state)
    employees_arr = await get_all_employees_from_db(["Administrator", "Employee"])

    message_ids_to_delete = [callback.message.message_id - i for i in range(1)]
    await delete_messages(callback.message.chat.id, message_ids_to_delete)

    if len(employees_arr) > 1:
        keyboard_items = [
            {'text': '👈',
             'callback_data': "getLeftEmployeeList"},
            {'text': '👉',
             'callback_data': "getRightEmployeeList"},
            {'text': 'Администраторы',
             'callback_data': "getAdminList"},
        ]

        data = await state.get_data()
        list_page = data.get('list_page')

        await callback.message.answer(
            text="<b>Список сотрудников:</b>\n"
                 f"{employees_arr[list_page]}",
            parse_mode='HTML',
            disable_web_page_preview=True,
            reply_markup=make_row_inline_keyboard(keyboard_items)
        )
    else:
        keyboard_items = [
            {'text': 'Администраторы',
             'callback_data': "getAdminList"},
        ]

        await callback.message.answer(
            text="<b>Список сотрудников:</b>\n"
                 f"{employees_arr[0]}",
            parse_mode='HTML',
            disable_web_page_preview=True,
            reply_markup=make_row_inline_keyboard(keyboard_items),
        )


@sup_admin_router.message(F.text.lower() == "пользователи")
async def emloyees_list(message: Message, state: FSMContext):
    await state.set_state(ActionState.employee_list_state)
    employees_arr = await get_all_employees_from_db(["Administrator", "Employee"])

    await state.update_data(admins_list_page=0)

    await state.update_data(list_page=0)
    await state.update_data(list_page_max=len(employees_arr) - 1)

    message_ids_to_delete = [message.message_id - i for i in range(1)]
    await delete_messages(message.chat.id, message_ids_to_delete)

    if len(employees_arr) > 1:
        keyboard_items = [
            {'text': '👈',
             'callback_data': "getLeftEmployeeList"},
            {'text': '👉',
             'callback_data': "getRightEmployeeList"},
            {'text': 'Администраторы',
             'callback_data': "getAdminList"},
        ]

        data = await state.get_data()
        list_page = data.get('list_page')
        await state.update_data(list_page=list_page)

        await message.answer(
            text="<b>Список сотрудников:</b>\n"
                 f"{employees_arr[list_page]}",
            parse_mode='HTML',
            disable_web_page_preview=True,
            reply_markup=make_row_inline_keyboard(keyboard_items)
        )
    else:
        keyboard_items = [
            {'text': 'Администраторы',
             'callback_data': "getAdminList"},
        ]

        await message.answer(
            text="<b>Список сотрудников:</b>\n"
                 f"{employees_arr[0]}",
            parse_mode='HTML',
            disable_web_page_preview=True,
            reply_markup=make_row_inline_keyboard(keyboard_items)
        )


@sup_admin_router.callback_query(lambda c: c.data and c.data.startswith('getAdminList'))
async def admin_list_callback(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(ActionState.admin_list_state)
    admins_arr = await get_all_employees_from_db(["Administrator"])

    await state.update_data(admins_list_page_max=len(admins_arr) - 1)

    message_ids_to_delete = [callback.message.message_id - i for i in range(2)]
    await delete_messages(callback.message.chat.id, message_ids_to_delete)

    if len(admins_arr) > 1:
        keyboard_items = [
            {'text': '👈',
             'callback_data': "getLeftAdminList"},
            {'text': '👉',
             'callback_data': "getRightAdminList"},
            {'text': 'Сотрудники',
             'callback_data': "getEmployeesList"},
        ]

        data = await state.get_data()
        list_page = data.get('admins_list_page')
        await state.update_data(admins_list_page=list_page)

        await callback.message.answer(
            text="<b>Список администраторов:</b>\n"
                 f"{admins_arr[list_page]}",
            parse_mode='HTML',
            disable_web_page_preview=True,
            reply_markup=make_row_inline_keyboard(keyboard_items)
        )
    else:
        keyboard_items = [
            {'text': 'Сотрудники',
             'callback_data': "getEmployeesList"},
        ]

        await callback.message.answer(
            text="<b>Список администраторов:</b>\n"
                 f"{admins_arr[0]}",
            parse_mode='HTML',
            disable_web_page_preview=True,
            reply_markup=make_row_inline_keyboard(keyboard_items),
        )


# Ответ на запрос на авторизацию
@sup_admin_router.callback_query(lambda c: c.data and c.data.startswith(('accept_', 'reject_')))
async def process_callback(callback: types.CallbackQuery):
    action, tg_id = callback.data.split('_')
    lastname, firstname, patronymic = await get_user_FIO_from_db(tg_id)
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
