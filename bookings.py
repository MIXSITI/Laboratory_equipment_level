"""Модуль работы с бронированиями (делегирует в models.bookings)."""

from models.bookings import (
    Booking,
    calculate_booking_cost,
    cancel_booking,
    create_booking,
    get_booking_statistics,
    get_booking_status,
    is_equipment_available,
    is_room_available,
    show_bookings,
)

__all__ = [
    "Booking",
    "calculate_booking_cost",
    "cancel_booking",
    "create_booking",
    "get_booking_statistics",
    "get_booking_status",
    "is_equipment_available",
    "is_room_available",
    "show_bookings",
]
