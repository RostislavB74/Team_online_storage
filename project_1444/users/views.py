from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist
from .models import User
from .serializers import OTPRequestSerializer, OTPVerifySerializer
from .utils import send_otp_via_email, send_otp_via_sms, send_otp_via_telegram
from rest_framework import generics, permissions
from django.contrib.auth import get_user_model

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
