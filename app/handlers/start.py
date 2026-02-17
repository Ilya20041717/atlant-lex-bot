import os

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile

from app.content.premium import START_CAPTION, START_MESSAGE
from app.config import settings
from app.keyboards.menus import start_menu


router = Router()


@router.message(CommandStart())
async def cmd_start(message, state: FSMContext):
    await state.clear()
    # Если задано стартовое изображение — отправляем его с подписью
    if settings.start_image_file_id:
        await message.answer_photo(
            photo=settings.start_image_file_id,
            caption=START_CAPTION,
            reply_markup=start_menu(),
            parse_mode="Markdown",
        )
        await message.answer(START_MESSAGE, reply_markup=start_menu(), parse_mode="Markdown")
        return

    if settings.start_image_path and os.path.exists(settings.start_image_path):
        await message.answer_photo(
            photo=FSInputFile(settings.start_image_path),
            caption=START_CAPTION,
            reply_markup=start_menu(),
            parse_mode="Markdown",
        )
        await message.answer(START_MESSAGE, reply_markup=start_menu(), parse_mode="Markdown")
        return

    await message.answer(START_MESSAGE, reply_markup=start_menu(), parse_mode="Markdown")
