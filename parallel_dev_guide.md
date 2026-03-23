# TsumuGraph 並行開発ガイド

複数のコーディングエージェントが並行して作業できるよう、プロジェクトを独立したトラックに分割する。各トラックはファイルレベルで衝突しないように設計されている。

---

## 現在の実装状況

Phase 0〜3はすべて実装・テスト済み。バックエンドテスト61/61パス、フロントエンドビルド成功。

| レイヤー | 状態 | 主要成果物 |
|----------|------|-----------|
| 共通型定義 | ✅完了 | `schemas/`（14ファイル）, `interfaces/`（15ファイル）, `lib/types.ts` |
| DBモデル | ✅完了 | `models/`（12モデル）, Alembicマイグレーション |
| Event Store | ✅完了 | `events/`（store, commands, projections, models） |
| 認証 | ✅完了 | `auth/`（JWT, PolicyEngine, dependencies） |
| ドメインサービス | ✅完了 | `services/`（12サービス） |
| ワークフロー | ✅完了 | `workflows/`（state_machine, trust_transitions, change_applier） |
| AI Agent | ✅完了 | `agent/`（7モジュール） |
| REST API | ✅完了 | `api/`（9ルート + router + dependencies + errors） |
| CLI | ✅完了 | `cli/cs/`（6コマンドグループ） |
| Web UI | ✅完了 | `frontend/src/`（6画面グループ + 15コンポーネント） |
| デモデータ | ✅完了 | `seeds/`（6ファイル + 7 JSONデータ） |

---

## エージェント分割マップ

```
Agent 1: Backend – Models / Events / Auth（データ基盤）
Agent 2: Backend – Services / Workflows（ビジネスロジック）
Agent 3: Backend – API Routes + main.py（HTTPインターフェース）
Agent 4: Backend – AI Linking Agent（AI連携パイプライン）
Agent 5: Frontend（Next.js Web UI）
Agent 6: CLI（コマンドラインツール）
Agent 7: Seeds / Data（デモデータ・テストデータ）
Agent 8: Specs / Docs（仕様書・ドキュメント）
```

---

## Agent 1: Backend – Models / Events / Auth（データ基盤）

データモデル、イベントストア、認証・認可の基盤レイヤーを担当する。

### 排他ファイル

```
backend/app/models/
├── __init__.py
├── base.py                 # SQLAlchemy Base, mixins
├── term.py                 # Term, TermConcept
├── concept.py              # Concept
├── referent.py             # Referent
├── claim.py                # Claim, ClaimContext, ClaimConcept, ClaimEvidence
├── context.py              # Context
├── evidence.py             # Evidence
├── cir.py                  # CIR, Condition
├── connection.py           # CrossFieldConnection
├── proposal.py             # Proposal
├── review.py               # Review
└── actor.py                # Actor

backend/app/events/
├── __init__.py
├── store.py                # EventStore実装
├── commands.py             # Command定義（ClaimCreated等）
├── projections.py          # Projection Engine
└── models.py               # Event SQLAlchemy model

backend/app/auth/
├── __init__.py
├── jwt.py                  # JWTトークン生成・検証
├── dependencies.py         # FastAPI Depends（get_current_actor等）
└── policy_engine.py        # PolicyEngine（権限チェック）

backend/alembic/
├── env.py
└── versions/
    └── 001_initial_schema.py
```

### 参照spec
- `openspec/specs/knowledge-graph/spec.md`（モデル定義）
- `openspec/specs/event-store/spec.md`（イベントストア）
- `openspec/specs/trust-model/spec.md`（認証・信頼モデル）

### テスト
```
backend/tests/test_models_smoke.py
backend/tests/test_events/
backend/tests/test_auth/
```

### 出力契約
- `from app.models import Claim, Concept, ...` でモデルインポート可能
- `IEventStore` 実装クラスを提供
- `Depends(get_current_actor)` で認証済みActorを取得可能

### 注意
- スキーマ変更時は必ず新しいAlembicマイグレーションファイルを追加する
- `backend/app/schemas/` と `backend/app/interfaces/` は共有契約（後述）のため、変更時は全エージェントに通知が必要

---

## Agent 2: Backend – Services / Workflows（ビジネスロジック）

ドメインサービス（CRUD + 検索）とProposal/Reviewワークフローを担当する。

### 排他ファイル

```
backend/app/services/
├── __init__.py
├── _shared.py              # 共通ユーティリティ（SessionFactory等）
├── actor_service.py        # ActorService
├── claim_service.py        # ClaimService（CRUD + バージョニング）
├── concept_service.py      # ConceptService
├── context_service.py      # ContextService
├── evidence_service.py     # EvidenceService
├── term_service.py         # TermService
├── referent_service.py     # ReferentService
├── cir_service.py          # CIRService
├── connection_service.py   # CrossFieldConnectionService
├── search_service.py       # SearchService
├── proposal_service.py     # ProposalService
└── review_service.py       # ReviewService

backend/app/workflows/
├── __init__.py
├── state_machine.py        # Proposalステートマシン
├── trust_transitions.py    # 信頼状態遷移ルール
└── change_applier.py       # Proposal承認時の変更適用
```

### 参照spec
- `openspec/specs/knowledge-graph/spec.md`（エンティティCRUD）
- `openspec/specs/proposal-review/spec.md`（ワークフロー）
- `openspec/specs/trust-model/spec.md`（信頼状態遷移）

### テスト
```
backend/tests/test_services/
backend/tests/test_workflows/
```

### 入力依存
- Agent 1 の `models/`, `events/`, `auth/`
- 共有契約: `schemas/`, `interfaces/`

### 出力契約
- `IClaimService`, `IProposalService` 等のインターフェース実装クラスを提供
- Agent 3（API）および Agent 4（Agent）が利用する

---

## Agent 3: Backend – API Routes + main.py（HTTPインターフェース）

REST APIエンドポイントとFastAPIアプリ初期化を担当する。

### 排他ファイル

```
backend/app/api/
├── __init__.py
├── router.py               # メインルーター（/api/v1 prefix）
├── dependencies.py         # サービスDI（get_claim_service等）
├── errors.py               # エラーハンドラー
├── claims.py               # /api/v1/claims
├── concepts.py             # /api/v1/concepts
├── contexts.py             # /api/v1/contexts
├── evidence.py             # /api/v1/evidence
├── terms.py                # /api/v1/terms
├── proposals.py            # /api/v1/proposals
├── agent.py                # /api/v1/agent
└── search.py               # /api/v1/search

backend/app/main.py          # FastAPIアプリ初期化、ルーター登録、CORS
```

### 参照spec
- `openspec/specs/rest-api/spec.md`

### テスト
```
backend/tests/test_api/
backend/tests/conftest.py     # 共有fixture（client, auth_header等）
```

### 入力依存
- Agent 1 の認証Depends
- Agent 2 のサービスクラス群
- 共有契約: `schemas/`, `interfaces/`

### 出力契約
- OpenAPI準拠のHTTPエンドポイントを提供
- Agent 5（Frontend）、Agent 6（CLI）がHTTP経由で利用

### 注意
- `conftest.py` は統合テスト全体で共有されるため、変更時は注意
- 新しいAPIルート追加時は `main.py` のルーター登録と `api/dependencies.py` のDI設定も更新する

---

## Agent 4: Backend – AI Linking Agent（AI連携パイプライン）

LLMを使った分野横断リンク提案パイプラインを担当する。

### 排他ファイル

```
backend/app/agent/
├── __init__.py
├── linking_agent.py        # LinkingAgent本体
├── trigger.py              # トリガーモジュール
├── context_collector.py    # コンテキスト収集
├── candidate_search.py     # 候補Claim検索
├── candidate_generator.py  # LLM接続候補生成
├── proposal_formatter.py   # Proposal自動生成・重複チェック
├── prompts.py              # LLMプロンプトテンプレート
└── config.py               # 確信度閾値等の設定
```

### 参照spec
- `openspec/specs/linking-agent/spec.md`

### テスト
```
backend/tests/test_agent/
```

### 入力依存
- Agent 2 のサービスクラス（リード系メソッド + ProposalService）
- 共有契約: `interfaces/linking_agent.py`

### 出力契約
- `ILinkingAgent` 実装クラスを提供
- Agent 3 の `/api/v1/agent` エンドポイントから呼び出される

---

## Agent 5: Frontend（Next.js Web UI）

Next.js 15 + React 19 + Tailwind CSS によるWeb UIを担当する。

### 排他ファイル

```
frontend/
├── package.json
├── next.config.js
├── tailwind.config.js
├── tsconfig.json
├── next-env.d.ts
├── src/
│   ├── app/
│   │   ├── layout.tsx              # 共通レイアウト
│   │   ├── page.tsx                # ダッシュボード
│   │   ├── claims/
│   │   │   ├── page.tsx            # Claim一覧
│   │   │   └── [id]/page.tsx       # Claim詳細
│   │   ├── concepts/
│   │   │   ├── page.tsx
│   │   │   └── [id]/page.tsx
│   │   ├── contexts/
│   │   │   ├── page.tsx
│   │   │   └── [id]/page.tsx
│   │   ├── graph/page.tsx          # グラフビュー
│   │   ├── review/page.tsx         # レビューキュー
│   │   └── search/page.tsx         # 検索
│   ├── components/
│   │   ├── layout/                 # Sidebar, Header, StatsCard
│   │   ├── claims/                 # ClaimCard, ClaimTable, ClaimDetail
│   │   ├── evidence/               # EvidenceCard
│   │   ├── proposals/              # ProposalCard, ReviewDialog
│   │   ├── graph/                  # ForceGraph
│   │   ├── common/                 # FilterBar, Pagination, SearchBar, TrustBadge
│   │   └── cir/                    # CIRDisplay
│   └── lib/
│       ├── api.ts                  # APIクライアント（サーバーサイドfetch）
│       └── types.ts                # TypeScript型定義
└── public/
```

### 参照spec
- `openspec/specs/web-ui/spec.md`

### 入力依存
- Agent 3 のREST APIエンドポイント（HTTP経由）
- 環境変数 `CS_API_TOKEN`（サーバーサイドfetchの認証トークン）

### サブ分割（Agent 5 内で更に分割可能）

| Sub-Agent | 画面 | 担当ファイル |
|-----------|------|-------------|
| 5-1 | レイアウト + ダッシュボード | `layout.tsx`, `page.tsx`, `layout/` |
| 5-2 | Claim一覧 + 詳細 | `claims/`, `claims/`, `evidence/`, `cir/` |
| 5-3 | Context + Concept画面 | `contexts/`, `concepts/`, `common/` |
| 5-4 | レビューキュー | `review/`, `proposals/` |
| 5-5 | グラフビュー | `graph/` |
| 5-6 | 検索 | `search/` |

### 注意
- 全ページに `export const dynamic = "force-dynamic"` が必要（SSRでAPI呼び出しするため）
- `lib/api.ts` は共通APIクライアントのため、変更時はすべての画面に影響する

---

## Agent 6: CLI（コマンドラインツール）

Typer + httpx によるCLIツールを担当する。

### 排他ファイル

```
cli/
├── pyproject.toml
├── cs/
│   ├── __init__.py
│   ├── main.py             # Typer app entry
│   ├── config.py           # ~/.cs/config.toml 管理
│   ├── api_client.py       # REST APIクライアント
│   ├── formatters.py       # テーブル/JSON出力フォーマッタ
│   └── commands/
│       ├── __init__.py
│       ├── auth.py         # cs auth login / create-admin
│       ├── claim.py        # cs claim list/get/create/history
│       ├── concept.py      # cs concept list/get/connections
│       ├── proposal.py     # cs proposal list/review
│       ├── agent.py        # cs agent suggest/suggestions
│       └── search.py       # cs search
└── tests/
    ├── test_claim_commands.py
    ├── test_proposal_commands.py
    └── test_agent_commands.py
```

### 参照spec
- `openspec/specs/cli/spec.md`

### 入力依存
- Agent 3 のREST APIエンドポイント（HTTP経由）

---

## Agent 7: Seeds / Data（デモデータ・テストデータ）

Seedスクリプトとデモ用JSONデータを担当する。

### 排他ファイル

```
backend/app/seeds/
├── __init__.py
├── entropy_dataset.py      # メインのSeedスクリプト
└── data/
    ├── contexts.json       # 6 Context
    ├── terms.json          # 9 Term
    ├── concepts.json       # 7 Concept
    ├── claims.json         # 120 Claim（24 base + 96 generated）
    ├── evidence.json       # 33 Evidence（8 base + 25 generated）
    ├── connections.json    # 4 Cross-field Connection
    └── cir.json            # 3 CIR

backend/manage.py               # CLI管理コマンド（seed / create-admin / serve）
```

### 参照spec
- `openspec/specs/demo-dataset/spec.md`

### 入力依存
- Agent 1 のモデル
- Agent 2 のサービス（`entropy_dataset.py` がサービス経由でデータ投入）

---

## Agent 8: Specs / Docs（仕様書・ドキュメント）

仕様書とドキュメントを担当する。コードには触れない。

### 排他ファイル

```
openspec/
├── config.yaml
├── changes/                # 変更提案（OpenSpec形式）
└── specs/
    ├── cli/spec.md
    ├── demo-dataset/spec.md
    ├── event-store/spec.md
    ├── knowledge-graph/spec.md
    ├── linking-agent/spec.md
    ├── proposal-review/spec.md
    ├── rest-api/spec.md
    ├── trust-model/spec.md
    └── web-ui/spec.md

docs/
├── architecture.md
├── demo-dataset.md
├── roadmap.md
└── specs-index.md

README.md
CODE_OF_CONDUCT.md
CONTRIBUTING.md
SECURITY.md
prototype_design.md
```

---

## 共有契約（全エージェント共通）

以下のファイル群は複数エージェントが参照する**契約境界**。変更時は関連エージェント全員に影響するため、単一エージェントが責任を持って変更し、他に通知する。

### Pydanticスキーマ（API入出力型）
```
backend/app/schemas/
├── __init__.py             # 全スキーマの re-export
├── common.py               # Enum群, PaginatedResponse, ErrorResponse
├── term.py                 # TermCreate, TermRead, TermUpdate
├── concept.py              # ConceptCreate, ConceptRead, ConceptUpdate
├── claim.py                # ClaimCreate, ClaimRead, ClaimUpdate
├── context.py              # ContextCreate, ContextRead, ContextUpdate
├── evidence.py             # EvidenceCreate, EvidenceRead, EvidenceUpdate
├── proposal.py             # ProposalCreate, ProposalRead
├── review.py               # ReviewCreate, ReviewRead
├── actor.py                # ActorCreate, ActorRead
├── referent.py             # ReferentCreate, ReferentRead, ReferentUpdate
├── cir.py                  # CIRCreate, CIRRead
├── connection.py           # CrossFieldConnectionCreate, Read
└── search.py               # SearchQuery, SearchResult
```

### サービスインターフェース（抽象基底クラス）
```
backend/app/interfaces/
├── __init__.py             # 全インターフェースの re-export
├── claim_service.py        # IClaimService
├── concept_service.py      # IConceptService
├── context_service.py      # IContextService
├── evidence_service.py     # IEvidenceService
├── term_service.py         # ITermService
├── actor_service.py        # IActorService
├── referent_service.py     # IReferentService
├── cir_service.py          # ICIRService
├── connection_service.py   # IConnectionService
├── search_service.py       # ISearchService
├── event_store.py          # IEventStore
├── proposal_service.py     # IProposalService
├── review_service.py       # IReviewService
└── linking_agent.py        # ILinkingAgent
```

### TypeScript型定義
```
frontend/src/lib/types.ts    # APIレスポンス型（フロントエンド側の契約）
```

### 共有契約の変更ルール

1. **スキーマ追加**: 既存フィールドに影響なければ各エージェント独立で追加可能
2. **スキーマ変更（フィールド名変更・削除）**: 全関連エージェントに通知必須
3. **インターフェース変更（メソッド追加）**: 実装側のエージェントが追加、他に通知
4. **インターフェース変更（シグネチャ変更）**: 全関連エージェントに通知必須
5. **types.ts変更**: Agent 5（Frontend）が責任を持つ。バックエンドのスキーマ変更に追従

---

## 依存関係マップ

```
共有契約（schemas/, interfaces/, types.ts）
    │
    ├──→ Agent 1: Models / Events / Auth
    │        │
    │        ├──→ Agent 2: Services / Workflows
    │        │        │
    │        │        ├──→ Agent 3: API Routes
    │        │        │        │
    │        │        │        ├──→ Agent 5: Frontend（HTTP経由）
    │        │        │        ├──→ Agent 6: CLI（HTTP経由）
    │        │        │        └──→ Agent 7: Seeds（直接 or HTTP経由）
    │        │        │
    │        │        └──→ Agent 4: AI Agent
    │        │
    │        └──→ Agent 7: Seeds（モデル直接利用）
    │
    └──→ Agent 8: Specs / Docs（コード参照のみ、変更なし）
```

### 並行作業可能な組み合わせ

| 同時作業可能 | 理由 |
|-------------|------|
| Agent 3 + Agent 4 | 別ディレクトリ（`api/` vs `agent/`）、同じサービスを参照するが排他なし |
| Agent 5 + Agent 6 | 完全に独立（`frontend/` vs `cli/`）、APIはHTTP経由 |
| Agent 5 + Agent 7 | 完全に独立（`frontend/` vs `seeds/`） |
| Agent 6 + Agent 7 | 完全に独立（`cli/` vs `seeds/`） |
| Agent 1 + Agent 5 | 完全に独立（`models/` vs `frontend/`） |
| Agent 1 + Agent 6 | 完全に独立（`models/` vs `cli/`） |
| Agent 8 + 全Agent | Docsは読み取り専用のため常に並行可能 |

### 注意が必要な組み合わせ

| 組み合わせ | 注意点 |
|-----------|--------|
| Agent 1 + Agent 2 | Agent 2がAgent 1のモデル変更を参照するため、モデル変更後にAgent 2に通知 |
| Agent 2 + Agent 3 | Agent 3がAgent 2のサービスをDIするため、メソッド追加時に通知 |
| Agent 2 + Agent 4 | Agent 4がAgent 2のサービスを利用するため、インターフェース変更時に通知 |

---

## ファイル衝突なしマップ

各エージェントが触るファイルが完全に分離されていることの確認:

```
Agent 1: backend/app/models/*,  backend/app/events/*,   backend/app/auth/*,     backend/alembic/*
Agent 2: backend/app/services/*, backend/app/workflows/*
Agent 3: backend/app/api/*,      backend/app/main.py
Agent 4: backend/app/agent/*
Agent 5: frontend/*
Agent 6: cli/*
Agent 7: backend/app/seeds/*
Agent 8: openspec/*, docs/*, README.md, *.md（ルート直下ドキュメント）
```

→ **衝突なし**: 最大8エージェントが同時に作業可能

---

## 技術スタック早見表

| レイヤー | 技術 | バージョン |
|----------|------|-----------|
| Backend Framework | FastAPI | - |
| ORM | SQLAlchemy | 2.x |
| Migration | Alembic | - |
| Auth | python-jose (JWT) | - |
| DB (dev) | SQLite | - |
| DB (prod) | PostgreSQL | 16 |
| Frontend Framework | Next.js | 15 |
| UI Library | React | 19 |
| CSS | Tailwind CSS | 3.4 |
| CLI Framework | Typer | - |
| HTTP Client (CLI) | httpx | - |
| Container | Docker Compose | - |

---

## 起動方法

### バックエンド
```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

### フロントエンド
```bash
cd frontend
CS_API_TOKEN="<JWT Token>" npm run dev
# → http://localhost:3000
```

### JWTトークン取得
```bash
cd backend
python manage.py create-admin
# → Actor ID と Token が出力される
```

### Docker Compose（本番風）
```bash
docker compose up --build
```

### テスト実行
```bash
# backend
cd backend && python -m pytest -q

# frontend
cd frontend && npm run build

# cli
cd cli && python -m pytest -q
```

---

## エージェントへの指示テンプレート

各エージェントに渡す指示の雛形:

```
あなたは TsumuGraph プロジェクトの [Agent X: トラック名] を担当します。

## コンテキスト
- プロジェクト概要: prototype_design.md を参照
- 並行開発ガイド: parallel_dev_guide.md を参照
- 詳細仕様: openspec/specs/[capability]/spec.md を参照
- 共通型定義: backend/app/schemas/ を参照
- サービスインターフェース: backend/app/interfaces/ を参照

## あなたの排他的担当範囲
[排他ファイル一覧]

## 触ってはいけないファイル
上記以外のすべてのファイル（他のエージェントが担当）

## 共有契約
schemas/, interfaces/, types.ts を変更する場合は他のエージェントへの通知が必要

## 作業内容
[具体的なタスク]

## テスト
[対応するテストディレクトリ]
```

---

## クイックリファレンス: Agent→Spec対応

| Agent | 主要参照Spec | 補助参照Spec |
|-------|------------|------------|
| 1: Models/Events/Auth | knowledge-graph, event-store, trust-model | — |
| 2: Services/Workflows | knowledge-graph, proposal-review | event-store, trust-model |
| 3: API Routes | rest-api | 全spec |
| 4: AI Agent | linking-agent | proposal-review |
| 5: Frontend | web-ui | rest-api |
| 6: CLI | cli | rest-api |
| 7: Seeds/Data | demo-dataset | knowledge-graph |
| 8: Specs/Docs | 全spec | — |
