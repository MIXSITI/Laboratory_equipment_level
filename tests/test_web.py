from datetime import timedelta
from io import BytesIO

import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import Client, override_settings
from django.utils import timezone
from PIL import Image

from bookings.models import Booking
from rooms.models import Room
from users.models import User

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def load_initial_fixture():
    call_command("loaddata", "data/fixtures/initial_data.json", verbosity=0)


def test_homepage_view_and_context_processor():
    client = Client()
    response = client.get("/")
    body = response.content.decode("utf-8")
    assert response.status_code == 200
    assert "Лабораторное оборудование" in body
    assert "Спектрофотометр UV-1800" in body
    assert "Помещения (4)" in body


@override_settings(DEBUG=False)
def test_unknown_url_uses_page_not_found():
    client = Client()
    response = client.get("/nonexistent/")
    body = response.content.decode("utf-8")
    assert response.status_code == 404
    assert "404 – страница не найдена" in body
    assert "На главную" in body


@override_settings(DEBUG=False)
def test_equipment_views_and_orm_search():
    client = Client()
    response = client.get("/equipment/")
    assert response.status_code == 200
    assert "Спектрофотометр UV-1800" in response.content.decode("utf-8")

    res_search = client.get("/equipment/?q=eq-301")
    body_search = res_search.content.decode("utf-8")
    assert res_search.status_code == 200
    assert "Спектрофотометр UV-1800" in body_search
    assert "Осциллограф" not in body_search

    response_detail = client.get("/equipment/1/")
    assert response_detail.status_code == 200
    assert "EQ-301" in response_detail.content.decode("utf-8")

    response_404 = client.get("/equipment/999/")
    assert response_404.status_code == 404
    assert "404 – страница не найдена" in response_404.content.decode("utf-8")


@override_settings(DEBUG=False)
def test_rooms_views_slug_and_search():
    client = Client()
    response = client.get("/rooms/")
    assert response.status_code == 200

    res_query = client.get("/rooms/?q=спектрофотометр&ready=1")
    body_query = res_query.content.decode("utf-8")
    assert res_query.status_code == 200
    assert "Спектрофотометр UV-1800" in body_query

    room = Room.objects.get(pk=1)
    response_slug = client.get(room.get_absolute_url())
    assert response_slug.status_code == 200
    assert "EQ-301" in response_slug.content.decode("utf-8")

    response_id = client.get("/rooms/1/", follow=True)
    assert response_id.status_code == 200
    assert "EQ-301" in response_id.content.decode("utf-8")

    response_404 = client.get("/rooms/nonexistent-room-slug/")
    assert response_404.status_code == 404


def test_available_rooms_view():
    client = Client()
    response = client.get("/rooms/available/")
    assert response.status_code == 200
    assert "Свободные помещения" in response.content.decode("utf-8")

    response_search = client.get("/rooms/available/?date=2026-09-20")
    assert response_search.status_code == 200
    body = response_search.content.decode("utf-8")
    assert "Дата: 2026-09-20" in body
    assert "Спектрофотометр UV-1800" in body
    assert "Сканирующий электронный микроскоп" not in body
    assert "3D-принтер Ultimaker S3" not in body

    response_completed = client.get("/rooms/available/?date=2026-08-10")
    assert response_completed.status_code == 200
    assert (
        "Осциллограф DSO-X 2024A"
        in response_completed.content.decode("utf-8")
    )

    response_invalid = client.get("/rooms/available/?date=invalid")
    assert response_invalid.status_code == 200
    assert (
        "Укажите корректную дату"
        in response_invalid.content.decode("utf-8")
    )


@override_settings(DEBUG=False)
def test_bookings_views():
    client = Client()
    response = client.get("/bookings/")
    assert response.status_code == 200
    body = response.content.decode("utf-8")
    assert "Список бронирований" in body
    assert "<title>Список бронирований – Roomly</title>" in body
    assert "Всего активных бронирований по выбранным условиям:" in body

    response_detail = client.get("/bookings/1/")
    assert response_detail.status_code == 200
    detail_body = response_detail.content.decode("utf-8")
    assert "Бронирование №1" in detail_body
    assert "<title>Бронирование № 1 – Roomly</title>" in detail_body

    response_404 = client.get("/bookings/999/")
    assert response_404.status_code == 404
    assert "404 – страница не найдена" in response_404.content.decode("utf-8")


def test_statistics_view():
    client = Client()
    response = client.get("/bookings/statistics/")
    assert response.status_code == 200
    body = response.content.decode("utf-8")
    assert "Статистика бронирований" in body
    assert "Количество бронирований по помещениям" in body
    assert "Активных бронирований" in body
    assert "Завершённых" in body
    assert "Django ORM" in body


def test_bookings_filter_sort_related_and_pagination():
    client = Client()

    res_sort = client.get("/bookings/?sort=room")
    assert res_sort.status_code == 200

    res_role = client.get("/bookings/?role=сотрудник")
    body_role = res_role.content.decode("utf-8")
    assert res_role.status_code == 200
    assert "Бронирование №3:" in body_role
    assert "Бронирование №1:" not in body_role

    res_search = client.get("/bookings/?search=микроскоп")
    body_search = res_search.content.decode("utf-8")
    assert res_search.status_code == 200
    assert "Сканирующий электронный микроскоп" in body_search

    res_paged = client.get("/bookings/?room=1&sort=date")
    body_paged = res_paged.content.decode("utf-8")
    assert res_paged.status_code == 200
    assert "page=2" in body_paged

    res_page2 = client.get("/bookings/?room=1&sort=date&page=2")
    body_page2 = res_page2.content.decode("utf-8")
    assert res_page2.status_code == 200
    assert "room=1" in body_page2
    assert "sort=date" in body_page2

    res_err = client.get("/bookings/?date=wrong-date")
    assert res_err.status_code == 200
    assert "Укажите корректную дату" in res_err.content.decode("utf-8")

    res_cancelled = client.get("/bookings/?status=cancelled")
    body_cancelled = res_cancelled.content.decode("utf-8")
    assert res_cancelled.status_code == 200
    assert "Бронирование №5:" in body_cancelled
    assert "Бронирование №1:" not in body_cancelled

    res_completed = client.get("/bookings/?status=completed")
    body_completed = res_completed.content.decode("utf-8")
    assert res_completed.status_code == 200
    assert "Бронирование №11:" in body_completed


def test_pr11_booking_and_room_forms_workflow(tmp_path, settings):
    settings.MEDIA_ROOT = tmp_path
    client = Client()
    auth_user_model = get_user_model()
    auth_user = auth_user_model.objects.create_user(
        username="ivanov_web",
        email="ivanov@edu.mirea.ru",
        password="WebPassword123!",
    )
    client.force_login(auth_user)
    future_date = (timezone.localdate() + timedelta(days=10)).isoformat()

    create_booking_res = client.post(
        "/bookings/create/",
        {
            "room": 1,
            "booking_date": future_date,
            "duration_hours": "2.0",
            "notes": "Тестовый запуск ПР13",
        },
        follow=True,
    )
    assert create_booking_res.status_code == 200
    created = Booking.objects.get(booking_date=future_date, room_id=1)
    assert created.cost == 2400.0
    assert created.user == User.objects.get(pk=1)

    cancel_res = client.post(
        f"/bookings/{created.pk}/cancel/",
        follow=True,
    )
    assert cancel_res.status_code == 200
    created.refresh_from_db()
    assert created.status == Booking.Status.CANCELLED

    buffer = BytesIO()
    Image.new("RGB", (8, 8), color=(10, 200, 100)).save(buffer, format="PNG")
    img_file = SimpleUploadedFile(
        "equip.png",
        buffer.getvalue(),
        content_type="image/png",
    )
    room_res = client.post(
        "/rooms/create/",
        {
            "name": "Хроматограф ГХ-1000",
            "inventory_number": "EQ-888",
            "capacity": "10",
            "required_level": "1",
            "hourly_rate": "950",
            "operational": "on",
            "image": img_file,
        },
        follow=True,
    )
    assert room_res.status_code == 200
    room = Room.objects.get(inventory_number="EQ-888")
    assert room.image.url in room_res.content.decode("utf-8")
