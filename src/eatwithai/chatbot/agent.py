"""
Gemini Restaurant Chatbot with Advanced Prompt Injection Defense.

Features:
- Multi-layer defense against prompt injection, jailbreaking, and system prompt leakage.
- Strict Data / Instruction separation using boundary tags.
- Mandatory Confirmation Barrier before database modifications (create/cancel reservations).
- Built-in input sanitization and heuristic attack rejection.
- Compatible with Google GenAI SDK (gemini-2.5-flash / gemini-2.0-flash / gemini-3.1-flash-lite).
- Interactive CLI for testing and terminal chat.
"""

import os
import sys
import json
import time
from typing import List, Dict, Any, Optional, Generator

from eatwithai.config import get_gemini_config
from eatwithai.security import (
    sanitize_input,
    check_prompt_injection,
    wrap_user_message_with_boundary,
    validate_booking_data,
)
from eatwithai.chatbot.prompts import get_system_instruction
from eatwithai.chatbot import tools

# Tool mappings
AVAILABLE_TOOLS = {
    "check_restaurant_status": tools.check_restaurant_status,
    "check_table_availability": tools.check_table_availability,
    "find_available_slots": tools.find_available_slots,
    "get_dining_duration_for_party": tools.get_dining_duration_for_party,
    "get_restaurant_schedule": tools.get_restaurant_schedule,
    "get_restaurant_areas_and_tables": tools.get_restaurant_areas_and_tables,
    "create_booking_reservation": tools.create_booking_reservation,
    "cancel_booking_reservation": tools.cancel_booking_reservation,
    "get_booking_info": tools.get_booking_info,
}


def init_gemini_client():
    """
    Initializes and returns the Gemini client (using modern google-genai or legacy google-generativeai).
    """
    cfg = get_gemini_config()
    api_key = cfg["api_key"]

    if not api_key or api_key == "your_gemini_api_key_here":
        raise ValueError(
            "\n" + "=" * 65 + "\n"
            "[ERROR] Missing GEMINI_API_KEY in your .env file.\n"
            "Please obtain an API key at: https://aistudio.google.com/\n"
            "And add it to your .env file:\n"
            "    GEMINI_API_KEY=AIzaSy...\n"
            + "=" * 65
        )

    # 1. Try modern google-genai SDK
    try:
        from google import genai
        return "google-genai", genai.Client(api_key=api_key), cfg["model"]
    except ImportError:
        pass

    # 2. Try legacy google-generativeai SDK
    try:
        import google.generativeai as legacy_genai
        legacy_genai.configure(api_key=api_key)
        return "google-generativeai", legacy_genai, cfg["model"]
    except ImportError:
        raise ImportError(
            "\n" + "=" * 65 + "\n"
            "[ERROR] Gemini SDK not installed.\n"
            "Please install it with:\n"
            "    pip install google-genai\n"
            "or: pip install -r requirements.txt\n"
            + "=" * 65
        )


class GeminiRestaurantChatbot:
    """
    Interactive conversation manager with defense-in-depth guardrails.
    """

    def __init__(self):
        self.sdk_type, self.client, self.model_name = init_gemini_client()
        self.history: List[Dict[str, Any]] = []

    def process_message_stream(self, user_message: str) -> Generator[str, None, None]:
        """
        Processes a customer message and yields text chunks in real time
        for smooth streaming responses.
        """
        # --- LAYER 1: Pre-execution Injection Check ---
        is_injection, reason = check_prompt_injection(user_message)
        if is_injection:
            # Deterministically reject hostile inputs without burning API tokens
            refusal = (
                "I am only able to assist with table reservations, opening hours, "
                "and dining questions for our restaurant. How can I help you with your booking today?"
            )
            for word in refusal.split(" "):
                yield word + " "
                time.sleep(0.012)
            return

        # --- LAYER 2: Structural Boundary Delimitation ---
        delimited_user_message = wrap_user_message_with_boundary(user_message)

        # --- LAYER 3: LLM Execution with Real-Time Streaming ---
        if self.sdk_type == "google-genai":
            yield from self._stream_google_genai(delimited_user_message)
        else:
            yield from self._stream_legacy_genai(delimited_user_message)

    def process_message(self, user_message: str) -> str:
        """
        Synchronous non-streaming wrapper returning the complete response string.
        """
        return "".join(self.process_message_stream(user_message))

    def _stream_google_genai(self, delimited_message: str) -> Generator[str, None, None]:
        """Streams conversation chunks in real time using google-genai SDK."""
        from google.genai import types

        # Package Python functions as tools
        tool_functions = [
            tools.check_restaurant_status,
            tools.check_table_availability,
            tools.find_available_slots,
            tools.get_dining_duration_for_party,
            tools.get_restaurant_schedule,
            tools.get_restaurant_areas_and_tables,
            tools.create_booking_reservation,
            tools.cancel_booking_reservation,
            tools.get_booking_info,
        ]

        if not hasattr(self, "_chat_session"):
            self._chat_session = self.client.chats.create(
                model=self.model_name,
                config=types.GenerateContentConfig(
                    system_instruction=get_system_instruction(),
                    tools=tool_functions,
                    temperature=0.0,
                )
            )

    def _extract_parts_text(self, obj: Any) -> str:
        """Safely extracts text parts from response or chunk without triggering SDK warning."""
        try:
            parts = []
            if hasattr(obj, "candidates") and obj.candidates:
                for candidate in obj.candidates:
                    if hasattr(candidate, "content") and candidate.content and hasattr(candidate.content, "parts"):
                        for part in candidate.content.parts:
                            if hasattr(part, "text") and part.text:
                                parts.append(part.text)
            return "".join(parts)
        except Exception:
            return ""

    def _stream_google_genai(self, delimited_message: str) -> Generator[str, None, None]:
        """Streams conversation chunks in real time using google-genai SDK."""
        from google.genai import types

        # Package Python functions as tools
        tool_functions = [
            tools.check_restaurant_status,
            tools.check_table_availability,
            tools.find_available_slots,
            tools.get_dining_duration_for_party,
            tools.get_restaurant_schedule,
            tools.get_restaurant_areas_and_tables,
            tools.create_booking_reservation,
            tools.cancel_booking_reservation,
            tools.get_booking_info,
        ]

        if not hasattr(self, "_chat_session"):
            self._chat_session = self.client.chats.create(
                model=self.model_name,
                config=types.GenerateContentConfig(
                    system_instruction=get_system_instruction(),
                    tools=tool_functions,
                    temperature=0.0,
                )
            )

        # Try native SDK streaming first
        try:
            stream_response = self._chat_session.send_message_stream(delimited_message)
            streamed_tokens = False
            for chunk in stream_response:
                text_part = self._extract_parts_text(chunk)
                if text_part:
                    streamed_tokens = True
                    yield text_part
            if streamed_tokens:
                return
        except Exception:
            # If send_message_stream encounters an issue with automatic function calling,
            # gracefully fall back to send_message and stream smoothly
            pass

        # Robust execution fallback with smooth token flow
        response = self._chat_session.send_message(delimited_message)
        full_text = self._extract_parts_text(response) or "I have processed your request. How else may I assist you?"
        for word in full_text.split(" "):
            yield word + " "
            time.sleep(0.015)

    def _stream_legacy_genai(self, delimited_message: str) -> Generator[str, None, None]:
        """Streams conversation chunks with legacy google-generativeai SDK."""
        if not hasattr(self, "_legacy_chat_session"):
            tool_functions = list(AVAILABLE_TOOLS.values())
            model = self.client.GenerativeModel(
                model_name=self.model_name,
                system_instruction=get_system_instruction(),
                tools=tool_functions,
            )
            self._legacy_chat_session = model.start_chat(enable_automatic_function_calling=True)

        try:
            response = self._legacy_chat_session.send_message(delimited_message, stream=True)
            streamed_tokens = False
            for chunk in response:
                if chunk.text:
                    streamed_tokens = True
                    yield chunk.text
            if streamed_tokens:
                return
        except Exception:
            pass

        response = self._legacy_chat_session.send_message(delimited_message)
        full_text = response.text or "I have processed your request. How else may I assist you?"
        for word in full_text.split(" "):
            yield word + " "
            time.sleep(0.015)


def run_cli():
    """Interactive CLI chat loop."""
    print("=" * 65)
    print(" ANTIGRAVITY OSTERIA - GEMINI RESERVATION ASSISTANT ")
    print("=" * 65)
    print("Active Guardrails:")
    print("  [x] Prompt injection & jailbreak regex pre-filtering")
    print("  [x] Structural message boundary isolation (<untrusted_customer_message>)")
    print("  [x] Explicit confirmation barrier before booking")
    print("  [x] Real-time token response streaming")
    print("-" * 65)
    print("Type 'exit' or 'quit' to end the session.\n")

    try:
        bot = GeminiRestaurantChatbot()
        print(f"Connected to model: {bot.model_name} (using {bot.sdk_type})\n")
    except Exception as e:
        print(f"{e}\n")
        print("[Offline Guardrail Test Mode Activated]")
        print("You can test prompt injection defense inputs right now:\n")
        while True:
            try:
                user_input = input("You: ").strip()
                if not user_input or user_input.lower() in ("exit", "quit"):
                    break
                flagged, reason = check_prompt_injection(user_input)
                if flagged:
                    print(f"Bot (Guardrail Triggered): [BLOCKED: {reason}]")
                    print("Bot: I am only able to assist with table reservations and dining questions.\n")
                else:
                    wrapped = wrap_user_message_with_boundary(user_input)
                    print("Bot (Guardrail Passed): Input is clean and would be safely passed to Gemini:")
                    print(f"       {wrapped}\n")
            except (KeyboardInterrupt, EOFError):
                break
        return

    # Live chat loop with real-time streaming to stdout
    while True:
        try:
            user_input = input("You: ").strip()
            if not user_input or user_input.lower() in ("exit", "quit"):
                print("\nGoodbye! Have a wonderful day.")
                break

            print("\nBot: ", end="", flush=True)
            for chunk in bot.process_message_stream(user_input):
                print(chunk, end="", flush=True)
            print("\n")
        except (KeyboardInterrupt, EOFError):
            print("\nSession ended.")
            break
        except Exception as err:
            print(f"\n[Error processing message]: {err}\n")


if __name__ == "__main__":
    run_cli()
