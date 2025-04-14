from django.contrib import admin
from django.contrib.auth import get_user_model

from utils.multi_backend_image_field import MultiBackendImageWidget
from .models import UserProfile
from discounts.models import (
    PersonalDiscount, BirthdayDiscount,
    Coupon, BonusAccount
)
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




@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "phone", "birthday")
    inlines = [
        PersonalDiscountInline,
        BirthdayDiscountInline,
        CouponInline,
        BonusAccountInline,
    ]
    # exclude = ("user",)  # Ховаємо поле user

    # def get_form(self, request, obj=None, **kwargs):
    #     form = super().get_form(request, obj, **kwargs)
    #     # Specify custom form for the 'avatar' field
    #     form.base_fields["avatar"].widget = MultiBackendImageWidget()
    #     return form

    def save_model(self, request, obj, form, change):
        if not obj.user_id:
            obj.user = User.objects.get(
                pk=request.user.pk
            )  # Отримуємо реальний User-об'єкт
        super().save_model(request, obj, form, change)
