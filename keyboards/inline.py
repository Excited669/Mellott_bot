# keyboards/inline.py
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def get_conversion_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(text="🎵 MP3 (320kbps)", callback_data="mp3"),
            InlineKeyboardButton(text="🗣️ Голосовое", callback_data="voice")
        ],
        [
            InlineKeyboardButton(text="🎬 MP4 (Исходное качество)", callback_data="mp4")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)