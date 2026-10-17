"""
Data models representing the restaurant database entities using Python dataclasses.
"""

from dataclasses import dataclass, field
from datetime import datetime, date, time
from typing import Optional, List


@dataclass
class Customer:
    customer_id: str  # UUID v4 string
    name: str
    surname: str
    phone: str
    email: Optional[str] = None
    created_at: Optional[datetime] = None


@dataclass
class RestaurantTable:
    table_id: int
    name: str  # e.g., 'T01', 'TR01'
    seats_min: int
    seats_max: int
    area: str  # 'indoor', 'terrace', 'bar', 'private_room'
    active: bool = True
    combinable_with: List[str] = field(default_factory=list)


@dataclass
class OpeningShift:
    shift_id: int
    shift_name: str  # 'lunch', 'dinner'
    weekday: int  # 0 = Monday, 6 = Sunday
    weekday_name: str
    start_time: str  # HH:MM
    end_time: str  # HH:MM
    last_bookable_time: str  # HH:MM


@dataclass
class Closure:
    closure_id: int
    date: str  # YYYY-MM-DD
    shift_id: Optional[int]  # None means full day closure
    reason: str


@dataclass
class DiningRule:
    rule_id: int
    party_size_from: int
    party_size_to: int
    duration_minutes: int
    description: Optional[str] = None


@dataclass
class Booking:
    booking_id: str  # UUID v4 string
    customer_id: str  # UUID v4 string
    start_time: datetime
    end_time: datetime
    party_size: int
    status: str  # 'pending', 'confirmed', 'cancelled', 'arrived', 'no_show'
    source: str  # 'chatbot', 'phone', 'staff', 'website'
    special_requests: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    assigned_tables: List[str] = field(default_factory=list)
