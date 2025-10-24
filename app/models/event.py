from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime


class EventBase(SQLModel):
    """Base event model with common fields."""
    title: str = Field(max_length=200)
    description: str = Field(max_length=1000)
    event_date: datetime
    location: str = Field(max_length=200)
    organizer: str = Field(max_length=100)
    contact_info: Optional[str] = Field(default=None, max_length=100)
    is_public: bool = Field(default=True)


class Event(EventBase, table=True):
    """Database model for events."""
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class EventCreate(EventBase):
    """Schema for creating events."""
    pass


class EventUpdate(SQLModel):
    """Schema for updating events."""
    title: Optional[str] = Field(default=None, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    event_date: Optional[datetime] = None
    location: Optional[str] = Field(default=None, max_length=200)
    organizer: Optional[str] = Field(default=None, max_length=100)
    contact_info: Optional[str] = Field(default=None, max_length=100)
    is_public: Optional[bool] = None


class EventResponse(EventBase):
    """Schema for event responses."""
    id: int
    created_at: datetime
    updated_at: datetime
