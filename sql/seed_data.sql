-- ============================================================================
-- Restaurant Reservation System - Seed Data (PostgreSQL)
-- ============================================================================

-- Clean existing data for idempotency (respecting dependencies)
TRUNCATE TABLE 
    booking_tables,
    bookings,
    table_combinations,
    tables,
    closures,
    opening_shifts,
    dining_rules,
    customers,
    menu_items,
    menu_categories
RESTART IDENTITY CASCADE;

-- ----------------------------------------------------------------------------
-- 1. Customers (10 Sample Customers with UUIDs)
-- ----------------------------------------------------------------------------
INSERT INTO customers (customer_id, name, surname, phone, email, created_at) VALUES
('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 'Marco', 'Rossi', '+39 340 1234567', 'marco.rossi@example.com', '2026-09-01 10:15:00+02'),
('b1eebc99-9c0b-4ef8-bb6d-6bb9bd380a22', 'Sofia', 'Bianchi', '+39 347 9876543', 'sofia.bianchi@example.com', '2026-09-05 14:22:10+02'),
('c2eebc99-9c0b-4ef8-bb6d-6bb9bd380a33', 'Luca', 'Ferrari', '+39 333 5551234', 'luca.ferrari@example.com', '2026-09-12 18:40:00+02'),
('d3eebc99-9c0b-4ef8-bb6d-6bb9bd380a44', 'Elena', 'Esposito', '+39 328 4448901', 'elena.esposito@example.com', '2026-09-18 09:10:45+02'),
('e4eebc99-9c0b-4ef8-bb6d-6bb9bd380a55', 'Alessandro', 'Ricci', '+39 349 7772345', 'alessandro.ricci@example.com', '2026-09-22 16:30:12+02'),
('f5eebc99-9c0b-4ef8-bb6d-6bb9bd380a66', 'Giulia', 'Marino', '+39 331 6663456', 'giulia.marino@example.com', '2026-10-01 11:05:00+02'),
('a6eebc99-9c0b-4ef8-bb6d-6bb9bd380a77', 'Matteo', 'Greco', '+39 345 8889012', 'matteo.greco@example.com', '2026-10-05 19:20:30+02'),
('b7eebc99-9c0b-4ef8-bb6d-6bb9bd380a88', 'Chiara', 'Conti', '+39 339 2227890', 'chiara.conti@example.com', '2026-10-08 12:45:00+02'),
('c8eebc99-9c0b-4ef8-bb6d-6bb9bd380a99', 'Davide', 'De Luca', '+39 348 3334567', 'davide.deluca@example.com', '2026-10-10 15:10:00+02'),
('d9eebc99-9c0b-4ef8-bb6d-6bb9bd380b00', 'Francesca', 'Mancini', '+39 320 1119876', 'francesca.mancini@example.com', '2026-10-14 20:00:00+02');

-- ----------------------------------------------------------------------------
-- 2. Tables (Indoor, Terrace, Bar, Private Room)
-- ----------------------------------------------------------------------------
INSERT INTO tables (table_id, name, seats_min, seats_max, area, active) VALUES
-- Indoor Tables
(1,  'T01', 1, 2, 'indoor', TRUE),
(2,  'T02', 1, 2, 'indoor', TRUE),
(3,  'T03', 2, 4, 'indoor', TRUE),
(4,  'T04', 3, 6, 'indoor', TRUE),
(5,  'T05', 3, 6, 'indoor', TRUE),
(6,  'T06', 2, 4, 'indoor', TRUE),
-- Terrace Tables
(7,  'TR01', 2, 4, 'terrace', TRUE),
(8,  'TR02', 2, 4, 'terrace', TRUE),
(9,  'TR03', 4, 6, 'terrace', TRUE),
(10, 'TR04', 4, 6, 'terrace', TRUE),
(11, 'TR05', 1, 2, 'terrace', TRUE),
-- Bar High Tops
(12, 'B01', 1, 2, 'bar', TRUE),
(13, 'B02', 1, 2, 'bar', TRUE),
(14, 'B03', 1, 2, 'bar', TRUE),
-- Private Dining Room
(15, 'P01', 8, 16, 'private_room', TRUE),
-- Inactive table for maintenance testing
(16, 'T99', 2, 4, 'indoor', FALSE);

-- Sync serial sequence for tables
SELECT setval(pg_get_serial_sequence('tables', 'table_id'), COALESCE(MAX(table_id), 1)) FROM tables;

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
(1,  'lunch',  0, 'Monday',    '12:00:00', '15:00:00', '14:00:00'),
(2,  'dinner', 0, 'Monday',    '19:00:00', '23:00:00', '21:30:00'),
-- Tuesday
(3,  'lunch',  1, 'Tuesday',   '12:00:00', '15:00:00', '14:00:00'),
(4,  'dinner', 1, 'Tuesday',   '19:00:00', '23:00:00', '21:30:00'),
-- Wednesday
(5,  'lunch',  2, 'Wednesday', '12:00:00', '15:00:00', '14:00:00'),
(6,  'dinner', 2, 'Wednesday', '19:00:00', '23:00:00', '21:30:00'),
-- Thursday
(7,  'lunch',  3, 'Thursday',  '12:00:00', '15:00:00', '14:00:00'),
(8,  'dinner', 3, 'Thursday',  '19:00:00', '23:30:00', '22:00:00'),
-- Friday
(9,  'lunch',  4, 'Friday',    '12:00:00', '15:00:00', '14:00:00'),
(10, 'dinner', 4, 'Friday',    '19:00:00', '23:59:00', '22:30:00'),
-- Saturday
(11, 'lunch',  5, 'Saturday',  '12:00:00', '15:30:00', '14:15:00'),
(12, 'dinner', 5, 'Saturday',  '19:00:00', '23:59:00', '22:30:00'),
-- Sunday
(13, 'lunch',  6, 'Sunday',    '12:00:00', '16:00:00', '14:30:00'),
(14, 'dinner', 6, 'Sunday',    '19:00:00', '23:00:00', '21:30:00');

-- Sync serial sequence for opening_shifts
SELECT setval(pg_get_serial_sequence('opening_shifts', 'shift_id'), COALESCE(MAX(shift_id), 1)) FROM opening_shifts;

-- ----------------------------------------------------------------------------
-- 4. Closures (Exceptions / Holidays / Events)
-- ----------------------------------------------------------------------------
INSERT INTO closures (closure_id, date, shift_id, reason) VALUES
(1, '2026-11-01', NULL, 'All Saints Day (Full Day Holiday)'),
(2, '2026-11-20', 10,   'Private Gala Dinner on Friday Night'),
(3, '2026-12-25', NULL, 'Christmas Day (Full Day Holiday)'),
(4, '2026-12-26', 1,    'St. Stephen Day Lunch (Kitchen Deep Cleaning)');

-- Sync serial sequence for closures
SELECT setval(pg_get_serial_sequence('closures', 'closure_id'), COALESCE(MAX(closure_id), 1)) FROM closures;

-- ----------------------------------------------------------------------------
-- 5. Dining Rules (Length of stay by party size)
-- ----------------------------------------------------------------------------
INSERT INTO dining_rules (rule_id, party_size_from, party_size_to, duration_minutes, description) VALUES
(1, 1,  2,   90,  'Solo diners and couples (1 hr 30 min)'),
(2, 3,  4,  105,  'Small groups and families (1 hr 45 min)'),
(3, 5,  6,  120,  'Standard medium groups (2 hr)'),
(4, 7,  10, 135,  'Large groups (2 hr 15 min)'),
(5, 11, 20, 180,  'Extra large groups & banquet events (3 hr)');

-- Sync serial sequence for dining_rules
SELECT setval(pg_get_serial_sequence('dining_rules', 'rule_id'), COALESCE(MAX(rule_id), 1)) FROM dining_rules;

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
 '2026-10-17 12:30:00+02', '2026-10-17 14:00:00+02', 2, 'confirmed', 'chatbot', 'Window seat preferred', '2026-10-16 18:20:00+02'),

-- 2. Arrived lunch for 4 (duration 105 min) via phone
('22222222-bbbb-4000-8000-000000000002', 'b1eebc99-9c0b-4ef8-bb6d-6bb9bd380a22',
 '2026-10-17 13:00:00+02', '2026-10-17 14:45:00+02', 4, 'arrived', 'phone', 'Highchair for toddler', '2026-10-17 09:30:00+02'),

-- 3. Confirmed dinner for 2 (duration 90 min) via chatbot
('33333333-cccc-4000-8000-000000000003', 'c2eebc99-9c0b-4ef8-bb6d-6bb9bd380a33',
 '2026-10-17 19:30:00+02', '2026-10-17 21:00:00+02', 2, 'confirmed', 'chatbot', 'Anniversary dinner', '2026-10-15 14:10:00+02'),

-- 4. Confirmed dinner for 8 (duration 135 min) via staff - Occupies joined tables T04 & T05
('44444444-dddd-4000-8000-000000000004', 'd3eebc99-9c0b-4ef8-bb6d-6bb9bd380a44',
 '2026-10-17 20:00:00+02', '2026-10-17 22:15:00+02', 8, 'confirmed', 'staff', 'Birthday celebration, will bring cake', '2026-10-14 11:00:00+02'),

-- 5. Pending dinner for 4 (duration 105 min) via chatbot
('55555555-eeee-4000-8000-000000000005', 'e4eebc99-9c0b-4ef8-bb6d-6bb9bd380a55',
 '2026-10-17 21:00:00+02', '2026-10-17 22:45:00+02', 4, 'pending', 'chatbot', 'Gluten allergy for one guest', '2026-10-17 11:15:00+02'),

-- 6. Cancelled booking for 2 via phone
('66666666-ffff-4000-8000-000000000006', 'f5eebc99-9c0b-4ef8-bb6d-6bb9bd380a66',
 '2026-10-17 19:00:00+02', '2026-10-17 20:30:00+02', 2, 'cancelled', 'phone', 'Client called to reschedule', '2026-10-16 10:00:00+02'),

-- 7. No-show booking for 2 from yesterday via chatbot
('77777777-aaaa-4000-8000-000000000007', 'a6eebc99-9c0b-4ef8-bb6d-6bb9bd380a77',
 '2026-10-16 20:30:00+02', '2026-10-16 22:00:00+02', 2, 'no_show', 'chatbot', NULL, '2026-10-16 15:45:00+02'),

-- 8. Confirmed Sunday lunch for 6 (duration 120 min) via website - Terrace
('88888888-bbbb-4000-8000-000000000008', 'b7eebc99-9c0b-4ef8-bb6d-6bb9bd380a88',
 '2026-10-18 13:00:00+02', '2026-10-18 15:00:00+02', 6, 'confirmed', 'website', 'Terrace table requested', '2026-10-16 19:40:00+02'),

-- 9. Confirmed private room banquet for 12 (duration 180 min) via staff
('99999999-cccc-4000-8000-000000000009', 'c8eebc99-9c0b-4ef8-bb6d-6bb9bd380a99',
 '2026-10-18 19:30:00+02', '2026-10-18 22:30:00+02', 12, 'confirmed', 'staff', 'Set tasting menu + wine pairing', '2026-10-10 16:00:00+02'),

-- 10. Solo diner at the bar (duration 90 min) via walk-in / staff
('aaaaaaaa-dddd-4000-8000-000000000010', 'd9eebc99-9c0b-4ef8-bb6d-6bb9bd380b00',
 '2026-10-18 20:00:00+02', '2026-10-18 21:30:00+02', 1, 'confirmed', 'staff', 'Bar seating', '2026-10-18 19:55:00+02');

-- ----------------------------------------------------------------------------
-- 7. Booking Tables Mapping
-- ----------------------------------------------------------------------------
INSERT INTO booking_tables (booking_id, table_id) VALUES
-- Booking 1 -> Table T01 (Indoor 2-seater)
('11111111-aaaa-4000-8000-000000000001', 1),

-- Booking 2 -> Table T03 (Indoor 4-seater)
('22222222-bbbb-4000-8000-000000000002', 3),

-- Booking 3 -> Table T02 (Indoor 2-seater)
('33333333-cccc-4000-8000-000000000003', 2),

-- Booking 4 -> Party of 8 occupies joined tables T04 and T05
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

-- ----------------------------------------------------------------------------
-- 8. Menu Categories (American Cuisine)
-- ----------------------------------------------------------------------------
INSERT INTO menu_categories (category_id, name, description, display_order) VALUES
(1, 'Appetizers & Starters', 'Crispy wings, loaded skins, and hearty starters to kick off your feast.', 1),
(2, 'Handcrafted Burgers', 'Prime Angus beef and plant-based burgers smashed or flame-grilled on brioche.', 2),
(3, 'Sandwiches & Subs', 'Iconic regional American sandwiches piled high with slow-cooked meats and cheeses.', 3),
(4, 'Texas & Southern BBQ', 'Low-and-slow hardwood smoked meats served with authentic regional glazes and rubs.', 4),
(5, 'Steaks & Prime Cuts', 'Hand-cut USDA Prime steaks charbroiled to order and basted with garlic herb butter.', 5),
(6, 'Classic Sides', 'Southern-style comfort sides, seasoned fries, and gourmet skillet sides.', 6),
(7, 'Handcrafted Desserts', 'Decadent American bakery classics, freshly baked pies, and warm skillet treats.', 7),
(8, 'Beverages & Hand-Spun Shakes', 'Thick hand-spun milkshakes, craft root beer floats, and refreshing iced teas.', 8);

-- Sync serial sequence for menu_categories
SELECT setval(pg_get_serial_sequence('menu_categories', 'category_id'), COALESCE(MAX(category_id), 1)) FROM menu_categories;

-- ----------------------------------------------------------------------------
-- 9. Menu Items (Authentic American Dishes)
-- ----------------------------------------------------------------------------
INSERT INTO menu_items (
    item_id, category_id, name, description, price, is_available, calories, 
    spicy_level, is_vegetarian, is_vegan, is_gluten_free, allergens
) VALUES
-- 1. Appetizers & Starters
(1, 1, 'Buffalo Chicken Wings', 'Crispy jumbo wings tossed in Frank''s authentic cayenne buffalo sauce, served with crisp celery and blue cheese dip.', 14.99, TRUE, 820, 2, FALSE, FALSE, TRUE, 'Dairy, Celery'),
(2, 1, 'Loaded Potato Skins', 'Crispy russet potato boats stuffed with melted Wisconsin cheddar, applewood smoked bacon, scallions, and sour cream.', 11.99, TRUE, 650, 0, FALSE, FALSE, TRUE, 'Dairy, Pork'),
(3, 1, 'Maryland Jumbo Lump Crab Cakes', 'Pan-seared jumbo lump blue crab cakes seasoned with Old Bay spice, served with house remoulade and lemon.', 18.99, TRUE, 520, 0, FALSE, FALSE, FALSE, 'Shellfish, Eggs, Gluten'),
(4, 1, 'Crispy Golden Mozzarella Sticks', 'Beer-battered Wisconsin whole milk mozzarella sticks fried golden, served with warm house marinara.', 10.50, TRUE, 580, 0, TRUE, FALSE, FALSE, 'Dairy, Gluten'),
(5, 1, 'New England Clam Chowder', 'Traditional creamy Boston chowder with tender sea clams, Yukon potatoes, celery, and smoky bacon lardons.', 9.50, TRUE, 440, 0, FALSE, FALSE, FALSE, 'Shellfish, Dairy, Gluten'),
(6, 1, 'Southern Fried Green Tomatoes', 'Heirloom green tomatoes crusted in seasoned cornmeal, topped with pimento cheese and candied bacon relish.', 11.50, TRUE, 480, 0, TRUE, FALSE, FALSE, 'Dairy, Gluten'),

-- 2. Handcrafted Burgers
(7, 2, 'The Classic American Cheeseburger', 'Half-pound certified Angus beef patty, double melted American cheese, crisp lettuce, tomato, pickles, and secret sauce on brioche.', 16.50, TRUE, 890, 0, FALSE, FALSE, FALSE, 'Dairy, Gluten, Eggs'),
(8, 2, 'Smokehouse Bacon BBQ Burger', 'Half-pound Angus beef, thick applewood bacon, smoked cheddar, crispy beer-battered onion ring, and sweet Kansas City BBQ sauce.', 18.50, TRUE, 1050, 0, FALSE, FALSE, FALSE, 'Dairy, Gluten'),
(9, 2, 'Oklahoma Onion Smash Burger', 'Twin seared smashed beef patties pressed with shaved sweet Vidalia onions, American cheese, and yellow mustard aioli on a potato roll.', 15.99, TRUE, 780, 0, FALSE, FALSE, FALSE, 'Dairy, Gluten, Eggs'),
(10, 2, 'Beyond Meat Plant Smash Burger', 'Plant-based patty with dairy-free vegan cheddar, avocado mash, baby arugula, vine tomato, and vegan garlic herb aioli on a toasted bun.', 17.50, TRUE, 680, 0, TRUE, TRUE, FALSE, 'Gluten'),

-- 3. Sandwiches & Subs
(11, 3, 'Authentic Philly Cheesesteak', 'Thinly sliced grilled ribeye, sautéed sweet onions, bell peppers, and melted provolone on a warm toasted Amoroso roll.', 17.50, TRUE, 840, 0, FALSE, FALSE, FALSE, 'Dairy, Gluten'),
(12, 3, 'Nashville Hot Fried Chicken Sandwich', 'Buttermilk fried chicken breast drenched in fiery cayenne pepper oil, topped with creamy slaw and pickles on a brioche bun.', 16.99, TRUE, 880, 2, FALSE, FALSE, FALSE, 'Dairy, Gluten, Eggs'),
(13, 3, 'NYC Pastrami on Rye', 'Warm, slow-cured black pepper pastrami piled high on Jewish rye bread with spicy deli brown mustard and a kosher pickle.', 19.50, TRUE, 790, 0, FALSE, FALSE, FALSE, 'Gluten, Mustard'),
(14, 3, 'Hickory Pulled Pork Sandwich', 'Twelve-hour smoked pulled pork shoulder, tangy Carolina gold mustard BBQ sauce, and crunchy coleslaw on a sesame seed bun.', 15.50, TRUE, 720, 0, FALSE, FALSE, FALSE, 'Gluten, Mustard'),

-- 4. Texas & Southern BBQ
(15, 4, 'St. Louis Smoked Baby Back Ribs', 'Full rack of tender pork ribs slow-smoked over hickory wood, glazed with tangy sweet BBQ sauce, served with warm skillet cornbread.', 27.99, TRUE, 1150, 0, FALSE, FALSE, FALSE, 'Dairy, Gluten'),
(16, 4, 'Texas Oak-Smoked Beef Brisket', 'USDA Prime beef brisket smoked 14 hours over Texas post oak, sliced thick with peppery bark, pickled jalapeños, and pit mop sauce.', 28.99, TRUE, 980, 1, FALSE, FALSE, TRUE, 'None'),
(17, 4, 'Southern Buttermilk Fried Chicken Platter', 'Three pieces of crispy golden fried chicken soaked in herb buttermilk brine, served with a hot honey butter biscuit and gravy.', 22.50, TRUE, 1020, 0, FALSE, FALSE, FALSE, 'Dairy, Gluten'),

-- 5. Steaks & Prime Cuts
(18, 5, 'USDA Prime Ribeye Steak (14 oz)', 'Heavily marbled hand-cut prime ribeye flame-grilled over open coals, topped with roasted garlic-herb butter and sea salt.', 39.99, TRUE, 1100, 0, FALSE, FALSE, TRUE, 'Dairy'),
(19, 5, 'Center-Cut Filet Mignon (8 oz)', 'Tender oak-grilled center-cut beef tenderloin, served with Cabernet Sauvignon reduction demi-glace and grilled asparagus.', 42.99, TRUE, 760, 0, FALSE, FALSE, TRUE, 'Dairy'),
(20, 5, 'Kansas City Bone-In Strip (12 oz)', 'Dry-aged bone-in New York strip steak seasoned with coarse sea salt and black peppercorns, charbroiled to temperature.', 36.99, TRUE, 920, 0, FALSE, FALSE, TRUE, 'Dairy'),

-- 6. Classic Sides
(21, 6, 'Signature Garlic & Herb Fries', 'Crisp hand-cut Idaho russet potatoes tossed in sea salt, roasted garlic oil, and fresh chopped parsley.', 6.50, TRUE, 380, 0, TRUE, TRUE, TRUE, 'None'),
(22, 6, 'Four-Cheese Truffle Mac & Cheese', 'Cavatappi pasta baked in sharp cheddar, gruyère, fontina, and parmesan Mornay sauce, infused with black truffle oil.', 9.50, TRUE, 620, 0, TRUE, FALSE, FALSE, 'Dairy, Gluten'),
(23, 6, 'Crispy Sweet Potato Fries', 'Crinkle-cut sweet potatoes fried crisp, served with house honey-cinnamon whipped dipping butter.', 7.50, TRUE, 410, 0, TRUE, FALSE, TRUE, 'Dairy'),
(24, 6, 'Cast-Iron Skillet Cornbread', 'Sweet golden yellow cornbread baked fresh in cast iron, served warm with whipped wildflower honey butter.', 6.50, TRUE, 390, 0, TRUE, FALSE, FALSE, 'Dairy, Gluten, Eggs'),
(25, 6, 'Craft Beer-Battered Onion Rings', 'Jumbo sweet Vidalia onion rings soaked in craft IPA batter and fried golden crisp, served with chipotle ranch.', 7.99, TRUE, 460, 0, TRUE, FALSE, FALSE, 'Dairy, Gluten, Eggs'),
(26, 6, 'Creamy Southern Buttermilk Coleslaw', 'Finely shredded crisp green cabbage and carrots tossed in sweet and tangy buttermilk poppyseed dressing.', 5.00, TRUE, 210, 0, TRUE, FALSE, TRUE, 'Dairy, Eggs'),

-- 7. Handcrafted Desserts
(27, 7, 'New York Style Cheesecake', 'Tall, rich, and velvety dense cream cheese cake on a graham cracker crust, drizzled with homemade strawberry compote.', 9.50, TRUE, 680, 0, TRUE, FALSE, FALSE, 'Dairy, Gluten, Eggs'),
(28, 7, 'Warm Honeycrisp Apple Pie à la Mode', 'Spiced Honeycrisp apple slices baked in flaky butter double crust, served warm with Madagascar vanilla bean ice cream.', 8.99, TRUE, 590, 0, TRUE, FALSE, FALSE, 'Dairy, Gluten, Eggs'),
(29, 7, 'Skillet Double Chocolate Fudge Brownie', 'Warm chocolate fudge brownie baked to order in a mini skillet, topped with vanilla ice cream, hot fudge drizzle, and toasted pecans.', 9.99, TRUE, 740, 0, TRUE, FALSE, FALSE, 'Dairy, Gluten, Eggs, Tree Nuts'),
(30, 7, 'Florida Key Lime Pie', 'Tangy and creamy custard made with authentic Key lime juice in a buttery graham crust, topped with freshly whipped chantilly cream.', 8.50, TRUE, 510, 0, TRUE, FALSE, FALSE, 'Dairy, Gluten, Eggs'),

-- 8. Beverages & Hand-Spun Shakes
(31, 8, 'Hand-Spun Madagascar Vanilla Shake', 'Premium vanilla bean ice cream spun thick with cold whole milk, crowned with whipped cream and a Luxardo cherry.', 7.00, TRUE, 520, 0, TRUE, FALSE, TRUE, 'Dairy'),
(32, 8, 'Oreo Cookies & Cream Milkshake', 'Creamy vanilla ice cream blended with crushed chocolate Oreo cookies, Hershey''s syrup drizzle, and whipped cream.', 7.50, TRUE, 640, 0, TRUE, FALSE, FALSE, 'Dairy, Gluten'),
(33, 8, 'Southern Sweet Brewed Iced Tea', 'Slow-brewed Orange Pekoe black tea sweetened southern-style with pure cane sugar and fresh lemon slices.', 4.00, TRUE, 120, 0, TRUE, TRUE, TRUE, 'None'),
(34, 8, 'Fresh-Squeezed Lemonade', 'Hand-squeezed Meyer lemons with pure cane sugar and spring water served over crushed ice with mint.', 4.50, TRUE, 140, 0, TRUE, TRUE, TRUE, 'None'),
(35, 8, 'Draft Craft Root Beer Float', 'Old-fashioned draft sarsaparilla root beer poured over two large scoops of velvety vanilla bean ice cream.', 6.50, TRUE, 360, 0, TRUE, FALSE, TRUE, 'Dairy');

-- Sync serial sequence for menu_items
SELECT setval(pg_get_serial_sequence('menu_items', 'item_id'), COALESCE(MAX(item_id), 1)) FROM menu_items;

