from datetime import date

from django.test import TestCase

from bookings.models import Booking
from rooms.models import Room
from users.models import User


class UsersModelTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.student = User.objects.create(
            name="Иванов Алексей Сергеевич",
            email="ivanov@edu.mirea.ru",
            role=User.ROLE_STUDENT,
            access_level=2,
            briefing_passed=True,
        )
        cls.untrained = User.objects.create(
            name="Петров Дмитрий Иванович",
            email="petrov@edu.mirea.ru",
            role=User.ROLE_STUDENT,
            access_level=3,
            briefing_passed=False,
        )
        cls.room = Room.objects.create(
            name="Осциллограф DSO-X 2024A",
            capacity=25,
            required_level=1,
        )
        Booking.objects.create(
            room=cls.room,
            user=cls.student,
            booking_date=date(2026, 10, 1),
        )

    def test_user_access_and_role_methods(self):
        self.assertTrue(self.student.is_student())
        self.assertTrue(self.student.has_access(2))
        self.assertFalse(self.student.has_access(3))
        self.assertFalse(self.untrained.has_access(1))

    def test_user_reverse_bookings_relation(self):
        self.assertEqual(self.student.bookings.count(), 1)
        self.assertEqual(self.untrained.bookings.count(), 0)
