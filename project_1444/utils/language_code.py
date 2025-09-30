from django.conf import settings
from rest_framework.request import Request
from django.http import HttpRequest
from django.utils.translation import get_language


def get_language_code(
    request: Request | HttpRequest, default: str = settings.LANGUAGE_CODE
) -> str:
    # Для DRF використовуємо query_params, для звичайного Django — GET
    lang = (
        request.query_params.get("lang")
        if isinstance(request, Request)
        else request.GET.get("lang")
    )
    if lang:
        lang = lang.strip()[:6].lower()
    else:
        # Якщо lang не вказано, перевіряємо Accept-Language
        if "Accept-Language" in request.headers:
            lang = request.headers["Accept-Language"].split(",")[0][:6].lower()
        else:
            lang = get_language()  # Поточна мова Django
    # Перевіряємо, чи мова підтримується
    supported_languages = getattr(settings, "PARLER_LANGUAGES_LIST", ["uk", "en"])
    lang = lang if lang in supported_languages else default
    print(f"Language from request: {lang}")  # Дебаг
    return lang


# def get_language_code(
#     request: Request | HttpRequest, default: str = settings.LANGUAGE_CODE
# ) -> str:
#     lang = request.GET.get("lang", "uk").strip()[:6].lower()
#     if lang == "" and ("Accept-Language" in request.headers):
#         # lang = request.headers["Accept-Language"].split(",")[0][:6].lower()
#         lang = get_language()
#     lang = lang if lang in settings.PARLER_LANGUAGES_LIST else default
#     # print(f"get_language_code {lang=}")
#     # return lang
#     print(f"Language from request: {lang}")
#     return request.GET.get("lang", settings.LANGUAGE_CODE)


# def get_language_code(request):
#     lang = request.query_params.get("lang", "uk")  # Використовуй query_params для DRF
#     print(f"Language from request: {lang}")  # Дебаг
#     return lang
