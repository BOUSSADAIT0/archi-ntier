from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID
import os
import logging

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from ...domain.entities.booking import BookingStatus
from ...domain.services.booking_service import BookingService, BookingError
from ...domain.services.event_service import EventService, EventError
from ..persistence.connection_pool import DatabaseConnectionPool
from ..persistence.mariadb_booking_repository import MariaDBBookingRepository
from ..persistence.mariadb_event_repository import MariaDBEventRepository

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialisation de la pool de connexions
try:
    DatabaseConnectionPool.get_instance(
        host=os.getenv('DB_HOST', 'haproxy'),
        port=int(os.getenv('DB_PORT', '3306')),
        user=os.getenv('DB_USER', 'app_user'),
        password=os.getenv('DB_PASSWORD', 'app_password'),
        database=os.getenv('DB_NAME', 'event_booking')
    )
    logger.info("Database connection pool initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize database connection pool: {str(e)}")
    raise

app = FastAPI(title="Event Booking System")

# Configuration CORS simplifiée
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,  # Important: doit être False quand allow_origins=["*"]
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_cors_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response

@app.options("/{full_path:path}")
async def options_handler(request: Request):
    return JSONResponse(
        content={},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
        },
    )

# DTOs
class EventCreate(BaseModel):
    name: str
    description: str
    venue: str
    categories: List[str]

class EventResponse(BaseModel):
    id: UUID
    name: str
    description: str
    venue: str
    categories: List[str]
    created_at: datetime

class SessionCreate(BaseModel):
    start_time: datetime
    end_time: datetime
    capacity: int
    base_price: Decimal

class SessionResponse(BaseModel):
    id: UUID
    event_id: UUID
    start_time: datetime
    end_time: datetime
    capacity: int
    available_seats: int
    base_price: Decimal
    current_price: Decimal

class BookingCreate(BaseModel):
    user_id: UUID
    session_id: UUID
    seats: int

class BookingResponse(BaseModel):
    id: UUID
    user_id: UUID
    session_id: UUID
    seats: int
    price_per_seat: Decimal
    status: str
    created_at: datetime
    confirmed_at: Optional[datetime]
    cancelled_at: Optional[datetime]

# Dependencies
def get_event_service():
    pool = DatabaseConnectionPool.get_instance()
    repository = MariaDBEventRepository(pool)
    return EventService(repository)

def get_booking_service():
    pool = DatabaseConnectionPool.get_instance()
    event_repository = MariaDBEventRepository(pool)
    booking_repository = MariaDBBookingRepository(pool)
    return BookingService(booking_repository, event_repository)

# Event endpoints
@app.post("/events/", response_model=EventResponse)
async def create_event(event: EventCreate, service: EventService = Depends(get_event_service)):
    try:
        created_event = service.create_event(
            name=event.name,
            description=event.description,
            venue=event.venue,
            categories=event.categories
        )
        return created_event
    except EventError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/events/", response_model=List[EventResponse])
async def list_events(category: Optional[str] = None, service: EventService = Depends(get_event_service)):
    try:
        logger.info(f"Fetching events with category: {category}")
        if category:
            events = service.get_events_by_category(category)
        else:
            events = service.event_repository.find_all()
        logger.info(f"Found {len(events)} events")
        return events
    except Exception as e:
        logger.error(f"Error fetching events: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/events/{event_id}", response_model=EventResponse)
async def get_event(event_id: UUID, service: EventService = Depends(get_event_service)):
    event = service.event_repository.find_by_id(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event

@app.post("/events/{event_id}/sessions", response_model=SessionResponse)
async def add_session(
    event_id: UUID,
    session: SessionCreate,
    service: EventService = Depends(get_event_service)
):
    try:
        created_session = service.add_session(
            event_id=event_id,
            start_time=session.start_time,
            end_time=session.end_time,
            capacity=session.capacity,
            base_price=session.base_price
        )
        return created_session
    except EventError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/events/{event_id}/sessions", response_model=List[SessionResponse])
async def list_sessions(event_id: UUID, service: EventService = Depends(get_event_service)):
    try:
        return service.get_available_sessions(event_id)
    except EventError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/events/{event_id}")
async def delete_event(event_id: UUID, service: EventService = Depends(get_event_service)):
    try:
        success = service.delete_event(event_id)
        if success:
            return {"message": "Event deleted successfully"}
        raise HTTPException(status_code=404, detail="Event not found")
    except EventError as e:
        raise HTTPException(status_code=400, detail=str(e))

# Booking endpoints
@app.post("/bookings/", response_model=BookingResponse)
async def create_booking(
    booking: BookingCreate,
    service: BookingService = Depends(get_booking_service)
):
    try:
        created_booking = service.create_booking(
            user_id=booking.user_id,
            session_id=booking.session_id,
            num_seats=booking.seats
        )
        return created_booking
    except BookingError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/bookings/{booking_id}/confirm", response_model=BookingResponse)
async def confirm_booking(
    booking_id: UUID,
    service: BookingService = Depends(get_booking_service)
):
    try:
        return service.confirm_booking(booking_id)
    except BookingError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/bookings/{booking_id}/cancel", response_model=BookingResponse)
async def cancel_booking(
    booking_id: UUID,
    service: BookingService = Depends(get_booking_service)
):
    try:
        return service.cancel_booking(booking_id)
    except BookingError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/bookings/{booking_id}", response_model=BookingResponse)
async def get_booking(
    booking_id: UUID,
    service: BookingService = Depends(get_booking_service)
):
    booking = service.booking_repository.find_by_id(booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    return booking

@app.get("/users/{user_id}/bookings", response_model=List[BookingResponse])
async def list_user_bookings(
    user_id: UUID,
    service: BookingService = Depends(get_booking_service)
):
    return service.booking_repository.find_by_user_id(user_id) 