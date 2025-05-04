from django.contrib.sessions.middleware import SessionMiddleware
from django.utils.functional import SimpleLazyObject
from django.conf import settings
from rest_framework.reverse import reverse_lazy


class AdminOnlySessionMiddleware(SessionMiddleware):

    SESSION_NAME = settings.SESSION_COOKIE_NAME or "sessionid"
    ADMIN_PREFIX = reverse_lazy("admin:index").rstrip("/")
    ADMIN_LOGOUT_PREFIX = reverse_lazy("admin:logout").rstrip("/")

    @staticmethod
    def get_admin_prefix():
        try:
            return reverse_lazy("admin:index").rstrip("/")
        except Exception:
            return "/admin"  # fallback during early stage

    @staticmethod
    def get_admin_logout_prefix():
        try:
            return reverse_lazy("admin:logout").rstrip("/")
        except Exception:
            return "/admin/logout"  # fallback during early stage

    def process_request(self, request):
        if request.path.startswith(self.ADMIN_PREFIX):
            # Use custom session cookie key
            session_key = request.COOKIES.get(self.SESSION_NAME)
            request.session = self.SessionStore(session_key)
        else:
            # Dummy session that behaves like a dict but does nothing
            request.session = SimpleLazyObject(lambda: {})

    def process_response(self, request, response):
        if (
            request.path.startswith(self.ADMIN_PREFIX)
            and hasattr(request, "session")
            and request.session.modified
        ):
            request.session.save()
            if request.path.startswith(self.ADMIN_LOGOUT_PREFIX):
                response.delete_cookie(
                    self.SESSION_NAME,
                    path=self.ADMIN_PREFIX,
                    domain=settings.SESSION_COOKIE_DOMAIN,
                )
            else:
                response.set_cookie(
                    self.SESSION_NAME,
                    request.session.session_key,
                    max_age=settings.SESSION_COOKIE_AGE,
                    domain=settings.SESSION_COOKIE_DOMAIN,
                    path=self.ADMIN_PREFIX,
                    secure=settings.SESSION_COOKIE_SECURE,
                    httponly=True,
                    samesite="lax",
                )
        return response
