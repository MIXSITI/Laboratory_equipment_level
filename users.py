"""Модуль работы с пользователями (делегирует в models.users)."""

from models.users import (
    Staff,
    Student,
    User,
    add_user,
    check_user_access,
    find_user,
    get_user_by_id,
    show_users,
)

__all__ = [
    "User",
    "Student",
    "Staff",
    "add_user",
    "find_user",
    "check_user_access",
    "get_user_by_id",
    "show_users",
]
