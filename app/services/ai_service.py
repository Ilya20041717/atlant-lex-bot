# ИИ-ответы с дисклеймером (не замена юристу)
from __future__ import annotations

import httpx
from openai import AsyncOpenAI

from app.config import settings

SYSTEM_PROMPT = (
    "Ты помощник бота юридической компании. Отвечай кратко, по делу, нейтрально. "
    "Не давай персональных правовых выводов и не заменяй консультацию юриста. "
    "Если вопрос сложный или персональный — рекомендуй обратиться к специалисту компании."
)

AI_DISCLAIMER = "\n\n_Это общая информация. Окончательное решение принимает специалист компании._"


async def ask_ai(user_text: str) -> str | None:
    """
    Отправляет вопрос ИИ и возвращает ответ.

    Провайдер выбирается через env:
    - AI_PROVIDER=auto (по умолчанию): OpenAI при наличии ключа, иначе DeepSeek при наличии ключа, иначе Ollama при наличии URL
    - AI_PROVIDER=openai|deepseek|ollama|none
    """
    try:
        provider = (settings.ai_provider or "auto").lower()
        if provider == "none":
            return None

        # auto: сначала OpenAI, затем DeepSeek, затем Ollama
        if provider in ("auto", "openai") and settings.openai_api_key:
            client = AsyncOpenAI(api_key=settings.openai_api_key)
            r = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_text},
                ],
                max_tokens=500,
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
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_text},
                ],
                max_tokens=500,
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
                            {"role": "system", "content": SYSTEM_PROMPT},
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
