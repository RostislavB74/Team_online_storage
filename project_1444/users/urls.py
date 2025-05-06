from django.urls import path
from .views import (
    LoginAPIView,
    RegisterAPIView,
    VerifyOTPAPIView,
    ProfileAPIView,
    LogoutAPIView,
    NotificationSettingsAPIView,
    CSRFAPIView,
    JsonObtainAuthToken,
    ListSocialBackends,
    SocialAuthSuccessToken,
    UnRegisterAPIView,
    VerifyOTPUnRegister,
)

# from rest_framework.authtoken.views import ObtainAuthToken

urlpatterns = [
    path("auth/csrf/", CSRFAPIView.as_view(), name="api_get_csrf_token"),
    path("auth/login/", LoginAPIView.as_view(), name="api_login"),
    path("auth/register/", RegisterAPIView.as_view(), name="api_register"),
    path(
        "auth/register/verify/",
        VerifyOTPAPIView.as_view(),
        name="api_register_verify_otp",
    ),
    path("auth/unregister/", UnRegisterAPIView.as_view(), name="api_unregister"),
    path(
        "auth/unregister/verify/",
        VerifyOTPUnRegister.as_view(),
        name="api_unregister_verify_otp",
    ),
    path("auth/logout/", LogoutAPIView.as_view(), name="api_logout"),
    path("auth/token/", JsonObtainAuthToken.as_view(), name="api_token"),
    path("user/profile/", ProfileAPIView.as_view(), name="api_profile"),
    path(
        "user/notifications/",
        NotificationSettingsAPIView.as_view(),
        name="api_notifications",
    ),
    path(
        "social-auth/backends/",
        ListSocialBackends.as_view(),
        name="social_auth_backends",
    ),
    path(
        "social-auth/token/",
        SocialAuthSuccessToken.as_view(),
        name="social_auth_success_token",
    ),
]
