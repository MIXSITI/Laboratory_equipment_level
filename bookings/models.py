from django.core.validators import MinValueValidator
from django.db import models

from rooms.models import Room
from users.models import User


class Booking(models.Model):
    room = models.ForeignKey(
        Room,
        on_delete=models.PROTECT,
        related_name="bookings",
        verbose_name="Помещение / оборудование",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="bookings",
        verbose_name="Пользователь",
    )
    booking_date = models.DateField(
        verbose_name="Дата бронирования",
    )
    duration_hours = models.FloatField(
        default=1.0,
        validators=[MinValueValidator(0.5)],
        verbose_name="Длительность (часы)",
    )
    cost = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0)],
        verbose_name="Стоимость",
    )
    is_cancelled = models.BooleanField(
        default=False,
        verbose_name="Бронирование отменено",
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name="Примечание",
    )

    def cancel(self) -> None:
        self.is_cancelled = True
        self.save(update_fields=["is_cancelled"])

    @property
    def status(self) -> str:
        return "Отменено" if self.is_cancelled else "Активно"

    def __str__(self) -> str:
        return f"{self.room} — {self.booking_date} ({self.user})"

    class Meta:
        ordering = ["booking_date", "pk"]
        verbose_name = "Бронирование"
        verbose_name_plural = "Бронирования"
