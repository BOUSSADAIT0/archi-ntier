-- Create database
CREATE DATABASE IF NOT EXISTS event_booking;
USE event_booking;

-- Create tables
CREATE TABLE IF NOT EXISTS events (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    venue VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS event_categories (
    event_id VARCHAR(36),
    category VARCHAR(50),
    PRIMARY KEY (event_id, category),
    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS sessions (
    id VARCHAR(36) PRIMARY KEY,
    event_id VARCHAR(36) NOT NULL,
    start_time DATETIME NOT NULL,
    end_time DATETIME NOT NULL,
    capacity INT NOT NULL,
    booked_seats INT NOT NULL DEFAULT 0,
    base_price DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS bookings (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    session_id VARCHAR(36) NOT NULL,
    seats INT NOT NULL,
    price_per_seat DECIMAL(10, 2) NOT NULL,
    status VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    confirmed_at TIMESTAMP NULL,
    cancelled_at TIMESTAMP NULL,
    FOREIGN KEY (session_id) REFERENCES sessions(id)
);

-- Create indexes
CREATE INDEX idx_events_venue ON events(venue);
CREATE INDEX idx_sessions_event_id ON sessions(event_id);
CREATE INDEX idx_sessions_start_time ON sessions(start_time);
CREATE INDEX idx_bookings_user_id ON bookings(user_id);
CREATE INDEX idx_bookings_session_id ON bookings(session_id);
CREATE INDEX idx_bookings_status ON bookings(status);

-- Create HAProxy check user
CREATE USER IF NOT EXISTS 'haproxy_check'@'%';

-- Grant necessary privileges
GRANT SELECT ON event_booking.* TO 'app_user'@'%';
GRANT INSERT ON event_booking.* TO 'app_user'@'%';
GRANT UPDATE ON event_booking.* TO 'app_user'@'%';
GRANT DELETE ON event_booking.* TO 'app_user'@'%'; 