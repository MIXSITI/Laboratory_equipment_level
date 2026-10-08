from collections.abc import Iterator
from typing import Optional


class Equipment:

    def __init__(
        self,
        equipment_id: int,
        name: str,
        inventory_number: str = "",
        operational: bool = True,
        under_maintenance: bool = False,
        required_level: int = 1,
        hourly_rate: float = 0.0,
        capacity: int = 1,
    ) -> None:
        self.id = equipment_id
        self.name = name
        self.inventory_number = inventory_number
        self.operational = operational
        self.under_maintenance = under_maintenance
        self.required_level = required_level
        self.hourly_rate = hourly_rate
        self.capacity = capacity

    @property
    def is_ready(self) -> bool:
        return self.operational and not self.under_maintenance

    def check_readiness(self) -> str:
        if not self.operational:
            return "Оборудование неисправно"
        if self.under_maintenance:
            return "Оборудование на техническом обслуживании"
        return "Оборудование готово к работе"

    def is_suitable_for_level(self, user_level: int) -> bool:
        return user_level >= self.required_level

    def is_suitable_for(self, people_count: int) -> bool:
        return self.capacity >= people_count

    @staticmethod
    def validate_rate(rate: float) -> bool:
        return rate >= 0.0

    @staticmethod
    def validate_level(level: int) -> bool:
        return 1 <= level <= 3

    @classmethod
    def from_data(cls, data: dict) -> "Equipment":
        return cls(
            equipment_id=int(data.get("id", data.get("equipment_id", 0))),
            name=str(data.get("name", "")),
            inventory_number=str(data.get("inventory_number", "")),
            operational=bool(data.get("operational", True)),
            under_maintenance=bool(data.get("under_maintenance", False)),
            required_level=int(data.get("required_level", 1)),
            hourly_rate=float(data.get("hourly_rate", 0.0)),
            capacity=int(data.get("capacity", 1)),
        )

    def to_dict(self) -> dict:
        res = {
            "id": self.id,
            "name": self.name,
            "inventory_number": self.inventory_number,
            "operational": self.operational,
            "under_maintenance": self.under_maintenance,
            "required_level": self.required_level,
            "hourly_rate": self.hourly_rate,
        }
        if self.capacity > 1:
            res["capacity"] = self.capacity
        return res

    def __str__(self) -> str:
        inv = (
            f", инв. {self.inventory_number}"
            if self.inventory_number
            else ""
        )
        return (
            f"[{self.id}] {self.name}{inv} "
            f"({self.hourly_rate} руб/час, допуск: {self.required_level}, "
            f"статус: {self.check_readiness()})"
        )


Room = Equipment


def _get_equipment_list(
    collection: list[Equipment] | dict,
) -> list[Equipment]:
    if isinstance(collection, dict):
        return list(collection.values())
    return list(collection)


def add_equipment(
    equipment: list[Equipment] | dict,
    name: str,
    inventory_number: str = "",
    operational: bool = True,
    under_maintenance: bool = False,
    required_level: int = 1,
    hourly_rate: float = 0.0,
    capacity: int = 1,
) -> Equipment:
    items = _get_equipment_list(equipment)
    eq_id = max((item.id for item in items), default=0) + 1
    new_item = Equipment(
        equipment_id=eq_id,
        name=name,
        inventory_number=inventory_number,
        operational=operational,
        under_maintenance=under_maintenance,
        required_level=required_level,
        hourly_rate=hourly_rate,
        capacity=capacity,
    )
    if isinstance(equipment, list):
        equipment.append(new_item)
    elif isinstance(equipment, dict):
        equipment[eq_id] = new_item
    return new_item


def find_equipment(
    equipment: list[Equipment] | dict,
    query: str,
) -> list[Equipment]:
    query_lower = query.lower()
    found: list[Equipment] = []
    for item in _get_equipment_list(equipment):
        name_match = query_lower in item.name.lower()
        inv_match = query_lower in item.inventory_number.lower()
        if name_match or inv_match:
            found.append(item)
    return found


def filter_equipment_by_level(
    equipment: list[Equipment] | dict,
    max_level: int,
) -> Iterator[Equipment]:
    for item in _get_equipment_list(equipment):
        if item.required_level <= max_level:
            yield item


def sort_equipment(
    equipment: list[Equipment] | dict,
    reverse: bool = False,
) -> list[Equipment]:
    return sorted(
        _get_equipment_list(equipment),
        key=lambda item: item.hourly_rate,
        reverse=reverse,
    )


def get_equipment_by_id(
    equipment: list[Equipment] | dict,
    equipment_id: Optional[int],
) -> Optional[Equipment]:
    if equipment_id is None:
        return None
    for item in _get_equipment_list(equipment):
        if item.id == equipment_id:
            return item
    return None


def show_equipment(equipment: list[Equipment] | dict) -> None:
    items = sort_equipment(equipment)
    if not items:
        print("Список оборудования пуст.")
        return
    header = (
        f"{'ID':<4}{'Название':<36}{'Инв.№':<10}"
        f"{'Ставка':<8}{'Ур.':<4}Статус"
    )
    print()
    print(header)
    print("-" * 80)
    for item in items:
        name = item.name[:34]
        inv = item.inventory_number or "-"
        print(
            f"{item.id:<4}{name:<36}{inv:<10}"
            f"{item.hourly_rate:<8}{item.required_level:<4}"
            f"{item.check_readiness()}"
        )


def check_equipment_availability(
    operational: bool,
    under_maintenance: bool,
) -> str:
    if not operational:
        return "Оборудование неисправно"
    if under_maintenance:
        return "Оборудование на техническом обслуживании"
    return "Оборудование готово к работе"


add_room = add_equipment
find_room = find_equipment
sort_rooms = sort_equipment
get_room_by_id = get_equipment_by_id
find_equipment_by_id = get_equipment_by_id
find_room_by_id = get_equipment_by_id
show_rooms = show_equipment
filter_rooms_by_level = filter_equipment_by_level
