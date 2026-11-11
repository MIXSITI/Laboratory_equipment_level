from datetime import date, datetime

from django.db.models import Q
from django.shortcuts import get_object_or_404, render

from bookings.models import Booking
from rooms.models import Room


def rooms(request):
    query = request.GET.get("q", "").strip()
    min_capacity = request.GET.get("capacity", "").strip()
    only_ready = request.GET.get("ready") == "1"

    rooms_list = Room.objects.all()

    if query:
        rooms_list = rooms_list.filter(
            Q(name__icontains=query) | Q(inventory_number__icontains=query)
        )

    if min_capacity.isdigit():
        rooms_list = rooms_list.filter(capacity__gte=int(min_capacity))

    if only_ready:
        rooms_list = rooms_list.filter(
            operational=True,
            under_maintenance=False,
        )

    rooms_list = rooms_list.order_by("name")

    context = {
        "rooms": rooms_list,
        "search_query": query,
        "min_capacity": min_capacity,
        "only_ready": only_ready,
    }
    return render(
        request,
        "rooms/room_list.html",
        context,
    )


def room_detail(request, room_id: int):
    room = get_object_or_404(Room, pk=room_id)
    room_bookings = (
        room.bookings
        .filter(is_cancelled=False)
        .select_related("user")
        .order_by("booking_date", "pk")[:5]
    )
    is_booked_today = room.bookings.filter(
        booking_date=date.today(),
        is_cancelled=False,
    ).exists()
    context = {
        "room": room,
        "room_bookings": room_bookings,
        "available_today": room.is_ready and not is_booked_today,
        "readiness": room.check_readiness(),
    }
    return render(
        request,
        "rooms/room_detail.html",
        context,
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
            rooms_list = (
                Room.objects
                .filter(operational=True, under_maintenance=False)
                .exclude(pk__in=booked_room_ids)
                .order_by("name")
            )

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
