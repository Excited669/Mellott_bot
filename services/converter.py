# services/converter.py
import asyncio
import logging
import os
import uuid
from aiogram import Bot
from aiogram.types import FSInputFile
from utils.helpers import sanitize_filename


async def process_conversion(link: str, choice: str, bot: Bot, chat_id: int, caption: str | None = None) -> bool:
    unique_id = str(uuid.uuid4())
    files_to_delete = []

    try:
        logging.info(f"[{chat_id}] Начало обработки: {choice} для {link}")
        proc_title = await asyncio.create_subprocess_shell(
            f'yt-dlp --get-title "{link}"',
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout_title, stderr_title = await proc_title.communicate()
        if proc_title.returncode != 0:
            raise Exception(f"Не удалось получить название видео: {stderr_title.decode(errors='ignore')}")

        video_title = stdout_title.decode().strip()
        sanitized_title = sanitize_filename(video_title)
        logging.info(f"[{chat_id}] Получено название: {video_title}")

        if choice == 'mp3':
            output_path = f"downloads/{sanitized_title}.mp3"
            files_to_delete.append(output_path)

            # Команда для максимального качества MP3
            command = f'--extract-audio --audio-format mp3 --ppa "ffmpeg:-b:a 320k"'
            proc = await asyncio.create_subprocess_shell(
                f'yt-dlp {command} -o "{output_path}" "{link}"',
                stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            _, stderr = await proc.communicate()
            if proc.returncode != 0: raise Exception(f"yt-dlp ошибка (mp3): {stderr.decode(errors='ignore')}")

            await bot.send_audio(chat_id, FSInputFile(output_path, filename=f"{video_title}.mp3"), caption=caption)

        elif choice == 'voice':
            temp_mp3_path = f"downloads/{unique_id}.mp3"
            final_ogg_path = f"downloads/{unique_id}.ogg"
            files_to_delete.extend([temp_mp3_path, final_ogg_path])

            command = '--extract-audio --audio-format mp3 --audio-quality 0'
            proc_dl = await asyncio.create_subprocess_shell(
                f'yt-dlp {command} -o "{temp_mp3_path}" "{link}"',
                stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            _, stderr_dl = await proc_dl.communicate()
            if proc_dl.returncode != 0: raise Exception(
                f"Ошибка скачивания аудио для ГС: {stderr_dl.decode(errors='ignore')}")

            proc_conv = await asyncio.create_subprocess_shell(
                f'ffmpeg -i "{temp_mp3_path}" -c:a libopus "{final_ogg_path}"',
                stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            _, stderr_conv = await proc_conv.communicate()
            if proc_conv.returncode != 0: raise Exception(
                f"Ошибка конвертации в OGG: {stderr_conv.decode(errors='ignore')}")

            await bot.send_voice(chat_id, FSInputFile(final_ogg_path))

        elif choice == 'mp4':
            output_path = f"downloads/{sanitized_title}.mp4"
            files_to_delete.append(output_path)

            # Команда для скачивания видео в исходном качестве без перекодирования
            command = '--remux-video mp4'
            proc_dl = await asyncio.create_subprocess_shell(
                f'yt-dlp {command} -o "{output_path}" "{link}"',
                stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            _, stderr_dl = await proc_dl.communicate()
            if proc_dl.returncode != 0: raise Exception(
                f"Ошибка скачивания видео (mp4): {stderr_dl.decode(errors='ignore')}")

            await bot.send_video(chat_id, FSInputFile(output_path, filename=f"{video_title}.mp4"), caption=caption)

        return True

    except Exception as e:
        logging.error(f"[{chat_id}] Ошибка при обработке {link}: {e}")
        await bot.send_message(chat_id, "❌ Произошла ошибка, не удалось обработать ссылку.")
        return False
    finally:
        for f in files_to_delete:
            if os.path.exists(f):
                os.remove(f)
        logging.info(f"[{chat_id}] Конвертация завершена, временные файлы удалены.")