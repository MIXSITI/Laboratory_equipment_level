import pytest
from django.core.management import call_command
from django.test import Client, override_settings

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def load_initial_fixture():
    call_command("loaddata", "data/fixtures/initial_data.json", verbosity=0)


def test_homepage_view():
    client = Client()
    response = client.get("/")
    body = response.content.decode("utf-8")
    assert response.status_code == 200
    assert "Лабораторное оборудование" in body
    assert "Спектрофотометр UV-1800" in body


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
def test_rooms_views_compat_and_search():
    client = Client()
    response = client.get("/rooms/")
    assert response.status_code == 200

    res_query = client.get("/rooms/?q=спектрофотометр&ready=1")
    body_query = res_query.content.decode("utf-8")
    assert res_query.status_code == 200
    assert "Спектрофотометр UV-1800" in body_query

    response_detail = client.get("/rooms/1/")
    assert response_detail.status_code == 200
    assert "EQ-301" in response_detail.content.decode("utf-8")

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
    assert "Сканирующий электронный микроскоп" not in body
    assert "3D-принтер Ultimaker S3" not in body

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
    assert "Бронирования оборудования" in response.content.decode("utf-8")

    response_detail = client.get("/bookings/1/")
    assert response_detail.status_code == 200
    assert "Бронирование №1" in response_detail.content.decode("utf-8")

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
