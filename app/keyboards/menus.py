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
