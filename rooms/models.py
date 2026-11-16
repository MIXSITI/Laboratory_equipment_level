from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Case, Value, When
from django.urls import reverse
from django.utils.text import slugify
from unidecode import unidecode


class Room(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name="Название помещения / оборудования",
    )
    slug = models.SlugField(
        max_length=180,
        unique=True,
        editable=False,
        verbose_name="URL-идентификатор",
    )
    capacity = models.PositiveIntegerField(
        default=1,
        verbose_name="Вместимость",
        help_text=(
            "Укажите максимальное количество человек, которое может "
            "находиться в помещении."
        ),
    )
    is_large = models.GeneratedField(
        expression=Case(
            When(capacity__gte=50, then=Value(True)),
            default=Value(False),
            output_field=models.BooleanField(),
        ),
        output_field=models.BooleanField(),
        db_persist=True,
        verbose_name="Большое помещение",
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

    def _build_slug(self, base_slug: str) -> str:
        suffix = f"-{self.pk}"
        max_len = self._meta.get_field("slug").max_length
        trimmed_base = base_slug[: max_len - len(suffix)].rstrip("-") or "room"
        return f"{trimmed_base}{suffix}"

    def save(self, *args, **kwargs) -> None:
        if not self.slug:
            transliterated_name = unidecode(self.name)
            base_slug = slugify(transliterated_name) or "room"
            if self.pk:
                self.slug = self._build_slug(base_slug)
            else:
                super().save(*args, **kwargs)
                self.slug = self._build_slug(base_slug)
                super().save(update_fields=["slug"])
                return
        super().save(*args, **kwargs)

    def get_absolute_url(self) -> str:
        return reverse(
            "rooms:detail",
            kwargs={"slug": self.slug},
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
