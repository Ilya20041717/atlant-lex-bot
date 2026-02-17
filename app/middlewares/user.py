from aiogram import BaseMiddleware

from app.config import settings
from app.repositories.user_repo import get_or_create_user


class UserMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        session = data.get("session")
        tg_user = data.get("event_from_user")
        if session and tg_user:
            user = await get_or_create_user(
                session=session,
                tg_id=tg_user.id,
                org_id=settings.default_org_id,
            )
            data["db_user"] = user
            data["role"] = user.role
        return await handler(event, data)
