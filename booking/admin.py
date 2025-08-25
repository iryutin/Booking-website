from django.contrib import admin
from .models import Table, Booking


@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ("id", "number", "capacity", "is_active")


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('booking_date', 'table', 'created_date', 'user')
    list_filter = ('user', 'table')
    search_fields = ('user', 'table')

    def save_model(self, request, obj, form, change):
        if not change:  # Если это создание нового объекта
            obj.owner = request.user
        super().save_model(request, obj, form, change)