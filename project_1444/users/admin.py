from django.contrib import admin
from django.contrib.auth import get_user_model
from .models import UserProfile

User = get_user_model()

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "phone", "birthday")
    # exclude = ("user",)  # Ховаємо поле user

    def save_model(self, request, obj, form, change):
        if not obj.user_id:
            obj.user = User.objects.get(pk=request.user.pk)  # Отримуємо реальний User-об'єкт
        super().save_model(request, obj, form, change)
