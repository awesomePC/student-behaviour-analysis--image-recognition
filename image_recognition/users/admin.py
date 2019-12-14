from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = [
        'email', 'username', 'first_name', 'last_name', 'user_type',
        'is_active', 'is_superuser',
    ]
    # for changing user_info
    fieldsets = (
        (
            ('User'), {
                'fields': ['username', 'password']
            }
        ),
        (
            ('Personal info'), {
                'fields': ['first_name', 'last_name', 'email', 'user_type']
            }
        ),
        (
            ('Permissions'), {
                'fields': ['is_active', 'is_staff', 'is_superuser']}
        ),
        (
            ('Important dates'), {
                'fields': ['last_login', 'date_joined']
            }
        ),
    )


admin.site.register(CustomUser, CustomUserAdmin)