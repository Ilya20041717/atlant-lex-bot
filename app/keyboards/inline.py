from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.constants import FAQ_NARE


class Cb:
    MAIN = "nav:main"
    CABINET = "nav:cabinet"
    REQUEST = "nav:request"
    QUESTION = "nav:question"
    MANAGER = "nav:manager"
    FAQ = "nav:faq"
    ASK_AI = "nav:ai"

    CAB_STATUS = "cab:status"
    CAB_STAGES = "cab:stages"
    CAB_UPLOAD = "cab:upload"
    CAB_BACK = "cab:back"
    PAY_DEMO = "pay:demo"

    FAQ_BACK = "faq:back"


def pay_inline() -> InlineKeyboardMarkup:
    """Кнопка «Оплатить» под экраном платежей (демо)."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Оплатить", callback_data=Cb.PAY_DEMO)],
        ]
    )


def start_inline() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Начать", callback_data=Cb.MAIN)],
        ]
    )


def main_inline() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Личный кабинет", callback_data=Cb.CABINET),
                InlineKeyboardButton(text="Оставить заявку", callback_data=Cb.REQUEST),
            ],
            [
                InlineKeyboardButton(text="Задать вопрос", callback_data=Cb.QUESTION),
                InlineKeyboardButton(text="Связаться с менеджером", callback_data=Cb.MANAGER),
            ],
            [
                InlineKeyboardButton(text="FAQ", callback_data=Cb.FAQ),
                InlineKeyboardButton(text="Спросить ИИ", callback_data=Cb.ASK_AI),
            ],
        ]
    )


def cabinet_inline() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Посмотреть статус дела", callback_data=Cb.CAB_STATUS),
                InlineKeyboardButton(text="Последующие этапы", callback_data=Cb.CAB_STAGES),
            ],
            [
                InlineKeyboardButton(text="Задать вопрос", callback_data=Cb.QUESTION),
                InlineKeyboardButton(text="Загрузить документы", callback_data=Cb.CAB_UPLOAD),
            ],
            [InlineKeyboardButton(text="Спросить ИИ", callback_data=Cb.ASK_AI)],
            [InlineKeyboardButton(text="В меню", callback_data=Cb.MAIN)],
        ]
    )


def back_to_main_inline() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="В меню", callback_data=Cb.MAIN)]]
    )


def faq_inline() -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    questions = list(FAQ_NARE.keys())
    for i, q in enumerate(questions):
        rows.append([InlineKeyboardButton(text=q, callback_data=f"faq:q:{i}")])
    rows.append([InlineKeyboardButton(text="В меню", callback_data=Cb.MAIN)])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def faq_answer_inline() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Назад к FAQ", callback_data=Cb.FAQ)],
            [InlineKeyboardButton(text="В меню", callback_data=Cb.MAIN)],
        ]
    )

