from django.test import TestCase


class BookingsViewsTests(TestCase):

    def test_bookings_list_view(self):
        response = self.client.get("/bookings/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Бронирования оборудования")

    def test_booking_detail_view_existing(self):
        response = self.client.get("/bookings/1/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Бронирование №1")

    def test_booking_detail_view_not_found(self):
        response = self.client.get("/bookings/999/")
        self.assertEqual(response.status_code, 404)
        self.assertContains(
            response,
            "Бронирование не найдено",
            status_code=404,
        )
