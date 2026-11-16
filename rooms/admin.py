from django.contrib import admin
from django.db.models import Count, Q

from bookings.models import Booking

from .models import Room


class BookingInline(admin.TabularInline):
    model = Booking
    fields = ("user", "booking_date", "is_cancelled")
    extra = 0
    can_delete = False


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "inventory_number",
        "capacity",
        "required_level",
        "hourly_rate",
        "operational",
        "under_maintenance",
        "active_bookings_count",
    )
    list_display_links = ("name",)
    list_editable = ("capacity",)
    search_fields = ("name", "inventory_number")
    list_filter = (
        "capacity",
        "operational",
        "under_maintenance",
        "required_level",
    )
    ordering = ("name",)
    list_per_page = 20
    readonly_fields = ("id",)
    inlines = (BookingInline,)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(
            active_bookings=Count(
                "bookings",
                filter=Q(bookings__is_cancelled=False),
            )
        )

    @admin.display(
        description="Активных бронирований",
        ordering="active_bookings",
    )
    def active_bookings_count(self, obj):
        return obj.active_bookings
