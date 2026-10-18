from django.urls import path

from . import views

app_name = "rooms"

urlpatterns = [
    path("", views.rooms, name="list"),
    path("<int:room_id>/", views.room_detail, name="detail"),
    path("", views.rooms, name="rooms"),
    path("<int:room_id>/", views.room_detail, name="room_detail"),
]
