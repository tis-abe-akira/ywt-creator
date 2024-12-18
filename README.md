# 改善施策管理API

改善施策の提案、評価、開発、リリースを管理するためのRESTful APIアプリケーションです。

## 概要

このアプリケーションは以下の機能を提供します：

- 改善施策の管理 (`/initiatives`)
- 用語の管理 (`/terms`)
- 開発状況の管理 (`/development`)
- リリース管理 (`/releases`)

## 必要要件

- Python 3.x
- 以下のPythonパッケージ:
  - fastapi >= 0.104.1
  - uvicorn >= 0.24.0
  - sqlalchemy >= 2.0.23
  - pydantic >= 2.5.2
  - pytest >= 7.4.3
  - httpx >= 0.25.2
  - python-multipart >= 0.0.6
  - python-jose[cryptography] >= 3.3.0
  - passlib[bcrypt] >= 1.7.4
  - python-dateutil >= 2.8.2

## セットアップ

1. 依存パッケージのインストール:
```bash
pip install -r src/requirements.txt
```

2. アプリケーションの実行:
```bash
cd src
python run.py
```

アプリケーションは `http://0.0.0.0:8000` で起動します。

## API ドキュメント

アプリケーション起動後、以下のURLでSwagger UIによるAPI仕様を確認できます：

- Swagger UI: `http://0.0.0.0:8000/docs`
- ReDoc: `http://0.0.0.0:8000/redoc`

## エンドポイント一覧

- `/`: ウェルカムメッセージ
- `/initiatives`: 改善施策の管理
- `/terms`: 用語の管理
- `/development`: 開発状況の管理
- `/releases`: リリース管理

各エンドポイントの詳細な使用方法については、Swagger UIのドキュメントを参照してください。

## テスト実行

プロジェクトのテストを実行するには：

```bash
cd src
pytest
