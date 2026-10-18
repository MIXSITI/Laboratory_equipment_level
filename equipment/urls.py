from django.urls import path

from . import views

app_name = "equipment"

urlpatterns = [
    path("", views.equipment_list, name="equipment_list"),
    path(
        "<int:equipment_id>/",
        views.equipment_detail,
        name="equipment_detail",
    ),
    path("", views.equipment_list, name="list"),
    path("<int:equipment_id>/", views.equipment_detail, name="detail"),
]
