from django.urls import path

from . import views

app_name = "rooms"

urlpatterns = [
    path("", views.rooms, name="list"),
    path("create/", views.room_create, name="create"),
    path("available/", views.available_rooms, name="available"),
    path("<int:room_id>/", views.room_detail_by_id, name="detail_by_id"),
    path("<slug:slug>/", views.room_detail, name="detail"),
    path("<slug:slug>/edit/", views.room_update, name="update"),
]
