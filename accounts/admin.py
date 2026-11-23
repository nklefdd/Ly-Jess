from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class ShopUserAdmin(UserAdmin):
    list_display = ["id", "username", "email", "phone", "is_staff", "is_active"]
    fieldsets = UserAdmin.fieldsets + (("Контакти", {"fields": ["phone"]}),)
