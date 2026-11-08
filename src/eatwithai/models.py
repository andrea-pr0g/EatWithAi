"""
Data models representing the restaurant database entities using Python dataclasses
and Pydantic validation schemas for booking requests.
"""

from dataclasses import dataclass, field
from datetime import datetime, date as dt_date, time as dt_time
from decimal import Decimal
import re
from typing import Optional, List, Literal, Any

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    AliasChoices,
    field_validator,
)

VALID_ZONES = ("indoor", "terrace", "bar", "private_room")
ZoneType = Literal["indoor", "terrace", "bar", "private_room"]

EMAIL_REGEX = re.compile(r"^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$")
PHONE_ALLOWED_REGEX = re.compile(r"^\+?[\d\s\-\(\)\.]+$")
TIME_FORMAT_REGEX = re.compile(r"^\d{1,2}:\d{2}(?::\d{2})?$")
DATE_FORMAT_REGEX = re.compile(r"^\d{4}-\d{2}-\d{2}$")


class BookingValidation(BaseModel):
    """
    Pydantic model validating booking parameters:
    - name: customer first name (1-50 chars)
    - surname: customer surname / last name (1-50 chars)
    - phone: contact phone number (7-16 digits)
    - email: optional email address
    - party_size: number of guests (1-30)
    - time: reservation time in HH:MM (24-hour) format
    - day: reservation day/date in YYYY-MM-DD format
    - zone: seating zone ('indoor', 'terrace', 'bar', 'private_room')
    - special_requests: optional special request / dietary notes (max 200 chars)
    """

    model_config = ConfigDict(
        populate_by_name=True,
        extra="forbid",
    )

    name: str = Field(
        ...,
        description="Customer's first name (1-50 characters)",
    )
    surname: str = Field(
        ...,
        description="Customer's surname / last name (1-50 characters)",
    )
    phone: str = Field(
        ...,
        description="Customer's contact phone number (7-16 digits)",
    )
    email: Optional[str] = Field(
        default=None,
        description="Optional customer email address",
    )
    party_size: int = Field(
        ...,
        validation_alias=AliasChoices("party_size", "partySize"),
        description="Number of guests (1-30)",
    )
    time: str = Field(
        ...,
        validation_alias=AliasChoices("time", "time_str"),
        description="Reservation time in HH:MM (24-hour) format",
    )
    day: str = Field(
        ...,
        validation_alias=AliasChoices("day", "date", "date_str"),
        description="Reservation day/date in YYYY-MM-DD format",
    )
    zone: ZoneType = Field(
        ...,
        validation_alias=AliasChoices("zone", "area", "zone_preference"),
        description="Dining zone ('indoor', 'terrace', 'bar', 'private_room')",
    )
    special_requests: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("special_requests", "special_request"),
        description="Optional dietary requirements or special notes (max 200 characters)",
    )

    @field_validator("name", mode="before")
    @classmethod
    def validate_name(cls, v: Any) -> str:
        if not isinstance(v, str):
            raise ValueError("Customer first name must be a string.")
        cleaned = v.strip()
        if not (1 <= len(cleaned) <= 50):
            raise ValueError("Customer first name must be between 1 and 50 characters.")
        from eatwithai.security import check_prompt_injection

        flagged, _ = check_prompt_injection(cleaned)
        if flagged:
            raise ValueError("Customer first name contains invalid or suspicious content.")
        return cleaned

    @field_validator("surname", mode="before")
    @classmethod
    def validate_surname(cls, v: Any) -> str:
        if not isinstance(v, str):
            raise ValueError("Customer surname must be a string.")
        cleaned = v.strip()
        if not (1 <= len(cleaned) <= 50):
            raise ValueError("Customer surname must be between 1 and 50 characters.")
        from eatwithai.security import check_prompt_injection

        flagged, _ = check_prompt_injection(cleaned)
        if flagged:
            raise ValueError("Customer surname contains invalid or suspicious content.")
        return cleaned

    @field_validator("phone", mode="before")
    @classmethod
    def validate_phone(cls, v: Any) -> str:
        if not isinstance(v, str):
            raise ValueError("Phone number must be a string.")
        cleaned = v.strip()
        digits_only = re.sub(r"\D", "", cleaned)
        if not cleaned or not PHONE_ALLOWED_REGEX.match(cleaned) or not (7 <= len(digits_only) <= 16):
            raise ValueError("Please provide a valid contact phone number with at least 7 digits.")
        return cleaned

    @field_validator("email", mode="before")
    @classmethod
    def validate_email(cls, v: Any) -> Optional[str]:
        if v is None:
            return None
        if not isinstance(v, str):
            raise ValueError("Email address must be a string.")
        cleaned = v.strip()
        if not cleaned:
            return None
        if len(cleaned) > 255 or not EMAIL_REGEX.match(cleaned):
            raise ValueError("Please provide a valid email address.")
        from eatwithai.security import check_prompt_injection

        flagged, _ = check_prompt_injection(cleaned)
        if flagged:
            raise ValueError("Email address contains invalid or suspicious content.")
        return cleaned

    @field_validator("party_size", mode="before")
    @classmethod
    def validate_party_size(cls, v: Any) -> int:
        if isinstance(v, bool):
            raise ValueError("Party size must be an integer between 1 and 30 guests.")
        if isinstance(v, str):
            stripped = v.strip()
            if stripped.lstrip("-").isdigit():
                v = int(stripped)
            else:
                raise ValueError("Party size must be an integer between 1 and 30 guests.")
        if not isinstance(v, int):
            raise ValueError("Party size must be an integer between 1 and 30 guests.")
        if not (1 <= v <= 30):
            raise ValueError("Party size must be between 1 and 30 guests.")
        return v

    @field_validator("time", mode="before")
    @classmethod
    def validate_time(cls, v: Any) -> str:
        if isinstance(v, dt_time):
            return v.strftime("%H:%M")
        if not isinstance(v, str):
            raise ValueError("Time must be a valid string in HH:MM format.")
        cleaned = v.strip()
        if not TIME_FORMAT_REGEX.match(cleaned):
            raise ValueError("Time must be in HH:MM 24-hour format (e.g. '19:30').")
        fmt = "%H:%M:%S" if cleaned.count(":") == 2 else "%H:%M"
        try:
            parsed = datetime.strptime(cleaned, fmt)
        except ValueError as exc:
            raise ValueError("Time must be a valid 24-hour clock time in HH:MM format.") from exc
        return parsed.strftime("%H:%M")

    @field_validator("day", mode="before")
    @classmethod
    def validate_day(cls, v: Any) -> str:
        if isinstance(v, datetime):
            return v.strftime("%Y-%m-%d")
        if isinstance(v, dt_date):
            return v.strftime("%Y-%m-%d")
        if not isinstance(v, str):
            raise ValueError("Day must be a valid date string in YYYY-MM-DD format.")
        cleaned = v.strip().replace("/", "-")
        if not DATE_FORMAT_REGEX.match(cleaned):
            raise ValueError("Day must be in YYYY-MM-DD format (e.g. '2026-10-20').")
        try:
            parsed = datetime.strptime(cleaned, "%Y-%m-%d")
        except ValueError as exc:
            raise ValueError("Day must be a valid calendar date in YYYY-MM-DD format.") from exc
        return parsed.strftime("%Y-%m-%d")

    @field_validator("zone", mode="before")
    @classmethod
    def validate_zone(cls, v: Any) -> str:
        if not isinstance(v, str) or not v.strip():
            raise ValueError(f"Zone must be one of: {', '.join(VALID_ZONES)}.")
        cleaned = v.strip().lower()
        if cleaned not in VALID_ZONES:
            raise ValueError(f"Invalid zone '{v}'. Must be one of: {', '.join(VALID_ZONES)}.")
        return cleaned

    @field_validator("special_requests", mode="before")
    @classmethod
    def validate_special_requests(cls, v: Any) -> Optional[str]:
        if v is None:
            return None
        if not isinstance(v, str):
            raise ValueError("Special requests must be a string.")
        cleaned = v.strip()
        if not cleaned:
            return None
        if len(cleaned) > 200:
            raise ValueError("Special requests must not exceed 200 characters.")
        from eatwithai.security import check_prompt_injection

        flagged, _ = check_prompt_injection(cleaned)
        if flagged:
            raise ValueError("Special requests contain invalid or suspicious instructions.")
        return cleaned

    @property
    def date(self) -> str:
        return self.day

    @property
    def date_str(self) -> str:
        return self.day

    @property
    def time_str(self) -> str:
        return self.time

    @property
    def area(self) -> str:
        return self.zone

    @property
    def special_request(self) -> Optional[str]:
        return self.special_requests


BookingRequest = BookingValidation
BookingInput = BookingValidation


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
    available: bool = True
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


@dataclass
class MenuCategory:
    category_id: int
    name: str
    description: Optional[str] = None
    display_order: int = 0
    created_at: Optional[datetime] = None


@dataclass
class MenuItem:
    item_id: int
    category_id: int
    name: str
    description: str
    price: Decimal
    category_name: Optional[str] = None
    is_available: bool = True
    calories: Optional[int] = None
    spicy_level: int = 0
    is_vegetarian: bool = False
    is_vegan: bool = False
    is_gluten_free: bool = False
    allergens: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

