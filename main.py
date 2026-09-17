"""Точка запуска системы бронирования лабораторного оборудования."""

from pathlib import Path

from bookings import (
    calculate_booking_cost,
    cancel_booking,
    create_booking,
    get_booking_statistics,
    get_booking_status,
    is_equipment_available,
)
from equipment import (
    check_equipment_availability,
    filter_equipment_by_level,
    find_equipment,
    get_equipment_by_id,
    sort_equipment,
)
from storage import (
    load_bookings,
    load_equipment,
    load_users,
    save_bookings,
    save_equipment,
    save_users,
)
from users import check_user_access, get_user_by_id
from utils import input_date, input_float, input_int

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
EQUIPMENT_FILE = DATA_DIR / "equipment.json"
USERS_FILE = DATA_DIR / "users.json"
BOOKINGS_FILE = DATA_DIR / "bookings.json"


def show_menu() -> None:
    """Вывести главное меню приложения."""
    print()
    print("=== Система бронирования лабораторного оборудования ===")
    print()
    print("1. Показать оборудование")
    print("2. Найти оборудование по названию")
    print("3. Проверить готовность оборудования")
    print("4. Проверить доступность на дату")
    print("5. Забронировать оборудование")
    print("6. Отменить бронирование")
    print("7. Показать бронирования")
    print("8. Показать пользователей")
    print("9. Статистика")
    print("0. Выход")
    print()


def show_equipment(equipment: dict[int, dict]) -> None:
    """Вывести список оборудования в виде таблицы."""
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
        status = check_equipment_availability(
            item["operational"],
            item["under_maintenance"],
        )
        name = item["name"][:36]
        inv = item["inventory_number"]
        print(
            f"{item['id']:<4}{name:<38}{inv:<10}"
            f"{item['hourly_rate']:<8}{item['required_level']:<4}"
            f"{status}"
        )


def show_users(users: dict[int, dict]) -> None:
    """Вывести список пользователей."""
    if not users:
        print("Список пользователей пуст.")
        return
    print()
    print(f"{'ID':<4}{'ФИО':<32}{'Статус':<12}{'Ур.':<4}ТБ")
    print("-" * 60)
    for item in users.values():
        briefing = "да" if item["briefing_passed"] else "нет"
        print(
            f"{item['id']:<4}{item['name']:<32}"
            f"{item['role']:<12}{item['access_level']:<4}{briefing}"
        )


def show_bookings(
    bookings: list[dict],
    equipment: dict[int, dict],
    users: dict[int, dict],
) -> None:
    """Вывести список бронирований."""
    if not bookings:
        print("Список бронирований пуст.")
        return
    print()
    print(
        f"{'ID':<4}{'Оборудование':<34}{'Пользователь':<22}"
        f"{'Дата':<12}{'Часы':<6}Стоимость"
    )
    print("-" * 90)
    for item in bookings:
        eq = get_equipment_by_id(equipment, item["equipment_id"])
        user = get_user_by_id(users, item.get("user_id"))
        eq_name = eq["name"][:32] if eq else "-"
        user_name = user["name"][:20] if user else "-"
        print(
            f"{item['id']:<4}{eq_name:<34}{user_name:<22}"
            f"{item['booking_date']!s:<12}"
            f"{item['duration_hours']:<6}{item['cost']}"
        )


def handle_find_equipment(equipment: dict[int, dict]) -> None:
    """Найти и вывести оборудование по названию."""
    query = input("Введите часть названия: ").strip()
    found = find_equipment(equipment, query)
    if not found:
        print("Оборудование не найдено.")
        return
    print("Найдено:")
    for item in found:
        print(f"  [{item['id']}] {item['name']}")


def handle_check_readiness(equipment: dict[int, dict]) -> None:
    """Проверить техническую готовность выбранного прибора."""
    equipment_id = input_int("Введите ID оборудования: ")
    item = get_equipment_by_id(equipment, equipment_id)
    if item is None:
        print("Оборудование с таким ID не найдено.")
        return
    status = check_equipment_availability(
        item["operational"],
        item["under_maintenance"],
    )
    print(f"{item['name']}: {status}")


def handle_check_availability(
    equipment: dict[int, dict],
    bookings: list[dict],
) -> None:
    """Проверить доступность оборудования на дату."""
    equipment_id = input_int("Введите ID оборудования: ")
    item = get_equipment_by_id(equipment, equipment_id)
    if item is None:
        print("Оборудование с таким ID не найдено.")
        return
    booking_date = input_date("Введите дату (ГГГГ-ММ-ДД): ")
    available = is_equipment_available(
        bookings,
        equipment_id,
        booking_date,
    )
    print(get_booking_status(available))


def handle_create_booking(
    equipment: dict[int, dict],
    users: dict[int, dict],
    bookings: list[dict],
) -> None:
    """Создать бронирование после всех проверок ПР1 и ПР2."""
    equipment_id = input_int("Введите ID оборудования: ")
    item = get_equipment_by_id(equipment, equipment_id)
    if item is None:
        print("Оборудование с таким ID не найдено.")
        return

    tech_status = check_equipment_availability(
        item["operational"],
        item["under_maintenance"],
    )
    if tech_status != "Оборудование готово к работе":
        print(f"Бронирование невозможно: {tech_status}")
        return

    user_id = input_int("Введите ID пользователя: ")
    user = get_user_by_id(users, user_id)
    if user is None:
        print("Пользователь с таким ID не найден.")
        return

    access_ok = check_user_access(
        user["access_level"],
        item["required_level"],
        user["briefing_passed"],
    )
    if not access_ok:
        print("Допуск пользователя: Отклонен")
        print("Бронирование невозможно.")
        return

    booking_date = input_date("Введите дату (ГГГГ-ММ-ДД): ")
    duration_hours = input_float("Введите длительность в часах: ")
    if duration_hours <= 0:
        print("Длительность должна быть больше нуля.")
        return

    is_student = user["role"].strip().lower() == "студент"
    cost = calculate_booking_cost(
        item["hourly_rate"],
        duration_hours,
        is_student,
    )
    booking = create_booking(
        bookings,
        equipment_id,
        booking_date,
        duration_hours,
        user_id,
        cost,
    )
    if booking is None:
        print(get_booking_status(False))
        return

    save_bookings(BOOKINGS_FILE, bookings)
    print("Бронирование успешно подтверждено.")
    print(f"Номер заявки: {booking['id']}")
    print(f"Стоимость: {cost} руб.")


def handle_cancel_booking(bookings: list[dict]) -> None:
    """Отменить бронирование по идентификатору заявки."""
    booking_id = input_int("Введите ID бронирования: ")
    if cancel_booking(bookings, booking_id):
        save_bookings(BOOKINGS_FILE, bookings)
        print("Бронирование отменено.")
    else:
        print("Бронирование с таким ID не найдено.")


def show_statistics(
    equipment: dict[int, dict],
    bookings: list[dict],
) -> None:
    """Вывести статистику по оборудованию и бронированиям."""
    stats = get_booking_statistics(bookings)
    print()
    print("=== Статистика ===")
    print(f"Всего приборов: {len(equipment)}")
    print(f"Бронирований: {stats['bookings_count']}")
    print(f"Задействовано приборов: {stats['unique_equipment']}")
    print(f"Суммарная стоимость: {stats['total_cost']} руб.")
    print("Оборудование, доступное при уровне допуска 1:")
    found = False
    for item in filter_equipment_by_level(equipment, 1):
        print(f"  - {item['name']}")
        found = True
    if not found:
        print("  нет подходящих приборов")


def save_all(
    equipment: dict[int, dict],
    users: dict[int, dict],
    bookings: list[dict],
) -> None:
    """Сохранить все данные проекта в JSON-файлы."""
    save_equipment(EQUIPMENT_FILE, equipment)
    save_users(USERS_FILE, users)
    save_bookings(BOOKINGS_FILE, bookings)


def main() -> None:
    """Точка запуска: меню приложения и вызов функций проекта."""
    equipment = load_equipment(EQUIPMENT_FILE)
    users = load_users(USERS_FILE)
    bookings = load_bookings(BOOKINGS_FILE)

    while True:
        show_menu()
        choice = input_int("Выберите действие: ")
        if choice == 1:
            show_equipment(equipment)
        elif choice == 2:
            handle_find_equipment(equipment)
        elif choice == 3:
            handle_check_readiness(equipment)
        elif choice == 4:
            handle_check_availability(equipment, bookings)
        elif choice == 5:
            handle_create_booking(equipment, users, bookings)
        elif choice == 6:
            handle_cancel_booking(bookings)
        elif choice == 7:
            show_bookings(bookings, equipment, users)
        elif choice == 8:
            show_users(users)
        elif choice == 9:
            show_statistics(equipment, bookings)
        elif choice == 0:
            save_all(equipment, users, bookings)
            print("Данные сохранены. Выход.")
            break
        else:
            print("Неизвестный пункт меню.")


if __name__ == "__main__":
    main()
