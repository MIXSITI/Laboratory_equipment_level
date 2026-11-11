from datetime import date

from django.test import TestCase, override_settings

from bookings.models import Booking
from rooms.models import Room
from users.models import User


class RoomsViewsTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.room_ready = Room.objects.create(
            pk=1,
            name="Спектрофотометр UV-1800",
            inventory_number="EQ-301",
            capacity=30,
            operational=True,
            under_maintenance=False,
            required_level=2,
            hourly_rate=1200.0,
        )
        cls.room_booked = Room.objects.create(
            pk=2,
            name="Сканирующий электронный микроскоп",
            inventory_number="EQ-505",
            capacity=60,
            operational=True,
            under_maintenance=False,
            required_level=3,
            hourly_rate=2500.0,
        )
        cls.room_maintenance = Room.objects.create(
            pk=4,
            name="3D-принтер Ultimaker S3",
            inventory_number="EQ-220",
            capacity=15,
            operational=True,
            under_maintenance=True,
            required_level=2,
            hourly_rate=610.0,
        )
        cls.user = User.objects.create(
            pk=1,
            name="Иванов Алексей Сергеевич",
            email="ivanov@edu.mirea.ru",
            role="студент",
            access_level=2,
            briefing_passed=True,
        )
        Booking.objects.create(
            room=cls.room_booked,
            user=cls.user,
            booking_date=date(2026, 9, 20),
            duration_hours=2.0,
            cost=5000.0,
            is_cancelled=False,
        )

    def test_rooms_list_view_and_search(self):
        response = self.client.get("/rooms/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Спектрофотометр UV-1800")

        res_search = self.client.get("/rooms/?q=спектрофотометр")
        self.assertEqual(res_search.status_code, 200)
        self.assertContains(res_search, "Спектрофотометр UV-1800")
        self.assertNotContains(res_search, "Ultimaker S3")

    def test_room_detail_view_existing(self):
        response = self.client.get("/rooms/1/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "EQ-301")

    @override_settings(DEBUG=False)
    def test_room_detail_view_not_found(self):
        response = self.client.get("/rooms/999/")
        self.assertEqual(response.status_code, 404)
        self.assertContains(
            response,
            "404 – страница не найдена",
            status_code=404,
        )

    def test_available_rooms_excludes_booked_and_maintenance(self):
        response = self.client.get("/rooms/available/?date=2026-09-20")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Спектрофотометр UV-1800")
        self.assertNotContains(response, "Сканирующий электронный микроскоп")
        self.assertNotContains(response, "3D-принтер Ultimaker S3")
