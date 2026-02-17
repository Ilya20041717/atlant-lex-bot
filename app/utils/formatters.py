from decimal import Decimal

from app.constants import DOCUMENT_STATUS_LABELS, PAYMENT_STATUS_LABELS, TASK_STATUS_LABELS


DISCLAIMER = "Окончательное решение принимает специалист агентства."


def with_disclaimer(text: str) -> str:
    return f"{text}\n\n{DISCLAIMER}"


def format_money(value) -> str:
    if value is None:
        return "—"
    if isinstance(value, Decimal):
        value = value.quantize(Decimal("0.01"))
    return f"{value} руб."


def format_tasks(tasks) -> str:
    if not tasks:
        return "Задачи клиента: не назначены."
    lines = ["Задачи клиента:"]
    for task in tasks:
        status = TASK_STATUS_LABELS.get(task.status, task.status)
        lines.append(f"- {task.title} ({status})")
    return "\n".join(lines)


def format_client_cabinet(client, stage, tasks) -> str:
    if not client:
        return (
            "Данные клиента не найдены. Доступ к кабинету откроется "
            "после подтверждения менеджером."
        )
    stage_title = stage.title if stage else "не назначен"
    stage_desc = stage.description if stage else "—"
    next_step = client.next_step or "—"
    return (
        f"Текущий этап: {stage_title}\n"
        f"Описание этапа: {stage_desc}\n"
        f"Следующий шаг: {next_step}\n\n"
        f"{format_tasks(tasks)}"
    )


def format_documents(documents) -> str:
    if not documents:
        return "Список документов пока не сформирован."
    lines = ["Документы клиента:"]
    for doc in documents:
        status = DOCUMENT_STATUS_LABELS.get(doc.status, doc.status)
        lines.append(f"- {doc.title}: {status}")
    return "\n".join(lines)


def format_payments(client, payments) -> str:
    if not client:
        return (
            "Данные клиента не найдены. Финансовый раздел появится "
            "после подтверждения менеджером."
        )
    total = format_money(client.total_cost)
    paid = format_money(client.paid_amount)
    balance_value = None
    if client.total_cost is not None and client.paid_amount is not None:
        balance_value = client.total_cost - client.paid_amount
    balance = format_money(balance_value)
    lines = [
        f"Стоимость услуг: {total}",
        f"Оплачено: {paid}",
        f"Остаток: {balance}",
    ]
    if not payments:
        lines.append("График платежей: не сформирован.")
        return "\n".join(lines)
    lines.append("График платежей:")
    for payment in payments:
        status = PAYMENT_STATUS_LABELS.get(payment.status, payment.status)
        lines.append(
            f"- {payment.due_date}: {format_money(payment.amount)} ({status})"
        )
    return "\n".join(lines)


def format_notifications(notifications) -> str:
    if not notifications:
        return (
            "Автоуведомления в разработке. "
            "Пока напоминания формируются вручную."
        )
    lines = ["Запланированные напоминания:"]
    for item in notifications:
        lines.append(f"- {item.scheduled_at}: {item.text}")
    return "\n".join(lines)
