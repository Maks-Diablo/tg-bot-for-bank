import asyncio
import logging

from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from config_reader import config
from tg_bot_for_bank.db.database_handler import get_user_role_from_db
from tg_bot_for_bank.filters.role_filter import RoleFilter
from tg_bot_for_bank.handlers.common import auth_router
from tg_bot_for_bank.handlers.sup_admin import sup_admin_router


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )

    dp = Dispatcher()
    bot = Bot(config.bot_token.get_secret_value())

    dp.include_router(auth_router)  # Include router for Guests
    dp.include_router(sup_admin_router)  # Include router for Guests

    sup_admin_router.message.filter(RoleFilter(role='Super-Administrator'))
    auth_router.message.filter(RoleFilter(role='Guest'))

    await bot.delete_webhook(drop_pending_updates=True)

    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
