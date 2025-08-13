# utils/helpers.py
import re

def sanitize_filename(filename: str) -> str:
    """Удаляет недопустимые символы из имени файла."""
    return re.sub(r'[\\/*?:"<>|]', "", filename).strip()