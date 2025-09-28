import os
from typing import Tuple, Optional

def get_file_path(category: str, chat_id: int, message_id: int) -> str:
    return f"files/{category}/{chat_id}/{message_id}"

def store_file(file_path: str, file_data: bytes):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'wb') as f:
        f.write(file_data)

def load_file(file_path: str) -> bytes:
    with open(file_path, 'rb') as f:
        return f.read()

def try_get_file(chat_id: int, message_id: int, categories=("photo", "voice")) -> Tuple[Optional[bytes], str]:
    for category in categories:
        file_path = get_file_path(category, chat_id, message_id)
        try:
            return load_file(file_path), category
        except FileNotFoundError:
            pass
    return None, ""

