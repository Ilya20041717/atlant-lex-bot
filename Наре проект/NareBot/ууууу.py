import telebot
import requests
import re
import json
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

user_sessions = {}
TOKEN = "7764900344:AAGAbqD9tuvrds2L5i7R4g97o500hvxPSJw"
BITRIX_WEBHOOK = "https://zeus.bitrix24.ru/rest/4582/tyvzmjhy80foyqjm/"
bot = telebot.TeleBot(TOKEN)

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
    bot.send_message(message.chat.id, "Выберите действие:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "📞 Связаться с менеджером")
def contact_manager(message):
    bot.send_message(message.chat.id, "📞 Вы можете позвонить менеджеру по номеру: +79697776110")

# Раздел FAQ
@bot.message_handler(func=lambda message: message.text == "❓ Часто задаваемые вопросы")
def show_faq(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for question in FAQ.keys():
        markup.add(KeyboardButton(question))
    markup.add(KeyboardButton("⬅️ Назад"))
    bot.send_message(message.chat.id, "Выберите вопрос:", reply_markup=markup)

# Ответы на FAQ
@bot.message_handler(func=lambda message: message.text in FAQ)
def faq_answer(message):
    bot.send_message(message.chat.id, FAQ[message.text])

# Обратно в главное меню
@bot.message_handler(func=lambda message: message.text == "⬅️ Назад")
def back_to_main(message):
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

                response_message = (
                    f"👤 **Имя:** {name}\n"
                    f"📌 **Статус сделки:** {deal_stage}\n"
                    f"💵 **Сумма сделки:** {deal_amount} ₽\n\n"
                    f"📜 **График платежей:**\n{payments_info or 'Нет информации о платежах.'}"
                )

                clients[message.chat.id] = phone_number  # Исправлено
                user_sessions[message.chat.id] = True

                markup = ReplyKeyboardMarkup(resize_keyboard=True)
                markup.add(KeyboardButton("📌 Посмотреть статус дела"))
                markup.add(KeyboardButton("📅 Последующие этапы"))
                markup.add(KeyboardButton("❓ Задать вопрос"))
                markup.add(KeyboardButton("📄 Загрузить документы"))
                bot.send_message(message.chat.id, response_message, reply_markup=markup, parse_mode="Markdown")
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
    # Проверяем, отправил ли пользователь контакт через кнопку
    if message.contact:
        phone = message.contact.phone_number  # Получаем номер из контакта
    elif message.text:
        phone = re.sub(r'\D', '', message.text)  # Очищаем текст от всего, кроме цифр
    else:
        bot.send_message(message.chat.id, "❌ Ошибка: Введите корректный номер телефона.")
        return

    # Создание заявки в Bitrix24
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
    bot.send_message(message.chat.id, "📎 Пришлите документ, и мы передадим его юристам.")
    bot.register_next_step_handler(message, save_document)

def save_document(message):
    if message.document:
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        file_name = message.document.file_name

        deal_id = clients.get(message.chat.id)
        if not deal_id:
            bot.send_message(message.chat.id, "❌ Ошибка: Не найдена активная сделка.")
            return

        upload_url = f"{BITRIX_WEBHOOK}crm.deal.update.json"
        payload = {
            "id": deal_id,
            "fields": {
                "UF_CRM_XX_DOCUMENTS": [{"fileData": [file_name, downloaded_file]}]
            }
        }

        response = requests.post(upload_url, json=payload)
        data = response.json()

        if "result" in data:
            bot.send_message(message.chat.id, "✅ Документ успешно прикреплен к заявке в CRM.")
        else:
            bot.send_message(message.chat.id, "❌ Ошибка при загрузке документа в CRM.")
    else:
        bot.send_message(message.chat.id, "❌ Ошибка. Пришлите файл в формате документа.")

@bot.message_handler(func=lambda message: message.text == "❓ Задать вопрос")
def ask_question(message):
    bot.send_message(message.chat.id, "📝 Напишите ваш вопрос, и мы передадим его юристам.")
    bot.register_next_step_handler(message, send_question_to_crm)

def send_question_to_crm(message):
    question = message.text
    phone_number = clients.get(message.chat.id, "Неизвестно")  # Исправлено
    payload = {
        "fields": {
            "TITLE": "Вопрос от клиента",
            "COMMENTS": f"Вопрос: {question}\nОтправитель: {phone_number}",
            "SOURCE_ID": "TELEGRAM_BOT"
        }
    }
    response = requests.post(f"{BITRIX_WEBHOOK}crm.lead.add.json", json=payload)
    bot.send_message(message.chat.id, "✅ Вопрос отправлен! Мы свяжемся с вами в ближайшее время.")

@bot.message_handler(func=lambda message: message.text == "📌 Посмотреть статус дела")
def view_case_status(message):
    phone_number = clients.get(message.chat.id)
    if not phone_number:
        bot.send_message(message.chat.id, "❌ Ошибка: Сначала авторизуйтесь через Личный кабинет.")
        return

    crm_url = f"{BITRIX_WEBHOOK}crm.contact.list.json"
    params = {"filter[PHONE]": phone_number}
    crm_response = requests.get(crm_url, params=params)
    data = crm_response.json()

    if "result" in data and data["result"]:
        contact = data["result"][0]
        contact_id = contact["ID"]
        name = contact.get("NAME", "Неизвестно")

        deal_url = f"{BITRIX_WEBHOOK}crm.deal.list.json"
        deal_params = {
            "filter[CONTACT_ID]": contact_id,
            "select[]": ["ID", "TITLE", "STAGE_ID", "OPPORTUNITY", "UF_CRM_XX_PAYMENTS"]
        }
        deal_response = requests.get(deal_url, params=deal_params)
        deal_data = deal_response.json()

        if "result" in deal_data and deal_data["result"]:
            deal = deal_data["result"][0]
            stage = deal.get("STAGE_ID", "Неизвестно")
            amount = deal.get("OPPORTUNITY", "Не указано")
            payments_raw = deal.get("UF_CRM_XX_PAYMENTS", "{}")

            try:
                payments = json.loads(payments_raw)
                schedule = ""
                for p in payments.get("installment_plan", []):
                    schedule += f"📅 {p['date']} — {p['amount']} ₽ ({p['status']})\n"
            except:
                schedule = "Нет информации о платежах."

            response = (
                f"👤 **Имя:** {name}\n"
                f"📌 **Статус сделки:** {stage}\n"
                f"💵 **Сумма сделки:** {amount} ₽\n\n"
                f"📜 **График платежей:**\n{schedule}"
            )
            bot.send_message(message.chat.id, response, parse_mode="Markdown")
        else:
            bot.send_message(message.chat.id, "⚠️ Сделка не найдена.")
    else:
        bot.send_message(message.chat.id, "⚠️ Контакт не найден.")

@bot.message_handler(func=lambda message: message.text == "📅 Последующие этапы")
def next_steps(message):
    bot.send_message(message.chat.id, "📋 **Последующие этапы:**\n1️⃣ Судебное заседание\n2️⃣ Принятие решения\n3️⃣ Закрытие дела\n\n🔔 Мы уведомим вас о каждом этапе.")

bot.polling()