from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models import ProtectedError
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from bookings.forms import BookingFilterForm, BookingForm
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


class BookingFormsTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.room = Room.objects.create(
            name="Спектрофотометр UV-1800",
            inventory_number="EQ-301",
            capacity=30,
            operational=True,
            under_maintenance=False,
            hourly_rate=1200.0,
        )
        cls.other_room = Room.objects.create(
            name="Осциллограф DSO-X 2024A",
            inventory_number="EQ-110",
            capacity=20,
            operational=True,
            under_maintenance=False,
            hourly_rate=800.0,
        )
        cls.maintenance_room = Room.objects.create(
            name="3D-принтер на ТО",
            inventory_number="EQ-220",
            capacity=10,
            operational=True,
            under_maintenance=True,
            hourly_rate=600.0,
        )
        cls.user = User.objects.create(
            name="Иванов Алексей Сергеевич",
            email="ivanov@edu.mirea.ru",
            role=User.ROLE_STUDENT,
            access_level=2,
            briefing_passed=True,
        )

    def test_booking_filter_form_validation(self):
        unbound = BookingFilterForm(None)
        self.assertFalse(unbound.is_bound)

        invalid_room_res = self.client.get("/bookings/?room=999999")
        self.assertEqual(invalid_room_res.status_code, 200)
        self.assertContains(
            invalid_room_res,
            "Проверьте корректность параметров фильтрации.",
        )

        invalid_sort_res = self.client.get("/bookings/?sort=unknown")
        self.assertEqual(invalid_sort_res.status_code, 200)
        self.assertContains(
            invalid_sort_res,
            "Проверьте корректность параметров фильтрации.",
        )

        invalid_date_res = self.client.get("/bookings/?date=not-a-date")
        self.assertEqual(invalid_date_res.status_code, 200)
        self.assertContains(invalid_date_res, "Укажите корректную дату.")

    def test_booking_create_get_initial_and_post_success(self):
        today = timezone.localdate()
        get_res = self.client.get(reverse("bookings:booking_create"))
        self.assertEqual(get_res.status_code, 200)
        self.assertContains(get_res, "csrfmiddlewaretoken")
        self.assertEqual(
            get_res.context["form"].initial["booking_date"],
            today,
        )

        post_res = self.client.post(
            reverse("bookings:booking_create"),
            {
                "room": self.room.pk,
                "booking_date": (today + timedelta(days=2)).isoformat(),
                "user": self.user.pk,
                "duration_hours": "2.5",
                "notes": "Измерение спектров",
            },
        )
        self.assertRedirects(post_res, reverse("bookings:bookings"))
        booking = Booking.objects.get()
        self.assertEqual(booking.status, Booking.Status.ACTIVE)
        self.assertEqual(booking.cost, 3000.0)
        self.assertEqual(booking.notes, "Измерение спектров")

    def test_booking_create_validation_and_availability(self):
        today = timezone.localdate()
        future_date = today + timedelta(days=3)

        past_res = self.client.post(
            reverse("bookings:booking_create"),
            {
                "room": self.room.pk,
                "booking_date": (today - timedelta(days=1)).isoformat(),
                "user": self.user.pk,
                "duration_hours": "1.0",
            },
        )
        self.assertEqual(past_res.status_code, 200)
        self.assertContains(
            past_res,
            "Нельзя создать бронирование на прошедшую дату.",
        )

        bad_dur_res = self.client.post(
            reverse("bookings:booking_create"),
            {
                "room": self.room.pk,
                "booking_date": future_date.isoformat(),
                "user": self.user.pk,
                "duration_hours": "20",
            },
        )
        self.assertEqual(bad_dur_res.status_code, 200)
        self.assertContains(
            bad_dur_res,
            "Длительность бронирования не может превышать 12 часов.",
        )

        maint_res = self.client.post(
            reverse("bookings:booking_create"),
            {
                "room": self.maintenance_room.pk,
                "booking_date": future_date.isoformat(),
                "user": self.user.pk,
                "duration_hours": "1.0",
            },
        )
        self.assertEqual(maint_res.status_code, 200)
        self.assertContains(maint_res, "недоступен")

        Booking.objects.create(
            room=self.room,
            user=self.user,
            booking_date=future_date,
            duration_hours=1.0,
            cost=1200.0,
            status=Booking.Status.ACTIVE,
        )
        conflict_res = self.client.post(
            reverse("bookings:booking_create"),
            {
                "room": self.room.pk,
                "booking_date": future_date.isoformat(),
                "user": self.user.pk,
                "duration_hours": "2.0",
            },
        )
        self.assertEqual(conflict_res.status_code, 200)
        self.assertContains(
            conflict_res,
            "Выбранное помещение уже забронировано на эту дату.",
        )
        self.assertEqual(Booking.objects.count(), 1)

        cancelled_date = today + timedelta(days=4)
        Booking.objects.create(
            room=self.room,
            user=self.user,
            booking_date=cancelled_date,
            duration_hours=1.0,
            cost=1200.0,
            status=Booking.Status.CANCELLED,
        )
        ok_after_cancel = self.client.post(
            reverse("bookings:booking_create"),
            {
                "room": self.room.pk,
                "booking_date": cancelled_date.isoformat(),
                "user": self.user.pk,
                "duration_hours": "1.5",
            },
        )
        self.assertRedirects(ok_after_cancel, reverse("bookings:bookings"))
        self.assertEqual(Booking.objects.active().count(), 2)

    def test_booking_update_and_cancel(self):
        today = timezone.localdate()
        date_1 = today + timedelta(days=5)
        date_2 = today + timedelta(days=6)
        booking = Booking.objects.create(
            room=self.room,
            user=self.user,
            booking_date=date_1,
            duration_hours=1.0,
            cost=1200.0,
            status=Booking.Status.ACTIVE,
        )
        other_booking = Booking.objects.create(
            room=self.other_room,
            user=self.user,
            booking_date=date_2,
            duration_hours=1.0,
            cost=800.0,
            status=Booking.Status.ACTIVE,
        )

        self.assertIn("room", BookingForm.Meta.fields)
        self.assertNotIn("status", BookingForm.Meta.fields)

        edit_url = reverse("bookings:booking_update", args=[booking.pk])
        get_edit = self.client.get(edit_url)
        self.assertEqual(get_edit.status_code, 200)
        self.assertContains(
            get_edit,
            f"Редактирование бронирования №{booking.pk}",
        )

        same_slot_res = self.client.post(
            edit_url,
            {
                "room": self.room.pk,
                "booking_date": date_1.isoformat(),
                "user": self.user.pk,
                "duration_hours": "3.0",
                "notes": "Обновлённая длительность",
            },
        )
        self.assertRedirects(same_slot_res, reverse("bookings:bookings"))
        booking.refresh_from_db()
        self.assertEqual(booking.cost, 3600.0)
        self.assertEqual(booking.notes, "Обновлённая длительность")
        self.assertEqual(Booking.objects.count(), 2)

        conflict_edit = self.client.post(
            edit_url,
            {
                "room": other_booking.room.pk,
                "booking_date": date_2.isoformat(),
                "user": self.user.pk,
                "duration_hours": "1.0",
            },
        )
        self.assertEqual(conflict_edit.status_code, 200)
        self.assertContains(
            conflict_edit,
            "Выбранное помещение уже забронировано на эту дату.",
        )

        not_found_edit = self.client.get(
            reverse("bookings:booking_update", args=[99999])
        )
        self.assertEqual(not_found_edit.status_code, 404)

        cancel_url = reverse("bookings:booking_cancel", args=[booking.pk])
        get_cancel = self.client.get(cancel_url)
        self.assertEqual(get_cancel.status_code, 405)

        post_cancel = self.client.post(cancel_url)
        self.assertRedirects(post_cancel, reverse("bookings:bookings"))
        booking.refresh_from_db()
        self.assertEqual(booking.status, Booking.Status.CANCELLED)

        repeat_cancel = self.client.post(cancel_url)
        self.assertEqual(repeat_cancel.status_code, 404)

        cancelled_edit = self.client.get(edit_url)
        self.assertEqual(cancelled_edit.status_code, 404)
