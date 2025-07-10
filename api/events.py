from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import json, os

app = FastAPI()

@app.get("/api/events")
async def get_events(request: Request):
    source = request.query_params.get("source", "clubberia")
    file_path = os.path.join(os.path.dirname(__file__), "data", f"{source}_events.json")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return JSONResponse(content=data)
    except FileNotFoundError:
        return JSONResponse(content={"error": "Source not found."}, status_code=404)