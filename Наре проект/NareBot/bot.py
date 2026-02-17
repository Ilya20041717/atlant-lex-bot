import os
import re
import json
import requests
from dotenv import load_dotenv
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
BITRIX_WEBHOOK = (os.getenv("BITRIX_WEBHOOK") or "").rstrip("/")
if BITRIX_WEBHOOK and not BITRIX_WEBHOOK.endswith("/"):
    BITRIX_WEBHOOK += "/"

if not TOKEN:
    raise RuntimeError("Задайте BOT_TOKEN в .env (скопируйте .env.example в .env и укажите токен от @BotFather)")

bot = telebot.TeleBot(TOKEN)
user_sessions = {}

clients = {}  # Словарь для хранения авторизованных пользователей

# Словарь часто задаваемых вопросов
FAQ = {
    "📌 Когда будет заседание?": "Судебное заседание назначают через месяц-полтора после подачи документов в суд.",
    "💰 Когда оплатить депозит?": "Депозит необходимо оплатить за две недели до даты заседания. Иногда суд запрашивает депозит при присвоении номера дела. Об этом мы сообщим Вам.",
    "📅 Когда завершение?": "В среднем процедура длится 9 месяцев. После первого заседания наступает второй этап (от 2 до 6 месяцев), после этого списываются долги и процедура считается завершенной.",
    "📌 Узнать статус моего дела?": "Статус можно уточнить в личном кабинете. Мы также можем предоставить информацию из Bitrix24.",
    "💰 Сколько осталось платить по договору?": "Точную информацию по оплатам можно уточнить у нашего специалиста.",
    "📅 Как прошло заседание?": "Решение формируется в течение 10 рабочих дней со дня заседания. Мы проверим информацию и напишем Вам.",
    "📄 Когда будет информация по делу?": "Отчеты мы отправляем раз в месяц, в нем будет содержаться вся проделанная работа и текущий этап.",
    "📅 Когда будут поданы документы в суд?": "Документы подаем в суд через месяц-полтора после заключения договора, исключением являются случаи, когда есть имущество.",
    "💰 Куда оплатить депозит?": "По готовности напишите нам, направим реквизиты суда."
}

# Главное меню
@bot.message_handler(commands=["start"])
def send_welcome(message):
    user_sessions.pop(message.chat.id, None)  # Обнуляем сессию пользователя
    clients.pop(message.chat.id, None)  # Удаляем данные клиента
    
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    btn_start = KeyboardButton("🚀 Начать")
    markup.add(btn_start)
    
    bot.send_message(
        message.chat.id,
        "💼 **Добро пожаловать в бота юридической компании ATLANT LEX!**\n"
        "Мы поможем вам контролировать ход вашего дела, загрузить документы, "
        "задать вопросы и получить юридическую поддержку.\n\n"
        "🔹 Используйте меню ниже, чтобы начать работу.",
        reply_markup=markup,
        parse_mode="Markdown"
    )

# Меню после нажатия "Начать"
@bot.message_handler(func=lambda message: message.text == "🚀 Начать")
def show_main_menu(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    btn_status = KeyboardButton("👤 Личный кабинет")
    btn_request = KeyboardButton("📝 Оставить заявку")
    btn_question = KeyboardButton("❓ Задать вопрос")
    btn_contact_manager = KeyboardButton("📞 Связаться с менеджером")
    markup.add(btn_status, btn_request)
    markup.add(btn_question, btn_contact_manager)
    btn_faq = KeyboardButton("📚 Часто задаваемые вопросы")
    markup.add(btn_faq)
    markup.add(KeyboardButton("⬅️ Назад"))
    bot.send_message(message.chat.id, "Выберите действие:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "📞 Связаться с менеджером")
def contact_manager(message):
    bot.send_message(message.chat.id, "📞 Вы можете позвонить менеджеру по номеру: +79697776110")

# Раздел FAQ
@bot.message_handler(func=lambda message: message.text == "📚 Часто задаваемые вопросы")
def show_faq(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for question in FAQ.keys():
        markup.add(KeyboardButton(question))
    markup.add(KeyboardButton("⬅️ Назад"))
    bot.send_message(message.chat.id, "Выберите вопрос:", reply_markup=markup)


# Ответы на FAQ
@bot.message_handler(func=lambda message: message.text in FAQ)
def faq_answer(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("⬅️ Назад"))
    bot.send_message(message.chat.id, FAQ[message.text], reply_markup=markup)

# Обратно в главное меню
@bot.message_handler(func=lambda message: message.text == "⬅️ Назад")
def back_to_main(message):
    if message.chat.id in clients:
        view_case_status(message)
    else:
        show_main_menu(message)

# Запрос номера телефона для проверки статуса
@bot.message_handler(func=lambda message: message.text == "👤 Личный кабинет")
def request_phone(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    btn_phone = KeyboardButton("📞 Отправить номер", request_contact=True)
    markup.add(btn_phone)
    bot.send_message(message.chat.id, "Введите ваш номер телефона в формате +7XXXXXXXXXX или нажмите кнопку ниже:", reply_markup=markup)
    bot.register_next_step_handler(message, process_phone)

# Обработка номера телефона (если введён вручную)
def process_phone(message):
    if message.contact:
        phone_number = message.contact.phone_number  # Если номер отправлен через кнопку
    elif message.text:
        phone_number = re.sub(r'\D', '', message.text)  # Если номер введён вручную
    else:
        bot.send_message(message.chat.id, "❌ Ошибка: Введите корректный номер телефона.")
        return

    if len(phone_number) < 10 or len(phone_number) > 11:
        bot.send_message(message.chat.id, "❌ Ошибка: Введите корректный номер телефона.")
        return

    check_status_in_crm(message, phone_number)

# Обработка контакта (если отправлен через кнопку)
@bot.message_handler(content_types=["contact"])
def process_contact(message):
    phone_number = message.contact.phone_number
    check_status_in_crm(message, phone_number)

# Проверка номера в CRM
def check_status_in_crm(message, phone_number):
    if not BITRIX_WEBHOOK:
        bot.send_message(
            message.chat.id,
            "⚠️ Интеграция с CRM временно недоступна. Оставьте заявку — мы свяжемся с вами.",
            reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton("📝 Оставить заявку")),
        )
        return
    print(f"✅ Проверяем номер в CRM: {phone_number}")
    crm_url = f"{BITRIX_WEBHOOK}crm.contact.list.json"
    
    possible_numbers = [
        phone_number,
        "+7" + phone_number[1:] if phone_number.startswith("7") else phone_number,
        "8" + phone_number[1:] if phone_number.startswith("7") else phone_number
    ]

    for num in possible_numbers:
        params = {"filter[PHONE]": num}
        print(f"📡 Пробуем запрос в CRM: {crm_url}, параметры: {params}")
        crm_response = requests.get(crm_url, params=params)
        data = crm_response.json()

        print(f"📡 Ответ от CRM: {data}")

        if data.get("result"):
            contact = data["result"][0]
            name = contact.get("NAME", "Неизвестно")

            deal_url = f"{BITRIX_WEBHOOK}crm.deal.list.json"
            deal_params = {
                "filter[CONTACT_ID]": contact["ID"],
                "select[]": ["ID", "TITLE", "STAGE_ID", "OPPORTUNITY", "UF_CRM_XX_PAYMENTS"]
            }
            deal_response = requests.get(deal_url, params=deal_params)
            deal_data = deal_response.json()

            print(f"📡 Данные сделки: {deal_data}")

            if "result" in deal_data and deal_data["result"]:
                deal = deal_data["result"][0]
                deal_id = deal["ID"]
                deal_stage = deal.get("STAGE_ID", "Неизвестно")
                deal_amount = deal.get("OPPORTUNITY", "Не указано")
                payments_json = deal.get("UF_CRM_XX_PAYMENTS", "{}")
                payments_data = json.loads(payments_json) if payments_json else {}

                payments_info = ""
                for payment in payments_data.get("installment_plan", []):
                    payments_info += f"📅 {payment['date']} - {payment['amount']} ₽ ({payment['status']})\n"

                if not deal_stage or deal_stage.startswith("UC_"):
                    readable_stage = "Подготовка документов"
                else:
                    readable_stage = deal_stage

                response_message = (
                    f"👤 Имя: {name}\n"
                    f"📌 Статус сделки: {readable_stage}\n"
                    f"💵 Сумма сделки: {deal_amount} ₽\n"
                )

                clients[message.chat.id] = phone_number  # Исправлено
                user_sessions[message.chat.id] = True

                markup = ReplyKeyboardMarkup(resize_keyboard=True)
                markup.add(KeyboardButton("📌 Посмотреть статус дела"))
                markup.add(KeyboardButton("📅 Последующие этапы"))
                markup.add(KeyboardButton("❓ Задать вопрос"))
                markup.add(KeyboardButton("📄 Загрузить документы"))
                bot.send_message(message.chat.id, response_message, reply_markup=markup)
                return
            
            else:
                print("⚠️ Сделка не найдена для контакта.")
    
    # Если ничего не нашли
    bot.send_message(
        message.chat.id,
        "🚀 Мы ещё не работаем с вами! Оставьте заявку, и наши юристы свяжутся с вами.",
        reply_markup=ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(KeyboardButton("📝 Оставить заявку"))
    )

# Обработка заявки нового клиента
@bot.message_handler(func=lambda message: message.text == "📝 Оставить заявку")
def create_request(message):
    bot.send_message(message.chat.id, "Введите ваше имя:")
    bot.register_next_step_handler(message, request_phone_for_lead)

def request_phone_for_lead(message):
    name = message.text
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    btn_phone = KeyboardButton("📞 Отправить номер", request_contact=True)
    markup.add(btn_phone)
    bot.send_message(message.chat.id, "Введите ваш номер телефона в формате +7XXXXXXXXXX или нажмите кнопку ниже:", reply_markup=markup)
    bot.register_next_step_handler(message, lambda msg: get_phone(msg, name))

# Запрос имени
def get_name(message):
    name = message.text
    bot.send_message(message.chat.id, "Введите ваш номер телефона:")
    bot.register_next_step_handler(message, lambda msg: get_phone(msg, name))

# Запрос телефона
def get_phone(message, name):
    if message.contact:
        phone = message.contact.phone_number
    elif message.text:
        phone = re.sub(r'\D', '', message.text)
    else:
        bot.send_message(message.chat.id, "❌ Ошибка: Введите корректный номер телефона.")
        return

    if not BITRIX_WEBHOOK:
        bot.send_message(
            message.chat.id,
            "✅ Заявка принята (демо-режим). В продакшене заявка уйдёт в CRM.",
        )
        return

    payload = {
        "fields": {
            "NAME": name,
            "PHONE": [{"VALUE": phone, "VALUE_TYPE": "WORK"}],
            "COMMENTS": "Новая заявка из Telegram",
            "SOURCE_ID": "TELEGRAM_BOT"  # Добавляем источник
        }
    }
    response = requests.post(f"{BITRIX_WEBHOOK}crm.lead.add.json", json=payload)
    data = response.json()

    if "result" in data:
        bot.send_message(message.chat.id, "✅ Ваша заявка принята! Наши специалисты скоро свяжутся с вами.")
    else:
        bot.send_message(message.chat.id, "❌ Ошибка при создании заявки. Попробуйте позже.")

@bot.message_handler(func=lambda message: message.text == "📄 Загрузить документы")
def upload_document(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("⬅️ Назад"))
    bot.send_message(message.chat.id, "📎 Пришлите документ, и мы передадим его юристам.", reply_markup=markup)
    bot.register_next_step_handler(message, save_document)

def save_document(message):
    if message.document:
        if not BITRIX_WEBHOOK:
            bot.send_message(message.chat.id, "⚠️ Загрузка документов в CRM недоступна (не задан BITRIX_WEBHOOK).")
            return
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        file_name = message.document.file_name
        phone_number = clients.get(message.chat.id)

        if not phone_number:
            bot.send_message(message.chat.id, "❌ Ошибка: Сначала авторизуйтесь через Личный кабинет.")
            return

        # Найти контакт по номеру телефона
        crm_url = f"{BITRIX_WEBHOOK}crm.contact.list.json"
        params = {"filter[PHONE]": phone_number}
        crm_response = requests.get(crm_url, params=params).json()

        if not crm_response.get("result"):
            bot.send_message(message.chat.id, "❌ Ошибка: Контакт не найден в CRM.")
            return

        contact_id = crm_response["result"][0]["ID"]

        # Найти сделку по contact_id
        deal_url = f"{BITRIX_WEBHOOK}crm.deal.list.json"
        deal_params = {
            "filter[CONTACT_ID]": contact_id,
            "select[]": ["ID"]
        }
        deal_response = requests.get(deal_url, params=deal_params).json()

        if not deal_response.get("result"):
            bot.send_message(message.chat.id, "❌ Ошибка: Сделка не найдена.")
            return

        deal_id = deal_response["result"][0]["ID"]

        # Загрузка файла в CRM (на диск)
        upload_response = requests.post(
            f"{BITRIX_WEBHOOK}disk.folder.uploadfile.json",
            files={'file': (file_name, downloaded_file)},
            data={"id": 3}  # ID общей папки
        ).json()

        if "result" not in upload_response:
            bot.send_message(message.chat.id, "❌ Ошибка при загрузке файла на диск.")
            return

        file_id = upload_response["result"]["ID"]

        # Привязка файла к сделке
        attach_response = requests.post(
            f"{BITRIX_WEBHOOK}crm.deal.update.json",
            json={
                "id": deal_id,
                "fields": {
                    "UF_CRM_XX_DOCUMENTS": file_id
                }
            }
        ).json()

        if "result" in attach_response:
            bot.send_message(message.chat.id, "✅ Документ успешно прикреплен к заявке в CRM.")
        else:
            bot.send_message(message.chat.id, "❌ Ошибка при прикреплении файла к сделке.")
    else:
        if message.text == "⬅️ Назад":
            view_case_status(message)
        else:
            bot.send_message(message.chat.id, "❌ Ошибка. Пришлите файл в формате документа.")

@bot.message_handler(func=lambda message: message.text == "❓ Задать вопрос")
def ask_question(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("⬅️ В личный кабинет"))
    markup.add(KeyboardButton("⬅️ Назад"))
    bot.send_message(message.chat.id, "📝 Напишите ваш вопрос, и мы передадим его юристам.", reply_markup=markup)
    
    user_sessions[message.chat.id] = clients.get(message.chat.id)
    
    def handle_question_input(msg):
        if msg.text == "⬅️ Назад":
            show_main_menu(msg)
        elif msg.text == "⬅️ В личный кабинет":
            view_case_status(msg)
        elif msg.chat.id in clients:
            send_question_to_crm(msg)
        else:
            request_phone_for_question(msg, msg.text)
    
    bot.register_next_step_handler(message, handle_question_input)

def send_question_to_crm(message):
    question = message.text
    if not BITRIX_WEBHOOK:
        bot.send_message(message.chat.id, "✅ Вопрос записан (демо-режим). В продакшене он уйдёт в CRM.")
        return
    phone_number = user_sessions.get(message.chat.id, "Неизвестно")
    name = message.from_user.first_name or "Неизвестно"
    payload = {
        "fields": {
            "TITLE": "Вопрос от клиента",
            "COMMENTS": f"Вопрос: {question}\nИмя: {name}\nТелефон: {phone_number}",
            "SOURCE_ID": "TELEGRAM_BOT"
        }
    }
    response = requests.post(f"{BITRIX_WEBHOOK}crm.lead.add.json", json=payload)
    bot.send_message(message.chat.id, "✅ Вопрос отправлен! Мы свяжемся с вами в ближайшее время.")

def request_phone_for_question(message, question):
    name = message.from_user.first_name or "Неизвестно"
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    btn_phone = KeyboardButton("📞 Отправить номер", request_contact=True)
    markup.add(btn_phone)
    bot.send_message(
        message.chat.id,
        "Введите ваш номер телефона в формате +7XXXXXXXXXX или нажмите кнопку ниже:",
        reply_markup=markup
    )
    bot.register_next_step_handler(message, lambda msg: send_question_with_phone(msg, question, name))

def send_question_with_phone(message, question, name):
    if message.contact:
        phone = message.contact.phone_number
    elif message.text:
        phone = re.sub(r'\D', '', message.text)
    else:
        bot.send_message(message.chat.id, "❌ Ошибка: Введите корректный номер телефона.")
        return

    if BITRIX_WEBHOOK:
        payload = {
            "fields": {
                "TITLE": "Вопрос от клиента",
                "COMMENTS": f"Вопрос: {question}\nИмя: {name}\nТелефон: {phone}",
                "SOURCE_ID": "TELEGRAM_BOT"
            }
        }
        requests.post(f"{BITRIX_WEBHOOK}crm.lead.add.json", json=payload)
    bot.send_message(message.chat.id, "✅ Вопрос отправлен! Мы свяжемся с вами в ближайшее время.")
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("⬅️ Назад"))
    bot.send_message(message.chat.id, "Выберите действие:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "📌 Посмотреть статус дела")
def view_case_status(message):
    phone_number = clients.get(message.chat.id)
    if not phone_number:
        bot.send_message(message.chat.id, "❌ Ошибка: Сначала авторизуйтесь через Личный кабинет.")
        return

    check_status_in_crm(message, phone_number)

@bot.message_handler(func=lambda message: message.text == "📅 Последующие этапы")
def next_steps(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("⬅️ Назад"))
    bot.send_message(message.chat.id, "📋 **Последующие этапы:**\n1️⃣ Судебное заседание\n2️⃣ Принятие решения\n3️⃣ Закрытие дела\n\n🔔 Мы уведомим вас о каждом этапе.", reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(func=lambda message: message.text in FAQ)
def answer_faq(message):
    answer = FAQ.get(message.text)
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("⬅️ Назад"))
    bot.send_message(message.chat.id, answer, reply_markup=markup)

bot.polling()