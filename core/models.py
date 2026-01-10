from django.db import models
from django.contrib.auth.models import User

class Amenity(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Amenities"

class Space(models.Model):
    name = models.CharField(max_length=100)
    capacity = models.IntegerField()
    description = models.TextField()
    price_per_hour = models.DecimalField(max_digits=6, decimal_places=2)
    amenities = models.ManyToManyField(Amenity, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Booking(models.Model):
    STATUS_CHOICES = [
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    space = models.ForeignKey(Space, on_delete=models.CASCADE, related_name='bookings')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='confirmed')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.space.name} ({self.start_time})"

class OccupancyLog(models.Model):
    space = models.ForeignKey(Space, on_delete=models.CASCADE, related_name='occupancy_logs')
    timestamp = models.DateTimeField(auto_now_add=True)
    occupied_count = models.IntegerField()
    # Weather factors
    temperature = models.FloatField(null=True, blank=True) # Celsius
    pressure = models.FloatField(null=True, blank=True) # mmHg
    precipitation = models.FloatField(null=True, blank=True, default=0.0) # mm
    # External factors
    traffic_index = models.IntegerField(default=0, help_text="0-10 scale")
    is_holiday = models.BooleanField(default=False)

    def __str__(self):
        temp_str = f"{self.temperature:.1f}°C" if self.temperature is not None else "N/A"
        return f"{self.space.name} @ {self.timestamp.strftime('%Y-%m-%d %H:%M')} | Occ: {self.occupied_count} | Temp: {temp_str}"
