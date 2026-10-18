-- ============================================================================
-- Restaurant Reservation System - Database Schema (PostgreSQL Compatible)
-- ============================================================================

-- Enable UUID extension (gen_random_uuid is built-in in PG 13+, uuid-ossp for older versions)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ----------------------------------------------------------------------------
-- Trigger Function: Automatically update updated_at timestamp
-- ----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ----------------------------------------------------------------------------
-- 1. Customers
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS customers (
    customer_id     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            VARCHAR(100) NOT NULL,
    surname         VARCHAR(100) NOT NULL,
    phone           VARCHAR(50) NOT NULL,
    email           VARCHAR(255) UNIQUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ----------------------------------------------------------------------------
-- 2. Tables & Combinations
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS tables (
    table_id        SERIAL PRIMARY KEY,
    name            VARCHAR(20) NOT NULL UNIQUE,          -- e.g. 'T01', 'T12', 'B01'
    seats_min       INTEGER NOT NULL CHECK (seats_min > 0),
    seats_max       INTEGER NOT NULL CHECK (seats_max >= seats_min),
    area            VARCHAR(50) NOT NULL CHECK (area IN ('indoor', 'terrace', 'bar', 'private_room')),
    active          BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
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
    shift_id            SERIAL PRIMARY KEY,
    shift_name          VARCHAR(50) NOT NULL,             -- e.g. 'lunch', 'dinner'
    weekday             INTEGER NOT NULL CHECK (weekday BETWEEN 0 AND 6), -- 0 = Monday, 6 = Sunday
    weekday_name        VARCHAR(20) NOT NULL CHECK (weekday_name IN ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday')),
    start_time          TIME NOT NULL,                    -- e.g. '12:00:00'
    end_time            TIME NOT NULL,                    -- e.g. '15:00:00', '23:59:00'
    last_bookable_time  TIME NOT NULL                     -- e.g. '14:00:00', '22:00:00'
);

-- ----------------------------------------------------------------------------
-- 4. Closures (Exceptions / Holidays / Private Events)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS closures (
    closure_id          SERIAL PRIMARY KEY,
    date                DATE NOT NULL,                    -- YYYY-MM-DD
    shift_id            INTEGER REFERENCES opening_shifts(shift_id) ON DELETE SET NULL, -- NULL = full day closure
    reason              VARCHAR(255) NOT NULL,            -- e.g. 'Christmas Day', 'Private Event'
    created_at          TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ----------------------------------------------------------------------------
-- 5. Dining Rules (Length of stay by party size)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS dining_rules (
    rule_id             SERIAL PRIMARY KEY,
    party_size_from     INTEGER NOT NULL CHECK (party_size_from > 0),
    party_size_to       INTEGER NOT NULL CHECK (party_size_to >= party_size_from),
    duration_minutes    INTEGER NOT NULL CHECK (duration_minutes > 0),
    description         TEXT
);

-- ----------------------------------------------------------------------------
-- 6. Bookings
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS bookings (
    booking_id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id         UUID NOT NULL REFERENCES customers(customer_id) ON DELETE RESTRICT,
    start_time          TIMESTAMPTZ NOT NULL,
    end_time            TIMESTAMPTZ NOT NULL,
    party_size          INTEGER NOT NULL CHECK (party_size > 0),
    status              VARCHAR(20) NOT NULL CHECK (status IN ('pending', 'confirmed', 'cancelled', 'arrived', 'no_show')),
    source              VARCHAR(20) NOT NULL CHECK (source IN ('chatbot', 'phone', 'staff', 'website')),
    special_requests    TEXT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (end_time > start_time)
);

-- ----------------------------------------------------------------------------
-- 7. Booking Tables (Which tables a booking occupies)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS booking_tables (
    booking_id          UUID NOT NULL REFERENCES bookings(booking_id) ON DELETE CASCADE,
    table_id            INTEGER NOT NULL REFERENCES tables(table_id) ON DELETE RESTRICT,
    PRIMARY KEY (booking_id, table_id)
);

-- ----------------------------------------------------------------------------
-- Indexes for Performance
-- ----------------------------------------------------------------------------
-- ----------------------------------------------------------------------------
-- 8. Menu Categories
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS menu_categories (
    category_id     SERIAL PRIMARY KEY,
    name            VARCHAR(50) NOT NULL UNIQUE,          -- e.g. 'Appetizers & Starters', 'Handcrafted Burgers'
    description     TEXT,
    display_order   INTEGER NOT NULL DEFAULT 0,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ----------------------------------------------------------------------------
-- 9. Menu Items
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS menu_items (
    item_id         SERIAL PRIMARY KEY,
    category_id     INTEGER NOT NULL REFERENCES menu_categories(category_id) ON DELETE CASCADE,
    name            VARCHAR(100) NOT NULL UNIQUE,
    description     TEXT NOT NULL,
    price           NUMERIC(6, 2) NOT NULL CHECK (price >= 0),
    is_available    BOOLEAN NOT NULL DEFAULT TRUE,
    calories        INTEGER CHECK (calories >= 0),
    spicy_level     INTEGER NOT NULL DEFAULT 0 CHECK (spicy_level BETWEEN 0 AND 3),
    is_vegetarian   BOOLEAN NOT NULL DEFAULT FALSE,
    is_vegan        BOOLEAN NOT NULL DEFAULT FALSE,
    is_gluten_free  BOOLEAN NOT NULL DEFAULT FALSE,
    allergens       TEXT,                                 -- e.g. 'Dairy, Gluten, Shellfish'
    created_at      TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
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
CREATE INDEX IF NOT EXISTS idx_menu_items_category ON menu_items(category_id);
CREATE INDEX IF NOT EXISTS idx_menu_items_available ON menu_items(is_available);
CREATE INDEX IF NOT EXISTS idx_menu_items_dietary ON menu_items(is_vegetarian, is_vegan, is_gluten_free);
CREATE INDEX IF NOT EXISTS idx_menu_categories_order ON menu_categories(display_order);

-- ----------------------------------------------------------------------------
-- Triggers: Keep updated_at synchronized on updates
-- ----------------------------------------------------------------------------
DROP TRIGGER IF EXISTS trg_bookings_updated_at ON bookings;
CREATE TRIGGER trg_bookings_updated_at
BEFORE UPDATE ON bookings
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS trg_menu_items_updated_at ON menu_items;
CREATE TRIGGER trg_menu_items_updated_at
BEFORE UPDATE ON menu_items
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- ----------------------------------------------------------------------------
-- Views
-- ----------------------------------------------------------------------------

-- View combining tables with a comma-separated list of combinable adjacent table names
CREATE OR REPLACE VIEW v_tables_with_combinations AS
SELECT 
    t.table_id,
    t.name,
    t.seats_min,
    t.seats_max,
    t.area,
    t.active,
    COALESCE(
        STRING_AGG(c.name, ', ' ORDER BY c.name), 
        'None'
    ) AS combinable_with
FROM tables t
LEFT JOIN table_combinations tc ON t.table_id = tc.table_id
LEFT JOIN tables c ON tc.combinable_with_table_id = c.table_id
GROUP BY t.table_id, t.name, t.seats_min, t.seats_max, t.area, t.active;

-- Detailed booking overview joining customer and assigned tables
CREATE OR REPLACE VIEW v_booking_details AS
SELECT 
    b.booking_id,
    c.customer_id,
    c.name || ' ' || c.surname AS customer_name,
    c.phone AS customer_phone,
    c.email AS customer_email,
    b.party_size,
    b.start_time,
    b.end_time,
    ROUND(EXTRACT(EPOCH FROM (b.end_time - b.start_time)) / 60) AS duration_minutes,
    b.status,
    b.source,
    b.special_requests,
    b.created_at,
    COALESCE(STRING_AGG(t.name, ', ' ORDER BY t.name), 'None') AS assigned_tables,
    COALESCE(SUM(t.seats_max), 0) AS total_table_capacity
FROM bookings b
JOIN customers c ON b.customer_id = c.customer_id
LEFT JOIN booking_tables bt ON b.booking_id = bt.booking_id
LEFT JOIN tables t ON bt.table_id = t.table_id
GROUP BY 
    b.booking_id, c.customer_id, c.name, c.surname, c.phone, c.email, 
    b.party_size, b.start_time, b.end_time, b.status, b.source, 
    b.special_requests, b.created_at;

-- Detailed menu items overview with category and dietary classification
CREATE OR REPLACE VIEW v_menu_details AS
SELECT 
    mi.item_id,
    mi.name,
    mc.name AS category_name,
    mc.category_id,
    mi.description,
    mi.price,
    mi.calories,
    mi.spicy_level,
    mi.is_vegetarian,
    mi.is_vegan,
    mi.is_gluten_free,
    mi.allergens,
    mi.is_available,
    mc.display_order AS category_order
FROM menu_items mi
JOIN menu_categories mc ON mi.category_id = mc.category_id
ORDER BY mc.display_order ASC, mi.item_id ASC;

