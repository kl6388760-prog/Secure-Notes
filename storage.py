import json
import os
from config import DATA_DIR, DATA_FILE
from crypto import encrypt, decrypt

def init_storage():
    DATA_DIR.mkdir(exist_ok=True)
    if not DATA_FILE.exists():
        with open(DATA_FILE, 'w') as f:
            json.dump({}, f)  # пустой словарь

def load_notes(password: str) -> dict:
    if not DATA_FILE.exists():
        return {}
    with open(DATA_FILE, 'r') as f:
        enc_data = json.load(f)  # ожидаем {"notes": "зашифрованная строка"}
    if "notes" not in enc_data:
        return {}
    try:
        json_str = decrypt(enc_data["notes"], password)
        return json.loads(json_str)  # словарь {id: {title, content, date}}
    except:
        return {}  # неверный пароль или повреждённые данные

def save_notes(notes: dict, password: str):
    json_str = json.dumps(notes, ensure_ascii=False, indent=2)
    enc = encrypt(json_str, password)
    with open(DATA_FILE, 'w') as f:
        json.dump({"notes": enc}, f)
