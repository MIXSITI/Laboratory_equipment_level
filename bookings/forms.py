from django import forms

from bookings.models import Booking
from rooms.models import Room
from users.models import User


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
