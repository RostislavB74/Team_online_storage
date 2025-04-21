from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .models import UserProfile, OTP, UserNotificationSettings
import re

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')
        if username and password:
            user = authenticate(
                request=self.context.get('request'),
                username=username,
                password=password
            )
            if not user:
                raise serializers.ValidationError('Invalid credentials')
        else:
            raise serializers.ValidationError('Must include username and password')
        data['user'] = user
        return data

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm']

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({'password': 'Passwords must match'})
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError({'email': 'Email already exists'})
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user

class OTPSerializer(serializers.Serializer):
    otp_code = serializers.CharField(max_length=6, min_length=6)
    otp_user_id = serializers.IntegerField(required=False)

class UserProfileSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.username', read_only=True)
    avatar = serializers.ImageField(allow_null=True, required=False)
    messengers = serializers.JSONField(default=dict, source='get_messengers_for_admin')

    class Meta:
        model = UserProfile
        fields = ["id", "user", "gender", "messengers", "avatar"]

    def validate_messengers(self, value):
        if not isinstance(value, dict):
            raise serializers.ValidationError("Messengers must be a dictionary")
        
        allowed_messengers = {'viber', 'telegram', 'whatsapp', 'signal'}
        
        for key in value:
            if key not in allowed_messengers:
                raise serializers.ValidationError(f"Unsupported messenger: {key}")
            
            if key in {'viber', 'whatsapp'} and value[key]:
                if not re.match(r'^\+?\d{10,15}$', value[key]):
                    raise serializers.ValidationError(f"Invalid {key} format. Must be a phone number (e.g., +380123456789)")
            
            if key == 'telegram' and value[key]:
                if not value[key].startswith('@'):
                    raise serializers.ValidationError("Telegram ID must start with @")
            
            if key == 'signal' and value[key] == '':
                raise serializers.ValidationError("Signal ID cannot be empty")

        return value

    def validate_user(self, value):
        request = self.context.get("request")
        if request and not request.user.is_staff:
            raise serializers.ValidationError("Ви не можете змінювати це поле.")
        return value

    def validate_avatar(self, value):
        if value and value.size > 2 * 1024 * 1024:
            raise serializers.ValidationError("Image size must be under 2MB.")
        return value

class UserNotificationSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserNotificationSettings
        fields = ['email_notifications', 'sms_notifications', 'viber_notifications']

class TokenSerializer(serializers.Serializer):
    token = serializers.CharField()
    user_id = serializers.IntegerField()
    username = serializers.CharField()

class LogoutSerializer(serializers.Serializer):
    status = serializers.CharField()
    message = serializers.CharField()
# from rest_framework import serializers
# from django.contrib.auth.models import User
# from django.contrib.auth import authenticate
# from .models import UserProfile, OTP, UserNotificationSettings

# class LoginSerializer(serializers.Serializer):
#     username = serializers.CharField(max_length=150)
#     password = serializers.CharField(write_only=True)

#     def validate(self, data):
#         username = data.get('username')
#         password = data.get('password')
#         if username and password:
#             user = authenticate(
#                 request=self.context.get('request'),
#                 username=username,
#                 password=password
#             )
#             if not user:
#                 raise serializers.ValidationError('Invalid credentials')
#         else:
#             raise serializers.ValidationError('Must include username and password')
#         data['user'] = user
#         return data

# class RegisterSerializer(serializers.ModelSerializer):
#     password = serializers.CharField(write_only=True, min_length=8)
#     password_confirm = serializers.CharField(write_only=True)
#     email = serializers.EmailField(required=True)

#     class Meta:
#         model = User
#         fields = ['username', 'email', 'password', 'password_confirm']

#     def validate(self, data):
#         if data['password'] != data['password_confirm']:
#             raise serializers.ValidationError({'password': 'Passwords must match'})
#         if User.objects.filter(email=data['email']).exists():
#             raise serializers.ValidationError({'email': 'Email already exists'})
#         return data

#     def create(self, validated_data):
#         validated_data.pop('password_confirm')
#         user = User.objects.create_user(
#             username=validated_data['username'],
#             email=validated_data['email'],
#             password=validated_data['password']
#         )
#         return user

# class OTPSerializer(serializers.Serializer):
#     otp_code = serializers.CharField(max_length=6, min_length=6)
#     otp_user_id = serializers.IntegerField(required=False)

# from rest_framework import serializers
# from django.contrib.auth.models import User
# from django.contrib.auth import authenticate
# from .models import UserProfile, OTP, UserNotificationSettings

# class LoginSerializer(serializers.Serializer):
#     username = serializers.CharField(max_length=150)
#     password = serializers.CharField(write_only=True)

#     def validate(self, data):
#         username = data.get('username')
#         password = data.get('password')
#         if username and password:
#             user = authenticate(
#                 request=self.context.get('request'),
#                 username=username,
#                 password=password
#             )
#             if not user:
#                 raise serializers.ValidationError('Invalid credentials')
#         else:
#             raise serializers.ValidationError('Must include username and password')
#         data['user'] = user
#         return data
# class RegisterSerializer(serializers.ModelSerializer):
#     password = serializers.CharField(write_only=True, min_length=8)
#     password_confirm = serializers.CharField(write_only=True)
#     email = serializers.EmailField(required=True)
#     first_name = serializers.CharField(required=False, allow_blank=True)
#     last_name = serializers.CharField(required=False, allow_blank=True)

#     class Meta:
#         model = User
#         fields = ['username', 'email', 'first_name', 'last_name', 'password', 'password_confirm']

#     def create(self, validated_data):
#         validated_data.pop('password_confirm')
#         user = User.objects.create_user(
#             username=validated_data['username'],
#             email=validated_data['email'],
#             password=validated_data['password'],
#             first_name=validated_data.get('first_name', ''),
#             last_name=validated_data.get('last_name', '')
#         )
#         return user
# class RegisterSerializer(serializers.ModelSerializer):
#     password = serializers.CharField(write_only=True, min_length=8)
#     password_confirm = serializers.CharField(write_only=True)
#     email = serializers.EmailField(required=True)

#     class Meta:
#         model = User
#         fields = ['username', 'email', 'password', 'password_confirm']

#     def validate(self, data):
#         if data['password'] != data['password_confirm']:
#             raise serializers.ValidationError({'password': 'Passwords must match'})
#         if User.objects.filter(email=data['email']).exists():
#             raise serializers.ValidationError({'email': 'Email already exists'})
#         return data

#     def create(self, validated_data):
#         validated_data.pop('password_confirm')
#         user = User.objects.create_user(
#             username=validated_data['username'],
#             email=validated_data['email'],
#             password=validated_data['password']
#         )
#         return user

class OTPSerializer(serializers.Serializer):
    otp_code = serializers.CharField(max_length=6, min_length=6)
    otp_user_id = serializers.IntegerField(required=False)

class UserProfileSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()  # Кастомне поле
    avatar = serializers.ImageField(allow_null=True, required=False)

    class Meta:
        model = UserProfile
        fields = ["id", "user", "gender", "viber", "telegram", "avatar"]

    def get_user(self, obj):
        user = obj.user
        full_name = f"{user.first_name} {user.last_name}".strip()
        return full_name if full_name else user.username

    def validate_user(self, value):
        request = self.context.get("request")
        if request and not request.user.is_staff:
            raise serializers.ValidationError("Ви не можете змінювати це поле.")
        return value

    def validate_avatar(self, value):
        if value and value.size > 2 * 1024 * 1024:
            raise serializers.ValidationError("Image size must be under 2MB.")
        return value
# class UserProfileSerializer(serializers.ModelSerializer):
#     user = serializers.CharField(source='user.username', read_only=True)  # Змінено на CharField
#     avatar = serializers.ImageField(allow_null=True, required=False)

#     class Meta:
#         model = UserProfile
#         fields = ["id", "user", "gender", "viber", "telegram", "avatar"]

#     def validate_user(self, value):
#         request = self.context.get("request")
#         if request and not request.user.is_staff:
#             raise serializers.ValidationError("Ви не можете змінювати це поле.")
#         return value

#     def validate_avatar(self, value):
#         if value and value.size > 2 * 1024 * 1024:
#             raise serializers.ValidationError("Image size must be under 2MB.")
#         return value

class UserNotificationSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserNotificationSettings
        fields = ['email_notifications', 'sms_notifications', 'viber_notifications']

class TokenSerializer(serializers.Serializer):
    token = serializers.CharField()
    user_id = serializers.IntegerField()
    username = serializers.CharField()

class LogoutSerializer(serializers.Serializer):
    status = serializers.CharField()
    message = serializers.CharField()

class UserNotificationSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserNotificationSettings
        fields = ['email_notifications', 'sms_notifications', 'viber_notifications']

class TokenSerializer(serializers.Serializer):
    token = serializers.CharField()
    user_id = serializers.IntegerField()
    username = serializers.CharField()

class LogoutSerializer(serializers.Serializer):
    status = serializers.CharField()
    message = serializers.CharField()
# from rest_framework import serializers
# from django.contrib.auth.models import User
# from django.contrib.auth import authenticate
# from .models import UserProfile, OTP, UserNotificationSettings

# class LoginSerializer(serializers.Serializer):
#     username = serializers.CharField(max_length=150)
#     password = serializers.CharField(write_only=True)

#     def validate(self, data):
#         username = data.get('username')
#         password = data.get('password')
#         if username and password:
#             user = authenticate(
#                 request=self.context.get('request'),
#                 username=username,
#                 password=password
#             )
#             if not user:
#                 raise serializers.ValidationError('Invalid credentials')
#         else:
#             raise serializers.ValidationError('Must include username and password')
#         data['user'] = user
#         return data

# class RegisterSerializer(serializers.ModelSerializer):
#     password = serializers.CharField(write_only=True, min_length=8)
#     password_confirm = serializers.CharField(write_only=True)

#     class Meta:
#         model = User
#         fields = ['username', 'password', 'password_confirm']

#     def validate(self, data):
#         if data['password'] != data['password_confirm']:
#             raise serializers.ValidationError({'password': 'Passwords must match'})
#         return data

#     def create(self, validated_data):
#         validated_data.pop('password_confirm')
#         user = User.objects.create_user(
#             username=validated_data['username'],
#             password=validated_data['password']
#         )
#         return user

# class OTPSerializer(serializers.Serializer):
#     otp_code = serializers.CharField(max_length=6, min_length=6)
#     otp_user_id = serializers.IntegerField(required=False)

# class UserProfileSerializer(serializers.ModelSerializer):
#     user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)

#     class Meta:
#         model = UserProfile
#         fields = ["id", "user", "gender", "viber", "telegram"]

#     def validate_user(self, value):
#         # Якщо юзер не є адміністратором, забороняємо зміну user_id
#         request = self.context.get("request")
#         if request and not request.user.is_staff:
#             raise serializers.ValidationError("Ви не можете змінювати це поле.")
#         return value

# class UserNotificationSettingsSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = UserNotificationSettings
#         fields = ['email_notifications', 'sms_notifications', 'viber_notifications']

# class TokenSerializer(serializers.Serializer):
#     token = serializers.CharField()
#     user_id = serializers.IntegerField()
#     username = serializers.CharField()

# class LogoutSerializer(serializers.Serializer):
#     status = serializers.CharField()
#     message = serializers.CharField()

# from rest_framework import serializers
# from django.contrib.auth.models import User
# from django.contrib.auth import authenticate
# from .models import UserProfile, OTP, UserNotificationSettings

# class LoginSerializer(serializers.Serializer):
#     username = serializers.CharField(max_length=150)
#     password = serializers.CharField(write_only=True)

#     def validate(self, data):
#         username = data.get('username')
#         password = data.get('password')
#         if username and password:
#             user = authenticate(
#                 request=self.context.get('request'),
#                 username=username,
#                 password=password
#             )
#             if not user:
#                 raise serializers.ValidationError('Invalid credentials')
#         else:
#             raise serializers.ValidationError('Must include username and password')
#         data['user'] = user
#         return data

# class RegisterSerializer(serializers.ModelSerializer):
#     password = serializers.CharField(write_only=True, min_length=8)
#     password_confirm = serializers.CharField(write_only=True)

#     class Meta:
#         model = User
#         fields = ['username', 'password', 'password_confirm']

#     def validate(self, data):
#         if data['password'] != data['password_confirm']:
#             raise serializers.ValidationError({'password': 'Passwords must match'})
#         return data

#     def create(self, validated_data):
#         validated_data.pop('password_confirm')
#         user = User.objects.create_user(
#             username=validated_data['username'],
#             password=validated_data['password']
#         )
#         return user

# class OTPSerializer(serializers.Serializer):
#     otp_code = serializers.CharField(max_length=6, min_length=6)
#     otp_user_id = serializers.IntegerField(required=False)

# class UserProfileSerializer(serializers.ModelSerializer):
#     user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)

#     class Meta:
#         model = UserProfile
#         fields = ["id", "user", "gender", "viber", "telegram"]

#     def validate_user(self, value):
#         # Якщо юзер не є адміністратором, забороняємо зміну user_id
#         request = self.context.get("request")
#         if request and not request.user.is_staff:
#             raise serializers.ValidationError("Ви не можете змінювати це поле.")
#         return value
# # class UserProfileSerializer(serializers.ModelSerializer):
# #     class Meta:
# #         model = UserProfile
# #         fields = [
# #             'phone', 'address', 'first_name', 'last_name',
# #             'gender', 'telegram', 'viber', 'avatar', 'birthday',
# #             'partner_name', 'partner_birthday', 'wedding_date',
# #             'ocassions_personal', 'ocassions_date'
# #         ]

# class UserNotificationSettingsSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = UserNotificationSettings
#         fields = ['email_notifications', 'sms_notifications', 'viber_notifications']

# class TokenSerializer(serializers.Serializer):
#     token = serializers.CharField()
#     user_id = serializers.IntegerField()
#     username = serializers.CharField()

# class LogoutSerializer(serializers.Serializer):
#     status = serializers.CharField()
#     message = serializers.CharField()

# from rest_framework import serializers
# from django.contrib.auth.models import User
# from django.contrib.auth import authenticate
# from .models import UserProfile, OTP

# class LoginSerializer(serializers.Serializer):
#     username = serializers.CharField(max_length=150)
#     password = serializers.CharField(write_only=True)

#     def validate(self, data):
#         username = data.get('username')
#         password = data.get('password')
#         if username and password:
#             user = authenticate(
#                 request=self.context.get('request'),
#                 username=username,
#                 password=password
#             )
#             if not user:
#                 raise serializers.ValidationError('Invalid credentials')
#         else:
#             raise serializers.ValidationError('Must include username and password')
#         data['user'] = user
#         return data

# class RegisterSerializer(serializers.ModelSerializer):
#     password = serializers.CharField(write_only=True, min_length=8)
#     password_confirm = serializers.CharField(write_only=True)

#     class Meta:
#         model = User
#         fields = ['username', 'password', 'password_confirm']

#     def validate(self, data):
#         if data['password'] != data['password_confirm']:
#             raise serializers.ValidationError({'password': 'Passwords must match'})
#         return data

#     def create(self, validated_data):
#         validated_data.pop('password_confirm')
#         user = User.objects.create_user(
#             username=validated_data['username'],
#             password=validated_data['password']
#         )
#         return user

# class OTPSerializer(serializers.Serializer):
#     otp_code = serializers.CharField(max_length=6, min_length=6)
#     otp_user_id = serializers.IntegerField(required=False)

# class UserProfileSerializer(serializers.ModelSerializer):
#     user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)

#     class Meta:
#         model = UserProfile
#         fields = ["id", "user", "gender", "viber", "telegram"]

#     def validate_user(self, value):
#         # Якщо юзер не є адміністратором, забороняємо зміну user_id
#         request = self.context.get("request")
#         if request and not request.user.is_staff:
#             raise serializers.ValidationError("Ви не можете змінювати це поле.")
#         return value

# class TokenSerializer(serializers.Serializer):
#     token = serializers.CharField()
#     user_id = serializers.IntegerField()
#     username = serializers.CharField()

# class LogoutSerializer(serializers.Serializer):
#     status = serializers.CharField()
#     message = serializers.CharField()


# from rest_framework import serializers
# from django.contrib.auth.models import User
# from django.contrib.auth import authenticate
# from .models import UserProfile, OTP
# from typing import List  # Для типу List[str]
# from drf_spectacular.utils import extend_schema_field

# class LoginSerializer(serializers.Serializer):
#     username = serializers.CharField(max_length=150)
#     password = serializers.CharField(write_only=True)
#     recaptcha = serializers.CharField()

#     def validate(self, data):
#         from django_recaptcha.fields import ReCaptchaField
#         recaptcha_field = ReCaptchaField()
#         recaptcha_field.clean(data['recaptcha'])


#     def validate(self, data):
#         username = data.get('username')
#         password = data.get('password')
#         if username and password:
#             user = authenticate(
#                 request=self.context.get('request'),
#                 username=username,
#                 password=password
#             )
#             if not user:
#                 raise serializers.ValidationError('Invalid credentials')
#         else:
#             raise serializers.ValidationError('Must include username and password')
#         data['user'] = user
#         return data

# class RegisterSerializer(serializers.ModelSerializer):
#     password = serializers.CharField(write_only=True, min_length=8)
#     password_confirm = serializers.CharField(write_only=True)

#     class Meta:
#         model = User
#         fields = ['username', 'password', 'password_confirm']

#     def validate(self, data):
#         if data['password'] != data['password_confirm']:
#             raise serializers.ValidationError({'password': 'Passwords must match'})
#         return data

#     def create(self, validated_data):
#         validated_data.pop('password_confirm')
#         user = User.objects.create_user(
#             username=validated_data['username'],
#             password=validated_data['password']
#         )
#         return user

# class OTPSerializer(serializers.Serializer):
#     otp_code = serializers.CharField(max_length=6, min_length=6)
#     otp_user_id = serializers.IntegerField(required=False)

# # class UserProfileSerializer(serializers.ModelSerializer):
# #     class Meta:
# #         model = UserProfile
# #         fields = ['phone', 'address', 'first_name', 'last_name']

# 

# class TokenSerializer(serializers.Serializer):
#     token = serializers.CharField()
#     user_id = serializers.IntegerField()
#     username = serializers.CharField()
# from rest_framework import serializers
# from django.contrib.auth.password_validation import validate_password
# from .models import UserAddress, UserProfile, User
# class OTPRequestSerializer(serializers.Serializer):
#     contact = serializers.CharField()

# class OTPVerifySerializer(serializers.Serializer):
#     contact = serializers.CharField()
#     code = serializers.CharField(max_length=6)


# class UserProfileSerializer(serializers.ModelSerializer):
#     user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)

#     class Meta:
#         model = UserProfile
#         fields = ["id", "user", "gender", "viber", "telegram"]

#     def validate_user(self, value):
#         # Якщо юзер не є адміністратором, забороняємо зміну user_id
#         request = self.context.get("request")
#         if request and not request.user.is_staff:
#             raise serializers.ValidationError("Ви не можете змінювати це поле.")
#         return value


# class UserAddressSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = UserAddress
#         fields = ["id", "user", "delivery_type", "city", "street", "postal_code", "nova_poshta_branch", "is_default"]

#     def validate(self, data):
#         """Валідація полів залежно від типу доставки"""
#         delivery_type = data.get("delivery_type")

#         if delivery_type == "home":
#             if not data.get("street") or not data.get("postal_code"):
#                 raise serializers.ValidationError("Для звичайної адреси необхідно вказати вулицю та поштовий індекс.")
        
#         elif delivery_type == "nova_poshta":
#             if not data.get("nova_poshta_branch"):
#                 raise serializers.ValidationError("Для Нової Пошти необхідно вказати номер відділення або поштомату.")
#             data["postal_code"] = "1234"  # Автоматично встановлюємо значення для НП

#         return data



# class ChangePasswordSerializer(serializers.Serializer):
#     old_password = serializers.CharField(required=True)
#     new_password = serializers.CharField(required=True, validators=[validate_password])

# class DeleteAccountSerializer(serializers.Serializer):
#     password = serializers.CharField(required=True)

#     def validate(self, data):
#         user = self.context["request"].user
#         if not user.check_password(data["password"]):
#             raise serializers.ValidationError("Невірний пароль")
#         return data
