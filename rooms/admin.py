from django.contrib import admin

from .models import Room


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
    )
    list_filter = ("operational", "under_maintenance", "required_level")
    search_fields = ("name", "inventory_number")
