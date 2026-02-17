from aiogram import Router, F

from app.constants import Roles
from app.keyboards.menus import employee_menu
from app.utils.auto_delete import reply_ephemeral
from app.utils.permissions import RoleFilter


router = Router()


@router.message(RoleFilter(Roles.EMPLOYEE), F.text)
async def employee_any(message):
    """Любая кнопка в режиме сотрудника — общая информация."""
    await reply_ephemeral(
        message,
        "Интерфейс сотрудников пока недоступен. Используйте «Главное меню» для возврата.",
        reply_markup=employee_menu(),
    )
