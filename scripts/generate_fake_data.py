import random
from datetime import datetime, timedelta
import os

def get_db_for_time_and_location(hour, loc_id):
    """
    Generate a dB level based on the hour of the day and the location.
    This creates a recognizable pattern for AI analysis.
    """
    base_db = 40.0

    if loc_id in ['mckeldin', 'esj']:
        if 10 <= hour <= 16:
            base_db = 75.0
        elif 17 <= hour <= 22:
            base_db = 60.0
        else:
            base_db = 45.0

    elif loc_id in ['stem', 'iribe']:
        if 14 <= hour <= 20:
            base_db = 70.0
        elif 9 <= hour <= 13:
            base_db = 55.0
        else:
            base_db = 42.0

    elif loc_id == 'stamp':
        if 12 <= hour <= 14 or 17 <= hour <= 19:
            base_db = 85.0
        elif 10 <= hour <= 21:
            base_db = 65.0
        else:
            base_db = 50.0

    else:
        if 9 <= hour <= 18:
            base_db = 60.0
        else:
            base_db = 45.0

    noise = random.uniform(-5.0, 5.0)
    return max(30.0, min(100.0, base_db + noise))

def get_fake_data(locations):
    now = datetime.utcnow()
    start_time = now - timedelta(hours=24)

    docs = []
    current_time = start_time
    while current_time <= now:
        hour = current_time.hour

        for loc in locations:
            db_level = get_db_for_time_and_location(hour, loc["id"])
            
            # Estimate people based on noise level. 
            # 35dB = ~0 people. Every 1.5 dB above 35 adds ~1 person.
            base_people = max(0, (db_level - 35) * 1.5)
            people_count = int(max(0, base_people + random.uniform(-5, 10)))

            doc = {
                "room_id": loc["id"],
                "location": {
                    "type": "Point",
                    "coordinates": [loc["lng"], loc["lat"]]
                },
                "db": round(db_level, 2),
                "people": people_count,
                "date": current_time
            }
            docs.append(doc)

        current_time += timedelta(minutes=15)
        
    return docs

def generate_fake_data():
    from pymongo import MongoClient
    MONGO_URI = os.getenv("MONGODB_URI", "mongodb+srv://SarayuJ:[EMAIL_ADDRESS]/testing")
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

    print("Clearing existing study room data...")
    collection.delete_many({})

    print("Generating 24 hours of fake data with patterns...")
    docs_to_insert = get_fake_data(UMD_LOCATIONS)

    print(f"Inserting {len(docs_to_insert)} records into MongoDB...")
    collection.insert_many(docs_to_insert)
    print("Done!")

if __name__ == "__main__":
    generate_fake_data()
