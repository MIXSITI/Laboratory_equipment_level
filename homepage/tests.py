from datetime import date

from django.test import TestCase, override_settings

from bookings.models import Booking
from rooms.models import Room
from users.models import User


class HomepageTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        room = Room.objects.create(
            name="Спектрофотометр UV-1800",
            inventory_number="EQ-301",
            capacity=30,
            hourly_rate=1200.0,
        )
        user = User.objects.create(
            name="Иванов Алексей Сергеевич",
            email="ivanov@edu.mirea.ru",
        )
        Booking.objects.create(
            room=room,
            user=user,
            booking_date=date(2026, 9, 15),
        )

    def test_homepage_status_and_content(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Лабораторное оборудование")
        self.assertContains(response, "/equipment/")
        self.assertContains(response, "/bookings/")
        self.assertContains(response, "Спектрофотометр UV-1800")

    @override_settings(DEBUG=False)
    def test_custom_404_handler(self):
        response = self.client.get("/unknown-route/")
        self.assertEqual(response.status_code, 404)
        self.assertContains(
            response,
            "404 – страница не найдена",
            status_code=404,
        )
