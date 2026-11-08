"""
Security and Guardrails Module for Restaurant Chatbot.
Provides defense-in-depth protection against Prompt Injection, Jailbreaking,
System Prompt Leakage, and Data Manipulation.
"""

import re
import html
from typing import Tuple, Optional

# Maximum allowed character length for a single customer message
MAX_MESSAGE_LENGTH = 600

# High-confidence heuristic patterns for prompt injection & jailbreak attempts
INJECTION_PATTERNS = [
    # Direct instruction overrides
    r"ignore\s+(all\s+|any\s+|previous\s+|your\s+)?instructions",
    r"disregard\s+(all\s+|any\s+|previous\s+|your\s+)?instructions",
    r"forget\s+(everything\s+|all\s+|what\s+you\s+were\s+told)",
    r"override\s+(system|rules|prompt|mode)",
    r"system\s*:\s*override",
    r"new\s+system\s+(instruction|prompt|directive)",

    # System prompt extraction & leakage
    r"(repeat|output|show|print|reveal|leak|tell\s+me)\s+(your\s+)?(system\s+prompt|instructions|initial\s+prompt|rules)",
    r"what\s+(is|are)\s+your\s+(exact\s+)?(system\s+prompt|instructions)",
    r"start\s+your\s+response\s+with\s+[\"']?system\s*:",

    # Roleplay / Jailbreak personas
    r"act\s+as\s+(dan|an\s+unfiltered|an\s+uncensored|a\s+hacker|a\s+terminal)",
    r"you\s+are\s+now\s+(in\s+developer\s+mode|dan|unrestricted)",
    r"jailbreak\s*(mode|enabled|prompt)?",
    r"do\s+anything\s+now",

    # SQL / Database schema exploration
    r"(drop|alter|delete\s+from|truncate)\s+table",
    r"union\s+select",
    r"'\s*or\s*'1'\s*=\s*'1",
    r"show\s+(all\s+)?(tables|schemas|database|users|passwords)",
]

COMPILED_INJECTION_REGEX = re.compile("|".join(INJECTION_PATTERNS), re.IGNORECASE)


def sanitize_input(text: str) -> str:
    """
    Cleans raw customer input:
    - Normalizes whitespace.
    - Strips non-printable control characters.
    - Limits maximum length to prevent token flood attacks.
    - Escapes basic HTML.
    """
    if not text:
        return ""

    # Truncate to maximum length
    cleaned = text[:MAX_MESSAGE_LENGTH].strip()

    # Remove non-printable control characters (except newline, tab)
    cleaned = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", cleaned)

    # Normalize multiple whitespace characters
    cleaned = re.sub(r"[ \t]+", " ", cleaned)

    return html.escape(cleaned, quote=False)


def check_prompt_injection(text: str) -> Tuple[bool, Optional[str]]:
    """
    Scans input for prompt injection, jailbreaking, or system prompt leakage signatures.

    Returns:
        (is_flagged: bool, reason: Optional[str])
    """
    if not text:
        return False, None

    match = COMPILED_INJECTION_REGEX.search(text)
    if match:
        return True, f"Blocked pattern matched: '{match.group(0)}'"

    return False, None


def wrap_user_message_with_boundary(text: str) -> str:
    """
    Wraps sanitized customer input in structural boundary tags.
    Instructs the LLM that content inside is raw untrusted data.
    """
    sanitized = sanitize_input(text)
    return (
        f"<untrusted_customer_message>\n"
        f"{sanitized}\n"
        f"</untrusted_customer_message>"
    )


from pydantic import ValidationError
from eatwithai.models import BookingValidation, BookingRequest, BookingInput, VALID_ZONES


def validate_booking_data(
    name: str,
    surname: str,
    phone: str,
    party_size: int,
    special_requests: Optional[str] = None,
    email: Optional[str] = None,
    time: str = "19:30",
    day: str = "2026-10-20",
    zone: str = "indoor",
    **kwargs,
) -> Tuple[bool, Optional[str]]:
    """
    Rigorous application-layer validation of reservation parameters using Pydantic (`BookingValidation`).
    Validates name, surname, phone, email (optional), party_size, time, day, zone,
    and special_requests (optional).
    """
    resolved_time = kwargs.pop("time_str", time)
    resolved_day = kwargs.pop("date_str", kwargs.pop("date", day))
    resolved_zone = kwargs.pop("area", kwargs.pop("zone_preference", zone))
    resolved_special = kwargs.pop("special_request", special_requests)

    try:
        BookingValidation(
            name=name,
            surname=surname,
            phone=phone,
            email=email,
            party_size=party_size,
            time=resolved_time,
            day=resolved_day,
            zone=resolved_zone,
            special_requests=resolved_special,
            **kwargs,
        )
        return True, None
    except ValidationError as exc:
        first_err = exc.errors()[0] if exc.errors() else {"msg": str(exc)}
        msg = first_err.get("msg", str(exc))
        if msg.startswith("Value error, "):
            msg = msg[len("Value error, "):]
        return False, msg

