import sqlite3
import json
import random
from datetime import datetime, timezone, timedelta

def inject_delhi_gps_events():
    db_path = "data/events.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Clear existing events and incidents so there are no residual Mumbai points
    for table in ['events', 'incidents', 'incident_events', 'incident_notes', 'incident_history']:
        cursor.execute(f"DELETE FROM {table}")
    conn.commit()

    # Highly accurate waypoints along the Delhi DTC Transit Corridor:
    # From Ring Road (AIIMS -> South Ext -> Lajpat Nagar -> Ashram)
    # North through Mathura Road (Nizamuddin -> Pragati Maidan)
    # And into Central Delhi (India Gate -> KG Marg -> Connaught Place)
    delhi_waypoints = [
        (28.5672, 77.2100, "AIIMS Flyover / Ring Road"),
        (28.5710, 77.2225, "South Extension II"),
        (28.5695, 77.2340, "Moolchand Underpass"),
        (28.5685, 77.2435, "Lajpat Nagar Ring Road"),
        (28.5710, 77.2588, "Ashram Chowk Intersection"),
        (28.5880, 77.2485, "Mathura Road / Nizamuddin"),
        (28.6040, 77.2440, "Sunder Nagar Main Road"),
        (28.6150, 77.2420, "Pragati Maidan / Bhairon Marg"),
        (28.6135, 77.2380, "Purana Qila Road"),
        (28.6129, 77.2295, "India Gate C-Hexagon"),
        (28.6235, 77.2240, "Kasturba Gandhi Marg"),
        (28.6275, 77.2205, "Tolstoy Marg Junction"),
        (28.6315, 77.2195, "Connaught Place Outer Circle"),
        (28.6328, 77.2197, "Rajiv Chowk / CP Inner Circle")
    ]

    event_types_pool = [
        ("pothole", "Pothole Defect", 0.35),
        ("alligator_crack", "Alligator Cracking", 0.20),
        ("longitudinal_crack", "Longitudinal Crack", 0.15),
        ("transverse_crack", "Transverse Crack", 0.10),
        ("plate_detected", "ANPR Vehicle Plate", 0.15),
        ("manhole", "Uneven Manhole Cover", 0.05)
    ]

    events_to_insert = []
    now = datetime.now(timezone.utc)

    num_events = 60
    print(f"Generating {num_events} geolocated road events along Delhi Transit Corridor...")

    for i in range(num_events):
        t = i / float(num_events - 1)
        seg_idx = int(t * (len(delhi_waypoints) - 1))
        next_idx = min(seg_idx + 1, len(delhi_waypoints) - 1)
        sub_t = (t * (len(delhi_waypoints) - 1)) - seg_idx

        p1 = delhi_waypoints[seg_idx]
        p2 = delhi_waypoints[next_idx]

        # Minor lane variance (within ~20 meters of road centerline)
        lat = p1[0] + sub_t * (p2[0] - p1[0]) + random.uniform(-0.0003, 0.0003)
        lng = p1[1] + sub_t * (p2[1] - p1[1]) + random.uniform(-0.0003, 0.0003)

        # Weighted selection of defect type
        r = random.random()
        cumulative = 0.0
        ev_type = "pothole"
        desc = "Pothole Defect"
        for et, d, weight in event_types_pool:
            cumulative += weight
            if r <= cumulative:
                ev_type = et
                desc = d
                break

        conf = round(random.uniform(0.78, 0.96), 4)
        evt_time = (now - timedelta(minutes=(num_events - i) * 4)).isoformat()
        ev_id = f"evt_delhi_{1000 + i}"
        bus_id = "DTC-BUS-104" if i % 2 == 0 else "DTC-BUS-218"

        payload = {
            "event_id": ev_id,
            "source": bus_id,
            "event_type": ev_type,
            "defect_class": ev_type,
            "description": desc,
            "confidence": conf,
            "latitude": round(lat, 6),
            "longitude": round(lng, 6),
            "location_name": f"{p1[2]} (Delhi Corridor)",
            "city": "New Delhi",
            "severity": "HIGH" if ev_type in ["pothole", "alligator_crack"] else "MEDIUM",
            "bounding_box": [
                random.randint(120, 280),
                random.randint(140, 380),
                random.randint(340, 480),
                random.randint(440, 580)
            ],
            "gps_hardware": "NMEA-GPS (DTC Mobile Sensing Unit)"
        }

        created_at = evt_time
        payload_json = json.dumps(payload, sort_keys=True)

        events_to_insert.append((
            ev_id,
            ev_type,
            bus_id,
            evt_time,
            round(lat, 6),
            round(lng, 6),
            conf,
            payload_json,
            created_at
        ))

    # Insert events into SQLite
    cursor.executemany("""
        INSERT INTO events (event_id, event_type, source, timestamp, latitude, longitude, confidence, payload_json, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, events_to_insert)

    # Insert 2 Delhi demo incidents
    cursor.execute("""
        INSERT INTO incidents (incident_id, event_id, status, severity, title, description, operator, created_at, updated_at)
        VALUES 
        ('inc_delhi_01', 'evt_delhi_1012', 'OPEN', 'HIGH', 'Deep Pothole — Mathura Road near Nizamuddin', 'Critical asphalt crater reported by DTC fleet on express corridor.', 'DTC_HQ_Officer', datetime('now'), datetime('now')),
        ('inc_delhi_02', 'evt_delhi_1038', 'IN_PROGRESS', 'MEDIUM', 'Alligator Cracks — India Gate C-Hexagon', 'Surface fatigue cracking on bus lane, repair team assigned.', 'PWD_Delhi_Unit4', datetime('now'), datetime('now'))
    """)

    conn.commit()
    conn.close()
    print(f"Successfully generated {len(events_to_insert)} Delhi road events and 2 active incidents!")

if __name__ == "__main__":
    inject_delhi_gps_events()
