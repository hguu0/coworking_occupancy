from django.contrib.auth.models import User
from core.models import Amenity, Space, Booking, OccupancyLog
from django.utils import timezone
import datetime
import random

def seed():
    if User.objects.filter(username='admin').exists():
        print("Data already seeded or admin exists.")
        return

    # Create users
    admin = User.objects.create_superuser('admin', 'admin@example.com', 'password')
    user1 = User.objects.create_user('user1', 'user1@example.com', 'password')
    user2 = User.objects.create_user('user2', 'user2@example.com', 'password')

    # Create amenities
    wifi = Amenity.objects.create(name='High-Speed WiFi')
    coffee = Amenity.objects.create(name='Free Coffee')
    projector = Amenity.objects.create(name='Projector')
    whiteboard = Amenity.objects.create(name='Whiteboard')

    # Create spaces
    space1 = Space.objects.create(name='Main Open Space', capacity=20, description='Open area desk', price_per_hour=5.00)
    space1.amenities.add(wifi, coffee)
    
    space2 = Space.objects.create(name='Meeting Room Alpha', capacity=6, description='Small meeting room', price_per_hour=25.00)
    space2.amenities.add(wifi, projector, whiteboard)
    
    space3 = Space.objects.create(name='Quiet Zone', capacity=10, description='Silent work area', price_per_hour=8.00)
    space3.amenities.add(wifi)

    # Create bookings
    now = timezone.now()
    Booking.objects.create(user=user1, space=space1, start_time=now + datetime.timedelta(hours=1), end_time=now + datetime.timedelta(hours=3))
    Booking.objects.create(user=user2, space=space2, start_time=now + datetime.timedelta(days=1, hours=10), end_time=now + datetime.timedelta(days=1, hours=12))
    Booking.objects.create(user=user1, space=space3, start_time=now - datetime.timedelta(hours=5), end_time=now - datetime.timedelta(hours=3), status='completed')

    # Create logs
    for i in range(10):
        OccupancyLog.objects.create(
            space=space1,
            occupied_count=random.randint(0, 20),
            temperature=random.uniform(20.0, 25.0),
            is_holiday=random.choice([True, False])
        )

    print("Seeding complete.")

seed()
