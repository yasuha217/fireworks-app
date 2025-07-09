from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Dict, Optional
import logging
from datetime import datetime
import asyncio
import os

from psytrance_scraper import PsytranceScraper
from cache import event_cache

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Vercel deployment support
is_production = os.getenv("VERCEL") == "1"

# FastAPIアプリケーション初期化
app = FastAPI(
    title="PsyFinder API",
    description="Psytrance Event Finder API - iFLYER scraping service",
    version="1.0.0",
    root_path="/api" if is_production else ""
)

# CORS設定
allowed_origins = [
    "http://localhost:8006",
    "http://localhost:5173", 
    "https://*.vercel.app"
]

if is_production:
    # Production - allow Vercel domains
    allowed_origins.extend([
        "https://psyfinder.vercel.app",
        "https://psyfinder-*.vercel.app"
    ])
else:
    # Development - allow localhost
    allowed_origins.append("*")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["*"],
)

# グローバル変数
scraper = PsytranceScraper()
is_scraping = False

@app.get("/")
async def root():
    """
    ルートエンドポイント - API情報を返す
    """
    return {
        "message": "PsyFinder API",
        "version": "1.0.0",
        "description": "Psytrance events from Tokyo, Japan",
        "endpoints": {
            "/events": "Get psytrance events",
            "/events?source=clubberia": "Get Clubberia events",
            "/events?source=major": "Get major festivals",
            "/events/refresh": "Force refresh events cache",
            "/cache/info": "Get cache information",
            "/health": "Health check"
        }
    }

@app.get("/events")
async def get_events(
    background_tasks: BackgroundTasks,
    force_refresh: bool = False,
    source: str = "clubberia",
    genre: str = "psy"
) -> Dict:
    """
    Psytranceイベント一覧を取得
    
    Args:
        force_refresh: キャッシュを無視して強制的に再取得する場合はTrue
        source: データソース ("clubberia", "psytrance")
        genre: ジャンルフィルタ ("psy", "all")
    
    Returns:
        イベント一覧とメタデータ
    """
    try:
        # Major Festivalsソースの場合
        if source == "major":
            from major_fests_scraper import MajorFestsScraper
            scraper = MajorFestsScraper()
            events = scraper.scrape_major_festivals()
            
            logger.info(f"Returning {len(events)} major festivals")
            data = {
                "success": True,
                "events": events,
                "total": len(events),
                "source": "major_festivals",
                "timestamp": datetime.now().isoformat()
            }
            return JSONResponse(content=data)
        
        # Clubberiaソースの場合は直接スクレイピング
        if source == "clubberia":
            events = event_cache.get_events(source="clubberia", ttl=21600)  # 6時間キャッシュ
            
            # ジャンルフィルタリング
            if genre == "psy":
                from filters import filter_psy_events, is_psy_event_strict
                
                # 二段階フィルタリング
                # 1. 基本的なPsy系フィルタ
                initial_filtered = filter_psy_events(events)
                
                # 2. より厳密なフィルタ（"Unknown"ジャンルなど除外）
                final_filtered = []
                for event in initial_filtered:
                    # タイトルやジャンルでPsy系を確認
                    if (event.get('genre', '').lower() in ['unknown', 'other'] and 
                        not is_psy_event_strict(event)):
                        continue  # 除外
                    final_filtered.append(event)
                
                logger.info(f"Filtered {len(events)} events to {len(final_filtered)} Psy events")
                events = final_filtered
            
            logger.info(f"Returning {len(events)} events from Clubberia")
            data = {
                "success": True,
                "events": events,
                "total": len(events),
                "source": "clubberia",
                "genre_filter": genre,
                "timestamp": datetime.now().isoformat()
            }
            return JSONResponse(content=data)
        
        # 従来のPsytranceスクレイピング（キャッシュあり）
        if not force_refresh and event_cache.is_cache_valid():
            events = event_cache.get_events()
            cache_info = event_cache.get_cache_info()
            
            logger.info(f"Returning {len(events)} events from cache")
            data = {
                "success": True,
                "events": events,
                "total": len(events),
                "source": "cache",
                "cache_info": cache_info,
                "timestamp": datetime.now().isoformat()
            }
            return JSONResponse(content=data)
        
        # キャッシュが無効または強制更新の場合、バックグラウンドでスクレイピング
        if not is_scraping:
            background_tasks.add_task(scrape_and_cache_events)
        
        # 既存のキャッシュがある場合はそれを返す（古くても）
        cached_events = event_cache.get_events()
        if cached_events:
            logger.info(f"Returning {len(cached_events)} events from expired cache while refreshing")
            return {
                "success": True,
                "events": cached_events,
                "total": len(cached_events),
                "source": "cache_expired",
                "message": "Refreshing in background",
                "cache_info": event_cache.get_cache_info(),
                "timestamp": datetime.now().isoformat()
            }
        
        # キャッシュが全くない場合は同期的にスクレイピング
        logger.info("No cache available, scraping synchronously")
        events = scraper.scrape_psytrance_events()
        event_cache.set_events(events)
        
        data = {
            "success": True,
            "events": events,
            "total": len(events),
            "source": "fresh_scrape",
            "cache_info": event_cache.get_cache_info(),
            "timestamp": datetime.now().isoformat()
        }
        return JSONResponse(content=data)
        
    except Exception as e:
        logger.error(f"Error in get_events: {e}")
        
        # エラー時はキャッシュから古いデータを返すか、モックデータを返す
        cached_events = event_cache.get_events()
        if cached_events:
            return {
                "success": True,
                "events": cached_events,
                "total": len(cached_events),
                "source": "cache_fallback",
                "warning": f"Error occurred: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
        
        # 最後の手段：モックデータ
        mock_events = scraper._get_mock_events()
        data = {
            "success": True,
            "events": mock_events,
            "total": len(mock_events),
            "source": "mock_fallback",
            "warning": f"Error occurred, returning mock data: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return JSONResponse(content=data)

@app.post("/events/refresh")
async def refresh_events(background_tasks: BackgroundTasks):
    """
    イベントキャッシュを強制的に更新
    """
    try:
        background_tasks.add_task(scrape_and_cache_events)
        
        return {
            "success": True,
            "message": "Cache refresh started in background",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error in refresh_events: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/cache/info")
async def get_cache_info():
    """
    キャッシュ情報を取得
    """
    try:
        return {
            "success": True,
            "cache_info": event_cache.get_cache_info(),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error in get_cache_info: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/cache")
async def clear_cache():
    """
    キャッシュをクリア
    """
    try:
        event_cache.clear_events()
        return {
            "success": True,
            "message": "Cache cleared successfully",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error in clear_cache: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """
    ヘルスチェックエンドポイント
    """
    try:
        cache_valid = event_cache.is_cache_valid()
        events_count = len(event_cache.get_events() or [])
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "cache_valid": cache_valid,
            "events_cached": events_count,
            "scraping_active": is_scraping
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )

async def scrape_and_cache_events():
    """
    バックグラウンドでイベントをスクレイピングしてキャッシュに保存
    """
    global is_scraping
    
    if is_scraping:
        logger.info("Scraping already in progress, skipping")
        return
    
    try:
        is_scraping = True
        logger.info("Starting background scraping...")
        
        # 非同期でスクレイピング実行
        loop = asyncio.get_event_loop()
        events = await loop.run_in_executor(None, scraper.scrape_psytrance_events)
        
        # キャッシュに保存
        event_cache.set_events(events)
        
        logger.info(f"Background scraping completed, cached {len(events)} events")
        
    except Exception as e:
        logger.error(f"Background scraping failed: {e}")
    finally:
        is_scraping = False

@app.on_event("startup")
async def startup_event():
    """
    アプリケーション起動時の処理
    """
    logger.info("PsyFinder API starting up...")
    
    # 起動時に初回スクレイピングを実行（エラーは無視）
    try:
        await scrape_and_cache_events()
        logger.info("Initial scraping completed")
    except Exception as e:
        logger.warning(f"Initial scraping failed, will use fallback data: {e}")

@app.on_event("shutdown") 
async def shutdown_event():
    """
    アプリケーション終了時の処理
    """
    logger.info("PsyFinder API shutting down...")

# エラーハンドラー
@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """
    一般的な例外ハンドラー
    """
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "detail": str(exc),
            "timestamp": datetime.now().isoformat()
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )