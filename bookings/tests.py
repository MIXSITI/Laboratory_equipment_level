from datetime import date

from django.db.models import ProtectedError
from django.test import TestCase, override_settings

from bookings.models import Booking
from rooms.models import Room
from users.models import User


class BookingsViewsTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.room = Room.objects.create(
            pk=1,
            name="Спектрофотометр UV-1800",
            inventory_number="EQ-301",
            capacity=30,
            hourly_rate=1200.0,
        )
        cls.user = User.objects.create(
            pk=1,
            name="Иванов Алексей Сергеевич",
            email="ivanov@edu.mirea.ru",
            role="студент",
            access_level=2,
            briefing_passed=True,
        )
        for day in range(1, 7):
            Booking.objects.create(
                pk=day,
                room=cls.room,
                user=cls.user,
                booking_date=date(2026, 9, day),
                duration_hours=2.0,
                cost=1200.0,
                is_cancelled=False,
            )

    def test_bookings_list_view_and_pagination(self):
        response = self.client.get("/bookings/?room=1&sort=date")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Бронирования оборудования")
        self.assertContains(response, "page=2")

        res_page2 = self.client.get("/bookings/?room=1&sort=date&page=2")
        self.assertEqual(res_page2.status_code, 200)
        self.assertContains(res_page2, "Бронирование №6")

    def test_booking_detail_view_existing(self):
        response = self.client.get("/bookings/1/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Бронирование №1")

    @override_settings(DEBUG=False)
    def test_booking_detail_view_not_found(self):
        response = self.client.get("/bookings/999/")
        self.assertEqual(response.status_code, 404)
        self.assertContains(
            response,
            "404 – страница не найдена",
            status_code=404,
        )

    def test_on_delete_protect_and_cancel_method(self):
        with self.assertRaises(ProtectedError):
            self.room.delete()

        booking = Booking.objects.get(pk=1)
        booking.cancel()
        booking.refresh_from_db()
        self.assertTrue(booking.is_cancelled)
        self.assertEqual(booking.status, "Отменено")
