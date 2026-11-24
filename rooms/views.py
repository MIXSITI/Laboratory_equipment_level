from datetime import datetime

from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.generic import DetailView

from bookings.models import Booking
from roomly.utils import DataMixin
from rooms.models import Room

from .forms import RoomForm


def rooms(request):
    query = request.GET.get("q", "").strip()
    min_capacity = request.GET.get("capacity", "").strip()
    only_ready = request.GET.get("ready") == "1"
    sort_by = request.GET.get("sort", "name").strip()
    direction = request.GET.get("direction", "asc").strip()

    rooms_list = Room.objects.all()

    if query:
        condition = (
            Q(name__icontains=query) | Q(inventory_number__icontains=query)
        )
        if query.isdigit():
            condition |= Q(capacity=int(query))
        rooms_list = rooms_list.filter(condition)

    if min_capacity.isdigit():
        rooms_list = rooms_list.filter(capacity__gte=int(min_capacity))

    if only_ready:
        rooms_list = rooms_list.filter(
            operational=True,
            under_maintenance=False,
        )

    allowed_sort_fields = {
        "name": "name",
        "capacity": "capacity",
    }
    sort_field = allowed_sort_fields.get(sort_by, "name")
    if sort_by not in allowed_sort_fields:
        sort_by = "name"
    if direction == "desc":
        sort_field = f"-{sort_field}"
    else:
        direction = "asc"

    rooms_list = rooms_list.order_by(sort_field, "id")

    context = {
        "rooms": rooms_list,
        "search_query": query,
        "min_capacity": min_capacity,
        "only_ready": only_ready,
        "sort_by": sort_by,
        "direction": direction,
    }
    return render(
        request,
        "rooms/room_list.html",
        context,
    )


class RoomDetailView(DataMixin, DetailView):
    model = Room
    template_name = "rooms/room_detail.html"
    context_object_name = "room"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        room = self.object
        room_bookings = (
            room.bookings
            .active()
            .select_related("user")
            .order_by("booking_date", "pk")[:5]
        )
        is_booked_today = (
            room.bookings
            .active()
            .for_date(timezone.localdate())
            .exists()
        )
        return self.get_mixin_context(
            context,
            title=f"Помещение: {room.name}",
            room_bookings=room_bookings,
            available_today=room.is_ready and not is_booked_today,
            readiness=room.check_readiness(),
        )


def room_detail_by_id(request, room_id: int):
    room = get_object_or_404(Room, pk=room_id)
    return redirect(room.get_absolute_url())


def room_create(request):
    if request.method == "POST":
        form = RoomForm(request.POST, request.FILES)
        if form.is_valid():
            room = form.save()
            return redirect(room.get_absolute_url())
    else:
        form = RoomForm()

    return render(
        request,
        "rooms/room_form.html",
        {"form": form},
    )


def room_update(request, slug: str):
    room = get_object_or_404(Room, slug=slug)
    if request.method == "POST":
        form = RoomForm(request.POST, request.FILES, instance=room)
        if form.is_valid():
            room = form.save()
            return redirect(room.get_absolute_url())
    else:
        form = RoomForm(instance=room)

    return render(
        request,
        "rooms/room_form.html",
        {
            "form": form,
            "room": room,
        },
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
            booked_room_ids = (
                Booking.objects
                .active()
                .for_date(selected_date)
                .values_list("room_id", flat=True)
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
