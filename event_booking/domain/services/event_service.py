from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from ..entities.event import Event
from ..entities.session import Session
from ..repositories.event_repository import EventRepository

class EventError(Exception):
    """Base class for event-related errors."""
    pass

class EventNotFoundError(EventError):
    """Raised when an event is not found."""
    pass

class SessionError(EventError):
    """Raised when there's an error with a session."""
    pass

class EventService:
    def __init__(self, event_repository: EventRepository):
        self.event_repository = event_repository

    def create_event(self, name: str, description: str, venue: str, categories: List[str]) -> Event:
        """Create a new event."""
        event = Event(
            name=name,
            description=description,
            venue=venue,
            categories=categories
        )
        event.validate()
        return self.event_repository.save(event)

    def add_session(self, event_id: UUID, start_time: datetime, end_time: datetime,
                   capacity: int, base_price: Decimal) -> Session:
        """Add a session to an event."""
        event = self.event_repository.find_by_id(event_id)
        if not event:
            raise EventNotFoundError(f"Event {event_id} not found")

        session = Session(
            event_id=event_id,
            start_time=start_time,
            end_time=end_time,
            capacity=capacity,
            base_price=base_price
        )
        session.validate()

        # Check for overlapping sessions
        for existing_session in event.sessions:
            if (existing_session.start_time < end_time and 
                existing_session.end_time > start_time):
                raise SessionError("Session overlaps with existing session")

        event.add_session(session)
        return self.event_repository.update(event).get_session(session.id)

    def remove_session(self, event_id: UUID, session_id: UUID) -> None:
        """Remove a session from an event."""
        event = self.event_repository.find_by_id(event_id)
        if not event:
            raise EventNotFoundError(f"Event {event_id} not found")

        session = event.get_session(session_id)
        if not session:
            raise SessionError(f"Session {session_id} not found")

        if session.booked_seats > 0:
            raise SessionError("Cannot remove session with existing bookings")

        event.remove_session(session_id)
        self.event_repository.update(event)

    def get_available_sessions(self, event_id: UUID) -> List[Session]:
        """Get all available sessions for an event."""
        event = self.event_repository.find_by_id(event_id)
        if not event:
            raise EventNotFoundError(f"Event {event_id} not found")

        return event.get_available_sessions()

    def get_events_by_category(self, category: str) -> List[Event]:
        """Get all events in a specific category."""
        return self.event_repository.find_by_category(category)

    def update_event(self, event_id: UUID, name: str = None, description: str = None,
                    venue: str = None, categories: List[str] = None) -> Event:
        """Update an event's details."""
        event = self.event_repository.find_by_id(event_id)
        if not event:
            raise EventNotFoundError(f"Event {event_id} not found")

        if name is not None:
            event.name = name
        if description is not None:
            event.description = description
        if venue is not None:
            event.venue = venue
        if categories is not None:
            event.categories = categories

        event.validate()
        return self.event_repository.update(event)

    def delete_event(self, event_id: UUID) -> bool:
        """Delete an event and all its sessions."""
        event = self.event_repository.find_by_id(event_id)
        if not event:
            raise EventNotFoundError(f"Event {event_id} not found")

        # Check if any sessions have bookings
        for session in event.sessions:
            if session.booked_seats > 0:
                raise EventError("Cannot delete event with existing bookings")

        return self.event_repository.delete(event_id) 