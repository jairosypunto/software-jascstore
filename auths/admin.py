from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Auth

@admin.register(Auth)
class AuthAdmin(UserAdmin):
    list_display = ('username', 'email', 'name', 'lastname', 'is_staff')
    search_fields = ('username', 'email', 'name', 'lastname')
    list_filter = ('is_staff', 'is_superuser', 'is_active')