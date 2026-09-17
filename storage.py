import json
from datetime import date, datetime
from pathlib import Path


def load_json_list(filename: str | Path) -> list:
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
    path = Path(filename)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def load_equipment(filename: str | Path) -> dict[int, dict]:
    items = load_json_list(filename)
    result = {}
    for item in items:
        if "id" in item:
            item_id = int(item["id"])
            item["id"] = item_id
            result[item_id] = item
    return result


def save_equipment(
    filename: str | Path,
    equipment: dict[int, dict],
) -> None:
    save_json_list(filename, list(equipment.values()))


def load_users(filename: str | Path) -> dict[int, dict]:
    items = load_json_list(filename)
    result = {}
    for item in items:
        if "id" in item:
            user_id = int(item["id"])
            item["id"] = user_id
            result[user_id] = item
    return result


def save_users(filename: str | Path, users: dict[int, dict]) -> None:
    save_json_list(filename, list(users.values()))


def load_bookings(filename: str | Path) -> list[dict]:
    items = load_json_list(filename)
    for item in items:
        if "id" in item:
            item["id"] = int(item["id"])
        if "equipment_id" in item:
            item["equipment_id"] = int(item["equipment_id"])
        if item.get("user_id") is not None:
            item["user_id"] = int(item["user_id"])
        raw_date = item.get("booking_date")
        if isinstance(raw_date, str):
            try:
                item["booking_date"] = date.fromisoformat(raw_date)
            except ValueError:
                try:
                    item["booking_date"] = datetime.strptime(
                        raw_date, "%d.%m.%Y"
                    ).date()
                except ValueError:
                    continue
    return items


def save_bookings(filename: str | Path, bookings: list[dict]) -> None:
    prepared = []
    for item in bookings:
        copy = dict(item)
        booking_date = copy.get("booking_date")
        if isinstance(booking_date, date):
            copy["booking_date"] = booking_date.isoformat()
        prepared.append(copy)
    save_json_list(filename, prepared)
