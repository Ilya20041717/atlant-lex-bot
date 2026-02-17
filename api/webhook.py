# Vercel serverless: POST /api/webhook — приём обновлений от Telegram (webhook).
import asyncio
import json
import os
import sys

# Корень проекта в PATH для импорта app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from http.server import BaseHTTPRequestHandler


def _run_async(coro):
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)


async def _process_update(body: bytes) -> None:
    from aiogram.types import Update

    from app.bot_app import create_bot_and_dispatcher, init_app

    await init_app()
    bot, dp = create_bot_and_dispatcher()
    data = json.loads(body.decode("utf-8"))
    update = Update.model_validate(data)
    await dp.feed_update(bot, update)


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path.rstrip("/") != "/api/webhook":
            self.send_response(404)
            self.end_headers()
            return
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)
        try:
            _run_async(_process_update(body))
        except Exception:
            self.send_response(500)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"Internal error")
            return
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"OK")

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"BINC LEXA webhook endpoint. POST only.")
