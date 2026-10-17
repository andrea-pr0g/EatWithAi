-- ============================================================================
-- Restaurant Reservation System - Seed Data
-- ============================================================================

-- Ensure Foreign Keys are respected
PRAGMA foreign_keys = ON;

-- ----------------------------------------------------------------------------
-- 1. Customers (10 Sample Customers with UUIDs)
-- ----------------------------------------------------------------------------
INSERT INTO customers (customer_id, name, surname, phone, email, created_at) VALUES
('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 'Marco', 'Rossi', '+39 340 1234567', 'marco.rossi@example.com', '2026-09-01 10:15:00'),
('b1eebc99-9c0b-4ef8-bb6d-6bb9bd380a22', 'Sofia', 'Bianchi', '+39 347 9876543', 'sofia.bianchi@example.com', '2026-09-05 14:22:10'),
('c2eebc99-9c0b-4ef8-bb6d-6bb9bd380a33', 'Luca', 'Ferrari', '+39 333 5551234', 'luca.ferrari@example.com', '2026-09-12 18:40:00'),
('d3eebc99-9c0b-4ef8-bb6d-6bb9bd380a44', 'Elena', 'Esposito', '+39 328 4448901', 'elena.esposito@example.com', '2026-09-18 09:10:45'),
('e4eebc99-9c0b-4ef8-bb6d-6bb9bd380a55', 'Alessandro', 'Ricci', '+39 349 7772345', 'alessandro.ricci@example.com', '2026-09-22 16:30:12'),
('f5eebc99-9c0b-4ef8-bb6d-6bb9bd380a66', 'Giulia', 'Marino', '+39 331 6663456', 'giulia.marino@example.com', '2026-10-01 11:05:00'),
('a6eebc99-9c0b-4ef8-bb6d-6bb9bd380a77', 'Matteo', 'Greco', '+39 345 8889012', 'matteo.greco@example.com', '2026-10-05 19:20:30'),
('b7eebc99-9c0b-4ef8-bb6d-6bb9bd380a88', 'Chiara', 'Conti', '+39 339 2227890', 'chiara.conti@example.com', '2026-10-08 12:45:00'),
('c8eebc99-9c0b-4ef8-bb6d-6bb9bd380a99', 'Davide', 'De Luca', '+39 348 3334567', 'davide.deluca@example.com', '2026-10-10 15:10:00'),
('d9eebc99-9c0b-4ef8-bb6d-6bb9bd380b00', 'Francesca', 'Mancini', '+39 320 1119876', 'francesca.mancini@example.com', '2026-10-14 20:00:00');

-- ----------------------------------------------------------------------------
-- 2. Tables (Indoor, Terrace, Bar, Private Room)
-- ----------------------------------------------------------------------------
INSERT INTO tables (table_id, name, seats_min, seats_max, area, active) VALUES
-- Indoor Tables
(1,  'T01', 1, 2, 'indoor', 1),
(2,  'T02', 1, 2, 'indoor', 1),
(3,  'T03', 2, 4, 'indoor', 1),
(4,  'T04', 3, 6, 'indoor', 1),
(5,  'T05', 3, 6, 'indoor', 1),
(6,  'T06', 2, 4, 'indoor', 1),
-- Terrace Tables
(7,  'TR01', 2, 4, 'terrace', 1),
(8,  'TR02', 2, 4, 'terrace', 1),
(9,  'TR03', 4, 6, 'terrace', 1),
(10, 'TR04', 4, 6, 'terrace', 1),
(11, 'TR05', 1, 2, 'terrace', 1),
-- Bar High Tops
(12, 'B01', 1, 2, 'bar', 1),
(13, 'B02', 1, 2, 'bar', 1),
(14, 'B03', 1, 2, 'bar', 1),
-- Private Dining Room
(15, 'P01', 8, 16, 'private_room', 1),
-- Inactive table for maintenance testing
(16, 'T99', 2, 4, 'indoor', 0);

-- ----------------------------------------------------------------------------
-- Combinable Tables (Symmetric Adjacencies)
-- ----------------------------------------------------------------------------
-- Indoor T01 & T02 can be joined (2+2 = up to 4 seats)
INSERT INTO table_combinations (table_id, combinable_with_table_id) VALUES
(1, 2),
(2, 1),
-- Indoor T04 & T05 can be joined (6+6 = up to 12 seats)
(4, 5),
(5, 4),
-- Terrace TR01 & TR02 can be joined (4+4 = up to 8 seats)
(7, 8),
(8, 7),
-- Terrace TR03 & TR04 can be joined (6+6 = up to 12 seats)
(9, 10),
(10, 9);

-- ----------------------------------------------------------------------------
-- 3. Opening Shifts (Lunch & Dinner for all 7 weekdays)
-- 0 = Monday, 1 = Tuesday, 2 = Wednesday, 3 = Thursday, 4 = Friday, 5 = Saturday, 6 = Sunday
-- ----------------------------------------------------------------------------
INSERT INTO opening_shifts (shift_id, shift_name, weekday, weekday_name, start_time, end_time, last_bookable_time) VALUES
-- Monday
(1,  'lunch',  0, 'Monday',    '12:00', '15:00', '14:00'),
(2,  'dinner', 0, 'Monday',    '19:00', '23:00', '21:30'),
-- Tuesday
(3,  'lunch',  1, 'Tuesday',   '12:00', '15:00', '14:00'),
(4,  'dinner', 1, 'Tuesday',   '19:00', '23:00', '21:30'),
-- Wednesday
(5,  'lunch',  2, 'Wednesday', '12:00', '15:00', '14:00'),
(6,  'dinner', 2, 'Wednesday', '19:00', '23:00', '21:30'),
-- Thursday
(7,  'lunch',  3, 'Thursday',  '12:00', '15:00', '14:00'),
(8,  'dinner', 3, 'Thursday',  '19:00', '23:30', '22:00'),
-- Friday
(9,  'lunch',  4, 'Friday',    '12:00', '15:00', '14:00'),
(10, 'dinner', 4, 'Friday',    '19:00', '23:59', '22:30'),
-- Saturday
(11, 'lunch',  5, 'Saturday',  '12:00', '15:30', '14:15'),
(12, 'dinner', 5, 'Saturday',  '19:00', '23:59', '22:30'),
-- Sunday
(13, 'lunch',  6, 'Sunday',    '12:00', '16:00', '14:30'),
(14, 'dinner', 6, 'Sunday',    '19:00', '23:00', '21:30');

-- ----------------------------------------------------------------------------
-- 4. Closures (Exceptions / Holidays / Events)
-- ----------------------------------------------------------------------------
INSERT INTO closures (closure_id, date, shift_id, reason) VALUES
(1, '2026-11-01', NULL, 'All Saints Day (Full Day Holiday)'),
(2, '2026-11-20', 10,   'Private Gala Dinner on Friday Night'),
(3, '2026-12-25', NULL, 'Christmas Day (Full Day Holiday)'),
(4, '2026-12-26', 1,    'St. Stephen Day Lunch (Kitchen Deep Cleaning)');

-- ----------------------------------------------------------------------------
-- 5. Dining Rules (Length of stay by party size)
-- ----------------------------------------------------------------------------
INSERT INTO dining_rules (rule_id, party_size_from, party_size_to, duration_minutes, description) VALUES
(1, 1,  2,   90,  'Solo diners and couples (1 hr 30 min)'),
(2, 3,  4,  105,  'Small groups and families (1 hr 45 min)'),
(3, 5,  6,  120,  'Standard medium groups (2 hr)'),
(4, 7,  10, 135,  'Large groups (2 hr 15 min)'),
(5, 11, 20, 180,  'Extra large groups & banquet events (3 hr)');

-- ----------------------------------------------------------------------------
-- 6. Bookings
-- Demonstrates all statuses (confirmed, arrived, pending, cancelled, no_show)
-- and all sources (chatbot, phone, staff, website)
-- End times strictly calculated based on dining_rules:
--   Party of 2 -> 90 min
--   Party of 4 -> 105 min
--   Party of 5/6 -> 120 min
--   Party of 8 -> 135 min
-- ----------------------------------------------------------------------------
INSERT INTO bookings (booking_id, customer_id, start_time, end_time, party_size, status, source, special_requests, created_at) VALUES
-- 1. Confirmed lunch for 2 (duration 90 min) via chatbot
('11111111-aaaa-4000-8000-000000000001', 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11',
 '2026-10-17 12:30:00', '2026-10-17 14:00:00', 2, 'confirmed', 'chatbot', 'Window seat preferred', '2026-10-16 18:20:00'),

-- 2. Arrived lunch for 4 (duration 105 min) via phone
('22222222-bbbb-4000-8000-000000000002', 'b1eebc99-9c0b-4ef8-bb6d-6bb9bd380a22',
 '2026-10-17 13:00:00', '2026-10-17 14:45:00', 4, 'arrived', 'phone', 'Highchair for toddler', '2026-10-17 09:30:00'),

-- 3. Confirmed dinner for 2 (duration 90 min) via chatbot
('33333333-cccc-4000-8000-000000000003', 'c2eebc99-9c0b-4ef8-bb6d-6bb9bd380a33',
 '2026-10-17 19:30:00', '2026-10-17 21:00:00', 2, 'confirmed', 'chatbot', 'Anniversary dinner', '2026-10-15 14:10:00'),

-- 4. Confirmed dinner for 8 (duration 135 min) via staff - Occupies joined tables T04 & T05
('44444444-dddd-4000-8000-000000000004', 'd3eebc99-9c0b-4ef8-bb6d-6bb9bd380a44',
 '2026-10-17 20:00:00', '2026-10-17 22:15:00', 8, 'confirmed', 'staff', 'Birthday celebration, will bring cake', '2026-10-14 11:00:00'),

-- 5. Pending dinner for 4 (duration 105 min) via chatbot
('55555555-eeee-4000-8000-000000000005', 'e4eebc99-9c0b-4ef8-bb6d-6bb9bd380a55',
 '2026-10-17 21:00:00', '2026-10-17 22:45:00', 4, 'pending', 'chatbot', 'Gluten allergy for one guest', '2026-10-17 11:15:00'),

-- 6. Cancelled booking for 2 via phone
('66666666-ffff-4000-8000-000000000006', 'f5eebc99-9c0b-4ef8-bb6d-6bb9bd380a66',
 '2026-10-17 19:00:00', '2026-10-17 20:30:00', 2, 'cancelled', 'phone', 'Client called to reschedule', '2026-10-16 10:00:00'),

-- 7. No-show booking for 2 from yesterday via chatbot
('77777777-aaaa-4000-8000-000000000007', 'a6eebc99-9c0b-4ef8-bb6d-6bb9bd380a77',
 '2026-10-16 20:30:00', '2026-10-16 22:00:00', 2, 'no_show', 'chatbot', NULL, '2026-10-16 15:45:00'),

-- 8. Confirmed Sunday lunch for 6 (duration 120 min) via website - Terrace
('88888888-bbbb-4000-8000-000000000008', 'b7eebc99-9c0b-4ef8-bb6d-6bb9bd380a88',
 '2026-10-18 13:00:00', '2026-10-18 15:00:00', 6, 'confirmed', 'website', 'Terrace table requested', '2026-10-16 19:40:00'),

-- 9. Confirmed private room banquet for 12 (duration 180 min) via staff
('99999999-cccc-4000-8000-000000000009', 'c8eebc99-9c0b-4ef8-bb6d-6bb9bd380a99',
 '2026-10-18 19:30:00', '2026-10-18 22:30:00', 12, 'confirmed', 'staff', 'Set tasting menu + wine pairing', '2026-10-10 16:00:00'),

-- 10. Solo diner at the bar (duration 90 min) via walk-in / staff
('aaaaaaaa-dddd-4000-8000-000000000010', 'd9eebc99-9c0b-4ef8-bb6d-6bb9bd380b00',
 '2026-10-18 20:00:00', '2026-10-18 21:30:00', 1, 'confirmed', 'staff', 'Bar seating', '2026-10-18 19:55:00');

-- ----------------------------------------------------------------------------
-- 7. Booking Tables Mapping
-- Demonstrates single table assignments and multi-table joined assignments
-- ----------------------------------------------------------------------------
INSERT INTO booking_tables (booking_id, table_id) VALUES
-- Booking 1 -> Table T01 (Indoor 2-seater)
('11111111-aaaa-4000-8000-000000000001', 1),

-- Booking 2 -> Table T03 (Indoor 4-seater)
('22222222-bbbb-4000-8000-000000000002', 3),

-- Booking 3 -> Table T02 (Indoor 2-seater)
('33333333-cccc-4000-8000-000000000003', 2),

-- Booking 4 -> Party of 8 occupies joined tables T04 (Table 4) and T05 (Table 5)
('44444444-dddd-4000-8000-000000000004', 4),
('44444444-dddd-4000-8000-000000000004', 5),

-- Booking 5 -> Table T06 (Indoor 4-seater)
('55555555-eeee-4000-8000-000000000005', 6),

-- Booking 6 -> Was assigned to T01 (cancelled)
('66666666-ffff-4000-8000-000000000006', 1),

-- Booking 7 -> Table T02 (no show)
('77777777-aaaa-4000-8000-000000000007', 2),

-- Booking 8 -> Table TR03 (Terrace 6-seater)
('88888888-bbbb-4000-8000-000000000008', 9),

-- Booking 9 -> Table P01 (Private Room up to 16 seats)
('99999999-cccc-4000-8000-000000000009', 15),

-- Booking 10 -> Table B01 (Bar high-top)
('aaaaaaaa-dddd-4000-8000-000000000010', 12);
