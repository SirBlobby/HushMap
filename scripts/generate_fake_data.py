import random
from datetime import datetime, timedelta
from pymongo import MongoClient

# MongoDB Setup
MONGO_URI = "mongodb+srv://SarayuJ:SarayuJ123@cluster0.xjy5c.mongodb.net/testing"
client = MongoClient(MONGO_URI)
db = client.study_buddy_db
collection = db.study_rooms

UMD_LOCATIONS = [
	{ "id": 'esj', "name": 'Edward St. John (ESJ)', "lng": -76.94209511596014, "lat": 38.987133359608755 },
	{ "id": 'mckeldin', "name": 'McKeldin Library', "lng": -76.94494907523277, "lat": 38.986021017749366 },
	{ "id": 'hornbake', "name": 'Hornbake Library', "lng": -76.94161787005467, "lat": 38.988233373664826 },
	{ "id": 'stem', "name": 'STEM Library', "lng": -76.93942003731279, "lat": 38.988991437126195 },
	{ "id": 'clarice', "name": 'Clarice Library', "lng": -76.9500912552473, "lat": 38.990547823732285 },
	{ "id": 'yahentamitsi', "name": 'Yahentamitsi', "lng": -76.9448027183373, "lat": 38.99108961575231 },
	{ "id": 'iribe', "name": 'Iribe', "lng": -76.93643838603555, "lat": 38.98933701397555 },
	{ "id": 'reckord', "name": 'Reckord Armory', "lng": -76.93897470250619, "lat": 38.98609556181066 },
	{ "id": 'stamp', "name": 'Stamp Student Union', "lng": -76.94473083972326, "lat": 38.988130238874874 }
]

def get_db_for_time_and_location(hour, loc_id):
    """
    Generate a dB level based on the hour of the day and the location.
    This creates a recognizable pattern for AI analysis.
    """
    base_db = 40.0 # Ambient noise
    
    if loc_id in ['mckeldin', 'esj']:
        # Busy during the day (10am - 4pm)
        if 10 <= hour <= 16:
            base_db = 75.0
        elif 17 <= hour <= 22:
            base_db = 60.0
        else:
            base_db = 45.0
            
    elif loc_id in ['stem', 'iribe']:
        # Busy in the afternoon/evening (2pm - 8pm)
        if 14 <= hour <= 20:
            base_db = 70.0
        elif 9 <= hour <= 13:
            base_db = 55.0
        else:
            base_db = 42.0
            
    elif loc_id == 'stamp':
        # Busy during lunch (12pm - 2pm) and dinner (5pm - 7pm)
        if 12 <= hour <= 14 or 17 <= hour <= 19:
            base_db = 85.0
        elif 10 <= hour <= 21:
            base_db = 65.0
        else:
            base_db = 50.0
            
    else:
        # General locations (Clarice, Yahentamitsi, Reckord, Hornbake)
        # Moderate noise during the day
        if 9 <= hour <= 18:
            base_db = 60.0
        else:
            base_db = 45.0
            
    # Add random noise to make it look realistic (+/- 5 dB)
    noise = random.uniform(-5.0, 5.0)
    return max(30.0, min(100.0, base_db + noise))

def generate_fake_data():
    print("Clearing existing study room data...")
    collection.delete_many({})
    
    now = datetime.utcnow()
    start_time = now - timedelta(hours=24)
    
    docs_to_insert = []
    
    print("Generating 24 hours of fake data with patterns...")
    # Generate data points every 15 minutes for the last 24 hours
    current_time = start_time
    while current_time <= now:
        hour = current_time.hour
        
        for loc in UMD_LOCATIONS:
            db_level = get_db_for_time_and_location(hour, loc["id"])
            
            doc = {
                "room_id": loc["id"],
                "location": {
                    "type": "Point",
                    "coordinates": [loc["lng"], loc["lat"]]
                },
                "db": round(db_level, 2),
                "date": current_time
            }
            docs_to_insert.append(doc)
            
        current_time += timedelta(minutes=15)
        
    print(f"Inserting {len(docs_to_insert)} records into MongoDB...")
    collection.insert_many(docs_to_insert)
    print("Done!")

if __name__ == "__main__":
    generate_fake_data()
