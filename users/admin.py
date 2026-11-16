from django.contrib import admin

from bookings.models import Booking

from .models import User


class UserBookingInline(admin.TabularInline):
    model = Booking
    fields = ("room", "booking_date", "status")
    extra = 0
    can_delete = False


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "email",
        "role",
        "access_level",
        "briefing_passed",
    )
    list_display_links = ("name",)
    search_fields = ("name", "email")
    list_filter = ("role", "access_level", "briefing_passed")
    ordering = ("name",)
    list_per_page = 20
    readonly_fields = ("id",)
    inlines = (UserBookingInline,)
