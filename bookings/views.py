from django.db.models import Avg, Count, F, Max, Min, Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from bookings.models import Booking
from rooms.models import Room
from users.models import User

from .forms import BookingFilterForm, BookingForm


class BookingListView(ListView):
    model = Booking
    template_name = "bookings/booking_list.html"
    context_object_name = "bookings"
    paginate_by = 5
    allow_empty = True
    extra_context = {
        "page_title": "Список бронирований",
        "page_description": "Просмотр и фильтрация активных бронирований",
    }

    def get_queryset(self):
        self.filter_form = BookingFilterForm(
            self.request.GET or None,
            initial={
                "status": Booking.Status.ACTIVE,
                "sort": "date",
            },
        )
        self.filter_valid = (
            self.filter_form.is_bound and self.filter_form.is_valid()
        )

        self.booking_date = None
        self.room_id = None
        self.user_id = None
        self.role = ""
        self.status_param = Booking.Status.ACTIVE
        self.search = ""
        self.sort = "date"
        self.filter_error = None

        if self.filter_form.is_bound:
            if self.filter_valid:
                self.booking_date = self.filter_form.cleaned_data.get("date")
                selected_room = self.filter_form.cleaned_data.get("room")
                selected_user = self.filter_form.cleaned_data.get("user")
                self.room_id = selected_room.pk if selected_room else None
                self.user_id = selected_user.pk if selected_user else None
                self.role = self.filter_form.cleaned_data.get("role") or ""
                self.status_param = (
                    self.filter_form.cleaned_data.get("status")
                    or Booking.Status.ACTIVE
                )
                self.search = (
                    self.filter_form.cleaned_data.get("search") or ""
                ).strip()
                self.sort = self.filter_form.cleaned_data.get("sort") or "date"
            else:
                self.filter_error = (
                    "Проверьте корректность параметров фильтрации."
                )

        if self.status_param == Booking.Status.CANCELLED:
            bookings_data = Booking.objects.cancelled()
        elif self.status_param == Booking.Status.COMPLETED:
            bookings_data = Booking.objects.completed()
        elif self.status_param == "all":
            bookings_data = Booking.objects.all()
        else:
            self.status_param = Booking.Status.ACTIVE
            bookings_data = Booking.objects.active()

        if self.filter_valid:
            if self.booking_date:
                bookings_data = bookings_data.for_date(self.booking_date)
            if self.room_id:
                bookings_data = bookings_data.filter(room_id=self.room_id)
            if self.user_id:
                bookings_data = bookings_data.filter(user_id=self.user_id)
            if self.role:
                bookings_data = bookings_data.filter(user__role=self.role)
            if self.search:
                bookings_data = bookings_data.filter(
                    Q(room__name__icontains=self.search)
                    | Q(user__name__icontains=self.search)
                )

        bookings_data = bookings_data.annotate(
            room_name=F("room__name"),
            capacity=F("room__capacity"),
            user_name=F("user__name"),
            user_role=F("user__role"),
        )

        sort_fields = {
            "date": "booking_date",
            "room": "room__name",
            "user": "user__name",
            "cost": "-cost",
        }
        sort_field = sort_fields.get(self.sort, "booking_date")
        bookings_data = bookings_data.order_by(sort_field, "id")

        return bookings_data.values(
            "id",
            "booking_date",
            "room_name",
            "capacity",
            "user_name",
            "user_role",
            "cost",
            "status",
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_bookings"] = self.get_queryset().count()
        context["form"] = self.filter_form
        context["booking_date"] = self.booking_date
        context["selected_room"] = self.room_id
        context["selected_user"] = self.user_id
        context["selected_role"] = self.role
        context["selected_status"] = self.status_param
        context["status_choices"] = Booking.Status.choices
        context["search_query"] = self.search
        context["sort"] = self.sort
        context["role_choices"] = User.ROLE_CHOICES
        context["rooms"] = Room.objects.order_by("name")
        context["users"] = User.objects.order_by("name")
        context["error"] = self.filter_error
        return context


class BookingDetailView(DetailView):
    model = Booking
    template_name = "bookings/booking_detail.html"
    context_object_name = "booking"
    pk_url_kwarg = "booking_id"

    def get_queryset(self):
        return Booking.objects.select_related("room", "user")


class BookingCreateView(CreateView):
    model = Booking
    form_class = BookingForm
    template_name = "bookings/booking_form.html"
    context_object_name = "booking"
    success_url = reverse_lazy("bookings:bookings")

    def get_initial(self):
        initial = super().get_initial()
        initial["booking_date"] = timezone.localdate()
        return initial

    def _get_booking_user(self):
        auth_user = self.request.user
        if not auth_user.is_authenticated:
            return None

        email = (getattr(auth_user, "email", "") or "").strip()
        if email:
            existing = User.objects.filter(email__iexact=email).first()
            if existing:
                return existing

        full_name = auth_user.get_full_name().strip()
        display_name = full_name or auth_user.get_username()
        existing_by_name = User.objects.filter(
            name__iexact=display_name
        ).first()
        if existing_by_name:
            return existing_by_name

        fallback_email = email or f"{auth_user.get_username()}@roomly.local"
        domain_user, _ = User.objects.get_or_create(
            email=fallback_email,
            defaults={
                "name": display_name,
                "role": (
                    User.ROLE_STAFF
                    if auth_user.is_staff
                    else User.ROLE_STUDENT
                ),
            },
        )
        return domain_user

    def form_valid(self, form):
        if not self.request.user.is_authenticated:
            form.add_error(
                None,
                "Для создания бронирования необходимо войти в систему.",
            )
            return self.form_invalid(form)

        room = form.cleaned_data["room"]
        booking_date = form.cleaned_data["booking_date"]
        is_booked = Booking.objects.active().filter(
            room=room,
            booking_date=booking_date,
        ).exists()
        if is_booked:
            form.add_error(
                None,
                "Выбранное помещение уже забронировано на эту дату.",
            )
            return self.form_invalid(form)

        form.instance.user = self._get_booking_user()
        form.instance.cost = round(
            room.hourly_rate * form.instance.duration_hours,
            2,
        )
        return super().form_valid(form)


class BookingUpdateView(UpdateView):
    model = Booking
    form_class = BookingForm
    template_name = "bookings/booking_form.html"
    context_object_name = "booking"
    pk_url_kwarg = "booking_id"
    success_url = reverse_lazy("bookings:bookings")

    def get_queryset(self):
        return Booking.objects.active()

    def form_valid(self, form):
        room = form.cleaned_data["room"]
        booking_date = form.cleaned_data["booking_date"]
        is_booked = (
            Booking.objects.active()
            .filter(room=room, booking_date=booking_date)
            .exclude(pk=self.object.pk)
            .exists()
        )
        if is_booked:
            form.add_error(
                None,
                "Выбранное помещение уже забронировано на эту дату.",
            )
            return self.form_invalid(form)

        form.instance.cost = round(
            room.hourly_rate * form.instance.duration_hours,
            2,
        )
        return super().form_valid(form)


@require_POST
def booking_cancel(request, booking_id: int):
    booking = get_object_or_404(
        Booking.objects.active(),
        pk=booking_id,
    )
    booking.cancel()
    return redirect("bookings:bookings")


def statistics(request):
    statistics_data = (
        Room.objects
        .annotate(
            bookings_count=Count(
                "bookings",
                filter=Q(bookings__status=Booking.Status.ACTIVE),
            ),
            room_revenue=Sum(
                "bookings__cost",
                filter=Q(bookings__status=Booking.Status.ACTIVE),
            ),
            room_name=F("name"),
            room_id=F("id"),
        )
        .values(
            "room_id",
            "room_name",
            "bookings_count",
            "room_revenue",
        )
        .order_by("-bookings_count", "name")
    )

    summary = Booking.objects.aggregate(
        total_bookings=Count("id"),
        active_bookings=Count(
            "id",
            filter=Q(status=Booking.Status.ACTIVE),
        ),
        cancelled_bookings=Count(
            "id",
            filter=Q(status=Booking.Status.CANCELLED),
        ),
        completed_bookings=Count(
            "id",
            filter=Q(status=Booking.Status.COMPLETED),
        ),
        total_revenue=Sum(
            "cost",
            filter=Q(status=Booking.Status.ACTIVE),
        ),
        avg_cost=Avg(
            "cost",
            filter=Q(status=Booking.Status.ACTIVE),
        ),
        min_cost=Min(
            "cost",
            filter=Q(status=Booking.Status.ACTIVE),
        ),
        max_cost=Max(
            "cost",
            filter=Q(status=Booking.Status.ACTIVE),
        ),
    )

    return render(
        request,
        "bookings/statistics.html",
        {
            "statistics": statistics_data,
            "summary": summary,
        },
    )
