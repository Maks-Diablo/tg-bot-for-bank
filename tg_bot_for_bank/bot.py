import asyncio
import logging

from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from config_reader import config
from tg_bot_for_bank.db.database_handler import get_user_role_from_db
from tg_bot_for_bank.handlers.common import auth_router
from tg_bot_for_bank.handlers.sup_admin import sup_admin_router

async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )

    dp = Dispatcher()
    bot = Bot(config.bot_token.get_secret_value())

    # пропускаем все входящие
    await bot.delete_webhook(drop_pending_updates=True)

    # Получаем роль пользователя из базы данных (примерно)
    @dp.message()
    async def handle_message(message: types.Message):
        user_id = message.from_user.id
        user_role = await get_user_role_from_db(user_id)  # Fetch user role asynchronously

        if user_role == 'Super-Administrator':
            print('Super-Administrator')
            dp.register_router(sup_admin_router, lambda message: message.from_user.id == user_id)
        elif user_role == 'Guest':
            dp.include_router(auth_router)  # Include router for Guests

    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
