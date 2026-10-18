# EatWithAi - AI Restaurant Reservation Platform

A complete, production-grade restaurant reservation system featuring a PostgreSQL relational database schema, Python data integration layer (`psycopg2`), and a conversational AI reservation host powered by **Google Gemini** with defense-in-depth prompt injection guardrails.

---

## 📁 Project Structure

The project follows a standard, modular Python repository layout:

```text
EatWithAi/
├── .env.example             # Template for database & Gemini credentials
├── .gitignore               # Excludes caches, local env, and temp files
├── pyproject.toml           # PEP 518/621 package metadata & CLI entry points
├── requirements.txt         # Pinned / flexible project dependencies
├── README.md                # Platform documentation & operational guide
│
├── sql/                     # PostgreSQL database scripts
│   ├── schema.sql           # DDL: tables, UUIDs, constraints, triggers, views
│   └── seed_data.sql        # Realistic sample data & sequence alignments
│
├── scripts/                 # Standalone operational CLI runners
│   ├── init_db.py           # Database initialisation & verification runner
│   ├── run_chatbot.py       # Interactive terminal chatbot runner
│   └── run_server.py        # FastAPI + Uvicorn web server runner
│
├── frontend/                # Modern Space-themed React + Tailwind CSS web application
│   ├── src/                 # React components (Chatbot, Menu, Zones, Hero, Modals)
│   ├── public/assets/       # Coherent photography (Burgers, Steaks, Shakes, Space Interior)
│   ├── tailwind.config.js   # Tailwind CSS v3 theme configuration (Cosmos palette & glows)
│   ├── package.json         # Frontend dependencies (React, Vite, Tailwind, Lucide)
│   └── dist/                # Pre-built production bundle served by FastAPI
│
├── src/
│   └── eatwithai/           # Core Python package (src layout)
│       ├── __init__.py      # Package exports & version
│       ├── server.py        # FastAPI backend (SSE streaming chat, menu, bookings, static SPA)
│       ├── config.py        # Centralized path, DB, and Gemini configuration
│       ├── models.py        # Domain dataclasses (Customer, RestaurantTable, Booking, etc.)
│       ├── security.py      # Defense-in-depth prompt injection defense & input sanitizers
│       ├── cli.py           # Unified CLI interface (`init-db`, `chat`, `status`)
│       ├── __main__.py      # Allows `python -m eatwithai`
│       │
│       ├── db/              # Database subpackage
│       │   ├── __init__.py  # Database facade exports
│       │   ├── connection.py# PostgreSQL connection manager & error handling
│       │   └── repository.py# Table availability lookups, CRUD queries, init/seed logic
│       │
│       └── chatbot/         # AI Chatbot subpackage
│           ├── __init__.py  # Chatbot facade exports
│           ├── agent.py     # GeminiRestaurantChatbot streaming engine & session manager
│           ├── prompts.py   # Dynamic system instruction with live time grounding
│           ├── tools.py     # LLM tool implementations (availability, booking, slots)
│           └── schemas.py   # OpenAI / JSON Schema tool definitions
│
└── tests/                   # Automated unit & integration tests
    ├── __init__.py
    ├── test_config.py       # Path & environment configuration tests
    ├── test_models.py       # Dataclass model instantiation & typing tests
    ├── test_security.py     # Prompt injection regex & sanitization tests
    ├── test_tools.py        # Tool formatting & JSON serialization tests
    └── test_db.py           # PostgreSQL integration tests
```

---

## 🔐 Configuration (`.env`)

Create a `.env` file in the project root (copy from `.env.example`):

```env
# PostgreSQL Database Credentials
DB_HOST=localhost
DB_PORT=5432
DB_NAME=Restaurant
DB_USER=postgres
DB_PASSWORD=your_actual_password_here
DB_SSLMODE=prefer

# Gemini AI Configuration
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash
```

> [!NOTE]
> `.env` is automatically excluded from git in `.gitignore` to prevent leaking credentials.

---

## 🚀 Setup & Installation

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```
Or install in editable mode:
```bash
pip install -e .
```

### 2. Initialize and Seed the Database
Run the database initializer script:
```bash
python3 scripts/init_db.py
```
Or via the package CLI:
```bash
python3 -m eatwithai init-db
```
This will:
- Connect to PostgreSQL using your `.env` credentials
- Run `sql/schema.sql` (creating extensions, tables, constraints, indexes, triggers, and views)
- Run `sql/seed_data.sql` (populating sample records and synchronizing ID sequences)
- Print a summary verification of all tables, views, and reservation logic

### 3. Launch the Web Server & Space Restaurant Website
Start the FastAPI web server to launch the full website and real-time AI concierge:
```bash
python3 scripts/run_server.py
```
Then open your browser at:
* **Website**: [http://localhost:8000](http://localhost:8000)
* **API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)

### 4. Launch the Terminal AI Chatbot (CLI Mode)
If you prefer testing the chatbot directly in your terminal:
```bash
python3 scripts/run_chatbot.py
```
Or via the package CLI:
```bash
python3 -m eatwithai chat
```

### 5. Check System Status
Verify database connectivity and environment configuration anytime:
```bash
python3 -m eatwithai status
```

---

## 🌐 Space Restaurant Web Application & Architecture

The website features an immersive space-station aesthetic ("Orbiting at 408 km") built with **Tailwind CSS v3**, **React**, and **FastAPI**:

### Key Features
1. **Gemini AI Concierge Terminal**:
   - Implements the exact logic and guardrails from `scripts/run_chatbot.py`.
   - Token-by-token **Server-Sent Events (SSE)** streaming (`POST /api/chat/stream`).
   - Live guardrail telemetry indicators (Prompt Injection Regex, Boundary Isolation, Confirmation Barrier).
   - Floating AI chat orb at bottom-right for seamless access while browsing.
2. **Database-Grounded Menu**:
   - Dynamically loads all 8 categories and 35 dishes directly from PostgreSQL (`GET /api/menu`).
   - Photography matches the database: Handcrafted Burgers, USDA Prime Steaks, and Hand-Spun Shakes.
   - Dietary filters (Vegetarian, Vegan, Gluten-Free) and search bar.
   - One-click *"Ask AI Host About This Dish"* integration.
3. **Dining Zones & Table Booking**:
   - Live visual layout of all 4 zones: Indoor Nebula Lounge, Starlight Terrace, Meteorite Bar, and Orbital Private Suite.
   - Interactive Booking Wizard (`POST /api/check-availability` & `POST /api/reserve`) with confetti celebrations.
4. **Mission Schedule & Shifts**:
   - Live hours and upcoming scheduled closures from PostgreSQL.

### Development Mode (Frontend HMR)
To modify frontend code with live reload:
```bash
# Terminal 1: Start backend
python3 scripts/run_server.py

# Terminal 2: Start Vite dev server
cd frontend
npm run dev
```
Open [http://localhost:5173](http://localhost:5173). Requests to `/api` proxy automatically to `:8000`.

To rebuild the production bundle:
```bash
cd frontend && npm run build
```

---

## 🧪 Running Automated Tests

Run the complete test suite with `unittest`:
```bash
PYTHONPATH=src python3 -m unittest discover -s tests -p "test_*.py"
```
Or with `pytest`:
```bash
pytest
```

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
| **`menu_categories`** | `SERIAL` (`category_id`) | `name` (UNIQUE, e.g. 'Handcrafted Burgers', 'Texas & Southern BBQ'), `description`, `display_order` |
| **`menu_items`** | `SERIAL` (`item_id`) | `category_id` (FK), `name` (UNIQUE), `description`, `price` (NUMERIC), `calories`, `spicy_level` (0-3), `is_vegetarian`, `is_vegan`, `is_gluten_free`, `allergens`, `is_available`, `updated_at` (auto-updated by trigger) |

### PostgreSQL Views
* **`v_tables_with_combinations`**: Shows each table along with an aggregated `combinable_with` column built with `STRING_AGG`.
* **`v_booking_details`**: Joined report of bookings with customer contact details, assigned tables, stay duration in minutes (`EXTRACT(EPOCH FROM ...)`), and capacity.
* **`v_menu_details`**: Comprehensive overview of American food menu items joined with category name, dietary flags, spicy level, and pricing.

---

## 💻 Python Usage Example

```python
from datetime import datetime
from eatwithai.db import get_connection, create_booking, get_available_tables, get_menu_items, search_menu

with get_connection() as conn:
    # 1. Check table availability for an upcoming slot
    start = datetime(2026, 10, 20, 19, 30)
    end = datetime(2026, 10, 20, 21, 15)
    tables = get_available_tables(conn, start, end, area="indoor")
    print("Available tables:", [t["name"] for t in tables])

    # 2. Query American menu items by category or dietary preference
    burgers = get_menu_items(conn, category="Burgers")
    print("Handcrafted Burgers:", [b["name"] for b in burgers])

    # 3. Search menu items
    brisket = search_menu(conn, "brisket")
    print("BBQ Brisket:", brisket[0]["name"], f"${brisket[0]['price']}")

    # 4. Book a table (duration automatically calculated from dining_rules)
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

## 🤖 Chatbot Tools (`eatwithai.chatbot.tools`)

| Function | Purpose |
| :--- | :--- |
| **`check_restaurant_status(date_str, time_str)`** | Evaluates if the restaurant is open, closed for holiday, outside shift hours, or past last bookable cutoff. |
| **`check_table_availability(date_str, time_str, party_size, area=None)`** | Determines if single or joined combinable tables are available and computes exact stay duration. |
| **`find_available_slots(date_str, party_size, preferred_time=None)`** | Searches for open time slots throughout the day if requested time is taken. |
| **`get_restaurant_schedule(date_str=None)`** | Returns weekly hours and holiday closures (or schedule for a specific date). |
| **`get_dining_duration_for_party(party_size)`** | Looks up allowed stay duration based on party size. |
| **`get_restaurant_menu(category=None, dietary_preference=None, max_price=None)`** | Returns the authentic American food menu, supporting category, dietary, and budget filtering. |
| **`search_menu_items(search_query)`** | Searches menu items by dish name, ingredient, keyword, or allergen. |
| **`create_booking_reservation(...)`** | End-to-end booking tool that creates the customer and assigns the best table. |
| **`cancel_booking_reservation(booking_id, phone_or_email)`** | Verifies ownership and cancels a booking. |
| **`get_booking_info(booking_id)`** | Retrieves details of an existing reservation. |

Includes pre-built OpenAI-compatible tool definitions in **`CHATBOT_TOOL_DEFINITIONS`** (`eatwithai.chatbot.schemas`).


---

## 🛡️ Gemini AI Chatbot & Security Guardrails (`eatwithai.security`)

A conversational AI reservation host powered by **Google Gemini**, engineered with defense-in-depth protection against prompt injection, jailbreaking, and data leakage.

### Security Layers:
1. **Deterministic Injection Pre-Filter (`security.py`)**:
   Regex pattern analysis detects and immediately blocks direct instruction overrides (`"ignore instructions"`), jailbreak roleplay (`"DAN"`, `"developer mode"`), system prompt leakage probes (`"print your system prompt"`), and SQL injection attempts before any API calls are made.
2. **Structural Boundary Delimitation**:
   User input is wrapped inside `<untrusted_customer_message>...</untrusted_customer_message>` boundary tags, training the model to treat content strictly as untrusted customer data.
3. **Mandatory Confirmation Barrier**:
   The bot is strictly prohibited by system rules from invoking `create_booking_reservation` without first presenting a full summary and receiving explicit user confirmation.
4. **Input Sanitization & Length Limits**:
   Normalizes whitespace, removes non-printable control characters, and caps message lengths at 600 characters to prevent buffer overflow/token flood attacks.
