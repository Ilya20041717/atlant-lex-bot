from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.lead_repo import upsert_lead_profile


async def save_lead_survey(
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
) -> None:
    await upsert_lead_profile(
        session=session,
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
