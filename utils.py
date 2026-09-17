"""Вспомогательные функции ввода данных и интроспекции."""

from datetime import date, datetime


def input_int(
    prompt: str,
    min_value: int | None = None,
    max_value: int | None = None,
) -> int:
    """Запросить у пользователя целое число с опциональной валидацией."""
    while True:
        raw_value = input(prompt).strip()
        try:
            value = int(raw_value)
            if min_value is not None and value < min_value:
                print(f"Ошибка: число должно быть не меньше {min_value}.")
                continue
            if max_value is not None and value > max_value:
                print(f"Ошибка: число должно быть не больше {max_value}.")
                continue
            return value
        except ValueError:
            print("Ошибка: введите целое число.")


def input_float(
    prompt: str,
    min_value: float | None = None,
) -> float:
    """Запросить у пользователя вещественное число."""
    while True:
        raw_value = input(prompt).strip()
        try:
            value = float(raw_value.replace(",", "."))
            if min_value is not None and value < min_value:
                print(f"Ошибка: число должно быть не меньше {min_value}.")
                continue
            return value
        except ValueError:
            print("Ошибка: введите число.")


def input_date(prompt: str) -> date:
    """Запросить у пользователя дату."""
    while True:
        raw_value = input(prompt).strip()
        for fmt in ("%Y-%m-%d", "%d.%m.%Y"):
            try:
                return datetime.strptime(raw_value, fmt).date()
            except ValueError:
                continue
        message = (
            "Ошибка: используйте формат ГГГГ-ММ-ДД или ДД.ММ.ГГГГ."
        )
        print(message)


def inspect_object(obj: object) -> dict:
    """Исследовать объект средствами интроспекции Python."""
    return {
        "type": type(obj).__name__,
        "id": id(obj),
        "callable": callable(obj),
        "attributes_count": len(dir(obj)),
        "doc": getattr(obj, "__doc__", None),
    }
