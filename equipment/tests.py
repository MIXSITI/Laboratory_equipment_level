"""Тесты приложения equipment."""

from django.test import TestCase


class EquipmentViewsTests(TestCase):
    """Проверка представлений лабораторного оборудования."""

    def test_equipment_list_view(self):
        """Список оборудования возвращает статус 200 и содержит приборы."""
        response = self.client.get("/equipment/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Лабораторное оборудование")
        self.assertContains(response, "Спектрофотометр UV-1800")

    def test_equipment_detail_view_existing(self):
        """Детальная страница существующего прибора возвращает 200."""
        response = self.client.get("/equipment/1/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Спектрофотометр UV-1800")
        self.assertContains(response, "Инвентарный номер")

    def test_equipment_detail_view_not_found(self):
        """Несуществующий прибор возвращает 404."""
        response = self.client.get("/equipment/999/")
        self.assertEqual(response.status_code, 404)
        self.assertContains(
            response,
            "Оборудование не найдено",
            status_code=404,
        )
