from django.core.validators import MinValueValidator
from django.db import models

from rooms.models import Room
from users.models import User


class BookingQuerySet(models.QuerySet):
    def active(self):
        return self.filter(status=self.model.Status.ACTIVE)

    def cancelled(self):
        return self.filter(status=self.model.Status.CANCELLED)

    def completed(self):
        return self.filter(status=self.model.Status.COMPLETED)

    def for_date(self, selected_date):
        return self.filter(booking_date=selected_date)


class BookingManager(models.Manager.from_queryset(BookingQuerySet)):
    pass


class Booking(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Активно"
        CANCELLED = "cancelled", "Отменено"
        COMPLETED = "completed", "Завершено"

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
    status = models.CharField(
        max_length=12,
        choices=Status.choices,
        default=Status.ACTIVE,
        verbose_name="Статус бронирования",
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name="Примечание",
    )

    objects = BookingManager()

    def cancel(self) -> None:
        self.status = self.Status.CANCELLED
        self.save(update_fields=["status"])

    def __str__(self) -> str:
        return f"{self.room} — {self.booking_date} ({self.user})"

    class Meta:
        ordering = ["booking_date", "pk"]
        verbose_name = "Бронирование"
        verbose_name_plural = "Бронирования"
