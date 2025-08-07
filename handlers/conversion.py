from aiogram import types, F, Router, Bot
from keyboards.inline import get_conversion_keyboard
from services.converter import process_conversion

router = Router()

@router.message(F.chat.type == "private", F.text.startswith(('http://', 'https://')))
async def process_link(message: types.Message):
    link = message.text
    await message.reply("Отлично! Теперь выбери формат:", reply_markup=get_conversion_keyboard(link))

@router.callback_query(F.data.contains('::'))
async def process_choice(callback: types.CallbackQuery, bot: Bot):
    choice_str, link = callback.data.split('::', 1)
    await callback.message.delete()
    working_message = await callback.message.answer("⏳ Уже работаю над этим...")
    await process_conversion(link=link, choice_str=choice_str, bot=bot, chat_id=callback.message.chat.id)
    await working_message.delete()