from django import template
from django.conf import settings
from social_core.backends.utils import load_backends

register = template.Library()


def get_active_social_backends():
    """Return a list of backend names that are enabled in settings."""
    return load_backends(settings.AUTHENTICATION_BACKENDS)


def get_social_auth_backend_name_map() -> dict:
    return {
        "google-oauth2": "Google",
        "apple-id": "Apple",
        "github": "GitHub",
        "facebook": "Facebook",
        "linkedin-openidconnect": "LinkedIn",
    }


@register.filter
def get_friendly_name(backend_name):
    mapping = get_social_auth_backend_name_map()
    return mapping.get(backend_name, backend_name)


@register.filter
def get_friendly_icon(backend_name):
    icons = {
        "google-oauth2": "users/icons/google.svg",
        "apple-id": "users/icons/apple.svg",
        "github": "users/icons/github.svg",
        "facebook": "users/icons/facebook.svg",
        "linkedin-openidconnect": "users/icons/linkedin.svg",
    }
    return icons.get(
        backend_name, "users/icons/password.png"
    )  # Default icon if none match
