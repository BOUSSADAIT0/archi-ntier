from typing import List, Optional
from uuid import UUID
import pymysql
from pymysql.cursors import DictCursor

from ...domain.entities.booking import Booking, BookingStatus
from ...domain.repositories.booking_repository import BookingRepository

class MariaDBBookingRepository(BookingRepository):
    def __init__(self, connection_pool):
        self.connection_pool = connection_pool

    def save(self, booking: Booking) -> Booking:
        with self.connection_pool.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO bookings (
                        id, user_id, session_id, seats, price_per_seat,
                        status, created_at, confirmed_at, cancelled_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    str(booking.id), str(booking.user_id), str(booking.session_id),
                    booking.seats, booking.price_per_seat, booking.status.value,
                    booking.created_at, booking.confirmed_at, booking.cancelled_at
                ))
            connection.commit()
            return booking

    def find_by_id(self, booking_id: UUID) -> Optional[Booking]:
        with self.connection_pool.get_connection() as connection:
            with connection.cursor(DictCursor) as cursor:
                cursor.execute("""
                    SELECT * FROM bookings WHERE id = %s
                """, (str(booking_id),))
                data = cursor.fetchone()

                if not data:
                    return None

                return Booking(
                    id=UUID(data['id']),
                    user_id=UUID(data['user_id']),
                    session_id=UUID(data['session_id']),
                    seats=data['seats'],
                    price_per_seat=data['price_per_seat'],
                    status=BookingStatus(data['status']),
                    created_at=data['created_at'],
                    confirmed_at=data['confirmed_at'],
                    cancelled_at=data['cancelled_at']
                )

    def find_by_user_id(self, user_id: UUID) -> List[Booking]:
        with self.connection_pool.get_connection() as connection:
            with connection.cursor(DictCursor) as cursor:
                cursor.execute("""
                    SELECT * FROM bookings WHERE user_id = %s
                    ORDER BY created_at DESC
                """, (str(user_id),))
                return [
                    Booking(
                        id=UUID(data['id']),
                        user_id=UUID(data['user_id']),
                        session_id=UUID(data['session_id']),
                        seats=data['seats'],
                        price_per_seat=data['price_per_seat'],
                        status=BookingStatus(data['status']),
                        created_at=data['created_at'],
                        confirmed_at=data['confirmed_at'],
                        cancelled_at=data['cancelled_at']
                    )
                    for data in cursor.fetchall()
                ]

    def find_by_session_id(self, session_id: UUID) -> List[Booking]:
        with self.connection_pool.get_connection() as connection:
            with connection.cursor(DictCursor) as cursor:
                cursor.execute("""
                    SELECT * FROM bookings WHERE session_id = %s
                    ORDER BY created_at DESC
                """, (str(session_id),))
                return [
                    Booking(
                        id=UUID(data['id']),
                        user_id=UUID(data['user_id']),
                        session_id=UUID(data['session_id']),
                        seats=data['seats'],
                        price_per_seat=data['price_per_seat'],
                        status=BookingStatus(data['status']),
                        created_at=data['created_at'],
                        confirmed_at=data['confirmed_at'],
                        cancelled_at=data['cancelled_at']
                    )
                    for data in cursor.fetchall()
                ]

    def find_by_status(self, status: BookingStatus) -> List[Booking]:
        with self.connection_pool.get_connection() as connection:
            with connection.cursor(DictCursor) as cursor:
                cursor.execute("""
                    SELECT * FROM bookings WHERE status = %s
                    ORDER BY created_at DESC
                """, (status.value,))
                return [
                    Booking(
                        id=UUID(data['id']),
                        user_id=UUID(data['user_id']),
                        session_id=UUID(data['session_id']),
                        seats=data['seats'],
                        price_per_seat=data['price_per_seat'],
                        status=BookingStatus(data['status']),
                        created_at=data['created_at'],
                        confirmed_at=data['confirmed_at'],
                        cancelled_at=data['cancelled_at']
                    )
                    for data in cursor.fetchall()
                ]

    def update(self, booking: Booking) -> Booking:
        with self.connection_pool.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE bookings
                    SET status = %s, confirmed_at = %s, cancelled_at = %s
                    WHERE id = %s
                """, (
                    booking.status.value,
                    booking.confirmed_at,
                    booking.cancelled_at,
                    str(booking.id)
                ))
            connection.commit()
            return booking

    def delete(self, booking_id: UUID) -> bool:
        with self.connection_pool.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM bookings WHERE id = %s", (str(booking_id),))
                connection.commit()
                return cursor.rowcount > 0

    def find_active_bookings_for_session(self, session_id: UUID) -> List[Booking]:
        with self.connection_pool.get_connection() as connection:
            with connection.cursor(DictCursor) as cursor:
                cursor.execute("""
                    SELECT * FROM bookings
                    WHERE session_id = %s
                    AND status != %s
                    ORDER BY created_at DESC
                """, (str(session_id), BookingStatus.CANCELLED.value))
                return [
                    Booking(
                        id=UUID(data['id']),
                        user_id=UUID(data['user_id']),
                        session_id=UUID(data['session_id']),
                        seats=data['seats'],
                        price_per_seat=data['price_per_seat'],
                        status=BookingStatus(data['status']),
                        created_at=data['created_at'],
                        confirmed_at=data['confirmed_at'],
                        cancelled_at=data['cancelled_at']
                    )
                    for data in cursor.fetchall()
                ] 