# ywt-creator

複数のペルソナによるYWT分析を行うPythonプロジェクト

## プロジェクト構造

```
ywt-creator/
  ├── src/
  │   └── main.py      # メインのプログラムファイル
  ├── .env             # 環境変数設定ファイル
  ├── pyproject.toml   # プロジェクト設定ファイル
  └── README.md        # プロジェクトの説明
```

## 必要なもの

- Python 3.11以上
- OpenAI APIキー

## セットアップ

1. 仮想環境のアクティベート:
```bash
source .venv/bin/activate
```

2. 依存関係のインストール:
```bash
uv add pydantic langchain-core langchain-openai langgraph python-dotenv
```

3. OpenAI APIキーの設定:
`.env`ファイルを作成し、あなたのAPIキーを設定してください：
```
OPENAI_API_KEY=your_api_key_here
```

## 使用方法

以下のコマンドで、指定したトピックについてのYWT分析を実行できます：

```bash
uv run python src/main.py --topic "分析したいトピック"
```

例：
```bash
uv run python src/main.py --topic "プログラミング学習"
```

指示文章が長い場合には、ファイル `task.txt` に書いて、そのファイルを引数に指定する。

```bash
cat task.txt
uv run python src/main.py --topic "$(cat task.txt)"
```

## 機能

- 指定したトピックに対して5つの異なるペルソナを自動生成
- 各ペルソナの視点でYWT（やったこと、わかったこと、つぎにやること）分析を実行
- 構造化されたデータモデルによる分析結果の整理
- LangGraphを使用した効率的なワークフロー管理

## 開発環境

- Python 3.11.6
- uv 0.4.30
- GPT-4 (OpenAI API)
