import asyncio
import os
import uuid
from aiogram import Bot
from aiogram.types import FSInputFile
from utils.helpers import sanitize_filename

async def process_conversion(link: str, choice_str: str, bot: Bot, chat_id: int):
    choice = 'convert_to_mp3' if choice_str == 'mp3' else 'convert_to_voice'

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
            await bot.send_audio(chat_id, FSInputFile(output_path, filename=f"{video_title}.mp3"))

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
            await bot.send_voice(chat_id, FSInputFile(final_ogg_path))

    except Exception as e:
        await bot.send_message(chat_id, f"❌ Ошибка при обработке ссылки `{link}`.\n`{e}`")
    finally:
        for file_path in files_to_delete:
            if os.path.exists(file_path):
                os.remove(file_path)