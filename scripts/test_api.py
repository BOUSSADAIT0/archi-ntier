import requests
import uuid
from datetime import datetime, timedelta
import json

# Configuration
API_BASE_URL = "http://localhost:18000"

def test_api():
    print("=== Testing Event Booking API ===")

    # 1. Create an event
    print("\n1. Creating event...")
    event_data = {
        "name": "Concert de Test",
        "description": "Un super concert test",
        "venue": "Salle de Test",
        "categories": ["musique", "concert"]
    }
    response = requests.post(f"{API_BASE_URL}/events/", json=event_data)
    if response.status_code == 200:
        event = response.json()
        print(f"Event created with ID: {event['id']}")
    else:
        print(f"Failed to create event: {response.text}")
        return

    # 2. Add a session to the event
    print("\n2. Adding session...")
    start_time = datetime.now() + timedelta(days=30)
    session_data = {
        "start_time": start_time.isoformat(),
        "end_time": (start_time + timedelta(hours=3)).isoformat(),
        "capacity": 100,
        "base_price": 50.00
    }
    response = requests.post(
        f"{API_BASE_URL}/events/{event['id']}/sessions",
        json=session_data
    )
    if response.status_code == 200:
        session = response.json()
        print(f"Session created with ID: {session['id']}")
    else:
        print(f"Failed to create session: {response.text}")
        return

    # 3. Create a booking
    print("\n3. Creating booking...")
    user_id = str(uuid.uuid4())
    booking_data = {
        "user_id": user_id,
        "session_id": session['id'],
        "seats": 2
    }
    response = requests.post(f"{API_BASE_URL}/bookings/", json=booking_data)
    if response.status_code == 200:
        booking = response.json()
        print(f"Booking created with ID: {booking['id']}")
        
        # 4. Confirm the booking
        print("\n4. Confirming booking...")
        response = requests.post(
            f"{API_BASE_URL}/bookings/{booking['id']}/confirm"
        )
        if response.status_code == 200:
            print("Booking confirmed successfully")
        else:
            print(f"Failed to confirm booking: {response.text}")
    else:
        print(f"Failed to create booking: {response.text}")

    # 5. List all events
    print("\n5. Listing all events...")
    response = requests.get(f"{API_BASE_URL}/events/")
    if response.status_code == 200:
        events = response.json()
        print(f"Found {len(events)} events:")
        for evt in events:
            print(f"- {evt['name']} at {evt['venue']}")
    else:
        print(f"Failed to list events: {response.text}")

if __name__ == "__main__":
    test_api() 