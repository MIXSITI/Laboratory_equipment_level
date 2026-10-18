from django.shortcuts import render

from models.rooms import find_room_by_id
from storage import load_rooms


def rooms(request):
    rooms_list = load_rooms("data/rooms.json")
    context = {
        "rooms": rooms_list,
    }
    return render(
        request,
        "rooms/room_list.html",
        context,
    )


def room_detail(request, room_id: int):
    rooms_list = load_rooms("data/rooms.json")
    room = find_room_by_id(
        rooms_list,
        room_id,
    )
    context = {
        "room": room,
    }
    return render(
        request,
        "rooms/room_detail.html",
        context,
        status=404 if room is None else 200,
    )
