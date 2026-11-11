from django.conf import settings
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("homepage.urls")),
    path("equipment/", include("equipment.urls")),
    path("rooms/", include("rooms.urls")),
    path("bookings/", include("bookings.urls")),
]

if getattr(settings, "ENABLE_DEBUG_TOOLBAR", False):
    urlpatterns.append(path("__debug__/", include("debug_toolbar.urls")))

handler404 = "homepage.views.page_not_found"
