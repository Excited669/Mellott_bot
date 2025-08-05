from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def get_conversion_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(text="🎵 MP3 файл", callback_data="convert_to_mp3"),
            InlineKeyboardButton(text="🗣️ Голосовое сообщение", callback_data="convert_to_voice")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)