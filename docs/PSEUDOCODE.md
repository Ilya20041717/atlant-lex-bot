## Псевдокод логики

### /start
```
on /start:
    clear FSM state
    ensure user in DB
    show status menu:
        "Я только интересуюсь"
        "Я уже работаю с агентством"
        "Я сотрудник агентства"
```

### Выбор статуса
```
if "Я только интересуюсь":
    set role = lead
    show lead menu

if "Я уже работаю с агентством":
    set role = client
    if client record exists:
        show client menu
    else:
        show "данные клиента не найдены"

if "Я сотрудник агентства":
    set role = employee
    show stub message
```

### Лид: информация и FAQ
```
if lead selects info section:
    send text + disclaimer

if lead selects FAQ topic:
    send short neutral answer + disclaimer
```

### Лид: анкета
```
start survey:
    ask debt_amount
    ask creditors_count
    ask overdue_months
    ask income
    ask assets
    ask region
    save to lead_profiles without evaluation
    confirm saved
```

### Клиент: кабинет
```
if client selects "Личный кабинет":
    load client, stage, tasks
    show current stage, description, next step, tasks
```

### Клиент: документы
```
if client selects "Документы":
    load document list and statuses
    show list
    [ЗАГЛУШКА] upload feature
```

### Клиент: напоминания
```
if client selects "Напоминания":
    [ЗАГЛУШКА] auto notification scheduling
```

### Клиент: финансы
```
if client selects "Финансы":
    show total, paid, balance, schedule
    [ЗАГЛУШКА] payment integration
```
