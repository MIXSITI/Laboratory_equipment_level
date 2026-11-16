from datetime import date

from django.test import TestCase, override_settings
from django.urls import reverse

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
            status=Booking.Status.ACTIVE,
        )
        Booking.objects.create(
            room=cls.room_ready,
            user=cls.user,
            booking_date=date(2026, 9, 20),
            duration_hours=1.5,
            cost=900.0,
            status=Booking.Status.COMPLETED,
        )

    def test_rooms_list_view_search_and_context_processor(self):
        response = self.client.get(reverse("rooms:list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Спектрофотометр UV-1800")
        self.assertEqual(response.context["site_name"], "Roomly")
        self.assertEqual(response.context["rooms_count"], 3)
        self.assertContains(response, "Помещения (3)")

        res_search = self.client.get("/rooms/?q=спектрофотометр")
        self.assertEqual(res_search.status_code, 200)
        self.assertContains(res_search, "Спектрофотометр UV-1800")
        self.assertNotContains(res_search, "Ultimaker S3")

        res_cap_query = self.client.get("/rooms/?q=60")
        self.assertEqual(res_cap_query.status_code, 200)
        self.assertContains(res_cap_query, "Сканирующий электронный микроскоп")
        self.assertNotContains(res_cap_query, "Спектрофотометр UV-1800")

        res_sort_desc = self.client.get(
            "/rooms/?sort=capacity&direction=desc"
        )
        self.assertEqual(res_sort_desc.status_code, 200)
        names = [room.name for room in res_sort_desc.context["rooms"]]
        self.assertEqual(
            names,
            [
                "Сканирующий электронный микроскоп",
                "Спектрофотометр UV-1800",
                "3D-принтер Ultimaker S3",
            ],
        )

    def test_room_slug_max_length_protection(self):
        long_name = "Щ" * 200
        long_room = Room.objects.create(name=long_name, capacity=10)
        self.assertLessEqual(len(long_room.slug), 180)
        self.assertTrue(long_room.slug.endswith(f"-{long_room.pk}"))

    def test_room_slug_get_absolute_url_and_id_redirect(self):
        self.assertEqual(self.room_ready.slug, "spektrofotometr-uv-1800-1")
        expected_url = "/rooms/spektrofotometr-uv-1800-1/"
        self.assertEqual(self.room_ready.get_absolute_url(), expected_url)

        response = self.client.get(expected_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "EQ-301")

        redirect_response = self.client.get("/rooms/1/")
        self.assertEqual(redirect_response.status_code, 302)
        self.assertEqual(redirect_response.url, expected_url)

    def test_generated_field_is_large(self):
        self.room_ready.refresh_from_db()
        self.room_booked.refresh_from_db()
        self.assertFalse(self.room_ready.is_large)
        self.assertTrue(self.room_booked.is_large)

        temp_room = Room.objects.create(name="Аудитория 401", capacity=30)
        temp_room.refresh_from_db()
        self.assertFalse(temp_room.is_large)

        temp_room.capacity = 55
        temp_room.save()
        temp_room.refresh_from_db()
        self.assertTrue(temp_room.is_large)

    @override_settings(DEBUG=False)
    def test_room_detail_view_not_found(self):
        response = self.client.get("/rooms/nonexistent-slug-999/")
        self.assertEqual(response.status_code, 404)
        self.assertContains(
            response,
            "404 – страница не найдена",
            status_code=404,
        )

    def test_available_rooms_excludes_active_and_allows_completed(self):
        response = self.client.get("/rooms/available/?date=2026-09-20")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Спектрофотометр UV-1800")
        self.assertNotContains(response, "Сканирующий электронный микроскоп")
        self.assertNotContains(response, "3D-принтер Ultimaker S3")
