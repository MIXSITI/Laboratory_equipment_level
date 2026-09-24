"""Класс оборудования и функции работы с лабораторными приборами."""

from collections.abc import Iterator
from typing import Optional


class Equipment:
    """Оборудование учебно-научной лаборатории."""

    def __init__(
        self,
        equipment_id: int,
        name: str,
        inventory_number: str = "",
        operational: bool = True,
        under_maintenance: bool = False,
        required_level: int = 1,
        hourly_rate: float = 0.0,
    ) -> None:
        """Инициализировать объект оборудования."""
        self.id = equipment_id
        self.name = name
        self.inventory_number = inventory_number
        self.operational = operational
        self.under_maintenance = under_maintenance
        self.required_level = required_level
        self.hourly_rate = hourly_rate

    @property
    def is_ready(self) -> bool:
        """Флаг технической готовности оборудования к работе."""
        return self.operational and not self.under_maintenance

    def check_readiness(self) -> str:
        """Проверить техническую готовность оборудования к эксплуатации."""
        if not self.operational:
            return "Оборудование неисправно"
        if self.under_maintenance:
            return "Оборудование на техническом обслуживании"
        return "Оборудование готово к работе"

    def is_suitable_for_level(self, user_level: int) -> bool:
        """Проверить, соответствует ли уровень допуска пользователя прибору."""
        return user_level >= self.required_level

    @staticmethod
    def validate_rate(rate: float) -> bool:
        """Проверить корректность значения почасовой ставки."""
        return rate >= 0.0

    @staticmethod
    def validate_level(level: int) -> bool:
        """Проверить корректность уровня допуска (от 1 до 3)."""
        return 1 <= level <= 3

    @classmethod
    def from_data(cls, data: dict) -> "Equipment":
        """Создать объект оборудования из словаря данных JSON."""
        return cls(
            equipment_id=int(data.get("id", 0)),
            name=str(data.get("name", "")),
            inventory_number=str(data.get("inventory_number", "")),
            operational=bool(data.get("operational", True)),
            under_maintenance=bool(data.get("under_maintenance", False)),
            required_level=int(data.get("required_level", 1)),
            hourly_rate=float(data.get("hourly_rate", 0.0)),
        )

    def to_dict(self) -> dict:
        """Преобразовать объект оборудования в словарь для сериализации."""
        return {
            "id": self.id,
            "name": self.name,
            "inventory_number": self.inventory_number,
            "operational": self.operational,
            "under_maintenance": self.under_maintenance,
            "required_level": self.required_level,
            "hourly_rate": self.hourly_rate,
        }

    def __str__(self) -> str:
        """Строковое представление объекта оборудования."""
        return (
            f"[{self.id}] {self.name} (инв. {self.inventory_number}, "
            f"ставка: {self.hourly_rate} руб/час, "
            f"допуск: {self.required_level}, статус: {self.check_readiness()})"
        )


def _get_items(collection: list[Equipment] | dict) -> list[Equipment]:
    """Вспомогательная функция извлечения списка объектов."""
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
) -> Equipment:
    """Создать объект Equipment и добавить его в коллекцию."""
    items = _get_items(equipment)
    equipment_id = max((item.id for item in items), default=0) + 1
    new_item = Equipment(
        equipment_id=equipment_id,
        name=name,
        inventory_number=inventory_number,
        operational=operational,
        under_maintenance=under_maintenance,
        required_level=required_level,
        hourly_rate=hourly_rate,
    )
    if isinstance(equipment, list):
        equipment.append(new_item)
    elif isinstance(equipment, dict):
        equipment[equipment_id] = new_item
    return new_item


def find_equipment(
    equipment: list[Equipment] | dict,
    query: str,
) -> list[Equipment]:
    """Найти оборудование по подстроке названия или инвентарному номеру."""
    query_lower = query.lower()
    found: list[Equipment] = []
    for item in _get_items(equipment):
        name_match = query_lower in item.name.lower()
        inv_match = query_lower in item.inventory_number.lower()
        if name_match or inv_match:
            found.append(item)
    return found


def check_equipment_availability(
    operational: bool,
    under_maintenance: bool,
) -> str:
    """Проверить техническую готовность оборудования (сохранена из ПР1)."""
    if not operational:
        return "Оборудование неисправно"
    if under_maintenance:
        return "Оборудование на техническом обслуживании"
    return "Оборудование готово к работе"


def filter_equipment_by_level(
    equipment: list[Equipment] | dict,
    max_level: int,
) -> Iterator[Equipment]:
    """Отобрать оборудование по допустимому уровню допуска через генератор."""
    for item in _get_items(equipment):
        if item.required_level <= max_level:
            yield item


def sort_equipment(
    equipment: list[Equipment] | dict,
    reverse: bool = False,
) -> list[Equipment]:
    """Отсортировать оборудование по почасовой ставке."""
    return sorted(
        _get_items(equipment),
        key=lambda item: item.hourly_rate,
        reverse=reverse,
    )


def get_equipment_by_id(
    equipment: list[Equipment] | dict,
    equipment_id: Optional[int],
) -> Optional[Equipment]:
    """Вернуть объект оборудования по идентификатору."""
    if equipment_id is None:
        return None
    for item in _get_items(equipment):
        if item.id == equipment_id:
            return item
    return None


def show_equipment(equipment: list[Equipment] | dict) -> None:
    """Вывести список оборудования в виде форматированной таблицы."""
    items = sort_equipment(equipment)
    if not items:
        print("Список оборудования пуст.")
        return
    header = (
        f"{'ID':<4}{'Название':<38}{'Инв.№':<10}"
        f"{'Ставка':<8}{'Ур.':<4}Статус"
    )
    print()
    print(header)
    print("-" * 78)
    for item in items:
        name = item.name[:36]
        inv = item.inventory_number
        print(
            f"{item.id:<4}{name:<38}{inv:<10}"
            f"{item.hourly_rate:<8}{item.required_level:<4}"
            f"{item.check_readiness()}"
        )
