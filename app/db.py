from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy import select

from app.config import settings
from app.content.stages import STAGES


Base = declarative_base()
engine = create_async_engine(settings.db_url, echo=False, future=True)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def init_db() -> None:
    from app import models  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with SessionLocal() as session:
        await _ensure_default_org(session)
        await _seed_stages(session)
        await session.commit()


async def _ensure_default_org(session: AsyncSession) -> None:
    from app.models import Organization

    result = await session.execute(
        select(Organization).where(Organization.id == settings.default_org_id)
    )
    org = result.scalar_one_or_none()
    if org:
        return
    session.add(
        Organization(
            id=settings.default_org_id,
            name=settings.agency_name,
        )
    )


async def _seed_stages(session: AsyncSession) -> None:
    from app.models import Stage

    for stage in STAGES:
        result = await session.execute(
            select(Stage).where(Stage.code == stage["code"])
        )
        existing = result.scalar_one_or_none()
        if existing:
            continue
        session.add(
            Stage(
                code=stage["code"],
                title=stage["title"],
                description=stage["description"],
                client_actions=stage["client_actions"],
                eta_text=stage["eta_text"],
            )
        )
