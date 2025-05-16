from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
from decimal import Decimal

@dataclass
class Session:
    event_id: UUID
    start_time: datetime
    end_time: datetime
    capacity: int
    base_price: Decimal
    id: UUID = field(default_factory=uuid4)
    booked_seats: int = 0
    _price_adjustment_factor: Decimal = Decimal('1.0')

    def is_available(self) -> bool:
        """Check if there are any seats available."""
        return self.available_seats > 0

    @property
    def available_seats(self) -> int:
        """Get number of available seats."""
        return max(0, self.capacity - self.booked_seats)

    def calculate_occupancy_rate(self) -> Decimal:
        """Calculate the current occupancy rate."""
        if self.capacity == 0:
            return Decimal('0')
        return Decimal(self.booked_seats) / Decimal(self.capacity)

    def book_seats(self, num_seats: int) -> bool:
        """Try to book a number of seats."""
        if num_seats <= 0:
            raise ValueError("Number of seats must be positive")
        if num_seats > self.available_seats:
            return False
        self.booked_seats += num_seats
        self._adjust_price_factor()
        return True

    def release_seats(self, num_seats: int) -> bool:
        """Release previously booked seats."""
        if num_seats <= 0:
            raise ValueError("Number of seats must be positive")
        if num_seats > self.booked_seats:
            return False
        self.booked_seats -= num_seats
        self._adjust_price_factor()
        return True

    def get_current_price(self) -> Decimal:
        """Get the current price based on occupancy rate."""
        return self.base_price * self._price_adjustment_factor

    def _adjust_price_factor(self) -> None:
        """Adjust price based on occupancy rate."""
        occupancy_rate = self.calculate_occupancy_rate()
        if occupancy_rate >= Decimal('0.8'):
            self._price_adjustment_factor = Decimal('1.5')
        elif occupancy_rate >= Decimal('0.6'):
            self._price_adjustment_factor = Decimal('1.2')
        elif occupancy_rate <= Decimal('0.2'):
            self._price_adjustment_factor = Decimal('0.8')
        else:
            self._price_adjustment_factor = Decimal('1.0')

    def validate(self) -> bool:
        """Validate session data."""
        if self.start_time >= self.end_time:
            raise ValueError("End time must be after start time")
        if self.capacity <= 0:
            raise ValueError("Capacity must be positive")
        if self.base_price <= Decimal('0'):
            raise ValueError("Base price must be positive")
        if self.booked_seats < 0:
            raise ValueError("Booked seats cannot be negative")
        if self.booked_seats > self.capacity:
            raise ValueError("Booked seats cannot exceed capacity")
        return True 