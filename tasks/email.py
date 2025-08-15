from core.celery import celery_app
import smtplib
from email.mime.text import MIMEText

SMTP_SERVER = "localhost"  # или smtp.gmail.com, если хочешь реальный сервер
SMTP_PORT = 1025  # порт локального debug SMTP сервера
FROM_EMAIL = "noreply@example.com"  # от кого письмо


@celery_app.task
def send_registration_email(email: str, name: str):
    subject = "Регистрация прошла успешно"
    body = f"Здравствуйте, {name}!\n\nВы успешно зарегистрировались."

    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = FROM_EMAIL
    msg["To"] = email

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.send_message(msg)
