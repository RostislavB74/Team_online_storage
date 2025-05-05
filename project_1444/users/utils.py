import logging
import mimetypes

from django.core.files.base import ContentFile
from django.core.mail import send_mail
import requests  # Для Telegram API або SMS-сервісу


logger = logging.getLogger(__name__)


# Відправка OTP на email
# def send_otp_via_email(email, otp):
#     subject = "Ваш код підтвердження"
#     message = f"Ваш код підтвердження: {otp}"
#     from_email = "your_email@gmail.com"
#     recipient_list = [email]
#     send_mail(subject, message, from_email, recipient_list)


# Відправка OTP через SMS (замінити на реальний API)
def send_otp_via_sms(phone, otp):
    sms_service_url = "https://api.your-sms-service.com/send"
    sms_api_key = "your_sms_api_key"
    payload = {
        "phone": phone,
        "message": f"Ваш код підтвердження: {otp}",
        "api_key": sms_api_key,
    }
    requests.post(sms_service_url, json=payload)


# Відправка OTP через Telegram бот
def send_otp_via_telegram(username, otp):
    bot_token = "your_telegram_bot_token"
    telegram_api_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": username,  # Потрібно знати ID користувача
        "text": f"Ваш код підтвердження: {otp}",
    }
    requests.post(telegram_api_url, json=payload)


# def send_otp_via_email(email, otp):
#     subject = "Ваш код підтвердження"
#     message = f"Ваш код підтвердження: {otp}"
#     from_email = "your_email@gmail.com"
#     recipient_list = [email]

#     send_mail(subject, message, from_email, recipient_list)


def send_email_in_background(*args, **kwargs):
    logger.debug("Sending email in background...")
    return send_mail(*args, **kwargs)


def mark_social_login(strategy, backend, user=None, *args, **kwargs):
    if user:
        strategy.session_set("is_social_login", True)
        # Force session to be saved
        if hasattr(strategy, "request") and hasattr(strategy.request, "session"):
            strategy.request.session.modified = True


def set_avatar_from_url(user, url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            content_type = response.headers.get("Content-Type", "")
            extension = mimetypes.guess_extension(content_type.split(";")[0].strip())

            # Fallback to .jpg if extension couldn't be guessed
            extension = extension or ".jpg"

            filename = f"{user.username}_avatar{extension}"
            user.profile.avatar.save(filename, ContentFile(response.content), save=True)
    except Exception as e:
        logger.error(f"Set Avatar from URL: {e}")


def set_profile_avatar_from_social(
    backend, user, response, is_new=False, *args, **kwargs
):
    if not is_new:
        return  # Skip for existing users

    url = None

    if backend.name == "google-oauth2":
        url = response.get("picture")
    elif backend.name == "facebook":
        url = f"https://graph.facebook.com/{response.get('id')}/picture?type=large"
    elif backend.name == "github":
        url = response.get("avatar_url")
    elif backend.name == "linkedin-openidconnect":
        try:
            elements = (
                response.get("profilePicture", {})
                .get("displayImage~", {})
                .get("elements", [])
            )
            if elements:
                identifiers = elements[-1].get("identifiers", [])
                if identifiers:
                    url = identifiers[0].get("identifier")
        except Exception as e:
            logger.error(f"Get Avatar url from LinkedIn. {e}")

    if url:
        try:
            profile = getattr(user, "profile", None)
            if profile and hasattr(profile, "avatar"):
                set_avatar_from_url(user, url)
        except Exception as e:
            logger.error(f"Save Avatar to profile. {e}")
