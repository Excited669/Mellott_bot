from aiogram import types, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from utils.states import ConversionStates

router = Router()

@router.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "👋 Привет! Я Mellot — твой весёлый музыкальный робот-проводник.\n"
        "От меня ссылки из соцсетей превращаются в чистый MP3 за пару секунд! 🎧✨\n\n"
        "Просто отправь любую ссылку ниже ⬇️"
    )
    await state.set_state(ConversionStates.waiting_for_link)
