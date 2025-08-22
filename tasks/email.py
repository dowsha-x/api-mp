import smtplib
from email.mime.text import MIMEText

from core.celery import celery_app

SMTP_SERVER = "mailhog"
SMTP_PORT = 1025
FROM_EMAIL = "noreply@example.com"


@celery_app.task(name="tasks.email.send_registration_email")
def send_registration_email(email: str, name: str):
    """
    Отправляет письмо о успешной регистрации пользователю.

    Args:
        email (str): Адрес электронной почты получателя.
        name (str): Имя пользователя для персонализации письма.

    Notes:
        Использует локальный SMTP-сервер (по умолчанию localhost:1025).
        Выполняется как фоновая задача Celery.
    """
    subject = "Регистрация прошла успешно"
    body = f"Здравствуйте, {name}!\n\nВы успешно зарегистрировались."

    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = FROM_EMAIL
    msg["To"] = email

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.send_message(msg)
