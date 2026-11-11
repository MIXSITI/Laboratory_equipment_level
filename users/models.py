from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class User(models.Model):
    ROLE_STUDENT = "студент"
    ROLE_STAFF = "сотрудник"
    ROLE_CHOICES = [
        (ROLE_STUDENT, "Студент"),
        (ROLE_STAFF, "Сотрудник"),
    ]

    name = models.CharField(
        max_length=200,
        verbose_name="Имя пользователя",
    )
    email = models.EmailField(
        verbose_name="Электронная почта",
    )
    role = models.CharField(
        max_length=50,
        choices=ROLE_CHOICES,
        default=ROLE_STUDENT,
        verbose_name="Роль",
    )
    access_level = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(3)],
        verbose_name="Уровень доступа",
    )
    briefing_passed = models.BooleanField(
        default=True,
        verbose_name="Инструктаж пройден",
    )

    def has_access(self, required_level: int) -> bool:
        if not self.briefing_passed:
            return False
        return self.access_level >= required_level

    def is_student(self) -> bool:
        return self.role.strip().lower() == self.ROLE_STUDENT

    def __str__(self) -> str:
        return self.name

    class Meta:
        ordering = ["name"]
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
