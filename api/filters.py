"""
PsyFinder イベントフィルタ機能
Psy系キーワードに基づいてイベントをフィルタリング
"""

import re
from typing import List

# Psy系キーワードリスト
ALLOWED_KEYWORDS = [
    "psy", "psychedelic", "goa", "forest", "フルオン", "サイケ", 
    "ハイテック", "psybient", "サイビエント", "trance", "トランス",
    "psytrance", "progressive", "プログレッシブ", "hitech", "darkpsy",
    "full-on", "minimal", "ミニマル", "ambient", "アンビエント"
]

def is_psy_event(text: str) -> bool:
    """
    テキストがPsy系イベントかどうかを判定
    
    Args:
        text: イベントのタイトル、説明、会場情報などのテキスト
        
    Returns:
        bool: Psy系キーワードを含む場合True
    """
    if not text:
        return False
    
    # テキストを小文字に変換
    lowered = text.lower()
    
    # キーワードマッチング
    for keyword in ALLOWED_KEYWORDS:
        if keyword.lower() in lowered:
            return True
    
    return False

def is_psy_event_strict(event_data: dict) -> bool:
    """
    より厳密なPsy系イベント判定
    タイトル、説明、ジャンル、会場情報を総合的に判定
    
    Args:
        event_data: イベントデータ辞書
        
    Returns:
        bool: Psy系イベントの場合True
    """
    # 検査対象のテキストを結合
    text_parts = [
        event_data.get('title', ''),
        event_data.get('description', ''),
        event_data.get('genre', ''),
        event_data.get('place', '')
    ]
    
    combined_text = ' '.join(text_parts)
    
    # 基本的なPsy判定
    if is_psy_event(combined_text):
        return True
    
    # 除外キーワードをチェック（より厳密な判定のため）
    exclude_keywords = [
        'jpop', 'j-pop', 'jazz', 'rock', 'punk', 'metal', 'classical',
        '演歌', 'カラオケ', 'アイドル', 'ポップス'
    ]
    
    lowered_text = combined_text.lower()
    for exclude in exclude_keywords:
        if exclude.lower() in lowered_text:
            return False
    
    return False

def filter_psy_events(events: List[dict]) -> List[dict]:
    """
    イベントリストからPsy系イベントのみをフィルタリング
    
    Args:
        events: イベントデータのリスト
        
    Returns:
        List[dict]: Psy系イベントのみのリスト
    """
    psy_events = []
    
    for event in events:
        # 厳密な判定を使用
        if is_psy_event_strict(event):
            psy_events.append(event)
    
    return psy_events

def get_keyword_matches(text: str) -> List[str]:
    """
    テキスト内で見つかったPsy系キーワードのリストを返す
    デバッグ用
    
    Args:
        text: 検査対象のテキスト
        
    Returns:
        List[str]: 見つかったキーワードのリスト
    """
    if not text:
        return []
    
    lowered = text.lower()
    matches = []
    
    for keyword in ALLOWED_KEYWORDS:
        if keyword.lower() in lowered:
            matches.append(keyword)
    
    return matches


# テスト用関数
if __name__ == "__main__":
    # テストケース
    test_events = [
        {
            'title': 'Psychedelic Trance Night',
            'description': 'Progressive psytrance event',
            'genre': 'Psytrance',
            'place': 'WOMB, Tokyo'
        },
        {
            'title': 'J-POP Night',
            'description': 'Japanese pop music event',
            'genre': 'J-Pop',
            'place': 'Karaoke Bar'
        },
        {
            'title': 'Goa Trance Classics',
            'description': 'Old school goa trance',
            'genre': 'Goa',
            'place': 'Underground Club'
        },
        {
            'title': 'Jazz Night',
            'description': 'Smooth jazz evening',
            'genre': 'Jazz',
            'place': 'Jazz Bar'
        }
    ]
    
    print("=== Psy Filter Test ===")
    for event in test_events:
        combined = f"{event['title']} {event['description']} {event['genre']}"
        is_psy = is_psy_event_strict(event)
        keywords = get_keyword_matches(combined)
        
        print(f"Event: {event['title']}")
        print(f"  Is Psy: {is_psy}")
        print(f"  Keywords: {keywords}")
        print()
    
    print("=== Filtered Results ===")
    psy_events = filter_psy_events(test_events)
    print(f"Original events: {len(test_events)}")
    print(f"Psy events: {len(psy_events)}")
    for event in psy_events:
        print(f"  - {event['title']}")