from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from typing import List, Optional
from datetime import datetime
from fastapi import HTTPException

from app.models.event import Event, EventCreate, EventUpdate, EventResponse


async def create_event(db: AsyncSession, event: EventCreate) -> EventResponse:
    """Create a new event."""
    db_event = Event(
        title=event.title,
        description=event.description,
        event_date=event.event_date,
        location=event.location,
        organizer=event.organizer,
        contact_info=event.contact_info,
        is_public=event.is_public
    )
    
    db.add(db_event)
    await db.commit()
    await db.refresh(db_event)
    
    return EventResponse.model_validate(db_event)


async def get_event(db: AsyncSession, event_id: int) -> Optional[EventResponse]:
    """Get a specific event by ID."""
    result = await db.execute(select(Event).where(Event.id == event_id))
    event = result.scalar_one_or_none()
    
    if not event:
        return None
    
    return EventResponse.model_validate(event)


async def get_events(
    db: AsyncSession, 
    skip: int = 0, 
    limit: int = 100,
    upcoming_only: bool = True
) -> List[EventResponse]:
    """Get all events with optional filtering."""
    query = select(Event)
    
    if upcoming_only:
        query = query.where(Event.event_date >= datetime.utcnow())
    
    query = query.order_by(Event.event_date.asc()).offset(skip).limit(limit)
    
    result = await db.execute(query)
    events = result.scalars().all()
    
    return [EventResponse.model_validate(event) for event in events]


async def update_event(
    db: AsyncSession, 
    event_id: int, 
    event_update: EventUpdate
) -> Optional[EventResponse]:
    """Update an existing event."""
    result = await db.execute(select(Event).where(Event.id == event_id))
    event = result.scalar_one_or_none()
    
    if not event:
        return None
    
    # Update only provided fields
    update_data = event_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(event, field, value)
    
    event.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(event)
    
    return EventResponse.model_validate(event)


async def delete_event(db: AsyncSession, event_id: int) -> bool:
    """Delete an event."""
    result = await db.execute(select(Event).where(Event.id == event_id))
    event = result.scalar_one_or_none()
    
    if not event:
        return False
    
    await db.delete(event)
    await db.commit()
    
    return True


async def get_upcoming_events(db: AsyncSession, limit: int = 5) -> List[EventResponse]:
    """Get upcoming events for homepage display."""
    return await get_events(db, skip=0, limit=limit, upcoming_only=True)


async def search_events(
    db: AsyncSession, 
    search_term: str,
    skip: int = 0,
    limit: int = 20
) -> List[EventResponse]:
    """Search events by title, description, or location."""
    query = select(Event).where(
        (Event.title.contains(search_term)) |
        (Event.description.contains(search_term)) |
        (Event.location.contains(search_term))
    ).order_by(Event.event_date.asc()).offset(skip).limit(limit)
    
    result = await db.execute(query)
    events = result.scalars().all()
    
    return [EventResponse.model_validate(event) for event in events]
