from aiogram import types, Router
from aiogram.filters import CommandStart

router = Router()

@router.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer(
        "👋 Привет! Я Mellot — твой весёлый музыкальный робот-проводник.\n"
        "От меня ссылки из соцсетей превращаются в чистый MP3 или голосовое сообщение за пару секунд! 🎧✨\n\n"
    )