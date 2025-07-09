# api/events.py  ★ここだけ修正★
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from datetime import datetime

app = FastAPI()            # root_path は付けない

# ← 余計な @app.get("/events") は削除
@app.get("/")              # /api/events で呼ばれる
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