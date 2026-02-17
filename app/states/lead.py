from aiogram.fsm.state import State, StatesGroup


class LeadSurvey(StatesGroup):
    debt_amount = State()
    creditors_count = State()
    overdue_months = State()
    income = State()
    assets = State()
    region = State()
