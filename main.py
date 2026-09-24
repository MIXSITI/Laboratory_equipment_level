"""Точка запуска системы бронирования помещений и оборудования."""

from pathlib import Path

from models import Booking, Room, User
from models.bookings import (
    calculate_booking_cost,
    cancel_booking,
    create_booking,
    get_booking_statistics,
    get_booking_status,
    is_room_available,
    show_bookings,
)
from models.rooms import (
    add_room,
    filter_rooms_by_capacity,
    find_room,
    get_room_by_id,
    show_rooms,
)
from models.users import (
    add_user,
    get_user_by_id,
    show_users,
)
from storage import (
    load_bookings,
    load_rooms,
    load_users,
    save_bookings,
    save_rooms,
    save_users,
)
from utils import input_date, input_float, input_int

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
ROOMS_FILE = DATA_DIR / "rooms.json"
USERS_FILE = DATA_DIR / "users.json"
BOOKINGS_FILE = DATA_DIR / "bookings.json"


def show_menu() -> None:
    """Вывести главное меню приложения."""
    print()
    print("=== Система бронирования помещений и оборудования ===")
    print()
    print("1. Показать помещения / оборудование")
    print("2. Найти помещение / оборудование по названию")
    print("3. Проверить готовность / вместимость")
    print("4. Проверить доступность на дату")
    print("5. Забронировать помещение / оборудование")
    print("6. Отменить бронирование")
    print("7. Показать бронирования")
    print("8. Показать пользователей")
    print("9. Статистика")
    print("10. Добавить помещение / оборудование")
    print("11. Добавить пользователя")
    print("0. Выход")
    print()


def handle_find_room(rooms: list[Room]) -> None:
    """Найти и вывести помещения по названию или инв. номеру."""
    query = input("Введите часть названия или инв. номер: ").strip()
    if not query:
        print("Поисковый запрос не может быть пустым.")
        return
    found = find_room(rooms, query)
    if not found:
        print("Помещение / оборудование не найдено.")
        return
    print(f"Найдено ({len(found)}):")
    for item in found:
        print(f"  {item}")


def handle_check_readiness(rooms: list[Room]) -> None:
    """Проверить готовность и вместимость выбранного объекта."""
    room_id = input_int("Введите ID помещения / оборудования: ")
    item = get_room_by_id(rooms, room_id)
    if item is None:
        print("Объект с таким ID не найден.")
        return
    print(f"{item.name}: {item.check_readiness()}")
    print(f"Вместимость: {item.capacity} чел.")


def handle_check_availability(
    rooms: list[Room],
    bookings: list[Booking],
) -> None:
    """Проверить доступность помещения на дату."""
    room_id = input_int("Введите ID помещения / оборудования: ")
    item = get_room_by_id(rooms, room_id)
    if item is None:
        print("Объект с таким ID не найден.")
        return
    print(f"Объект: {item.name}")
    if not item.is_ready:
        print(f"Техническое состояние: {item.check_readiness()}")
    booking_date = input_date("Введите дату (ГГГГ-ММ-ДД): ")
    available = is_room_available(
        bookings,
        item,
        booking_date,
    )
    print(get_booking_status(available))


def create_new_booking(
    rooms: list[Room],
    users: list[User],
    bookings: list[Booking],
) -> None:
    """Создать бронирование в объектной модели предметной области."""
    room_id = input_int("Введите ID помещения / оборудования: ")
    item = get_room_by_id(rooms, room_id)
    if item is None:
        print("Объект с таким ID не найден.")
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
    if not is_room_available(bookings, item, booking_date):
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
        room=item,
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
    print(f"Объект: {booking.room.name}")
    print(f"Пользователь: {booking.user.name}")


def handle_cancel_booking(bookings: list[Booking]) -> None:
    """Отменить бронирование по идентификатору заявки."""
    booking_id = input_int("Введите ID бронирования: ")
    if cancel_booking(bookings, booking_id):
        save_bookings(BOOKINGS_FILE, bookings)
        print("Бронирование отменено.")
    else:
        print("Бронирование с таким ID не найдено.")


def show_statistics(
    rooms: list[Room],
    bookings: list[Booking],
) -> None:
    """Вывести статистику по помещениям и бронированиям."""
    stats = get_booking_statistics(bookings)
    print()
    print("=== Статистика ===")
    print(f"Всего объектов: {len(rooms)}")
    print(f"Активных бронирований: {stats['bookings_count']}")
    print(f"Всего заявок в базе: {stats['total_bookings']}")
    print(f"Задействовано объектов: {stats['unique_rooms']}")
    print(f"Суммарная стоимость: {stats['total_cost']} руб.")
    print("Объекты вместимостью от 5 человек:")
    found = False
    for item in filter_rooms_by_capacity(rooms, 5):
        print(f"  - {item.name} ({item.capacity} чел.)")
        found = True
    if not found:
        print("  нет подходящих объектов")


def handle_add_room(rooms: list[Room]) -> None:
    """Добавить новое помещение / оборудование в систему."""
    name = input("Введите наименование: ").strip()
    if not name:
        print("Наименование не может быть пустым.")
        return
    capacity = input_int(
        "Введите вместимость (кол-во человек): ",
        min_value=1,
    )
    inv = input("Введите инвентарный номер (при наличии): ").strip()
    level = input_int(
        "Введите требуемый уровень допуска (1-3): ",
        min_value=1,
        max_value=3,
    )
    rate = input_float(
        "Введите почасовую ставку (руб/час): ",
        min_value=0.0,
    )
    item = add_room(
        rooms=rooms,
        name=name,
        capacity=capacity,
        inventory_number=inv,
        operational=True,
        under_maintenance=False,
        required_level=level,
        hourly_rate=rate,
    )
    save_rooms(ROOMS_FILE, rooms)
    print(f"Объект '{item.name}' успешно добавлен.")


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
    email = input("Введите email (необязательно): ").strip()
    user = add_user(
        users=users,
        name=name,
        role=role,
        access_level=level,
        briefing_passed=briefing,
        email=email,
    )
    save_users(USERS_FILE, users)
    print(f"Пользователь '{user.name}' успешно добавлен.")


def save_all(
    rooms: list[Room],
    users: list[User],
    bookings: list[Booking],
) -> None:
    """Сохранить все данные проекта в JSON-файлы."""
    save_rooms(ROOMS_FILE, rooms)
    save_users(USERS_FILE, users)
    save_bookings(BOOKINGS_FILE, bookings)


def main() -> None:
    """Точка запуска: меню приложения и вызов функций проекта."""
    rooms = load_rooms(ROOMS_FILE)
    users = load_users(USERS_FILE)
    bookings = load_bookings(BOOKINGS_FILE, rooms, users)

    try:
        while True:
            show_menu()
            choice = input_int(
                "Выберите действие: ",
                min_value=0,
                max_value=11,
            )
            if choice == 1:
                show_rooms(rooms)
            elif choice == 2:
                handle_find_room(rooms)
            elif choice == 3:
                handle_check_readiness(rooms)
            elif choice == 4:
                handle_check_availability(rooms, bookings)
            elif choice == 5:
                create_new_booking(rooms, users, bookings)
            elif choice == 6:
                handle_cancel_booking(bookings)
            elif choice == 7:
                show_bookings(bookings)
            elif choice == 8:
                show_users(users)
            elif choice == 9:
                show_statistics(rooms, bookings)
            elif choice == 10:
                handle_add_room(rooms)
            elif choice == 11:
                handle_add_user(users)
            elif choice == 0:
                save_all(rooms, users, bookings)
                print("Данные сохранены. Выход.")
                break
    except (KeyboardInterrupt, EOFError):
        print("\nЗавершение работы программы.")
        save_all(rooms, users, bookings)


if __name__ == "__main__":
    main()
