from aiogram import Dispatcher, Router
from . import start, conversion

def register_handlers(dp: Dispatcher):
    dp.include_router(start.router)
    dp.include_router(conversion.router)