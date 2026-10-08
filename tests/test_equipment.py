import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import pytest  # noqa: E402
from models.equipment import (  # noqa: E402
    Equipment,
    add_equipment,
    check_equipment_availability,
    filter_equipment_by_level,
    find_equipment,
    get_equipment_by_id,
    sort_equipment,
)
from utils import inspect_object  # noqa: E402


def test_equipment_creation():
    item = Equipment(
        equipment_id=1,
        name="Спектрофотометр UV-1800",
        inventory_number="EQ-301",
        operational=True,
        under_maintenance=False,
        required_level=2,
        hourly_rate=1200.0,
    )
    assert item.id == 1
    assert item.name == "Спектрофотометр UV-1800"
    assert item.inventory_number == "EQ-301"
    assert item.operational is True
    assert item.under_maintenance is False
    assert item.required_level == 2
    assert item.hourly_rate == 1200.0


def test_equipment_str():
    item = Equipment(1, "Осциллограф", "EQ-101", True, False, 1, 500.0)
    text = str(item)
    assert "[1] Осциллограф" in text
    assert "EQ-101" in text
    assert "500.0" in text


def test_equipment_readiness():
    ready_item = Equipment(
        1, "Прибор 1", operational=True, under_maintenance=False
    )
    broken_item = Equipment(
        2, "Прибор 2", operational=False, under_maintenance=False
    )
    service_item = Equipment(
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


def test_equipment_suitable_for_level():
    item = Equipment(1, "Микроскоп", required_level=2)
    assert item.is_suitable_for_level(2) is True
    assert item.is_suitable_for_level(3) is True
    assert item.is_suitable_for_level(1) is False


def test_equipment_static_validation():
    assert Equipment.validate_rate(100.0) is True
    assert Equipment.validate_rate(-5.0) is False
    assert Equipment.validate_level(1) is True
    assert Equipment.validate_level(3) is True
    assert Equipment.validate_level(4) is False
    assert Equipment.validate_level(0) is False


def test_equipment_from_data_and_to_dict():
    data = {
        "id": 5,
        "name": "3D-принтер",
        "inventory_number": "EQ-220",
        "operational": True,
        "under_maintenance": True,
        "required_level": 2,
        "hourly_rate": 610.0,
    }
    item = Equipment.from_data(data)
    assert item.id == 5
    assert item.name == "3D-принтер"
    assert item.under_maintenance is True
    assert item.to_dict() == data


def test_add_equipment():
    equipment = []
    item = add_equipment(equipment, "Спектрофотометр UV-1800")
    assert len(equipment) == 1
    assert item.id == 1
    assert item.name == "Спектрофотометр UV-1800"


def test_find_equipment():
    equipment = []
    add_equipment(
        equipment,
        "Спектрофотометр UV-1800",
        inventory_number="EQ-301",
    )
    assert len(find_equipment(equipment, "спектрофотометр")) == 1
    assert len(find_equipment(equipment, "eq-301")) == 1
    assert len(find_equipment(equipment, "несуществующий")) == 0


def test_check_equipment_availability():
    ready = check_equipment_availability(True, False)
    broken = check_equipment_availability(False, False)
    service = check_equipment_availability(True, True)
    assert ready == "Оборудование готово к работе"
    assert broken == "Оборудование неисправно"
    assert service == "Оборудование на техническом обслуживании"


def test_filter_equipment_by_level():
    equipment = [
        Equipment(1, "Прибор 1", required_level=1),
        Equipment(2, "Прибор 2", required_level=2),
        Equipment(3, "Прибор 3", required_level=3),
    ]
    filtered = list(filter_equipment_by_level(equipment, 2))
    assert len(filtered) == 2
    assert [x.name for x in filtered] == ["Прибор 1", "Прибор 2"]


def test_sort_equipment():
    equipment = [
        Equipment(1, "Бюджетный", hourly_rate=500.0),
        Equipment(2, "Премиум", hourly_rate=2000.0),
        Equipment(3, "Средний", hourly_rate=1000.0),
    ]
    sorted_asc = sort_equipment(equipment, reverse=False)
    assert [x.hourly_rate for x in sorted_asc] == [500.0, 1000.0, 2000.0]
    sorted_desc = sort_equipment(equipment, reverse=True)
    assert [x.hourly_rate for x in sorted_desc] == [2000.0, 1000.0, 500.0]


def test_get_equipment_by_id():
    equipment = [Equipment(1, "Прибор 1"), Equipment(2, "Прибор 2")]
    assert get_equipment_by_id(equipment, 1).name == "Прибор 1"
    assert get_equipment_by_id(equipment, 99) is None
    assert get_equipment_by_id(equipment, None) is None


def test_inspect_object():
    add_equipment.__doc__ = "Equipment"
    info = inspect_object(add_equipment)
    assert info["type"] == "function"
    assert info["callable"] is True
    assert "Equipment" in str(info.get("doc"))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
