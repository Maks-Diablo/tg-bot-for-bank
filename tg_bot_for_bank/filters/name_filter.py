from aiogram.filters import BaseFilter
from aiogram.types import Message

import re

# Регулярное выражение для проверки формата "Фамилия Имя Отчество"

FIO_PATTERN = re.compile(r'^[А-ЯЁ][а-яё]+\s[А-ЯЁ][а-яё]+\s[А-ЯЁ][а-яё]+$')


class IsFIO(BaseFilter):  # [1]
    def __init__(self, is_fio: bool):
        self.is_fio = is_fio

    async def __call__(self, message: Message) -> bool:  # [3]
        if self.is_fio:
            return bool(FIO_PATTERN.match(message.text))
        return False
