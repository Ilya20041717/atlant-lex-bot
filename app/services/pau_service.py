from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx

from app.config import settings


@dataclass(frozen=True)
class PauClientConfig:
    base_url: str
    login: str
    password: str
    category: str
    default_court_name: str


def _pau_enabled() -> bool:
    return bool(settings.pau_base_url and settings.pau_login and settings.pau_password)


def get_pau_config() -> PauClientConfig | None:
    if not _pau_enabled():
        return None
    return PauClientConfig(
        base_url=settings.pau_base_url.rstrip("/"),
        login=settings.pau_login,
        password=settings.pau_password,
        category=settings.pau_category or "customer",
        default_court_name=settings.pau_default_court_name,
    )


async def pau_auth() -> str | None:
    """
    Получить токен доступа ПАУ (Витрина данных).
    По Swagger: POST {base}/Auth?login=...&category=... + form password=...
    Ответ: {"token": "..."}
    """
    cfg = get_pau_config()
    if not cfg:
        return None
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            r = await client.post(
                f"{cfg.base_url}/Auth",
                params={"login": cfg.login, "category": cfg.category},
                data={"password": cfg.password},
                headers={"Accept": "application/json"},
            )
            if r.status_code != 200:
                return None
            data = r.json()
            token = (data or {}).get("token")
            return token if isinstance(token, str) and token else None
    except Exception:
        return None


async def pau_registrate_bankruptcy_petition(
    *,
    debtor_name: str,
    debtor_category: str = "citizen",
    court_name: str | None = None,
    debtor_inn: str | None = None,
    debtor_snils: str | None = None,
    debtor_ogrn: str | None = None,
) -> dict[str, Any] | None:
    """
    Записать в ПАУ информацию о поданном заявлении.
    Минимум по Swagger: court[name], debtor[category], debtor[name]
    Возвращает JSON ответа (обычно {"ok": true/false, "message": ...})
    """
    cfg = get_pau_config()
    if not cfg:
        return None

    token = await pau_auth()
    if not token:
        return None

    params: dict[str, Any] = {
        "court[name]": court_name or cfg.default_court_name,
        "debtor[category]": debtor_category,
        "debtor[name]": debtor_name,
    }
    if debtor_inn:
        params["debtor[inn]"] = debtor_inn
    if debtor_snils:
        params["debtor[snils]"] = debtor_snils
    if debtor_ogrn:
        params["debtor[ogrn]"] = debtor_ogrn

    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            r = await client.post(
                f"{cfg.base_url}/RegistrateBankruptcyPetition",
                params=params,
                headers={
                    "Accept": "application/json",
                    "ama-datamart-access-token": token,
                },
            )
            if r.status_code != 200:
                return None
            return r.json()
    except Exception:
        return None


async def pau_get_changed_procedures(*, revision_greater_than: int = 0, limit: int = 1000, case_number: str = "") -> dict[str, Any] | None:
    """
    Прочитать список изменённых процедур (как в Swagger /GetChangedProcedures).
    """
    cfg = get_pau_config()
    if not cfg:
        return None
    token = await pau_auth()
    if not token:
        return None
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            r = await client.post(
                f"{cfg.base_url}/GetChangedProcedures",
                params={
                    "ama-dm-revision-greater-than": revision_greater_than,
                    "limit": limit,
                    "procedure[case_number]": case_number,
                },
                headers={"Accept": "application/json", "ama-datamart-access-token": token},
            )
            if r.status_code != 200:
                return None
            return r.json()
    except Exception:
        return None


async def pau_download_procedure_info(*, id_mprocedure: str | int) -> str | dict[str, Any] | None:
    """
    Скачать информацию о процедуре (Swagger /DownloadProcedureInfo).
    Схема ответа не указана; возвращаем JSON, если он есть, иначе текст.
    """
    cfg = get_pau_config()
    if not cfg:
        return None
    token = await pau_auth()
    if not token:
        return None
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            r = await client.post(
                f"{cfg.base_url}/DownloadProcedureInfo",
                params={"id_MProcedure": id_mprocedure},
                headers={"ama-datamart-access-token": token},
            )
            if r.status_code != 200:
                return None
            # может быть JSON или файл/текст
            ctype = (r.headers.get("content-type") or "").lower()
            if "application/json" in ctype:
                return r.json()
            return r.text
    except Exception:
        return None

