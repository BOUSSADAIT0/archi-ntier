from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum
from uuid import UUID, uuid4
from typing import Optional

class BookingStatus(Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"

@dataclass
class Booking:
    user_id: UUID
    session_id: UUID
    seats: int
    price_per_seat: Decimal
    id: UUID = field(default_factory=uuid4)
    status: BookingStatus = BookingStatus.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)
    confirmed_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None

    def confirm(self) -> None:
        """Confirm the booking."""
        if self.status != BookingStatus.PENDING:
            raise ValueError("Can only confirm pending bookings")
        self.status = BookingStatus.CONFIRMED
        self.confirmed_at = datetime.utcnow()

    def cancel(self) -> None:
        """Cancel the booking."""
        if self.status == BookingStatus.CANCELLED:
            raise ValueError("Booking is already cancelled")
        self.status = BookingStatus.CANCELLED
        self.cancelled_at = datetime.utcnow()

    def calculate_total_price(self) -> Decimal:
        """Calculate the total price for all seats."""
        return self.price_per_seat * Decimal(self.seats)

    def is_cancellable(self) -> bool:
        """Check if the booking can be cancelled."""
        if self.status != BookingStatus.CONFIRMED:
            return False
        # Add any additional business rules for cancellation here
        return True

    def validate(self) -> bool:
        """Validate booking data."""
        if self.seats <= 0:
            raise ValueError("Number of seats must be positive")
        if self.price_per_seat <= Decimal('0'):
            raise ValueError("Price per seat must be positive")
        if self.status == BookingStatus.CONFIRMED and not self.confirmed_at:
            raise ValueError("Confirmed bookings must have confirmation timestamp")
        if self.status == BookingStatus.CANCELLED and not self.cancelled_at:
            raise ValueError("Cancelled bookings must have cancellation timestamp")
        return True 