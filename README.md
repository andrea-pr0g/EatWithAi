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
├── chatbot_tools.py     # AI Chatbot tool functions & LLM function calling schemas
├── security.py          # Input sanitization and prompt injection guardrails
├── gemini_chatbot.py    # Hardened Gemini AI reservation agent & interactive CLI
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

---

## 🤖 Chatbot Tools (`chatbot_tools.py`)

A set of specialized functions ready for conversational AI agents (OpenAI function calling, Anthropic tool use, LangChain, or custom bots):

| Function | Purpose |
| :--- | :--- |
| **`check_restaurant_status(date_str, time_str)`** | Evaluates if the restaurant is open, closed for holiday, outside shift hours, or past last bookable cutoff. |
| **`check_table_availability(date_str, time_str, party_size, area=None)`** | Determines if single or joined combinable tables are available and computes exact stay duration. |
| **`find_available_slots(date_str, party_size, preferred_time=None)`** | Searches for open time slots throughout the day if requested time is taken. |
| **`get_restaurant_schedule(date_str=None)`** | Returns weekly hours and holiday closures (or schedule for a specific date). |
| **`get_dining_duration_for_party(party_size)`** | Looks up allowed stay duration based on party size. |
| **`create_booking_reservation(...)`** | End-to-end booking tool that creates the customer and assigns the best table. |
| **`cancel_booking_reservation(booking_id, phone_or_email)`** | Verifies ownership and cancels a booking. |
| **`get_booking_info(booking_id)`** | Retrieves details of an existing reservation. |

Includes pre-built OpenAI-compatible tool definitions in **`CHATBOT_TOOL_DEFINITIONS`**.

---

## 🛡️ Gemini AI Chatbot & Security Guardrails (`gemini_chatbot.py`)

A fully-featured conversational AI reservation host powered by **Google Gemini** (`gemini-2.5-flash` / `gemini-2.0-flash`), engineered with defense-in-depth protection against prompt injection, jailbreaking, and data leakage.

### Security Layers:
1. **Deterministic Injection Pre-Filter (`security.py`)**:
   Regex pattern analysis detects and immediately blocks direct instruction overrides (`"ignore instructions"`), jailbreak roleplay (`"DAN"`, `"developer mode"`), system prompt leakage probes (`"print your system prompt"`), and SQL injection attempts before any API calls are made.
2. **Structural Boundary Delimitation**:
   User input is wrapped inside `<untrusted_customer_message>...</untrusted_customer_message>` boundary tags, training the model to treat content strictly as untrusted customer data.
3. **Mandatory Confirmation Barrier**:
   The bot is strictly prohibited by system rules from invoking `create_booking_reservation` without first presenting a full summary and receiving explicit user confirmation.
4. **Input Sanitization & Length Limits**:
   Normalizes whitespace, removes non-printable control characters, and caps message lengths at 600 characters to prevent buffer overflow/token flood attacks.

### Running the Gemini Chatbot:
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Add your Gemini API key in .env
# GEMINI_API_KEY=AIzaSy...

# 3. Launch interactive chat in terminal
python3 gemini_chatbot.py
```



