from .models import Room


def room_context(request):
    rooms_count = Room.objects.count()
    return {
        "site_name": "Roomly",
        "rooms_count": rooms_count,
    }
