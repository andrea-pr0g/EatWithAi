"""
Chatbot package for EatWithAi.
Provides conversational AI agent, LLM tool definitions, prompts, and CLI.
"""

from eatwithai.chatbot.agent import (
    GeminiRestaurantChatbot,
    init_gemini_client,
    run_cli,
    AVAILABLE_TOOLS,
)
from eatwithai.chatbot.prompts import get_system_instruction
from eatwithai.chatbot.schemas import CHATBOT_TOOL_DEFINITIONS
from eatwithai.chatbot import tools

__all__ = [
    "GeminiRestaurantChatbot",
    "init_gemini_client",
    "run_cli",
    "AVAILABLE_TOOLS",
    "CHATBOT_TOOL_DEFINITIONS",
    "get_system_instruction",
    "tools",
]
