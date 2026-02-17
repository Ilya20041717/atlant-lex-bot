from aiogram import Router
from aiogram.fsm.context import FSMContext

from app.content.premium import BACK_TO_MENU
from app.keyboards.menus import main_menu
from app.utils.screen import set_screen


router = Router()


@router.message()
async def fallback(message, state: FSMContext):
    """Любое необработанное сообщение — показываем главное меню."""
    await state.clear()
    await set_screen(message, BACK_TO_MENU, reply_markup=main_menu())
