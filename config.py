import os
from pathlib import Path

APP_NAME = "Secure Notes"
VERSION = "1.0.0"
DATA_DIR = Path.home() / ".secure_notes"
DATA_FILE = DATA_DIR / "notes.enc"
SALT_SIZE = 32
KEY_SIZE = 32
ITERATIONS = 100_000
