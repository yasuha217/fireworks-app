import time
from typing import Any, Optional, Dict
import threading
from datetime import datetime, timedelta

class TTLCache:
    """
    TTL (Time To Live) 機能付きメモリキャッシュ
    60分でキャッシュが期限切れになる
    """
    
    def __init__(self, default_ttl: int = 3600):  # デフォルト60分 = 3600秒
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.RLock()
        self.default_ttl = default_ttl
    
    def get(self, key: str) -> Optional[Any]:
        """
        キーに対応する値を取得
        期限切れの場合はNoneを返す
        """
        with self._lock:
            if key not in self._cache:
                return None
            
            item = self._cache[key]
            
            # TTLチェック
            if time.time() > item['expires_at']:
                del self._cache[key]
                return None
            
            # アクセス時間を更新
            item['last_accessed'] = time.time()
            return item['value']
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        キーと値をキャッシュに保存
        """
        if ttl is None:
            ttl = self.default_ttl
        
        with self._lock:
            expires_at = time.time() + ttl
            self._cache[key] = {
                'value': value,
                'expires_at': expires_at,
                'created_at': time.time(),
                'last_accessed': time.time()
            }
    
    def delete(self, key: str) -> bool:
        """
        指定されたキーをキャッシュから削除
        """
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False
    
    def clear(self) -> None:
        """
        キャッシュをクリア
        """
        with self._lock:
            self._cache.clear()
    
    def cleanup_expired(self) -> int:
        """
        期限切れのアイテムを削除
        削除したアイテム数を返す
        """
        current_time = time.time()
        expired_keys = []
        
        with self._lock:
            for key, item in self._cache.items():
                if current_time > item['expires_at']:
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self._cache[key]
        
        return len(expired_keys)
    
    def get_stats(self) -> Dict[str, Any]:
        """
        キャッシュの統計情報を取得
        """
        with self._lock:
            current_time = time.time()
            total_items = len(self._cache)
            expired_items = sum(1 for item in self._cache.values() 
                              if current_time > item['expires_at'])
            valid_items = total_items - expired_items
            
            return {
                'total_items': total_items,
                'valid_items': valid_items,
                'expired_items': expired_items,
                'cache_keys': list(self._cache.keys())
            }
    
    def has_valid_cache(self, key: str) -> bool:
        """
        指定されたキーに有効なキャッシュが存在するかチェック
        """
        with self._lock:
            if key not in self._cache:
                return False
            
            item = self._cache[key]
            return time.time() <= item['expires_at']


class EventCache:
    """
    イベント専用のキャッシュクラス
    """
    
    def __init__(self):
        self.cache = TTLCache(default_ttl=3600)  # 60分
        self.events_key = "psytrance_events"
        self.last_update_key = "last_update"
    
    def get_events(self, source: str = "psytrance", ttl: int = 21600) -> Optional[list]:
        """
        キャッシュからイベントリストを取得
        sourceが指定された場合は、該当するスクレイパーを使用
        
        Args:
            source: データソース ("clubberia", "psytrance")
            ttl: キャッシュのTTL秒数 (デフォルト21600秒=6時間)
        """
        if source == "clubberia":
            # Clubberiaソース専用のキャッシュキー
            clubberia_key = f"clubberia_events"
            
            # キャッシュの有効性をチェック
            if self.cache.has_valid_cache(clubberia_key):
                cached_events = self.cache.get(clubberia_key)
                if cached_events:
                    return cached_events
            
            # キャッシュが無効な場合、新しくスクレイピング
            try:
                from clubberia_scraper import ClubberScraper
                scraper = ClubberScraper()
                fresh_events = scraper.scrape_clubberia()
                
                # カスタムTTLでキャッシュに保存
                self.cache.set(clubberia_key, fresh_events, ttl=ttl)
                
                return fresh_events
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.exception("Scraping failed: %s", e)
                raise
        
        # 従来のpsytranceソース
        return self.cache.get(self.events_key)
    
    def set_events(self, events: list) -> None:
        """
        イベントリストをキャッシュに保存
        """
        self.cache.set(self.events_key, events)
        self.cache.set(self.last_update_key, datetime.now().isoformat())
    
    def get_last_update(self) -> Optional[str]:
        """
        最後の更新時間を取得
        """
        return self.cache.get(self.last_update_key)
    
    def clear_events(self) -> None:
        """
        イベントキャッシュをクリア
        """
        self.cache.delete(self.events_key)
        self.cache.delete(self.last_update_key)
    
    def is_cache_valid(self) -> bool:
        """
        キャッシュが有効かどうかチェック
        """
        return self.cache.has_valid_cache(self.events_key)
    
    def get_cache_info(self) -> Dict[str, Any]:
        """
        キャッシュ情報を取得
        """
        stats = self.cache.get_stats()
        last_update = self.get_last_update()
        
        cache_age = None
        if last_update:
            try:
                update_time = datetime.fromisoformat(last_update)
                cache_age = (datetime.now() - update_time).total_seconds()
            except:
                pass
        
        return {
            'is_valid': self.is_cache_valid(),
            'last_update': last_update,
            'cache_age_seconds': cache_age,
            'cache_stats': stats
        }


# グローバルキャッシュインスタンス
event_cache = EventCache()

# 使用例
if __name__ == "__main__":
    # TTLキャッシュのテスト
    cache = TTLCache(default_ttl=5)  # 5秒でテスト
    
    print("=== TTL Cache Test ===")
    cache.set("test_key", "test_value")
    print(f"Immediate get: {cache.get('test_key')}")
    
    time.sleep(3)
    print(f"After 3 seconds: {cache.get('test_key')}")
    
    time.sleep(3)
    print(f"After 6 seconds (expired): {cache.get('test_key')}")
    
    # イベントキャッシュのテスト
    print("\n=== Event Cache Test ===")
    event_cache = EventCache()
    
    test_events = [
        {'title': 'Test Event 1', 'date': '2025/08/01'},
        {'title': 'Test Event 2', 'date': '2025/08/02'}
    ]
    
    event_cache.set_events(test_events)
    print(f"Cached events: {len(event_cache.get_events())}")
    print(f"Cache info: {event_cache.get_cache_info()}")