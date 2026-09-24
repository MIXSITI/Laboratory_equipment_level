"""Тесты для класса Booking, Period и функций управления бронированием."""

import sys
from datetime import date
from pathlib import Path

# Поддержка прямого запуска файла: python tests/test_bookings.py
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import pytest  # noqa: E402
from models.bookings import (  # noqa: E402
    Booking,
    Period,
    calculate_booking_cost,
    cancel_booking,
    create_booking,
    get_booking_statistics,
    is_equipment_available,
)
from models.equipment import Equipment  # noqa: E402
from models.users import Student, User  # noqa: E402
from storage import (  # noqa: E402
    load_bookings,
    load_equipment,
    load_users,
    save_bookings,
    save_equipment,
    save_users,
)


def test_booking_creation_and_period():
    """Проверить создание объекта Booking, связей и сущности Period."""
    equipment = Equipment(1, "Спектрофотометр", hourly_rate=1200.0)
    user = Student(1, "Иванов Алексей")
    booking = Booking(
        booking_id=1,
        equipment=equipment,
        booking_date=date(2026, 9, 15),
        user=user,
        duration_hours=3.0,
        cost=1800.0,
    )
    assert booking.id == 1
    assert booking.equipment is equipment
    assert booking.user is user

    # Проверка инкапсуляции сущности Период
    assert isinstance(booking.period, Period)
    assert booking.booking_date == date(2026, 9, 15)
    assert booking.duration_hours == 3.0
    assert booking.cost == 1800.0
    assert booking.is_cancelled is False


def test_period_entity():
    """Проверить сущность Period (период бронирования)."""
    p = Period("2026-10-01", 2.5)
    assert p.date == date(2026, 10, 1)
    assert p.duration_hours == 2.5
    assert "2026-10-01" in str(p)


def test_booking_str():
    """Проверить строковое представление объекта Booking (__str__)."""
    equipment = Equipment(1, "Микроскоп")
    user = User(1, "Петров")
    booking = Booking(1, equipment, date(2026, 10, 1), user, 2.0, 1000.0)
    text = str(booking)
    assert "Заявка #1" in text
    assert "[АКТИВНО]" in text
    assert "Микроскоп" in text
    assert "Петров" in text


def test_booking_status_property():
    """Проверить свойство status объекта Booking (@property)."""
    equipment = Equipment(1, "Прибор")
    user = User(1, "Пользователь")
    booking = Booking(1, equipment, date(2026, 9, 15), user)

    assert booking.status == "Подтверждено"
    booking.cancel()
    assert booking.status == "Отменено"
    assert booking.is_cancelled is True


def test_booking_cancel():
    """Проверить, что отмена не удаляет бронирование, а меняет его статус."""
    equipment = Equipment(1, "Прибор")
    user = User(1, "Пользователь")
    bookings = []
    booking = create_booking(bookings, equipment, date(2026, 9, 20), user)

    assert cancel_booking(bookings, booking.id) is True
    assert len(bookings) == 1
    assert bookings[0].is_cancelled is True
    assert bookings[0].status == "Отменено"


def test_is_equipment_available():
    """Проверить функцию проверки доступности оборудования."""
    bookings = []
    equipment = Equipment(1, "Прибор")
    booking_date = date(2026, 9, 15)
    assert is_equipment_available(bookings, equipment, booking_date) is True


def test_duplicate_booking_forbidden():
    """Проверить запрет повторного активного бронирования на одну дату."""
    bookings = []
    equipment = Equipment(1, "Прибор")
    user1 = User(1, "Пользователь 1")
    user2 = User(2, "Пользователь 2")
    booking_date = date(2026, 9, 15)

    create_booking(bookings, equipment, booking_date, user1)
    second_booking = create_booking(bookings, equipment, booking_date, user2)
    assert second_booking is None
    assert is_equipment_available(bookings, equipment, booking_date) is False


def test_cancelled_booking_frees_date():
    """Проверить правило: отмененное бронирование освобождает дату."""
    bookings = []
    equipment = Equipment(1, "Прибор")
    user1 = User(1, "Пользователь 1")
    user2 = User(2, "Пользователь 2")
    booking_date = date(2026, 9, 15)

    booking_1 = create_booking(bookings, equipment, booking_date, user1)
    assert booking_1 is not None

    booking_1.cancel()
    assert booking_1.is_cancelled is True

    assert is_equipment_available(bookings, equipment, booking_date) is True

    booking_2 = create_booking(bookings, equipment, booking_date, user2)
    assert booking_2 is not None
    assert booking_2.id != booking_1.id
    assert len(bookings) == 2


def test_calculate_booking_cost():
    """Проверить расчет стоимости с учетом студенческой скидки 50%."""
    student_cost = calculate_booking_cost(1200.0, 3.0, True)
    staff_cost = calculate_booking_cost(1200.0, 3.0, False)
    assert student_cost == 1800.0
    assert staff_cost == 3600.0


def test_get_booking_statistics():
    """Проверить статистику по активным и общим бронированиям."""
    e1 = Equipment(1, "Прибор 1")
    e2 = Equipment(2, "Прибор 2")
    u = User(1, "Пользователь")

    bookings = [
        Booking(1, e1, date(2026, 9, 10), u, cost=1000.0),
        Booking(2, e2, date(2026, 9, 11), u, cost=1500.0),
        Booking(3, e1, date(2026, 9, 12), u, cost=500.0, is_cancelled=True),
    ]
    stats = get_booking_statistics(bookings)
    assert stats["bookings_count"] == 2
    assert stats["total_bookings"] == 3
    assert stats["unique_equipment"] == 2
    assert stats["total_cost"] == 2500.0


def test_storage_equipment_users_bookings(tmp_path: Path):
    """Проверить сквозное сохранение и загрузку объектов через JSON."""
    eq_file = tmp_path / "equipment.json"
    users_file = tmp_path / "users.json"
    book_file = tmp_path / "bookings.json"

    equipment = [
        Equipment(
            equipment_id=1,
            name="Микроскоп",
            inventory_number="EQ-001",
            operational=True,
            under_maintenance=False,
            required_level=1,
            hourly_rate=500.0,
        )
    ]
    save_equipment(eq_file, equipment)
    loaded_eq = load_equipment(eq_file)
    assert len(loaded_eq) == 1
    assert loaded_eq[0].name == "Микроскоп"

    users = [
        Student(1, "Иванов Алексей", access_level=2, briefing_passed=True)
    ]
    save_users(users_file, users)
    loaded_users = load_users(users_file)
    assert len(loaded_users) == 1
    assert isinstance(loaded_users[0], Student)
    assert loaded_users[0].name == "Иванов Алексей"

    bookings = [
        Booking(
            booking_id=1,
            equipment=loaded_eq[0],
            booking_date=date(2026, 10, 1),
            user=loaded_users[0],
            duration_hours=2.0,
            cost=500.0,
        )
    ]
    save_bookings(book_file, bookings)
    loaded_b = load_bookings(book_file, loaded_eq, loaded_users)
    assert len(loaded_b) == 1
    assert loaded_b[0].booking_date == date(2026, 10, 1)
    assert loaded_b[0].equipment.name == "Микроскоп"
    assert loaded_b[0].user.name == "Иванов Алексей"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
