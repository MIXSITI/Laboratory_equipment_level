"""Тесты приложения homepage."""

from django.test import TestCase


class HomepageTests(TestCase):
    """Проверка доступности главной страницы."""

    def test_homepage_status_and_content(self):
        """Главная страница возвращает статус 200 и содержит ссылки."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Лабораторное оборудование")
        self.assertContains(response, "/equipment/")
        self.assertContains(response, "/bookings/")
