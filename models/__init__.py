"""Пакет models объектной модели предметной области."""

from .bookings import Booking
from .equipment import Equipment
from .users import Staff, Student, User

# Псевдоним Room для совместимости с примером методических указаний
Room = Equipment

__all__ = [
    "Equipment",
    "Room",
    "User",
    "Student",
    "Staff",
    "Booking",
]
