from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.controllers.event_controller import (
    create_event,
    get_event,
    get_events,
    update_event,
    delete_event,
    get_upcoming_events,
    search_events
)
from app.models.event import EventCreate, EventUpdate, EventResponse

router = APIRouter(prefix="/api/v1/events", tags=["events"])


@router.post("/", response_model=EventResponse, status_code=201)
async def create_event_endpoint(
    event: EventCreate,
    db: AsyncSession = Depends(get_db)
) -> EventResponse:
    """Create a new event."""
    return await create_event(db, event)


@router.get("/", response_model=List[EventResponse])
async def get_events_endpoint(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    upcoming_only: bool = Query(True),
    db: AsyncSession = Depends(get_db)
) -> List[EventResponse]:
    """Get all events with optional filtering."""
    return await get_events(db, skip=skip, limit=limit, upcoming_only=upcoming_only)


@router.get("/upcoming", response_model=List[EventResponse])
async def get_upcoming_events_endpoint(
    limit: int = Query(5, ge=1, le=20),
    db: AsyncSession = Depends(get_db)
) -> List[EventResponse]:
    """Get upcoming events for homepage display."""
    return await get_upcoming_events(db, limit=limit)


@router.get("/search", response_model=List[EventResponse])
async def search_events_endpoint(
    q: str = Query(..., min_length=1),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
) -> List[EventResponse]:
    """Search events by title, description, or location."""
    return await search_events(db, search_term=q, skip=skip, limit=limit)


@router.get("/{event_id}", response_model=EventResponse)
async def get_event_endpoint(
    event_id: int,
    db: AsyncSession = Depends(get_db)
) -> EventResponse:
    """Get a specific event by ID."""
    event = await get_event(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@router.put("/{event_id}", response_model=EventResponse)
async def update_event_endpoint(
    event_id: int,
    event_update: EventUpdate,
    db: AsyncSession = Depends(get_db)
) -> EventResponse:
    """Update an existing event."""
    event = await update_event(db, event_id, event_update)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@router.delete("/{event_id}", status_code=204)
async def delete_event_endpoint(
    event_id: int,
    db: AsyncSession = Depends(get_db)
) -> None:
    """Delete an event."""
    success = await delete_event(db, event_id)
    if not success:
        raise HTTPException(status_code=404, detail="Event not found")
