from django import template

register = template.Library()


@register.filter
def get_friendly_name(backend_name):
    mapping = {
        "google-oauth2": "Google",
        "apple-id": "Apple",
        "github": "GitHub",
        "facebook": "Facebook",
        "linkedin-openidconnect": "LinkedIn",
    }
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
