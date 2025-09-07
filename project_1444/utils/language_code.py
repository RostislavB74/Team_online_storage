from django.conf import settings
from django.http import HttpRequest
from django.utils.translation import get_language
from rest_framework.request import Request


def get_language_code(
    request: Request | HttpRequest, default: str = settings.LANGUAGE_CODE
) -> str:
    lang = request.GET.get("lang", "").strip()[:6].lower()
    if lang == "" and ("Accept-Language" in request.headers):
        # lang = request.headers["Accept-Language"].split(",")[0][:6].lower()
        lang = get_language()
    lang = lang if lang in settings.PARLER_LANGUAGES_LIST else default
    # print(f"get_language_code {lang=}")
    return lang
