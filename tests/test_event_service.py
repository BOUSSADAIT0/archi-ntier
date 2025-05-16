import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from uuid import uuid4

from event_booking.domain.entities.event import Event
from event_booking.domain.entities.session import Session
from event_booking.domain.services.event_service import EventService, EventError, SessionError

class MockEventRepository:
    def __init__(self):
        self.events = {}

    def save(self, event):
        self.events[event.id] = event
        return event

    def find_by_id(self, event_id):
        return self.events.get(event_id)

    def find_all(self):
        return list(self.events.values())

    def find_by_category(self, category):
        return [event for event in self.events.values() if category in event.categories]

    def update(self, event):
        self.events[event.id] = event
        return event

    def delete(self, event_id):
        if event_id in self.events:
            del self.events[event_id]
            return True
        return False

@pytest.fixture
def event_service():
    return EventService(MockEventRepository())

def test_create_event(event_service):
    event = event_service.create_event(
        name="Test Event",
        description="Test Description",
        venue="Test Venue",
        categories=["test"]
    )
    assert event.name == "Test Event"
    assert event.description == "Test Description"
    assert event.venue == "Test Venue"
    assert event.categories == ["test"]

def test_create_event_invalid_data(event_service):
    with pytest.raises(ValueError):
        event_service.create_event(
            name="",
            description="Test Description",
            venue="Test Venue",
            categories=["test"]
        )

def test_add_session(event_service):
    event = event_service.create_event(
        name="Test Event",
        description="Test Description",
        venue="Test Venue",
        categories=["test"]
    )

    start_time = datetime.now() + timedelta(days=1)
    end_time = start_time + timedelta(hours=2)
    session = event_service.add_session(
        event_id=event.id,
        start_time=start_time,
        end_time=end_time,
        capacity=100,
        base_price=Decimal("50.00")
    )

    assert session.event_id == event.id
    assert session.start_time == start_time
    assert session.end_time == end_time
    assert session.capacity == 100
    assert session.base_price == Decimal("50.00")

def test_add_session_invalid_times(event_service):
    event = event_service.create_event(
        name="Test Event",
        description="Test Description",
        venue="Test Venue",
        categories=["test"]
    )

    start_time = datetime.now() + timedelta(days=1)
    end_time = start_time - timedelta(hours=2)  # End time before start time

    with pytest.raises(ValueError):
        event_service.add_session(
            event_id=event.id,
            start_time=start_time,
            end_time=end_time,
            capacity=100,
            base_price=Decimal("50.00")
        )

def test_add_session_overlapping(event_service):
    event = event_service.create_event(
        name="Test Event",
        description="Test Description",
        venue="Test Venue",
        categories=["test"]
    )

    start_time1 = datetime.now() + timedelta(days=1)
    end_time1 = start_time1 + timedelta(hours=2)
    event_service.add_session(
        event_id=event.id,
        start_time=start_time1,
        end_time=end_time1,
        capacity=100,
        base_price=Decimal("50.00")
    )

    # Try to add overlapping session
    start_time2 = start_time1 + timedelta(hours=1)  # Overlaps with first session
    end_time2 = start_time2 + timedelta(hours=2)

    with pytest.raises(SessionError):
        event_service.add_session(
            event_id=event.id,
            start_time=start_time2,
            end_time=end_time2,
            capacity=100,
            base_price=Decimal("50.00")
        )

def test_get_available_sessions(event_service):
    event = event_service.create_event(
        name="Test Event",
        description="Test Description",
        venue="Test Venue",
        categories=["test"]
    )

    start_time = datetime.now() + timedelta(days=1)
    end_time = start_time + timedelta(hours=2)
    session = event_service.add_session(
        event_id=event.id,
        start_time=start_time,
        end_time=end_time,
        capacity=100,
        base_price=Decimal("50.00")
    )

    available_sessions = event_service.get_available_sessions(event.id)
    assert len(available_sessions) == 1
    assert available_sessions[0].id == session.id

def test_get_events_by_category(event_service):
    event1 = event_service.create_event(
        name="Test Event 1",
        description="Test Description",
        venue="Test Venue",
        categories=["test", "music"]
    )

    event2 = event_service.create_event(
        name="Test Event 2",
        description="Test Description",
        venue="Test Venue",
        categories=["test", "theater"]
    )

    music_events = event_service.get_events_by_category("music")
    assert len(music_events) == 1
    assert music_events[0].id == event1.id

    test_events = event_service.get_events_by_category("test")
    assert len(test_events) == 2 