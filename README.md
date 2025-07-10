# PsyFinder 🎵

**Psytrance Event Finder** - ClubberiaからPsytranceイベント情報をスクレイピングして配信するWebアプリケーション

## 🏗️ アーキテクチャ

```
PsyFinder/
├── backend/                 # FastAPI Backend
│   ├── main.py             # FastAPI アプリケーション
│   ├── clubberia_scraper.py # Clubberia スクレイピング
│   ├── psytrance_scraper.py # Psytrance スクレイピング (Legacy)
│   ├── cache.py            # TTL キャッシュ (60分)
│   └── requirements.txt    # Python 依存関係
├── frontend/               # Frontend
│   └── public/
│       ├── index.html      # メインページ
│       ├── styles.css      # スタイル
│       └── app.js          # JavaScript
├── Dockerfile.api          # Backend Dockerfile
├── Dockerfile.frontend     # Frontend Dockerfile
├── docker-compose.yml      # 開発環境
└── README.md              # このファイル
```

## 🚀 クイックスタート

### 1. 開発環境 (Local)

#### Backend (FastAPI)
```bash
# Python依存関係をインストール
cd backend
pip install -r requirements.txt

# サーバー起動
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend (Static Server)
```bash
# フロントエンドを配信 (Python簡易サーバー)
cd frontend/public
python -m http.server 3000
```

### 2. Docker環境

```bash
# 全サービスを起動
docker-compose up --build

# バックグラウンドで起動
docker-compose up -d --build

# ログ確認
docker-compose logs -f

# 停止
docker-compose down
```

## 📡 API エンドポイント

| エンドポイント | メソッド | 説明 |
|---------------|---------|------|
| `/` | GET | API情報 |
| `/events` | GET | Psytranceイベント一覧 |
| `/events?source=clubberia` | GET | Clubberiaからイベント取得 |
| `/events?source=psytrance` | GET | 従来のスクレイピング (Legacy) |
| `/events/refresh` | POST | キャッシュ強制更新 |
| `/cache/info` | GET | キャッシュ情報 |
| `/cache` | DELETE | キャッシュクリア |
| `/health` | GET | ヘルスチェック |

### API使用例

```bash
# Clubberiaからイベント一覧取得 (デフォルト)
curl http://localhost:8000/events
curl http://localhost:8000/events?source=clubberia

# 従来のスクレイピング (Legacy)
curl http://localhost:8000/events?source=psytrance

# 強制更新
curl -X POST http://localhost:8000/events/refresh

# ヘルスチェック
curl http://localhost:8000/health
```

## 🔧 機能

### Backend (FastAPI)
- ✅ **Clubberiaスクレイピング**: BeautifulSoupでPsychedelicイベント情報を抽出
- ✅ **マルチソース対応**: Clubberia + 従来スクレイピング
- ✅ **TTLキャッシュ**: 60分間のメモリキャッシュでパフォーマンス向上
- ✅ **バックグラウンド更新**: 非同期でデータ更新
- ✅ **エラーハンドリング**: フォールバック機能付き
- ✅ **ヘルスチェック**: 監視用エンドポイント

### Frontend 
- ✅ **レスポンシブデザイン**: モバイル対応
- ✅ **リアルタイム検索**: キーワード・場所・ジャンルフィルター
- ✅ **キャッシュ情報表示**: データソース表示
- ✅ **エラーハンドリング**: ユーザーフレンドリーなエラー表示
- ✅ **サイケデリックUI**: ネオンカラー・アニメーション

## 🌐 Cloud Run デプロイ

### 1. Google Cloud 設定

```bash
# Google Cloud SDK インストール・設定
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# Container Registry 有効化
gcloud services enable containerregistry.googleapis.com
gcloud services enable run.googleapis.com
```

### 2. Backend デプロイ

```bash
# イメージビルド・プッシュ
docker build -f Dockerfile.api -t gcr.io/YOUR_PROJECT_ID/psyfinder-api .
docker push gcr.io/YOUR_PROJECT_ID/psyfinder-api

# Cloud Run デプロイ
gcloud run deploy psyfinder-api \
  --image gcr.io/YOUR_PROJECT_ID/psyfinder-api \
  --platform managed \
  --region asia-northeast1 \
  --allow-unauthenticated \
  --memory 512Mi \
  --cpu 1 \
  --timeout 300 \
  --max-instances 10
```

### 3. Frontend デプロイ

```bash
# Frontend用のapp.jsでAPI_BASE_URLを更新
# const API_BASE_URL = 'https://psyfinder-api-xxx.a.run.app';

# フロントエンドイメージビルド・プッシュ
docker build -f Dockerfile.frontend -t gcr.io/YOUR_PROJECT_ID/psyfinder-frontend .
docker push gcr.io/YOUR_PROJECT_ID/psyfinder-frontend

# Cloud Run デプロイ
gcloud run deploy psyfinder-frontend \
  --image gcr.io/YOUR_PROJECT_ID/psyfinder-frontend \
  --platform managed \
  --region asia-northeast1 \
  --allow-unauthenticated \
  --port 80
```

## 🔄 GitHub Actions 日次更新

### `.github/workflows/daily-update.yml`

```yaml
name: Daily Event Update

on:
  schedule:
    - cron: '0 1 * * *'  # 毎日午前1時 (JST 10時)
  workflow_dispatch:      # 手動実行可能

jobs:
  update-events:
    runs-on: ubuntu-latest
    steps:
      - name: Trigger Cache Refresh
        run: |
          curl -X POST \
            -H "Authorization: Bearer ${{ secrets.CLOUD_RUN_TOKEN }}" \
            https://psyfinder-api-xxx.a.run.app/events/refresh

      - name: Health Check
        run: |
          curl -f https://psyfinder-api-xxx.a.run.app/health

  deploy-if-needed:
    runs-on: ubuntu-latest
    if: github.event_name == 'push'
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Google Cloud
        uses: google-github-actions/setup-gcloud@v1
        with:
          service_account_key: ${{ secrets.GCP_SA_KEY }}
          project_id: ${{ secrets.GCP_PROJECT_ID }}

      - name: Configure Docker
        run: gcloud auth configure-docker

      - name: Build and Deploy API
        run: |
          docker build -f Dockerfile.api -t gcr.io/${{ secrets.GCP_PROJECT_ID }}/psyfinder-api .
          docker push gcr.io/${{ secrets.GCP_PROJECT_ID }}/psyfinder-api
          gcloud run deploy psyfinder-api \
            --image gcr.io/${{ secrets.GCP_PROJECT_ID }}/psyfinder-api \
            --platform managed \
            --region asia-northeast1 \
            --allow-unauthenticated
```

### GitHub Secrets 設定

1. GitHub リポジトリ → Settings → Secrets and variables → Actions
2. 以下のシークレットを追加:
   - `GCP_PROJECT_ID`: Google Cloud プロジェクトID
   - `GCP_SA_KEY`: サービスアカウントJSONキー
   - `CLOUD_RUN_TOKEN`: Cloud Run認証トークン（オプション）

## 🧪 テスト

### Backend テスト
```bash
cd backend

# Clubberiaスクレイピングテスト
python clubberia_scraper.py

# 従来スクレイピングテスト  
python psytrance_scraper.py

# キャッシュテスト
python cache.py

# API テスト
uvicorn main:app --reload &
curl http://localhost:8000/health
curl http://localhost:8000/events?source=clubberia
```

### Frontend テスト
```bash
cd frontend/public
python -m http.server 3000

# ブラウザで http://localhost:3000 にアクセス
```

## 📊 監視・ログ

### Cloud Run ログ確認
```bash
# ログストリーミング
gcloud logs tail --follow \
  --filter="resource.type=cloud_run_revision AND resource.labels.service_name=psyfinder-api"

# エラーログのみ
gcloud logs read \
  --filter="resource.type=cloud_run_revision AND resource.labels.service_name=psyfinder-api AND severity>=ERROR"
```

### メトリクス確認
- **Cloud Run**: Google Cloud Console → Cloud Run → psyfinder-api → メトリクス
- **API**: `GET /health` でアプリケーション状態確認
- **キャッシュ**: `GET /cache/info` でキャッシュ状態確認

## 🛠️ 開発

### 新機能追加
1. `backend/clubberia_scraper.py`: Clubberiaサイト対応
2. `backend/psytrance_scraper.py`: 従来スクレイピング (Legacy)
3. `backend/main.py`: 新しいエンドポイント追加
4. `frontend/public/app.js`: UI機能追加

### デバッグ
```bash
# Backend デバッグモード
uvicorn main:app --reload --log-level debug

# Frontend ローカルプロキシ (CORS回避)
# package.json に以下追加:
# "proxy": "http://localhost:8000"
```

## 📈 パフォーマンス最適化

### Backend
- **キャッシュ戦略**: TTL 60分で適切なバランス
- **バックグラウンド更新**: ユーザー待機時間を最小化
- **エラーフォールバック**: 可用性を最大化

### Frontend
- **画像遅延読み込み**: `loading="lazy"` 属性
- **CDN活用**: 静的ファイルの配信最適化
- **圧縮**: gzip/Brotli圧縮でファイルサイズ削減

## 🚨 トラブルシューティング

### よくある問題

1. **スクレイピング失敗**
   - User-Agentヘッダー確認
   - Clubberiaサイト構造変更の可能性
   - ネットワーク接続確認
   - `?source=psytrance` で従来スクレイピングを試す

2. **CORS エラー**
   - Frontend の `API_BASE_URL` 確認
   - Backend の CORS設定確認

3. **キャッシュ問題**
   - `/cache/info` でキャッシュ状態確認
   - 必要に応じて `/cache` DELETE でクリア

## 📄 ライセンス

MIT License

## 🤝 コントリビューション

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

---

**PsyFinder** - あなたの次のPsytranceイベントを見つけよう! 🎵✨