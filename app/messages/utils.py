import os
import re

from typing import Tuple, Optional


def get_file_path(category: str, chat_id: int, message_id: int) -> str:
    return f"files/{category}/{chat_id}/{message_id}"


def store_file(file_path: str, file_data: bytes):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "wb") as f:
        f.write(file_data)


def load_file(file_path: str) -> bytes:
    with open(file_path, "rb") as f:
        return f.read()


def try_get_file(
    chat_id: int, message_id: int, categories=("photo", "voice")
) -> Tuple[Optional[bytes], str]:
    for category in categories:
        file_path = get_file_path(category, chat_id, message_id)
        try:
            return load_file(file_path), category
        except FileNotFoundError:
            pass
    return None, ""


def contains_laughter(text: str) -> bool:
    """
    Detect if a text message contains basic laughter expressions.
    Returns True if laughter is detected, False otherwise.
    """
    laughter_patterns = [
        # Basic patterns with repeating 'a'
        r"[ax]a{2,}",  # xaa, axa, xaaa, etc.
        r"[χα]α{2,}",  # χαα, αχα, χααα, etc.
        r"[ah]a{2,}",  # haa, aha, haaa, etc.
        # Alternating patterns
        r"[ax][ax]+a",  # xaxa, axax, xaxxa, etc.
        r"[χα][χα]+α",  # χαχα, αχαχ, χαχχα, etc.
        r"[ah][ah]+a",  # haha, ahah, hahha, etc.
    ]

    combined_pattern = "|".join(laughter_patterns)
    return bool(re.search(combined_pattern, text.lower()))
