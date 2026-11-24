from django.shortcuts import render
from django.views.generic import TemplateView

from bookings.models import Booking
from rooms.models import Room


class HomePageView(TemplateView):
    template_name = "homepage/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["featured_rooms"] = (
            Room.objects
            .filter(operational=True, under_maintenance=False)
            .order_by("name")[:3]
        )
        context["recent_bookings"] = (
            Booking.objects
            .active()
            .select_related("room", "user")
            .order_by("booking_date", "pk")[:3]
        )
        return context


def page_not_found(request, exception):
    return render(
        request,
        "404.html",
        status=404,
    )
