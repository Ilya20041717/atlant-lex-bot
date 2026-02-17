from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext

from app.constants import Buttons, Roles
from app.content.faq import FAQ_TEXTS
from app.content.info import INFO_TEXTS
from app.keyboards.menus import back_menu, faq_menu, info_menu, lead_menu
from app.services.lead_service import save_lead_survey
from app.states.lead import LeadSurvey
from app.utils.auto_delete import reply_ephemeral
from app.utils.formatters import with_disclaimer
from app.utils.parsing import parse_int
from app.utils.permissions import RoleFilter


router = Router()


@router.message(RoleFilter(Roles.LEAD), F.text == Buttons.LEAD_INFO)
async def show_info_menu(message):
    await reply_ephemeral(message, "Выберите тему:", reply_markup=info_menu())


@router.message(RoleFilter(Roles.LEAD), F.text.in_(list(INFO_TEXTS.keys())))
async def show_info_text(message):
    text = INFO_TEXTS.get(message.text, "")
    await reply_ephemeral(
        message,
        with_disclaimer(text),
        reply_markup=info_menu(),
    )


@router.message(RoleFilter(Roles.LEAD), F.text == Buttons.LEAD_FAQ)
async def show_faq_menu(message):
    await reply_ephemeral(message, "Выберите вопрос:", reply_markup=faq_menu())


@router.message(RoleFilter(Roles.LEAD), F.text.in_(list(FAQ_TEXTS.keys())))
async def show_faq_text(message):
    text = FAQ_TEXTS.get(message.text, "")
    await reply_ephemeral(
        message,
        with_disclaimer(text),
        reply_markup=faq_menu(),
    )


@router.message(RoleFilter(Roles.LEAD), F.text == Buttons.LEAD_SURVEY)
async def start_survey(message, state: FSMContext):
    await state.set_state(LeadSurvey.debt_amount)
    await reply_ephemeral(
        message,
        "Укажите сумму долга (числом):",
        reply_markup=back_menu(),
    )


@router.message(RoleFilter(Roles.LEAD), StateFilter(LeadSurvey.debt_amount))
async def survey_debt_amount(message, state: FSMContext):
    value = parse_int(message.text)
    if value is None:
        await reply_ephemeral(message, "Введите сумму долга числом.", reply_markup=back_menu())
        return
    await state.update_data(debt_amount=value)
    await state.set_state(LeadSurvey.creditors_count)
    await reply_ephemeral(message, "Укажите количество кредиторов (числом):", reply_markup=back_menu())


@router.message(RoleFilter(Roles.LEAD), StateFilter(LeadSurvey.creditors_count))
async def survey_creditors_count(message, state: FSMContext):
    value = parse_int(message.text)
    if value is None:
        await reply_ephemeral(message, "Введите количество кредиторов числом.", reply_markup=back_menu())
        return
    await state.update_data(creditors_count=value)
    await state.set_state(LeadSurvey.overdue_months)
    await reply_ephemeral(message, "Укажите количество месяцев просрочки (числом):", reply_markup=back_menu())


@router.message(RoleFilter(Roles.LEAD), StateFilter(LeadSurvey.overdue_months))
async def survey_overdue_months(message, state: FSMContext):
    value = parse_int(message.text)
    if value is None:
        await reply_ephemeral(message, "Введите количество месяцев числом.", reply_markup=back_menu())
        return
    await state.update_data(overdue_months=value)
    await state.set_state(LeadSurvey.income)
    await reply_ephemeral(message, "Укажите доход в месяц (числом):", reply_markup=back_menu())


@router.message(RoleFilter(Roles.LEAD), StateFilter(LeadSurvey.income))
async def survey_income(message, state: FSMContext):
    value = parse_int(message.text)
    if value is None:
        await reply_ephemeral(message, "Введите доход числом.", reply_markup=back_menu())
        return
    await state.update_data(income=value)
    await state.set_state(LeadSurvey.assets)
    await reply_ephemeral(message, "Перечислите имущество (кратко текстом):", reply_markup=back_menu())


@router.message(RoleFilter(Roles.LEAD), StateFilter(LeadSurvey.assets))
async def survey_assets(message, state: FSMContext):
    await state.update_data(assets=message.text.strip())
    await state.set_state(LeadSurvey.region)
    await reply_ephemeral(message, "Укажите ваш регион (текстом):", reply_markup=back_menu())


@router.message(RoleFilter(Roles.LEAD), StateFilter(LeadSurvey.region))
async def survey_region(message, state: FSMContext, session, db_user):
    data = await state.get_data()
    region = message.text.strip()
    await save_lead_survey(
        session=session,
        user_id=db_user.id,
        debt_amount=data.get("debt_amount"),
        creditors_count=data.get("creditors_count"),
        overdue_months=data.get("overdue_months"),
        income=data.get("income"),
        assets=data.get("assets", ""),
        region=region,
    )
    await state.clear()
    await reply_ephemeral(
        message,
        "Спасибо. Данные анкеты сохранены. Менеджер свяжется с вами.",
        reply_markup=lead_menu(),
    )


@router.message(RoleFilter(Roles.LEAD), F.text == Buttons.LEAD_CONSULT)
async def consult_stub(message):
    await reply_ephemeral(
        message,
        "Функция онлайн-записи будет доступна позже. Менеджер свяжется с вами.",
        reply_markup=lead_menu(),
    )
