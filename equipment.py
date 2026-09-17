from collections.abc import Iterator


def add_equipment(
    equipment: dict[int, dict],
    name: str,
    inventory_number: str = "",
    operational: bool = True,
    under_maintenance: bool = False,
    required_level: int = 1,
    hourly_rate: float = 0.0,
) -> None:
    equipment_id = max(equipment.keys(), default=0) + 1
    equipment[equipment_id] = {
        "id": equipment_id,
        "name": name,
        "inventory_number": inventory_number,
        "operational": operational,
        "under_maintenance": under_maintenance,
        "required_level": required_level,
        "hourly_rate": hourly_rate,
    }


def find_equipment(equipment: dict[int, dict], query: str) -> list[dict]:
    query_lower = query.lower()
    found = []
    for item in equipment.values():
        name_match = query_lower in item.get("name", "").lower()
        inv_match = query_lower in item.get("inventory_number", "").lower()
        if name_match or inv_match:
            found.append(item)
    return found


def check_equipment_availability(
    operational: bool,
    under_maintenance: bool,
) -> str:
    if not operational:
        return "Оборудование неисправно"
    if under_maintenance:
        return "Оборудование на техническом обслуживании"
    return "Оборудование готово к работе"


def filter_equipment_by_level(
    equipment: dict[int, dict],
    max_level: int,
) -> Iterator[dict]:
    for item in equipment.values():
        if item["required_level"] <= max_level:
            yield item


def sort_equipment(
    equipment: dict[int, dict],
    reverse: bool = False,
) -> list[dict]:
    return sorted(
        equipment.values(),
        key=lambda item: item["hourly_rate"],
        reverse=reverse,
    )


def get_equipment_by_id(
    equipment: dict[int, dict],
    equipment_id: int,
) -> dict | None:
    return equipment.get(equipment_id)
