from datetime import date
from pathlib import Path

from bookings import (
    calculate_booking_cost,
    cancel_booking,
    create_booking,
    get_booking_statistics,
    is_equipment_available,
)
from storage import (
    load_bookings,
    load_equipment,
    save_bookings,
    save_equipment,
)


def test_is_equipment_available():
    bookings = []
    booking_date = date(2026, 9, 15)
    assert is_equipment_available(bookings, 1, booking_date)


def test_duplicate_booking_forbidden():
    bookings = []
    booking_date = date(2026, 9, 15)
    create_booking(bookings, 1, booking_date)
    assert not is_equipment_available(bookings, 1, booking_date)


def test_cancel_booking():
    bookings = []
    booking = create_booking(bookings, 1, date(2026, 9, 20))
    assert cancel_booking(bookings, booking["id"])
    assert bookings == []


def test_calculate_booking_cost():
    student_cost = calculate_booking_cost(1200, 3, True)
    staff_cost = calculate_booking_cost(1200, 3, False)
    assert student_cost == 1800.0
    assert staff_cost == 3600.0


def test_get_booking_statistics():
    bookings = [
        {"equipment_id": 1, "cost": 1000.0},
        {"equipment_id": 2, "cost": 1500.0},
        {"equipment_id": 1, "cost": 500.0},
    ]
    stats = get_booking_statistics(bookings)
    assert stats["bookings_count"] == 3
    assert stats["unique_equipment"] == 2
    assert stats["total_cost"] == 3000.0


def test_storage_equipment_and_bookings(tmp_path: Path):
    eq_file = tmp_path / "equipment.json"
    book_file = tmp_path / "bookings.json"

    equipment = {
        1: {
            "id": 1,
            "name": "Микроскоп",
            "inventory_number": "EQ-001",
            "operational": True,
            "under_maintenance": False,
            "required_level": 1,
            "hourly_rate": 500.0,
        }
    }
    save_equipment(eq_file, equipment)
    loaded_eq = load_equipment(eq_file)
    assert len(loaded_eq) == 1
    assert loaded_eq[1]["name"] == "Микроскоп"

    bookings = [
        {
            "id": 1,
            "equipment_id": 1,
            "booking_date": date(2026, 10, 1),
            "duration_hours": 2.0,
            "cost": 1000.0,
        }
    ]
    save_bookings(book_file, bookings)
    loaded_b = load_bookings(book_file)
    assert len(loaded_b) == 1
    assert loaded_b[0]["booking_date"] == date(2026, 10, 1)
