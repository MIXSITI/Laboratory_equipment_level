"""Функции для работы с пользователями лаборатории."""


def add_user(
    users: dict[int, dict],
    name: str,
    role: str = "студент",
    access_level: int = 1,
    briefing_passed: bool = False,
) -> None:
    """Добавить пользователя в словарь users."""
    user_id = max(users.keys(), default=0) + 1
    users[user_id] = {
        "id": user_id,
        "name": name,
        "role": role,
        "access_level": access_level,
        "briefing_passed": briefing_passed,
    }


def find_user(users: dict[int, dict], query: str) -> list[dict]:
    """Найти пользователей по подстроке ФИО."""
    query_lower = query.lower()
    found = []
    for item in users.values():
        if query_lower in item.get("name", "").lower():
            found.append(item)
    return found


def check_user_access(
    user_level: int,
    min_level: int,
    briefing_passed: bool,
) -> bool:
    """Проверить соответствие прав пользователя требованиям прибора.

    Функция сохранена из начального сценария ПР1.
    """
    if not briefing_passed:
        return False
    if user_level >= min_level:
        return True
    return False


def get_user_by_id(users: dict[int, dict], user_id: int | None) -> dict | None:
    """Вернуть запись пользователя по идентификатору."""
    if user_id is None:
        return None
    return users.get(user_id)
