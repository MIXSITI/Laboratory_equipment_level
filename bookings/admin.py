from django.contrib import admin, messages

from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "room",
        "user",
        "room_capacity",
        "booking_date",
        "duration_hours",
        "cost",
        "status",
    )
    list_display_links = ("id",)
    search_fields = ("room__name", "user__name", "notes")
    list_filter = ("booking_date", "status", "room", "user")
    ordering = ("-booking_date",)
    list_per_page = 20
    readonly_fields = ("id",)
    list_select_related = ("room", "user")
    date_hierarchy = "booking_date"
    autocomplete_fields = ("room", "user")
    actions = ("cancel_bookings", "restore_bookings")

    @admin.display(description="Вместимость", ordering="room__capacity")
    def room_capacity(self, obj):
        return obj.room.capacity

    @admin.action(description="Отменить выбранные бронирования")
    def cancel_bookings(self, request, queryset):
        count = 0
        for booking in queryset:
            booking.cancel()
            count += 1
        self.message_user(
            request,
            f"Отменено бронирований: {count}.",
            messages.SUCCESS,
        )

    @admin.action(description="Вернуть в активные")
    def restore_bookings(self, request, queryset):
        updated = queryset.update(status=Booking.Status.ACTIVE)
        self.message_user(
            request,
            f"Возвращено бронирований: {updated}.",
            messages.SUCCESS,
        )
