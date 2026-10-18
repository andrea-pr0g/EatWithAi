"""
OpenAI & LLM Function Calling Schema Definitions for EatWithAi Chatbot.
"""

CHATBOT_TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "check_restaurant_status",
            "description": "Checks if the restaurant is open on a specific date and time, evaluating weekly shifts, holiday closures, and shift cutoff times.",
            "parameters": {
                "type": "object",
                "properties": {
                    "date_str": {"type": "string", "description": "Date in YYYY-MM-DD format (e.g. '2026-10-20')"},
                    "time_str": {"type": "string", "description": "Time in HH:MM format (24-hour clock, e.g. '19:30')"}
                },
                "required": ["date_str", "time_str"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_table_availability",
            "description": "Checks whether table(s) are available for a given party size on a specific date, time, and optional seating area.",
            "parameters": {
                "type": "object",
                "properties": {
                    "date_str": {"type": "string", "description": "Date in YYYY-MM-DD format"},
                    "time_str": {"type": "string", "description": "Time in HH:MM format (24-hour clock)"},
                    "party_size": {"type": "integer", "description": "Number of guests (e.g. 2, 4, 8)"},
                    "area": {
                        "type": "string",
                        "enum": ["indoor", "terrace", "bar", "private_room"],
                        "description": "Optional seating area preference"
                    }
                },
                "required": ["date_str", "time_str", "party_size"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "find_available_slots",
            "description": "Finds open time slots for a party on a given date if their preferred hour is unavailable or when asked for options.",
            "parameters": {
                "type": "object",
                "properties": {
                    "date_str": {"type": "string", "description": "Date in YYYY-MM-DD format"},
                    "party_size": {"type": "integer", "description": "Number of guests"},
                    "preferred_time": {"type": "string", "description": "Optional preferred time (e.g. '20:00')"},
                    "area": {"type": "string", "description": "Optional seating area"}
                },
                "required": ["date_str", "party_size"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_restaurant_schedule",
            "description": "Retrieves the weekly opening hours, shifts, and holiday closures, or the hours for a specific date.",
            "parameters": {
                "type": "object",
                "properties": {
                    "date_str": {"type": "string", "description": "Optional specific date in YYYY-MM-DD format"}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_booking_reservation",
            "description": "Confirms and books a table reservation for a customer with contact details, party size, and optional requests.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Customer's first name"},
                    "surname": {"type": "string", "description": "Customer's last name"},
                    "phone": {"type": "string", "description": "Customer's contact phone number"},
                    "email": {"type": "string", "description": "Optional customer email address"},
                    "date_str": {"type": "string", "description": "Reservation date in YYYY-MM-DD format"},
                    "time_str": {"type": "string", "description": "Reservation time in HH:MM format (24-hour clock)"},
                    "party_size": {"type": "integer", "description": "Number of guests"},
                    "area": {"type": "string", "enum": ["indoor", "terrace", "bar", "private_room"]},
                    "special_requests": {"type": "string", "description": "Dietary requirements or special notes"}
                },
                "required": ["name", "surname", "phone", "date_str", "time_str", "party_size"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "cancel_booking_reservation",
            "description": "Cancels an existing reservation after verifying the customer's phone or email address.",
            "parameters": {
                "type": "object",
                "properties": {
                    "booking_id": {"type": "string", "description": "UUID reference ID of the reservation"},
                    "phone_or_email": {"type": "string", "description": "Customer's phone or email for identity verification"}
                },
                "required": ["booking_id", "phone_or_email"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_restaurant_areas_and_tables",
            "description": "Retrieves the available dining zones/areas (indoor, terrace, bar, private room), their seat capacities, active table counts, and seating configurations.",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_booking_info",
            "description": "Retrieves the details and status of an existing reservation by its reference ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "booking_id": {"type": "string", "description": "UUID reference ID of the reservation"}
                },
                "required": ["booking_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_restaurant_menu",
            "description": "Retrieves the restaurant's authentic American food menu, including categories, dish descriptions, prices, spicy levels, and dietary information (vegetarian, vegan, gluten-free).",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "Optional category filter (e.g. 'Burgers', 'BBQ', 'Steaks', 'Starters', 'Sides', 'Desserts', 'Beverages')"
                    },
                    "dietary_preference": {
                        "type": "string",
                        "enum": ["vegetarian", "vegan", "gluten-free"],
                        "description": "Optional dietary filter"
                    },
                    "max_price": {
                        "type": "number",
                        "description": "Optional maximum price filter"
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_menu_items",
            "description": "Searches American menu items by keyword, dish name, ingredient, or allergen (e.g. 'ribeye', 'wings', 'cheeseburger', 'brisket', 'shake', 'fries').",
            "parameters": {
                "type": "object",
                "properties": {
                    "search_query": {
                        "type": "string",
                        "description": "Dish name, ingredient, or food term to search for"
                    }
                },
                "required": ["search_query"]
            }
        }
    }
]

