import asyncio
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
        # Внутренние настройки TCPConnector (см. aiogram.client.session.aiohttp.AiohttpSession)
        try:
            self._connector_init["family"] = socket.AF_INET
            self._connector_init["ttl_dns_cache"] = 300
        except Exception:
            pass


async def main() -> None:
    await init_db()
    # Более устойчивый long-polling (иногда IPv6/сеть дают таймауты)
    bot = Bot(token=settings.bot_token, session=IPv4Session(timeout=75.0))
    dp = Dispatcher(storage=MemoryStorage())

    dp.update.middleware(DbSessionMiddleware(SessionLocal))
    dp.update.middleware(UserMiddleware())

    dp.include_router(start.router)
    dp.include_router(nare.router)
    dp.include_router(common.router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
