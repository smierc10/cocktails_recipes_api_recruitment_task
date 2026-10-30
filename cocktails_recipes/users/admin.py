from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User  # Replace with your actual model name


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ("username", "email", "handle", "is_staff", "is_active")

    search_fields = ("username", "email", "handle")

    fieldsets = UserAdmin.fieldsets + (
        ("Profile Information", {"fields": ("handle",)}),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Profile Information", {"fields": ("handle",)}),
    )
