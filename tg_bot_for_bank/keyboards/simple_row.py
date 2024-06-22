from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


def sup_admin_keyboard():
    first_button = [
        [KeyboardButton(text=("Пользователи")), KeyboardButton(text=("2"))],
        [KeyboardButton(text=("3"))]
    ]
    markup = ReplyKeyboardMarkup(keyboard=first_button, resize_keyboard=True)
    return markup

def make_row_keyboard(items: list[str]) -> ReplyKeyboardMarkup:
    """
    Создаёт реплай-клавиатуру с кнопками в один ряд
    :param items: список текстов для кнопок
    :return: объект реплай-клавиатуры
    """
    row = [KeyboardButton(text=item) for item in items]
    return ReplyKeyboardMarkup(keyboard=[row], resize_keyboard=True)


async def contact_keyboard():
    first_button = [[KeyboardButton(text=("📱 Отправить"), request_contact=True)]]
    markup = ReplyKeyboardMarkup(keyboard=first_button, resize_keyboard=True)
    return markup


# inline keyboard
def make_row_inline_keyboard(items: list[dict]) -> InlineKeyboardMarkup:
    """
    Создаёт инлайн-клавиатуру с кнопками в один ряд
    :param items: список словарей с текстами для кнопок и callback_data
    :return: объект инлайн-клавиатуры
    """
    row = [
        InlineKeyboardButton(
            text=item['text'],
            callback_data=item.get('callback_data', item['text'])
        )
        for item in items
    ]
    return InlineKeyboardMarkup(inline_keyboard=[row])
