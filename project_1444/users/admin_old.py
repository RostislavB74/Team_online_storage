 # readonly_fields = ('email', 'phone', 'telegram')

    # def save_model(self, request, obj, form, change):
    #     if not change:
    #         obj.set_password(obj.password)
    #     obj.save()

    # def get_readonly_fields(self, request, obj=None):
    #     readonly_fields = super().get_readonly_fields(request, obj)
    #     if not request.user.is_superuser:
    #         readonly_fields += ('email', 'phone', 'telegram')
    #     return readonly_fields

    # def get_form(self, request, obj=None, **kwargs):
    #     form = super().get_form(request, obj, **kwargs)
    #     form.base_fields['password'].widget = None
    #     return form 

    # def get_queryset(self, request):
    #     qs = super().get_queryset(request)
    #     if request.user.is_superuser:
    #         return qs
    #     return qs.filter(email=request.user.email)  

    # def has_add_permission(self, request):
    #     return request.user.is_superuser   

    # def has_change_permission(self, request, obj=None):
    #     return request.user.is_superuser

    # def has_delete_permission(self, request, obj=None):
    #     return request.user.is_superuser
    
# admin.site.register(User, CustomUserAdmin)