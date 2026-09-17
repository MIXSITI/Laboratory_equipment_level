from datetime import date


def is_equipment_available(
    bookings: list[dict],
    equipment_id: int,
    booking_date: date | str,
) -> bool:
    if isinstance(booking_date, str):
        booking_date = date.fromisoformat(booking_date)
    for booking in bookings:
        target_date = booking["booking_date"]
        if isinstance(target_date, str):
            target_date = date.fromisoformat(target_date)
        same_item = booking["equipment_id"] == equipment_id
        same_date = target_date == booking_date
        if same_item and same_date:
            return False
    return True


def create_booking(
    bookings: list[dict],
    equipment_id: int,
    booking_date: date,
    duration_hours: float = 1.0,
    user_id: int | None = None,
    cost: float = 0.0,
) -> dict | None:
    if not is_equipment_available(bookings, equipment_id, booking_date):
        return None
    booking_id = max((item["id"] for item in bookings), default=0) + 1
    booking = {
        "id": booking_id,
        "equipment_id": equipment_id,
        "user_id": user_id,
        "booking_date": booking_date,
        "duration_hours": duration_hours,
        "cost": cost,
    }
    bookings.append(booking)
    return booking


def cancel_booking(bookings: list[dict], booking_id: int) -> bool:
    for index, booking in enumerate(bookings):
        if booking["id"] == booking_id:
            del bookings[index]
            return True
    return False


def get_booking_status(is_available: bool) -> str:
    if is_available:
        return "Оборудование доступно для бронирования"
    return "Оборудование уже занято"


def calculate_booking_cost(
    rate: float,
    hours: float,
    student: bool,
) -> float:
    base_cost = rate * hours
    if student:
        discount = 0.5
        total_cost = base_cost - (base_cost * discount)
    else:
        total_cost = base_cost
    return round(total_cost, 2)


def get_booking_statistics(bookings: list[dict]) -> dict:
    booked_ids = {
        item["equipment_id"]
        for item in bookings
        if "equipment_id" in item
    }
    total_cost = sum(item.get("cost", 0.0) for item in bookings)
    return {
        "bookings_count": len(bookings),
        "unique_equipment": len(booked_ids),
        "total_cost": round(total_cost, 2),
    }
