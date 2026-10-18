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


def validate_booking_data(
    name: str,
    surname: str,
    phone: str,
    party_size: int,
    special_requests: Optional[str] = None
) -> Tuple[bool, Optional[str]]:
    """
    Rigorous application-layer validation of reservation parameters before execution.
    Prevents malformed data or injected payloads in table/name fields.
    """
    # Name validation
    if not (1 <= len(name.strip()) <= 50):
        return False, "Customer first name must be between 1 and 50 characters."
    if not (1 <= len(surname.strip()) <= 50):
        return False, "Customer surname must be between 1 and 50 characters."

    # Phone validation (must contain at least 7 digits)
    digits_only = re.sub(r"\D", "", phone)
    if len(digits_only) < 7 or len(digits_only) > 16:
        return False, "Please provide a valid contact phone number with at least 7 digits."

    # Party size validation
    if not (1 <= party_size <= 30):
        return False, "Party size must be between 1 and 30 guests."

    # Special requests payload inspection
    if special_requests:
        if len(special_requests) > 200:
            return False, "Special requests must not exceed 200 characters."
        flagged, reason = check_prompt_injection(special_requests)
        if flagged:
            return False, "Special requests contain invalid or suspicious instructions."

    return True, None
