from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Client, ClientDocument, ClientPayment, ClientTask, Notification, Stage


async def get_client_by_user_id(
    session: AsyncSession, user_id: int
) -> Client | None:
    result = await session.execute(select(Client).where(Client.user_id == user_id))
    return result.scalar_one_or_none()


async def get_client_stage(
    session: AsyncSession, stage_id: int | None
) -> Stage | None:
    if not stage_id:
        return None
    result = await session.execute(select(Stage).where(Stage.id == stage_id))
    return result.scalar_one_or_none()


async def list_client_tasks(
    session: AsyncSession, client_id: int
) -> list[ClientTask]:
    result = await session.execute(
        select(ClientTask).where(ClientTask.client_id == client_id)
    )
    return list(result.scalars().all())


async def list_client_documents(
    session: AsyncSession, client_id: int
) -> list[ClientDocument]:
    result = await session.execute(
        select(ClientDocument).where(ClientDocument.client_id == client_id)
    )
    return list(result.scalars().all())


async def list_client_payments(
    session: AsyncSession, client_id: int
) -> list[ClientPayment]:
    result = await session.execute(
        select(ClientPayment).where(ClientPayment.client_id == client_id)
    )
    return list(result.scalars().all())


async def list_client_notifications(
    session: AsyncSession, client_id: int
) -> list[Notification]:
    result = await session.execute(
        select(Notification).where(Notification.client_id == client_id)
    )
    return list(result.scalars().all())
