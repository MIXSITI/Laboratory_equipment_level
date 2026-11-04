from datetime import datetime

from django.core.paginator import Paginator
from django.db.models import Avg, Count, F, Q, Sum
from django.shortcuts import render

from bookings.models import Booking
from rooms.models import Room
from users.models import User


def booking_list(request):
    booking_date = request.GET.get("date", "").strip()
    room_id = request.GET.get("room", "").strip()
    user_id = request.GET.get("user", "").strip()
    sort = request.GET.get("sort", "date").strip()
    error = None

    bookings_data = Booking.objects.filter(is_cancelled=False)

    if booking_date:
        try:
            selected_date = datetime.strptime(
                booking_date,
                "%Y-%m-%d",
            ).date()
        except ValueError:
            error = "Укажите корректную дату."
        else:
            bookings_data = bookings_data.filter(
                booking_date=selected_date,
            )

    if room_id.isdigit():
        bookings_data = bookings_data.filter(room_id=int(room_id))
    if user_id.isdigit():
        bookings_data = bookings_data.filter(user_id=int(user_id))

    bookings_data = bookings_data.annotate(
        room_name=F("room__name"),
        capacity=F("room__capacity"),
        user_name=F("user__name"),
    )

    sort_fields = {
        "date": "booking_date",
        "room": "room__name",
        "user": "user__name",
    }
    sort_field = sort_fields.get(sort, "booking_date")
    bookings_data = bookings_data.order_by(sort_field, "id")

    bookings_data = bookings_data.values(
        "id",
        "booking_date",
        "room_name",
        "capacity",
        "user_name",
        "is_cancelled",
    )

    paginator = Paginator(bookings_data, 5)
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "bookings": page_obj,
        "page_obj": page_obj,
        "booking_date": booking_date,
        "selected_room": room_id,
        "selected_user": user_id,
        "sort": sort,
        "rooms": Room.objects.order_by("name"),
        "users": User.objects.order_by("name"),
        "error": error,
    }
    return render(request, "bookings/booking_list.html", context)


bookings = booking_list


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
