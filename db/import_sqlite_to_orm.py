import os
import sqlite3
import sys
from datetime import date
from pathlib import Path

import django
from django.db import transaction

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

SOURCE_DB = BASE_DIR / "data" / "roomly.sqlite"

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "roomly.settings")
django.setup()

from bookings.models import Booking  # noqa: E402
from rooms.models import Room  # noqa: E402
from users.models import User  # noqa: E402


def main() -> None:
    if not SOURCE_DB.exists():
        raise FileNotFoundError(f"Исходная база не найдена: {SOURCE_DB}")

    with sqlite3.connect(SOURCE_DB) as connection:
        connection.row_factory = sqlite3.Row

        rooms = connection.execute(
            """
            SELECT
                id,
                name,
                inventory_number,
                capacity,
                operational,
                under_maintenance,
                required_level,
                hourly_rate
            FROM rooms
            ORDER BY id
            """
        ).fetchall()

        users = connection.execute(
            """
            SELECT
                id,
                name,
                email,
                role,
                access_level,
                briefing_passed
            FROM users
            ORDER BY id
            """
        ).fetchall()

        bookings = connection.execute(
            """
            SELECT
                id,
                room_id,
                user_id,
                booking_date,
                duration_hours,
                cost,
                is_cancelled
            FROM bookings
            ORDER BY id
            """
        ).fetchall()

        with transaction.atomic():
            for row in rooms:
                Room.objects.update_or_create(
                    pk=row["id"],
                    defaults={
                        "name": row["name"],
                        "inventory_number": row["inventory_number"] or "",
                        "capacity": row["capacity"],
                        "operational": bool(row["operational"]),
                        "under_maintenance": bool(row["under_maintenance"]),
                        "required_level": row["required_level"],
                        "hourly_rate": row["hourly_rate"],
                    },
                )

            for row in users:
                User.objects.update_or_create(
                    pk=row["id"],
                    defaults={
                        "name": row["name"],
                        "email": row["email"],
                        "role": row["role"],
                        "access_level": row["access_level"],
                        "briefing_passed": bool(row["briefing_passed"]),
                    },
                )

            for row in bookings:
                booking_date = date.fromisoformat(row["booking_date"])
                Booking.objects.update_or_create(
                    pk=row["id"],
                    defaults={
                        "room_id": row["room_id"],
                        "user_id": row["user_id"],
                        "booking_date": booking_date,
                        "duration_hours": row["duration_hours"],
                        "cost": row["cost"],
                        "is_cancelled": bool(row["is_cancelled"]),
                    },
                )

    print("Перенос данных завершён.")
    print(f"Комнат: {Room.objects.count()}")
    print(f"Пользователей: {User.objects.count()}")
    print(f"Бронирований: {Booking.objects.count()}")


if __name__ == "__main__":
    main()
