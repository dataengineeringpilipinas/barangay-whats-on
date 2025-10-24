from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import os

from app.database import init_db
from app.routes.event_routes import router as event_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan."""
    # Startup
    await init_db()
    print("Database initialized successfully!")
    yield
    # Shutdown
    print("Application shutting down...")


# Create FastAPI application
app = FastAPI(
    title="What's On in our Barangay?",
    description="Community event management system for barangay residents",
    version="1.0.0",
    lifespan=lifespan
)

# Mount static files (if any)
# app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="app/templates")

# Include API routes
app.include_router(event_router)


# Frontend routes
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Homepage with upcoming events."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/events", response_class=HTMLResponse)
async def events_page(request: Request):
    """Events listing page."""
    return templates.TemplateResponse("events.html", {"request": request})


@app.get("/events/new", response_class=HTMLResponse)
async def new_event_page(request: Request):
    """New event form page."""
    return templates.TemplateResponse("new_event.html", {"request": request})


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "message": "What's On in our Barangay is running!"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
