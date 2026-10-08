from django.test import TestCase


class RoomsViewsTests(TestCase):
    """Проверка представлений помещений."""

    def test_rooms_list_view(self):
        """Список помещений возвращает статус 200."""
        response = self.client.get("/rooms/")
        self.assertEqual(response.status_code, 200)

    def test_room_detail_view_existing(self):
        """Детальная страница возвращает статус 200."""
        response = self.client.get("/rooms/1/")
        self.assertEqual(response.status_code, 200)

    def test_room_detail_view_not_found(self):
        """Несуществующий ID возвращает статус 404."""
        response = self.client.get("/rooms/999/")
        self.assertEqual(response.status_code, 404)
