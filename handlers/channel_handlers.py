# handlers/channel_handlers.py
import asyncio
from aiogram import Router, types, Bot
from aiogram.filters import Command, CommandObject
from services.converter import process_conversion

router = Router()


async def common_channel_handler(message: types.Message, command: CommandObject, bot: Bot, choice: str):
    if not command.args:
        await message.delete()
        return

    link = command.args
    caption = None

    if message.from_user:
        user_mention = f"@{message.from_user.username}" if message.from_user.username else message.from_user.full_name
        if choice in ['mp3', 'mp4']:
            caption = f"{choice.upper()} от {user_mention}"

    await message.delete()

    # Запускаем тяжелую задачу в фоне, чтобы избежать таймаутов
    asyncio.create_task(
        process_conversion(link=link, choice=choice, bot=bot, chat_id=message.chat.id, caption=caption)
    )


@router.channel_post(Command("cmp3"))
async def channel_mp3(message: types.Message, command: CommandObject, bot: Bot):
    await common_channel_handler(message, command, bot, 'mp3')


@router.channel_post(Command("cgs"))
async def channel_voice(message: types.Message, command: CommandObject, bot: Bot):
    await common_channel_handler(message, command, bot, 'voice')


@router.channel_post(Command("cmp4"))
async def channel_mp4(message: types.Message, command: CommandObject, bot: Bot):
    await common_channel_handler(message, command, bot, 'mp4')