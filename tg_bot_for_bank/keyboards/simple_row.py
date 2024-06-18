from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


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