#!/usr/bin/env python3
"""
Устанавливает приветствие в профиле бота (видно до нажатия «Старт»).
Запуск один раз: из корня проекта: python scripts/set_bot_welcome.py
"""
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv
import httpx

load_dotenv()

from app.content.premium import BOT_DESCRIPTION, BOT_SHORT_DESCRIPTION


async def main():
    token = os.getenv("BOT_TOKEN")
    if not token:
        print("В .env не задан BOT_TOKEN")
        sys.exit(1)
    short = BOT_SHORT_DESCRIPTION[:120]
    desc = BOT_DESCRIPTION[:512]
    async with httpx.AsyncClient(timeout=15.0) as client:
        for name, method, param, text in (
            ("Short description (до 120 символов)", "setMyShortDescription", "short_description", short),
            ("Description (профиль)", "setMyDescription", "description", desc),
        ):
            r = await client.get(
                f"https://api.telegram.org/bot{token}/{method}",
                params={param: text},
            )
            ok = r.json().get("ok", False)
            print(f"✓ {name}: установлено" if ok else f"✗ {name}: {r.text}")
    print("\nГотово. Откройте бота в Telegram — приветствие видно до нажатия «Запустить».")


if __name__ == "__main__":
    asyncio.run(main())
