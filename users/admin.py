from django.contrib import admin

from .models import User


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
    list_filter = ("role", "access_level", "briefing_passed")
    search_fields = ("name", "email")
