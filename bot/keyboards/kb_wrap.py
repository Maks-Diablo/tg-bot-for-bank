import functools
import inspect
from typing import Any, Callable, Literal, Tuple, TypeVar

from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

F = TypeVar("F", bound=Callable[..., Any])


def kb_wrap(
        keyboard_type: Literal["reply", "inline"] = "inline",
        adjust_keyboard: int | Tuple[int] = 1,
        **builder_params,
):
    def get_keyboard_builder(
            keyboard_type: Literal["reply", "inline"]
    ) -> ReplyKeyboardBuilder | InlineKeyboardBuilder:
        if keyboard_type == "inline":
            return InlineKeyboardBuilder()
        elif keyboard_type == "reply":
            return ReplyKeyboardBuilder()

    def apply_builder_changes(
            builder: InlineKeyboardBuilder | ReplyKeyboardBuilder,
            adjust_keyboard: int | Tuple[int] = 1,
            **builder_params,
    ) -> InlineKeyboardMarkup | ReplyKeyboardMarkup:
        if adjust_keyboard:
            if isinstance(adjust_keyboard, int):
                adjust_keyboard = (adjust_keyboard,)
            builder.adjust(*adjust_keyboard)

        return builder.as_markup(**builder_params, resize_keyboard=True)

    def wrapper(func: F) -> F:
        @functools.wraps(func)
        async def wrapped_f(
                *args: Any, **kwargs: Any
        ) -> InlineKeyboardMarkup | ReplyKeyboardMarkup:
            builder = get_keyboard_builder(keyboard_type=keyboard_type)

            await func(builder=builder, *args, **kwargs)

            return apply_builder_changes(builder, adjust_keyboard, **builder_params)

        @functools.wraps(func)
        def sync_wrapped_f(
                *args: Any, **kwargs: Any
        ) -> InlineKeyboardMarkup | ReplyKeyboardMarkup:
            builder = get_keyboard_builder(keyboard_type=keyboard_type)

            func(builder=builder, *args, **kwargs)

            return apply_builder_changes(builder, adjust_keyboard, **builder_params)

        if inspect.iscoroutinefunction(func):
            return wrapped_f
        else:
            return sync_wrapped_f

    return wrapper

