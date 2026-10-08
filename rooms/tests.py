from django.test import TestCase


class RoomsViewsTests(TestCase):

    def test_rooms_list_view(self):
        response = self.client.get("/rooms/")
        self.assertEqual(response.status_code, 200)

    def test_room_detail_view_existing(self):
        response = self.client.get("/rooms/1/")
        self.assertEqual(response.status_code, 200)

    def test_room_detail_view_not_found(self):
        response = self.client.get("/rooms/999/")
        self.assertEqual(response.status_code, 404)
