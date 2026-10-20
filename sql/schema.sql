-- ==========================================
-- Roomly: структура базы данных (ПР7)
-- ==========================================

CREATE TABLE IF NOT EXISTS rooms (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    inventory_number TEXT DEFAULT '',
    capacity INTEGER NOT NULL DEFAULT 1,
    operational INTEGER NOT NULL DEFAULT 1,
    under_maintenance INTEGER NOT NULL DEFAULT 0,
    required_level INTEGER NOT NULL DEFAULT 1,
    hourly_rate REAL NOT NULL DEFAULT 0.0
);

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL DEFAULT '',
    role TEXT NOT NULL DEFAULT 'студент',
    access_level INTEGER NOT NULL DEFAULT 1,
    briefing_passed INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS bookings (
    id INTEGER PRIMARY KEY,
    room_id INTEGER NOT NULL,
    equipment_id INTEGER,
    user_id INTEGER NOT NULL,
    booking_date TEXT NOT NULL,
    duration_hours REAL NOT NULL DEFAULT 1.0,
    cost REAL NOT NULL DEFAULT 0.0,
    is_cancelled INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (room_id) REFERENCES rooms(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE VIEW IF NOT EXISTS equipment AS
SELECT
    id,
    name,
    inventory_number,
    capacity,
    operational,
    under_maintenance,
    required_level,
    hourly_rate
FROM rooms;
