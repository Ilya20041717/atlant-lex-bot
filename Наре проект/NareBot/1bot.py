import telebot
import requests
import re
import json
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

user_sessions = {}
TOKEN = "7356173561:AAGybmMiKd07bQ-51luiGVerhjIWAU7oTdA"
BITRIX_WEBHOOK = "https://zeus.bitrix24.ru/rest/4582/tyvzmjhy80foyqjm/"
bot = telebot.TeleBot(TOKEN)

clients = {}  # Словарь для хранения авторизованных пользователей

# Словарь часто задаваемых вопросов
FAQ = {
    "📌 Когда будет заседание?": "Судебное заседание назначают через месяц-полтора после подачи документов в суд.",
    "💰 Когда оплатить депозит?": "Депозит необходимо оплатить за две недели до даты заседания. Иногда суд запрашивает депозит при присвоении номера дела. Об этом мы сообщим Вам.",
    "📅 Когда завершение?": "В среднем процедура длится 9 месяцев. После первого заседания наступает второй этап (от 2 до 6 месяцев), после этого списываются долги и процедура считается завершенной.",
    "📌 Узнать статус моего дела?": "Вы можете войти в личный кабинет и узнать статус вашего дела.",
    "💰 Сколько осталось платить по договору?": "Точную информацию по оплатам можно уточнить у нашего специалиста.",
    "📅 Как прошло заседание?": "Решение формируется в течение 10 рабочих дней со дня заседания. Мы проверим информацию и напишем Вам.",
    "📄 Когда будет информация по делу?": "Отчеты мы отправляем раз в месяц, в нем будет содержаться вся проделанная работа и текущий этап.",
    "📅 Когда будут поданы документы в суд?": "Документы подаем в суд через месяц-полтора после заключения договора, исключением являются случаи, когда есть имущество.",
    "💰 Куда оплатить депозит?": "По готовности напишите нам, направим реквизиты суда.",
    "💰 В каком размере денежные средства полагаются после первого заседания? Что не переходит в конкурсную массу?":
        "В конкурсной массе не учитываются:\n\n"
        "1. Средства в размере прожиточного минимума, необходимые для обеспечения жизнедеятельности должника и лиц, находящихся на его иждивении.\n"
        "2. Автотранспортное средство, если его использование необходимо должнику в связи с имеющейся инвалидностью.\n"
        "3. Денежные средства, предназначенные для оплаты аренды жилья (если нету собственного жилья).\n"
        "4. Финансы, выделенные на приобретение медикаментов, при условии предоставления подтверждающих документов (справок, чеков).\n"
        "5. Часть средств, предназначенных для оплаты жилищно-коммунальных услуг (как правило, исключается не всегда, но подобная практика существует).\n\n"
        "В ходе процедуры сохраняются выплаты алиментов на детей, социальные выплаты и пособия.",
    "📋 Какие этапы я прохожу при процедуре банкротства?":
        "1️⃣ Сбор документов и анализ дела\n"
        "2️⃣ Сохранность имущества (при необходимости)\n"
        "3️⃣ Составление заявления о признании гражданина банкротом в Арбитражный суд\n"
        "4️⃣ Уведомления кредиторов о банкротстве\n"
        "5️⃣ Подача заявления в Арбитражный суд\n"
        "6️⃣ Оплата судебных издержек (депозит-оплата финансовому управляющему)\n"
        "7️⃣ Первое судебное заседание\n"
        "8️⃣ Вынесение решения о признании гражданина банкротом\n"
        "9️⃣ Период реализации/реструктуризации\n"
        "🔟 Второе судебное заседание\n"
        "1️⃣1️⃣ Оплата судебных издержек финансовому управляющему\n"
        "1️⃣2️⃣ Завершение процедуры",
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
    btn_contact_manager = KeyboardButton("📩 Связаться с менеджером")
    markup.add(btn_status, btn_request)
    markup.add(btn_question, btn_contact_manager)
    btn_faq = KeyboardButton("📚 Часто задаваемые вопросы")
    markup.add(btn_faq)
    bot.send_message(message.chat.id, "Выберите действие:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "📩 Связаться с менеджером")
def contact_manager(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("⬅️ Назад"))
    bot.send_message(message.chat.id, "✉️ Вы можете написать вопрос, менеджер с Вами свяжется в ближайшее время.", reply_markup=markup)

    user_sessions[message.chat.id] = clients.get(message.chat.id)

    def handle_manager_question(msg):
        if msg.text == "⬅️ Назад":
            view_case_status(msg)
            return
        elif msg.chat.id in clients:
            send_question_to_crm(msg)
        else:
            request_phone_for_question(msg, msg.text)

    bot.register_next_step_handler(message, handle_manager_question)

# Раздел FAQ
@bot.message_handler(func=lambda message: message.text == "❓ Часто задаваемые вопросы")
def show_faq(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for question in FAQ.keys():
        markup.add(KeyboardButton(question))
    markup.add(KeyboardButton("⬅️ Назад"))
    bot.send_message(message.chat.id, "Выберите вопрос:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "📚 Часто задаваемые вопросы")
def show_faq_button(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for question in FAQ.keys():
        markup.add(KeyboardButton(question))
    markup.add(KeyboardButton("⬅️ Назад"))
    bot.send_message(message.chat.id, "Выберите вопрос:", reply_markup=markup)


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
 
                # Переводим код этапа в читаемое название
                stage_map = {
                    "NEW": "Новая заявка",
                    "PREPARATION": "Подготовка документов",
                    "UC_STAGE_1": "Сбор документов",
                    "UC_STAGE_2": "Сохранность имущества",
                    "UC_STAGE_3": "Составление заявления в суд",
                    "UC_STAGE_4": "Уведомления кредиторов",
                    "UC_STAGE_5": "Подача в суд",
                    "UC_STAGE_6": "Оплата судебных издержек",
                    "UC_STAGE_7": "Первое судебное заседание",
                    "UC_STAGE_8": "Вынесение решения",
                    "UC_STAGE_9": "Период реализации/реструктуризации",
                    "UC_STAGE_10": "Второе судебное заседание",
                    "UC_STAGE_11": "Завершение процедуры",
                    "UC_5AZE14": "Согласование документов",
                    "UC_0F2JYD": "Подписание договора",
                    "UC_F726GN": "Подготовка документов",
                    "UC_R93K2N": "Подача в суд",
                    "UC_BTTXVP": "Судебное разбирательство",
                    "WON": "Завершено успешно",
                "LOSE": "Закрыто без успеха",
                    "C8:NEW": "Первичная регистрация заявки",
                    "C8:PREPARATION": "Подготовка документов",
                    "C8:EXECUTING": "Процедура в процессе исполнения",
                    "C8:FINAL": "Завершение сделки",
                    "C8:CONTROL": "Контроль исполнения",
                    "C8:PAYMENT": "Ожидание оплаты",
                    "C8:APPROVAL": "Ожидает утверждения",
                    "C8:AGREEMENT": "Заключение соглашения",
                    "C8:PROCESSING": "Обработка информации",
                    "C8:REVIEW": "На рассмотрении",
                    "C8:COMPLETED": "Завершено",
                    "C8:QUALITY_CHECK": "Проверка качества",
                    "C8:CONSULTING": "Консультирование",
                    "C8:APPEAL": "Апелляция",
                    "C8:LEGAL_REVIEW": "Юридическая проверка",
                    "UC_STAGE_DOCS": "Сбор пакета документов",
                    "UC_STAGE_PROPERTY": "Вывод имущества",
                    "UC_STAGE_FREEZE": "Заморозка",
                    "UC_STAGE_DELAY": "Отсрочка подготовки заявления",
                    "UC_STAGE_PREPARE_PETITION": "Подготовка заявления на банкротство",
                    "UC_STAGE_FILE_PETITION": "Подача/принятие заявления",
                    "UC_STAGE_HOLD": "Заявление оставлено без движения",
                    "UC_STAGE_PAYMENT": "Оплата депозита",
                    "UC_STAGE_COURT": "Судебное заседание",
                    "UC_STAGE_RESTRUCTURING": "Этап реструктуризации",
                    "UC_STAGE_REALIZATION": "Этап реализации",
                    "UC_STAGE_CANCEL": "Расторгли договор",
                    "UC_STAGE_FINISH": "Завершить сделку",
                    "UC_5AZE14": "Встреча назначена",
                    "UC_F726GN": "Недозвон / не подключился к встрече",
                    "UC_V9L4S4": "Догрев",
                    "NEW": "Преддоговор/Заключили договор",
                    "WON": "Полная/частичная оплата получена",
                    "LOSE": "Брак",
                    "2": "Брак подтвержден",
                    "C8:NEW": "Сбор пакета документов",
                    "C8:UC_Y0U229": "Вывод имущества",
                    "C8:UC_AMKUBZ": "Заморозка",
                    "C8:UC_XE9O72": "Отсрочка подготовки заявления",
                    "C8:UC_YY5WLS": "Подготовка заявления на банкротство",
                    "C8:UC_KAXKC9": "Подача/принятие заявления",
                    "C8:UC_CK32SJ": "Заявление оставлено без движения",
                    "C8:UC_G2686A": "Оплата депозита",
                    "C8:EXECUTING": "Судебное заседание",
                    "C8:UC_SKZ032": "Этап реализации",
                    "C8:WON": "Акты подписаны, работы завершены",
                }
                readable_stage = stage_map.get(deal_stage, f"Неизвестный этап: {deal_stage}")
 
                response_message = (
                    f"👤 Имя: {name}\n"
                    f"📌 Статус сделки: {readable_stage}\n"
                    f"💵 Сумма сделки: {deal_amount} ₽"
                )

                clients[message.chat.id] = phone_number  # Исправлено
                user_sessions[message.chat.id] = {"stage_id": deal_stage}

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

    payload = {
        "fields": {
            "TITLE": f"Новая заявка от {name}",
            "NAME": name,
            "PHONE": [{"VALUE": phone, "VALUE_TYPE": "WORK"}],
            "COMMENTS": "Новая заявка из Telegram",
            "SOURCE_ID": "TELEGRAM_BOT",
            "ASSIGNED_BY_ID": 2332
        }
    }
    response = requests.post(f"{BITRIX_WEBHOOK}crm.lead.add.json", json=payload)
    data = response.json()

    if "result" in data:
        lead_id = data["result"]

        # Отправка уведомления Анастасии
        notify_payload = {
            "to": 3660,
            "message": f"💬 Поступила новая заявка из Telegram от {name} (тел: {phone})\nПосмотреть: https://zeus.bitrix24.ru/crm/lead/details/{lead_id}/"
        }
        requests.post(f"{BITRIX_WEBHOOK}im.notify.json", json=notify_payload)

        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(KeyboardButton("⬅️ Назад"))
        bot.send_message(message.chat.id, "✅ Ваша заявка принята! Наши специалисты скоро свяжутся с вами.", reply_markup=markup)
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
    markup.add(KeyboardButton("⬅️ Назад"))
    bot.send_message(message.chat.id, "📝 Напишите ваш вопрос, и мы передадим его юристам.", reply_markup=markup)
    
    user_sessions[message.chat.id] = clients.get(message.chat.id)
    
    def handle_question_input(msg):
        if msg.text == "⬅️ Назад":
            view_case_status(msg)
            return
        elif msg.chat.id in clients:
            send_question_to_crm(msg)
        else:
            request_phone_for_question(msg, msg.text)
    
    bot.register_next_step_handler(message, handle_question_input)

def send_question_to_crm(message):
    question = message.text
    phone_number = user_sessions.get(message.chat.id, "Неизвестно")
    contact_name = ""

    # Попробуем получить имя клиента из CRM
    crm_url = f"{BITRIX_WEBHOOK}crm.contact.list.json"
    params = {"filter[PHONE]": phone_number}
    crm_response = requests.get(crm_url, params=params).json()
    if crm_response.get("result"):
        contact_name = crm_response["result"][0].get("NAME", "")

    payload = {
        "fields": {
            "TITLE": "Вопрос от клиента",
            "COMMENTS": f"Вопрос: {question}\nИмя: {contact_name}\nТелефон: {phone_number}",
            "SOURCE_ID": "TELEGRAM_BOT",
            "ASSIGNED_BY_ID": 2332,
            "RESPONSIBLE_ID": 2332
        }
    }
    response = requests.post(f"{BITRIX_WEBHOOK}crm.lead.add.json", json=payload)
    data = response.json()
    if "result" in data:
        lead_id = data["result"]
        notify_payloads = [
            {
                "to": 2332,
                "message": f"💬 Поступил новый вопрос от клиента: {question}\nПосмотреть: https://zeus.bitrix24.ru/crm/lead/details/{lead_id}/"
            },
            {
                "to": 3660,
                "message": f"💬 Поступил новый вопрос от клиента: {question}\nПосмотреть: https://zeus.bitrix24.ru/crm/lead/details/{lead_id}/"
            }
        ]
        for notify_payload in notify_payloads:
            requests.post(f"{BITRIX_WEBHOOK}im.notify.json", json=notify_payload)

    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("⬅️ Назад"))
    bot.send_message(message.chat.id, "✅ Вопрос отправлен! Мы свяжемся с вами в ближайшее время.", reply_markup=markup)

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

    payload = {
        "fields": {
            "TITLE": "Вопрос от клиента",
            "COMMENTS": f"Вопрос: {question}\nИмя: {name}\nТелефон: {phone}",
            "SOURCE_ID": "TELEGRAM_BOT",
            "ASSIGNED_BY_ID": 2332,
            "RESPONSIBLE_ID": 2332
        }
    }
    response = requests.post(f"{BITRIX_WEBHOOK}crm.lead.add.json", json=payload)
    data = response.json()
    if "result" in data:
        lead_id = data["result"]
        notify_payload = {
            "to": 3660,
            "message": f"💬 Поступил новый вопрос от клиента: {question}\nПосмотреть: https://zeus.bitrix24.ru/crm/lead/details/{lead_id}/"
        }
        requests.post(f"{BITRIX_WEBHOOK}im.notify.json", json=notify_payload)
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("⬅️ Назад"))
    bot.send_message(message.chat.id, "✅ Вопрос отправлен! Мы свяжемся с вами в ближайшее время.", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "📌 Посмотреть статус дела")
def view_case_status(message):
    phone_number = clients.get(message.chat.id)
    if not phone_number:
        bot.send_message(message.chat.id, "❌ Ошибка: Сначала авторизуйтесь через Личный кабинет.")
        return

    check_status_in_crm(message, phone_number)

@bot.message_handler(func=lambda message: message.text == "📅 Последующие этапы")
def next_steps(message):
    session = user_sessions.get(message.chat.id)
    if not session or not isinstance(session, dict) or "stage_id" not in session:
        bot.send_message(message.chat.id, "❌ Ошибка: Не удалось определить текущий этап. Попробуйте заново авторизоваться через личный кабинет.")
        return

    stage_id = session["stage_id"]

    all_stages = [
        ("C8:NEW", "Сбор пакета документов"),
        ("C8:UC_Y0U229", "Вывод имущества"),
        ("C8:UC_AMKUBZ", "Заморозка"),
        ("C8:UC_XE9O72", "Отсрочка подготовки заявления"),
        ("C8:UC_YY5WLS", "Подготовка заявления на банкротство"),
        ("C8:UC_KAXKC9", "Подача/принятие заявления"),
        ("C8:UC_CK32SJ", "Заявление оставлено без движения"),
        ("C8:UC_G2686A", "Оплата депозита"),
        ("C8:EXECUTING", "Судебное заседание"),
        ("C8:UC_SKZ032", "Этап реализации"),
        ("C8:WON", "Акты подписаны, работы завершены"),
    ]

    stage_keys = [s[0] for s in all_stages]
    if stage_id not in stage_keys:
        bot.send_message(message.chat.id, f"📋 Этап не определён или не входит в список этапов. (ID: {stage_id})")
        return

    current_index = stage_keys.index(stage_id)
    remaining_stages = all_stages[current_index + 1:]

    if not remaining_stages:
        bot.send_message(message.chat.id, "✅ Вы уже на финальном этапе!")
        return

    text = "📋 Последующие этапы:\n"
    for i, (_, title) in enumerate(remaining_stages, start=1):
        number = f"{i}️⃣"
        text += f"{number} {title}\n"

    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("⬅️ Назад"))
    bot.send_message(message.chat.id, text, reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "📚 Часто задаваемые вопросы")
def show_faq(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    for question in FAQ:
        markup.add(KeyboardButton(question))
    markup.add(KeyboardButton("⬅️ Назад"))
    bot.send_message(message.chat.id, "Выберите вопрос:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text in FAQ)
def answer_faq(message):
    answer = FAQ.get(message.text)
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("⬅️ Назад"))
    bot.send_message(message.chat.id, answer, reply_markup=markup)

bot.polling()