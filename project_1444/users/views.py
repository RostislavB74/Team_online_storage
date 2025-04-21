import random
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.throttling import AnonRateThrottle
from drf_spectacular.utils import extend_schema
from .models import UserProfile, OTP, UserNotificationSettings
from .serializers import (
    LoginSerializer, RegisterSerializer, OTPSerializer,
    UserProfileSerializer, TokenSerializer, LogoutSerializer,
    UserNotificationSettingsSerializer
)
from cart.models import Cart
from django.core.mail import send_mail
import logging

logger = logging.getLogger(__name__)
from django.template.loader import render_to_string

def merge_carts(user, session_key):
    guest_carts = Cart.objects.filter(session_key=session_key)
    for guest_cart in guest_carts:
        user_cart, created = Cart.objects.get_or_create(
            user=user,
            product=guest_cart.product,
            defaults={'quantity': guest_cart.quantity}
        )
        if not created:
            user_cart.quantity += guest_cart.quantity
            user_cart.save()
    guest_carts.delete()

class LoginAPIView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]

    @extend_schema(
        request=LoginSerializer,
        responses={200: TokenSerializer},
        description="Аутентифікація користувача та генерація OTP"
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        user = authenticate(request, username=username, password=password)
        if user:
            if not user.email:
                return Response({
                    'status': 'error',
                    'message': 'Email address is required for OTP verification'
                }, status=status.HTTP_400_BAD_REQUEST)
                
            otp_code = ''.join(random.choices('0123456789', k=6))
            OTP.objects.create(
                user=user,
                code=otp_code,
                expires_at=timezone.now() + timedelta(minutes=5)
            )
            
            # Відправка OTP на email
            try:
                html_message = render_to_string('emails/otp_email.html', {'otp_code': otp_code})
                send_mail(
                    subject='Your OTP Code',
                    message='Your verification code is ' + otp_code,
                    from_email=None,
                    recipient_list=[user.email],
                    html_message=html_message,
                    fail_silently=False,
                )
                # send_mail(
                #     subject='Your OTP Code',
                #     message=f'Your verification code is {otp_code}. It is valid for 5 minutes.',
                #     from_email=None,  # Використовує DEFAULT_FROM_EMAIL
                #     recipient_list=[user.email],
                #     fail_silently=False,
                # )
                logger.info(f"OTP sent to {user.email}: {otp_code}")
            except Exception as e:
                logger.error(f"Failed to send OTP to {user.email}: {str(e)}")
                return Response({
                    'status': 'error',
                    'message': 'Failed to send OTP. Please try again.'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            request.session['otp_user_id'] = user.id
            return Response({
                'status': 'otp_sent',
                'message': 'OTP sent to your email',
                'otp_user_id': user.id
            }, status=status.HTTP_200_OK)
        return Response({
            'status': 'error',
            'message': 'Invalid credentials'
        }, status=status.HTTP_400_BAD_REQUEST)

class VerifyOTPAPIView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]

    @extend_schema(
        request=OTPSerializer,
        responses={200: TokenSerializer},
        description="Верифікація OTP та видача токена"
    )
    def post(self, request):
        serializer = OTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        otp_code = serializer.validated_data['otp_code']
        user_id = serializer.validated_data.get('otp_user_id') or request.session.get('otp_user_id')
        if not user_id:
            return Response({
                'status': 'error',
                'message': 'Invalid session'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({
                'status': 'error',
                'message': 'User not found'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        otp = OTP.objects.filter(
            user=user,
            code=otp_code,
            expires_at__gte=timezone.now()
        ).first()
        if otp:
            login(request, user)
            otp.delete()
            merge_carts(user, request.session.session_key)
            token, created = Token.objects.get_or_create(user=user)
            if 'otp_user_id' in request.session:
                del request.session['otp_user_id']
            return Response({
                'status': 'success',
                'message': f'Welcome, {user.username}!',
                'token': token.key,
                'user_id': user.pk,
                'username': user.username
            }, status=status.HTTP_200_OK)
        return Response({
            'status': 'error',
            'message': 'Invalid or expired OTP'
        }, status=status.HTTP_400_BAD_REQUEST)

class RegisterAPIView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]

    @extend_schema(
        request=RegisterSerializer,
        responses={201: TokenSerializer},
        description="Реєстрація нового користувача"
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        login(request, user)
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'status': 'success',
            'message': 'Registration successful',
            'token': token.key,
            'user_id': user.pk,
            'username': user.username
        }, status=status.HTTP_201_CREATED)

class ProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=UserProfileSerializer,
        responses={200: UserProfileSerializer},
        description="Отримання або оновлення профілю користувача"
    )
    def get(self, request):
        try:
            profile = request.user.profile
        except UserProfile.DoesNotExist:
            profile = UserProfile.objects.create(user=request.user)
        serializer = UserProfileSerializer(profile, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=UserProfileSerializer,
        responses={200: UserProfileSerializer}
    )
    def post(self, request):
        try:
            profile = request.user.profile
        except UserProfile.DoesNotExist:
            profile = UserProfile.objects.create(user=request.user)
        serializer = UserProfileSerializer(profile, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({
                'status': 'success',
                'message': 'Profile updated',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        return Response({
            'status': 'error',
            'message': 'Invalid profile data',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class NotificationSettingsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=UserNotificationSettingsSerializer,
        responses={200: UserNotificationSettingsSerializer},
        description="Отримання або оновлення налаштувань сповіщень"
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
        responses={200: UserNotificationSettingsSerializer}
    )
    def post(self, request):
        try:
            settings = request.user.notifications
        except UserNotificationSettings.DoesNotExist:
            settings = UserNotificationSettings.objects.create(user=request.user)
        serializer = UserNotificationSettingsSerializer(settings, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'status': 'success',
                'message': 'Notification settings updated',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        return Response({
            'status': 'error',
            'message': 'Invalid notification settings',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=None,
        responses={200: LogoutSerializer},
        description="Вихід користувача та видалення токена"
    )
    def post(self, request):
        try:
            request.user.auth_token.delete()
        except (AttributeError, Token.DoesNotExist):
            pass
        return Response({
            'status': 'success',
            'message': 'Successfully logged out'
        }, status=status.HTTP_200_OK)
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
#         responses={200: TokenSerializer},
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
#         responses={200: TokenSerializer},
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
#         responses={200: UserProfileSerializer},
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
#         responses={200: UserProfileSerializer}
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
#         responses={200: UserNotificationSettingsSerializer},
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
#         responses={200: UserNotificationSettingsSerializer}
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
#         responses={200: LogoutSerializer},
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
#         responses={200: TokenSerializer},
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
#         responses={200: TokenSerializer},
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
#         responses={200: UserProfileSerializer},
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
#         responses={200: UserProfileSerializer}
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
#         responses={200: LogoutSerializer},
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
#         responses={200: TokenSerializer},
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
#         responses={200: TokenSerializer},
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
#         responses={200: UserProfileSerializer},
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
#         responses={200: UserProfileSerializer}
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
#         responses={200: None},
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
#     #     responses={200: TokenSerializer},
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
#         responses={200: TokenSerializer},
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
#         responses={200: UserProfileSerializer},
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
#         responses={200: UserProfileSerializer}
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
#         responses={200: None},
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
