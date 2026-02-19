from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import LeadProfile


async def upsert_lead_profile(
    session: AsyncSession,
    user_id: int,
    debt_amount: int | None,
    creditors_count: int | None,
    overdue_months: int | None,
    income: int | None,
    assets: str,
    region: str,
    contact_name: str | None = None,
    contact_phone: str | None = None,
) -> LeadProfile:
    result = await session.execute(
        select(LeadProfile).where(LeadProfile.user_id == user_id)
    )
    profile = result.scalar_one_or_none()
    if profile:
        profile.debt_amount = debt_amount
        profile.creditors_count = creditors_count
        profile.overdue_months = overdue_months
        profile.income = income
        profile.assets = assets
        profile.region = region
        if contact_name is not None:
            profile.contact_name = contact_name
        if contact_phone is not None:
            profile.contact_phone = contact_phone
        return profile
    profile = LeadProfile(
        user_id=user_id,
        debt_amount=debt_amount,
        creditors_count=creditors_count,
        overdue_months=overdue_months,
        income=income,
        assets=assets,
        region=region,
        contact_name=contact_name,
        contact_phone=contact_phone,
    )
    session.add(profile)
    await session.flush()
    return profile
