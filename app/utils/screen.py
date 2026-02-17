from __future__ import annotations

from typing import Optional

from aiogram.types import CallbackQuery, Message


# Храним id «актуального экрана» на чат — чтобы удалять устаревшие сообщения бота.
_LAST_SCREEN_MESSAGE_ID: dict[int, int] = {}


async def _delete_safe(message: Message, message_id: int) -> None:
    try:
        await message.bot.delete_message(chat_id=message.chat.id, message_id=message_id)
    except Exception:
        pass


async def set_screen(
    message: Message,
    text: str,
    *,
    reply_markup=None,
    parse_mode: Optional[str] = None,
    remove_prev: bool = True,
) -> Message:
    """
    Устанавливает «экран»: удаляет предыдущий экран бота в чате и отправляет новый.
    """
    if remove_prev:
        prev_id = _LAST_SCREEN_MESSAGE_ID.get(message.chat.id)
        if prev_id:
            await _delete_safe(message, prev_id)

    sent = await message.answer(text, reply_markup=reply_markup, parse_mode=parse_mode)
    _LAST_SCREEN_MESSAGE_ID[message.chat.id] = sent.message_id
    return sent


async def edit_screen(
    query: CallbackQuery,
    text: str,
    *,
    reply_markup=None,
    parse_mode: Optional[str] = None,
) -> None:
    """
    Редактирует текущее сообщение-экран (предпочтительно, чтобы чат не засорялся).
    Если редактирование невозможно — создаёт новый экран через set_screen().
    """
    msg = query.message
    if not msg:
        return
    try:
        await msg.edit_text(text, reply_markup=reply_markup, parse_mode=parse_mode)
        _LAST_SCREEN_MESSAGE_ID[msg.chat.id] = msg.message_id
    except Exception:
        await set_screen(msg, text, reply_markup=reply_markup, parse_mode=parse_mode)

