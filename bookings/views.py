import sqlite3
from typing import Any
from django.shortcuts import render

from db.database import DB_PATH


class BookingRecord:

    def __init__(self, row: sqlite3.Row) -> None:
        self._row = row
        self.id = row["id"]
        self.booking_date = row["booking_date"]
        self.duration_hours = row["duration_hours"]
        self.cost = row["cost"]
        self.is_cancelled = bool(row["is_cancelled"])
        self.room_name = row["room_name"]
        self.capacity = row["capacity"]
        self.user_name = row["user_name"]
        self.room = type("RoomObj", (), {
            "name": row["room_name"],
            "capacity": row["capacity"],
        })()
        self.user = type("UserObj", (), {
            "name": row["user_name"],
        })()

    def __getitem__(self, key: str) -> Any:
        return self._row[key]

    @property
    def status(self) -> str:
        return "Отменено" if self.is_cancelled else "Активно"


def bookings(request):
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    rows = conn.execute("""
        SELECT
            bookings.id,
            bookings.booking_date,
            bookings.duration_hours,
            bookings.cost,
            bookings.is_cancelled,
            rooms.name AS room_name,
            rooms.capacity,
            users.name AS user_name
        FROM bookings
        JOIN rooms ON bookings.room_id = rooms.id
        JOIN users ON bookings.user_id = users.id
        WHERE bookings.is_cancelled = 0
        ORDER BY bookings.booking_date;
    """).fetchall()
    conn.close()

    bookings_data = [BookingRecord(row) for row in rows]
    return render(
        request,
        "bookings/booking_list.html",
        {"bookings": bookings_data},
    )


def booking_detail(request, booking_id: int):
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    row = conn.execute("""
        SELECT
            bookings.id,
            bookings.booking_date,
            bookings.duration_hours,
            bookings.cost,
            bookings.is_cancelled,
            rooms.name AS room_name,
            rooms.capacity,
            users.name AS user_name
        FROM bookings
        JOIN rooms ON bookings.room_id = rooms.id
        JOIN users ON bookings.user_id = users.id
        WHERE bookings.id = ?;
    """, [booking_id]).fetchone()
    conn.close()

    booking = BookingRecord(row) if row is not None else None
    return render(
        request,
        "bookings/booking_detail.html",
        {"booking": booking},
        status=404 if booking is None else 200,
    )


def statistics(request):
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    statistics_data = conn.execute("""
        SELECT
            rooms.id AS room_id,
            rooms.name AS room_name,
            COUNT(bookings.id) AS bookings_count
        FROM rooms
        LEFT JOIN bookings ON rooms.id = bookings.room_id
                           AND bookings.is_cancelled = 0
        GROUP BY rooms.id, rooms.name
        ORDER BY bookings_count DESC, rooms.name ASC;
    """).fetchall()

    summary = conn.execute("""
        SELECT
            COUNT(*) AS total_bookings,
            SUM(cost) AS total_revenue,
            AVG(cost) AS avg_cost
        FROM bookings
        WHERE is_cancelled = 0;
    """).fetchone()

    conn.close()
    return render(
        request,
        "bookings/statistics.html",
        {
            "statistics": statistics_data,
            "summary": summary,
        },
    )
