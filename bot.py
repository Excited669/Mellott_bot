# bot.py
import asyncio
import logging
import os
import sys

from aiogram import Bot, Dispatcher

from config import BOT_TOKEN
from handlers import private_handlers, channel_handlers

async def main():
    # Убрали таймаут, т.к. фоновые задачи решают эту проблему лучше
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    dp.include_router(private_handlers.router)
    dp.include_router(channel_handlers.router)

    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    if not os.path.exists('downloads'):
        os.makedirs('downloads')
    asyncio.run(main())