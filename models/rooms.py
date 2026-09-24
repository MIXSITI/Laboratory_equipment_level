"""Класс Room и функции для работы с помещениями и оборудованием."""

from collections.abc import Iterator
from typing import Optional


class Room:
    """Помещение или лабораторный прибор для бронирования."""

    def __init__(
        self,
        room_id: int,
        name: str,
        capacity: int = 1,
        inventory_number: str = "",
        operational: bool = True,
        under_maintenance: bool = False,
        required_level: int = 1,
        hourly_rate: float = 0.0,
    ) -> None:
        """Создать объект помещения / оборудования."""
        self.id = room_id
        self.name = name
        self.capacity = capacity
        self.inventory_number = inventory_number
        self.operational = operational
        self.under_maintenance = under_maintenance
        self.required_level = required_level
        self.hourly_rate = hourly_rate

    def is_suitable_for(self, people_count: int) -> bool:
        """Проверить вместимость помещения."""
        return self.capacity >= people_count

    @property
    def is_ready(self) -> bool:
        """Флаг технической готовности оборудования/помещения к работе."""
        return self.operational and not self.under_maintenance

    def check_readiness(self) -> str:
        """Проверить готовность к использованию."""
        if not self.operational:
            return "Оборудование неисправно"
        if self.under_maintenance:
            return "Оборудование на техническом обслуживании"
        return "Оборудование готово к работе"

    def is_suitable_for_level(self, user_level: int) -> bool:
        """Проверить соответствие уровня допуска пользователя."""
        return user_level >= self.required_level

    @staticmethod
    def validate_capacity(capacity: int) -> bool:
        """Проверить корректность вместимости."""
        return capacity > 0

    @staticmethod
    def validate_rate(rate: float) -> bool:
        """Проверить корректность почасовой ставки."""
        return rate >= 0.0

    @staticmethod
    def validate_level(level: int) -> bool:
        """Проверить корректность уровня допуска (от 1 до 3)."""
        return 1 <= level <= 3

    @classmethod
    def from_data(cls, data: dict) -> "Room":
        """Создать объект помещения из набора данных."""
        return cls(
            room_id=int(data.get("id", data.get("room_id", 0))),
            name=str(data.get("name", "")),
            capacity=int(data.get("capacity", 1)),
            inventory_number=str(data.get("inventory_number", "")),
            operational=bool(data.get("operational", True)),
            under_maintenance=bool(data.get("under_maintenance", False)),
            required_level=int(data.get("required_level", 1)),
            hourly_rate=float(data.get("hourly_rate", 0.0)),
        )

    def to_dict(self) -> dict:
        """Преобразовать объект в словарь для сохранения в JSON."""
        return {
            "id": self.id,
            "name": self.name,
            "capacity": self.capacity,
            "inventory_number": self.inventory_number,
            "operational": self.operational,
            "under_maintenance": self.under_maintenance,
            "required_level": self.required_level,
            "hourly_rate": self.hourly_rate,
        }

    def __str__(self) -> str:
        """Вернуть строковое представление помещения."""
        inv = (
            f", инв. {self.inventory_number}"
            if self.inventory_number
            else ""
        )
        return (
            f"[{self.id}] {self.name} "
            f"(вместимость: {self.capacity} чел.{inv}, "
            f"{self.hourly_rate} руб/час)"
        )


# Псевдоним Equipment для обратной совместимости
Equipment = Room


def _get_rooms(collection: list[Room] | dict) -> list[Room]:
    """Вспомогательная функция извлечения списка объектов."""
    if isinstance(collection, dict):
        return list(collection.values())
    return list(collection)


def add_room(
    rooms: list[Room] | dict,
    name: str,
    capacity: int = 1,
    inventory_number: str = "",
    operational: bool = True,
    under_maintenance: bool = False,
    required_level: int = 1,
    hourly_rate: float = 0.0,
) -> Room:
    """Добавить помещение в коллекцию rooms."""
    items = _get_rooms(rooms)
    room_id = max((r.id for r in items), default=0) + 1
    new_room = Room(
        room_id=room_id,
        name=name,
        capacity=capacity,
        inventory_number=inventory_number,
        operational=operational,
        under_maintenance=under_maintenance,
        required_level=required_level,
        hourly_rate=hourly_rate,
    )
    if isinstance(rooms, list):
        rooms.append(new_room)
    elif isinstance(rooms, dict):
        rooms[room_id] = new_room
    return new_room


def find_room(rooms: list[Room] | dict, query: str) -> list[Room]:
    """Найти помещения по подстроке названия или инвентарному номеру."""
    query_lower = query.lower()
    found: list[Room] = []
    for item in _get_rooms(rooms):
        name_match = query_lower in item.name.lower()
        inv_match = query_lower in item.inventory_number.lower()
        if name_match or inv_match:
            found.append(item)
    return found


def check_room_capacity(
    rooms: list[Room] | dict,
    room_id: int,
    min_capacity: int,
) -> bool:
    """Проверить вместимость помещения через метод объекта."""
    room = get_room_by_id(rooms, room_id)
    if room is None:
        return False
    return room.is_suitable_for(min_capacity)


def filter_rooms_by_capacity(
    rooms: list[Room] | dict,
    min_capacity: int,
) -> Iterator[Room]:
    """Отобрать помещения по вместимости через генератор."""
    for item in _get_rooms(rooms):
        if item.capacity >= min_capacity:
            yield item


def filter_rooms_by_level(
    rooms: list[Room] | dict,
    max_level: int,
) -> Iterator[Room]:
    """Отобрать оборудование/помещения по уровню допуска."""
    for item in _get_rooms(rooms):
        if item.required_level <= max_level:
            yield item


def sort_rooms(
    rooms: list[Room] | dict,
    reverse: bool = False,
) -> list[Room]:
    """Отсортировать помещения по вместимости или ставке."""
    return sorted(
        _get_rooms(rooms),
        key=lambda item: (item.hourly_rate, item.capacity),
        reverse=reverse,
    )


def get_room_by_id(
    rooms: list[Room] | dict,
    room_id: Optional[int],
) -> Optional[Room]:
    """Вернуть объект помещения по идентификатору."""
    if room_id is None:
        return None
    for item in _get_rooms(rooms):
        if item.id == room_id:
            return item
    return None


def show_rooms(rooms: list[Room] | dict) -> None:
    """Вывести список помещений в виде таблицы."""
    items = sort_rooms(rooms)
    if not items:
        print("Список помещений пуст.")
        return
    header = (
        f"{'ID':<4}{'Название':<36}{'Инв.№':<10}"
        f"{'Вмест.':<8}{'Ставка':<8}{'Ур.':<4}Статус"
    )
    print()
    print(header)
    print("-" * 86)
    for item in items:
        name = item.name[:34]
        inv = item.inventory_number or "-"
        print(
            f"{item.id:<4}{name:<36}{inv:<10}"
            f"{item.capacity:<8}{item.hourly_rate:<8}{item.required_level:<4}"
            f"{item.check_readiness()}"
        )


def check_equipment_availability(
    operational: bool,
    under_maintenance: bool,
) -> str:
    """Проверить техническую готовность (сохранена из ПР1)."""
    if not operational:
        return "Оборудование неисправно"
    if under_maintenance:
        return "Оборудование на техническом обслуживании"
    return "Оборудование готово к работе"


# Псевдонимы функций для полной совместимости
add_equipment = add_room
find_equipment = find_room
sort_equipment = sort_rooms
get_equipment_by_id = get_room_by_id
show_equipment = show_rooms
filter_equipment_by_level = filter_rooms_by_level
