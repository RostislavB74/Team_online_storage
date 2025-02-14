# from django.core.mail import send_mail

# def send_otp_via_email(email, otp):
#     subject = "Ваш код підтвердження"
#     message = f"Ваш код підтвердження: {otp}"
#     from_email = "your_email@gmail.com"
#     recipient_list = [email]

#     send_mail(subject, message, from_email, recipient_list)
from django.core.mail import send_mail
import requests  # Для Telegram API або SMS-сервісу

# Відправка OTP на email
def send_otp_via_email(email, otp):
    subject = "Ваш код підтвердження"
    message = f"Ваш код підтвердження: {otp}"
    from_email = "your_email@gmail.com"
    recipient_list = [email]
    send_mail(subject, message, from_email, recipient_list)

# Відправка OTP через SMS (замінити на реальний API)
def send_otp_via_sms(phone, otp):
    sms_service_url = "https://api.your-sms-service.com/send"
    sms_api_key = "your_sms_api_key"
    payload = {
        "phone": phone,
        "message": f"Ваш код підтвердження: {otp}",
        "api_key": sms_api_key
    }
    requests.post(sms_service_url, json=payload)

# Відправка OTP через Telegram бот
def send_otp_via_telegram(username, otp):
    bot_token = "your_telegram_bot_token"
    telegram_api_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": username,  # Потрібно знати ID користувача
        "text": f"Ваш код підтвердження: {otp}"
    }
    requests.post(telegram_api_url, json=payload)
