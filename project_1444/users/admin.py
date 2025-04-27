from django.contrib import admin
from django.contrib.auth import get_user_model

from utils.multi_backend_image_field import MultiBackendImageWidget
# from .models import UserProfile
from discounts.models import (
    PersonalDiscount, BirthdayDiscount,
    Coupon, BonusAccount
)
from .models import UserProfile, OTP, UserNotificationSettings, UserAddress
from django import forms
import json
import re
from django.conf import settings
from django.template.loader import get_template
from django.utils.translation import gettext_lazy as _
from order.models import Order
from django.template.loader import get_template

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


class MessengerFieldWidget(forms.Widget):
    template_name = 'admin/messenger_field.html'

    def render(self, name, value, attrs=None, renderer=None):
        messengers = value if isinstance(value, dict) else {}
        allowed_messengers = settings.ALLOWED_MESSENGERS
        template = get_template(self.template_name)
        context = {
            'name': name,
            'messengers': messengers,
            'allowed_messengers': allowed_messengers,
        }
        print('Rendering MessengerFieldWidget with context:', context)
        return template.render(context)

class UserProfileAdminForm(forms.ModelForm):
    messengers = forms.JSONField(widget=MessengerFieldWidget, required=False)

    class Meta:
        model = UserProfile
        fields = '__all__'

    def clean_messengers(self):
        messengers = self.cleaned_data.get('messengers', {})
        print('Cleaning messengers:', messengers)
        if not isinstance(messengers, dict):
            raise forms.ValidationError("Messengers must be a dictionary")
        
        allowed_messengers = set(settings.ALLOWED_MESSENGERS)
        for key in messengers:
            if key not in allowed_messengers:
                raise forms.ValidationError(f"Unsupported messenger: {key}")
            
            # Перевірка для viber і whatsapp (тільки номер телефону)
            if key in {'viber', 'whatsapp'} and messengers[key]:
                if not re.match(r'^\+?\d{10,15}$', messengers[key]):
                    raise forms.ValidationError(f"Invalid {key} format. Must be a phone number (e.g., +380123456789)")
            
            # Перевірка для telegram (ID з @ або номер телефону)
            if key == 'telegram' and messengers[key]:
                if not (messengers[key].startswith('@') or re.match(r'^\+?\d{10,15}$', messengers[key])):
                    raise forms.ValidationError("Telegram must start with @ (e.g., @username) or be a phone number (e.g., +380123456789)")
            
            # Перевірка для signal (не може бути порожнім)
            if key == 'signal' and messengers[key] == '':
                raise forms.ValidationError("Signal ID cannot be empty")
        
        return messengers

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and hasattr(self.instance, '_messengers'):
            print('Initializing form with _messengers:', self.instance._messengers)
            self.initial['messengers'] = self.instance._messengers if self.instance._messengers else {}
            if 'messengers' in self.data:
                try:
                    self.initial['messengers'] = json.loads(self.data.get('messengers', '{}'))
                except json.JSONDecodeError:
                    pass
        else:
            self.initial['messengers'] = {}

    def save(self, commit=True):
        instance = super().save(commit=False)
        current_messengers = instance._messengers if instance._messengers else {}
        new_messengers = self.cleaned_data.get('messengers', {})
        current_messengers.update(new_messengers)
        instance._messengers = current_messengers
        print('Saving UserProfile with _messengers:', instance._messengers)
        if commit:
            instance.save()
        return instance
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    form = UserProfileAdminForm
    list_display = ('user', 'gender', 'get_messengers_display', 'get_orders_display')
    search_fields = ('user__username', 'messengers__viber', 'messengers__telegram')
    fields = (
        'user', 'gender', 'messengers',
        'phone', 'avatar', 'birthday', 'partner_name', 'partner_birthday',
        'address', 'wedding_date', 'ocassions_personal', 'ocassions_date'
    )

    def get_messengers_display(self, obj):
        return json.dumps(obj._messengers, indent=2, ensure_ascii=False)
    get_messengers_display.short_description = 'Messengers'

    def get_orders_display(self, obj):
        if not obj.user:  # Перевіряємо, чи є користувач
            return "No user associated"
        orders = obj.user.orders.all()  # Тепер orders доступний завдяки related_name
        if not orders:
            return "No orders"
        return ", ".join([f"Order #{order.id} ({order.status})" for order in orders])
    get_orders_display.short_description = 'Orders'

    class Media:
        js = ('admin/js/messenger_field.js',)
        css = {'all': ('admin/css/messenger_field.css',)}
# @admin.register(UserProfile)
# class UserProfileAdmin(admin.ModelAdmin):
#     form = UserProfileAdminForm
#     list_display = ('user', 'gender', 'get_messengers_display', 'get_orders_display')
#     search_fields = ('user__username', 'messengers__viber', 'messengers__telegram')
#     fields = (
#         'user', 'gender', 'messengers',
#         'phone', 'avatar', 'birthday', 'partner_name', 'partner_birthday',
#         'address', 'wedding_date', 'ocassions_personal', 'ocassions_date'
#     )

#     def get_messengers_display(self, obj):
#         return json.dumps(obj._messengers, indent=2, ensure_ascii=False)
#     get_messengers_display.short_description = 'Messengers'

#     def get_orders_display(self, obj):
#         orders = obj.user.orders.all()
#         return ", ".join([f"Order #{order.id} ({order.status})" for order in orders])
#     get_orders_display.short_description = 'Orders'

#     class Media:
#         js = ('admin/js/messenger_field.js',)
#         css = {'all': ('admin/css/messenger_field.css',)}

# @admin.register(Order)
# class OrderAdmin(admin.ModelAdmin):
#     list_display = ('id', 'user', 'status', 'total_price', 'created_at')
#     list_filter = ('status', 'created_at')
#     search_fields = ('user__username',)
# @admin.register(UserProfile)
# class UserProfileAdmin(admin.ModelAdmin):
#     form = UserProfileAdminForm
#     list_display = ('user', 'gender', 'get_messengers_display')
#     search_fields = ('user__username', 'messengers__viber', 'messengers__telegram')
#     fields = (
#         'user', 'gender', 'messengers',
#         'phone', 'avatar', 'birthday', 'partner_name', 'partner_birthday',
#         'address', 'wedding_date', 'ocassions_personal', 'ocassions_date'
#     )

#     def get_messengers_display(self, obj):
#         return json.dumps(obj._messengers, indent=2, ensure_ascii=False)
#     get_messengers_display.short_description = 'Messengers'

#     class Media:
#         js = ('admin/js/messenger_field.js',)
#         css = {'all': ('admin/css/messenger_field.css',)}

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

