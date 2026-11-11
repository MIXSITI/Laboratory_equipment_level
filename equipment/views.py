from datetime import date

from django.db.models import Q
from django.shortcuts import get_object_or_404, render

from bookings.models import Booking
from rooms.models import Room


def equipment_list(request):
    query = request.GET.get("q", "").strip()
    level = request.GET.get("level", "").strip()
    only_ready = request.GET.get("ready") == "1"

    equipment_items = Room.objects.all()

    if query:
        equipment_items = equipment_items.filter(
            Q(name__icontains=query) | Q(inventory_number__icontains=query)
        )

    if level.isdigit():
        equipment_items = equipment_items.filter(
            required_level__lte=int(level),
        )

    if only_ready:
        equipment_items = equipment_items.filter(
            operational=True,
            under_maintenance=False,
        )

    equipment_items = equipment_items.order_by("name")

    context = {
        "equipment_items": equipment_items,
        "search_query": query,
        "selected_level": level,
        "only_ready": only_ready,
    }
    return render(
        request,
        "equipment/equipment_list.html",
        context,
    )


def equipment_detail(request, equipment_id: int):
    item = get_object_or_404(Room, pk=equipment_id)
    is_booked_today = Booking.objects.filter(
        room=item,
        booking_date=date.today(),
        is_cancelled=False,
    ).exists()
    available = item.is_ready and not is_booked_today
    context = {
        "item": item,
        "available": available,
        "readiness": item.check_readiness(),
    }
    return render(
        request,
        "equipment/equipment_detail.html",
        context,
    )


equipment = equipment_list
