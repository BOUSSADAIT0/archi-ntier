-- Create events table
CREATE TABLE IF NOT EXISTS events (
    id CHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    venue VARCHAR(255) NOT NULL,
    categories JSON NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create sessions table
CREATE TABLE IF NOT EXISTS sessions (
    id CHAR(36) PRIMARY KEY,
    event_id CHAR(36) NOT NULL,
    start_time DATETIME NOT NULL,
    end_time DATETIME NOT NULL,
    capacity INT NOT NULL,
    base_price DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (event_id) REFERENCES events(id)
);

-- Create bookings table
CREATE TABLE IF NOT EXISTS bookings (
    id CHAR(36) PRIMARY KEY,
    user_id CHAR(36) NOT NULL,
    session_id CHAR(36) NOT NULL,
    seats INT NOT NULL,
    price_per_seat DECIMAL(10,2) NOT NULL,
    status ENUM('PENDING', 'CONFIRMED', 'CANCELLED') NOT NULL DEFAULT 'PENDING',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    confirmed_at TIMESTAMP NULL,
    cancelled_at TIMESTAMP NULL,
    FOREIGN KEY (session_id) REFERENCES sessions(id)
);

-- Insert some sample data
INSERT INTO events (id, name, description, venue, categories) VALUES
('550e8400-e29b-41d4-a716-446655440000', 'Concert Rock', 'Un super concert de rock', 'Stade de France', '["musique", "rock"]'),
('550e8400-e29b-41d4-a716-446655440001', 'Théâtre Moderne', 'Une pièce de théâtre contemporaine', 'Théâtre du Châtelet', '["théâtre", "culture"]');

INSERT INTO sessions (id, event_id, start_time, end_time, capacity, base_price) VALUES
('660e8400-e29b-41d4-a716-446655440000', '550e8400-e29b-41d4-a716-446655440000', '2024-06-01 20:00:00', '2024-06-01 23:00:00', 1000, 50.00),
('660e8400-e29b-41d4-a716-446655440001', '550e8400-e29b-41d4-a716-446655440001', '2024-06-15 19:30:00', '2024-06-15 22:00:00', 500, 35.00); 