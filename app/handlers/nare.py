# Обработчики: меню как в Nare + демо личного кабинета + ИИ (премиальные тексты)
import re

from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from app.constants import Buttons, FAQ_NARE
from app.content.premium import (
    ASK_AI_PROMPT,
    ASK_AI_UNAVAILABLE,
    CABINET_ASK_NAME,
    CABINET_ASK_PHONE,
    CABINET_DEMO_SCREEN,
    CABINET_PHONE_INVALID,
    CABINET_REQUIRED,
    CABINET_STATUS_SCREEN,
    CONTACT_MANAGER,
    FAQ_DISCLAIMER,
    FAQ_INTRO,
    NEXT_STAGES_TEXT,
    QUESTION_ASK,
    QUESTION_SENT,
    REQUEST_ACCEPTED,
    REQUEST_ASK_NAME,
    REQUEST_ASK_PHONE,
    REQUEST_PHONE_INVALID,
    UPLOAD_DOCS_PROMPT,
    UPLOAD_DOCS_RECEIVED,
    BACK_TO_MENU,
    PAU_ASK_CASE_NUMBER,
    PAU_CASE_LINKED,
    PAU_CASE_NOT_FOUND,
    PAU_TEMP_UNAVAILABLE,
    PAYMENTS_SCREEN,
    PAYMENT_DEMO_REQUISITES,
)
from app.keyboards.inline import pay_inline
from app.keyboards.menus import back_only, client_submenu, faq_menu, main_menu, phone_request_keyboard
from app.services.ai_service import ask_ai
from app.services.pau_service import (
    get_pau_config,
    pau_download_procedure_info,
    pau_get_changed_procedures,
    pau_registrate_bankruptcy_petition,
)
from app.states.nare import AskAI, AskQuestion, CabinetCase, CabinetPhone, RequestLead
from app.utils.screen import set_screen


router = Router()

_stored_phones: dict[int, str] = {}
_cabinet_users: dict[int, dict] = {}
_pau_enabled = get_pau_config() is not None


@router.message(F.text == Buttons.START)
async def show_main(message, state: FSMContext):
    await state.clear()
    await set_screen(message, BACK_TO_MENU, reply_markup=main_menu())


@router.message(F.text == Buttons.CONTACT_MANAGER)
async def contact_manager(message):
    await set_screen(message, CONTACT_MANAGER, reply_markup=main_menu(), parse_mode="Markdown")


@router.message(F.text == Buttons.FAQ)
async def show_faq_list(message):
    await set_screen(message, FAQ_INTRO, reply_markup=faq_menu())


@router.message(F.text.in_(FAQ_NARE))
async def faq_answer(message):
    text = FAQ_NARE[message.text] + FAQ_DISCLAIMER
    await set_screen(message, text, reply_markup=faq_menu(), parse_mode="Markdown")


@router.message(F.text == Buttons.BACK)
async def back_to_main(message, state: FSMContext):
    await state.clear()
    _cabinet_users.pop(message.chat.id, None)
    await set_screen(message, BACK_TO_MENU, reply_markup=main_menu())


@router.callback_query(F.data == "pay:demo")
async def pay_demo_callback(query: CallbackQuery):
    await query.message.answer(PAYMENT_DEMO_REQUISITES, parse_mode="Markdown")
    await query.answer()


# ——— Личный кабинет ———
@router.message(F.text == Buttons.CABINET)
async def cabinet_start(message, state: FSMContext):
    # Если пользователь уже “в кабинете” — показываем кабинет сразу (без повторного входа)
    cab = _cabinet_users.get(message.chat.id)
    if cab:
        text = CABINET_DEMO_SCREEN.format(name=cab.get("name", "Клиент"), phone=cab.get("phone", ""))
        await state.clear()
        await set_screen(message, text, reply_markup=client_submenu(), parse_mode="Markdown")
        return
    await state.set_state(CabinetPhone.phone)
    await set_screen(message, CABINET_ASK_PHONE, reply_markup=phone_request_keyboard())


@router.message(StateFilter(CabinetPhone.phone), F.text == Buttons.BACK)
async def cabinet_cancel(message, state: FSMContext):
    await state.clear()
    await set_screen(message, BACK_TO_MENU, reply_markup=main_menu(), remove_prev=False)


def _normalize_phone(phone: str) -> str:
    digits = re.sub(r"\D", "", phone or "")
    if len(digits) >= 10:
        return "+7" + digits[-10:] if digits[-10] != "7" else "+" + digits[-11:]
    return phone


@router.message(StateFilter(CabinetPhone.phone), F.contact)
async def cabinet_phone_contact(message, state: FSMContext):
    phone = _normalize_phone(message.contact.phone_number or "")
    _stored_phones[message.chat.id] = phone
    # чистим сообщение пользователя
    try:
        await message.delete()
    except Exception:
        pass
    await state.set_state(CabinetPhone.name)
    await set_screen(message, CABINET_ASK_NAME, reply_markup=back_only())


@router.message(StateFilter(CabinetPhone.phone), F.text)
async def cabinet_phone_text(message, state: FSMContext):
    phone = re.sub(r"\D", "", message.text or "")
    if len(phone) < 10 or len(phone) > 11:
        await set_screen(message, CABINET_PHONE_INVALID, reply_markup=phone_request_keyboard())
        return
    _stored_phones[message.chat.id] = _normalize_phone(message.text)
    try:
        await message.delete()
    except Exception:
        pass
    await state.set_state(CabinetPhone.name)
    await set_screen(message, CABINET_ASK_NAME, reply_markup=back_only())


@router.message(StateFilter(CabinetPhone.name), F.text == Buttons.BACK)
async def cabinet_cancel_name(message, state: FSMContext):
    _stored_phones.pop(message.chat.id, None)
    await state.clear()
    await set_screen(message, BACK_TO_MENU, reply_markup=main_menu())


@router.message(StateFilter(CabinetPhone.name), F.text)
async def cabinet_enter_name(message, state: FSMContext):
    name = (message.text or "").strip() or "Клиент"
    chat_id = message.chat.id
    phone = _stored_phones.pop(chat_id, "")
    _cabinet_users[chat_id] = {"name": name, "phone": phone}
    try:
        await message.delete()
    except Exception:
        pass
    await state.clear()
    text = CABINET_DEMO_SCREEN.format(name=name, phone=phone)
    await set_screen(message, text, reply_markup=client_submenu(), parse_mode="Markdown", remove_prev=False)


# ——— Оставить заявку ———
@router.message(F.text == Buttons.REQUEST)
async def request_start(message, state: FSMContext):
    await state.set_state(RequestLead.name)
    await set_screen(message, REQUEST_ASK_NAME, reply_markup=back_only())


@router.message(StateFilter(RequestLead.name), F.text == Buttons.BACK)
async def request_cancel_name(message, state: FSMContext):
    await state.clear()
    await set_screen(message, BACK_TO_MENU, reply_markup=main_menu())


@router.message(StateFilter(RequestLead.name), F.text)
async def request_phone_step(message, state: FSMContext):
    name = message.text.strip()
    chat_id = message.chat.id
    if chat_id in _stored_phones:
        _stored_phones.pop(chat_id, None)
        if _pau_enabled:
            await pau_registrate_bankruptcy_petition(debtor_name=name)
        await state.clear()
        await set_screen(message, REQUEST_ACCEPTED, reply_markup=main_menu(), parse_mode="Markdown")
        return
    await state.update_data(name=name)
    await state.set_state(RequestLead.phone)
    await set_screen(message, REQUEST_ASK_PHONE, reply_markup=phone_request_keyboard())


@router.message(StateFilter(RequestLead.phone), F.text == Buttons.BACK)
async def request_cancel_phone(message, state: FSMContext):
    await state.clear()
    await set_screen(message, BACK_TO_MENU, reply_markup=main_menu())


@router.message(StateFilter(RequestLead.phone), F.contact)
async def request_done_contact(message, state: FSMContext):
    data = await state.get_data()
    name = (data.get("name") or "").strip() or "Клиент"
    if _pau_enabled:
        await pau_registrate_bankruptcy_petition(debtor_name=name)
    try:
        await message.delete()
    except Exception:
        pass
    await state.clear()
    await set_screen(message, REQUEST_ACCEPTED, reply_markup=main_menu(), parse_mode="Markdown")


@router.message(StateFilter(RequestLead.phone), F.text)
async def request_done_text(message, state: FSMContext):
    phone = re.sub(r"\D", "", message.text or "")
    if len(phone) < 10 or len(phone) > 11:
        await set_screen(message, REQUEST_PHONE_INVALID, reply_markup=phone_request_keyboard())
        return
    data = await state.get_data()
    name = (data.get("name") or "").strip() or "Клиент"
    if _pau_enabled:
        await pau_registrate_bankruptcy_petition(debtor_name=name)
    try:
        await message.delete()
    except Exception:
        pass
    await state.clear()
    await set_screen(message, REQUEST_ACCEPTED, reply_markup=main_menu(), parse_mode="Markdown")


# ——— Задать вопрос ———
@router.message(F.text == Buttons.QUESTION)
async def question_start(message, state: FSMContext):
    await state.set_state(AskQuestion.text)
    await set_screen(message, QUESTION_ASK, reply_markup=back_only())


@router.message(StateFilter(AskQuestion.text), F.text == Buttons.BACK)
async def question_cancel(message, state: FSMContext):
    await state.clear()
    await set_screen(message, BACK_TO_MENU, reply_markup=main_menu())


@router.message(StateFilter(AskQuestion.text), F.text)
async def question_sent(message, state: FSMContext):
    await state.clear()
    try:
        await message.delete()
    except Exception:
        pass
    await set_screen(message, QUESTION_SENT, reply_markup=main_menu(), parse_mode="Markdown")


# ——— Личный кабинет (демо): статус и этапы ———
@router.message(F.text == Buttons.VIEW_STATUS)
async def view_status(message, state: FSMContext):
    cab = _cabinet_users.get(message.chat.id)
    if cab:
        if _pau_enabled:
            if not cab.get("pau_case_number"):
                await state.set_state(CabinetCase.case_number)
                await set_screen(message, PAU_ASK_CASE_NUMBER, reply_markup=back_only())
                return

            # Попытка прочитать статус из ПАУ
            changed = await pau_get_changed_procedures(limit=10, case_number=str(cab.get("pau_case_number", "")))
            items = (((changed or {}).get("Запрошенный_список_процедур")) or [])
            if not items:
                name = cab.get("name", "Клиент")
                text = CABINET_STATUS_SCREEN.format(name=name) + "\n\n" + PAU_TEMP_UNAVAILABLE
                await set_screen(message, text, reply_markup=client_submenu(), parse_mode="Markdown")
                return

            id_mprocedure = (items[0] or {}).get("id_MProcedure")
            if id_mprocedure is None:
                name = cab.get("name", "Клиент")
                text = CABINET_STATUS_SCREEN.format(name=name) + "\n\n" + PAU_TEMP_UNAVAILABLE
                await set_screen(message, text, reply_markup=client_submenu(), parse_mode="Markdown")
                return

            cab["pau_id_MProcedure"] = id_mprocedure
            info = await pau_download_procedure_info(id_mprocedure=id_mprocedure)
            # Не выводим весь JSON: показываем подтверждение, что данные получены.
            status_text = (
                "**Статус дела (ПАУ)**\n\n"
                f"Номер дела: {cab.get('pau_case_number')}\n"
                f"ID процедуры: {id_mprocedure}\n\n"
                "_Данные получены из ПАУ._"
            )
            await set_screen(message, status_text, reply_markup=client_submenu(), parse_mode="Markdown")
            return

        name = cab.get("name", "Клиент")
        text = CABINET_STATUS_SCREEN.format(name=name)
        await set_screen(message, text, reply_markup=client_submenu(), parse_mode="Markdown")
    else:
        await set_screen(message, CABINET_REQUIRED, reply_markup=main_menu())


@router.message(StateFilter(CabinetCase.case_number), F.text == Buttons.BACK)
async def pau_case_cancel(message, state: FSMContext):
    await state.clear()
    markup = client_submenu() if message.chat.id in _cabinet_users else main_menu()
    await set_screen(message, BACK_TO_MENU, reply_markup=markup)


@router.message(StateFilter(CabinetCase.case_number), F.text)
async def pau_case_set(message, state: FSMContext):
    cab = _cabinet_users.get(message.chat.id)
    if not cab:
        await state.clear()
        await set_screen(message, CABINET_REQUIRED, reply_markup=main_menu())
        return

    case_number = (message.text or "").strip()
    if not case_number:
        await set_screen(message, PAU_CASE_NOT_FOUND, reply_markup=back_only())
        return

    await set_screen(message, PAU_CASE_LINKED, reply_markup=back_only())
    changed = await pau_get_changed_procedures(limit=10, case_number=case_number)
    items = (((changed or {}).get("Запрошенный_список_процедур")) or [])
    if not items:
        await set_screen(message, PAU_CASE_NOT_FOUND, reply_markup=back_only())
        return

    id_mprocedure = (items[0] or {}).get("id_MProcedure")
    if id_mprocedure is None:
        await set_screen(message, PAU_CASE_NOT_FOUND, reply_markup=back_only())
        return

    cab["pau_case_number"] = case_number
    cab["pau_id_MProcedure"] = id_mprocedure
    await state.clear()
    # Показать сразу статус
    status_text = (
        "**Статус дела (ПАУ)**\n\n"
        f"Номер дела: {case_number}\n"
        f"ID процедуры: {id_mprocedure}\n\n"
        "_Данные получены из ПАУ._"
    )
    await set_screen(message, status_text, reply_markup=client_submenu(), parse_mode="Markdown")


@router.message(F.text == Buttons.PAYMENTS)
async def show_payments(message):
    if message.chat.id not in _cabinet_users:
        await set_screen(message, CABINET_REQUIRED, reply_markup=main_menu())
        return
    await set_screen(
        message,
        PAYMENTS_SCREEN,
        reply_markup=pay_inline(),
        parse_mode="Markdown",
        remove_prev=False,
    )


@router.message(F.text == Buttons.NEXT_STAGES)
async def next_stages(message):
    if message.chat.id in _cabinet_users:
        await set_screen(message, NEXT_STAGES_TEXT, reply_markup=client_submenu(), parse_mode="Markdown")
    else:
        await set_screen(message, NEXT_STAGES_TEXT, reply_markup=back_only(), parse_mode="Markdown")


@router.message(F.text == Buttons.UPLOAD_DOCS)
async def upload_docs(message):
    markup = client_submenu() if message.chat.id in _cabinet_users else back_only()
    await set_screen(message, UPLOAD_DOCS_PROMPT, reply_markup=markup)


# ——— ИИ ———
@router.message(F.text == Buttons.ASK_AI)
async def ask_ai_start(message, state: FSMContext):
    await state.set_state(AskAI.text)
    await set_screen(message, ASK_AI_PROMPT, reply_markup=back_only())


@router.message(StateFilter(AskAI.text), F.text == Buttons.BACK)
async def ask_ai_cancel(message, state: FSMContext):
    await state.clear()
    markup = client_submenu() if message.chat.id in _cabinet_users else main_menu()
    await set_screen(message, BACK_TO_MENU, reply_markup=markup)


@router.message(StateFilter(AskAI.text), F.text)
async def ask_ai_reply(message, state: FSMContext):
    await state.clear()
    reply = await ask_ai(message.text or "")
    markup = client_submenu() if message.chat.id in _cabinet_users else main_menu()
    if reply:
        try:
            await message.delete()
        except Exception:
            pass
        await set_screen(message, reply, reply_markup=markup, parse_mode="Markdown")
    else:
        await set_screen(message, ASK_AI_UNAVAILABLE, reply_markup=markup)


@router.message(F.document)
async def document_received(message):
    markup = client_submenu() if message.chat.id in _cabinet_users else main_menu()
    try:
        await message.delete()
    except Exception:
        pass
    await set_screen(message, UPLOAD_DOCS_RECEIVED, reply_markup=markup)
