import asyncio
from typing import TYPE_CHECKING

from app.config import settings

if TYPE_CHECKING:
    from aiogram import Bot


async def _delete_after(bot: "Bot", chat_id: int, message_id: int, seconds: int) -> None:
    await asyncio.sleep(seconds)
    try:
        await bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception:
        pass


async def reply_ephemeral(
    message,
    text: str,
    reply_markup=None,
    delete_after: int | None = None,
):
    """Отправляет ответ и удаляет его через delete_after секунд (исчезающее сообщение)."""
    sent = await message.answer(text, reply_markup=reply_markup)
    delay = delete_after if delete_after is not None else settings.delete_message_after_seconds
    if delay > 0:
        asyncio.create_task(
            _delete_after(sent.bot, sent.chat.id, sent.message_id, delay)
        )
    return sent
