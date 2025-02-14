from rest_framework import serializers

class OTPRequestSerializer(serializers.Serializer):
    contact = serializers.CharField()

class OTPVerifySerializer(serializers.Serializer):
    contact = serializers.CharField()
    code = serializers.CharField(max_length=6)