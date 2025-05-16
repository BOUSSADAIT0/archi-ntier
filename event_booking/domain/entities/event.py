from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

@dataclass
class Event:
    name: str
    description: str
    venue: str
    categories: List[str]
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=datetime.utcnow)
    sessions: List['Session'] = field(default_factory=list)

    def add_session(self, session: 'Session') -> None:
        """Add a session to the event."""
        if not any(s.id == session.id for s in self.sessions):
            self.sessions.append(session)

    def remove_session(self, session_id: UUID) -> None:
        """Remove a session from the event."""
        self.sessions = [s for s in self.sessions if s.id != session_id]

    def get_available_sessions(self) -> List['Session']:
        """Get all sessions that still have available seats."""
        return [s for s in self.sessions if s.is_available()]

    def get_session(self, session_id: UUID) -> Optional['Session']:
        """Get a specific session by ID."""
        return next((s for s in self.sessions if s.id == session_id), None)

    def validate(self) -> bool:
        """Validate event data."""
        if not self.name or len(self.name.strip()) == 0:
            raise ValueError("Event name cannot be empty")
        if not self.venue or len(self.venue.strip()) == 0:
            raise ValueError("Venue cannot be empty")
        if not self.categories:
            raise ValueError("Event must have at least one category")
        return True 