"""Сборка Bot и Dispatcher для polling и webhook (в т.ч. Vercel)."""
import socket

from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.fsm.storage.memory import MemoryStorage

from app.config import settings
from app.db import SessionLocal, init_db
from app.handlers import common, nare, start
from app.middlewares.db import DbSessionMiddleware
from app.middlewares.user import UserMiddleware


class IPv4Session(AiohttpSession):
    """AiohttpSession, принудительно IPv4 (устойчивее на некоторых сетях)."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        try:
            self._connector_init["family"] = socket.AF_INET
            self._connector_init["ttl_dns_cache"] = 300
        except Exception:
            pass


async def init_app() -> None:
    """Инициализация БД (таблицы и сиды). Вызывать до создания диспетчера."""
    await init_db()


def create_bot_and_dispatcher() -> tuple[Bot, Dispatcher]:
    """Создаёт экземпляры Bot и Dispatcher с роутерами и middlewares."""
    bot = Bot(token=settings.bot_token, session=IPv4Session(timeout=75.0))
    dp = Dispatcher(storage=MemoryStorage())

    dp.update.middleware(DbSessionMiddleware(SessionLocal))
    dp.update.middleware(UserMiddleware())

    dp.include_router(start.router)
    dp.include_router(nare.router)
    dp.include_router(common.router)

    return bot, dp
