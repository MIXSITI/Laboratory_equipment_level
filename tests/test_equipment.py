from equipment import (
    add_equipment,
    check_equipment_availability,
    find_equipment,
)
from users import add_user, check_user_access


def test_add_equipment():
    equipment = {}
    add_equipment(equipment, "Спектрофотометр UV-1800")
    assert len(equipment) == 1


def test_find_equipment():
    equipment = {}
    add_equipment(equipment, "Спектрофотометр UV-1800")
    assert find_equipment(equipment, "спектрофотометр")


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
