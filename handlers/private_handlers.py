# handlers/private_handlers.py
from aiogram import types, F, Router, Bot
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keyboards.inline import get_conversion_keyboard
from services.converter import process_conversion

router = Router()


class UserState(StatesGroup):
    waiting_for_choice = State()


@router.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer(
        "👋 Привет! Я Mellot. Отправь мне ссылку, и я помогу тебе ее преобразовать."
    )


@router.message(F.chat.type == "private", F.text.startswith(('http://', 'https://')))
async def process_link_private(message: types.Message, state: FSMContext):
    await state.update_data(link=message.text)
    await state.set_state(UserState.waiting_for_choice)
    await message.reply("Отлично! Выбери формат:", reply_markup=get_conversion_keyboard())


@router.callback_query(UserState.waiting_for_choice, F.data.in_(['mp3', 'voice', 'mp4']))
async def process_choice_private(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    user_data = await state.get_data()
    link = user_data.get('link')
    choice = callback.data

    if not link:
        await callback.answer("Произошла ошибка, попробуйте отправить ссылку снова.", show_alert=True)
        return

    await callback.message.delete()
    working_message = await bot.send_message(callback.from_user.id, "⏳ Работаю над этим...")

    success = await process_conversion(link=link, choice=choice, bot=bot, chat_id=callback.from_user.id)

    await working_message.delete()

    if success:
        final_messages = {
            'mp3': "✅ Вот твой MP3 файл! Если захочешь что-то еще, присылай ссылку.",
            'voice': "✅ Готово! Твое голосовое сообщение. Присылай еще ссылки, если нужно.",
            'mp4': "✅ Твой MP4 файл готов. Захочешь еще видео - ты знаешь, что делать!"
        }
        await callback.message.answer(final_messages.get(choice, "✅ Готово!"))

    await state.clear()