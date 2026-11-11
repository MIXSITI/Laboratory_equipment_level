from django.shortcuts import render

from bookings.models import Booking
from rooms.models import Room


def index(request):
    featured_rooms = (
        Room.objects
        .filter(operational=True, under_maintenance=False)
        .order_by("name")[:3]
    )
    recent_bookings = (
        Booking.objects
        .filter(is_cancelled=False)
        .select_related("room", "user")
        .order_by("booking_date", "pk")[:3]
    )
    context = {
        "featured_rooms": featured_rooms,
        "recent_bookings": recent_bookings,
    }
    return render(
        request,
        "homepage/index.html",
        context,
    )


def page_not_found(request, exception):
    return render(
        request,
        "404.html",
        status=404,
    )
