from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist
from .models import OTP, User
from .serializers import OTPRequestSerializer, OTPVerifySerializer
from .utils import send_otp_via_email

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist
from .models import OTP, User
from .serializers import OTPRequestSerializer, OTPVerifySerializer
from .utils import send_otp_via_email, send_otp_via_sms, send_otp_via_telegram

class OTPRequestView(APIView):
    def post(self, request):
        serializer = OTPRequestSerializer(data=request.data)
        if serializer.is_valid():
            contact = serializer.validated_data['contact']
            user, created = User.objects.get_or_create(
                email=contact if '@' in contact else None,
                phone=contact if contact.isdigit() else None,
                telegram=contact if contact.startswith('@') else None
                    )

            if created:
                # Наприклад, логувати створення нового користувача
                print(f"Створено нового користувача: {user}")
            # user, created = User.objects.get_or_create(
            #     email=contact if '@' in contact else None,
            #     phone=contact if contact.isdigit() else None,
            #     telegram=contact if contact.startswith('@') else None
            # )
            otp = OTP.objects.create(user=user)

            # Визначаємо спосіб відправки OTP
            if user.email:
                send_otp_via_email(user.email, otp.code)
            elif user.phone:
                send_otp_via_sms(user.phone, otp.code)
            elif user.telegram:
                send_otp_via_telegram(user.telegram, otp.code)

            return Response({"message": "OTP відправлено!"})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# class OTPRequestView(APIView):
#     def post(self, request):
#         serializer = OTPRequestSerializer(data=request.data)
#         if serializer.is_valid():
#             contact = serializer.validated_data['contact']
#             user, created = User.objects.get_or_create(
#                 email=contact if '@' in contact else None,
#                 phone=contact if contact.isdigit() else None,
#                 telegram=contact if contact.startswith('@') else None
#             )
#             otp = OTP.objects.create(user=user)
#             return Response({"message": "OTP sent", "code": otp.code})
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class OTPVerifyView(APIView):
    def post(self, request):
        serializer = OTPVerifySerializer(data=request.data)
        if serializer.is_valid():
            contact = serializer.validated_data['contact']
            code = serializer.validated_data['code']
            try:
                user = User.objects.get(
                    email=contact if '@' in contact else None,
                    phone=contact if contact.isdigit() else None,
                    telegram=contact if contact.startswith('@') else None
                )
                otp = OTP.objects.filter(user=user, code=code).first()
                if otp:
                    tokens = user.get_tokens()
                    otp.delete()
                    return Response(tokens)
                return Response({"error": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)
            except ObjectDoesNotExist:
                return Response({"error": "User not found"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
