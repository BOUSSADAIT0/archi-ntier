from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from ..entities.event import Event

class EventRepository(ABC):
    @abstractmethod
    def save(self, event: Event) -> Event:
        """Save an event to the repository."""
        pass

    @abstractmethod
    def find_by_id(self, event_id: UUID) -> Optional[Event]:
        """Find an event by its ID."""
        pass

    @abstractmethod
    def find_all(self) -> List[Event]:
        """Find all events."""
        pass

    @abstractmethod
    def find_by_category(self, category: str) -> List[Event]:
        """Find events by category."""
        pass

    @abstractmethod
    def delete(self, event_id: UUID) -> bool:
        """Delete an event by its ID."""
        pass

    @abstractmethod
    def update(self, event: Event) -> Event:
        """Update an existing event."""
        pass 