# bot.py

import asyncio
import logging
import os
import sys

from aiogram import Bot, Dispatcher

# Импортируем все наши роутеры
from handlers import start, conversion, channel
from config import BOT_TOKEN

async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # Включаем роутеры в главный диспетчер
    dp.include_router(start.router)
    dp.include_router(conversion.router)
    dp.include_router(channel.router)  # <-- ДОБАВЛЕНО

    # Запускаем бота
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    if not os.path.exists('downloads'):
        os.makedirs('downloads')
    asyncio.run(main())