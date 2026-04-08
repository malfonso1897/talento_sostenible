from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Team


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("username", "email", "first_name", "last_name", "role", "department", "is_active")
    list_filter = ("role", "department", "is_active", "is_staff")
    fieldsets = BaseUserAdmin.fieldsets + (
        ("CRM", {"fields": ("role", "phone", "avatar", "department", "timezone", "language")}),
        ("Notificaciones", {"fields": ("email_notifications", "browser_notifications")}),
    )


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ("name", "leader", "created_at")
    filter_horizontal = ("members",)
