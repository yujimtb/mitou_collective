# アーキテクチャ概要

> **🇯🇵 日本語** | [English](#architecture-overview)

CollectiveScienceは、科学的知識を構造化グラフとして表現し、分野横断的な概念的つながりを探索するClaim中心の知識プラットフォームです。Claim、Context、Evidence、Proposal、Review、分野横断接続はすべてファーストクラスオブジェクトです。

## コアデータモデル

システムは12のエンティティ型を管理します：

| エンティティ | 役割 |
|-------------|------|
| **Claim** | 原子的な科学的記述（バージョン管理、信頼ステータス付き） |
| **Context** | Claimが意味を持つ仮定と学問分野の枠組み |
| **Concept** | 分野を横断して対応づけられる概念単位 |
| **Term** | 1つ以上の言語における概念の表層形 |
| **Evidence** | Claimを支持または反論するソース（信頼度評価付き） |
| **CIR** | Claim in Formal Representation — Claimの構造化形式表現 |
| **CrossFieldConnection** | 分野を越えたClaim間の明示的関係 |
| **Proposal** | 変更リクエスト（Claim作成、Claimリンク、信頼度更新等） |
| **Review** | Proposalに対する判定（承認/却下/変更要求） |
| **Actor** | 信頼レベルを持つ人間またはAIエージェント |
| **Referent** | TermやConceptが指し示す対象オブジェクト |
| **Event** | 履歴と再構築のための追記専用イベントレコード |

主なN:M関係：Claim↔Context、Claim↔Concept、Claim↔Evidence、Term↔Concept。

## システムアーキテクチャ

```
┌─────────────┐  ┌─────────────┐
│  Frontend   │  │    CLI      │
│  (Next.js)  │  │  (Typer)    │
└──────┬──────┘  └──────┬──────┘
       │  HTTP/REST      │
       └────────┬────────┘
                ▼
┌───────────────────────────────┐
│        REST APIレイヤー        │
│   FastAPI（9ルートグループ）    │
├───────────────────────────────┤
│       サービスレイヤー          │
│   12ドメインサービス            │
│   + ワークフローエンジン        │
│   + AIリンキングエージェント    │
├───────────────────────────────┤
│       データレイヤー           │
│   SQLAlchemy ORM（12モデル）   │
│   追記専用イベントストア        │
│   JWT認証 + PolicyEngine      │
├───────────────────────────────┤
│       データベース              │
│   SQLite（開発）/ PostgreSQL   │
└───────────────────────────────┘
```

## バックエンド

**フレームワーク**: FastAPI + SQLAlchemy 2.x + Alembic

### レイヤー構成

| レイヤー | ディレクトリ | 内容 |
|---------|-------------|------|
| モデル | `app/models/` | UUID主キー、タイムスタンプ、ミックスインを持つ12のSQLAlchemyモデル |
| スキーマ | `app/schemas/` | エンティティごとのCreate/Read/Updateを含む14のPydanticスキーマモジュール |
| インターフェース | `app/interfaces/` | DI用の14の抽象サービスインターフェース（ABC） |
| サービス | `app/services/` | 12のサービス実装（CRUD、検索、イベント記録） |
| ワークフロー | `app/workflows/` | Proposalステートマシン、信頼度遷移、変更適用 |
| イベント | `app/events/` | 追記専用イベントストア、コマンド、プロジェクション |
| 認証 | `app/auth/` | JWT（python-jose）、PolicyEngine、FastAPI依存性注入 |
| エージェント | `app/agent/` | AIリンキングパイプライン（トリガー、コンテキスト、候補、フォーマッター） |
| API | `app/api/` | 9ルートグループ + DI + エラーハンドラー |
| シード | `app/seeds/` | デモデータセット（エントロピーテーマ、120+ Claim） |

### APIルート

| ルート | エンドポイント |
|-------|--------------|
| `/api/v1/auth` | ログイン、管理者作成 |
| `/api/v1/claims` | 一覧、作成、取得、更新、履歴 |
| `/api/v1/concepts` | 一覧、作成、取得、接続 |
| `/api/v1/contexts` | 一覧、作成、取得、更新 |
| `/api/v1/evidence` | 一覧、作成、取得 |
| `/api/v1/terms` | 一覧、作成、取得、検索 |
| `/api/v1/proposals` | 一覧、作成、取得、提出、レビュー |
| `/api/v1/agent` | 接続提案、提案一覧 |
| `/api/v1/search` | エンティティ横断全文検索 |

### 認証・認可

- `actor_type`、`trust_level`を埋め込んだJWTトークン
- 4段階信頼モデル：admin > reviewer > contributor > observer
- PolicyEngineが操作 × trust_levelの権限を執行
- 自己レビュー禁止

## フロントエンド

**フレームワーク**: Next.js 15 + React 19 + Tailwind CSS 3.4 + TypeScript

すべてのページは `force-dynamic` エクスポートによるサーバーサイドレンダリング（SSR）を使用。フロントエンドは `CS_API_TOKEN` 環境変数でバックエンドに認証し、SSRビューに作成/レビューワークフロー用のクライアントサイドダイアログを加えて表示します。

| ページ | パス | 説明 |
|-------|------|------|
| ダッシュボード | `/` | 統計サマリー + 最新Claim/Proposal |
| Claim一覧 | `/claims` | テーブル/カードビューとClaim作成ダイアログ付きフィルタリスト |
| Claim詳細 | `/claims/[id]` | Evidence、CIR、履歴、Evidence作成、手動AI提案トリガー付き |
| Concept一覧 | `/concepts` | Concept作成ダイアログ付きリスト |
| Concept詳細 | `/concepts/[id]` | 分野横断接続付きConcept |
| Context一覧 | `/contexts` | Context作成ダイアログ付きリスト |
| Context詳細 | `/contexts/[id]` | 関連Claim付きContext |
| レビューキュー | `/review` | 承認/却下アクション、トーストフィードバック、フェードアウト付きProposal一覧 |
| グラフ | `/graph` | D3フォースグラフビジュアライゼーション |
| 検索 | `/search` | 全エンティティ横断全文検索 |

20のReactコンポーネントをドメイン別に整理：レイアウト、Claim、Evidence、Proposal、グラフ、共通、CIR、作成/フィードバックワークフロー。

## CLI

**フレームワーク**: Typer + httpx + Rich

6コマンドグループ：`auth`、`claim`、`concept`、`proposal`、`agent`、`search`。すべてのコマンドはREST API経由でバックエンドと通信。`--json` 出力モードをサポート。

## イベントストア

すべての状態変更を記録する追記専用イベントログ（ClaimCreated、ClaimUpdated、ClaimTrustChanged等）。サポート機能：

- 集約ID別クエリ（エンティティ履歴）
- シーケンス番号別クエリ（グローバル順序付け）
- リードモデル再構築用プロジェクションエンジン

## AIリンキングエージェント

分野横断的な概念リンクを発見するパイプライン：

1. **トリガー** — 新規Claim/Conceptの検知または手動リクエスト
2. **コンテキスト収集** — 周辺のClaim/Concept情報の収集
3. **候補検索** — 分野を越えた関連Claimの検索
4. **候補生成** — プロバイダーアダプター（`OpenAIAdapter`または`AnthropicAdapter`）によるLLM接続提案の生成
5. **Proposalフォーマッター** — 確信度フィルタリングと重複排除を行いProposalとして整形

バックエンドはアプリケーション起動時に環境変数から `LLMConfig` を設定。サポートされるAPIキーが存在する場合、`main.py` が選択されたアダプターの `generate()` メソッドを `CandidateGenerator` に注入し、存在しない場合はno-opフォールバックを維持してシークレットなしでAPIが起動可能。

手動AI提案リクエストはAPIレイヤーで制御：プロバイダーAPIキーが設定されていない場合、`POST /api/v1/agent/suggest-connections` は `503`（`llm_unavailable`）を返却。

## 仕様駆動開発

`openspec/specs/` 配下の9つのOpenSpecドキュメントが意図された動作を記述：knowledge-graph、event-store、trust-model、proposal-review、linking-agent、rest-api、cli、web-ui、demo-dataset。詳細は [仕様書インデックス](specs-index.md) を参照。

## テスト

34のテストファイルにわたる69のバックエンドテスト：

- API統合テスト（8ルートグループ）
- サービスユニットテスト
- ワークフローテスト（ステートマシン、信頼度遷移、変更適用）
- 認証テスト（JWT、PolicyEngine、依存性注入）
- エージェントテスト（全パイプラインステージ）
- LLMアダプター/設定テスト（OpenAI、Anthropic、ファクトリー選択、API準備状態）
- イベントストアテスト
- シードデータセットテスト
- モデルスモークテスト

## デプロイ

- **開発環境**: SQLite + `uvicorn --reload` + `npm run dev`
- **本番環境**: PostgreSQL 16、バックエンド、フロントエンドコンテナを含むDocker Compose
- 主要なバックエンド環境変数：`LLM_PROVIDER`、`LLM_MODEL`、`OPENAI_API_KEY`、`ANTHROPIC_API_KEY`、`LLM_TEMPERATURE`、`LLM_MAX_TOKENS`、`LLM_TIMEOUT_SECONDS`
- 環境変数：`.env.example` を参照

---

# Architecture Overview

> **🇬🇧 English** | [日本語](#アーキテクチャ概要)

CollectiveScience is a claim-centered knowledge platform for representing scientific knowledge as a structured graph and exploring conceptual links across disciplines. Claims, contexts, evidence, proposals, reviews, and cross-field connections are all first-class objects.

## Core Data Model

The system manages 12 entity types:

| Entity | Role |
|--------|------|
| **Claim** | Atomic scientific statement (versioned, with trust status) |
| **Context** | Assumptions and disciplinary frame in which claims are meaningful |
| **Concept** | Conceptual unit that may map across domains |
| **Term** | Surface form in one or more languages, linked to concepts |
| **Evidence** | Source supporting or contradicting claims (with reliability rating) |
| **CIR** | Claim in Formal Representation — structured formal encoding of a claim |
| **CrossFieldConnection** | Explicit relation between claims across fields |
| **Proposal** | Change request (create claim, link claims, update trust, etc.) |
| **Review** | Decision on a proposal (approve / reject / request changes) |
| **Actor** | Human or AI agent with trust level |
| **Referent** | Target object that a term or concept refers to |
| **Event** | Append-only event record for history and reconstruction |

Key N:M relationships: Claim↔Context, Claim↔Concept, Claim↔Evidence, Term↔Concept.

## System Architecture

```
┌─────────────┐  ┌─────────────┐
│  Frontend   │  │    CLI      │
│  (Next.js)  │  │  (Typer)    │
└──────┬──────┘  └──────┬──────┘
       │  HTTP/REST      │
       └────────┬────────┘
                ▼
┌───────────────────────────────┐
│        REST API Layer         │
│   FastAPI (9 route groups)    │
├───────────────────────────────┤
│       Service Layer           │
│   12 domain services          │
│   + Workflow engine           │
│   + AI Linking Agent          │
├───────────────────────────────┤
│       Data Layer              │
│   SQLAlchemy ORM (12 models)  │
│   Append-only Event Store     │
│   JWT Auth + PolicyEngine     │
├───────────────────────────────┤
│       Database                │
│   SQLite (dev) / PostgreSQL   │
└───────────────────────────────┘
```

## Backend

**Framework**: FastAPI + SQLAlchemy 2.x + Alembic

### Layer breakdown

| Layer | Directory | Contents |
|-------|-----------|----------|
| Models | `app/models/` | 12 SQLAlchemy models with UUID PKs, timestamps, mixins |
| Schemas | `app/schemas/` | 14 Pydantic schema modules (Create/Read/Update per entity) |
| Interfaces | `app/interfaces/` | 14 abstract service interfaces (ABC) for DI |
| Services | `app/services/` | 12 service implementations (CRUD, search, event recording) |
| Workflows | `app/workflows/` | Proposal state machine, trust transitions, change applier |
| Events | `app/events/` | Append-only event store, commands, projections |
| Auth | `app/auth/` | JWT (python-jose), PolicyEngine, FastAPI dependencies |
| Agent | `app/agent/` | AI linking pipeline (trigger, context, candidates, formatter) |
| API | `app/api/` | 9 route groups + DI + error handlers |
| Seeds | `app/seeds/` | Demo dataset (entropy theme, 120+ claims) |

### API routes

| Route | Endpoints |
|-------|-----------|
| `/api/v1/auth` | Login, create admin |
| `/api/v1/claims` | List, create, get, update, history |
| `/api/v1/concepts` | List, create, get, connections |
| `/api/v1/contexts` | List, create, get, update |
| `/api/v1/evidence` | List, create, get |
| `/api/v1/terms` | List, create, get, lookup |
| `/api/v1/proposals` | List, create, get, submit, review |
| `/api/v1/agent` | Suggest connections, list suggestions |
| `/api/v1/search` | Full-text search across entities |

### Authentication & authorization

- JWT tokens with embedded `actor_type`, `trust_level`
- 4-tier trust model: admin > reviewer > contributor > observer
- PolicyEngine enforces operation × trust_level permissions
- Self-review prohibition

## Frontend

**Framework**: Next.js 15 + React 19 + Tailwind CSS 3.4 + TypeScript

All pages use server-side rendering (SSR) with `force-dynamic` export. The frontend authenticates to the backend via the `CS_API_TOKEN` environment variable and augments SSR views with client-side dialogs for create/review workflows.

| Page | Path | Description |
|------|------|-------------|
| Dashboard | `/` | Stats summary + recent claims/proposals |
| Claims | `/claims` | Filterable list with table/card views and a create-claim dialog |
| Claim detail | `/claims/[id]` | Full claim with evidence, CIR, history, evidence creation, and manual AI suggestion trigger |
| Concepts | `/concepts` | Concept list with create-concept dialog |
| Concept detail | `/concepts/[id]` | Concept with cross-field connections |
| Contexts | `/contexts` | Context list with create-context dialog |
| Context detail | `/contexts/[id]` | Context with associated claims |
| Review queue | `/review` | Proposal list with approve/reject actions, toast feedback, and fade-out completion |
| Graph | `/graph` | D3 force-directed graph visualization |
| Search | `/search` | Full-text search across all entities |

20 React components organized by domain: layout, claims, evidence, proposals, graph, common, cir, and create/feedback workflows.

## CLI

**Framework**: Typer + httpx + Rich

6 command groups: `auth`, `claim`, `concept`, `proposal`, `agent`, `search`. All commands communicate with the backend via REST API. Supports `--json` output mode.

## Event Store

Append-only event log recording all state changes (ClaimCreated, ClaimUpdated, ClaimTrustChanged, etc.). Supports:

- Query by aggregate ID (entity history)
- Query by sequence number (global ordering)
- Projection engine for read model reconstruction

## AI Linking Agent

Pipeline for discovering cross-field conceptual links:

1. **Trigger** — detect new claims/concepts or manual request
2. **Context collector** — gather surrounding claim/concept information
3. **Candidate search** — find related claims across fields
4. **Candidate generator** — generate connection proposals via a provider adapter (`OpenAIAdapter` or `AnthropicAdapter`)
5. **Proposal formatter** — format as Proposals with confidence filtering and deduplication

The backend wires `LLMConfig` from environment variables at application startup. When a supported API key is present, `main.py` injects the selected adapter's `generate()` method into `CandidateGenerator`; otherwise it keeps the no-op fallback so the API can boot without secrets.

Manual AI suggestion requests are guarded at the API layer: `POST /api/v1/agent/suggest-connections` returns `503` with `llm_unavailable` when no provider API key is configured.

## Specification-Driven Development

9 OpenSpec documents under `openspec/specs/` describe intended behavior: knowledge-graph, event-store, trust-model, proposal-review, linking-agent, rest-api, cli, web-ui, demo-dataset. See [Specification Index](specs-index.md) for details.

## Testing

69 backend tests across 34 test files covering:

- API integration tests (8 route groups)
- Service unit tests
- Workflow tests (state machine, trust transitions, change applier)
- Auth tests (JWT, policy engine, dependencies)
- Agent tests (all pipeline stages)
- LLM adapter/config tests for OpenAI, Anthropic, factory selection, and API readiness behavior
- Event store tests
- Seed dataset tests
- Model smoke tests

## Deployment

- **Development**: SQLite + `uvicorn --reload` + `npm run dev`
- **Production**: Docker Compose with PostgreSQL 16, backend, and frontend containers
- Key backend environment variables: `LLM_PROVIDER`, `LLM_MODEL`, `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `LLM_TEMPERATURE`, `LLM_MAX_TOKENS`, `LLM_TIMEOUT_SECONDS`
- Environment variables: see `.env.example`
