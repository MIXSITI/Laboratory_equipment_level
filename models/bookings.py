"""Класс бронирования и функции управления резервированием оборудования."""

from datetime import date
from typing import Optional

from .equipment import Equipment
from .users import User


class Booking:
    """Бронирование оборудования пользователем лаборатории."""

    def __init__(
        self,
        booking_id: int,
        equipment: Equipment,
        booking_date: date | str,
        user: User,
        duration_hours: float = 1.0,
        cost: float = 0.0,
        is_cancelled: bool = False,
    ) -> None:
        """Инициализировать объект бронирования."""
        self.id = booking_id
        self.equipment = equipment
        if isinstance(booking_date, str):
            self.booking_date: date = date.fromisoformat(booking_date)
        else:
            self.booking_date = booking_date
        self.user = user
        self.duration_hours = duration_hours
        self.cost = cost
        self.is_cancelled = is_cancelled

    @property
    def room(self) -> Equipment:
        """Псевдоним прибора для совместимости с интерфейсом ПР3."""
        return self.equipment

    @property
    def status(self) -> str:
        """Текстовый статус состояния бронирования."""
        return "Отменено" if self.is_cancelled else "Подтверждено"

    def cancel(self) -> None:
        """Отменить бронирование, изменив его состояние."""
        self.is_cancelled = True

    def to_dict(self) -> dict:
        """Преобразовать объект бронирования в словарь для сериализации."""
        b_date = (
            self.booking_date.isoformat()
            if isinstance(self.booking_date, date)
            else str(self.booking_date)
        )
        return {
            "id": self.id,
            "equipment_id": self.equipment.id if self.equipment else 0,
            "user_id": self.user.id if self.user else 0,
            "booking_date": b_date,
            "duration_hours": self.duration_hours,
            "cost": self.cost,
            "is_cancelled": self.is_cancelled,
        }

    def __str__(self) -> str:
        """Строковое представление объекта бронирования."""
        eq_name = self.equipment.name if self.equipment else "-"
        u_name = self.user.name if self.user else "-"
        state = "[ОТМЕНЕНО]" if self.is_cancelled else "[АКТИВНО]"
        return (
            f"Заявка #{self.id} {state}: {eq_name} | {u_name} | "
            f"Дата: {self.booking_date} | {self.duration_hours} ч. | "
            f"{self.cost} руб."
        )


def is_equipment_available(
    bookings: list[Booking],
    equipment: Equipment | int,
    booking_date: date | str,
) -> bool:
    """Проверить, свободно ли оборудование на указанную дату.

    Отмененные бронирования не блокируют оборудование.
    """
    eq_id = equipment.id if isinstance(equipment, Equipment) else equipment
    if isinstance(booking_date, str):
        booking_date = date.fromisoformat(booking_date)

    for booking in bookings:
        if getattr(booking, "is_cancelled", False):
            continue
        if hasattr(booking, "equipment") and booking.equipment:
            b_eq_id = booking.equipment.id
        elif isinstance(booking, dict):
            b_eq_id = booking.get("equipment_id")
        else:
            continue

        b_date = getattr(booking, "booking_date", None)
        if b_date is None and isinstance(booking, dict):
            b_date = booking.get("booking_date")
        if isinstance(b_date, str):
            b_date = date.fromisoformat(b_date)

        if b_eq_id == eq_id and b_date == booking_date:
            return False
    return True


is_room_available = is_equipment_available


def calculate_booking_cost(
    rate: float,
    hours: float,
    student: bool,
) -> float:
    """Рассчитать стоимость сеанса с учетом скидки (сохранена из ПР1)."""
    base_cost = rate * hours
    if student:
        discount = 0.5
        total_cost = base_cost - (base_cost * discount)
    else:
        total_cost = base_cost
    return round(total_cost, 2)


def create_booking(
    bookings: list[Booking],
    equipment: Equipment | int,
    booking_date: date | str,
    user: Optional[User] = None,
    duration_hours: float = 1.0,
    cost: Optional[float] = None,
    user_id: Optional[int] = None,
) -> Optional[Booking]:
    """Создать и вернуть объект Booking, если оборудование свободно."""
    if not is_equipment_available(bookings, equipment, booking_date):
        return None

    booking_id = max((b.id for b in bookings), default=0) + 1

    # Поддержка вызова со старой сигнатурой ПР2
    if isinstance(equipment, int):
        from .equipment import Equipment as EqClass
        equipment = EqClass(
            equipment_id=equipment,
            name=f"Оборудование #{equipment}",
        )
    if user is None and user_id is not None:
        from .users import User as UserClass
        user = UserClass(
            user_id=user_id,
            name=f"Пользователь #{user_id}",
        )
    elif user is None:
        from .users import User as UserClass
        user = UserClass(
            user_id=1,
            name="Не указан",
        )

    if cost is None:
        discount = user.get_discount() if hasattr(user, "get_discount") else (
            0.5 if user.is_student() else 0.0
        )
        base = equipment.hourly_rate * duration_hours
        cost = round(base * (1.0 - discount), 2)

    new_booking = Booking(
        booking_id=booking_id,
        equipment=equipment,
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
    """Отменить бронирование, изменив статус объекта Booking."""
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
    """Вернуть текстовый статус доступности (сохранена из ПР1)."""
    if is_available:
        return "Оборудование доступно для бронирования"
    return "Оборудование уже занято"


def get_booking_statistics(bookings: list[Booking]) -> dict:
    """Собрать статистику по списку бронирований лаборатории."""
    active_bookings = [
        b for b in bookings
        if not getattr(b, "is_cancelled", False)
    ]
    booked_ids = set()
    total_cost = 0.0
    for b in active_bookings:
        if hasattr(b, "equipment") and b.equipment:
            booked_ids.add(b.equipment.id)
        elif isinstance(b, dict) and "equipment_id" in b:
            booked_ids.add(b["equipment_id"])
        cost_val = getattr(b, "cost", None)
        if cost_val is None and isinstance(b, dict):
            cost_val = b.get("cost", 0.0)
        total_cost += cost_val or 0.0

    return {
        "bookings_count": len(active_bookings),
        "total_bookings": len(bookings),
        "unique_equipment": len(booked_ids),
        "total_cost": round(total_cost, 2),
    }


def show_bookings(bookings: list[Booking]) -> None:
    """Вывести список бронирований в виде таблицы."""
    if not bookings:
        print("Список бронирований пуст.")
        return
    print()
    print(
        f"{'ID':<4}{'Оборудование':<32}{'Пользователь':<20}"
        f"{'Дата':<12}{'Часы':<6}{'Сумма':<8}Статус"
    )
    print("-" * 92)
    for item in bookings:
        eq_name = (
            item.equipment.name[:30]
            if (hasattr(item, "equipment") and item.equipment)
            else "-"
        )
        user_name = (
            item.user.name[:18]
            if (hasattr(item, "user") and item.user)
            else "-"
        )
        b_date = getattr(item, "booking_date", "-")
        duration = getattr(item, "duration_hours", 0.0)
        cost = getattr(item, "cost", 0.0)
        status = getattr(item, "status", "Подтверждено")
        print(
            f"{item.id:<4}{eq_name:<32}{user_name:<20}"
            f"{b_date!s:<12}{duration:<6}{cost:<8}{status}"
        )
