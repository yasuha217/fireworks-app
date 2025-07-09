from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

# 最小限のFastAPIアプリ
app = FastAPI(title="PsyFinder Test API")

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "message": "PsyFinder Test API is working!",
        "timestamp": datetime.now().isoformat(),
        "status": "ok"
    }

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/test")
def test_endpoint():
    return {
        "test": "success",
        "message": "This is a test endpoint",
        "timestamp": datetime.now().isoformat()
    }