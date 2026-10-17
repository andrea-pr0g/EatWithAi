-- ============================================================================
-- Restaurant Reservation System - Database Schema (SQLite & ANSI SQL Compatible)
-- ============================================================================

-- Enforce Foreign Key constraints (SQLite)
PRAGMA foreign_keys = ON;

-- ----------------------------------------------------------------------------
-- 1. Customers
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS customers (
    customer_id     TEXT PRIMARY KEY,              -- UUID (v4 format string)
    name            TEXT NOT NULL,
    surname         TEXT NOT NULL,
    phone           TEXT NOT NULL,
    email           TEXT UNIQUE,
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ----------------------------------------------------------------------------
-- 2. Tables & Combinations
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS tables (
    table_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT NOT NULL UNIQUE,          -- e.g. 'T01', 'T12', 'B01'
    seats_min       INTEGER NOT NULL CHECK (seats_min > 0),
    seats_max       INTEGER NOT NULL CHECK (seats_max >= seats_min),
    area            TEXT NOT NULL CHECK (area IN ('indoor', 'terrace', 'bar', 'private_room')),
    active          BOOLEAN NOT NULL DEFAULT 1 CHECK (active IN (0, 1)),
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Normalized junction table for tables that can be joined together for large groups
CREATE TABLE IF NOT EXISTS table_combinations (
    table_id                    INTEGER NOT NULL REFERENCES tables(table_id) ON DELETE CASCADE,
    combinable_with_table_id    INTEGER NOT NULL REFERENCES tables(table_id) ON DELETE CASCADE,
    PRIMARY KEY (table_id, combinable_with_table_id),
    CHECK (table_id <> combinable_with_table_id)
);

-- ----------------------------------------------------------------------------
-- 3. Opening Shifts
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS opening_shifts (
    shift_id            INTEGER PRIMARY KEY AUTOINCREMENT,
    shift_name          TEXT NOT NULL,             -- e.g. 'lunch', 'dinner'
    weekday             INTEGER NOT NULL CHECK (weekday BETWEEN 0 AND 6), -- 0 = Monday, 6 = Sunday
    weekday_name        TEXT NOT NULL CHECK (weekday_name IN ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday')),
    start_time          TEXT NOT NULL,             -- HH:MM (e.g. '12:00')
    end_time            TEXT NOT NULL,             -- HH:MM (e.g. '15:00', '23:59')
    last_bookable_time  TEXT NOT NULL              -- HH:MM (e.g. '14:00', '22:00')
);

-- ----------------------------------------------------------------------------
-- 4. Closures (Exceptions / Holidays / Private Events)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS closures (
    closure_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    date                TEXT NOT NULL,             -- YYYY-MM-DD
    shift_id            INTEGER REFERENCES opening_shifts(shift_id) ON DELETE SET NULL, -- NULL = full day closure
    reason              TEXT NOT NULL,             -- e.g. 'Christmas Day', 'Private Event'
    created_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ----------------------------------------------------------------------------
-- 5. Dining Rules (Length of stay by party size)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS dining_rules (
    rule_id             INTEGER PRIMARY KEY AUTOINCREMENT,
    party_size_from     INTEGER NOT NULL CHECK (party_size_from > 0),
    party_size_to       INTEGER NOT NULL CHECK (party_size_to >= party_size_from),
    duration_minutes    INTEGER NOT NULL CHECK (duration_minutes > 0),
    description         TEXT
);

-- ----------------------------------------------------------------------------
-- 6. Bookings
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS bookings (
    booking_id          TEXT PRIMARY KEY,          -- UUID (v4)
    customer_id         TEXT NOT NULL REFERENCES customers(customer_id) ON DELETE RESTRICT,
    start_time          TIMESTAMP NOT NULL,        -- YYYY-MM-DD HH:MM:SS
    end_time            TIMESTAMP NOT NULL,        -- YYYY-MM-DD HH:MM:SS (calculated from dining_rules)
    party_size          INTEGER NOT NULL CHECK (party_size > 0),
    status              TEXT NOT NULL CHECK (status IN ('pending', 'confirmed', 'cancelled', 'arrived', 'no_show')),
    source              TEXT NOT NULL CHECK (source IN ('chatbot', 'phone', 'staff', 'website')),
    special_requests    TEXT,
    created_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (end_time > start_time)
);

-- ----------------------------------------------------------------------------
-- 7. Booking Tables (Which tables a booking occupies)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS booking_tables (
    booking_id          TEXT NOT NULL REFERENCES bookings(booking_id) ON DELETE CASCADE,
    table_id            INTEGER NOT NULL REFERENCES tables(table_id) ON DELETE RESTRICT,
    PRIMARY KEY (booking_id, table_id)
);

-- ----------------------------------------------------------------------------
-- Indexes for Performance
-- ----------------------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_customers_email ON customers(email);
CREATE INDEX IF NOT EXISTS idx_customers_phone ON customers(phone);
CREATE INDEX IF NOT EXISTS idx_tables_area ON tables(area);
CREATE INDEX IF NOT EXISTS idx_tables_active ON tables(active);
CREATE INDEX IF NOT EXISTS idx_opening_shifts_weekday ON opening_shifts(weekday);
CREATE INDEX IF NOT EXISTS idx_closures_date ON closures(date);
CREATE INDEX IF NOT EXISTS idx_bookings_customer ON bookings(customer_id);
CREATE INDEX IF NOT EXISTS idx_bookings_start_end ON bookings(start_time, end_time);
CREATE INDEX IF NOT EXISTS idx_bookings_status ON bookings(status);
CREATE INDEX IF NOT EXISTS idx_booking_tables_table ON booking_tables(table_id);

-- ----------------------------------------------------------------------------
-- Trigger: Update updated_at timestamp on bookings update
-- ----------------------------------------------------------------------------
CREATE TRIGGER IF NOT EXISTS trg_bookings_updated_at
AFTER UPDATE ON bookings
FOR EACH ROW
BEGIN
    UPDATE bookings SET updated_at = CURRENT_TIMESTAMP WHERE booking_id = OLD.booking_id;
END;

-- ----------------------------------------------------------------------------
-- Convenient Views
-- ----------------------------------------------------------------------------

-- View combining tables with a comma-separated list of combinable adjacent table names
CREATE VIEW IF NOT EXISTS v_tables_with_combinations AS
SELECT 
    t.table_id,
    t.name,
    t.seats_min,
    t.seats_max,
    t.area,
    t.active,
    COALESCE(
        GROUP_CONCAT(c.name, ', '), 
        'None'
    ) AS combinable_with
FROM tables t
LEFT JOIN table_combinations tc ON t.table_id = tc.table_id
LEFT JOIN tables c ON tc.combinable_with_table_id = c.table_id
GROUP BY t.table_id;

-- Detailed booking overview joining customer and assigned tables
CREATE VIEW IF NOT EXISTS v_booking_details AS
SELECT 
    b.booking_id,
    c.customer_id,
    c.name || ' ' || c.surname AS customer_name,
    c.phone AS customer_phone,
    c.email AS customer_email,
    b.party_size,
    b.start_time,
    b.end_time,
    ROUND((STRFTIME('%s', b.end_time) - STRFTIME('%s', b.start_time)) / 60) AS duration_minutes,
    b.status,
    b.source,
    b.special_requests,
    b.created_at,
    GROUP_CONCAT(t.name, ', ') AS assigned_tables,
    SUM(t.seats_max) AS total_table_capacity
FROM bookings b
JOIN customers c ON b.customer_id = c.customer_id
LEFT JOIN booking_tables bt ON b.booking_id = bt.booking_id
LEFT JOIN tables t ON bt.table_id = t.table_id
GROUP BY b.booking_id;
