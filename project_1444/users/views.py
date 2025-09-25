import logging
import random
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.text import format_lazy
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from drf_spectacular.types import OpenApiTypes
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiExample,
    OpenApiResponse,
)
from cart.models import Cart
from .models import UserProfile, OTP, UserNotificationSettings
from .serializers import (
    LoginSerializer,
    RegisterSerializer,
    OTPSerializer,
    UserProfileSerializer,
    TokenSerializer,
    LogoutSerializer,
    UserNotificationSettingsSerializer,
    SocialBackendSerializer,
    OTPResponseSerializer,
    ErrorResponseSerializer,
)
from .templatetags.social_extras import (
    get_social_auth_backend_name_map,
    get_active_social_backends,
    get_social_auth_backend_icon_map,
)
from .utils import send_email_in_background

logger = logging.getLogger(__name__)

STATIC_PREFIX_EXAMPLE = "https://static.example.com/"


class ListSocialBackends(APIView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.STATIC_PREFIX = getattr(settings, "STATIC_URL", "")

    @extend_schema(
        responses={
            status.HTTP_200_OK: OpenApiTypes.OBJECT,
        },
        examples=[
            OpenApiExample(
                name="SocialBackendsExample",
                value={
                    "google-oauth2": {
                        "name": "Google",
                        "icon": STATIC_PREFIX_EXAMPLE + "users/icons/google.svg",
                    },
                    "github": {
                        "name": "GitHub",
                        "icon": STATIC_PREFIX_EXAMPLE + "users/icons/github.svg",
                    },
                    "linkedin-openidconnect": {
                        "name": "LinkedIn",
                        "icon": STATIC_PREFIX_EXAMPLE + "users/icons/linkedin.svg",
                    },
                },
                response_only=True,
            )
        ],
        description=format_lazy(
            _(
                "List of Active Social Auth Backends names for later use in API URL for social auth like: `{}`"
            ),
            "/social-auth/login/{backend}/",
        ),
        tags=["auth"],
    )
    def get(self, request):
        friendly_names = get_social_auth_backend_name_map()
        friendly_icons = get_social_auth_backend_icon_map()
        active_backend_names = get_active_social_backends().keys()
        result = {
            key: {
                "name": friendly_names[key],
                "icon": self.STATIC_PREFIX + friendly_icons.get(key),
            }
            for key in active_backend_names
            if key in friendly_names
        }
        serialized_data = {
            backend: SocialBackendSerializer(value).data
            for backend, value in result.items()
        }
        return Response(serialized_data)


@method_decorator(csrf_exempt, name="dispatch")
class SocialAuthSuccessToken(APIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]

    def __init__(self):
        super().__init__()
        self.force_logout = getattr(
            settings, "SOCIAL_AUTH_FORCE_LOGOUT_AFTER_TOKEN", True
        )

    @extend_schema(
        responses={
            status.HTTP_200_OK: {
                "type": "object",
                "properties": {
                    "token": {"type": "string", "example": "3234373847856878436"}
                },
            }
        },
        description=_(
            "Retrieves the authentication token for the user after a successful social login. "
            "This is the default callback for the Social Auth URL: `/social-auth/login/{backend}/`. "
            "Appending a custom `?next={callback}` is optional and only required if you want to override the default redirect."
        ),
        tags=["auth"],
    )
    def get(self, request):
        if not request.user.is_authenticated:
            return JsonResponse(
                {"error": "Not authenticated"}, status=status.HTTP_401_UNAUTHORIZED
            )
        if not request.session.get("is_social_login"):
            return JsonResponse(
                {"error": "This endpoint is only for social login users."},
                status=status.HTTP_403_FORBIDDEN,
            )
        referer = request.META.get("HTTP_REFERER")
        logger.debug(f"REFERER: {referer}")
        CSRF_TRUSTED_ORIGINS = getattr(settings, "CSRF_TRUSTED_ORIGINS", [])
        if referer and len(CSRF_TRUSTED_ORIGINS) > 0:
            from urllib.parse import urlparse

            parsed = urlparse(referer)
            referer_origin = f"{parsed.scheme}://{parsed.netloc}"
            logger.debug(f"{referer_origin=}")
            if referer_origin not in CSRF_TRUSTED_ORIGINS:
                return JsonResponse(
                    {"error": "Invalid referer domain."},
                    status=status.HTTP_403_FORBIDDEN,
                )

        request.session.pop("is_social_login", None)
        request.session.modified = True  # this forces save
        token, created = Token.objects.get_or_create(user=request.user)
        if self.force_logout:
            logout(request)
        return JsonResponse({"token": token.key})


@extend_schema_view(
    post=extend_schema(
        description=_("Get the authentication token for the user"),
        tags=["auth"],
    )
)
class JsonObtainAuthToken(ObtainAuthToken):
    parser_classes = (JSONParser,)


class CSRFAPIView(APIView):
    @method_decorator(ensure_csrf_cookie)
    @extend_schema(
        responses={
            status.HTTP_200_OK: {
                "type": "object",
                "properties": {
                    "message": {"type": "string", "example": "CSRF cookie set"}
                },
            }
        },
        description="Sets the CSRF cookie and returns a confirmation message.",
    )
    def get(self, request):
        return JsonResponse({"message": "CSRF cookie set"})


def merge_carts(user, session_key):
    guest_carts = Cart.objects.filter(session_key=session_key)
    for guest_cart in guest_carts:
        user_cart, created = Cart.objects.get_or_create(
            user=user,
            product=guest_cart.product,
            defaults={"quantity": guest_cart.quantity},
        )
        if not created:
            user_cart.quantity += guest_cart.quantity
            user_cart.save()
    guest_carts.delete()


def send_otp_by_email(request, user):
    otp_code = "".join(random.choices("0123456789", k=6))
    expires_at = timezone.now() + timedelta(
        minutes=getattr(settings, "OTP_EXPIRATION_TIME", 15)
    )

    OTP.objects.update_or_create(
        user=user,
        defaults={
            "code": otp_code,
            "expires_at": expires_at,
        },
    )

    # Відправка OTP на email
    try:
        html_message = render_to_string(
            "emails/otp_email.html",
            {
                "otp_code": otp_code,
                "expiration_time": getattr(settings, "OTP_EXPIRATION_TIME", 15),
            },
        )
        send_email_in_background(
            subject=_("Your OTP Code"),
            message=_("Your verification code is ") + otp_code,
            from_email=None,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        logger.info(f"OTP sent to {user.email}: {otp_code}")
    except Exception as e:
        logger.error(f"Failed to send OTP to {user.email}: {str(e)}")
        return Response(
            {
                "status": "error",
                "message": _("Failed to send OTP. Please try again."),
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    request.session["otp_user_id"] = user.id
    return {
        "status": "otp_sent",
        "message": _("OTP sent to your email"),
        "otp_user_id": user.id,
    }


class LoginAPIView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]

    @extend_schema(
        request=LoginSerializer,
        responses={status.HTTP_200_OK: TokenSerializer},
        description=_("Аутентифікація користувача та генерація OTP"),
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            username = serializer.validated_data["username"]
            password = serializer.validated_data["password"]
            user = authenticate(username=username, password=password)
            if not user:
                raise Exception("Invalid credentials")
        except Exception:
            return Response(
                {"status": "error", "message": _("Invalid credentials")},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not user.email:
            return Response(
                {
                    "status": "error",
                    "message": _("Email address is required for OTP verification"),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        data = send_otp_by_email(request, user)

        return Response(data=data, status=status.HTTP_200_OK)


class VerifyOTPAPIView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]

    @extend_schema(
        request=OTPSerializer,
        responses={status.HTTP_200_OK: TokenSerializer},
        description=_("Верифікація OTP та видача токена"),
    )
    def post(self, request):
        serializer = OTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        otp_code = serializer.validated_data["otp_code"]
        user_id = serializer.validated_data.get("otp_user_id") or request.session.get(
            "otp_user_id"
        )
        if not user_id:
            return Response(
                {"status": "error", "message": _("Invalid session")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {"status": "error", "message": _("User not found")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        otp = OTP.objects.filter(
            user=user, code=otp_code, expires_at__gte=timezone.now()
        ).first()
        if otp:
            login(request, user, "django.contrib.auth.backends.ModelBackend")
            otp.delete()
            merge_carts(user, request.session.session_key)
            token, created = Token.objects.get_or_create(user=user)
            if created and user.is_active is False:
                user.is_active = True
                user.save()

            if "otp_user_id" in request.session:
                del request.session["otp_user_id"]
            return Response(
                {
                    "status": "success",
                    "message": _("Welcome, {username}!").format(username=user.username),
                    "token": token.key,
                    "user_id": user.pk,
                    "username": user.username,
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {"status": "error", "message": _("Invalid or expired OTP")},
            status=status.HTTP_400_BAD_REQUEST,
        )


class RegisterAPIView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]

    @extend_schema(
        request=RegisterSerializer,
        responses={status.HTTP_201_CREATED: TokenSerializer},
        description=_("Реєстрація нового користувача"),
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        # login(request, user, "django.contrib.auth.backends.ModelBackend")
        if not user.email:
            user.delete()
            return Response(
                {
                    "status": "error",
                    "message": _("Email address is required for OTP verification"),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        data = send_otp_by_email(request, user)
        otp_status = data.get("status")
        if otp_status == "error" or otp_status is None:
            user.delete()
            return Response(
                {
                    "status": otp_status,
                    "message": _("Failed to send OTP. Please try again."),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        # token, created = Token.objects.get_or_create(user=user)
        return Response(
            {
                "status": otp_status,
                "message": _("Registration successful. {message}").format(
                    message=data.get("message", "")
                ),
                # "token": token.key,
                "user_id": user.pk,
                "username": user.username,
            },
            status=status.HTTP_201_CREATED,
        )


class ProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=UserProfileSerializer,
        responses={status.HTTP_200_OK: UserProfileSerializer},
        description=_("Отримання або оновлення профілю користувача"),
    )
    def get(self, request):
        try:
            profile = request.user.profile
        except UserProfile.DoesNotExist:
            profile = UserProfile.objects.create(user=request.user)

        # Оптимізуємо запит із prefetch_related для замовлень
        profile = UserProfile.objects.prefetch_related(
            "user__orders__items__product"
        ).get(user=request.user)

        serializer = UserProfileSerializer(profile, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=UserProfileSerializer,
        responses={status.HTTP_200_OK: UserProfileSerializer},
    )
    def post(self, request):
        try:
            profile = request.user.profile
        except UserProfile.DoesNotExist:
            profile = UserProfile.objects.create(user=request.user)
        serializer = UserProfileSerializer(
            profile, data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "status": "success",
                    "message": _("Profile updated"),
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {
                "status": "error",
                "message": _("Invalid profile data"),
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


# class ProfileAPIView(APIView):
#     permission_classes = [IsAuthenticated]

#     @extend_schema(
#         request=UserProfileSerializer,
#         responses={status.HTTP_200_OK: UserProfileSerializer},
#         description="Отримання або оновлення профілю користувача"
#     )
#     def get(self, request):
#         try:
#             profile = request.user.profile
#         except UserProfile.DoesNotExist:
#             profile = UserProfile.objects.create(user=request.user)
#         serializer = UserProfileSerializer(profile, context={'request': request})
#         return Response(serializer.data, status=status.HTTP_200_OK)

#     @extend_schema(
#         request=UserProfileSerializer,
#         responses={status.HTTP_200_OK: UserProfileSerializer}
#     )
#     def post(self, request):
#         try:
#             profile = request.user.profile
#         except UserProfile.DoesNotExist:
#             profile = UserProfile.objects.create(user=request.user)
#         serializer = UserProfileSerializer(profile, data=request.data, context={'request': request})
#         if serializer.is_valid():
#             serializer.save()
#             return Response({
#                 'status': 'success',
#                 'message': 'Profile updated',
#                 'data': serializer.data
#             }, status=status.HTTP_200_OK)
#         return Response({
#             'status': 'error',
#             'message': 'Invalid profile data',
#             'errors': serializer.errors
#         }, status=status.HTTP_400_BAD_REQUEST)


class NotificationSettingsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=UserNotificationSettingsSerializer,
        responses={status.HTTP_200_OK: UserNotificationSettingsSerializer},
        description=_("Отримання або оновлення налаштувань сповіщень"),
    )
    def get(self, request):
        try:
            settings = request.user.notifications
        except UserNotificationSettings.DoesNotExist:
            settings = UserNotificationSettings.objects.create(user=request.user)
        serializer = UserNotificationSettingsSerializer(settings)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=UserNotificationSettingsSerializer,
        responses={status.HTTP_200_OK: UserNotificationSettingsSerializer},
    )
    def post(self, request):
        try:
            settings = request.user.notifications
        except UserNotificationSettings.DoesNotExist:
            settings = UserNotificationSettings.objects.create(user=request.user)
        serializer = UserNotificationSettingsSerializer(settings, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "status": "success",
                    "message": "Notification settings updated",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {
                "status": "error",
                "message": "Invalid notification settings",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=None,
        responses={status.HTTP_200_OK: LogoutSerializer},
        description=_("Вихід користувача та видалення токена"),
    )
    def post(self, request):
        try:
            logout(request)
            request.user.auth_token.delete()
        except (AttributeError, Token.DoesNotExist):
            pass
        return Response(
            {"status": "success", "message": _("Successfully logged out")},
            status=status.HTTP_200_OK,
        )


class UnRegisterAPIView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]

    @extend_schema(
        request=None,
        description=_("Запит на видалення користувача (надсилається OTP)"),
        responses={
            status.HTTP_202_ACCEPTED: OpenApiResponse(
                response=OTPResponseSerializer,
                description=_("OTP code was sent successfully"),
            ),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                response=ErrorResponseSerializer,
                description=_("Missing email address or invalid input"),
            ),
            status.HTTP_401_UNAUTHORIZED: OpenApiResponse(
                response=ErrorResponseSerializer,
                description=_("User is not authenticated"),
            ),
            status.HTTP_500_INTERNAL_SERVER_ERROR: OpenApiResponse(
                response=ErrorResponseSerializer, description=_("Failed to send OTP")
            ),
        },
    )
    def post(self, request):
        user = request.user
        if not user.is_authenticated:
            return Response(
                {
                    "status": "error",
                    "message": _("Unauthorized"),
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )
        # login(request, user, "django.contrib.auth.backends.ModelBackend")
        if not user.email:
            return Response(
                {
                    "status": "error",
                    "message": _("Email address is required for OTP verification"),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        data = send_otp_by_email(request, user)
        otp_status = data.get("status")
        if otp_status == "error":
            return Response(
                {
                    "status": otp_status,
                    "message": _("Failed to send OTP. Please try again."),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        return Response(
            {
                "status": otp_status,
                "message": _("OTP code was sent for continue UnRegistration")
                + ". "
                + data.get("message"),
                "user_id": user.pk,
            },
            status=status.HTTP_202_ACCEPTED,
        )


class VerifyOTPUnRegister(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]

    @extend_schema(
        request=OTPSerializer,
        responses={
            status.HTTP_204_NO_CONTENT: OpenApiResponse(
                description=_("Користувача успішно видалено після верифікації OTP")
            ),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                response=ErrorResponseSerializer,
                description=_("Невірний або прострочений OTP, або помилка сесії"),
            ),
            status.HTTP_401_UNAUTHORIZED: OpenApiResponse(
                response=ErrorResponseSerializer,
                description=_("Користувач не автентифікований"),
            ),
        },
        description=_("Верифікація OTP та остаточне видалення користувача"),
    )
    def post(self, request):
        user = request.user
        if not user or not user.is_authenticated:
            return Response(
                {
                    "status": "error",
                    "message": _("Unauthorized"),
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )
        serializer = OTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        otp_code = serializer.validated_data["otp_code"]
        user_id = serializer.validated_data.get("otp_user_id") or request.session.get(
            "otp_user_id"
        )
        if not user_id or user_id != user.pk:
            return Response(
                {"status": "error", "message": _("Invalid session")},
                status=status.HTTP_400_BAD_REQUEST,
            )
        otp = OTP.objects.filter(
            user=user, code=otp_code, expires_at__gte=timezone.now()
        ).first()
        if otp:
            otp.delete()
            if "otp_user_id" in request.session:
                del request.session["otp_user_id"]
            logout(request)
            user.delete()
            return Response(
                status=status.HTTP_204_NO_CONTENT,
            )
        return Response(
            {"status": "error", "message": _("Invalid or expired OTP")},
            status=status.HTTP_400_BAD_REQUEST,
        )


# import random
# from django.contrib.auth import authenticate, login
# from django.contrib.auth.models import User
# from django.utils import timezone
# from datetime import timedelta
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from rest_framework.authtoken.models import Token
# from rest_framework.permissions import IsAuthenticated, AllowAny
# from rest_framework.throttling import AnonRateThrottle
# from drf_spectacular.utils import extend_schema
# from .models import UserProfile, OTP, UserNotificationSettings
# from .serializers import (
#     LoginSerializer, RegisterSerializer, OTPSerializer,
#     UserProfileSerializer, TokenSerializer, LogoutSerializer,
#     UserNotificationSettingsSerializer
# )
# from cart.models import Cart
# import logging

# logger = logging.getLogger(__name__)

# def merge_carts(user, session_key):
#     guest_carts = Cart.objects.filter(session_key=session_key)
#     for guest_cart in guest_carts:
#         user_cart, created = Cart.objects.get_or_create(
#             user=user,
#             product=guest_cart.product,
#             defaults={'quantity': guest_cart.quantity}
#         )
#         if not created:
#             user_cart.quantity += guest_cart.quantity
#             user_cart.save()
#     guest_carts.delete()

# class LoginAPIView(APIView):
#     permission_classes = [AllowAny]
#     throttle_classes = [AnonRateThrottle]

#     @extend_schema(
#         request=LoginSerializer,
#         responses={status.HTTP_200_OK: TokenSerializer},
#         description="Аутентифікація користувача та генерація OTP"
#     )
#     def post(self, request):
#         serializer = LoginSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         username = serializer.validated_data['username']
#         password = serializer.validated_data['password']
#         user = authenticate(request, username=username, password=password)
#         if user:
#             otp_code = ''.join(random.choices('0123456789', k=6))
#             OTP.objects.create(
#                 user=user,
#                 code=otp_code,
#                 expires_at=timezone.now() + timedelta(minutes=5)
#             )
#             logger.info(f"OTP for {username}: {otp_code}")
#             request.session['otp_user_id'] = user.id
#             return Response({
#                 'status': 'otp_sent',
#                 'message': 'OTP sent to your phone/email',
#                 'otp_user_id': user.id
#             }, status=status.HTTP_200_OK)
#         return Response({
#             'status': 'error',
#             'message': 'Invalid credentials'
#         }, status=status.HTTP_400_BAD_REQUEST)

# class VerifyOTPAPIView(APIView):
#     permission_classes = [AllowAny]
#     throttle_classes = [AnonRateThrottle]

#     @extend_schema(
#         request=OTPSerializer,
#         responses={status.HTTP_200_OK: TokenSerializer},
#         description="Верифікація OTP та видача токена"
#     )
#     def post(self, request):
#         serializer = OTPSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         otp_code = serializer.validated_data['otp_code']
#         user_id = serializer.validated_data.get('otp_user_id') or request.session.get('otp_user_id')
#         if not user_id:
#             return Response({
#                 'status': 'error',
#                 'message': 'Invalid session'
#             }, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             user = User.objects.get(id=user_id)
#         except User.DoesNotExist:
#             return Response({
#                 'status': 'error',
#                 'message': 'User not found'
#             }, status=status.HTTP_400_BAD_REQUEST)

#         otp = OTP.objects.filter(
#             user=user,
#             code=otp_code,
#             expires_at__gte=timezone.now()
#         ).first()
#         if otp:
#             login(request, user)
#             otp.delete()
#             merge_carts(user, request.session.session_key)
#             token, created = Token.objects.get_or_create(user=user)
#             if 'otp_user_id' in request.session:
#                 del request.session['otp_user_id']
#             return Response({
#                 'status': 'success',
#                 'message': f'Welcome, {user.username}!',
#                 'token': token.key,
#                 'user_id': user.pk,
#                 'username': user.username
#             }, status=status.HTTP_200_OK)
#         return Response({
#             'status': 'error',
#             'message': 'Invalid or expired OTP'
#         }, status=status.HTTP_400_BAD_REQUEST)

# class RegisterAPIView(APIView):
#     permission_classes = [AllowAny]
#     throttle_classes = [AnonRateThrottle]

#     @extend_schema(
#         request=RegisterSerializer,
#         responses={201: TokenSerializer},
#         description="Реєстрація нового користувача"
#     )
#     def post(self, request):
#         serializer = RegisterSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         user = serializer.save()
#         login(request, user)
#         token, created = Token.objects.get_or_create(user=user)
#         return Response({
#             'status': 'success',
#             'message': 'Registration successful',
#             'token': token.key,
#             'user_id': user.pk,
#             'username': user.username
#         }, status=status.HTTP_201_CREATED)

# class ProfileAPIView(APIView):
#     permission_classes = [IsAuthenticated]

#     @extend_schema(
#         request=UserProfileSerializer,
#         responses={status.HTTP_200_OK: UserProfileSerializer},
#         description="Отримання або оновлення профілю користувача"
#     )
#     def get(self, request):
#         try:
#             profile = request.user.profile
#         except UserProfile.DoesNotExist:
#             profile = UserProfile.objects.create(user=request.user)
#         serializer = UserProfileSerializer(profile, context={'request': request})
#         return Response(serializer.data, status=status.HTTP_200_OK)

#     @extend_schema(
#         request=UserProfileSerializer,
#         responses={status.HTTP_200_OK: UserProfileSerializer}
#     )
#     def post(self, request):
#         try:
#             profile = request.user.profile
#         except UserProfile.DoesNotExist:
#             profile = UserProfile.objects.create(user=request.user)
#         serializer = UserProfileSerializer(profile, data=request.data, context={'request': request})
#         if serializer.is_valid():
#             serializer.save()
#             return Response({
#                 'status': 'success',
#                 'message': 'Profile updated',
#                 'data': serializer.data
#             }, status=status.HTTP_200_OK)
#         return Response({
#             'status': 'error',
#             'message': 'Invalid profile data',
#             'errors': serializer.errors
#         }, status=status.HTTP_400_BAD_REQUEST)

# class NotificationSettingsAPIView(APIView):
#     permission_classes = [IsAuthenticated]

#     @extend_schema(
#         request=UserNotificationSettingsSerializer,
#         responses={status.HTTP_200_OK: UserNotificationSettingsSerializer},
#         description="Отримання або оновлення налаштувань сповіщень"
#     )
#     def get(self, request):
#         try:
#             settings = request.user.notifications
#         except UserNotificationSettings.DoesNotExist:
#             settings = UserNotificationSettings.objects.create(user=request.user)
#         serializer = UserNotificationSettingsSerializer(settings)
#         return Response(serializer.data, status=status.HTTP_200_OK)

#     @extend_schema(
#         request=UserNotificationSettingsSerializer,
#         responses={status.HTTP_200_OK: UserNotificationSettingsSerializer}
#     )
#     def post(self, request):
#         try:
#             settings = request.user.notifications
#         except UserNotificationSettings.DoesNotExist:
#             settings = UserNotificationSettings.objects.create(user=request.user)
#         serializer = UserNotificationSettingsSerializer(settings, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response({
#                 'status': 'success',
#                 'message': 'Notification settings updated',
#                 'data': serializer.data
#             }, status=status.HTTP_200_OK)
#         return Response({
#             'status': 'error',
#             'message': 'Invalid notification settings',
#             'errors': serializer.errors
#         }, status=status.HTTP_400_BAD_REQUEST)

# class LogoutAPIView(APIView):
#     permission_classes = [IsAuthenticated]

#     @extend_schema(
#         request=None,
#         responses={status.HTTP_200_OK: LogoutSerializer},
#         description="Вихід користувача та видалення токена"
#     )
#     def post(self, request):
#         try:
#             request.user.auth_token.delete()
#         except (AttributeError, Token.DoesNotExist):
#             pass
#         return Response({
#             'status': 'success',
#             'message': 'Successfully logged out'
#         }, status=status.HTTP_200_OK)
# import random
# from django.contrib.auth import authenticate, login
# from django.contrib.auth.models import User
# from django.utils import timezone
# from datetime import timedelta
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from rest_framework.authtoken.models import Token
# from rest_framework.permissions import IsAuthenticated, AllowAny
# from rest_framework.throttling import AnonRateThrottle
# from drf_spectacular.utils import extend_schema
# from .models import UserProfile, OTP
# from .serializers import (
#     LoginSerializer, RegisterSerializer, OTPSerializer,
#     UserProfileSerializer, TokenSerializer, LogoutSerializer
# )
# from cart.models import Cart
# import logging

# logger = logging.getLogger(__name__)

# def merge_carts(user, session_key):
#     guest_carts = Cart.objects.filter(session_key=session_key)
#     for guest_cart in guest_carts:
#         user_cart, created = Cart.objects.get_or_create(
#             user=user,
#             product=guest_cart.product,
#             defaults={'quantity': guest_cart.quantity}
#         )
#         if not created:
#             user_cart.quantity += guest_cart.quantity
#             user_cart.save()
#     guest_carts.delete()

# class LoginAPIView(APIView):
#     permission_classes = [AllowAny]
#     throttle_classes = [AnonRateThrottle]

#     @extend_schema(
#         request=LoginSerializer,
#         responses={status.HTTP_200_OK: TokenSerializer},
#         description="Аутентифікація користувача та генерація OTP"
#     )
#     def post(self, request):
#         serializer = LoginSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         username = serializer.validated_data['username']
#         password = serializer.validated_data['password']
#         user = authenticate(request, username=username, password=password)
#         if user:
#             otp_code = ''.join(random.choices('0123456789', k=6))
#             OTP.objects.create(
#                 user=user,
#                 code=otp_code,
#                 expires_at=timezone.now() + timedelta(minutes=5)
#             )
#             logger.info(f"OTP for {username}: {otp_code}")  # Замінити на email/SMS у продакшені
#             request.session['otp_user_id'] = user.id
#             return Response({
#                 'status': 'otp_sent',
#                 'message': 'OTP sent to your phone/email',
#                 'otp_user_id': user.id
#             }, status=status.HTTP_200_OK)
#         return Response({
#             'status': 'error',
#             'message': 'Invalid credentials'
#         }, status=status.HTTP_400_BAD_REQUEST)

# class VerifyOTPAPIView(APIView):
#     permission_classes = [AllowAny]
#     throttle_classes = [AnonRateThrottle]

#     @extend_schema(
#         request=OTPSerializer,
#         responses={status.HTTP_200_OK: TokenSerializer},
#         description="Верифікація OTP та видача токена"
#     )
#     def post(self, request):
#         serializer = OTPSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         otp_code = serializer.validated_data['otp_code']
#         user_id = serializer.validated_data.get('otp_user_id') or request.session.get('otp_user_id')
#         if not user_id:
#             return Response({
#                 'status': 'error',
#                 'message': 'Invalid session'
#             }, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             user = User.objects.get(id=user_id)
#         except User.DoesNotExist:
#             return Response({
#                 'status': 'error',
#                 'message': 'User not found'
#             }, status=status.HTTP_400_BAD_REQUEST)

#         otp = OTP.objects.filter(
#             user=user,
#             code=otp_code,
#             expires_at__gte=timezone.now()
#         ).first()
#         if otp:
#             login(request, user)
#             otp.delete()
#             merge_carts(user, request.session.session_key)
#             token, created = Token.objects.get_or_create(user=user)
#             if 'otp_user_id' in request.session:
#                 del request.session['otp_user_id']
#             return Response({
#                 'status': 'success',
#                 'message': f'Welcome, {user.username}!',
#                 'token': token.key,
#                 'user_id': user.pk,
#                 'username': user.username
#             }, status=status.HTTP_200_OK)
#         return Response({
#             'status': 'error',
#             'message': 'Invalid or expired OTP'
#         }, status=status.HTTP_400_BAD_REQUEST)

# class RegisterAPIView(APIView):
#     permission_classes = [AllowAny]
#     throttle_classes = [AnonRateThrottle]

#     @extend_schema(
#         request=RegisterSerializer,
#         responses={201: TokenSerializer},
#         description="Реєстрація нового користувача"
#     )
#     def post(self, request):
#         serializer = RegisterSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         user = serializer.save()
#         login(request, user)
#         token, created = Token.objects.get_or_create(user=user)
#         return Response({
#             'status': 'success',
#             'message': 'Registration successful',
#             'token': token.key,
#             'user_id': user.pk,
#             'username': user.username
#         }, status=status.HTTP_201_CREATED)

# class ProfileAPIView(APIView):
#     permission_classes = [IsAuthenticated]

#     @extend_schema(
#         request=UserProfileSerializer,
#         responses={status.HTTP_200_OK: UserProfileSerializer},
#         description="Отримання або оновлення профілю користувача"
#     )
#     def get(self, request):
#         try:
#             profile = request.user.profile
#         except UserProfile.DoesNotExist:
#             profile = UserProfile.objects.create(user=request.user)
#         serializer = UserProfileSerializer(profile)
#         return Response(serializer.data, status=status.HTTP_200_OK)

#     @extend_schema(
#         request=UserProfileSerializer,
#         responses={status.HTTP_200_OK: UserProfileSerializer}
#     )
#     def post(self, request):
#         try:
#             profile = request.user.profile
#         except UserProfile.DoesNotExist:
#             profile = UserProfile.objects.create(user=request.user)
#         serializer = UserProfileSerializer(profile, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response({
#                 'status': 'success',
#                 'message': 'Profile updated',
#                 'data': serializer.data
#             }, status=status.HTTP_200_OK)
#         return Response({
#             'status': 'error',
#             'message': 'Invalid profile data',
#             'errors': serializer.errors
#         }, status=status.HTTP_400_BAD_REQUEST)

# class LogoutAPIView(APIView):
#     permission_classes = [IsAuthenticated]

#     @extend_schema(
#         request=None,
#         responses={status.HTTP_200_OK: LogoutSerializer},
#         description="Вихід користувача та видалення токена"
#     )
#     def post(self, request):
#         try:
#             request.user.auth_token.delete()
#         except (AttributeError, Token.DoesNotExist):
#             pass
#         return Response({
#             'status': 'success',
#             'message': 'Successfully logged out'
#         }, status=status.HTTP_200_OK)
# #
# 0 import random
# from django.contrib.auth import authenticate, login
# from django.contrib.auth.models import User
# from django.utils import timezone
# from datetime import timedelta
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from rest_framework.authtoken.models import Token
# from rest_framework.permissions import IsAuthenticated, AllowAny
# from rest_framework.throttling import AnonRateThrottle
# from drf_spectacular.utils import extend_schema
# from .models import UserProfile, OTP
# from .serializers import (
#     LoginSerializer, RegisterSerializer, OTPSerializer,
#     UserProfileSerializer, TokenSerializer
# )
# from cart.models import Cart
# import logging

# logger = logging.getLogger(__name__)

# def merge_carts(user, session_key):
#     guest_carts = Cart.objects.filter(session_key=session_key)
#     for guest_cart in guest_carts:
#         user_cart, created = Cart.objects.get_or_create(
#             user=user,
#             product=guest_cart.product,
#             defaults={'quantity': guest_cart.quantity}
#         )
#         if not created:
#             user_cart.quantity += guest_cart.quantity
#             user_cart.save()
#     guest_carts.delete()

# class LoginAPIView(APIView):
#     permission_classes = [AllowAny]
#     throttle_classes = [AnonRateThrottle]

#     @extend_schema(
#         request=LoginSerializer,
#         responses={status.HTTP_200_OK: TokenSerializer},
#         description="Аутентифікація користувача та генерація OTP"
#     )
#     def post(self, request):
#         serializer = LoginSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         username = serializer.validated_data['username']
#         password = serializer.validated_data['password']
#         user = authenticate(request, username=username, password=password)
#         if user:
#             otp_code = ''.join(random.choices('0123456789', k=6))
#             OTP.objects.create(
#                 user=user,
#                 code=otp_code,
#                 expires_at=timezone.now() + timedelta(minutes=5)
#             )
#             logger.info(f"OTP for {username}: {otp_code}")  # Замінити на email/SMS у продакшені
#             request.session['otp_user_id'] = user.id
#             return Response({
#                 'status': 'otp_sent',
#                 'message': 'OTP sent to your phone/email',
#                 'otp_user_id': user.id
#             }, status=status.HTTP_200_OK)
#         return Response({
#             'status': 'error',
#             'message': 'Invalid credentials'
#         }, status=status.HTTP_400_BAD_REQUEST)

# class VerifyOTPAPIView(APIView):
#     permission_classes = [AllowAny]
#     throttle_classes = [AnonRateThrottle]

#     @extend_schema(
#         request=OTPSerializer,
#         responses={status.HTTP_200_OK: TokenSerializer},
#         description="Верифікація OTP та видача токена"
#     )
#     def post(self, request):
#         serializer = OTPSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         otp_code = serializer.validated_data['otp_code']
#         user_id = serializer.validated_data.get('otp_user_id') or request.session.get('otp_user_id')
#         if not user_id:
#             return Response({
#                 'status': 'error',
#                 'message': 'Invalid session'
#             }, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             user = User.objects.get(id=user_id)
#         except User.DoesNotExist:
#             return Response({
#                 'status': 'error',
#                 'message': 'User not found'
#             }, status=status.HTTP_400_BAD_REQUEST)

#         otp = OTP.objects.filter(
#             user=user,
#             code=otp_code,
#             expires_at__gte=timezone.now()
#         ).first()
#         if otp:
#             login(request, user)
#             otp.delete()
#             merge_carts(user, request.session.session_key)
#             token, created = Token.objects.get_or_create(user=user)
#             if 'otp_user_id' in request.session:
#                 del request.session['otp_user_id']
#             return Response({
#                 'status': 'success',
#                 'message': f'Welcome, {user.username}!',
#                 'token': token.key,
#                 'user_id': user.pk,
#                 'username': user.username
#             }, status=status.HTTP_200_OK)
#         return Response({
#             'status': 'error',
#             'message': 'Invalid or expired OTP'
#         }, status=status.HTTP_400_BAD_REQUEST)

# class RegisterAPIView(APIView):
#     permission_classes = [AllowAny]
#     throttle_classes = [AnonRateThrottle]

#     @extend_schema(
#         request=RegisterSerializer,
#         responses={201: TokenSerializer},
#         description="Реєстрація нового користувача"
#     )
#     def post(self, request):
#         serializer = RegisterSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         user = serializer.save()
#         login(request, user)
#         token, created = Token.objects.get_or_create(user=user)
#         return Response({
#             'status': 'success',
#             'message': 'Registration successful',
#             'token': token.key,
#             'user_id': user.pk,
#             'username': user.username
#         }, status=status.HTTP_201_CREATED)

# class ProfileAPIView(APIView):
#     permission_classes = [IsAuthenticated]

#     @extend_schema(
#         request=UserProfileSerializer,
#         responses={status.HTTP_200_OK: UserProfileSerializer},
#         description="Отримання або оновлення профілю користувача"
#     )
#     def get(self, request):
#         try:
#             profile = request.user.profile
#         except UserProfile.DoesNotExist:
#             profile = UserProfile.objects.create(user=request.user)
#         serializer = UserProfileSerializer(profile)
#         return Response(serializer.data, status=status.HTTP_200_OK)

#     @extend_schema(
#         request=UserProfileSerializer,
#         responses={status.HTTP_200_OK: UserProfileSerializer}
#     )
#     def post(self, request):
#         try:
#             profile = request.user.profile
#         except UserProfile.DoesNotExist:
#             profile = UserProfile.objects.create(user=request.user)
#         serializer = UserProfileSerializer(profile, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response({
#                 'status': 'success',
#                 'message': 'Profile updated',
#                 'data': serializer.data
#             }, status=status.HTTP_200_OK)
#         return Response({
#             'status': 'error',
#             'message': 'Invalid profile data',
#             'errors': serializer.errors
#         }, status=status.HTTP_400_BAD_REQUEST)

# class LogoutAPIView(APIView):

#     permission_classes = [IsAuthenticated]

#     @extend_schema(
#         responses={status.HTTP_200_OK: None},
#         description="Вихід користувача та видалення токена"
#     )
#     def post(self, request):
#         try:
#             request.user.auth_token.delete()
#         except (AttributeError, Token.DoesNotExist):
#             pass
#         return Response({
#             'status': 'success',
#             'message': 'Successfully logged out'
#         }, status=status.HTTP_200_OK)
# # import random
# from django.contrib.auth import authenticate, login
# from django.contrib.auth.models import User
# from django.utils import timezone
# from datetime import timedelta
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from rest_framework.authtoken.models import Token
# from rest_framework.permissions import IsAuthenticated, AllowAny
# from rest_framework.decorators import permission_classes
# from drf_spectacular.utils import extend_schema
# from .models import UserProfile, OTP
# from .serializers import (
#     LoginSerializer, RegisterSerializer, OTPSerializer,
#     UserProfileSerializer, TokenSerializer
# )
# from cart.models import Cart
# import logging
# from ratelimit.decorators import ratelimit

# logger = logging.getLogger(__name__)

# def merge_carts(user, session_key):
#     guest_carts = Cart.objects.filter(session_key=session_key)
#     for guest_cart in guest_carts:
#         user_cart, created = Cart.objects.get_or_create(
#             user=user,
#             product=guest_cart.product,
#             defaults={'quantity': guest_cart.quantity}
#         )
#         if not created:
#             user_cart.quantity += guest_cart.quantity
#             user_cart.save()
#     guest_carts.delete()


# class LoginAPIView(APIView):
#     permission_classes = [AllowAny]

#     # @extend_schema(
#     #     request=LoginSerializer,
#     #     responses={status.HTTP_200_OK: TokenSerializer},
#     #     description="Аутентифікація користувача та генерація OTP"
#     # )
#     @ratelimit(key='ip', rate='5/m', method='POST')
#     def post(self, request):
#         serializer = LoginSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         username = serializer.validated_data['username']
#         password = serializer.validated_data['password']
#         user = authenticate(request, username=username, password=password)
#         if user:
#             otp_code = ''.join(random.choices('0123456789', k=6))
#             OTP.objects.create(
#                 user=user,
#                 code=otp_code,
#                 expires_at=timezone.now() + timedelta(minutes=5)
#             )
#             logger.info(f"OTP for {username}: {otp_code}")  # Замінити на email/SMS у продакшені
#             request.session['otp_user_id'] = user.id
#             return Response({
#                 'status': 'otp_sent',
#                 'message': 'OTP sent to your phone/email',
#                 'otp_user_id': user.id
#             }, status=status.HTTP_200_OK)
#         return Response({
#             'status': 'error',
#             'message': 'Invalid credentials'
#         }, status=status.HTTP_400_BAD_REQUEST)

# class VerifyOTPAPIView(APIView):
#     permission_classes = [AllowAny]

#     @extend_schema(
#         request=OTPSerializer,
#         responses={status.HTTP_200_OK: TokenSerializer},
#         description="Верифікація OTP та видача токена"
#     )
#     def post(self, request):
#         serializer = OTPSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         otp_code = serializer.validated_data['otp_code']
#         user_id = serializer.validated_data.get('otp_user_id') or request.session.get('otp_user_id')
#         if not user_id:
#             return Response({
#                 'status': 'error',
#                 'message': 'Invalid session'
#             }, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             user = User.objects.get(id=user_id)
#         except User.DoesNotExist:
#             return Response({
#                 'status': 'error',
#                 'message': 'User not found'
#             }, status=status.HTTP_400_BAD_REQUEST)

#         otp = OTP.objects.filter(
#             user=user,
#             code=otp_code,
#             expires_at__gte=timezone.now()
#         ).first()
#         if otp:
#             login(request, user)
#             otp.delete()
#             merge_carts(user, request.session.session_key)
#             token, created = Token.objects.get_or_create(user=user)
#             if 'otp_user_id' in request.session:
#                 del request.session['otp_user_id']
#             return Response({
#                 'status': 'success',
#                 'message': f'Welcome, {user.username}!',
#                 'token': token.key,
#                 'user_id': user.pk,
#                 'username': user.username
#             }, status=status.HTTP_200_OK)
#         return Response({
#             'status': 'error',
#             'message': 'Invalid or expired OTP'
#         }, status=status.HTTP_400_BAD_REQUEST)

# class RegisterAPIView(APIView):
#     permission_classes = [AllowAny]

#     @extend_schema(
#         request=RegisterSerializer,
#         responses={201: TokenSerializer},
#         description="Реєстрація нового користувача"
#     )
#     def post(self, request):
#         serializer = RegisterSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         user = serializer.save()
#         login(request, user)
#         token, created = Token.objects.get_or_create(user=user)
#         return Response({
#             'status': 'success',
#             'message': 'Registration successful',
#             'token': token.key,
#             'user_id': user.pk,
#             'username': user.username
#         }, status=status.HTTP_201_CREATED)

# class ProfileAPIView(APIView):
#     permission_classes = [IsAuthenticated]

#     @extend_schema(
#         request=UserProfileSerializer,
#         responses={status.HTTP_200_OK: UserProfileSerializer},
#         description="Отримання або оновлення профілю користувача"
#     )
#     def get(self, request):
#         try:
#             profile = request.user.profile
#         except UserProfile.DoesNotExist:
#             profile = UserProfile.objects.create(user=request.user)
#         serializer = UserProfileSerializer(profile)
#         return Response(serializer.data, status=status.HTTP_200_OK)

#     @extend_schema(
#         request=UserProfileSerializer,
#         responses={status.HTTP_200_OK: UserProfileSerializer}
#     )
#     def post(self, request):
#         try:
#             profile = request.user.profile
#         except UserProfile.DoesNotExist:
#             profile = UserProfile.objects.create(user=request.user)
#         serializer = UserProfileSerializer(profile, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response({
#                               'status': 'success',
#                 'message': 'Profile updated',
#                 'data': serializer.data
#             }, status=status.HTTP_200_OK)
#         return Response({
#             'status': 'error',
#             'message': 'Invalid profile data',
#             'errors': serializer.errors
#         }, status=status.HTTP_400_BAD_REQUEST)

# class LogoutAPIView(APIView):
#     permission_classes = [IsAuthenticated]

#     @extend_schema(
#         responses={status.HTTP_200_OK: None},
#         description="Вихід користувача та видалення токена"
#     )
#     def post(self, request):
#         try:
#             request.user.auth_token.delete()
#         except (AttributeError, Token.DoesNotExist):
#             pass
#         return Response({
#             'status': 'success',
#             'message': 'Successfully logged out'
#         }, status=status.HTTP_200_OK)

# # users/views.py
# import random
# from django.shortcuts import render, redirect
# from django.contrib.auth import authenticate, login, logout
# from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
# from django.contrib import messages
# from django.contrib.auth.decorators import login_required
# from django.utils import timezone
# from datetime import timedelta
# from .models import UserProfile, OTP
# from .forms import UserProfileForm
# from rest_framework.authtoken.models import Token
# from rest_framework.authtoken.views import ObtainAuthToken
# from rest_framework.response import Response
# from cart.models import Cart

# def merge_carts(user, session_key):
#     guest_carts = Cart.objects.filter(session_key=session_key)
#     for guest_cart in guest_carts:
#         user_cart, created = Cart.objects.get_or_create(
#             user=user,
#             product=guest_cart.product,
#             defaults={'quantity': guest_cart.quantity}
#         )
#         if not created:
#             user_cart.quantity += guest_cart.quantity
#             user_cart.save()
#     guest_carts.delete()

# def login_view(request):
#     if request.method == 'POST':
#         form = AuthenticationForm(request, data=request.POST)
#         if form.is_valid():
#             username = form.cleaned_data.get('username')
#             password = form.cleaned_data.get('password')
#             user = authenticate(request, username=username, password=password)
#             if user is not None:
#                 otp_code = ''.join(random.choices('0123456789', k=6))
#                 OTP.objects.create(
#                     user=user,
#                     code=otp_code,
#                     expires_at=timezone.now() + timedelta(minutes=5)
#                 )
#                 print(f"OTP for {username}: {otp_code}")  # Замінити на email у продакшені
#                 request.session['otp_user_id'] = user.id
#                 return redirect('verify_otp')
#             else:
#                 messages.error(request, 'Невірний логін або пароль.')
#         else:
#             messages.error(request, 'Невірний логін або пароль.')
#     else:
#         form = AuthenticationForm()
#     return render(request, 'users/login.html', {'form': form})

# def register_view(request):
#     if request.method == 'POST':
#         form = UserCreationForm(request.POST)
#         if form.is_valid():
#             user = form.save()
#             login(request, user)
#             messages.success(request, 'Реєстрація успішна! Заповніть профіль.')
#             return redirect('profile')
#         else:
#             messages.error(request, 'Помилка реєстрації. Перевірте форму.')
#     else:
#         form = UserCreationForm()
#     return render(request, 'users/register.html', {'form': form})

# def verify_otp(request):
#     if request.method == 'POST':
#         otp_code = request.POST.get('otp_code')
#         user_id = request.session.get('otp_user_id')
#         if user_id:
#             user = User.objects.get(id=user_id)
#             otp = OTP.objects.filter(
#                 user=user,
#                 code=otp_code,
#                 expires_at__gte=timezone.now()
#             ).first()
#             if otp:
#                 login(request, user)
#                 otp.delete()
#                 merge_carts(user, request.session.session_key)
#                 messages.success(request, f'Вітаємо, {user.username}!')
#                 del request.session['otp_user_id']
#                 return redirect('profile')
#             else:
#                 messages.error(request, 'Невірний або прострочений OTP.')
#         else:
#             messages.error(request, 'Сесія недійсна. Спробуйте увійти знову.')
#     return render(request, 'users/verify_otp.html')

# def logout_view(request):
#     logout(request)
#     messages.success(request, 'Ви вийшли з системи.')
#     return redirect('login')

# @login_required
# def profile_view(request):
#     try:
#         profile = request.user.profile
#     except UserProfile.DoesNotExist:
#         profile = UserProfile.objects.create(user=request.user)

#     if request.method == 'POST':
#         form = UserProfileForm(request.POST, instance=profile)
#         if form.is_valid():
#             form.save()
#             messages.success(request, 'Профіль оновлено!')
#             return redirect('checkout')
#         else:
#             messages.error(request, 'Помилка оновлення профілю.')
#     else:
#         form = UserProfileForm(instance=profile)
#     return render(request, 'users/profile.html', {'form': form})

# class CustomAuthToken(ObtainAuthToken):
#     def post(self, request, *args, **kwargs):
#         serializer = self.serializer_class(data=request.data, context={'request': request})
#         serializer.is_valid(raise_exception=True)
#         user = serializer.validated_data['user']
#         token, created = Token.objects.get_or_create(user=user)
#         return Response({
#             'token': token.key,
#             'user_id': user.pk,
#             'username': user.username
#         })
