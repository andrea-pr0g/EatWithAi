"""
EatWithAi - AI-powered Restaurant Reservation System.

A production-grade PostgreSQL and Google Gemini conversational reservation assistant
with strict prompt injection defense and automated availability scheduling.
"""

from eatwithai import config, models, security, db, chatbot
from eatwithai.models import BookingValidation, BookingRequest, BookingInput
from eatwithai.chatbot.agent import GeminiRestaurantChatbot
from eatwithai.db.connection import get_connection

__version__ = "1.0.0"

__all__ = [
    "__version__",
    "config",
    "models",
    "security",
    "db",
    "chatbot",
    "BookingValidation",
    "BookingRequest",
    "BookingInput",
    "GeminiRestaurantChatbot",
    "get_connection",
]
