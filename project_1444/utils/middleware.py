import time

from django.contrib.sessions.backends.base import UpdateError
from django.contrib.sessions.exceptions import SessionInterrupted
from django.contrib.sessions.middleware import SessionMiddleware
from django.urls import reverse
from django.utils.cache import patch_vary_headers
from django.conf import settings
from django.utils.http import http_date


class AdminSplitterSessionMiddleware(SessionMiddleware):
    def __init__(self, get_response):
        super().__init__(get_response)
        self.ADMIN_SESSION_COOKIE_NAME = "adminsessionid"
        self.ADMIN_PREFIX = reverse("admin:index").rstrip("/")
        self.ADMIN_SESSION_COOKIE_SAMESITE = "lax"
        self.ADMIN_SESSION_COOKIE_HTTPONLY = True

    def get_is_admin(self, request):
        return request.path.startswith(self.ADMIN_PREFIX)

    def get_session_cookie_name(self, is_admin: bool):
        return (
            self.ADMIN_SESSION_COOKIE_NAME if is_admin else settings.SESSION_COOKIE_NAME
        )

    def get_session_cookie_path(self, is_admin: bool):
        return self.ADMIN_PREFIX if is_admin else settings.SESSION_COOKIE_PATH

    def get_session_cookie_samesite(self, is_admin: bool):
        return (
            self.ADMIN_SESSION_COOKIE_SAMESITE
            if is_admin
            else settings.SESSION_COOKIE_SAMESITE
        )

    def get_session_cookie_httponly(self, is_admin: bool):
        return (
            self.ADMIN_SESSION_COOKIE_HTTPONLY
            if is_admin
            else settings.SESSION_COOKIE_HTTPONLY
        )

    def process_request(self, request):
        session_cookie_name = self.get_session_cookie_name(self.get_is_admin(request))
        session_key = request.COOKIES.get(session_cookie_name)
        request.session = self.SessionStore(session_key)

    def process_response(self, request, response):
        """
        If request.session was modified, or if the configuration is to save the
        session every time, save the changes and set a session cookie or delete
        the session cookie if the session has been emptied.
        """
        try:
            accessed = request.session.accessed
            modified = request.session.modified
            empty = request.session.is_empty()
        except AttributeError:
            return response
        is_admin = self.get_is_admin(request)
        session_cookie_name = self.get_session_cookie_name(is_admin)
        session_cookie_path = self.get_session_cookie_path(is_admin)
        session_cookie_samesite = self.get_session_cookie_samesite(is_admin)
        session_cookie_httponly = self.get_session_cookie_httponly(is_admin)

        # First check if we need to delete this cookie.
        # The session should be deleted only if the session is entirely empty.
        if session_cookie_name in request.COOKIES and empty:
            response.delete_cookie(
                session_cookie_name,
                path=session_cookie_path,
                domain=settings.SESSION_COOKIE_DOMAIN,
                samesite=session_cookie_samesite,
            )
            patch_vary_headers(response, ("Cookie",))
        else:
            if accessed:
                patch_vary_headers(response, ("Cookie",))
            if (modified or settings.SESSION_SAVE_EVERY_REQUEST) and not empty:
                if request.session.get_expire_at_browser_close():
                    max_age = None
                    expires = None
                else:
                    max_age = request.session.get_expiry_age()
                    expires_time = time.time() + max_age
                    expires = http_date(expires_time)
                # Save the session data and refresh the client cookie.
                # Skip session save for 5xx responses.
                if response.status_code < 500:
                    try:
                        request.session.save()
                    except UpdateError:
                        raise SessionInterrupted(
                            "The request's session was deleted before the "
                            "request completed. The user may have logged "
                            "out in a concurrent request, for example."
                        )
                    response.set_cookie(
                        session_cookie_name,
                        request.session.session_key,
                        max_age=max_age,
                        expires=expires,
                        domain=settings.SESSION_COOKIE_DOMAIN,
                        path=session_cookie_path,
                        secure=settings.SESSION_COOKIE_SECURE or None,
                        httponly=session_cookie_httponly or None,
                        samesite=session_cookie_samesite,
                    )
        return response
