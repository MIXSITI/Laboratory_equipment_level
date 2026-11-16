from django.contrib import admin
from django.db.models import Count, Q
from django.utils.html import format_html

from bookings.models import Booking

from .models import Room


class BookingInline(admin.TabularInline):
    model = Booking
    fields = ("user", "booking_date", "status")
    extra = 0
    can_delete = False


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "inventory_number",
        "capacity",
        "is_large",
        "required_level",
        "hourly_rate",
        "operational",
        "under_maintenance",
        "active_bookings_count",
        "site_link",
    )
    list_display_links = ("name",)
    list_editable = ("capacity",)
    search_fields = ("name", "inventory_number")
    list_filter = (
        "capacity",
        "is_large",
        "operational",
        "under_maintenance",
        "required_level",
    )
    ordering = ("name",)
    list_per_page = 20
    readonly_fields = ("id", "slug", "is_large")
    inlines = (BookingInline,)
    view_on_site = True

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(
            active_bookings=Count(
                "bookings",
                filter=Q(bookings__status=Booking.Status.ACTIVE),
            )
        )

    @admin.display(
        description="Активных бронирований",
        ordering="active_bookings",
    )
    def active_bookings_count(self, obj):
        return obj.active_bookings

    @admin.display(description="Страница на сайте")
    def site_link(self, obj):
        return format_html(
            '<a href="{}" target="_blank">Открыть</a>',
            obj.get_absolute_url(),
        )
