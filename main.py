import asyncio

from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from middlewares.db import DataBaseSession

from database.engine import create_db, drop_db, session_maker

from handlers.user_privat import user_private_router
from handlers.admin_privat import admin_router

bot = Bot(token=', default=DefaultBotProperties(parse_mode=ParseMode.HTML))
bot.my_admins_list = [7777777777]

dp = Dispatcher()
########################### Регистрация диспетчеров ##################################
dp.include_router(user_private_router)
dp.include_router(admin_router)

async def on_startup(bot):
    #await drop_db()

    await create_db()


async def main():
    dp.startup.register(on_startup)

    dp.update.middleware(DataBaseSession(session_pool=session_maker)) # подключение мидлваре с БД

    await bot.delete_webhook(drop_pending_updates=True) #Убирает старые сообщения при запуске
    print('Начало работы')
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
try:
    asyncio.run(main())
except KeyboardInterrupt:
    print('Бот лег')
