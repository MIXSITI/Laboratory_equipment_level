from django.db.models import Avg, Count, F, Q, Sum
from django.shortcuts import render

from bookings.models import Booking
from rooms.models import Room


def bookings(request):
    bookings_data = (
        Booking.objects
        .filter(is_cancelled=False)
        .annotate(
            room_name=F("room__name"),
            capacity=F("room__capacity"),
            user_name=F("user__name"),
        )
        .values(
            "id",
            "booking_date",
            "room_name",
            "capacity",
            "user_name",
            "is_cancelled",
        )
        .order_by("booking_date")
    )
    return render(
        request,
        "bookings/booking_list.html",
        {"bookings": bookings_data},
    )


booking_list = bookings


def booking_detail(request, booking_id: int):
    try:
        booking = (
            Booking.objects
            .select_related("room", "user")
            .get(pk=booking_id)
        )
    except Booking.DoesNotExist:
        booking = None
    return render(
        request,
        "bookings/booking_detail.html",
        {"booking": booking},
        status=404 if booking is None else 200,
    )


def statistics(request):
    statistics_data = (
        Room.objects
        .annotate(
            bookings_count=Count(
                "bookings",
                filter=Q(bookings__is_cancelled=False),
            ),
            room_name=F("name"),
            room_id=F("id"),
        )
        .values(
            "room_id",
            "room_name",
            "bookings_count",
        )
        .order_by("-bookings_count", "name")
    )

    summary = Booking.objects.filter(is_cancelled=False).aggregate(
        total_bookings=Count("id"),
        total_revenue=Sum("cost"),
        avg_cost=Avg("cost"),
    )

    return render(
        request,
        "bookings/statistics.html",
        {
            "statistics": statistics_data,
            "summary": summary,
        },
    )
