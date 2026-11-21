from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone

from bookings.models import Booking
from rooms.models import Room
from users.models import User


def validate_positive_duration(value):
    if value is None or value <= 0:
        raise ValidationError(
            "Длительность бронирования должна быть больше нуля."
        )
    if value > 12:
        raise ValidationError(
            "Длительность бронирования не может превышать 12 часов."
        )


class BookingFilterForm(forms.Form):
    search = forms.CharField(
        required=False,
        label="Поиск (прибор или пользователь)",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Например: Спектрофотометр или Иванов",
            }
        ),
    )
    date = forms.DateField(
        required=False,
        label="Дата бронирования",
        widget=forms.DateInput(
            attrs={
                "type": "date",
                "class": "form-control",
            }
        ),
        error_messages={
            "invalid": "Укажите корректную дату.",
        },
    )
    status = forms.ChoiceField(
        required=False,
        label="Статус бронирования",
        choices=[
            *Booking.Status.choices,
            ("all", "Все статусы"),
        ],
        widget=forms.Select(
            attrs={"class": "form-select"},
        ),
    )
    room = forms.ModelChoiceField(
        queryset=Room.objects.order_by("name"),
        required=False,
        label="Помещение / прибор",
        empty_label="Все помещения",
        widget=forms.Select(
            attrs={"class": "form-select"},
        ),
    )
    user = forms.ModelChoiceField(
        queryset=User.objects.order_by("name"),
        required=False,
        label="Пользователь",
        empty_label="Все пользователи",
        widget=forms.Select(
            attrs={"class": "form-select"},
        ),
    )
    role = forms.ChoiceField(
        required=False,
        label="Роль пользователя",
        choices=[
            ("", "Все роли"),
            *User.ROLE_CHOICES,
        ],
        widget=forms.Select(
            attrs={"class": "form-select"},
        ),
    )
    sort = forms.ChoiceField(
        required=False,
        label="Сортировать по",
        choices=[
            ("date", "По дате"),
            ("room", "По помещению / прибору"),
            ("user", "По пользователю"),
            ("cost", "По стоимости (по убыванию)"),
        ],
        widget=forms.Select(
            attrs={"class": "form-select"},
        ),
    )


class BookingForm(forms.ModelForm):
    duration_hours = forms.FloatField(
        min_value=0.5,
        initial=1.0,
        label="Длительность (часы)",
        help_text="Укажите длительность от 0.5 до 12 часов.",
        validators=[validate_positive_duration],
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "step": "0.5",
                "min": "0.5",
                "max": "12",
            }
        ),
    )

    class Meta:
        model = Booking
        fields = [
            "room",
            "booking_date",
            "user",
            "duration_hours",
            "notes",
        ]
        labels = {
            "room": "Помещение / оборудование",
            "booking_date": "Дата бронирования",
            "user": "Пользователь",
            "duration_hours": "Длительность (часы)",
            "notes": "Примечание",
        }
        help_texts = {
            "room": "Выберите помещение или оборудование для бронирования.",
            "booking_date": "Укажите дату проведения мероприятия.",
            "user": "Выберите пользователя, оформляющего заявку.",
            "notes": "Дополнительные пожелания или цель использования.",
        }
        widgets = {
            "room": forms.Select(
                attrs={"class": "form-select"},
            ),
            "booking_date": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control",
                },
                format="%Y-%m-%d",
            ),
            "user": forms.Select(
                attrs={"class": "form-select"},
            ),
            "notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "cols": 40,
                    "placeholder": "Цель бронирования или комментарий",
                }
            ),
        }

    def clean_booking_date(self):
        booking_date = self.cleaned_data["booking_date"]
        if booking_date < timezone.localdate():
            raise ValidationError(
                "Нельзя создать бронирование на прошедшую дату."
            )
        return booking_date

    def clean(self):
        cleaned_data = super().clean()
        room = cleaned_data.get("room")
        if room and not room.is_ready:
            raise ValidationError(
                f"Ресурс «{room.name}» недоступен: "
                f"{room.check_readiness().lower()}."
            )
        return cleaned_data
