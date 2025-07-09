from fastapi import FastAPI
from fastapi.responses import JSONResponse
from datetime import datetime

app = FastAPI()

@app.get("/")
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
                    "image": "https://placehold.co/600x400"
                }
            ],
            "total": 1,
            "timestamp": datetime.utcnow().isoformat()
        }
    )