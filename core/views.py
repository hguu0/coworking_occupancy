from django.shortcuts import get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.urls import reverse_lazy

from .models import Space, Booking
from .utils import generate_occupancy_graph, generate_prediction_graph, generate_correlation_graph
from .forms import BookingForm


class SpaceListView(ListView):
    model = Space
    template_name = 'core/space_list.html'
    context_object_name = 'spaces'

    def get_queryset(self):
        return Space.objects.annotate(booking_count=Count('bookings'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Attach current occupancy to each space in the context list
        for space in context['spaces']:
            last_log = space.occupancy_logs.order_by('-timestamp').first()
            space.current_occupancy = last_log.occupied_count if last_log else 0
            
            if space.capacity > 0:
                space.occupancy_percentage = int((space.current_occupancy / space.capacity) * 100)
            else:
                space.occupancy_percentage = 0
                
            # Quick color coding for UI
            if space.occupancy_percentage > 80:
                space.occupancy_color = 'red'
            elif space.occupancy_percentage > 50:
                space.occupancy_color = 'yellow'
            else:
                space.occupancy_color = 'green'
                
        return context


from core.utils import generate_occupancy_graph, generate_prediction_graph, generate_correlation_graph

# ... (imports)

class SpaceDetailView(DetailView):
    model = Space
    template_name = 'core/space_detail.html'
    context_object_name = 'space'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get visualization params from GET request
        try:
            window_size = int(self.request.GET.get('window_size', 1))
        except ValueError:
            window_size = 1
            
        remove_outliers = self.request.GET.get('remove_outliers') == 'on'

        # Optional: Add recent occupancy logs
        context['recent_logs'] = self.object.occupancy_logs.order_by(
            '-timestamp')[:5]
        
        # Generate graph with params
        context['graph_image'] = generate_occupancy_graph(
            self.object.id, 
            window_size=window_size, 
            remove_outliers=remove_outliers
        )
        
        # Pass params back to template to maintain state
        context['window_size'] = window_size
        context['remove_outliers'] = remove_outliers
        
        # Generate prediction graph
        context['prediction_image'] = generate_prediction_graph(self.object.id)
        
        # NEW: Correlation Graph
        context['correlation_image'] = generate_correlation_graph(self.object.id)
        
        return context


class BookingListView(LoginRequiredMixin, ListView):
    model = Booking
    template_name = 'core/booking_list.html'
    context_object_name = 'bookings'

    def get_queryset(self):
        return Booking.objects.filter(
            user=self.request.user
        ).order_by('-start_time')


class BookingUpdateView(LoginRequiredMixin, UpdateView):
    model = Booking
    form_class = BookingForm
    template_name = 'core/booking_form.html'
    success_url = reverse_lazy('booking_list')

    def get_queryset(self):
        # Ensure user can only edit their own bookings
        return Booking.objects.filter(user=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Pass the space object for context, derived from the booking instance
        booking = self.get_object()
        context['space'] = booking.space
        context['is_update'] = True
        return context


class BookingCreateView(LoginRequiredMixin, CreateView):
    model = Booking
    form_class = BookingForm
    template_name = 'core/booking_form.html'
    success_url = reverse_lazy('booking_list')

    def form_valid(self, form):
        space = get_object_or_404(Space, pk=self.kwargs['space_id'])
        form.instance.space = space
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['space'] = get_object_or_404(
            Space, pk=self.kwargs['space_id'])
        return context

