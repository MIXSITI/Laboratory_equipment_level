from django.contrib import admin

from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "room",
        "user",
        "booking_date",
        "duration_hours",
        "cost",
        "is_cancelled",
    )
    list_filter = ("is_cancelled", "booking_date", "room")
    search_fields = ("room__name", "user__name", "notes")
    list_select_related = ("room", "user")
