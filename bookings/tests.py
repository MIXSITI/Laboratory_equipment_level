from django.test import TestCase


class BookingsViewsTests(TestCase):
    """Проверка представлений бронирований."""

    def test_bookings_list_view(self):
        """Список бронирований возвращает 200 и содержит заявки."""
        response = self.client.get("/bookings/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Бронирования оборудования")

    def test_booking_detail_view_existing(self):
        """Детальная страница бронирования возвращает 200."""
        response = self.client.get("/bookings/1/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Бронирование №1")

    def test_booking_detail_view_not_found(self):
        """Несуществующее бронирование возвращает 404."""
        response = self.client.get("/bookings/999/")
        self.assertEqual(response.status_code, 404)
        self.assertContains(
            response,
            "Бронирование не найдено",
            status_code=404,
        )
