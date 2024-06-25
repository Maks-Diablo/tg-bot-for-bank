from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.dispatcher.flags import get_flag
from aiogram.types import Message
from aiogram.utils.chat_action import ChatActionSender


class ChatActionMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:
        long_operation_type = get_flag(data, "long_operation")

        # Check if the long_operation flag is present and valid
        if long_operation_type:
            async with ChatActionSender(
                    action=long_operation_type,
                    chat_id=event.chat.id,
                    bot=event.bot
            ):
                return await handler(event, data)

        # If the flag is not present, proceed without triggering the ChatActionSender
        return await handler(event, data)
