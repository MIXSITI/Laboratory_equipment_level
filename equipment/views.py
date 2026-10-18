from datetime import date

from django.shortcuts import render

from models.bookings import is_equipment_available
from models.equipment import find_equipment_by_id
from storage import load_bookings, load_equipment, load_users


def equipment_list(request):
    equipment_items = load_equipment("data/equipment.json")
    context = {
        "equipment_items": equipment_items,
    }
    return render(
        request,
        "equipment/equipment_list.html",
        context,
    )


def equipment_detail(request, equipment_id: int):
    equipment_items = load_equipment("data/equipment.json")
    item = find_equipment_by_id(equipment_items, equipment_id)
    if item is None:
        return render(
            request,
            "equipment/equipment_detail.html",
            {"item": None},
            status=404,
        )

    users_list = load_users("data/users.json")
    bookings_list = load_bookings(
        "data/bookings.json",
        equipment_items,
        users_list,
    )
    available = is_equipment_available(
        bookings_list,
        item,
        date.today(),
    )
    context = {
        "item": item,
        "available": available,
        "readiness": item.check_readiness(),
    }
    return render(
        request,
        "equipment/equipment_detail.html",
        context,
        status=200,
    )


equipment = equipment_list
