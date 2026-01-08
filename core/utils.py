import matplotlib.pyplot as plt
import base64
from io import BytesIO
import pandas as pd
from .models import OccupancyLog
import matplotlib

# Set non-interactive backend
matplotlib.use('Agg')

def generate_occupancy_graph(space_id):
    logs = OccupancyLog.objects.filter(space_id=space_id).order_by('timestamp')
    if not logs.exists():
        return None

    df = pd.DataFrame(list(logs.values('timestamp', 'occupied_count')))
    
    if df.empty:
        return None

    # Plotting
    plt.figure(figsize=(10, 5))
    plt.plot(df['timestamp'], df['occupied_count'], marker='o', linestyle='-', color='b')
    plt.title('Occupancy History')
    plt.xlabel('Date/Time')
    plt.ylabel('Occupied Seats')
    plt.grid(True)
    plt.xticks(rotation=45)
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
