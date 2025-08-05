import asyncio
import os
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from handlers import register_handlers
from utils.states import ConversionStates

async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # Регистрация всех обработчиков
    register_handlers(dp)

    # Запуск бота
    await dp.start_polling(bot)

if __name__ == "__main__":
    if not os.path.exists('downloads'):
        os.makedirs('downloads')
    asyncio.run(main())