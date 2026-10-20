import json
import sqlite3
from pathlib import Path
from typing import Any

from db.database import get_connection

BASE_DIR = Path(__file__).resolve().parent.parent
ROOMS_FILE = BASE_DIR / "data" / "rooms.json"
EQUIPMENT_FILE = BASE_DIR / "data" / "equipment.json"
USERS_FILE = BASE_DIR / "data" / "users.json"
BOOKINGS_FILE = BASE_DIR / "data" / "bookings.json"


def load_json(filename: Path | str) -> list[dict[str, Any]]:
    path = Path(filename)
    if not path.exists():
        return []
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def import_rooms(conn: sqlite3.Connection) -> None:
    source_file = ROOMS_FILE if ROOMS_FILE.exists() else EQUIPMENT_FILE
    rooms = load_json(source_file)
    conn.executemany(
        """
        INSERT INTO rooms (
            id,
            name,
            inventory_number,
            capacity,
            operational,
            under_maintenance,
            required_level,
            hourly_rate
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                int(room["id"]),
                str(room["name"]),
                str(room.get("inventory_number", "")),
                int(room.get("capacity", 1)),
                1 if room.get("operational", True) else 0,
                1 if room.get("under_maintenance", False) else 0,
                int(room.get("required_level", 1)),
                float(room.get("hourly_rate", 0.0)),
            )
            for room in rooms
        ],
    )


def import_users(conn: sqlite3.Connection) -> None:
    users = load_json(USERS_FILE)
    conn.executemany(
        """
        INSERT INTO users (
            id,
            name,
            email,
            role,
            access_level,
            briefing_passed
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        [
            (
                int(user["id"]),
                str(user["name"]),
                str(user.get("email") or f"user{user['id']}@example.com"),
                str(user.get("role", "студент")),
                int(user.get("access_level", 1)),
                1 if user.get("briefing_passed", True) else 0,
            )
            for user in users
        ],
    )


def import_bookings(conn: sqlite3.Connection) -> None:
    bookings = load_json(BOOKINGS_FILE)
    conn.executemany(
        """
        INSERT INTO bookings (
            id,
            room_id,
            equipment_id,
            user_id,
            booking_date,
            duration_hours,
            cost,
            is_cancelled
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                int(booking["id"]),
                int(booking.get("room_id", booking.get("equipment_id", 1))),
                int(booking.get("equipment_id", booking.get("room_id", 1))),
                int(booking.get("user_id", 1)),
                str(booking["booking_date"]),
                float(booking.get("duration_hours", 1.0)),
                float(booking.get("cost", 0.0)),
                1 if booking.get("is_cancelled", False) else 0,
            )
            for booking in bookings
        ],
    )


def main() -> None:
    conn = get_connection()
    try:
        conn.execute("DELETE FROM bookings;")
        conn.execute("DELETE FROM users;")
        conn.execute("DELETE FROM rooms;")
        import_rooms(conn)
        import_users(conn)
        import_bookings(conn)
        conn.commit()
        print("Импорт данных из JSON в SQLite успешно завершён.")
    except Exception as exc:
        conn.rollback()
        print(f"Ошибка при импорте данных: {exc}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()
