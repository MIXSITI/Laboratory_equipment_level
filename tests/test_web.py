import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "roomly.settings")
django.setup()

from django.test import Client, override_settings


def test_homepage_view():
    client = Client()
    response = client.get("/")
    assert response.status_code == 200
    assert "Лабораторное оборудование" in response.content.decode("utf-8")


@override_settings(DEBUG=False)
def test_unknown_url_uses_page_not_found():
    client = Client()
    response = client.get("/nonexistent/")
    body = response.content.decode("utf-8")
    assert response.status_code == 404
    assert "404 – страница не найдена" in body
    assert "На главную" in body


def test_equipment_list_view():
    client = Client()
    response = client.get("/equipment/")
    assert response.status_code == 200
    assert "Спектрофотометр UV-1800" in response.content.decode("utf-8")


def test_equipment_detail_view():
    client = Client()
    response = client.get("/equipment/1/")
    assert response.status_code == 200
    assert "EQ-301" in response.content.decode("utf-8")

    response_404 = client.get("/equipment/999/")
    assert response_404.status_code == 404
    assert "Оборудование не найдено" in response_404.content.decode("utf-8")


def test_rooms_views_compat():
    client = Client()
    response = client.get("/rooms/")
    assert response.status_code == 200

    response_detail = client.get("/rooms/1/")
    assert response_detail.status_code == 200

    response_404 = client.get("/rooms/999/")
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

    response_invalid = client.get("/rooms/available/?date=invalid")
    assert response_invalid.status_code == 200
    assert (
        "Укажите корректную дату"
        in response_invalid.content.decode("utf-8")
    )


def test_bookings_views():
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


def test_statistics_view():
    client = Client()
    response = client.get("/bookings/statistics/")
    assert response.status_code == 200
    body = response.content.decode("utf-8")
    assert "Статистика бронирований" in body
    assert "Количество бронирований по помещениям" in body
    assert "Активных бронирований" in body


def test_bookings_filter_and_sort_view():
    client = Client()

    res_sort = client.get("/bookings/?sort=room")
    assert res_sort.status_code == 200

    res_room = client.get("/bookings/?room=1")
    assert res_room.status_code == 200

    res_user = client.get("/bookings/?user=1")
    assert res_user.status_code == 200

    res_date = client.get("/bookings/?date=2026-07-15")
    assert res_date.status_code == 200

    res_err = client.get("/bookings/?date=wrong-date")
    assert res_err.status_code == 200
    assert "Укажите корректную дату" in res_err.content.decode("utf-8")

    res_page = client.get("/bookings/?page=1")
    assert res_page.status_code == 200
