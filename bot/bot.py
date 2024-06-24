import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config_reader import config
from bot.filters.role_filter import RoleFilter
from bot.handlers.auth_user import auth_router
from bot.handlers.common import common_router
from bot.handlers.sup_admin import sup_admin_router


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )

    bot = Bot(config.bot_token.get_secret_value())
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(common_router)  # Include router for Guests
    dp.include_router(auth_router)  # Include router for Guests
    dp.include_router(sup_admin_router)  # Include router for Guests

    sup_admin_router.message.filter(RoleFilter(role='Super-Administrator'))
    auth_router.message.filter(RoleFilter(role='Guest'))

    await bot.delete_webhook(drop_pending_updates=True)

    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
