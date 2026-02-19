from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from app.constants import Buttons, FAQ_NARE


def start_menu() -> ReplyKeyboardMarkup:
    """Как в Nare: только кнопка «Начать»."""
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=Buttons.START)]],
        resize_keyboard=True,
    )


def main_menu() -> ReplyKeyboardMarkup:
    """Главное меню: Личный кабинет, Заявка, Вопрос, Менеджер, FAQ, ИИ, Назад."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=Buttons.CABINET),
                KeyboardButton(text=Buttons.REQUEST),
            ],
            [
                KeyboardButton(text=Buttons.QUESTION),
                KeyboardButton(text=Buttons.CONTACT_MANAGER),
            ],
            [KeyboardButton(text=Buttons.FAQ), KeyboardButton(text=Buttons.ASK_AI)],
            [KeyboardButton(text=Buttons.BACK)],
        ],
        resize_keyboard=True,
    )


def faq_menu() -> ReplyKeyboardMarkup:
    """Список вопросов FAQ как в Nare + Назад."""
    rows = []
    for question in FAQ_NARE:
        rows.append([KeyboardButton(text=question)])
    rows.append([KeyboardButton(text=Buttons.BACK)])
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)


def back_only() -> ReplyKeyboardMarkup:
    """Только «Назад»."""
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=Buttons.BACK)]],
        resize_keyboard=True,
    )


# ——— Опросник: быстрые ответы + можно ввести свой вариант ———

SURVEY_DEBT_BUTTONS = ["До 500 тыс. ₽", "500 тыс. - 1 млн ₽", "1 - 3 млн ₽", "Более 3 млн ₽"]
SURVEY_CREDITORS_BUTTONS = ["1-3", "4-10", "Более 10"]
SURVEY_OVERDUE_BUTTONS = ["До 3 мес.", "3-6 мес.", "6-12 мес.", "Более года"]
SURVEY_INCOME_BUTTONS = ["До 30 тыс. ₽", "30-50 тыс. ₽", "50-100 тыс. ₽", "Более 100 тыс. ₽"]
SURVEY_ASSETS_BUTTONS = ["Нет имущества", "Автомобиль", "Недвижимость", "Авто и недвижимость"]
SURVEY_REGION_BUTTONS = ["Москва", "МО", "Санкт-Петербург", "Другой регион"]

# Маппинг кнопок на числовые значения (для БД)
SURVEY_DEBT_VALUES = {"До 500 тыс. ₽": 250_000, "500 тыс. - 1 млн ₽": 750_000, "1 - 3 млн ₽": 2_000_000, "Более 3 млн ₽": 5_000_000}
SURVEY_CREDITORS_VALUES = {"1-3": 2, "4-10": 7, "Более 10": 15}
SURVEY_OVERDUE_VALUES = {"До 3 мес.": 2, "3-6 мес.": 5, "6-12 мес.": 9, "Более года": 18}
SURVEY_INCOME_VALUES = {"До 30 тыс. ₽": 20_000, "30-50 тыс. ₽": 40_000, "50-100 тыс. ₽": 75_000, "Более 100 тыс. ₽": 150_000}


def survey_debt_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=SURVEY_DEBT_BUTTONS[0]), KeyboardButton(text=SURVEY_DEBT_BUTTONS[1])],
            [KeyboardButton(text=SURVEY_DEBT_BUTTONS[2]), KeyboardButton(text=SURVEY_DEBT_BUTTONS[3])],
            [KeyboardButton(text=Buttons.BACK)],
        ],
        resize_keyboard=True,
    )


def survey_creditors_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=b) for b in SURVEY_CREDITORS_BUTTONS],
            [KeyboardButton(text=Buttons.BACK)],
        ],
        resize_keyboard=True,
    )


def survey_overdue_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=b) for b in SURVEY_OVERDUE_BUTTONS],
            [KeyboardButton(text=Buttons.BACK)],
        ],
        resize_keyboard=True,
    )


def survey_income_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=SURVEY_INCOME_BUTTONS[0]), KeyboardButton(text=SURVEY_INCOME_BUTTONS[1])],
            [KeyboardButton(text=SURVEY_INCOME_BUTTONS[2]), KeyboardButton(text=SURVEY_INCOME_BUTTONS[3])],
            [KeyboardButton(text=Buttons.BACK)],
        ],
        resize_keyboard=True,
    )


def survey_assets_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=SURVEY_ASSETS_BUTTONS[0]), KeyboardButton(text=SURVEY_ASSETS_BUTTONS[1])],
            [KeyboardButton(text=SURVEY_ASSETS_BUTTONS[2]), KeyboardButton(text=SURVEY_ASSETS_BUTTONS[3])],
            [KeyboardButton(text=Buttons.BACK)],
        ],
        resize_keyboard=True,
    )


def survey_region_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=SURVEY_REGION_BUTTONS[0]), KeyboardButton(text=SURVEY_REGION_BUTTONS[1])],
            [KeyboardButton(text=SURVEY_REGION_BUTTONS[2]), KeyboardButton(text=SURVEY_REGION_BUTTONS[3])],
            [KeyboardButton(text=Buttons.BACK)],
        ],
        resize_keyboard=True,
    )


def phone_request_keyboard() -> ReplyKeyboardMarkup:
    """«Отправить номер» (из профиля Telegram) + «Назад»."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=Buttons.SEND_PHONE, request_contact=True)],
            [KeyboardButton(text=Buttons.BACK)],
        ],
        resize_keyboard=True,
    )


def client_submenu() -> ReplyKeyboardMarkup:
    """Меню личного кабинета: статус, этапы, платежи, вопрос, документы, ИИ, Назад."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=Buttons.VIEW_STATUS), KeyboardButton(text=Buttons.NEXT_STAGES)],
            [KeyboardButton(text=Buttons.PAYMENTS)],
            [KeyboardButton(text=Buttons.QUESTION), KeyboardButton(text=Buttons.UPLOAD_DOCS)],
            [KeyboardButton(text=Buttons.ASK_AI)],
            [KeyboardButton(text=Buttons.BACK)],
        ],
        resize_keyboard=True,
    )


def request_only() -> ReplyKeyboardMarkup:
    """Одна кнопка «Оставить заявку» (после «мы не работаем с вами»)."""
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=Buttons.REQUEST)]],
        resize_keyboard=True,
    )
