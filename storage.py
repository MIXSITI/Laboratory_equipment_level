"""Функции сохранения и загрузки данных проекта."""

import json
from datetime import date
from pathlib import Path


def load_json_list(filename: str | Path) -> list:
    """Загрузить список из JSON-файла.

    При отсутствии файла или некорректном JSON
    возвращает пустой список.
    """
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
    """Сохранить список в JSON-файл через контекстный менеджер."""
    path = Path(filename)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def load_equipment(filename: str | Path) -> dict[int, dict]:
    """Загрузить оборудование из JSON-файла."""
    items = load_json_list(filename)
    result = {}
    for item in items:
        result[item["id"]] = item
    return result


def save_equipment(
    filename: str | Path,
    equipment: dict[int, dict],
) -> None:
    """Сохранить оборудование в JSON-файл."""
    save_json_list(filename, list(equipment.values()))


def load_users(filename: str | Path) -> dict[int, dict]:
    """Загрузить пользователей из JSON-файла."""
    items = load_json_list(filename)
    result = {}
    for item in items:
        result[item["id"]] = item
    return result


def save_users(filename: str | Path, users: dict[int, dict]) -> None:
    """Сохранить пользователей в JSON-файл."""
    save_json_list(filename, list(users.values()))


def load_bookings(filename: str | Path) -> list[dict]:
    """Загрузить бронирования из JSON-файла."""
    items = load_json_list(filename)
    for item in items:
        raw_date = item.get("booking_date")
        if isinstance(raw_date, str):
            item["booking_date"] = date.fromisoformat(raw_date)
    return items


def save_bookings(filename: str | Path, bookings: list[dict]) -> None:
    """Сохранить бронирования в JSON-файл."""
    prepared = []
    for item in bookings:
        copy = dict(item)
        booking_date = copy.get("booking_date")
        if isinstance(booking_date, date):
            copy["booking_date"] = booking_date.isoformat()
        prepared.append(copy)
    save_json_list(filename, prepared)
