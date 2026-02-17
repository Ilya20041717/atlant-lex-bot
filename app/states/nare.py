from aiogram.fsm.state import State, StatesGroup


class RequestLead(StatesGroup):
    name = State()
    phone = State()


class AskQuestion(StatesGroup):
    text = State()


class CabinetPhone(StatesGroup):
    phone = State()
    name = State()


class CabinetCase(StatesGroup):
    case_number = State()


class AskAI(StatesGroup):
    text = State()
