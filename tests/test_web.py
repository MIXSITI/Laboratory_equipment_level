import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "roomly.settings")
django.setup()

from django.test import Client  # noqa: E402


def test_homepage_view():
    """Проверка главной страницы."""
    client = Client()
    response = client.get("/")
    assert response.status_code == 200
    assert "Лабораторное оборудование" in response.content.decode("utf-8")


def test_equipment_list_view():
    """Проверка списка оборудования."""
    client = Client()
    response = client.get("/equipment/")
    assert response.status_code == 200
    assert "Спектрофотометр UV-1800" in response.content.decode("utf-8")


def test_equipment_detail_view():
    """Проверка детальной информации оборудования и ошибки 404."""
    client = Client()
    response = client.get("/equipment/1/")
    assert response.status_code == 200
    assert "EQ-301" in response.content.decode("utf-8")

    response_404 = client.get("/equipment/999/")
    assert response_404.status_code == 404
    assert "Оборудование не найдено" in response_404.content.decode("utf-8")


def test_rooms_views_compat():
    """Проверка совместимости маршрутов /rooms/."""
    client = Client()
    response = client.get("/rooms/")
    assert response.status_code == 200

    response_detail = client.get("/rooms/1/")
    assert response_detail.status_code == 200

    response_404 = client.get("/rooms/999/")
    assert response_404.status_code == 404


def test_bookings_views():
    """Проверка списка бронирований и детальной страницы."""
    client = Client()
    response = client.get("/bookings/")
    assert response.status_code == 200
    assert "Бронирования оборудования" in response.content.decode("utf-8")

    response_detail = client.get("/bookings/1/")
    assert response_detail.status_code == 200
    assert "Бронирование №1" in response_detail.content.decode("utf-8")

    response_404 = client.get("/bookings/999/")
    assert response_404.status_code == 404
    assert "Бронирование не найдено" in response_404.content.decode("utf-8")
