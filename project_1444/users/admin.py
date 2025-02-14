from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from .models import User

class CustomUserAdmin(UserAdmin):
    list_display = ('name', 'email', 'phone', 'telegram', 'is_staff', 'is_active', 'is_superuser', "display_groups")
    search_fields = ('name', 'email', 'phone', 'telegram')
    list_filter = ('is_staff', 'is_active', 'is_superuser', 'groups')

    fieldsets = (
        (None, {'fields': ('name', 'email', 'phone', 'telegram', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('name', 'email', 'phone', 'telegram', 'password1', 'password2', 'is_staff', 'is_active', 'is_superuser', 'groups'),
        }),
    )

    ordering = ('name', 'email',)
    filter_horizontal = ('groups', 'user_permissions')

    def display_groups(self, obj):
        return ", ".join([group.name for group in obj.groups.all()]) if obj.groups.exists() else "Без групи"
    display_groups.short_description = "Groups"

# **Видаляємо попередню реєстрацію, якщо була**
try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass

admin.site.register(User, CustomUserAdmin)

# from django.contrib import admin
# from django.contrib.auth.admin import UserAdmin
# from .models import User  # імпортуй свою модель
# from django.contrib.auth.models import Group

# # @admin.register(User)
# class CustomUserAdmin(UserAdmin):
#     list_display = ('name' ,'email', 'phone', 'telegram', 'is_staff', 'is_active', 'is_superuser', "display_groups")
#     search_fields = ('name','email', 'phone', 'telegram')
#     list_filter = ('is_staff', 'is_active', 'is_superuser')
#     fieldsets = (
#         (None, {'fields': ('email', 'phone', 'telegram', 'password')}),
#         ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser')}),
#     )

#     add_fieldsets = (
#         (None, {
#             'classes': ('wide',),    
#             'fields': ('email', 'phone', 'telegram', 'password1', 'password2', 'is_staff', 'is_active', 'is_superuser'),
#         }),
#     )

#     ordering = ('name','email',)
#     filter_horizontal = ()
#     def display_groups(self, obj):
#         return ", ".join([group.name for group in obj.groups.all()]) if obj.groups.exists() else "Без групи"
#     display_groups.short_description = "Groups"

# admin.site.register(User, CustomUserAdmin)
   
   