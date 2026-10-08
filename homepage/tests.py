from django.test import TestCase


class HomepageTests(TestCase):

    def test_homepage_status_and_content(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Лабораторное оборудование")
        self.assertContains(response, "/equipment/")
        self.assertContains(response, "/bookings/")
