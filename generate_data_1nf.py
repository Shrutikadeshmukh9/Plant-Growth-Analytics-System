# Generate dummy data this can be tailored as needed to create more data and also add zones,
import json
import random
from datetime import datetime, timedelta
import math

def generate_sample_data():
    """Generate 7 days of sensor data for a plant monitoring system."""
    zones = ["zone_1", "zone_2", "zone_3"]
    plants = {
        "zone_1": ["tomato_1", "tomato_2", "pepper_1"],
        "zone_2": ["lettuce_1", "lettuce_2", "lettuce_3"],
        "zone_3": ["basil_1", "basil_2", "cilantro_1"]
    }
    
    start_date = datetime(2024, 1, 1)
    data = []
    
    for zone in zones:
        base_temp = {"zone_1": 25, "zone_2": 22, "zone_3": 24}[zone]
        base_humidity = {"zone_1": 65, "zone_2": 70, "zone_3": 60}[zone]
        base_moisture = {"zone_1": 0.7, "zone_2": 0.8, "zone_3": 0.65}[zone]
        base_light = {"zone_1": 800, "zone_2": 600, "zone_3": 700}[zone]
        
        current_date = start_date
        for day in range(7):
            for hour in range(24):
                time_factor = math.sin(hour * math.pi / 12)  # Daily cycle
                temp = base_temp + time_factor * 3 + random.uniform(-0.5, 0.5)
                humidity = base_humidity + time_factor * -5 + random.uniform(-2, 2)
                moisture = base_moisture + random.uniform(-0.05, 0.05)
                light = base_light + (time_factor * 400 if 6 <= hour <= 18 else 0) + random.uniform(-50, 50)
                
                timestamp = current_date + timedelta(hours=hour)
                
                # Generate readings for each plant in the zone
                for plant_id in plants[zone]:
                    height = 10 + (day * 1.5) + random.uniform(-0.2, 0.2)  
                    leaf_count = 5 + math.floor(day * 0.7) + random.randint(-1, 1)  # Adding leaves over time
                    
                    #Feel free to structure the data in a way that is easier to work with 
                    reading = {
                        "timestamp": timestamp.isoformat(),
                        "zone_id": zone,
                        "plant_id": plant_id,                        
                        "temperature": round(temp, 2),
                        "humidity": round(humidity, 2),
                        "soil_moisture": round(moisture, 3),
                        "light_level": round(light, 1),
                        "plant_height": round(height, 1),
                        "leaf_count": max(0, leaf_count)
                    }
                    data.append(reading)
                
                current_date = timestamp
    
    return data

if __name__ == "__main__":
    data = generate_sample_data()
    
    print("Sample sensor readings:")
    print(json.dumps(data[:2], indent=2))
    
    with open('plant_monitoring_data.json', 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"\nGenerated {len(data)} readings")
    print("Data saved to 'plant_monitoring_data.json'")