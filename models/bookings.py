from datetime import date
from typing import Optional

from .equipment import Equipment
from .users import User


class Period:
    """Сущность периода бронирования: дата и длительность в часах."""

    def __init__(
        self,
        booking_date: date | str,
        duration_hours: float = 1.0,
    ) -> None:
        """Инициализировать период бронирования."""
        if isinstance(booking_date, str):
            self.date: date = date.fromisoformat(booking_date)
        else:
            self.date = booking_date
        self.duration_hours = duration_hours

    def __str__(self) -> str:
        """Строковое представление периода бронирования."""
        return f"{self.date} ({self.duration_hours} ч.)"


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
        """Создать объект бронирования оборудования."""
        self.id = booking_id
        self.equipment = equipment
        self.user = user
        self.cost = cost
        self.is_cancelled = is_cancelled
        self.period = Period(booking_date, duration_hours)

    @property
    def booking_date(self) -> date:
        """Календарная дата бронирования."""
        return self.period.date

    @booking_date.setter
    def booking_date(self, value: date | str) -> None:
        if isinstance(value, str):
            self.period.date = date.fromisoformat(value)
        else:
            self.period.date = value

    @property
    def duration_hours(self) -> float:
        """Длительность сеанса в часах."""
        return self.period.duration_hours

    @duration_hours.setter
    def duration_hours(self, value: float) -> None:
        self.period.duration_hours = value

    @property
    def room(self) -> Equipment:
        """Псевдоним прибора."""
        return self.equipment

    @property
    def status(self) -> str:
        """Текстовый статус состояния бронирования."""
        return "Отменено" if self.is_cancelled else "Подтверждено"

    def cancel(self) -> None:
        """Отменить бронирование, изменив его состояние."""
        self.is_cancelled = True

    def to_dict(self) -> dict:
        """Преобразовать объект бронирования в структуру JSON."""
        return {
            "id": self.id,
            "equipment_id": self.equipment.id if self.equipment else 0,
            "user_id": self.user.id if self.user else 0,
            "booking_date": self.booking_date.isoformat(),
            "duration_hours": self.duration_hours,
            "cost": self.cost,
            "is_cancelled": self.is_cancelled,
        }

    def __str__(self) -> str:
        """Вернуть строковое представление бронирования."""
        eq_name = self.equipment.name if self.equipment else "-"
        u_name = self.user.name if self.user else "-"
        state = "[ОТМЕНЕНО]" if self.is_cancelled else "[АКТИВНО]"
        return (
            f"Заявка #{self.id} {state}: {eq_name} | {u_name} | "
            f"Период: {self.period} | {self.cost} руб."
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

        b_eq = getattr(booking, "equipment", None)
        if b_eq is None and hasattr(booking, "room"):
            b_eq = booking.room

        if b_eq:
            b_eq_id = b_eq.id
        elif isinstance(booking, dict):
            b_eq_id = booking.get("equipment_id", booking.get("room_id"))
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
    """Рассчитать стоимость бронирования со скидкой."""
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
    room: Optional[Equipment | int] = None,
) -> Optional[Booking]:
    """Создать новое бронирование и добавить его в коллекцию."""
    target_equipment = equipment if equipment is not None else room
    if target_equipment is None:
        return None

    if not is_equipment_available(bookings, target_equipment, booking_date):
        return None

    booking_id = max((b.id for b in bookings), default=0) + 1

    if isinstance(target_equipment, int):
        from .equipment import Equipment as EqClass
        target_equipment = EqClass(
            equipment_id=target_equipment,
            name=f"Оборудование #{target_equipment}",
        )

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
        base = target_equipment.hourly_rate * duration_hours
        cost = round(base * (1.0 - discount), 2)

    new_booking = Booking(
        booking_id=booking_id,
        equipment=target_equipment,
        booking_date=booking_date,
        user=user,
        duration_hours=duration_hours,
        cost=cost,
        is_cancelled=False,
    )
    bookings.append(new_booking)
    return new_booking


def find_booking_by_id(
    bookings: list[Booking],
    booking_id: int,
) -> Optional[Booking]:
    """Найти бронирование по идентификатору."""
    for booking in bookings:
        b_id = booking.id if hasattr(booking, "id") else booking.get("id")
        if b_id == booking_id:
            return booking
    return None


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
    """Вернуть текстовый статус доступности оборудования."""
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
        eq = getattr(b, "equipment", None)
        if eq is None and hasattr(b, "room"):
            eq = b.room
        if eq:
            booked_ids.add(eq.id)
        elif isinstance(b, dict):
            eq_id = b.get("equipment_id", b.get("room_id"))
            if eq_id:
                booked_ids.add(eq_id)
        cost_val = getattr(b, "cost", None)
        if cost_val is None and isinstance(b, dict):
            cost_val = b.get("cost", 0.0)
        total_cost += cost_val or 0.0

    return {
        "bookings_count": len(active_bookings),
        "total_bookings": len(bookings),
        "unique_equipment": len(booked_ids),
        "unique_rooms": len(booked_ids),
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
        eq = getattr(item, "equipment", None)
        if eq is None and hasattr(item, "room"):
            eq = item.room
        eq_name = eq.name[:30] if eq else "-"
        u_name = item.user.name[:18] if getattr(item, "user", None) else "-"
        b_date = getattr(item, "booking_date", "-")
        duration = getattr(item, "duration_hours", 0.0)
        cost = getattr(item, "cost", 0.0)
        status = getattr(item, "status", "Подтверждено")
        print(
            f"{item.id:<4}{eq_name:<32}{u_name:<20}"
            f"{b_date!s:<12}{duration:<6}{cost:<8}{status}"
        )
