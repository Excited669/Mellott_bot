# keyboards/inline.py

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def get_conversion_keyboard(link: str) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(text="🎵 MP3 файл", callback_data=f"mp3::{link}"),
            InlineKeyboardButton(text="🗣️ Голосовое сообщение", callback_data=f"voice::{link}")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)