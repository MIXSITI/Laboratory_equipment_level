from django.http import HttpResponse

from homepage.views import page
from models.bookings import find_booking_by_id
from storage import load_bookings, load_equipment, load_users


def bookings(request) -> HttpResponse:
    """Отобразить список бронирований."""
    equipment_items = load_equipment("data/equipment.json")
    users_list = load_users("data/users.json")
    bookings_list = load_bookings(
        "data/bookings.json",
        equipment_items,
        users_list,
    )
    items = ""
    for booking in bookings_list:
        status = "отменено" if booking.is_cancelled else "активно"
        badge = "bg-secondary" if booking.is_cancelled else "bg-success"
        eq_name = (
            booking.equipment.name if booking.equipment else "Оборудование"
        )
        items += f"""
<li class="list-group-item d-flex justify-content-between align-items-center">
    <a href="/bookings/{booking.id}/">
        {eq_name} – {booking.booking_date}
    </a>
    <span class="badge {badge}">
        {status}
    </span>
</li>
"""
    content = f"""
<h1>Бронирования оборудования</h1>
<ul class="list-group mb-4">
{items}
</ul>
<a href="/" class="btn btn-outline-secondary">← На главную</a>
"""
    return HttpResponse(
        page("Бронирования", content)
    )


def booking_detail(request, booking_id: int) -> HttpResponse:
    """Отобразить карточку отдельного бронирования."""
    equipment_items = load_equipment("data/equipment.json")
    users_list = load_users("data/users.json")
    bookings_list = load_bookings(
        "data/bookings.json",
        equipment_items,
        users_list,
    )
    booking = find_booking_by_id(
        bookings_list,
        booking_id,
    )
    if booking is None:
        content = """
<h1 class="text-danger">
Бронирование не найдено
</h1>
<p class="lead">Бронирование с указанным номером отсутствует.</p>
<a href="/bookings/"
class="btn btn-outline-secondary">
← к списку бронирований
</a>
"""
        return HttpResponse(
            page("Бронирование не найдено", content),
            status=404,
        )
    status = "отменено" if booking.is_cancelled else "активно"
    badge = "bg-secondary" if booking.is_cancelled else "bg-success"
    eq_name = booking.equipment.name if booking.equipment else "—"
    u_name = booking.user.name if booking.user else "—"
    content = f"""
<div class="card">
<div class="card-body">
<h5 class="card-title">
Бронирование №{booking.id}
</h5>
<p class="card-text">
<strong>Оборудование:</strong> {eq_name}
</p>
<p class="card-text">
<strong>Дата:</strong> {booking.booking_date}
</p>
<p class="card-text">
<strong>Длительность:</strong> {booking.duration_hours} ч.
</p>
<p class="card-text">
<strong>Пользователь:</strong> {u_name}
</p>
<p class="card-text">
<strong>Стоимость:</strong> {booking.cost} руб.
</p>
<p class="card-text">
<strong>Статус:</strong>
<span class="badge {badge}">
{status}
</span>
</p>
<a href="/bookings/"
class="btn btn-outline-secondary">
← к списку бронирований
</a>
</div>
</div>
"""
    return HttpResponse(
        page(
            f"Бронирование №{booking.id}",
            content,
        ),
        status=200,
    )
