from django.contrib import admin
from .models import CustomUser


@admin.register(CustomUser)
class CustomAdmin(admin.ModelAdmin):
    list_display = ("id", "email", "phone_number", "name")
    list_filter = ("email",)
    search_fields = ("email", "phone_number")