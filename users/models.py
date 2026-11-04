from django.db import models


class User(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name="Имя пользователя",
    )
    email = models.EmailField(
        verbose_name="Электронная почта",
    )
    role = models.CharField(
        max_length=50,
        default="студент",
        verbose_name="Роль",
    )
    access_level = models.PositiveIntegerField(
        default=1,
        verbose_name="Уровень доступа",
    )
    briefing_passed = models.BooleanField(
        default=True,
        verbose_name="Инструктаж пройден",
    )

    def __str__(self) -> str:
        return self.name

    class Meta:
        ordering = ["name"]
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
