"""Точка запуска системы бронирования лабораторного оборудования."""

from pathlib import Path

from models import Booking, Equipment, User
from models.bookings import (
    calculate_booking_cost,
    cancel_booking,
    create_booking,
    get_booking_statistics,
    get_booking_status,
    is_equipment_available,
    show_bookings,
)
from models.equipment import (
    add_equipment,
    filter_equipment_by_level,
    find_equipment,
    get_equipment_by_id,
    show_equipment,
)
from models.users import (
    add_user,
    get_user_by_id,
    show_users,
)
from storage import (
    load_bookings,
    load_equipment,
    load_users,
    save_bookings,
    save_equipment,
    save_users,
)
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
    print("10. Добавить оборудование")
    print("11. Добавить пользователя")
    print("0. Выход")
    print()


def handle_find_equipment(equipment: list[Equipment]) -> None:
    """Найти и вывести оборудование по названию или инв. номеру."""
    query = input("Введите часть названия или инв. номер: ").strip()
    if not query:
        print("Поисковый запрос не может быть пустым.")
        return
    found = find_equipment(equipment, query)
    if not found:
        print("Оборудование не найдено.")
        return
    print(f"Найдено ({len(found)}):")
    for item in found:
        print(f"  {item}")


def handle_check_readiness(equipment: list[Equipment]) -> None:
    """Проверить техническую готовность выбранного прибора."""
    equipment_id = input_int("Введите ID оборудования: ")
    item = get_equipment_by_id(equipment, equipment_id)
    if item is None:
        print("Оборудование с таким ID не найдено.")
        return
    print(f"{item.name}: {item.check_readiness()}")


def handle_check_availability(
    equipment: list[Equipment],
    bookings: list[Booking],
) -> None:
    """Проверить доступность оборудования на дату."""
    equipment_id = input_int("Введите ID оборудования: ")
    item = get_equipment_by_id(equipment, equipment_id)
    if item is None:
        print("Оборудование с таким ID не найдено.")
        return
    print(f"Прибор: {item.name}")
    if not item.is_ready:
        print(f"Техническое состояние: {item.check_readiness()}")
    booking_date = input_date("Введите дату (ГГГГ-ММ-ДД): ")
    available = is_equipment_available(
        bookings,
        item,
        booking_date,
    )
    print(get_booking_status(available))


def create_new_booking(
    equipment: list[Equipment],
    users: list[User],
    bookings: list[Booking],
) -> None:
    """Создать бронирование в объектной модели предметной области."""
    equipment_id = input_int("Введите ID оборудования: ")
    item = get_equipment_by_id(equipment, equipment_id)
    if item is None:
        print("Оборудование с таким ID не найдено.")
        return

    if not item.is_ready:
        print(f"Бронирование невозможно: {item.check_readiness()}")
        return

    user_id = input_int("Введите ID пользователя: ")
    user = get_user_by_id(users, user_id)
    if user is None:
        print("Пользователь с таким ID не найден.")
        return

    if not user.has_access(item.required_level):
        print("Допуск пользователя: Отклонен")
        print("Бронирование невозможно.")
        return

    booking_date = input_date("Введите дату (ГГГГ-ММ-ДД): ")
    if not is_equipment_available(bookings, item, booking_date):
        print(get_booking_status(False))
        return

    duration_hours = input_float(
        "Введите длительность в часах: ",
        min_value=0.5,
    )

    cost = calculate_booking_cost(
        item.hourly_rate,
        duration_hours,
        user.is_student(),
    )
    booking = create_booking(
        bookings=bookings,
        equipment=item,
        booking_date=booking_date,
        user=user,
        duration_hours=duration_hours,
        cost=cost,
    )
    if booking is None:
        print(get_booking_status(False))
        return

    save_bookings(BOOKINGS_FILE, bookings)
    print("Бронирование успешно подтверждено.")
    print(f"Номер заявки: {booking.id}")
    print(f"Стоимость: {booking.cost} руб.")
    print(f"Прибор: {booking.equipment.name}")
    print(f"Пользователь: {booking.user.name}")


handle_create_booking = create_new_booking


def handle_cancel_booking(bookings: list[Booking]) -> None:
    """Отменить бронирование по идентификатору заявки."""
    booking_id = input_int("Введите ID бронирования: ")
    if cancel_booking(bookings, booking_id):
        save_bookings(BOOKINGS_FILE, bookings)
        print("Бронирование отменено.")
    else:
        print("Бронирование с таким ID не найдено.")


def show_statistics(
    equipment: list[Equipment],
    bookings: list[Booking],
) -> None:
    """Вывести статистику по оборудованию и бронированиям."""
    stats = get_booking_statistics(bookings)
    print()
    print("=== Статистика ===")
    print(f"Всего приборов: {len(equipment)}")
    print(f"Активных бронирований: {stats['bookings_count']}")
    print(f"Всего заявок в базе: {stats['total_bookings']}")
    print(f"Задействовано приборов: {stats['unique_equipment']}")
    print(f"Суммарная стоимость: {stats['total_cost']} руб.")
    print("Оборудование, доступное при уровне допуска 1:")
    found = False
    for item in filter_equipment_by_level(equipment, 1):
        print(f"  - {item.name}")
        found = True
    if not found:
        print("  нет подходящих приборов")


def handle_add_equipment(equipment: list[Equipment]) -> None:
    """Добавить новое оборудование в систему."""
    name = input("Введите наименование оборудования: ").strip()
    if not name:
        print("Наименование не может быть пустым.")
        return
    inv = input("Введите инвентарный номер (например EQ-101): ").strip()
    level = input_int(
        "Введите требуемый уровень допуска (1-3): ",
        min_value=1,
        max_value=3,
    )
    rate = input_float(
        "Введите почасовую ставку (руб/час): ",
        min_value=0.0,
    )
    item = add_equipment(
        equipment=equipment,
        name=name,
        inventory_number=inv,
        operational=True,
        under_maintenance=False,
        required_level=level,
        hourly_rate=rate,
    )
    save_equipment(EQUIPMENT_FILE, equipment)
    print(f"Оборудование '{item.name}' успешно добавлено.")


def handle_add_user(users: list[User]) -> None:
    """Добавить нового пользователя в систему."""
    name = input("Введите ФИО пользователя: ").strip()
    if not name:
        print("ФИО не может быть пустым.")
        return
    role = input("Введите статус (студент / сотрудник): ").strip().lower()
    if role not in ("студент", "сотрудник"):
        role = "студент"
    level = input_int(
        "Введите уровень допуска пользователя (1-3): ",
        min_value=1,
        max_value=3,
    )
    briefing_str = input(
        "Пройден ли инструктаж по ТБ (да/нет): "
    ).strip().lower()
    briefing = (briefing_str == "да")
    user = add_user(
        users=users,
        name=name,
        role=role,
        access_level=level,
        briefing_passed=briefing,
    )
    save_users(USERS_FILE, users)
    print(f"Пользователь '{user.name}' успешно добавлен.")


def save_all(
    equipment: list[Equipment],
    users: list[User],
    bookings: list[Booking],
) -> None:
    """Сохранить все данные проекта в JSON-файлы."""
    save_equipment(EQUIPMENT_FILE, equipment)
    save_users(USERS_FILE, users)
    save_bookings(BOOKINGS_FILE, bookings)


def main() -> None:
    """Точка запуска: меню приложения и вызов функций проекта."""
    equipment = load_equipment(EQUIPMENT_FILE)
    users = load_users(USERS_FILE)
    bookings = load_bookings(BOOKINGS_FILE, equipment, users)

    try:
        while True:
            show_menu()
            choice = input_int(
                "Выберите действие: ",
                min_value=0,
                max_value=11,
            )
            if choice == 1:
                show_equipment(equipment)
            elif choice == 2:
                handle_find_equipment(equipment)
            elif choice == 3:
                handle_check_readiness(equipment)
            elif choice == 4:
                handle_check_availability(equipment, bookings)
            elif choice == 5:
                create_new_booking(equipment, users, bookings)
            elif choice == 6:
                handle_cancel_booking(bookings)
            elif choice == 7:
                show_bookings(bookings)
            elif choice == 8:
                show_users(users)
            elif choice == 9:
                show_statistics(equipment, bookings)
            elif choice == 10:
                handle_add_equipment(equipment)
            elif choice == 11:
                handle_add_user(users)
            elif choice == 0:
                save_all(equipment, users, bookings)
                print("Данные сохранены. Выход.")
                break
    except (KeyboardInterrupt, EOFError):
        print("\nЗавершение работы программы.")
        save_all(equipment, users, bookings)


if __name__ == "__main__":
    main()
