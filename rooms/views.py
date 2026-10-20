import sqlite3
from django.shortcuts import render

from db.database import DB_PATH


def rooms(request):
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    rooms_list = conn.execute("""
        SELECT
            id,
            name,
            capacity,
            inventory_number,
            hourly_rate
        FROM rooms
        ORDER BY name;
    """).fetchall()
    conn.close()
    return render(
        request,
        "rooms/room_list.html",
        {"rooms": rooms_list},
    )


def room_detail(request, room_id: int):
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    room = conn.execute("""
        SELECT
            id,
            name,
            capacity,
            inventory_number,
            hourly_rate
        FROM rooms
        WHERE id = ?;
    """, [room_id]).fetchone()
    conn.close()
    return render(
        request,
        "rooms/room_detail.html",
        {"room": room},
        status=404 if room is None else 200,
    )


def available_rooms(request):
    booking_date = request.GET.get("date")
    rooms_data = []
    if booking_date:
        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row
        rooms_data = conn.execute("""
            SELECT
                rooms.id,
                rooms.name,
                rooms.capacity,
                rooms.hourly_rate
            FROM rooms
            WHERE rooms.id NOT IN (
                SELECT bookings.room_id
                FROM bookings
                WHERE bookings.booking_date = ?
                  AND bookings.is_cancelled = 0
            )
            ORDER BY rooms.name;
        """, [booking_date]).fetchall()
        conn.close()
    return render(
        request,
        "rooms/available.html",
        {
            "rooms": rooms_data,
            "booking_date": booking_date,
        },
    )
