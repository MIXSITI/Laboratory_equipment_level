from equipment import (
    add_equipment,
    check_equipment_availability,
    filter_equipment_by_level,
    find_equipment,
    sort_equipment,
)
from users import add_user, check_user_access, find_user
from utils import inspect_object


def test_add_equipment():
    equipment = {}
    add_equipment(equipment, "Спектрофотометр UV-1800")
    assert len(equipment) == 1
    assert equipment[1]["name"] == "Спектрофотометр UV-1800"


def test_find_equipment():
    equipment = {}
    add_equipment(
        equipment,
        "Спектрофотометр UV-1800",
        inventory_number="EQ-301",
    )
    assert find_equipment(equipment, "спектрофотометр")
    assert find_equipment(equipment, "eq-301")
    assert not find_equipment(equipment, "несуществующий")


def test_check_equipment_availability():
    ready = check_equipment_availability(True, False)
    broken = check_equipment_availability(False, False)
    service = check_equipment_availability(True, True)
    assert ready == "Оборудование готово к работе"
    assert broken == "Оборудование неисправно"
    assert service == "Оборудование на техническом обслуживании"


def test_check_user_access():
    users = {}
    add_user(users, "Иванов Алексей Сергеевич", "студент", 2, True)
    user = users[1]
    assert check_user_access(user["access_level"], 2, True)
    assert not check_user_access(1, 3, True)
    assert not check_user_access(3, 1, False)


def test_filter_equipment_by_level():
    equipment = {
        1: {"name": "Прибор 1", "required_level": 1},
        2: {"name": "Прибор 2", "required_level": 2},
        3: {"name": "Прибор 3", "required_level": 3},
    }
    generator = filter_equipment_by_level(equipment, 2)
    filtered = list(generator)
    assert len(filtered) == 2
    assert [item["name"] for item in filtered] == ["Прибор 1", "Прибор 2"]


def test_sort_equipment():
    equipment = {
        1: {"name": "Бюджетный", "hourly_rate": 500.0},
        2: {"name": "Премиум", "hourly_rate": 2000.0},
        3: {"name": "Средний", "hourly_rate": 1000.0},
    }
    sorted_asc = sort_equipment(equipment, reverse=False)
    assert [x["hourly_rate"] for x in sorted_asc] == [500.0, 1000.0, 2000.0]
    sorted_desc = sort_equipment(equipment, reverse=True)
    assert [x["hourly_rate"] for x in sorted_desc] == [2000.0, 1000.0, 500.0]


def test_find_user():
    users = {}
    add_user(users, "Иванов Алексей Сергеевич")
    assert len(find_user(users, "Иванов")) == 1
    assert len(find_user(users, "Сидоров")) == 0


def test_inspect_object():
    info = inspect_object(add_equipment)
    assert info["type"] == "function"
    assert info["callable"] is True
    assert "оборудование" in str(info.get("doc"))
