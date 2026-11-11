from django.test import TestCase, override_settings

from rooms.models import Room


class EquipmentViewsTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        Room.objects.create(
            pk=1,
            name="Спектрофотометр UV-1800",
            inventory_number="EQ-301",
            capacity=30,
            operational=True,
            under_maintenance=False,
            required_level=2,
            hourly_rate=1200.0,
        )
        Room.objects.create(
            pk=2,
            name="Осциллограф DSO-X 2024A",
            inventory_number="EQ-110",
            capacity=25,
            operational=True,
            under_maintenance=False,
            required_level=1,
            hourly_rate=850.0,
        )

    def test_equipment_list_view_and_filters(self):
        response = self.client.get("/equipment/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Лабораторное оборудование")
        self.assertContains(response, "Спектрофотометр UV-1800")

        res_level = self.client.get("/equipment/?level=1")
        self.assertEqual(res_level.status_code, 200)
        self.assertContains(res_level, "Осциллограф DSO-X 2024A")
        self.assertNotContains(res_level, "Спектрофотометр UV-1800")

    def test_equipment_detail_view_existing(self):
        response = self.client.get("/equipment/1/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Спектрофотометр UV-1800")
        self.assertContains(response, "Инвентарный номер")

    @override_settings(DEBUG=False)
    def test_equipment_detail_view_not_found(self):
        response = self.client.get("/equipment/999/")
        self.assertEqual(response.status_code, 404)
        self.assertContains(
            response,
            "404 – страница не найдена",
            status_code=404,
        )
