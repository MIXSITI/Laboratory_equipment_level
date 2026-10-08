from typing import Optional


class User:
    """Базовый класс пользователя лаборатории."""

    def __init__(
        self,
        user_id: int,
        name: str,
        role: str = "студент",
        access_level: int = 1,
        briefing_passed: bool = False,
        email: str = "",
    ) -> None:
        """Инициализировать объект пользователя."""
        self.id = user_id
        self.name = name
        self.role = role
        self.access_level = access_level
        self.briefing_passed = briefing_passed
        self.email = email

    def has_access(self, required_level: int) -> bool:
        """Проверить допуск пользователя к прибору с учетом инструктажа."""
        if not self.briefing_passed:
            return False
        return self.access_level >= required_level

    def is_student(self) -> bool:
        """Проверить, является ли пользователь студентом."""
        return self.role.strip().lower() == "студент"

    def get_discount(self) -> float:
        """Вернуть базовый размер скидки на аренду оборудования."""
        return 0.5 if self.is_student() else 0.0

    @staticmethod
    def validate_level(level: int) -> bool:
        """Проверить корректность значения уровня допуска."""
        return 1 <= level <= 3

    @classmethod
    def from_data(cls, data: dict) -> "User":
        """Создать объект пользователя из словаря данных JSON."""
        user_id = int(data.get("id", data.get("user_id", 0)))
        name = str(data.get("name", ""))
        role = str(data.get("role", "студент")).strip().lower()
        level = int(data.get("access_level", 1))
        briefing = bool(data.get("briefing_passed", False))
        email = str(data.get("email", ""))
        if role == "студент":
            return Student(
                user_id=user_id,
                name=name,
                access_level=level,
                briefing_passed=briefing,
                email=email,
            )
        if role == "сотрудник":
            return Staff(
                user_id=user_id,
                name=name,
                access_level=level,
                briefing_passed=briefing,
                email=email,
            )
        return cls(
            user_id=user_id,
            name=name,
            role=role,
            access_level=level,
            briefing_passed=briefing,
            email=email,
        )

    def to_dict(self) -> dict:
        """Преобразовать объект пользователя в словарь для сериализации."""
        res = {
            "id": self.id,
            "name": self.name,
            "role": self.role,
            "access_level": self.access_level,
            "briefing_passed": self.briefing_passed,
        }
        if self.email:
            res["email"] = self.email
        return res

    def __str__(self) -> str:
        """Строковое представление объекта пользователя."""
        briefing = "да" if self.briefing_passed else "нет"
        return (
            f"[{self.id}] {self.name} ({self.role}, "
            f"допуск: {self.access_level}, ТБ: {briefing})"
        )


class Student(User):
    """Студент лаборатории (наследует User, скидка 50%)."""

    def __init__(
        self,
        user_id: int,
        name: str,
        access_level: int = 1,
        briefing_passed: bool = False,
        email: str = "",
    ) -> None:
        """Инициализировать профиль студента."""
        super().__init__(
            user_id=user_id,
            name=name,
            role="студент",
            access_level=access_level,
            briefing_passed=briefing_passed,
            email=email,
        )

    def get_discount(self) -> float:
        """Студент имеет льготную скидку 50% на бронирование."""
        return 0.5


class Staff(User):
    """Сотрудник лаборатории (наследует User, без скидки)."""

    def __init__(
        self,
        user_id: int,
        name: str,
        access_level: int = 1,
        briefing_passed: bool = False,
        email: str = "",
    ) -> None:
        """Инициализировать профиль сотрудника."""
        super().__init__(
            user_id=user_id,
            name=name,
            role="сотрудник",
            access_level=access_level,
            briefing_passed=briefing_passed,
            email=email,
        )

    def get_discount(self) -> float:
        """Сотрудник оплачивает полную почасовую ставку."""
        return 0.0


def _get_users(collection: list[User] | dict) -> list[User]:
    """Вспомогательная функция извлечения списка пользователей."""
    if isinstance(collection, dict):
        return list(collection.values())
    return list(collection)


def add_user(
    users: list[User] | dict,
    name: str,
    role: str = "студент",
    access_level: int = 1,
    briefing_passed: bool = False,
    email: str = "",
) -> User:
    """Создать объект User/Student/Staff и добавить в коллекцию."""
    items = _get_users(users)
    user_id = max((u.id for u in items), default=0) + 1
    role_norm = role.strip().lower()
    if role_norm == "студент":
        user = Student(
            user_id=user_id,
            name=name,
            access_level=access_level,
            briefing_passed=briefing_passed,
            email=email,
        )
    elif role_norm == "сотрудник":
        user = Staff(
            user_id=user_id,
            name=name,
            access_level=access_level,
            briefing_passed=briefing_passed,
            email=email,
        )
    else:
        user = User(
            user_id=user_id,
            name=name,
            role=role,
            access_level=access_level,
            briefing_passed=briefing_passed,
            email=email,
        )

    if isinstance(users, list):
        users.append(user)
    elif isinstance(users, dict):
        users[user_id] = user
    return user


def find_user(users: list[User] | dict, query: str) -> list[User]:
    """Найти пользователей по подстроке ФИО или email."""
    query_lower = query.lower()
    found: list[User] = []
    for item in _get_users(users):
        name_match = query_lower in item.name.lower()
        email_match = bool(item.email and query_lower in item.email.lower())
        if name_match or email_match:
            found.append(item)
    return found


def check_user_access(
    user_level: int,
    min_level: int,
    briefing_passed: bool,
) -> bool:
    """Проверить соответствие прав пользователя."""
    if not briefing_passed:
        return False
    return user_level >= min_level


def get_user_by_id(
    users: list[User] | dict,
    user_id: Optional[int],
) -> Optional[User]:
    """Вернуть объект пользователя по идентификатору."""
    if user_id is None:
        return None
    for item in _get_users(users):
        if item.id == user_id:
            return item
    return None


def show_users(users: list[User] | dict) -> None:
    """Вывести список пользователей в виде таблицы."""
    items = _get_users(users)
    if not items:
        print("Список пользователей пуст.")
        return
    print()
    print(f"{'ID':<4}{'ФИО':<32}{'Статус':<12}{'Ур.':<4}ТБ")
    print("-" * 60)
    for item in items:
        briefing = "да" if item.briefing_passed else "нет"
        print(
            f"{item.id:<4}{item.name[:30]:<32}"
            f"{item.role[:10]:<12}{item.access_level:<4}{briefing}"
        )
