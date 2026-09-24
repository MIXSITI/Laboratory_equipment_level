"""Класс Booking и функции для создания и проверки бронирований."""

from datetime import date
from typing import Optional

from .rooms import Room
from .users import User


class Booking:
    """Бронирование помещения / оборудования пользователем."""

    def __init__(
        self,
        booking_id: int,
        room: Room,
        booking_date: date | str,
        user: User,
        duration_hours: float = 1.0,
        cost: float = 0.0,
        is_cancelled: bool = False,
    ) -> None:
        """Создать объект бронирования."""
        self.id = booking_id
        self.room = room
        if isinstance(booking_date, str):
            self.booking_date: date = date.fromisoformat(booking_date)
        else:
            self.booking_date = booking_date
        self.user = user
        self.duration_hours = duration_hours
        self.cost = cost
        self.is_cancelled = is_cancelled

    @property
    def equipment(self) -> Room:
        """Псевдоним room для совместимости с кодом оборудования."""
        return self.room

    @property
    def status(self) -> str:
        """Текстовый статус состояния бронирования."""
        return "Отменено" if self.is_cancelled else "Подтверждено"

    def cancel(self) -> None:
        """Отменить бронирование, изменив его состояние."""
        self.is_cancelled = True

    def to_dict(self) -> dict:
        """Преобразовать объект бронирования в структуру для JSON."""
        b_date = (
            self.booking_date.isoformat()
            if isinstance(self.booking_date, date)
            else str(self.booking_date)
        )
        return {
            "id": self.id,
            "room_id": self.room.id if self.room else 0,
            "equipment_id": self.room.id if self.room else 0,
            "booking_date": b_date,
            "user_id": self.user.id if self.user else 0,
            "duration_hours": self.duration_hours,
            "cost": self.cost,
            "is_cancelled": self.is_cancelled,
        }

    def __str__(self) -> str:
        """Вернуть строковое представление бронирования."""
        room_name = self.room.name if self.room else "-"
        user_name = self.user.name if self.user else "-"
        state = "[ОТМЕНЕНО]" if self.is_cancelled else "[АКТИВНО]"
        return (
            f"Заявка #{self.id} {state}: {room_name} | {user_name} | "
            f"Дата: {self.booking_date} | {self.duration_hours} ч. | "
            f"{self.cost} руб."
        )


def is_room_available(
    bookings: list[Booking],
    room: Room | int,
    booking_date: date | str,
) -> bool:
    """Проверить, свободно ли помещение/оборудование на указанную дату.

    Отмененные бронирования не блокируют помещение.
    """
    room_id = room.id if isinstance(room, Room) else room
    if isinstance(booking_date, str):
        booking_date = date.fromisoformat(booking_date)

    for booking in bookings:
        if getattr(booking, "is_cancelled", False):
            continue
        if hasattr(booking, "room") and booking.room:
            b_room_id = booking.room.id
        elif isinstance(booking, dict):
            b_room_id = booking.get("room_id", booking.get("equipment_id"))
        else:
            continue

        b_date = getattr(booking, "booking_date", None)
        if b_date is None and isinstance(booking, dict):
            b_date = booking.get("booking_date")
        if isinstance(b_date, str):
            b_date = date.fromisoformat(b_date)

        if b_room_id == room_id and b_date == booking_date:
            return False
    return True


is_equipment_available = is_room_available


def calculate_booking_cost(
    rate: float,
    hours: float,
    student: bool,
) -> float:
    """Рассчитать стоимость бронирования со скидкой (сохранена из ПР1)."""
    base_cost = rate * hours
    if student:
        discount = 0.5
        total_cost = base_cost - (base_cost * discount)
    else:
        total_cost = base_cost
    return round(total_cost, 2)


def create_booking(
    bookings: list[Booking],
    room: Room | int,
    booking_date: date | str,
    user: Optional[User] = None,
    duration_hours: float = 1.0,
    cost: Optional[float] = None,
    user_id: Optional[int] = None,
) -> Optional[Booking]:
    """Создать новое бронирование и добавить его в коллекцию."""
    if not is_room_available(bookings, room, booking_date):
        return None

    booking_id = max((b.id for b in bookings), default=0) + 1

    if isinstance(room, int):
        from .rooms import Room as RoomClass
        room = RoomClass(room_id=room, name=f"Помещение #{room}")

    if user is None and user_id is not None:
        from .users import User as UserClass
        user = UserClass(user_id=user_id, name=f"Пользователь #{user_id}")
    elif user is None:
        from .users import User as UserClass
        user = UserClass(user_id=1, name="Не указан")

    if cost is None:
        discount = user.get_discount() if hasattr(user, "get_discount") else (
            0.5 if user.is_student() else 0.0
        )
        base = room.hourly_rate * duration_hours
        cost = round(base * (1.0 - discount), 2)

    new_booking = Booking(
        booking_id=booking_id,
        room=room,
        booking_date=booking_date,
        user=user,
        duration_hours=duration_hours,
        cost=cost,
        is_cancelled=False,
    )
    bookings.append(new_booking)
    return new_booking


def cancel_booking(
    bookings: list[Booking],
    booking_id: int,
) -> bool:
    """Отменить бронирование через метод объекта cancel()."""
    for booking in bookings:
        b_id = booking.id if hasattr(booking, "id") else booking.get("id")
        if b_id == booking_id:
            if hasattr(booking, "cancel"):
                booking.cancel()
            else:
                booking["is_cancelled"] = True
            return True
    return False


def get_booking_status(is_available: bool) -> str:
    """Вернуть текстовый статус доступности помещения (из ПР1)."""
    if is_available:
        return "Помещение доступно для бронирования"
    return "Помещение уже занято"


def get_booking_statistics(bookings: list[Booking]) -> dict:
    """Собрать статистику по списку бронирований."""
    active_bookings = [
        b for b in bookings
        if not getattr(b, "is_cancelled", False)
    ]
    booked_room_ids = set()
    total_cost = 0.0
    for b in active_bookings:
        if hasattr(b, "room") and b.room:
            booked_room_ids.add(b.room.id)
        elif isinstance(b, dict):
            r_id = b.get("room_id", b.get("equipment_id"))
            if r_id:
                booked_room_ids.add(r_id)
        cost_val = getattr(b, "cost", None)
        if cost_val is None and isinstance(b, dict):
            cost_val = b.get("cost", 0.0)
        total_cost += cost_val or 0.0

    return {
        "bookings_count": len(active_bookings),
        "total_bookings": len(bookings),
        "unique_rooms": len(booked_room_ids),
        "unique_equipment": len(booked_room_ids),
        "total_cost": round(total_cost, 2),
    }


def show_bookings(bookings: list[Booking]) -> None:
    """Вывести список бронирований в виде таблицы."""
    if not bookings:
        print("Список бронирований пуст.")
        return
    print()
    print(
        f"{'ID':<4}{'Помещение / прибор':<32}{'Пользователь':<20}"
        f"{'Дата':<12}{'Часы':<6}{'Сумма':<8}Статус"
    )
    print("-" * 92)
    for item in bookings:
        r_name = item.room.name[:30] if getattr(item, "room", None) else "-"
        u_name = item.user.name[:18] if getattr(item, "user", None) else "-"
        b_date = getattr(item, "booking_date", "-")
        duration = getattr(item, "duration_hours", 0.0)
        cost = getattr(item, "cost", 0.0)
        status = getattr(item, "status", "Подтверждено")
        print(
            f"{item.id:<4}{r_name:<32}{u_name:<20}"
            f"{b_date!s:<12}{duration:<6}{cost:<8}{status}"
        )
