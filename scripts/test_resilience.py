#!/usr/bin/env python3
import time
import uuid
import random
from datetime import datetime, timedelta
import subprocess
import pymysql
from pymysql.cursors import DictCursor

def create_connection(host='localhost', port=3309):
    """Create a database connection."""
    return pymysql.connect(
        host=host,
        port=port,
        user='app_user',
        password='app_password',
        database='event_booking',
        cursorclass=DictCursor
    )

def create_test_event(conn):
    """Create a test event with a session."""
    event_id = str(uuid.uuid4())
    session_id = str(uuid.uuid4())
    
    with conn.cursor() as cursor:
        # Create event
        cursor.execute("""
            INSERT INTO events (id, name, description, venue)
            VALUES (%s, %s, %s, %s)
        """, (event_id, 'Test Event', 'Test Description', 'Test Venue'))

        # Create event category
        cursor.execute("""
            INSERT INTO event_categories (event_id, category)
            VALUES (%s, %s)
        """, (event_id, 'test'))

        # Create session
        start_time = datetime.now() + timedelta(days=1)
        end_time = start_time + timedelta(hours=2)
        cursor.execute("""
            INSERT INTO sessions (id, event_id, start_time, end_time, capacity, base_price)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (session_id, event_id, start_time, end_time, 100, 50.00))

    conn.commit()
    return session_id

def simulate_bookings(conn, session_id, num_bookings=10):
    """Simulate multiple concurrent bookings."""
    successful_bookings = 0
    failed_bookings = 0

    for _ in range(num_bookings):
        try:
            booking_id = str(uuid.uuid4())
            user_id = str(uuid.uuid4())
            seats = random.randint(1, 5)

            with conn.cursor() as cursor:
                # Check available seats
                cursor.execute("""
                    SELECT capacity, booked_seats
                    FROM sessions
                    WHERE id = %s
                    FOR UPDATE
                """, (session_id,))
                session = cursor.fetchone()

                if session['capacity'] - session['booked_seats'] >= seats:
                    # Create booking
                    cursor.execute("""
                        INSERT INTO bookings (id, user_id, session_id, seats, price_per_seat, status)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (booking_id, user_id, session_id, seats, 50.00, 'CONFIRMED'))

                    # Update session
                    cursor.execute("""
                        UPDATE sessions
                        SET booked_seats = booked_seats + %s
                        WHERE id = %s
                    """, (seats, session_id))

                    successful_bookings += 1
                else:
                    failed_bookings += 1

            conn.commit()
            time.sleep(0.1)  # Small delay to simulate real-world usage

        except Exception as e:
            print(f"Booking failed: {e}")
            failed_bookings += 1
            conn.rollback()

    return successful_bookings, failed_bookings

def test_node_failure():
    """Test system behavior during node failure."""
    print("Starting node failure test...")
    
    # Create initial connection through HAProxy
    conn = create_connection()
    
    # Create test event and session
    session_id = create_test_event(conn)
    print(f"Created test session: {session_id}")

    # Start booking simulation
    print("Starting booking simulation...")
    
    # Simulate node failure by stopping one of the MariaDB containers
    print("Simulating node failure...")
    subprocess.run(["docker", "stop", "mariadb-node-2"])
    
    try:
        # Continue making bookings
        successful, failed = simulate_bookings(conn, session_id)
        print(f"After node failure: {successful} successful bookings, {failed} failed bookings")
        
        # Verify data consistency
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT booked_seats
                FROM sessions
                WHERE id = %s
            """, (session_id,))
            session = cursor.fetchone()
            
            cursor.execute("""
                SELECT SUM(seats) as total_booked
                FROM bookings
                WHERE session_id = %s AND status = 'CONFIRMED'
            """, (session_id,))
            bookings = cursor.fetchone()
            
            print(f"Session booked_seats: {session['booked_seats']}")
            print(f"Total seats in bookings: {bookings['total_booked']}")
            
            assert session['booked_seats'] == bookings['total_booked'], "Data inconsistency detected!"
            print("Data consistency verified!")
            
    finally:
        # Restore the failed node
        print("Restoring failed node...")
        subprocess.run(["docker", "start", "mariadb-node-2"])
        time.sleep(5)  # Wait for node to rejoin cluster
        
    print("Node failure test completed!")

if __name__ == '__main__':
    try:
        test_node_failure()
    except Exception as e:
        print(f"Test failed: {e}")
    finally:
        # Ensure all nodes are running
        subprocess.run(["docker", "start", "mariadb-node-1"])
        subprocess.run(["docker", "start", "mariadb-node-2"])
        subprocess.run(["docker", "start", "mariadb-node-3"]) 