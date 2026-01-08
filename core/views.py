from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Avg
from .models import Space, Booking, OccupancyLog

class SpaceListView(ListView):
    model = Space
    template_name = 'core/space_list.html'
    context_object_name = 'spaces'

    def get_queryset(self):
        return Space.objects.annotate(booking_count=Count('bookings'))

class SpaceDetailView(DetailView):
    model = Space
    template_name = 'core/space_detail.html'
    context_object_name = 'space'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Optional: Add recent occupancy logs
        context['recent_logs'] = self.object.occupancy_logs.order_by('-timestamp')[:5]
        return context

class BookingListView(LoginRequiredMixin, ListView):
    model = Booking
    template_name = 'core/booking_list.html'
    context_object_name = 'bookings'
    
    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user).order_by('-start_time')

