from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Room(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name="Название помещения / оборудования",
    )
    capacity = models.PositiveIntegerField(
        default=1,
        verbose_name="Вместимость",
    )
    inventory_number = models.CharField(
        max_length=50,
        blank=True,
        default="",
        verbose_name="Инвентарный номер",
    )
    operational = models.BooleanField(
        default=True,
        verbose_name="Исправно",
    )
    under_maintenance = models.BooleanField(
        default=False,
        verbose_name="На обслуживании",
    )
    required_level = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(3)],
        verbose_name="Требуемый уровень",
    )
    hourly_rate = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0)],
        verbose_name="Почасовая ставка",
    )

    @property
    def is_ready(self) -> bool:
        return self.operational and not self.under_maintenance

    def check_readiness(self) -> str:
        if not self.operational:
            return "Оборудование неисправно"
        if self.under_maintenance:
            return "Оборудование на техническом обслуживании"
        return "Оборудование готово к работе"

    def is_suitable_for_level(self, user_level: int) -> bool:
        return user_level >= self.required_level

    def is_suitable_for(self, people_count: int) -> bool:
        return self.capacity >= people_count

    def __str__(self) -> str:
        return self.name

    class Meta:
        ordering = ["name"]
        verbose_name = "Помещение / оборудование"
        verbose_name_plural = "Помещения и оборудование"
