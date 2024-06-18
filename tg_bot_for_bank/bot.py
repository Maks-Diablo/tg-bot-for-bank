import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config_reader import config
from tg_bot_for_bank.handlers.common import router


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )

    # Если не указать storage, то по умолчанию всё равно будет MemoryStorage
    dp = Dispatcher()
    bot = Bot(config.bot_token.get_secret_value())

    dp.include_router(router)

    # пропускаем все входящие
    await bot.delete_webhook(drop_pending_updates=True)

    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())