from fastapi import FastAPI
from fastapi.responses import JSONResponse
from datetime import datetime

app = FastAPI()

@app.get("/")
@app.get("/events")
def events():
    return JSONResponse(
        {
            "success": True,
            "events": [
                {
                    "title": "Tomorrowland 2025",
                    "date": "2025-07-18",
                    "place": "Boom, Belgium",
                    "genre": "Psytrance",
                    "description": "The world's most famous electronic music festival",
                    "url": "https://www.tomorrowland.com",
                    "image": "https://placehold.co/600x400"
                },
                {
                    "title": "Ultra Music Festival 2026",
                    "date": "2026-03-27",
                    "place": "Miami, USA",
                    "genre": "EDM / Psy",
                    "description": "Premier electronic music festival",
                    "url": "https://ultramusicfestival.com",
                    "image": "https://placehold.co/600x400"
                },
                {
                    "title": "Creamfields 2025",
                    "date": "2025-08-22",
                    "place": "Daresbury, UK",
                    "genre": "Electronic",
                    "description": "UK's biggest dance music festival",
                    "url": "https://creamfields.com",
                    "image": "https://placehold.co/600x400"
                }
            ],
            "total": 3,
            "timestamp": datetime.utcnow().isoformat()
        }
    )

@app.get("/api/events")
def events_alias():
    return events()