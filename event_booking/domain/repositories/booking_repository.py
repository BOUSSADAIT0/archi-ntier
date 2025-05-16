from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from ..entities.booking import Booking, BookingStatus

class BookingRepository(ABC):
    @abstractmethod
    def save(self, booking: Booking) -> Booking:
        """Save a booking to the repository."""
        pass

    @abstractmethod
    def find_by_id(self, booking_id: UUID) -> Optional[Booking]:
        """Find a booking by its ID."""
        pass

    @abstractmethod
    def find_by_user_id(self, user_id: UUID) -> List[Booking]:
        """Find all bookings for a user."""
        pass

    @abstractmethod
    def find_by_session_id(self, session_id: UUID) -> List[Booking]:
        """Find all bookings for a session."""
        pass

    @abstractmethod
    def find_by_status(self, status: BookingStatus) -> List[Booking]:
        """Find all bookings with a specific status."""
        pass

    @abstractmethod
    def update(self, booking: Booking) -> Booking:
        """Update an existing booking."""
        pass

    @abstractmethod
    def delete(self, booking_id: UUID) -> bool:
        """Delete a booking by its ID."""
        pass

    @abstractmethod
    def find_active_bookings_for_session(self, session_id: UUID) -> List[Booking]:
        """Find all non-cancelled bookings for a session."""
        pass 