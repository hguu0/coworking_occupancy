import matplotlib.pyplot as plt
import base64
from io import BytesIO
import pandas as pd
from .models import OccupancyLog
import matplotlib
import datetime
from django.utils import timezone
import matplotlib.dates as mdates

# Set non-interactive backend
matplotlib.use('Agg')

def generate_occupancy_graph(space_id, window_size=1, remove_outliers=False):
    logs = OccupancyLog.objects.filter(space_id=space_id).order_by('timestamp')
    if not logs.exists():
        return None

    df = pd.DataFrame(list(logs.values('timestamp', 'occupied_count')))
    
    if df.empty:
        return None

    # Sort checks
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values('timestamp')

    # 1. Remove Outliers (Z-score method) if requested
    if remove_outliers and len(df) > 10:
        mean = df['occupied_count'].mean()
        std = df['occupied_count'].std()
        if std > 0:
            # Keep rows with Z-score < 2
            df = df[((df['occupied_count'] - mean) / std).abs() < 2]

    # 2. Smoothing (Rolling Average)
    if window_size > 1:
        # Use min_periods=1 to avoid NaNs at start
        df['occupied_count'] = df['occupied_count'].rolling(window=window_size, min_periods=1, center=True).mean()

    # Plotting
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(df['timestamp'], df['occupied_count'], marker='o' if len(df) < 50 else None, linestyle='-', color='b', linewidth=1.5)
    
    # Format Time Axis
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))
    fig.autofmt_xdate()

    plt.title('Occupancy History')
    plt.xlabel('Date/Time')
    plt.ylabel('Occupied Seats')
    plt.grid(True)
    plt.tight_layout()

    # Save to buffer
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    
    graphic = base64.b64encode(image_png)
    graphic = graphic.decode('utf-8')
    plt.close() 
    
    return graphic

def generate_correlation_graph(space_id):
    """
    Generates a 1x3 subplot showing correlation between Occupancy and:
    1. Temperature
    2. Precipitation
    3. Traffic Index
    """
    logs = OccupancyLog.objects.filter(space_id=space_id).values(
        'occupied_count', 'temperature', 'precipitation', 'traffic_index'
    )
    
    if not logs.exists():
        return None

    df = pd.DataFrame(list(logs))
    
    if len(df) < 5:
        return None
        
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    
    # 1. Occupancy vs Temperature
    axes[0].scatter(df['temperature'], df['occupied_count'], alpha=0.5, c='orange')
    axes[0].set_title(f"vs Temperature (r={df['temperature'].corr(df['occupied_count']):.2f})")
    axes[0].set_xlabel("Temp (°C)")
    axes[0].set_ylabel("Occupancy")
    
    # 2. Occupancy vs Precipitation
    axes[1].scatter(df['precipitation'], df['occupied_count'], alpha=0.5, c='blue')
    axes[1].set_title(f"vs Rain (r={df['precipitation'].corr(df['occupied_count']):.2f})")
    axes[1].set_xlabel("Rain (mm)")
    
    # 3. Occupancy vs Traffic
    # Jitter the traffic integer data for better visibility
    # We need numpy or just use basic loop since we can't import numpy in tool easily if not installed?
    # Actually random is imported in seed_script, not here.
    # But this is inside utils.py, lets check imports.
    # imports: plt, base64, BytesIO, pd, OccupancyLog, matplotlib, datetime, timezone, mdates.
    # We can use pd apply or just simple list comprehension if random is imported
    # Let's import random inside function to be safe or add to top.
    import random
    
    jitter = [random.uniform(-0.2, 0.2) for _ in range(len(df))]
    axes[2].scatter(df['traffic_index'] + jitter, df['occupied_count'], alpha=0.5, c='red')
    axes[2].set_title(f"vs Traffic (r={df['traffic_index'].corr(df['occupied_count']):.2f})")
    axes[2].set_xlabel("Traffic Index (0-10)")

    plt.tight_layout()
    
    # Save to buffer
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    
    graphic = base64.b64encode(image_png)
    graphic = graphic.decode('utf-8')
    plt.close()
    
    return graphic

def generate_prediction_graph(space_id):
    logs = OccupancyLog.objects.filter(space_id=space_id)
    if not logs.exists():
        return None

    df = pd.DataFrame(list(logs.values('timestamp', 'occupied_count')))
    
    if df.empty:
        return None
        
    # Process data to get DayOfWeek(0-6) and Hour(0-23)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['day_of_week'] = df['timestamp'].dt.dayofweek
    df['hour'] = df['timestamp'].dt.hour
    
    # Calculate average occupancy for every (Day, Hour) combination
    # Group by [Day, Hour] -> Mean
    # This creates a model like: "On Mondays at 10am, avg occupancy is 5"
    occupancy_model = df.groupby(['day_of_week', 'hour'])['occupied_count'].mean()
    
    # Generate forecast for the NEXT 7 DAYS (Hourly)
    future_dates = []
    predicted_values = []
    
    now = timezone.now()
    # Align 'now' to start of next hour for cleaner graph
    start_time = now.replace(minute=0, second=0, microsecond=0) + datetime.timedelta(hours=1)
    
    for i in range(24 * 7): # 7 days * 24 hours
        future_time = start_time + datetime.timedelta(hours=i)
        day_of_week = future_time.weekday()
        hour = future_time.hour
        
        val = 0 # Default to 0
        
        # Lookup in model
        try:
            val = occupancy_model.loc[(day_of_week, hour)]
        except KeyError:
             # Fallback: try finding avg for just the hour across all days
             try:
                 val = df[df['hour'] == hour]['occupied_count'].mean()
             except:
                 val = 0
        
        # Ensure val is not NaN (pandas mean() returns NaN for empty slices)
        if pd.isna(val):
            val = 0
            
        future_dates.append(future_time)
        predicted_values.append(val)
        
    # Plotting
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(future_dates, predicted_values, color='purple', linewidth=2, label='Predicted Occupancy')
    
    # Format Time Axis
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))
    fig.autofmt_xdate()
    
    # Formatting
    plt.title('Occupancy Forecast (Next 7 Days)')
    plt.xlabel('Date/Time')
    plt.ylabel('Predicted Occupied Seats')
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend()
    plt.tight_layout()

    # Save to buffer
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    
    graphic = base64.b64encode(image_png)
    graphic = graphic.decode('utf-8')
    plt.close() 
    
    return graphic
