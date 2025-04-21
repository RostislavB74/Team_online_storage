from django.contrib import admin
from django.contrib.auth import get_user_model

from utils.multi_backend_image_field import MultiBackendImageWidget
# from .models import UserProfile
from discounts.models import (
    PersonalDiscount, BirthdayDiscount,
    Coupon, BonusAccount
)
from django.contrib import admin
from .models import UserProfile, OTP, UserNotificationSettings, UserAddress
from django import forms
import json

User = get_user_model()





class PersonalDiscountInline(admin.TabularInline):
    model = PersonalDiscount
    extra = 0
    autocomplete_fields = ['assigned_by']
    verbose_name = 'Персональна знижка'
    verbose_name_plural = 'Персональні знижки'


class BirthdayDiscountInline(admin.TabularInline):
    model = BirthdayDiscount
    extra = 0
    verbose_name = 'Знижка до Дня народження'
    verbose_name_plural = 'Знижки до Дня народження'


class CouponInline(admin.TabularInline):
    model = Coupon
    extra = 0
    verbose_name = 'Купон'
    verbose_name_plural = 'Купони'


class BonusAccountInline(admin.StackedInline):
    model = BonusAccount
    extra = 0
    verbose_name = 'Бонусний рахунок'
    verbose_name_plural = 'Бонусний рахунок'
    readonly_fields = ('balance',)

# users/admin.py


# class UserProfileAdminForm(forms.ModelForm):
#     messengers = forms.CharField(widget=forms.Textarea, required=False)

#     class Meta:
#         model = UserProfile
#         fields = '__all__'

#     def clean_messengers(self):
#         data = self.cleaned_data['messengers']
#         if data:
#             try:
#                 json_data = json.loads(data)
#                 if not isinstance(json_data, dict):
#                     raise forms.ValidationError("Messengers must be a JSON dictionary")
#                 return json_data
#             except json.JSONDecodeError:
#                 raise forms.ValidationError("Invalid JSON format")
#         return {}

# #     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         if self.instance and self.instance.messengers:
#             self.initial['messengers'] = json.dumps(self.instance.messengers, indent=2)


# @admin.register(UserProfile)


class UserProfileAdminForm(forms.ModelForm):
    viber = forms.CharField(max_length=50, required=False, label="Viber")
    telegram = forms.CharField(max_length=50, required=False, label="Telegram")
    whatsapp = forms.CharField(max_length=50, required=False, label="WhatsApp")
    signal = forms.CharField(max_length=50, required=False, label="Signal")

    class Meta:
        model = UserProfile
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance._messengers:
            messengers = self.instance.get_messengers_for_admin()
            self.initial['viber'] = messengers.get('viber', '')
            self.initial['telegram'] = messengers.get('telegram', '')
            self.initial['whatsapp'] = messengers.get('whatsapp', '')
            self.initial['signal'] = messengers.get('signal', '')

    def clean(self):
        cleaned_data = super().clean()
        messengers = {
            'viber': cleaned_data.get('viber', ''),
            'telegram': cleaned_data.get('telegram', ''),
            'whatsapp': cleaned_data.get('whatsapp', ''),
            'signal': cleaned_data.get('signal', '')
        }
        # Видаляємо порожні значення
        cleaned_data['messengers'] = {k: v for k, v in messengers.items() if v}
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance._messengers = self.cleaned_data['messengers']
        if commit:
            instance.save()
        return instance

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    form = UserProfileAdminForm
    list_display = ('user', 'gender', 'get_messengers_display')
    search_fields = ('user__username', 'messengers__viber', 'messengers__telegram')
    fields = (
        'user', 'gender', 'viber', 'telegram', 'whatsapp', 'signal',
        'phone', 'avatar', 'birthday', 'partner_name', 'partner_birthday',
        'address', 'wedding_date', 'ocassions_personal', 'ocassions_date'
    )

    def get_messengers_display(self, obj):
        return json.dumps(obj.get_messengers_for_admin(), indent=2, ensure_ascii=False)
    get_messengers_display.short_description = 'Messengers'

@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display = ('user', 'code', 'created_at', 'expires_at')
    search_fields = ('user__username', 'code')

@admin.register(UserNotificationSettings)
class UserNotificationSettingsAdmin(admin.ModelAdmin):
    list_display = ('user', 'email_notifications', 'sms_notifications', 'viber_notifications')
    search_fields = ('user__username',)

@admin.register(UserAddress)
class UserAddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'delivery_type', 'city', 'is_default')
    search_fields = ('user__username', 'city')
# @admin.register(UserProfile)
# class UserProfileAdmin(admin.ModelAdmin):
#     form = UserProfileAdminForm
#     list_display = ('user', 'gender', 'messengers')
#     search_fields = ('user__username', 'messengers__viber', 'messengers__telegram')

# @admin.register(OTP)
# class OTPAdmin(admin.ModelAdmin):
#     list_display = ('user', 'code', 'created_at', 'expires_at')
#     search_fields = ('user__username', 'code')

# @admin.register(UserNotificationSettings)
# class UserNotificationSettingsAdmin(admin.ModelAdmin):
#     list_display = ('user', 'email_notifications', 'sms_notifications', 'viber_notifications')
#     search_fields = ('user__username',)

# @admin.register(UserAddress)
# class UserAddressAdmin(admin.ModelAdmin):
#     list_display = ('user', 'delivery_type', 'city', 'is_default')
#     search_fields = ('user__username', 'city')


# @admin.register(UserProfile)
# class UserProfileAdmin(admin.ModelAdmin):
#     list_display = ("id", "user", "phone", "birthday")
#     inlines = [
#         PersonalDiscountInline,
#         BirthdayDiscountInline,
#         CouponInline,
#         BonusAccountInline,
#     ]
#     # exclude = ("user",)  # Ховаємо поле user

#     # def get_form(self, request, obj=None, **kwargs):
#     #     form = super().get_form(request, obj, **kwargs)
#     #     # Specify custom form for the 'avatar' field
#     #     form.base_fields["avatar"].widget = MultiBackendImageWidget()
#     #     return form

#     def save_model(self, request, obj, form, change):
#         if not obj.user_id:
#             obj.user = User.objects.get(
#                 pk=request.user.pk
#             )  # Отримуємо реальний User-об'єкт
#         super().save_model(request, obj, form, change)
