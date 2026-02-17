from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants import Roles
from app.models import User


async def get_user_by_tg_id(session: AsyncSession, tg_id: int) -> User | None:
    result = await session.execute(select(User).where(User.tg_id == tg_id))
    return result.scalar_one_or_none()


async def get_or_create_user(
    session: AsyncSession, tg_id: int, org_id: int
) -> User:
    user = await get_user_by_tg_id(session, tg_id)
    if user:
        return user
    user = User(tg_id=tg_id, role=Roles.UNKNOWN, org_id=org_id)
    session.add(user)
    await session.flush()
    return user


async def set_user_role(session: AsyncSession, user_id: int, role: str) -> None:
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        return
    user.role = role
