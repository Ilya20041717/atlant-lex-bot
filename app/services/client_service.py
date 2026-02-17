from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.client_repo import (
    get_client_by_user_id,
    get_client_stage,
    list_client_documents,
    list_client_notifications,
    list_client_payments,
    list_client_tasks,
)


async def get_client_cabinet_data(session: AsyncSession, user_id: int):
    client = await get_client_by_user_id(session, user_id)
    if not client:
        return None
    stage = await get_client_stage(session, client.current_stage_id)
    tasks = await list_client_tasks(session, client.id)
    return {"client": client, "stage": stage, "tasks": tasks}


async def get_client_documents(session: AsyncSession, user_id: int):
    client = await get_client_by_user_id(session, user_id)
    if not client:
        return None
    documents = await list_client_documents(session, client.id)
    return {"client": client, "documents": documents}


async def get_client_payments(session: AsyncSession, user_id: int):
    client = await get_client_by_user_id(session, user_id)
    if not client:
        return None
    payments = await list_client_payments(session, client.id)
    return {"client": client, "payments": payments}


async def get_client_notifications(session: AsyncSession, user_id: int):
    client = await get_client_by_user_id(session, user_id)
    if not client:
        return None
    notifications = await list_client_notifications(session, client.id)
    return {"client": client, "notifications": notifications}
