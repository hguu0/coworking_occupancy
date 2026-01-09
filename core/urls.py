from django.urls import path
from . import views

urlpatterns = [
    path('', views.SpaceListView.as_view(), name='space_list'),
    path('space/<int:pk>/', views.SpaceDetailView.as_view(), name='space_detail'),
    path('space/<int:space_id>/book/', views.BookingCreateView.as_view(), name='book_space'),
    path('bookings/', views.BookingListView.as_view(), name='booking_list'),
]
