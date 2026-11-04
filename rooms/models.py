from django.db import models


class Room(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name="Название помещения",
    )
    capacity = models.PositiveIntegerField(
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
        verbose_name="Требуемый уровень",
    )
    hourly_rate = models.FloatField(
        default=0.0,
        verbose_name="Почасовая ставка",
    )

    def is_suitable_for(self, people_count: int) -> bool:
        return self.capacity >= people_count

    def __str__(self) -> str:
        return self.name

    class Meta:
        ordering = ["name"]
        verbose_name = "Помещение"
        verbose_name_plural = "Помещения"
