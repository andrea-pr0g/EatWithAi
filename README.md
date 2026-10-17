# Restaurant Reservation System - PostgreSQL & Python (`psycopg2`)

A complete, production-grade PostgreSQL relational database schema and Python integration layer using `psycopg2` for a restaurant reservation system.

---

## 📁 Project Structure

```text
Restaurant/
├── .env                 # (Ignored by git) Put your PostgreSQL credentials here
├── .env.example         # Template for environment variables
├── .gitignore           # Ignores .env, __pycache__, and temporary files
├── requirements.txt     # Python dependencies (psycopg2-binary, python-dotenv)
├── config.py            # Loads credentials from .env with fallback parser
├── schema.sql           # PostgreSQL DDL (UUIDs, SERIAL, constraints, triggers, views)
├── seed_data.sql        # Realistic sample dataset
├── database.py          # PostgreSQL connection manager & query helpers via psycopg2
├── models.py            # Python dataclasses representing entities
├── init_db.py           # CLI runner to initialize, seed, and verify the database
└── README.md            # Documentation and instructions
```

---

## 🔐 Where to Put PostgreSQL Credentials

Put your PostgreSQL connection credentials in the [**`.env`**](file:///Users/andrealavalle/Documents/Restaurant/.env) file located in the root of the project:

```env
# PostgreSQL Database Credentials
DB_HOST=localhost
DB_PORT=5432
DB_NAME=restaurant_db
DB_USER=postgres
DB_PASSWORD=your_actual_password_here
DB_SSLMODE=prefer
```

> [!NOTE]
> `.env` is automatically excluded from git in `.gitignore` to prevent leaking passwords.
> A template file [`.env.example`](file:///Users/andrealavalle/Documents/Restaurant/.env.example) is committed to git for reference.

---

## 🚀 Setup & Installation

### 1. Install Python Dependencies
Install `psycopg2-binary` and `python-dotenv`:
```bash
pip install -r requirements.txt
```

### 2. Create the Database in PostgreSQL
Ensure PostgreSQL is running, then create the database (if it doesn't already exist):
```bash
# Using CLI
createdb restaurant_db

# Or using psql
psql -U postgres -c "CREATE DATABASE restaurant_db;"
```

### 3. Initialize and Seed the Database
Run the initialization script:
```bash
python3 init_db.py
```
This will:
- Connect to PostgreSQL using your `.env` credentials
- Run `schema.sql` (creating extensions, tables, constraints, indexes, triggers, and views)
- Run `seed_data.sql` (populating sample records and synchronizing ID sequences)
- Print a summary verification of all tables, views, and reservation logic

---

## 🗄️ PostgreSQL Schema Details

| Table | Primary Key | Key Columns & Notes |
| :--- | :--- | :--- |
| **`customers`** | `UUID` (`gen_random_uuid()`) | `name`, `surname`, `phone`, `email` (UNIQUE), `created_at` (TIMESTAMPTZ) |
| **`tables`** | `SERIAL` (`table_id`) | `name` (`VARCHAR(20)` UNIQUE), `seats_min`, `seats_max`, `area` (`indoor`, `terrace`, `bar`, `private_room`), `active` (BOOLEAN) |
| **`table_combinations`** | `(table_id, combinable_with_table_id)` | Junction table for adjacent tables that can be joined for large groups (e.g. T01 + T02, T04 + T05) |
| **`opening_shifts`** | `SERIAL` (`shift_id`) | `shift_name`, `weekday` (0=Monday...6=Sunday), `weekday_name`, `start_time` (TIME), `end_time` (TIME), `last_bookable_time` (TIME) |
| **`closures`** | `SERIAL` (`closure_id`) | `date` (DATE), `shift_id` (NULL = full day closure), `reason` |
| **`dining_rules`** | `SERIAL` (`rule_id`) | `party_size_from`, `party_size_to`, `duration_minutes`, `description` |
| **`bookings`** | `UUID` (`gen_random_uuid()`) | `customer_id` (UUID FK), `start_time`, `end_time` (TIMESTAMPTZ), `party_size`, `status` (`pending`, `confirmed`, `cancelled`, `arrived`, `no_show`), `source` (`chatbot`, `phone`, `staff`, `website`), `updated_at` (auto-updated by trigger) |
| **`booking_tables`** | `(booking_id, table_id)` | Maps reservations to one or multiple tables |

### PostgreSQL Views
* **`v_tables_with_combinations`**: Shows each table along with an aggregated `combinable_with` column built with `STRING_AGG`.
* **`v_booking_details`**: Joined report of bookings with customer contact details, assigned tables, stay duration in minutes (`EXTRACT(EPOCH FROM ...)`), and capacity.

---

## 💻 Python Usage Example

```python
from database import get_connection, create_booking, get_available_tables
from datetime import datetime

with get_connection() as conn:
    # 1. Check table availability for an upcoming slot
    start = datetime(2026, 10, 20, 19, 30)
    end = datetime(2026, 10, 20, 21, 15)
    tables = get_available_tables(conn, start, end, area="indoor")
    print("Available tables:", [t["name"] for t in tables])

    # 2. Book a table (duration automatically calculated from dining_rules)
    customer_id = "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11"
    booking_id = create_booking(
        conn=conn,
        customer_id=customer_id,
        start_time=start,
        party_size=4,
        table_ids=[3],
        source="chatbot",
        special_requests="Quiet table requested"
    )
    print("Booking confirmed with UUID:", booking_id)
```
