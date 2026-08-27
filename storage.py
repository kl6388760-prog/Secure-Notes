import json
import os
from config import DATA_DIR, DATA_FILE
from crypto import encrypt, decrypt

def init_storage():
    DATA_DIR.mkdir(exist_ok=True)
    if not DATA_FILE.exists():
        with open(DATA_FILE, 'w') as f:
            json.dump({}, f)  # пустой словарь

def load_notes(password: str):
    """
    Возвращает:
    - словарь заметок (может быть пустым), если расшифровка успешна
    - None, если файл не существует или повреждён (первый запуск)
    - "WRONG_PASSWORD", если пароль неверный (расшифровка не удалась)
    """
    if not DATA_FILE.exists():
        return None

    with open(DATA_FILE, 'r') as f:
        enc_data = json.load(f)

    if "notes" not in enc_data:
        return None  # повреждённый файл

    try:
        json_str = decrypt(enc_data["notes"], password)
        return json.loads(json_str)
    except:
        # Не удалось расшифровать — скорее всего, неверный пароль
        return "WRONG_PASSWORD"

def save_notes(notes: dict, password: str):
    json_str = json.dumps(notes, ensure_ascii=False, indent=2)
    enc = encrypt(json_str, password)
    with open(DATA_FILE, 'w') as f:
        json.dump({"notes": enc}, f)
