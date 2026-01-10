import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "coworking_occupancy.settings")
django.setup()

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
    # Generate realistic data for the last 30 days
    print("Generating comprehensive historical data...")
    start_date = now - datetime.timedelta(days=30)
    spaces = [space1, space2, space3]
    
    # Generate density: ~1 record per hour per space
    for day in range(31): 
        current_date_base = start_date + datetime.timedelta(days=day)
        
        for hour in range(8, 22): # Hours 8 to 21
            for space in spaces:
                # Add some randomness to time
                log_time = current_date_base.replace(hour=hour, minute=random.randint(0, 59))
                
                # Base pattern: Peak at 10-11am and 2-3pm
                is_weekend = log_time.weekday() >= 5
                
                if is_weekend:
                    occupancy_factor = 0.2
                else:
                    # Simple double peak curve
                    if 9 <= hour <= 12:
                        occupancy_factor = 0.8 + random.uniform(-0.1, 0.1)
                    elif 13 <= hour <= 14: # Lunch dip
                        occupancy_factor = 0.5 + random.uniform(-0.1, 0.1)
                    elif 15 <= hour <= 17:
                        occupancy_factor = 0.7 + random.uniform(-0.1, 0.1)
                    else:
                        occupancy_factor = 0.3 + random.uniform(-0.1, 0.1)
                
                # Base conditions
                temperature = 22.0 + random.uniform(-5, 5) # 17 to 27
                rain_mm = 0.0
                pressure = 760 + random.uniform(-10, 10)
                traffic = random.randint(0, 10)
                
                # Weather simulation: Low pressure often means rain
                if pressure < 755 and random.random() < 0.7:
                     rain_mm = random.uniform(0.1, 15.0)
                     temperature -= 2 # Rain cools it down

                # Traffic peaks at rush hours
                if (8 <= hour <= 9) or (17 <= hour <= 19):
                    traffic = min(10, traffic + random.randint(2, 5))

                # --- INDIRECT EFFECTS ON OCCUPANCY ---
                
                # 1. Rain Effect: Heavy rain (>5mm) reduces walk-ins
                if rain_mm > 5.0:
                    occupancy_factor *= 0.85 # -15%
                elif rain_mm > 0:
                    occupancy_factor *= 0.95 # -5%
                    
                # 2. Traffic Effect: Heavy traffic (8+) might delay people (reduce morning) or keep them longer (avoid evening rush)
                if traffic >= 8:
                    if 8 <= hour <= 10:
                        occupancy_factor *= 0.9 # Late arrivals
                    elif 17 <= hour <= 19:
                         occupancy_factor *= 1.1 # Stay later to avoid traffic

                # 3. Temperature Effect: Too hot (>26) or too cold (<18) 
                if temperature > 26 or temperature < 18:
                    occupancy_factor *= 0.95
                
                # Apply factor to capacity
                occupancy = int(space.capacity * occupancy_factor)
                
                # Add noise
                occupancy += random.randint(-2, 2)
                occupancy = max(0, min(occupancy, space.capacity))
                
                # Specific "Exces" (Outliers) - occasional huge spike or drop
                if random.random() < 0.05: # 5% chance of outlier
                    occupancy = random.randint(0, space.capacity)

                OccupancyLog.objects.create(
                    space=space,
                    timestamp=log_time,
                    occupied_count=occupancy,
                    temperature=temperature,
                    pressure=pressure,
                    precipitation=rain_mm,
                    traffic_index=traffic,
                    is_holiday=is_weekend
                )

    print("Seeding complete.")

seed()
