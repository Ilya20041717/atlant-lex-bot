import re


def parse_int(text: str) -> int | None:
    digits = re.sub(r"[^\d]", "", text or "")
    if not digits:
        return None
    return int(digits)
