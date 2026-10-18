from django.shortcuts import render

from models.bookings import find_booking_by_id
from storage import load_bookings, load_equipment, load_users


def bookings(request):
    equipment_items = load_equipment("data/equipment.json")
    users_list = load_users("data/users.json")
    bookings_list = load_bookings(
        "data/bookings.json",
        equipment_items,
        users_list,
    )
    context = {
        "bookings": bookings_list,
    }
    return render(
        request,
        "bookings/booking_list.html",
        context,
    )


def booking_detail(request, booking_id: int):
    equipment_items = load_equipment("data/equipment.json")
    users_list = load_users("data/users.json")
    bookings_list = load_bookings(
        "data/bookings.json",
        equipment_items,
        users_list,
    )
    booking = find_booking_by_id(
        bookings_list,
        booking_id,
    )
    context = {
        "booking": booking,
    }
    return render(
        request,
        "bookings/booking_detail.html",
        context,
        status=404 if booking is None else 200,
    )
