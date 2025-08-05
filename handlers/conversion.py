import asyncio
import os
import uuid
from aiogram import types, F, Router, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile
from utils.states import ConversionStates
from keyboards.inline import get_conversion_keyboard
from utils.helpers import sanitize_filename

router = Router()

@router.message(ConversionStates.waiting_for_link, F.text.startswith(('http://', 'https://')))
async def process_link(message: types.Message, state: FSMContext):
    await state.update_data(link=message.text)
    await state.set_state(ConversionStates.waiting_for_choice)
    await message.reply("Отлично! Теперь выбери формат:", reply_markup=get_conversion_keyboard())

@router.message(ConversionStates.waiting_for_link)
async def process_wrong_link(message: types.Message):
    await message.reply("Пожалуйста, отправь корректную ссылку, которая начинается с http:// или https://")

@router.callback_query(ConversionStates.waiting_for_choice, F.data.in_(['convert_to_mp3', 'convert_to_voice']))
async def process_choice(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    await callback.message.edit_text(
        f"{callback.message.text}\n\nВыбрано: {'MP3' if callback.data == 'convert_to_mp3' else 'Голосовое сообщение'}")
    working_message = await callback.message.answer("⏳ Уже работаю над этим...")

    user_data = await state.get_data()
    link = user_data.get('link')
    choice = callback.data

    unique_id = str(uuid.uuid4())
    temp_mp3_path = f"downloads/{unique_id}.mp3"
    final_ogg_path = f"downloads/{unique_id}.ogg"
    files_to_delete = []

    try:
        proc_title = await asyncio.create_subprocess_shell(
            f'yt-dlp --get-title "{link}"',
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout_title, stderr_title = await proc_title.communicate()
        if proc_title.returncode != 0: raise Exception(f"Не удалось получить название видео: {stderr_title.decode()}")
        video_title = stdout_title.decode().strip()
        sanitized_title = sanitize_filename(video_title)

        if choice == 'convert_to_mp3':
            output_path = f"downloads/{sanitized_title}.mp3"
            files_to_delete.append(output_path)
            proc = await asyncio.create_subprocess_shell(
                f'yt-dlp --extract-audio --audio-format mp3 --audio-quality 0 -o "{output_path}" "{link}"',
                stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            _, stderr = await proc.communicate()
            if proc.returncode != 0: raise Exception(f"yt-dlp error: {stderr.decode()}")
            await bot.send_audio(callback.from_user.id, FSInputFile(output_path, filename=f"{video_title}.mp3"))
            success_message = "✅ Готово! Твой MP3-файл улетел в чат. Если захочешь ещё звуковых превращений — запусти меня снова! 😉🚀"

        elif choice == 'convert_to_voice':
            proc_download = await asyncio.create_subprocess_shell(
                f'yt-dlp --extract-audio --audio-format mp3 --audio-quality 0 -o "{temp_mp3_path}" "{link}"',
                stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            _, stderr_dl = await proc_download.communicate()
            if proc_download.returncode != 0: raise Exception(f"yt-dlp download error: {stderr_dl.decode()}")
            files_to_delete.append(temp_mp3_path)

            proc_convert = await asyncio.create_subprocess_shell(
                f'ffmpeg -i "{temp_mp3_path}" -c:a libopus "{final_ogg_path}"',
                stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            _, stderr_conv = await proc_convert.communicate()
            if proc_convert.returncode != 0: raise Exception(f"FFmpeg error: {stderr_conv.decode()}")
            files_to_delete.append(final_ogg_path)

            await bot.send_voice(callback.from_user.id, FSInputFile(final_ogg_path))
            success_message = "✅ Готово! Твое голосовое сообщение улетело в чат. Если захочешь ещё звуковых превращений — отправляй новую ссылку! 😉🚀"

        await bot.delete_message(chat_id=callback.from_user.id, message_id=working_message.message_id)
        await callback.message.answer(success_message)

    except Exception as e:
        await bot.delete_message(chat_id=callback.from_user.id, message_id=working_message.message_id)
        await callback.message.answer(f"❌ Ой, что-то пошло не так. Попробуйте еще раз.\n\n`Ошибка: {e}`")
    finally:
        for file_path in files_to_delete:
            if os.path.exists(file_path):
                os.remove(file_path)
        await state.set_state(ConversionStates.waiting_for_link)