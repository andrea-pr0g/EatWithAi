"""
FastAPI Backend Server for EatWithAi Space-Themed Restaurant.
Exposes real-time streaming chatbot endpoints, menu data, availability checks,
and reservation management powered by Gemini and PostgreSQL.
"""

import os
import sys
import json
import uuid
import time
import asyncio
import logging
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Generator

from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

# Ensure src is on sys.path
SRC_DIR = Path(__file__).resolve().parent.parent
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from eatwithai.chatbot.agent import GeminiRestaurantChatbot
from eatwithai.chatbot import tools
from eatwithai.security import check_prompt_injection
from eatwithai.db import get_connection, update_tables_occupancy, get_tables_status

logger = logging.getLogger("eatwithai.server")

async def table_occupancy_checker(interval_seconds: int = 10):
    """
    Continuous background loop that always checks whether each table
    in the database is occupied by an active booking or free.
    Updates the 'available' column in PostgreSQL (False if occupied/inactive, True if free).
    """
    try:
        with get_connection() as conn:
            update_tables_occupancy(conn)
            logger.info("Initial table occupancy synchronized successfully.")
    except Exception as e:
        logger.error(f"Initial table occupancy check failed: {e}")

    while True:
        try:
            await asyncio.sleep(interval_seconds)
            with get_connection() as conn:
                update_tables_occupancy(conn)
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Error in continuous table occupancy monitor: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start continuous table occupancy monitoring daemon
    monitor_task = asyncio.create_task(table_occupancy_checker(interval_seconds=10))
    yield
    # Cleanup on server shutdown
    monitor_task.cancel()
    try:
        await monitor_task
    except asyncio.CancelledError:
        pass


app = FastAPI(
    title="EatWithAi Galactic Restaurant API",
    description="Space-themed restaurant AI reservation system & authentic American dining API",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for local Vite dev server and external clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Active chat sessions in memory
_sessions: Dict[str, GeminiRestaurantChatbot] = {}
_session_last_active: Dict[str, float] = {}

def get_or_create_bot(session_id: str) -> GeminiRestaurantChatbot:
    """Retrieves an existing chatbot session or instantiates a new one."""
    current_time = time.time()
    
    # Simple clean up of sessions older than 2 hours
    expired_ids = [sid for sid, last_t in _session_last_active.items() if current_time - last_t > 7200]
    for sid in expired_ids:
        _sessions.pop(sid, None)
        _session_last_active.pop(sid, None)

    if session_id not in _sessions:
        _sessions[session_id] = GeminiRestaurantChatbot()
    _session_last_active[session_id] = current_time
    return _sessions[session_id]


# Pydantic Schemas
class ChatRequest(BaseModel):
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    message: str

class ResetChatRequest(BaseModel):
    session_id: str

class AvailabilityRequest(BaseModel):
    date: str
    time: str
    party_size: int
    zone: Optional[str] = None

class ReservationRequest(BaseModel):
    customer_name: str
    customer_phone: str
    customer_email: Optional[str] = None
    party_size: int
    date: str
    time: str
    zone_preference: Optional[str] = None
    special_requests: Optional[str] = None

class CancellationRequest(BaseModel):
    booking_id: str
    verification_phone_or_email: str
    cancellation_reason: Optional[str] = "Customer requested cancellation"


@app.get("/api/health")
def health_check():
    return {
        "status": "online",
        "station": "EatWithAi Orbital Platform 1",
        "timestamp": datetime.now().isoformat(),
        "gemini_model": os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite"),
    }


@app.get("/api/tables")
def get_tables_live():
    """
    Returns real-time occupancy and availability status for all restaurant tables.
    Each table has an 'available' boolean column updated based on whether an active
    booking currently occupies the table.
    """
    try:
        with get_connection() as conn:
            tables_data = update_tables_occupancy(conn)
            # Ensure JSON-safe serialization
            safe_tables = [tools.serialize_for_json(t) for t in tables_data]
        return {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "total_tables": len(safe_tables),
            "tables": safe_tables,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/tables/sync-occupancy")
def sync_tables():
    """
    Forces an immediate recalculation of table occupancy and updates the available column.
    """
    try:
        with get_connection() as conn:
            tables_data = update_tables_occupancy(conn)
            safe_tables = [tools.serialize_for_json(t) for t in tables_data]
        return {
            "status": "success",
            "message": "Table occupancy synchronized successfully.",
            "timestamp": datetime.now().isoformat(),
            "tables": safe_tables,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/restaurant-info")
def get_restaurant_info():
    """Returns live restaurant status, operating schedule, and dining zones."""
    try:
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H:%M")
        
        status = tools.check_restaurant_status(date_str, time_str)
        schedule = tools.get_restaurant_schedule()
        areas = tools.get_restaurant_areas_and_tables()
        with get_connection() as conn:
            tables_data = update_tables_occupancy(conn)
            safe_tables = [tools.serialize_for_json(t) for t in tables_data]
        
        return {
            "status": status,
            "schedule": schedule,
            "areas": areas,
            "tables": safe_tables,
            "current_time": f"{date_str} {time_str}",
            "space_coordinates": {
                "altitude": "408 km (Low Earth Orbit)",
                "orbital_speed": "27,600 km/h",
                "inclination": "51.6°",
                "docking_bay": "Bay Alpha-7",
                "atmosphere": "Standard Earth 1.0 ATM / 21% O2",
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/menu")
def get_menu(category: Optional[str] = None, dietary: Optional[str] = None):
    """
    Returns authentic American food menu items categorized directly from PostgreSQL.
    """
    try:
        data = tools.get_restaurant_menu(category=category, dietary_preference=dietary)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/check-availability")
def check_availability(req: AvailabilityRequest):
    """Checks table availability and finds nearby slots."""
    try:
        # Check restaurant open/closed
        status = tools.check_restaurant_status(req.date, req.time)
        if not status.get("is_open"):
            alt_slots = tools.find_available_slots(req.date, req.party_size, req.time)
            return {
                "available": False,
                "reason": status.get("message", "Restaurant is closed at this time."),
                "shift": status.get("shift"),
                "alternative_slots": alt_slots.get("available_slots", []),
            }

        avail = tools.check_table_availability(req.date, req.time, req.party_size, req.zone)
        if avail.get("is_available"):
            duration = tools.get_dining_duration_for_party(req.party_size)
            return {
                "available": True,
                "message": avail.get("message"),
                "assigned_tables": avail.get("assigned_tables", []),
                "zone": avail.get("zone"),
                "dining_duration_minutes": duration.get("duration_minutes", 105),
            }
        else:
            alt_slots = tools.find_available_slots(req.date, req.party_size, req.time)
            return {
                "available": False,
                "reason": avail.get("reason", "Fully booked at this hour."),
                "alternative_slots": alt_slots.get("available_slots", []),
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/reserve")
def direct_reserve(req: ReservationRequest):
    """Direct reservation submission (for visual booking form)."""
    try:
        parts = req.customer_name.strip().split(" ", 1)
        first_name = parts[0]
        surname = parts[1] if len(parts) > 1 else "Traveler"

        result = tools.create_booking_reservation(
            name=first_name,
            surname=surname,
            phone=req.customer_phone,
            date_str=req.date,
            time_str=req.time,
            party_size=req.party_size,
            email=req.customer_email,
            area=req.zone_preference,
            special_requests=req.special_requests,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/cancel-booking")
def cancel_booking(req: CancellationRequest):
    """Cancels a booking with verification."""
    try:
        result = tools.cancel_booking_reservation(
            booking_id=req.booking_id,
            verification_phone_or_email=req.verification_phone_or_email,
            cancellation_reason=req.cancellation_reason,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/chat/reset")
def reset_chat(req: ResetChatRequest):
    """Resets conversation state for the given session ID."""
    _sessions.pop(req.session_id, None)
    _session_last_active.pop(req.session_id, None)
    return {"status": "reset", "session_id": req.session_id}


@app.post("/api/chat/stream")
async def chat_stream(req: ChatRequest):
    """
    Real-time Server-Sent Events (SSE) streaming endpoint for Gemini chatbot.
    Streams token chunks directly as generated, with guardrail telemetry.
    """
    # Pre-check injection
    is_injection, reason = check_prompt_injection(req.message)

    async def event_generator():
        # Telemetry event
        yield f"event: guardrails\ndata: {json.dumps({'injection_detected': is_injection, 'reason': reason})}\n\n"
        await asyncio.sleep(0.01)

        try:
            bot = get_or_create_bot(req.session_id)
            # Run generator in executor to not block async loop
            loop = asyncio.get_event_loop()

            def sync_stream():
                return list(bot.process_message_stream(req.message))

            chunks = await loop.run_in_executor(None, sync_stream)
            for chunk in chunks:
                yield f"event: token\ndata: {json.dumps({'chunk': chunk})}\n\n"
                await asyncio.sleep(0.015)

            yield f"event: done\ndata: {json.dumps({'done': True})}\n\n"
        except Exception as exc:
            yield f"event: error\ndata: {json.dumps({'error': str(exc)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )


# Serve built frontend static files if present
FRONTEND_DIST = SRC_DIR.parent / "frontend" / "dist"
if FRONTEND_DIST.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIST), html=True), name="frontend")
