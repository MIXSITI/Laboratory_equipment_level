import sys
from pathlib import Path

# Поддержка прямого запуска файла: python tests/test_users.py
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import pytest  # noqa: E402
from models.users import (  # noqa: E402
    Staff,
    Student,
    User,
    add_user,
    check_user_access,
    find_user,
    get_user_by_id,
)


def test_user_creation():
    """Проверить создание базового объекта User и его атрибуты."""
    user = User(
        user_id=1,
        name="Иванов Алексей Сергеевич",
        role="студент",
        access_level=2,
        briefing_passed=True,
        email="ivanov@example.com",
    )
    assert user.id == 1
    assert user.name == "Иванов Алексей Сергеевич"
    assert user.role == "студент"
    assert user.access_level == 2
    assert user.briefing_passed is True
    assert user.email == "ivanov@example.com"


def test_user_str():
    """Проверить строковое представление объекта User (__str__)."""
    user = User(1, "Петров Дмитрий", "студент", 1, False)
    text = str(user)
    assert "[1] Петров Дмитрий" in text
    assert "студент" in text
    assert "ТБ: нет" in text


def test_user_has_access():
    """Проверить метод has_access у объекта User."""
    trained_user = User(1, "Алексей", access_level=2, briefing_passed=True)
    untrained_user = User(2, "Дмитрий", access_level=3, briefing_passed=False)

    assert trained_user.has_access(required_level=2) is True
    assert trained_user.has_access(required_level=1) is True
    assert trained_user.has_access(required_level=3) is False

    assert untrained_user.has_access(required_level=1) is False


def test_student_and_staff_inheritance_and_polymorphism():
    """Проверить наследование и полиморфизм расчета скидки."""
    student = Student(
        1, "Иванов Алексей", access_level=2, briefing_passed=True
    )
    staff = Staff(
        2, "Сидорова Мария", access_level=3, briefing_passed=True
    )

    assert isinstance(student, User)
    assert isinstance(staff, User)

    assert student.role == "студент"
    assert staff.role == "сотрудник"

    # Полиморфный вызов get_discount()
    assert student.get_discount() == 0.5
    assert staff.get_discount() == 0.0


def test_user_from_data():
    """Проверить фабричный метод @classmethod from_data."""
    student_data = {
        "id": 1,
        "name": "Иванов Алексей",
        "role": "студент",
        "access_level": 2,
        "briefing_passed": True,
        "email": "ivanov@edu.mirea.ru",
    }
    staff_data = {
        "id": 2,
        "name": "Сидорова Мария",
        "role": "сотрудник",
        "access_level": 3,
        "briefing_passed": True,
    }

    student_obj = User.from_data(student_data)
    staff_obj = User.from_data(staff_data)

    assert isinstance(student_obj, Student)
    assert student_obj.email == "ivanov@edu.mirea.ru"
    assert isinstance(staff_obj, Staff)
    assert staff_obj.email == ""


def test_user_to_dict():
    """Проверить сериализацию объекта в словарь JSON."""
    user = Student(1, "Алексей", access_level=2, briefing_passed=True)
    data = user.to_dict()
    assert data["id"] == 1
    assert data["name"] == "Алексей"
    assert data["role"] == "студент"
    assert data["access_level"] == 2
    assert data["briefing_passed"] is True


def test_user_static_validation():
    """Проверить метод @staticmethod validate_level."""
    assert User.validate_level(1) is True
    assert User.validate_level(3) is True
    assert User.validate_level(0) is False
    assert User.validate_level(4) is False


def test_add_user():
    """Проверить функцию добавления пользователя в коллекцию."""
    users = []
    user = add_user(users, "Иванов Алексей Сергеевич", "студент", 2, True)
    assert len(users) == 1
    assert user.id == 1
    assert isinstance(user, Student)


def test_find_user():
    """Проверить функцию поиска пользователей."""
    users = [
        Student(1, "Иванов Алексей", email="ivanov@example.com"),
        Staff(2, "Петров Дмитрий", email="petrov@example.com"),
    ]
    assert len(find_user(users, "Иванов")) == 1
    assert len(find_user(users, "petrov@example.com")) == 1
    assert len(find_user(users, "Сидоров")) == 0


def test_check_user_access_function():
    """Проверить функцию check_user_access, сохраненную из ПР1."""
    assert check_user_access(2, 2, True) is True
    assert check_user_access(1, 2, True) is False
    assert check_user_access(3, 1, False) is False


def test_get_user_by_id():
    """Проверить получение объекта пользователя по ID."""
    users = [Student(1, "Алексей"), Staff(2, "Мария")]
    assert get_user_by_id(users, 1).name == "Алексей"
    assert get_user_by_id(users, 99) is None
    assert get_user_by_id(users, None) is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
