import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from uuid import uuid4

from event_booking.domain.entities.booking import Booking, BookingStatus
from event_booking.domain.entities.event import Event
from event_booking.domain.entities.session import Session
from event_booking.domain.services.booking_service import (
    BookingService, BookingError, InsufficientSeatsError, SessionNotFoundError
)

class MockBookingRepository:
    def __init__(self):
        self.bookings = {}

    def save(self, booking):
        self.bookings[booking.id] = booking
        return booking

    def find_by_id(self, booking_id):
        return self.bookings.get(booking_id)

    def find_by_user_id(self, user_id):
        return [b for b in self.bookings.values() if b.user_id == user_id]

    def find_by_session_id(self, session_id):
        return [b for b in self.bookings.values() if b.session_id == session_id]

    def find_by_status(self, status):
        return [b for b in self.bookings.values() if b.status == status]

    def update(self, booking):
        self.bookings[booking.id] = booking
        return booking

    def delete(self, booking_id):
        if booking_id in self.bookings:
            del self.bookings[booking_id]
            return True
        return False

    def find_active_bookings_for_session(self, session_id):
        return [b for b in self.bookings.values()
                if b.session_id == session_id and b.status != BookingStatus.CANCELLED]

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

    def update(self, event):
        self.events[event.id] = event
        return event

@pytest.fixture
def booking_service():
    return BookingService(MockBookingRepository(), MockEventRepository())

@pytest.fixture
def test_event(booking_service):
    event = Event(
        name="Test Event",
        description="Test Description",
        venue="Test Venue",
        categories=["test"]
    )
    session = Session(
        event_id=event.id,
        start_time=datetime.now() + timedelta(days=1),
        end_time=datetime.now() + timedelta(days=1, hours=2),
        capacity=100,
        base_price=Decimal("50.00")
    )
    event.add_session(session)
    booking_service.event_repository.save(event)
    return event

def test_create_booking(booking_service, test_event):
    session = test_event.sessions[0]
    user_id = uuid4()
    
    booking = booking_service.create_booking(
        user_id=user_id,
        session_id=session.id,
        num_seats=2
    )

    assert booking.user_id == user_id
    assert booking.session_id == session.id
    assert booking.seats == 2
    assert booking.status == BookingStatus.PENDING
    assert session.booked_seats == 2

def test_create_booking_insufficient_seats(booking_service, test_event):
    session = test_event.sessions[0]
    user_id = uuid4()
    
    with pytest.raises(InsufficientSeatsError):
        booking_service.create_booking(
            user_id=user_id,
            session_id=session.id,
            num_seats=101  # More than capacity
        )

def test_create_booking_session_not_found(booking_service):
    user_id = uuid4()
    session_id = uuid4()
    
    with pytest.raises(SessionNotFoundError):
        booking_service.create_booking(
            user_id=user_id,
            session_id=session_id,
            num_seats=2
        )

def test_confirm_booking(booking_service, test_event):
    session = test_event.sessions[0]
    user_id = uuid4()
    
    booking = booking_service.create_booking(
        user_id=user_id,
        session_id=session.id,
        num_seats=2
    )

    confirmed_booking = booking_service.confirm_booking(booking.id)
    assert confirmed_booking.status == BookingStatus.CONFIRMED
    assert confirmed_booking.confirmed_at is not None

def test_cancel_booking(booking_service, test_event):
    session = test_event.sessions[0]
    user_id = uuid4()
    
    booking = booking_service.create_booking(
        user_id=user_id,
        session_id=session.id,
        num_seats=2
    )
    booking_service.confirm_booking(booking.id)

    cancelled_booking = booking_service.cancel_booking(booking.id)
    assert cancelled_booking.status == BookingStatus.CANCELLED
    assert cancelled_booking.cancelled_at is not None
    assert session.booked_seats == 0

def test_cancel_already_cancelled_booking(booking_service, test_event):
    session = test_event.sessions[0]
    user_id = uuid4()
    
    booking = booking_service.create_booking(
        user_id=user_id,
        session_id=session.id,
        num_seats=2
    )
    booking_service.confirm_booking(booking.id)
    booking_service.cancel_booking(booking.id)

    with pytest.raises(BookingError):
        booking_service.cancel_booking(booking.id)

def test_dynamic_pricing(booking_service, test_event):
    session = test_event.sessions[0]
    user_id = uuid4()
    
    # Book 80% of capacity to trigger price increase
    booking = booking_service.create_booking(
        user_id=user_id,
        session_id=session.id,
        num_seats=80  # 80% of capacity
    )

    # Try to book more seats - price should be higher
    booking2 = booking_service.create_booking(
        user_id=uuid4(),
        session_id=session.id,
        num_seats=10
    )

    assert booking2.price_per_seat > booking.price_per_seat 