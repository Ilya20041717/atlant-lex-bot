from aiogram import Router, F

from app.constants import Buttons, Roles
from app.content.stages import STAGES
from app.keyboards.menus import client_menu
from app.services.client_service import (
    get_client_cabinet_data,
    get_client_documents,
    get_client_notifications,
    get_client_payments,
)
from app.utils.auto_delete import reply_ephemeral
from app.utils.formatters import (
    format_client_cabinet,
    format_documents,
    format_notifications,
    format_payments,
)
from app.utils.permissions import RoleFilter


router = Router()


@router.message(RoleFilter(Roles.CLIENT), F.text == Buttons.CLIENT_CABINET)
async def show_client_cabinet(message, session, db_user):
    data = await get_client_cabinet_data(session, db_user.id)
    text = format_client_cabinet(
        data["client"] if data else None,
        data["stage"] if data else None,
        data["tasks"] if data else [],
    )
    await reply_ephemeral(message, text, reply_markup=client_menu())


@router.message(RoleFilter(Roles.CLIENT), F.text == Buttons.CLIENT_STAGES)
async def show_stages(message):
    lines = ["Этапы процедуры:"]
    for stage in STAGES:
        lines.append(
            f"\n{stage['title']}\n"
            f"Описание: {stage['description']}\n"
            f"Действия клиента: {stage['client_actions']}\n"
            f"Сроки: {stage['eta_text']}"
        )
    await reply_ephemeral(message, "\n".join(lines), reply_markup=client_menu())


@router.message(RoleFilter(Roles.CLIENT), F.text == Buttons.CLIENT_DOCS)
async def show_documents(message, session, db_user):
    data = await get_client_documents(session, db_user.id)
    if not data:
        text = (
            "Данные клиента не найдены. Документы появятся после подтверждения менеджером. "
            "Общий список документов для процедуры: паспорт, справки о доходах, "
            "список кредиторов, документы на имущество."
        )
    else:
        text = format_documents(data["documents"])
        text += "\n\nЗагрузка документов будет доступна позже."
    await reply_ephemeral(message, text, reply_markup=client_menu())


@router.message(RoleFilter(Roles.CLIENT), F.text == Buttons.CLIENT_REMINDERS)
async def show_reminders(message, session, db_user):
    data = await get_client_notifications(session, db_user.id)
    if not data:
        text = (
            "Данные клиента не найдены. Напоминания появятся после подключения кабинета. "
            "Пока вы можете уточнять сроки и действия у менеджера."
        )
    else:
        text = format_notifications(data["notifications"])
    await reply_ephemeral(message, text, reply_markup=client_menu())


@router.message(RoleFilter(Roles.CLIENT), F.text == Buttons.CLIENT_FINANCE)
async def show_finance(message, session, db_user):
    data = await get_client_payments(session, db_user.id)
    if not data:
        text = (
            "Данные клиента не найдены. Финансовый раздел появится после заключения договора. "
            "Стоимость и график платежей согласуются с менеджером."
        )
    else:
        text = format_payments(data["client"], data["payments"])
    await reply_ephemeral(message, text, reply_markup=client_menu())

