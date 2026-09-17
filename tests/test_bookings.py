from datetime import date

from bookings import (
    calculate_booking_cost,
    cancel_booking,
    create_booking,
    is_equipment_available,
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
