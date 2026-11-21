from django import forms
from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible

from rooms.models import Room


@deconstructible
class MinimumCapacityValidator:
    def __init__(self, minimum: int = 1):
        self.minimum = minimum

    def __call__(self, value):
        if value is None or value < self.minimum:
            raise ValidationError(
                "Вместимость должна быть не меньше %(minimum)s.",
                params={"minimum": self.minimum},
            )


class RoomForm(forms.ModelForm):
    capacity = forms.IntegerField(
        min_value=1,
        initial=1,
        label="Вместимость",
        help_text=(
            "Укажите максимальное количество человек, которое может "
            "находиться в помещении."
        ),
        validators=[MinimumCapacityValidator(1)],
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "min": 1,
            }
        ),
    )

    class Meta:
        model = Room
        fields = [
            "name",
            "inventory_number",
            "capacity",
            "required_level",
            "hourly_rate",
            "operational",
            "under_maintenance",
            "image",
        ]
        labels = {
            "name": "Название помещения / оборудования",
            "inventory_number": "Инвентарный номер",
            "capacity": "Вместимость",
            "required_level": "Требуемый уровень допуска",
            "hourly_rate": "Почасовая ставка (руб/ч)",
            "operational": "Исправно",
            "under_maintenance": "На техническом обслуживании",
            "image": "Изображение",
        }
        help_texts = {
            "required_level": "Уровень допуска от 1 до 3.",
            "image": "Загрузите фотографию помещения или прибора.",
        }
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Введите название помещения или прибора",
                }
            ),
            "inventory_number": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Например: EQ-301",
                }
            ),
            "required_level": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 1,
                    "max": 3,
                }
            ),
            "hourly_rate": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 0,
                    "step": "0.01",
                }
            ),
            "operational": forms.CheckboxInput(
                attrs={"class": "form-check-input"},
            ),
            "under_maintenance": forms.CheckboxInput(
                attrs={"class": "form-check-input"},
            ),
            "image": forms.ClearableFileInput(
                attrs={"class": "form-control"},
            ),
        }

    def clean_name(self):
        name = self.cleaned_data["name"].strip()
        if not name:
            raise ValidationError("Название не должно быть пустым.")
        return name

    def clean_hourly_rate(self):
        hourly_rate = self.cleaned_data["hourly_rate"]
        if hourly_rate is not None and hourly_rate < 0:
            raise ValidationError(
                "Почасовая ставка не может быть отрицательной."
            )
        return hourly_rate
