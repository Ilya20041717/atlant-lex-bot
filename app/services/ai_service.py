# ИИ-ответы с дисклеймером (не замена юристу)
from __future__ import annotations

import asyncio
import httpx
from openai import AsyncOpenAI

from app.config import settings

# Кэш thread_id по telegram user_id (для Assistants API — один диалог на пользователя)
_assistant_threads: dict[int, str] = {}

def _system_prompt() -> str:
    base = (
        "Ты внутренний консультант юридической компании ATLANT LEX. Отвечай кратко, по делу, нейтрально. "
        "Не давай персональных правовых выводов и не заменяй консультацию юриста. "
        "Если вопрос сложный или персональный — рекомендуй обратиться к специалисту ATLANT LEX."
    )
    extra = getattr(settings, "ai_system_prompt_extra", "") or ""
    if extra:
        return base + "\n\n" + extra
    return base


AI_DISCLAIMER = "\n\n_Это общая информация. Окончательное решение принимает специалист компании._"


async def _ask_openai_assistant(client: AsyncOpenAI, user_text: str, user_id: int) -> str | None:
    """Использует OpenAI Assistants API (ассистент с файлами/инструкциями)."""
    assistant_id = getattr(settings, "openai_assistant_id", "") or ""
    if not assistant_id:
        return None
    thread_id = _assistant_threads.get(user_id)
    if not thread_id:
        thread = await client.beta.threads.create()
        thread_id = thread.id
        _assistant_threads[user_id] = thread_id
    await client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=user_text,
    )
    run = await client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id,
    )
    max_wait = 60
    step = 0.5
    waited = 0.0
    while waited < max_wait:
        run = await client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
        if run.status == "completed":
            break
        if run.status == "failed" or run.status == "cancelled" or run.status == "expired":
            return None
        await asyncio.sleep(step)
        waited += step
    if run.status != "completed":
        return None
    messages = await client.beta.threads.messages.list(thread_id=thread_id, order="desc", limit=1)
    for msg in messages.data:
        if msg.role != "assistant":
            continue
        for block in msg.content or []:
            if hasattr(block, "text") and block.text and getattr(block.text, "value", None):
                return block.text.value.strip() + AI_DISCLAIMER
    return None


async def ask_ai(user_text: str, user_id: int | None = None) -> str | None:
    """
    Отправляет вопрос ИИ и возвращает ответ.
    user_id — telegram user id; нужен для Assistants API (один диалог на пользователя).

    Провайдер: AI_PROVIDER=openai|deepseek|ollama|none.
    Если задан OPENAI_ASSISTANT_ID — используется Assistants API (файлы, база знаний).
    """
    try:
        provider = (settings.ai_provider or "auto").lower()
        if provider == "none":
            return None

        # OpenAI: Assistants API (если задан assistant_id) или Chat Completions
        if provider in ("auto", "openai") and settings.openai_api_key:
            client = AsyncOpenAI(api_key=settings.openai_api_key)
            assistant_id = getattr(settings, "openai_assistant_id", "") or ""
            if assistant_id and user_id is not None:
                reply = await _ask_openai_assistant(client, user_text, user_id)
                if reply:
                    return reply
            # Иначе обычный чат (или ассистент не задан / без user_id)
            r = await client.chat.completions.create(
                model=settings.openai_model or "gpt-4o-mini",
                messages=[
                    {"role": "system", "content": _system_prompt()},
                    {"role": "user", "content": user_text},
                ],
                max_tokens=min(4096, max(100, getattr(settings, "openai_max_tokens", 500))),
            )
            if r.choices and r.choices[0].message.content:
                return r.choices[0].message.content.strip() + AI_DISCLAIMER

        if provider in ("auto", "deepseek") and settings.deepseek_api_key:
            base_url = settings.deepseek_base_url or "https://api.deepseek.com/v1"
            model = settings.deepseek_model or "deepseek-chat"
            client = AsyncOpenAI(api_key=settings.deepseek_api_key, base_url=base_url)
            r = await client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": _system_prompt()},
                    {"role": "user", "content": user_text},
                ],
                max_tokens=min(4096, max(100, getattr(settings, "openai_max_tokens", 500))),
            )
            if r.choices and r.choices[0].message.content:
                return r.choices[0].message.content.strip() + AI_DISCLAIMER

        if provider in ("auto", "ollama") and settings.ollama_base_url:
            model = settings.ollama_model or "llama3.1:8b-instruct"
            async with httpx.AsyncClient(timeout=30.0) as client:
                rr = await client.post(
                    settings.ollama_base_url.rstrip("/") + "/api/chat",
                    json={
                        "model": model,
                        "stream": False,
                        "messages": [
                            {"role": "system", "content": _system_prompt()},
                            {"role": "user", "content": user_text},
                        ],
                    },
                )
                if rr.status_code != 200:
                    return None
                data = rr.json()
                content = (data.get("message") or {}).get("content")
                if isinstance(content, str) and content.strip():
                    return content.strip() + AI_DISCLAIMER

    except Exception:
        return None
    return None
