from django.core.paginator import Paginator
from django.db.models import Avg, Count, F, Max, Min, Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from bookings.models import Booking
from rooms.models import Room
from users.models import User

from .forms import BookingFilterForm, BookingForm


def booking_list(request):
    form = BookingFilterForm(
        request.GET or None,
        initial={
            "status": Booking.Status.ACTIVE,
            "sort": "date",
        },
    )
    form_valid = form.is_bound and form.is_valid()

    booking_date = None
    room_id = None
    user_id = None
    role = ""
    status_param = Booking.Status.ACTIVE
    search = ""
    sort = "date"
    error = None

    if form.is_bound:
        if form_valid:
            booking_date = form.cleaned_data.get("date")
            selected_room = form.cleaned_data.get("room")
            selected_user = form.cleaned_data.get("user")
            room_id = selected_room.pk if selected_room else None
            user_id = selected_user.pk if selected_user else None
            role = form.cleaned_data.get("role") or ""
            status_param = (
                form.cleaned_data.get("status") or Booking.Status.ACTIVE
            )
            search = (form.cleaned_data.get("search") or "").strip()
            sort = form.cleaned_data.get("sort") or "date"
        else:
            error = "Проверьте корректность параметров фильтрации."

    if status_param == Booking.Status.CANCELLED:
        bookings_data = Booking.objects.cancelled()
    elif status_param == Booking.Status.COMPLETED:
        bookings_data = Booking.objects.completed()
    elif status_param == "all":
        bookings_data = Booking.objects.all()
    else:
        status_param = Booking.Status.ACTIVE
        bookings_data = Booking.objects.active()

    if form_valid:
        if booking_date:
            bookings_data = bookings_data.for_date(booking_date)
        if room_id:
            bookings_data = bookings_data.filter(room_id=room_id)
        if user_id:
            bookings_data = bookings_data.filter(user_id=user_id)
        if role:
            bookings_data = bookings_data.filter(user__role=role)
        if search:
            bookings_data = bookings_data.filter(
                Q(room__name__icontains=search)
                | Q(user__name__icontains=search)
            )

    bookings_data = bookings_data.annotate(
        room_name=F("room__name"),
        capacity=F("room__capacity"),
        user_name=F("user__name"),
        user_role=F("user__role"),
    )

    sort_fields = {
        "date": "booking_date",
        "room": "room__name",
        "user": "user__name",
        "cost": "-cost",
    }
    sort_field = sort_fields.get(sort, "booking_date")
    bookings_data = bookings_data.order_by(sort_field, "id")

    bookings_data = bookings_data.values(
        "id",
        "booking_date",
        "room_name",
        "capacity",
        "user_name",
        "user_role",
        "cost",
        "status",
    )

    paginator = Paginator(bookings_data, 5)
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "bookings": page_obj,
        "page_obj": page_obj,
        "form": form,
        "booking_date": booking_date,
        "selected_room": room_id,
        "selected_user": user_id,
        "selected_role": role,
        "selected_status": status_param,
        "status_choices": Booking.Status.choices,
        "search_query": search,
        "sort": sort,
        "role_choices": User.ROLE_CHOICES,
        "rooms": Room.objects.order_by("name"),
        "users": User.objects.order_by("name"),
        "error": error,
    }
    return render(request, "bookings/booking_list.html", context)


def booking_detail(request, booking_id: int):
    booking = get_object_or_404(
        Booking.objects.select_related("room", "user"),
        pk=booking_id,
    )
    return render(
        request,
        "bookings/booking_detail.html",
        {"booking": booking},
    )


def booking_create(request):
    if request.method == "POST":
        form = BookingForm(request.POST)
        if form.is_valid():
            room = form.cleaned_data["room"]
            booking_date = form.cleaned_data["booking_date"]
            is_booked = Booking.objects.active().filter(
                room=room,
                booking_date=booking_date,
            ).exists()
            if is_booked:
                form.add_error(
                    None,
                    "Выбранное помещение уже забронировано на эту дату.",
                )
            else:
                booking = form.save(commit=False)
                booking.cost = round(
                    booking.room.hourly_rate * booking.duration_hours,
                    2,
                )
                booking.save()
                return redirect("bookings:bookings")
    else:
        form = BookingForm(
            initial={
                "booking_date": timezone.localdate(),
            }
        )

    return render(
        request,
        "bookings/booking_form.html",
        {"form": form},
    )


def booking_update(request, booking_id: int):
    booking = get_object_or_404(
        Booking.objects.active(),
        pk=booking_id,
    )
    if request.method == "POST":
        form = BookingForm(request.POST, instance=booking)
        if form.is_valid():
            room = form.cleaned_data["room"]
            booking_date = form.cleaned_data["booking_date"]
            is_booked = (
                Booking.objects.active()
                .filter(room=room, booking_date=booking_date)
                .exclude(pk=booking.pk)
                .exists()
            )
            if is_booked:
                form.add_error(
                    None,
                    "Выбранное помещение уже забронировано на эту дату.",
                )
            else:
                updated_booking = form.save(commit=False)
                updated_booking.cost = round(
                    updated_booking.room.hourly_rate
                    * updated_booking.duration_hours,
                    2,
                )
                updated_booking.save()
                return redirect("bookings:bookings")
    else:
        form = BookingForm(instance=booking)

    return render(
        request,
        "bookings/booking_form.html",
        {
            "form": form,
            "booking": booking,
        },
    )


@require_POST
def booking_cancel(request, booking_id: int):
    booking = get_object_or_404(
        Booking.objects.active(),
        pk=booking_id,
    )
    booking.cancel()
    return redirect("bookings:bookings")


def statistics(request):
    statistics_data = (
        Room.objects
        .annotate(
            bookings_count=Count(
                "bookings",
                filter=Q(bookings__status=Booking.Status.ACTIVE),
            ),
            room_revenue=Sum(
                "bookings__cost",
                filter=Q(bookings__status=Booking.Status.ACTIVE),
            ),
            room_name=F("name"),
            room_id=F("id"),
        )
        .values(
            "room_id",
            "room_name",
            "bookings_count",
            "room_revenue",
        )
        .order_by("-bookings_count", "name")
    )

    summary = Booking.objects.aggregate(
        total_bookings=Count("id"),
        active_bookings=Count(
            "id",
            filter=Q(status=Booking.Status.ACTIVE),
        ),
        cancelled_bookings=Count(
            "id",
            filter=Q(status=Booking.Status.CANCELLED),
        ),
        completed_bookings=Count(
            "id",
            filter=Q(status=Booking.Status.COMPLETED),
        ),
        total_revenue=Sum(
            "cost",
            filter=Q(status=Booking.Status.ACTIVE),
        ),
        avg_cost=Avg(
            "cost",
            filter=Q(status=Booking.Status.ACTIVE),
        ),
        min_cost=Min(
            "cost",
            filter=Q(status=Booking.Status.ACTIVE),
        ),
        max_cost=Max(
            "cost",
            filter=Q(status=Booking.Status.ACTIVE),
        ),
    )

    return render(
        request,
        "bookings/statistics.html",
        {
            "statistics": statistics_data,
            "summary": summary,
        },
    )
