from aiogram import Router, types, Bot
from aiogram.filters import Command, CommandObject
from services.converter import process_conversion

router = Router()

@router.channel_post(Command("cmp3"))
async def convert_mp3_in_channel(message: types.Message, command: CommandObject, bot: Bot):
    if not command.args:
        await message.delete()
        return
    link = command.args
    if not link.startswith(('http://', 'https://')):
        await message.delete()
        return
    await message.delete()
    await process_conversion(link=link, choice_str='mp3', bot=bot, chat_id=message.chat.id)

@router.channel_post(Command("cgs"))
async def convert_gs_in_channel(message: types.Message, command: CommandObject, bot: Bot):
    if not command.args:
        await message.delete()
        return
    link = command.args
    if not link.startswith(('http://', 'https://')):
        await message.delete()
        return
    await message.delete()
    await process_conversion(link=link, choice_str='voice', bot=bot, chat_id=message.chat.id)