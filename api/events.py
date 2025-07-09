from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
import os

# Environment check
is_production = os.getenv("VERCEL") == "1"

# FastAPI app
app = FastAPI(
    title="PsyFinder API",
    version="1.0.0",
    root_path="/api" if is_production else ""
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "message": "PsyFinder API",
        "version": "1.0.0",
        "status": "running",
        "environment": "vercel" if is_production else "development",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "environment": "vercel" if is_production else "development"
    }

@app.get("/events")
def get_events(source: str = "major"):
    """Simple events endpoint with mock data"""
    
    mock_events = [
        {
            "title": "Tomorrowland 2024",
            "date": "2024-07-19",
            "place": "Boom, Belgium", 
            "genre": "Electronic/Psytrance",
            "description": "The world's most famous electronic music festival",
            "url": "https://www.tomorrowland.com",
            "image": "https://images.unsplash.com/photo-1518005020951-eccb49447d0a"
        },
        {
            "title": "Ultra Music Festival",
            "date": "2024-03-24",
            "place": "Miami, USA",
            "genre": "Electronic/EDM", 
            "description": "Premier electronic music festival",
            "url": "https://ultramusicfestival.com",
            "image": "https://images.unsplash.com/photo-1506157786151-b8491531f063"
        },
        {
            "title": "Creamfields",
            "date": "2024-08-23",
            "place": "Daresbury, UK",
            "genre": "Electronic/Dance",
            "description": "UK's biggest dance music festival",
            "url": "https://creamfields.com", 
            "image": "https://images.unsplash.com/photo-1459749411175-04bf5292ceea"
        }
    ]
    
    return JSONResponse(content={
        "success": True,
        "events": mock_events,
        "total": len(mock_events),
        "source": f"mock_{source}",
        "timestamp": datetime.now().isoformat()
    })

# Error handler
@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "detail": str(exc),
            "timestamp": datetime.now().isoformat()
        }
    )