"""Представления приложения для работы с лабораторным оборудованием."""

from datetime import date

from django.http import HttpResponse

from homepage.views import page
from models.bookings import is_equipment_available
from models.equipment import find_equipment_by_id
from storage import load_bookings, load_equipment, load_users


def equipment_list(request) -> HttpResponse:
    """Отобразить список лабораторного оборудования."""
    equipment_items = load_equipment("data/equipment.json")
    items = ""
    for item in equipment_items:
        inv = f" ({item.inventory_number})" if item.inventory_number else ""
        text = (
            f"{item.name}{inv} – ставка {item.hourly_rate} руб/час, "
            f"допуск: ур. {item.required_level}"
        )
        badge = "bg-success" if item.is_ready else "bg-warning text-dark"
        status_text = "готов" if item.is_ready else "ТО / ремонт"
        items += (
            f'<li class="list-group-item d-flex justify-content-between '
            f'align-items-center">'
            f'<a href="/equipment/{item.id}/">{text}</a>'
            f'<span class="badge {badge}">{status_text}</span>'
            f'</li>'
        )
    content = f"""
<h1>Лабораторное оборудование</h1>
<ul class="list-group mb-4">{items}</ul>
<a href="/" class="btn btn-outline-secondary">← На главную</a>
"""
    return HttpResponse(page("Лабораторное оборудование", content))


def equipment_detail(request, equipment_id: int) -> HttpResponse:
    """Отобразить детальную информацию о лабораторном оборудовании."""
    equipment_items = load_equipment("data/equipment.json")
    item = find_equipment_by_id(equipment_items, equipment_id)
    if item is None:
        content = """
<h1 class="text-danger">Оборудование не найдено</h1>
<p class="lead">Прибор с указанным ID не зарегистрирован в системе.</p>
<a href="/equipment/" class="btn btn-outline-secondary">
← к списку оборудования
</a>
"""
        return HttpResponse(
            page("Оборудование не найдено", content),
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
    status_avail = "доступно" if available else "занято"
    badge_avail = "bg-success" if available else "bg-danger"

    readiness = item.check_readiness()
    badge_ready = (
        "bg-success" if item.is_ready else "bg-warning text-dark"
    )

    inv = item.inventory_number or "—"
    content = f"""
<div class="card">
<div class="card-body">
<h5 class="card-title">{item.name}</h5>
<p class="card-text">
<strong>ID:</strong> {item.id}
</p>
<p class="card-text">
<strong>Инвентарный номер:</strong> {inv}
</p>
<p class="card-text">
<strong>Почасовая ставка:</strong> {item.hourly_rate} руб/час
</p>
<p class="card-text">
<strong>Требуемый уровень допуска:</strong> Уровень {item.required_level}
</p>
<p class="card-text">
<strong>Техническое состояние:</strong>
<span class="badge {badge_ready}">{readiness}</span>
</p>
<p class="card-text">
Доступность на текущую дату:
<span class="badge {badge_avail}">
{status_avail}
</span>
</p>
<a href="/equipment/" class="btn btn-outline-secondary">
← к списку оборудования
</a>
</div>
</div>
"""
    return HttpResponse(
        page(item.name, content),
        status=200,
    )


# Псевдонимы
equipment = equipment_list
