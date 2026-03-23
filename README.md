# TsumuGraph

> **🇯🇵 日本語** | [English](#tsumugraph-1)

TsumuGraphは、科学的知識をClaim中心グラフとして表現し、分野横断的な概念的つながりを探索するプロトタイププラットフォームです。

現在のプロトタイプは、熱力学、統計力学、情報理論、量子情報理論、アルゴリズム情報理論にまたがるエントロピー関連概念に焦点を当てています。

## 現在の状態

本リポジトリは、すべてのコアサブシステムが実装・テスト済みの動作するフルスタックプロトタイプです。

- **バックエンド**: FastAPI + SQLAlchemy、12サービス、9 APIルートグループ、JWT認証、イベントストア、OpenAI/Anthropicアダプター付きAIリンキングエージェント。69テスト通過。
- **フロントエンド**: Next.js 15 + React 19 + Tailwind CSS、SSRとクライアントサイド作成/レビューフローを備えた10ページ、ライブバックエンドAPIに接続。
- **CLI**: Typerベースのコマンドラインクライアント、6コマンドグループ。
- **Docker**: PostgreSQL 16、バックエンド、フロントエンドコンテナを含むDocker Composeセットアップ。

## プロジェクトの目的

科学的概念は、異なる分野で異なる名前、仮定、形式体系のもとに現れることがあります。TsumuGraphは、Claim、Context、Evidence、分野横断的接続をファーストクラスオブジェクトとして扱うことで、それらの関係を検査可能にすることを目指しています。

本プロトタイプは以下をサポートするよう設計されています：

- Claim中心の知識表現
- 記述の明示的な文脈化
- エビデンスに紐づくレビュー・提案ワークフロー
- AIによる分野横断的概念リンクの発見

## リポジトリ構成

```text
backend/     FastAPI + SQLAlchemyバックエンド（12サービス、9 APIルート、69テスト）
frontend/    Next.js 15フロントエンド（10ページ、20コンポーネント）
cli/         Typerベースコマンドラインインターフェース（6コマンドグループ）
openspec/    OpenSpec仕様書（9サブシステム）
docs/        プロジェクトドキュメント
```

## はじめに

### バックエンド

必要要件：

- Python 3.11+

セットアップ：

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate      # Windows
# source .venv/bin/activate  # Linux/macOS
pip install -e .[dev]
```

デモデータセットの投入と管理者ユーザーの作成：

```bash
python manage.py seed
python manage.py create-admin
```

テスト実行：

```bash
python -m pytest tests
```

APIサーバー起動：

```bash
python manage.py serve
# または: uvicorn app.main:app --reload
```

LLMによる接続提案を有効にするには、プロバイダーを設定してください：

```bash
# OpenAI
LLM_PROVIDER=openai
OPENAI_API_KEY=
LLM_MODEL=gpt-4o

# Anthropic
# LLM_PROVIDER=anthropic
# ANTHROPIC_API_KEY=
# LLM_MODEL=claude-sonnet-4-20250514

LLM_TEMPERATURE=0.3
LLM_MAX_TOKENS=4096
LLM_TIMEOUT_SECONDS=60
```

LLM APIキーが設定されていない場合、バックエンドは正常に起動しますが、`POST /api/v1/agent/suggest-connections` は `503`（`llm_unavailable`）を返します。

### フロントエンド

必要要件：

- Node.js 20+

セットアップ：

```bash
cd frontend
npm install
npm run dev
```

フロントエンドはデフォルトで `http://localhost:8000` のバックエンドに接続します。
サーバーサイド認証用に `CS_API_TOKEN` を有効なJWTに設定してください（バックエンドディレクトリで `python manage.py create-admin` を実行して取得）。

現在のWeb UIは以下をサポートしています：

- モーダルダイアログからのClaim、Concept、Context、Evidenceの作成
- Claim詳細ページからのAI接続提案の手動トリガー
- トーストフィードバックと自動更新による提案のインプレースレビュー

### Docker Compose（フルスタック）

Docker Composeでスタック全体を実行：

```bash
docker compose up --build
```

これにより、PostgreSQL、バックエンドAPI（ポート8000）、フロントエンド（ポート3000）が起動します。

### デモデータセット

エントロピー中心のデモデータセットを投入：

```bash
cd backend
python manage.py seed
```

投入されるデータセットの内容：

- 6 Context（5分野 + 分野横断）
- 9 Term、7 Concept
- 120 Claim
- 33 Evidence
- 4 分野横断接続
- 3 CIR例

詳細は [デモデータセット](docs/demo-dataset.md) を参照してください。

## ドキュメント

- [アーキテクチャ](docs/architecture.md) — システム設計とコンポーネント概要
- [デモデータセット](docs/demo-dataset.md) — エントロピーテーマのシードデータ説明
- [ロードマップ](docs/roadmap.md) — 現在の状態と今後の計画
- [品質監査](docs/quality-audit.md) — 現在の不具合サマリーと修正優先度
- [仕様書インデックス](docs/specs-index.md) — 全サブシステムのOpenSpecドキュメント
- [並行開発ガイド](parallel_dev_guide.md) — マルチエージェント並行開発セットアップ
- [エージェント割り当て](docs/agent-assignments.md) — エージェントの役割、ファイル所有権、衝突マップ
- [コントリビューティング](CONTRIBUTING.md)
- [セキュリティ](SECURITY.md)
- [行動規範](CODE_OF_CONDUCT.md)

## OpenSpec

リポジトリには `openspec/specs/` 配下に仕様書が含まれています。これらのドキュメントは9つのサブシステム（knowledge-graph、event-store、trust-model、proposal-review、linking-agent、rest-api、cli、web-ui、demo-dataset）の意図された動作を記述しており、開発プロセスの一部です。

## 設定

`.env.example` を `.env` にコピーし、必要に応じて値を調整してください：

```bash
# バックエンド
DATABASE_URL=sqlite:///./tsumu_graph.db
JWT_SECRET=change-me-in-production
CORS_ORIGINS=http://localhost:3000
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
LLM_TEMPERATURE=0.3
LLM_MAX_TOKENS=4096
LLM_TIMEOUT_SECONDS=60

# フロントエンド
NEXT_PUBLIC_API_URL=http://localhost:8000
CS_API_TOKEN=
```

## 公開リポジトリに関する注意事項

この公開リポジトリは、内部提案書草稿、エージェント運用ディレクトリ、ローカル開発アーティファクトを意図的に今後の追跡対象から除外しています。

## ライセンス

本リポジトリはApache License 2.0の下でライセンスされています。[LICENSE](LICENSE) を参照してください。

---

# TsumuGraph

> **🇬🇧 English** | [日本語](#tsumugraph)

TsumuGraph is a prototype platform for representing scientific knowledge as a claim-centered graph and exploring conceptual links across disciplines.

The current prototype focuses on entropy-related concepts across thermodynamics, statistical mechanics, information theory, quantum information theory, and algorithmic information theory.

## Status

This repository is a working full-stack prototype with all core subsystems implemented and tested.

- **Backend**: FastAPI + SQLAlchemy with 12 services, 9 API route groups, JWT auth, event store, and AI linking agent with OpenAI/Anthropic adapters. 69 tests passing.
- **Frontend**: Next.js 15 + React 19 + Tailwind CSS, 10 pages with SSR and client-side creation/review flows connected to the live backend API.
- **CLI**: Typer-based command-line client with 6 command groups.
- **Docker**: Docker Compose setup with PostgreSQL 16, backend, and frontend containers.

## Why This Project Exists

Scientific concepts often appear under different names, assumptions, and formal systems in different fields. TsumuGraph aims to make those relationships inspectable by treating claims, contexts, evidence, and cross-field connections as first-class objects.

The prototype is designed to support:

- claim-centered knowledge representation
- explicit contextualization of statements
- evidence-linked review and proposal workflows
- AI-assisted discovery of cross-field conceptual links

## Repository Structure

```text
backend/     FastAPI + SQLAlchemy backend (12 services, 9 API routes, 69 tests)
frontend/    Next.js 15 frontend (10 pages, 20 components)
cli/         Typer-based command-line interface (6 command groups)
openspec/    OpenSpec specification documents (9 subsystems)
docs/        Project documentation
```

## Getting Started

### Backend

Requirements:

- Python 3.11+

Setup:

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate      # Windows
# source .venv/bin/activate  # Linux/macOS
pip install -e .[dev]
```

Seed the demo dataset and create an admin user:

```bash
python manage.py seed
python manage.py create-admin
```

Run tests:

```bash
python -m pytest tests
```

Run the API server:

```bash
python manage.py serve
# or: uvicorn app.main:app --reload
```

To enable real LLM-backed connection suggestions, configure one provider:

```bash
# OpenAI
LLM_PROVIDER=openai
OPENAI_API_KEY=
LLM_MODEL=gpt-4o

# Anthropic
# LLM_PROVIDER=anthropic
# ANTHROPIC_API_KEY=
# LLM_MODEL=claude-sonnet-4-20250514

LLM_TEMPERATURE=0.3
LLM_MAX_TOKENS=4096
LLM_TIMEOUT_SECONDS=60
```

If no LLM API key is configured, the backend still starts normally, but `POST /api/v1/agent/suggest-connections` returns `503` with `llm_unavailable`.

### Frontend

Requirements:

- Node.js 20+

Setup:

```bash
cd frontend
npm install
npm run dev
```

The frontend connects to the backend at `http://localhost:8000` by default.
Set `CS_API_TOKEN` to a valid JWT for server-side authentication (obtain one via `python manage.py create-admin` in the backend directory).

The current web UI supports:

- creating Claims, Concepts, Contexts, and Evidence from modal dialogs
- manually triggering AI connection suggestions from the Claim detail page
- reviewing proposals in-place with toast feedback and automatic refresh

### Docker Compose (Full Stack)

Run the entire stack with Docker Compose:

```bash
docker compose up --build
```

This starts PostgreSQL, the backend API (port 8000), and the frontend (port 3000).

### Demo Dataset

Seed the entropy-centered demo dataset:

```bash
cd backend
python manage.py seed
```

The seeded dataset contains:

- 6 contexts (5 fields + cross-field)
- 9 terms and 7 concepts
- 120 claims
- 33 evidence items
- 4 cross-field connections
- 3 CIR examples

See [Demo Dataset](docs/demo-dataset.md) for details.

## Documentation

- [Architecture](docs/architecture.md) — System design and component overview
- [Demo Dataset](docs/demo-dataset.md) — Entropy-themed seed data description
- [Roadmap](docs/roadmap.md) — Current state and future plans
- [Quality Audit](docs/quality-audit.md) — Current defect summary and remediation priorities
- [Specification Index](docs/specs-index.md) — OpenSpec documents for all subsystems
- [Parallel Development Guide](parallel_dev_guide.md) — Multi-agent parallel development setup
- [Agent Assignments](docs/agent-assignments.md) — Agent roles, file ownership, and collision map
- [Contributing](CONTRIBUTING.md)
- [Security](SECURITY.md)
- [Code of Conduct](CODE_OF_CONDUCT.md)

## OpenSpec

The repository includes specification documents under `openspec/specs/`. These documents describe the intended behavior of 9 subsystems (knowledge-graph, event-store, trust-model, proposal-review, linking-agent, rest-api, cli, web-ui, demo-dataset) and are part of the development process.

## Configuration

Copy `.env.example` to `.env` and adjust values as needed:

```bash
# Backend
DATABASE_URL=sqlite:///./tsumu_graph.db
JWT_SECRET=change-me-in-production
CORS_ORIGINS=http://localhost:3000
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
LLM_TEMPERATURE=0.3
LLM_MAX_TOKENS=4096
LLM_TIMEOUT_SECONDS=60

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
CS_API_TOKEN=
```

## Public Repository Notes

This public repository intentionally excludes internal proposal drafts, agent-operation directories, and local development artifacts from future tracking.

## License

This repository is licensed under the Apache License 2.0. See [LICENSE](LICENSE).
