from datetime import datetime

from django.shortcuts import render

from bookings.models import Booking
from rooms.models import Room


def rooms(request):
    rooms_list = Room.objects.order_by("name")
    return render(
        request,
        "rooms/room_list.html",
        {"rooms": rooms_list},
    )


def room_detail(request, room_id: int):
    try:
        room = Room.objects.get(pk=room_id)
    except Room.DoesNotExist:
        room = None
    return render(
        request,
        "rooms/room_detail.html",
        {"room": room},
        status=404 if room is None else 200,
    )


def available_rooms(request):
    booking_date = request.GET.get("date", "").strip()
    rooms_list = []
    error = None

    if booking_date:
        try:
            selected_date = datetime.strptime(
                booking_date,
                "%Y-%m-%d",
            ).date()
        except ValueError:
            error = "Укажите корректную дату."
        else:
            booked_room_ids = Booking.objects.filter(
                booking_date=selected_date,
                is_cancelled=False,
            ).values_list(
                "room_id",
                flat=True,
            )
            rooms_list = Room.objects.exclude(
                pk__in=booked_room_ids,
            ).order_by("name")

    context = {
        "rooms": rooms_list,
        "booking_date": booking_date,
        "error": error,
    }
    return render(
        request,
        "rooms/available.html",
        context,
    )
