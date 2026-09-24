"""Тесты для класса Room и функций работы с помещениями."""

import sys
from pathlib import Path

# Поддержка прямого запуска файла: python tests/test_rooms.py
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import pytest  # noqa: E402
from models.rooms import (  # noqa: E402
    Room,
    add_room,
    check_equipment_availability,
    check_room_capacity,
    filter_rooms_by_capacity,
    filter_rooms_by_level,
    find_room,
    get_room_by_id,
    sort_rooms,
)
from utils import inspect_object  # noqa: E402


def test_room_creation():
    """Проверить создание объекта Room и значения его атрибутов."""
    room = Room(
        room_id=1,
        name="Аудитория 301",
        capacity=30,
        inventory_number="EQ-301",
        operational=True,
        under_maintenance=False,
        required_level=2,
        hourly_rate=1200.0,
    )
    assert room.id == 1
    assert room.name == "Аудитория 301"
    assert room.capacity == 30
    assert room.inventory_number == "EQ-301"
    assert room.operational is True
    assert room.under_maintenance is False
    assert room.required_level == 2
    assert room.hourly_rate == 1200.0


def test_room_is_suitable_for():
    """Проверить метод is_suitable_for по вместимости (Шаг 1 ТЗ)."""
    room = Room(1, "Аудитория 301", 30)
    assert room.is_suitable_for(20) is True
    assert room.is_suitable_for(30) is True
    assert room.is_suitable_for(40) is False


def test_room_str():
    """Проверить строковое представление объекта Room (__str__)."""
    room = Room(1, "Аудитория 301", 30, hourly_rate=500.0)
    text = str(room)
    assert "[1] Аудитория 301" in text
    assert "30 чел" in text
    assert "500.0" in text


def test_room_readiness():
    """Проверить методы и свойства готовности помещения/оборудования."""
    ready_item = Room(
        1, "Прибор 1", operational=True, under_maintenance=False
    )
    broken_item = Room(
        2, "Прибор 2", operational=False, under_maintenance=False
    )
    service_item = Room(
        3, "Прибор 3", operational=True, under_maintenance=True
    )

    assert ready_item.is_ready is True
    assert ready_item.check_readiness() == "Оборудование готово к работе"

    assert broken_item.is_ready is False
    assert broken_item.check_readiness() == "Оборудование неисправно"

    assert service_item.is_ready is False
    assert service_item.check_readiness() == (
        "Оборудование на техническом обслуживании"
    )


def test_room_suitable_for_level():
    """Проверить метод is_suitable_for_level."""
    room = Room(1, "Микроскоп", required_level=2)
    assert room.is_suitable_for_level(2) is True
    assert room.is_suitable_for_level(3) is True
    assert room.is_suitable_for_level(1) is False


def test_room_static_validation():
    """Проверить статические методы валидации @staticmethod."""
    assert Room.validate_capacity(30) is True
    assert Room.validate_capacity(0) is False
    assert Room.validate_capacity(-5) is False
    assert Room.validate_rate(100.0) is True
    assert Room.validate_rate(-5.0) is False
    assert Room.validate_level(1) is True
    assert Room.validate_level(3) is True
    assert Room.validate_level(4) is False


def test_room_from_data_and_to_dict():
    """Проверить методы @classmethod from_data и to_dict."""
    data = {
        "id": 5,
        "name": "3D-принтер",
        "capacity": 6,
        "inventory_number": "EQ-220",
        "operational": True,
        "under_maintenance": True,
        "required_level": 2,
        "hourly_rate": 610.0,
    }
    room = Room.from_data(data)
    assert room.id == 5
    assert room.name == "3D-принтер"
    assert room.capacity == 6
    assert room.under_maintenance is True
    assert room.to_dict() == data


def test_add_room():
    """Проверить добавление помещения в коллекцию."""
    rooms = []
    room = add_room(rooms, "Аудитория 301", capacity=30)
    assert len(rooms) == 1
    assert room.id == 1
    assert room.name == "Аудитория 301"
    assert room.capacity == 30


def test_find_room():
    """Проверить поиск помещений по подстроке и инвентарному номеру."""
    rooms = []
    add_room(
        rooms,
        "Аудитория 301",
        capacity=30,
        inventory_number="EQ-301",
    )
    assert len(find_room(rooms, "аудитория")) == 1
    assert len(find_room(rooms, "eq-301")) == 1
    assert len(find_room(rooms, "несуществующий")) == 0


def test_check_room_capacity():
    """Проверить функцию check_room_capacity."""
    rooms = [Room(1, "Конференц-зал", capacity=60)]
    assert check_room_capacity(rooms, 1, 50) is True
    assert check_room_capacity(rooms, 1, 70) is False
    assert check_room_capacity(rooms, 99, 10) is False


def test_filter_rooms_by_capacity():
    """Проверить фильтрацию помещений по вместимости через генератор."""
    rooms = [
        Room(1, "Малая комната", capacity=10),
        Room(2, "Средний зал", capacity=30),
        Room(3, "Большой зал", capacity=60),
    ]
    filtered = list(filter_rooms_by_capacity(rooms, 30))
    assert len(filtered) == 2
    assert [r.name for r in filtered] == ["Средний зал", "Большой зал"]


def test_filter_rooms_by_level():
    """Проверить отбор оборудования по уровню через генератор."""
    rooms = [
        Room(1, "Прибор 1", required_level=1),
        Room(2, "Прибор 2", required_level=2),
        Room(3, "Прибор 3", required_level=3),
    ]
    filtered = list(filter_rooms_by_level(rooms, 2))
    assert len(filtered) == 2
    assert [x.name for x in filtered] == ["Прибор 1", "Прибор 2"]


def test_sort_rooms():
    """Проверить сортировку помещений."""
    rooms = [
        Room(1, "Малый", hourly_rate=500.0, capacity=10),
        Room(2, "Премиум", hourly_rate=2000.0, capacity=50),
        Room(3, "Средний", hourly_rate=1000.0, capacity=30),
    ]
    sorted_asc = sort_rooms(rooms, reverse=False)
    assert [x.hourly_rate for x in sorted_asc] == [500.0, 1000.0, 2000.0]
    sorted_desc = sort_rooms(rooms, reverse=True)
    assert [x.hourly_rate for x in sorted_desc] == [2000.0, 1000.0, 500.0]


def test_get_room_by_id():
    """Проверить поиск помещения по ID."""
    rooms = [Room(1, "Зал 1"), Room(2, "Зал 2")]
    assert get_room_by_id(rooms, 1).name == "Зал 1"
    assert get_room_by_id(rooms, 99) is None
    assert get_room_by_id(rooms, None) is None


def test_check_equipment_availability():
    """Проверить функцию check_equipment_availability из ПР1."""
    ready = check_equipment_availability(True, False)
    broken = check_equipment_availability(False, False)
    service = check_equipment_availability(True, True)
    assert ready == "Оборудование готово к работе"
    assert broken == "Оборудование неисправно"
    assert service == "Оборудование на техническом обслуживании"


def test_inspect_object():
    """Проверить интроспекцию функций и объектов."""
    info = inspect_object(add_room)
    assert info["type"] == "function"
    assert info["callable"] is True
    assert "помещение" in str(info.get("doc")).lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
