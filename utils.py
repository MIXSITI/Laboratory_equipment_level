"""Вспомогательные функции ввода данных."""

from datetime import date, datetime


def input_int(prompt: str) -> int:
    """Запросить у пользователя целое число."""
    while True:
        raw_value = input(prompt).strip()
        try:
            return int(raw_value)
        except ValueError:
            print("Ошибка: введите целое число.")


def input_float(prompt: str) -> float:
    """Запросить у пользователя вещественное число."""
    while True:
        raw_value = input(prompt).strip()
        try:
            return float(raw_value.replace(",", "."))
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
