from django.contrib import admin
from .models import Amenity, Space, Booking, OccupancyLog

@admin.register(Amenity)
class AmenityAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Space)
class SpaceAdmin(admin.ModelAdmin):
    list_display = ('name', 'capacity', 'price_per_hour')
    search_fields = ('name', 'description')
    list_filter = ('capacity',)

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'space', 'start_time', 'end_time', 'status')
    search_fields = ('user__username', 'space__name')
    list_filter = ('status', 'start_time')

@admin.register(OccupancyLog)
class OccupancyLogAdmin(admin.ModelAdmin):
    list_display = ('space', 'timestamp', 'occupied_count', 'temperature')
    list_filter = ('space', 'is_holiday')
