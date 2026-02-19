from dataclasses import dataclass
import os

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    bot_token: str
    db_url: str
    agency_name: str
    default_org_id: int
    delete_message_after_seconds: int
    openai_api_key: str  # пустая строка = ИИ отключён
    openai_model: str
    openai_max_tokens: int
    openai_assistant_id: str  # если задан — бот использует Assistants API (файлы, база знаний)
    ai_system_prompt_extra: str  # доп. инструкции к системному промпту (через .env)
    deepseek_api_key: str
    deepseek_base_url: str
    deepseek_model: str
    ai_provider: str  # auto|openai|deepseek|ollama|none
    ollama_base_url: str
    ollama_model: str
    start_image_file_id: str
    start_image_path: str

    # ПАУ (Витрина данных)
    pau_base_url: str
    pau_login: str
    pau_password: str
    pau_category: str  # customer|manager|partner|viewer
    pau_default_court_name: str


def get_settings() -> Settings:
    bot_token = os.getenv("BOT_TOKEN")
    if not bot_token:
        raise RuntimeError("BOT_TOKEN is required")
    db_url = os.getenv("DB_URL") or os.getenv("DATABASE_URL") or "sqlite+aiosqlite:///./data/app.db"
    if db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    agency_name = os.getenv(
        "AGENCY_NAME",
        "Агентство по банкротству физических лиц",
    )
    default_org_id = int(os.getenv("DEFAULT_ORG_ID", "1"))
    delete_after = int(os.getenv("DELETE_MESSAGE_AFTER_SECONDS", "60"))
    openai_api_key = os.getenv("OPENAI_API_KEY", "").strip()
    openai_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip()
    openai_max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", "500"))
    openai_assistant_id = os.getenv("OPENAI_ASSISTANT_ID", "").strip()
    ai_system_prompt_extra = os.getenv("AI_SYSTEM_PROMPT_EXTRA", "").strip()
    deepseek_api_key = os.getenv("DEEPSEEK_API_KEY", "").strip()
    deepseek_base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1").strip()
    deepseek_model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat").strip()

    ai_provider = os.getenv("AI_PROVIDER", "auto").strip().lower()
    ollama_base_url = os.getenv("OLLAMA_BASE_URL", "").strip()
    ollama_model = os.getenv("OLLAMA_MODEL", "").strip()
    start_image_file_id = os.getenv("START_IMAGE_FILE_ID", "").strip()
    start_image_path = os.getenv("START_IMAGE_PATH", "").strip()

    pau_base_url = os.getenv("PAU_BASE_URL", "").strip()
    pau_login = os.getenv("PAU_LOGIN", "").strip()
    pau_password = os.getenv("PAU_PASSWORD", "").strip()
    pau_category = os.getenv("PAU_CATEGORY", "customer").strip().lower()
    pau_default_court_name = os.getenv("PAU_DEFAULT_COURT_NAME", "").strip()

    return Settings(
        bot_token=bot_token,
        db_url=db_url,
        agency_name=agency_name,
        default_org_id=default_org_id,
        delete_message_after_seconds=delete_after,
        openai_api_key=openai_api_key,
        openai_model=openai_model,
        openai_max_tokens=openai_max_tokens,
        openai_assistant_id=openai_assistant_id,
        ai_system_prompt_extra=ai_system_prompt_extra,
        deepseek_api_key=deepseek_api_key,
        deepseek_base_url=deepseek_base_url,
        deepseek_model=deepseek_model,
        ai_provider=ai_provider,
        ollama_base_url=ollama_base_url,
        ollama_model=ollama_model,
        start_image_file_id=start_image_file_id,
        start_image_path=start_image_path,
        pau_base_url=pau_base_url,
        pau_login=pau_login,
        pau_password=pau_password,
        pau_category=pau_category,
        pau_default_court_name=pau_default_court_name,
    )


settings = get_settings()
