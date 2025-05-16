from typing import List, Optional
from uuid import UUID
import pymysql
from pymysql.cursors import DictCursor

from ...domain.entities.event import Event
from ...domain.entities.session import Session
from ...domain.repositories.event_repository import EventRepository

class MariaDBEventRepository(EventRepository):
    def __init__(self, connection_pool):
        self.connection_pool = connection_pool

    def save(self, event: Event) -> Event:
        with self.connection_pool.get_connection() as connection:
            with connection.cursor() as cursor:
                # Save event
                cursor.execute("""
                    INSERT INTO events (id, name, description, venue, created_at)
                    VALUES (%s, %s, %s, %s, %s)
                """, (str(event.id), event.name, event.description, event.venue, event.created_at))

                # Save categories
                for category in event.categories:
                    cursor.execute("""
                        INSERT INTO event_categories (event_id, category)
                        VALUES (%s, %s)
                    """, (str(event.id), category))

                # Save sessions
                for session in event.sessions:
                    cursor.execute("""
                        INSERT INTO sessions (id, event_id, start_time, end_time, capacity, booked_seats)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (str(session.id), str(event.id), session.start_time, session.end_time,
                          session.capacity, session.booked_seats))

            connection.commit()
            return event

    def find_by_id(self, event_id: UUID) -> Optional[Event]:
        with self.connection_pool.get_connection() as connection:
            with connection.cursor(DictCursor) as cursor:
                # Get event
                cursor.execute("""
                    SELECT * FROM events WHERE id = %s
                """, (str(event_id),))
                event_data = cursor.fetchone()

                if not event_data:
                    return None

                # Get categories
                cursor.execute("""
                    SELECT category FROM event_categories WHERE event_id = %s
                """, (str(event_id),))
                categories = [row['category'] for row in cursor.fetchall()]

                # Get sessions
                cursor.execute("""
                    SELECT * FROM sessions WHERE event_id = %s
                """, (str(event_id),))
                sessions_data = cursor.fetchall()

                # Create Event object
                event = Event(
                    name=event_data['name'],
                    description=event_data['description'],
                    venue=event_data['venue'],
                    categories=categories,
                    id=UUID(event_data['id']),
                    created_at=event_data['created_at']
                )

                # Add sessions
                for session_data in sessions_data:
                    session = Session(
                        event_id=UUID(session_data['event_id']),
                        start_time=session_data['start_time'],
                        end_time=session_data['end_time'],
                        capacity=session_data['capacity'],
                        base_price=session_data['base_price'],
                        id=UUID(session_data['id']),
                        booked_seats=session_data['booked_seats']
                    )
                    event.add_session(session)

                return event

    def find_all(self) -> List[Event]:
        with self.connection_pool.get_connection() as connection:
            with connection.cursor(DictCursor) as cursor:
                cursor.execute("SELECT id FROM events")
                event_ids = [UUID(row['id']) for row in cursor.fetchall()]
                return [self.find_by_id(event_id) for event_id in event_ids]

    def find_by_category(self, category: str) -> List[Event]:
        with self.connection_pool.get_connection() as connection:
            with connection.cursor(DictCursor) as cursor:
                cursor.execute("""
                    SELECT DISTINCT e.id
                    FROM events e
                    JOIN event_categories ec ON e.id = ec.event_id
                    WHERE ec.category = %s
                """, (category,))
                event_ids = [UUID(row['id']) for row in cursor.fetchall()]
                return [self.find_by_id(event_id) for event_id in event_ids]

    def update(self, event: Event) -> Event:
        with self.connection_pool.get_connection() as connection:
            with connection.cursor() as cursor:
                # Update event
                cursor.execute("""
                    UPDATE events
                    SET name = %s, description = %s, venue = %s
                    WHERE id = %s
                """, (event.name, event.description, event.venue, str(event.id)))

                # Update categories
                cursor.execute("DELETE FROM event_categories WHERE event_id = %s", (str(event.id),))
                for category in event.categories:
                    cursor.execute("""
                        INSERT INTO event_categories (event_id, category)
                        VALUES (%s, %s)
                    """, (str(event.id), category))

                # Update sessions
                for session in event.sessions:
                    cursor.execute("""
                        INSERT INTO sessions (id, event_id, start_time, end_time, capacity, booked_seats)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE
                            start_time = VALUES(start_time),
                            end_time = VALUES(end_time),
                            capacity = VALUES(capacity),
                            booked_seats = VALUES(booked_seats)
                    """, (str(session.id), str(event.id), session.start_time, session.end_time,
                          session.capacity, session.booked_seats))

            connection.commit()
            return event

    def delete(self, event_id: UUID) -> bool:
        with self.connection_pool.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM events WHERE id = %s", (str(event_id),))
                connection.commit()
                return cursor.rowcount > 0 