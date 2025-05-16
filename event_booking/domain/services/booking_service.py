from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from ..entities.booking import Booking, BookingStatus
from ..entities.session import Session
from ..repositories.booking_repository import BookingRepository
from ..repositories.event_repository import EventRepository

class BookingError(Exception):
    """Base class for booking-related errors."""
    pass

class InsufficientSeatsError(BookingError):
    """Raised when there are not enough seats available."""
    pass

class SessionNotFoundError(BookingError):
    """Raised when the requested session is not found."""
    pass

class BookingService:
    def __init__(self, booking_repository: BookingRepository, event_repository: EventRepository):
        self.booking_repository = booking_repository
        self.event_repository = event_repository

    def create_booking(self, user_id: UUID, session_id: UUID, num_seats: int) -> Booking:
        """Create a new booking for a session."""
        # Find the event and session
        event = None
        session = None
        for evt in self.event_repository.find_all():
            if (s := evt.get_session(session_id)) is not None:
                event = evt
                session = s
                break

        if not session:
            raise SessionNotFoundError(f"Session {session_id} not found")

        # Check seat availability
        if not session.is_available() or session.available_seats < num_seats:
            raise InsufficientSeatsError("Not enough seats available")

        # Calculate price
        current_price = session.get_current_price()

        # Create booking
        booking = Booking(
            user_id=user_id,
            session_id=session_id,
            seats=num_seats,
            price_per_seat=current_price
        )

        # Update session
        if not session.book_seats(num_seats):
            raise BookingError("Failed to book seats")

        # Save booking
        saved_booking = self.booking_repository.save(booking)
        
        # Update event
        self.event_repository.update(event)

        return saved_booking

    def confirm_booking(self, booking_id: UUID) -> Booking:
        """Confirm a pending booking."""
        booking = self.booking_repository.find_by_id(booking_id)
        if not booking:
            raise BookingError(f"Booking {booking_id} not found")

        booking.confirm()
        return self.booking_repository.update(booking)

    def cancel_booking(self, booking_id: UUID) -> Booking:
        """Cancel a booking and release its seats."""
        booking = self.booking_repository.find_by_id(booking_id)
        if not booking:
            raise BookingError(f"Booking {booking_id} not found")

        if not booking.is_cancellable():
            raise BookingError("Booking cannot be cancelled")

        # Find the session
        event = None
        session = None
        for evt in self.event_repository.find_all():
            if (s := evt.get_session(booking.session_id)) is not None:
                event = evt
                session = s
                break

        if not session:
            raise SessionNotFoundError(f"Session {booking.session_id} not found")

        # Release seats
        if not session.release_seats(booking.seats):
            raise BookingError("Failed to release seats")

        # Cancel booking
        booking.cancel()
        
        # Save changes
        self.event_repository.update(event)
        return self.booking_repository.update(booking)

    def get_booking_status(self, booking_id: UUID) -> Optional[BookingStatus]:
        """Get the current status of a booking."""
        booking = self.booking_repository.find_by_id(booking_id)
        return booking.status if booking else None 