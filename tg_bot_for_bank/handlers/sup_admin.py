from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove

from tg_bot_for_bank.db.database_handler import update_position_id, get_all_employees_list_from_db, \
    get_user_FIO_from_db, get_all_employees_from_db, un_block_empolyee
from tg_bot_for_bank.keyboards.simple_row import make_row_inline_keyboard, make_row_inline_keyboard_mutiple, \
    make_row_keyboard, sup_admin_keyboard, make_row_keyboard_mutiple
from tg_bot_for_bank.services.message_deleter import delete_messages
from tg_bot_for_bank.services.sender import send_to

sup_admin_router = Router()


class ActionState(StatesGroup):
    start_state = State()
    employee_list_state = State()
    admin_list_state = State()
    inf_msg = State()
    inf_msg_entr = State()
    inf_msg_success = State()

class UserManagState(StatesGroup):
    user_manag = State()
    employee_block = State()
    employee_block_success = State()
    employee_unlock = State()
    employee_unlock_success = State()
    employee_change_role = State()

@sup_admin_router.message(ActionState.start_state)
async def information_message_success(message: Message, state: FSMContext):
    await state.clear()


@sup_admin_router.message(F.text.lower() == "запросы")
async def emlist2(message: Message, state: FSMContext):
    message_ids_to_delete = [message.message_id - i for i in range(1, 2)]
    await delete_messages(message.chat.id, message_ids_to_delete)


@sup_admin_router.message(F.text.lower() == "📢 информирование")
async def information_message(message: Message, state: FSMContext):
    await state.set_state(ActionState.inf_msg_entr)

    message_ids_to_delete = [message.message_id - i for i in range(2)]
    await delete_messages(message.chat.id, message_ids_to_delete)

    await message.answer(
        text="Введите сообщение для отправки сотрудникам 👇",
        reply_markup=make_row_keyboard(["❌ Отмена"])
    )

@sup_admin_router.message(
    F.text.lower() == "❌ отмена",
    UserManagState.employee_block
)
@sup_admin_router.message(
    F.text.lower() == "❌ отмена",
    UserManagState.employee_unlock
)
@sup_admin_router.message(F.text.lower() == "👥 управление пользователями")
async def employees_buttons_manage(message: Message, state: FSMContext):
    await state.set_state(UserManagState.user_manag)

    message_ids_to_delete = [message.message_id - i for i in range(2)]
    await delete_messages(message.chat.id, message_ids_to_delete)

    await message.answer(
        text="Вы находитесь в меню <b>Управления пользователями</b>.\nВыберите действие 👇",
        parse_mode='HTML',
        reply_markup=make_row_keyboard_mutiple([
            ["📋 Список пользователей"],
            ["🔒 Заблокировать", "🔓 Разблокировать"],
            ["🎭 Изменить роль пользователя"],
            ["🔙 Назад"]
        ]
        )
    )

@sup_admin_router.message(
    F.text.lower() == "❌ отмена",
    ActionState.inf_msg_entr
)
@sup_admin_router.message(F.text.lower() == "🔙 назад")
async def employees_buttons(message: Message, state: FSMContext):
    if ActionState.employee_list_state or ActionState.admin_list_state:
        message_ids_to_delete = [message.message_id - i for i in range(0, 4)]
        await delete_messages(message.chat.id, message_ids_to_delete)
    else:
        message_ids_to_delete = [message.message_id - i for i in range(0, 2)]
        await delete_messages(message.chat.id, message_ids_to_delete)

    await state.clear()

    await message.answer(
        text=f"Вы находитесь в <b>Главном меню</b>.\nВыберите действие 👇",
        parse_mode='HTML',
        reply_markup=sup_admin_keyboard()
    )


@sup_admin_router.message(ActionState.inf_msg_entr, F.text)
async def information_message_entry(message: Message, state: FSMContext):
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


@sup_admin_router.message(ActionState.inf_msg_success, F.text.lower() == "✅ подтвердить")
async def information_message_success(message: Message, state: FSMContext):
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


@sup_admin_router.message(ActionState.inf_msg_success, F.text.lower() == "🔄 изменить")
async def information_message_re_enter(message: Message, state: FSMContext):
    await information_message(message, state)

# Обработка нажатия "Изменить роль пользователя"
# @sup_admin_router.message(
#     F.text.lower() == "🎭 изменить роль пользователя",
#     UserManagState.user_manag
# )
# async def emloyee_role_change(message: Message, state: FSMContext):
#     await state.set_state(UserManagState.employee_change_role)
#
#     message_ids_to_delete = [message.message_id - i for i in range(2)]
#     await delete_messages(message.chat.id, message_ids_to_delete)
#
#     await message.answer(
#         text="Введите ФИО пользователя, чью роль хотите изменить 👇",
#         reply_markup=make_row_keyboard(["❌ Отмена"])
#     )
#
# @sup_admin_router.message(UserManagState.employee_change_role, F.text)
# async def emloyee_role_change_entry(message: Message, state: FSMContext):
#     await state.update_data(
#         fio_change_msg=message.text
#     )
#
#     data = await state.get_data()
#     fio_change_msg = data.get('fio_change_msg')
#
#     message_ids_to_delete = [message.message_id - i for i in range(2)]
#     await delete_messages(message.chat.id, message_ids_to_delete)
#
#     await message.answer(
#         text=f"Вы собираетесь изменить роль пользователя:\n\n<i>{fio_change_msg}</i>\n\nВсё верно?",
#         parse_mode='HTML',
#         reply_markup=make_row_keyboard_mutiple([
#             ["✅ Подтвердить", "🔄 Изменить"],
#             ["❌ Отмена"]]
#         )
#     )
#
#     await state.set_state(UserManagState.employee_block_success)

# Обработка нажатия "Заблокировать"
@sup_admin_router.message(
    F.text.lower() == "🔒 заблокировать",
    UserManagState.user_manag
)
async def emloyees_block(message: Message, state: FSMContext):
    await state.set_state(UserManagState.employee_block)

    message_ids_to_delete = [message.message_id - i for i in range(2)]
    await delete_messages(message.chat.id, message_ids_to_delete)

    await message.answer(
        text="Введите ФИО пользователя, которого хотите заблокировать 👇",
        reply_markup=make_row_keyboard(["❌ Отмена"])
    )


@sup_admin_router.message(UserManagState.employee_block_success, F.text.lower() == "🔄 изменить")
async def information_message_re_enter(message: Message, state: FSMContext):
    await emloyees_block(message, state)


@sup_admin_router.message(UserManagState.employee_block, F.text)
async def emloyees_block_entry(message: Message, state: FSMContext):
    await state.update_data(
        fio_block_msg=message.text
    )

    data = await state.get_data()
    fio_block_msg = data.get('fio_block_msg')

    message_ids_to_delete = [message.message_id - i for i in range(2)]
    await delete_messages(message.chat.id, message_ids_to_delete)

    await message.answer(
        text=f"Вы собираетесь заблокировать пользователя:\n\n<i>{fio_block_msg}</i>\n\nВсё верно?",
        parse_mode='HTML',
        reply_markup=make_row_keyboard_mutiple([
            ["✅ Подтвердить", "🔄 Изменить"],
            ["❌ Отмена"]]
        )
    )

    await state.set_state(UserManagState.employee_block_success)


@sup_admin_router.message(UserManagState.employee_block_success, F.text.lower() == "✅ подтвердить")
async def emloyees_block_success(message: Message, state: FSMContext):
    data = await state.get_data()
    fio_block_msg = data.get('fio_block_msg')

    message_ids_to_delete = [message.message_id - i for i in range(2)]
    await delete_messages(message.chat.id, message_ids_to_delete)

    block_result = await un_block_empolyee(fio_block_msg, 'block')
    if block_result:
        await message.answer(
            text=f"Пользователь <i>{fio_block_msg}</i> заблокирован.",
            reply_markup=sup_admin_keyboard(),
            parse_mode='HTML'
        )
    else:
        await message.answer(
            text=f"Пользователь <i>{fio_block_msg}</i> не найден.",
            reply_markup=sup_admin_keyboard(),
            parse_mode='HTML'
        )
    await state.clear()
    await state.set_state(ActionState.start_state)


# Обработка нажатия "Разблокировать"
@sup_admin_router.message(
    F.text.lower() == "🔓 разблокировать",
    UserManagState.user_manag
)
async def emloyees_unlock(message: Message, state: FSMContext):
    await state.set_state(UserManagState.employee_unlock)

    message_ids_to_delete = [message.message_id - i for i in range(2)]
    await delete_messages(message.chat.id, message_ids_to_delete)

    await message.answer(
        text="Введите ФИО пользователя, которого хотите разблокировать 👇",
        reply_markup=make_row_keyboard(["❌ Отмена"])
    )


@sup_admin_router.message(UserManagState.employee_unlock_success, F.text.lower() == "🔄 изменить")
async def information_message_re_enter(message: Message, state: FSMContext):
    await emloyees_unlock(message, state)


@sup_admin_router.message(UserManagState.employee_unlock, F.text)
async def emloyees_unlock_entry(message: Message, state: FSMContext):
    await state.update_data(
        fio_unlock_msg=message.text
    )

    data = await state.get_data()
    fio_unlock_msg = data.get('fio_unlock_msg')

    message_ids_to_delete = [message.message_id - i for i in range(2)]
    await delete_messages(message.chat.id, message_ids_to_delete)

    await message.answer(
        text=f"Вы собираетесь разблокировать пользователя:\n\n<i>{fio_unlock_msg}</i>\n\nВсё верно?",
        parse_mode='HTML',
        reply_markup=make_row_keyboard_mutiple([
            ["✅ Подтвердить", "🔄 Изменить"],
            ["❌ Отмена"]]
        )
    )

    await state.set_state(UserManagState.employee_unlock_success)


@sup_admin_router.message(UserManagState.employee_unlock_success, F.text.lower() == "✅ подтвердить")
async def emloyees_unlock_success(message: Message, state: FSMContext):
    data = await state.get_data()
    fio_unlock_msg = data.get('fio_unlock_msg')

    message_ids_to_delete = [message.message_id - i for i in range(2)]
    await delete_messages(message.chat.id, message_ids_to_delete)

    unlock_result = await un_block_empolyee(fio_unlock_msg, 'unlock')
    if unlock_result:
        await message.answer(
            text=f"Пользователь <i>{fio_unlock_msg}</i> разблокирован.",
            reply_markup=sup_admin_keyboard(),
            parse_mode='HTML'
        )
    else:
        await message.answer(
            text=f"Пользователь <i>{fio_unlock_msg}</i> не найден.",
            reply_markup=sup_admin_keyboard(),
            parse_mode='HTML'
        )
    await state.clear()
    await state.set_state(ActionState.start_state)


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
    employees_arr = await get_all_employees_list_from_db(["Administrator", "Employee"])

    message_ids_to_delete = [callback.message.message_id - i for i in range(1)]
    await delete_messages(callback.message.chat.id, message_ids_to_delete)

    if len(employees_arr) > 1:
        keyboard_items = [
            [{'text': '👈',
              'callback_data': "getLeftEmployeeList"},
             {'text': '👉',
              'callback_data': "getRightEmployeeList"}],
            [{'text': 'Администраторы 🤖',
              'callback_data': "getAdminList"}]
        ]

        data = await state.get_data()
        list_page = data.get('list_page')

        await callback.message.answer(
            text="<b>Список сотрудников:</b>\n"
                 f"{employees_arr[list_page]}",
            parse_mode='HTML',
            disable_web_page_preview=True,
            reply_markup=make_row_inline_keyboard_mutiple(keyboard_items)
        )
    else:
        keyboard_items = [
            {'text': 'Администраторы 🤖',
             'callback_data': "getAdminList"},
        ]

        await callback.message.answer(
            text="<b>Список сотрудников:</b>\n"
                 f"{employees_arr[0]}",
            parse_mode='HTML',
            disable_web_page_preview=True,
            reply_markup=make_row_inline_keyboard(keyboard_items),
        )


@sup_admin_router.message(
    F.text.lower() == "📋 список пользователей",
    UserManagState.user_manag
)
async def emloyees_list(message: Message, state: FSMContext):
    await state.set_state(ActionState.employee_list_state)
    employees_arr = await get_all_employees_list_from_db(["Administrator", "Employee"])

    await state.update_data(admins_list_page=0)

    await state.update_data(list_page=0)
    await state.update_data(list_page_max=len(employees_arr) - 1)

    message_ids_to_delete = [message.message_id - i for i in range(1)]
    await delete_messages(message.chat.id, message_ids_to_delete)

    if len(employees_arr) > 1:
        keyboard_items = [
            [{'text': '👈',
              'callback_data': "getLeftEmployeeList"},
             {'text': '👉',
              'callback_data': "getRightEmployeeList"}],
            [{'text': 'Администраторы 🤖',
              'callback_data': "getAdminList"}]
        ]

        data = await state.get_data()
        list_page = data.get('list_page')
        await state.update_data(list_page=list_page)

        await message.answer(
            text="<b>Список сотрудников:</b>\n"
                 f"{employees_arr[list_page]}",
            parse_mode='HTML',
            disable_web_page_preview=True,
            reply_markup=make_row_inline_keyboard_mutiple(keyboard_items)
        )
    else:
        keyboard_items = [
            {'text': 'Администраторы 🤖',
             'callback_data': "getAdminList"},
        ]

        await message.answer(
            text="<b>Список сотрудников:</b>\n"
                 f"{employees_arr[0]}",
            parse_mode='HTML',
            disable_web_page_preview=True,
            reply_markup=make_row_inline_keyboard_mutiple([keyboard_items])
        )


@sup_admin_router.callback_query(lambda c: c.data and c.data.startswith('getAdminList'))
async def admin_list_callback(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(ActionState.admin_list_state)
    admins_arr = await get_all_employees_list_from_db(["Administrator"])

    await state.update_data(admins_list_page_max=len(admins_arr) - 1)

    message_ids_to_delete = [callback.message.message_id - i for i in range(2)]
    await delete_messages(callback.message.chat.id, message_ids_to_delete)

    if len(admins_arr) > 1:
        keyboard_items = [
            [{'text': '👈',
              'callback_data': "getLeftAdminList"},
             {'text': '👉',
              'callback_data': "getRightAdminList"}],
            [{'text': 'Сотрудники 👨‍💼',
              'callback_data': "getEmployeesList"}]
        ]

        data = await state.get_data()
        list_page = data.get('admins_list_page')
        await state.update_data(admins_list_page=list_page)

        await callback.message.answer(
            text="<b>Список администраторов:</b>\n"
                 f"{admins_arr[list_page]}",
            parse_mode='HTML',
            disable_web_page_preview=True,
            reply_markup=make_row_inline_keyboard_mutiple(keyboard_items)
        )
    else:
        keyboard_items = [
            {'text': 'Сотрудники 👨‍💼',
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
