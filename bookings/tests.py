from datetime import date

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
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
                status=Booking.Status.ACTIVE,
            )
        Booking.objects.create(
            pk=7,
            room=cls.room,
            user=cls.user,
            booking_date=date(2026, 9, 10),
            duration_hours=1.0,
            cost=600.0,
            status=Booking.Status.CANCELLED,
        )
        Booking.objects.create(
            pk=8,
            room=cls.room,
            user=cls.user,
            booking_date=date(2026, 8, 15),
            duration_hours=2.0,
            cost=1200.0,
            status=Booking.Status.COMPLETED,
        )

    def test_booking_queryset_and_manager_methods(self):
        self.assertEqual(Booking.objects.count(), 8)
        self.assertEqual(Booking.objects.active().count(), 6)
        self.assertEqual(Booking.objects.cancelled().count(), 1)
        self.assertEqual(Booking.objects.completed().count(), 1)
        self.assertEqual(
            Booking.objects.for_date(date(2026, 9, 1)).count(),
            1,
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
        self.assertContains(response, self.room.get_absolute_url())

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
        self.assertEqual(booking.status, Booking.Status.CANCELLED)
        self.assertEqual(booking.get_status_display(), "Отменено")

    def test_django_admin_pages_and_actions(self):
        auth_user_model = get_user_model()
        admin_user = auth_user_model.objects.create_superuser(
            username="test_admin",
            email="admin@example.com",
            password="StrongPassword123!",
        )
        self.client.force_login(admin_user)

        for admin_url in (
            "/admin/",
            "/admin/rooms/room/",
            "/admin/rooms/room/1/change/",
            "/admin/users/user/",
            "/admin/users/user/1/change/",
            "/admin/bookings/booking/",
            "/admin/bookings/booking/1/change/",
        ):
            res = self.client.get(admin_url)
            self.assertEqual(res.status_code, 200)

        res_cancel = self.client.post(
            "/admin/bookings/booking/",
            {
                "action": "cancel_bookings",
                "_selected_action": ["2", "3"],
            },
            follow=True,
        )
        self.assertEqual(res_cancel.status_code, 200)
        self.assertEqual(
            Booking.objects.get(pk=2).status,
            Booking.Status.CANCELLED,
        )

        res_restore = self.client.post(
            "/admin/bookings/booking/",
            {
                "action": "restore_bookings",
                "_selected_action": ["2", "8"],
            },
            follow=True,
        )
        self.assertEqual(res_restore.status_code, 200)
        self.assertEqual(
            Booking.objects.get(pk=2).status,
            Booking.Status.ACTIVE,
        )
        self.assertEqual(
            Booking.objects.get(pk=8).status,
            Booking.Status.COMPLETED,
        )

    def test_roomly_operators_group_permissions(self):
        auth_user_model = get_user_model()
        room_ct = ContentType.objects.get_for_model(Room)
        allowed_perms = Permission.objects.filter(
            content_type=room_ct,
            codename__in=("view_room", "add_room", "change_room"),
        )
        operators_group = Group.objects.create(name="Roomly Operators")
        operators_group.permissions.set(allowed_perms)

        operator_user = auth_user_model.objects.create_user(
            username="roomly_operator",
            email="operator@example.com",
            password="OperatorPassword123!",
            is_staff=True,
            is_superuser=False,
        )
        operator_user.groups.add(operators_group)
        self.client.force_login(operator_user)

        self.assertTrue(operator_user.has_perm("rooms.view_room"))
        self.assertTrue(operator_user.has_perm("rooms.add_room"))
        self.assertTrue(operator_user.has_perm("rooms.change_room"))
        self.assertFalse(operator_user.has_perm("rooms.delete_room"))

        list_res = self.client.get("/admin/rooms/room/")
        self.assertEqual(list_res.status_code, 200)

        add_res = self.client.get("/admin/rooms/room/add/")
        self.assertEqual(add_res.status_code, 200)

        change_res = self.client.get("/admin/rooms/room/1/change/")
        self.assertEqual(change_res.status_code, 200)
        self.assertNotContains(change_res, "/admin/rooms/room/1/delete/")

        delete_res = self.client.get("/admin/rooms/room/1/delete/")
        self.assertEqual(delete_res.status_code, 403)
