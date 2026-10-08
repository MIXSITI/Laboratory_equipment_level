import json
from datetime import date, datetime
from pathlib import Path
from typing import Optional

from models.bookings import Booking
from models.equipment import Equipment, get_equipment_by_id
from models.users import User, get_user_by_id


def load_json_list(filename: str | Path) -> list:
    """Загрузить список из JSON-файла через контекстный менеджер with."""
    try:
        with open(filename, "r", encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        print(f"Файл {filename} содержит некорректный JSON.")
        return []
    if not isinstance(data, list):
        return []
    return data


def save_json_list(filename: str | Path, data: list) -> None:
    """Сохранить список в JSON-файл через контекстный менеджер with."""
    path = Path(filename)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def load_equipment(
    filename: str | Path = "data/equipment.json",
) -> list[Equipment]:
    """Загрузить оборудование из JSON и преобразовать в объекты."""
    target_path = Path(filename)
    if not target_path.exists() and "rooms.json" in str(target_path):
        fallback = target_path.parent / "equipment.json"
        if fallback.exists():
            target_path = fallback
    items = load_json_list(target_path)
    result: list[Equipment] = []
    for item in items:
        if isinstance(item, dict) and "id" in item:
            result.append(Equipment.from_data(item))
    return result


def save_equipment(
    filename: str | Path,
    equipment: list[Equipment] | dict,
) -> None:
    """Сохранить коллекцию объектов оборудования в JSON-файл."""
    items = (
        list(equipment.values())
        if isinstance(equipment, dict)
        else equipment
    )
    prepared = [
        item.to_dict() if hasattr(item, "to_dict") else dict(item)
        for item in items
    ]
    save_json_list(filename, prepared)


def load_users(filename: str | Path) -> list[User]:
    """Загрузить пользователей из JSON-файла и преобразовать в объекты."""
    items = load_json_list(filename)
    result: list[User] = []
    for item in items:
        if isinstance(item, dict) and "id" in item:
            result.append(User.from_data(item))
    return result


def save_users(
    filename: str | Path,
    users: list[User] | dict,
) -> None:
    """Сохранить коллекцию объектов пользователей в JSON-файл."""
    items = list(users.values()) if isinstance(users, dict) else users
    prepared = [
        item.to_dict() if hasattr(item, "to_dict") else dict(item)
        for item in items
    ]
    save_json_list(filename, prepared)


def load_bookings(
    filename: str | Path,
    equipment: Optional[list[Equipment] | dict] = None,
    users: Optional[list[User] | dict] = None,
) -> list[Booking]:
    """Загрузить бронирования из JSON и восстановить связи с объектами."""
    items = load_json_list(filename)
    result: list[Booking] = []

    if equipment is None:
        eq_path = Path(filename).parent / "equipment.json"
        equipment = load_equipment(eq_path)
    if users is None:
        u_path = Path(filename).parent / "users.json"
        users = load_users(u_path)

    for item in items:
        if not isinstance(item, dict) or "id" not in item:
            continue
        booking_id = int(item["id"])
        eq_id = int(item.get("equipment_id", item.get("room_id", 0)))
        u_id = int(item.get("user_id", 0))

        eq = get_equipment_by_id(equipment, eq_id)
        user = get_user_by_id(users, u_id)

        raw_date = item.get("booking_date")
        if isinstance(raw_date, str):
            try:
                b_date = date.fromisoformat(raw_date)
            except ValueError:
                try:
                    b_date = datetime.strptime(raw_date, "%d.%m.%Y").date()
                except ValueError:
                    b_date = date.today()
        elif isinstance(raw_date, date):
            b_date = raw_date
        else:
            b_date = date.today()

        duration = float(item.get("duration_hours", 1.0))
        cost = float(item.get("cost", 0.0))
        is_cancelled = bool(item.get("is_cancelled", False))

        if eq is not None and user is not None:
            booking = Booking(
                booking_id=booking_id,
                equipment=eq,
                booking_date=b_date,
                user=user,
                duration_hours=duration,
                cost=cost,
                is_cancelled=is_cancelled,
            )
            result.append(booking)

    return result


def save_bookings(
    filename: str | Path,
    bookings: list[Booking],
) -> None:
    """Сохранить бронирования в JSON-файл с заменой объектов на ID."""
    prepared = []
    for item in bookings:
        if hasattr(item, "to_dict"):
            prepared.append(item.to_dict())
        elif isinstance(item, dict):
            copy_dict = dict(item)
            b_date = copy_dict.get("booking_date")
            if isinstance(b_date, date):
                copy_dict["booking_date"] = b_date.isoformat()
            prepared.append(copy_dict)
    save_json_list(filename, prepared)


load_rooms = load_equipment
save_rooms = save_equipment
