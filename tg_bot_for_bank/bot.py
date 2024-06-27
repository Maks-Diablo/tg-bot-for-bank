import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand

from config_reader import config
from tg_bot_for_bank.filters.chat_action_middleware import ChatActionMiddleware
from tg_bot_for_bank.filters.role_filter import RoleFilter
from tg_bot_for_bank.handlers.admin import admin_router
from tg_bot_for_bank.handlers.auth_user import auth_router
from tg_bot_for_bank.handlers.common import common_router
from tg_bot_for_bank.handlers.employee import employee_router
from tg_bot_for_bank.handlers.sup_admin import sup_admin_router


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )

    bot = Bot(config.bot_token.get_secret_value())
    dp = Dispatcher(storage=MemoryStorage())

    dp.startup.register(set_main_menu)

    employee_router.message.middleware(ChatActionMiddleware())

    dp.include_router(common_router)
    dp.include_router(auth_router)
    dp.include_router(employee_router)
    dp.include_router(admin_router)
    dp.include_router(sup_admin_router)

    auth_router.message.filter(RoleFilter(role='Guest'))
    employee_router.message.filter(RoleFilter(role='Employee'))
    admin_router.message.filter(RoleFilter(role='Administrator'))
    sup_admin_router.message.filter(RoleFilter(role='Super-Administrator'))

    await bot.delete_webhook(drop_pending_updates=True)

    await dp.start_polling(bot)


async def set_main_menu(bot: Bot):
    # Создаем список с командами и их описанием для кнопки menu
    main_menu_commands = [
        BotCommand(command='/start',
                   description='Перезапуск бота'),
        BotCommand(command='/support',
                   description='Поддержка')
    ]

    await bot.set_my_commands(main_menu_commands)

if __name__ == '__main__':
    asyncio.run(main())
