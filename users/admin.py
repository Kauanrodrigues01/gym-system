from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

class UserAdmin(BaseUserAdmin):
    list_display = ('cpf', 'email', 'full_name', 'is_staff', 'is_active')
    search_fields = ('cpf', 'email', 'full_name')
    ordering = ('cpf',)
    
    fieldsets = (
        (None, {'fields': ('cpf', 'email', 'password')}),
        ('Personal Info', {'fields': ('full_name',)}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
    )

admin.site.register(User, UserAdmin)
