# CollectiveScience 並行開発ガイド

コーディングエージェントが並行して作業できるよう、作業を独立したトラックに分割する。各トラックはファイルレベルで衝突しないように設計されている。

---

## 全体依存関係図

```
Phase 0: 共通型定義・インターフェース契約
  │  （全トラックの前提、1エージェントで実行）
  ▼
Phase 1: 基盤レイヤー（3トラック並行）
  ├── Track A: DBスキーマ + SQLAlchemyモデル
  ├── Track B: Event Store基盤
  └── Track C: Trust Model / ActorRef / 認証
  │
  ▼
Phase 2: ビジネスロジック（3トラック並行）
  ├── Track D: ドメインサービス（CRUD）
  ├── Track E: Proposal/Reviewワークフロー
  └── Track F: AI Linking Agent
  │
  ▼
Phase 3: インターフェース（4トラック並行）
  ├── Track G: REST APIエンドポイント
  ├── Track H: CLI
  ├── Track I: Web UI
  └── Track J: デモデータセット
```

---

## Phase 0: 共通型定義・インターフェース契約

**目的**: 全トラックが参照する型定義とインターフェースを先に確定する。これにより後続のPhaseが互いを待たずに並行開発できる。

**担当**: 1エージェント（他の全トラックの前提）

### 成果物

```
backend/
├── app/
│   ├── schemas/                    ← Pydantic スキーマ（API入出力型）
│   │   ├── __init__.py
│   │   ├── term.py                 # TermCreate, TermRead, TermUpdate
│   │   ├── concept.py              # ConceptCreate, ConceptRead, ConceptUpdate
│   │   ├── claim.py                # ClaimCreate, ClaimRead, ClaimUpdate
│   │   ├── context.py              # ContextCreate, ContextRead, ContextUpdate
│   │   ├── evidence.py             # EvidenceCreate, EvidenceRead, EvidenceUpdate
│   │   ├── proposal.py             # ProposalCreate, ProposalRead
│   │   ├── review.py               # ReviewCreate, ReviewRead
│   │   ├── actor.py                # ActorCreate, ActorRead
│   │   ├── referent.py             # ReferentCreate, ReferentRead, ReferentUpdate
│   │   ├── cir.py                  # CIRCreate, CIRRead
│   │   ├── connection.py           # CrossFieldConnectionCreate, Read
│   │   ├── search.py               # SearchQuery, SearchResult
│   │   └── common.py               # PaginatedResponse, ErrorResponse, enums
│   └── interfaces/                 ← サービスインターフェース（抽象基底クラス）
│       ├── actor_service.py        # IActorService
│       ├── referent_service.py     # IReferentService
│       ├── __init__.py
│       ├── claim_service.py        # IClaimService
│       ├── concept_service.py      # IConceptService
│       ├── context_service.py      # IContextService
│       ├── evidence_service.py     # IEvidenceService
│       ├── term_service.py         # ITermService
│       ├── cir_service.py          # ICIRService
│       ├── connection_service.py   # IConnectionService
│       ├── search_service.py       # ISearchService
│       ├── event_store.py          # IEventStore
│       ├── proposal_service.py     # IProposalService
│       ├── review_service.py       # IReviewService
│       └── linking_agent.py        # ILinkingAgent
frontend/
└── src/
    └── lib/
        └── types.ts                ← TypeScript型定義（APIレスポンス型）
```

### `common.py` に定義するEnum群

```python
# ClaimType: definition | theorem | empirical | conjecture | meta
# TrustStatus: established | tentative | disputed | ai_suggested
# EvidenceType: textbook | paper | experiment | proof | expert_opinion
# Reliability: high | medium | low | unverified
# ProposalType: create_claim | link_claims | update_trust | add_evidence | connect_concepts
# ProposalStatus: pending | in_review | approved | rejected | withdrawn
# ReviewDecision: approve | reject | request_changes
# ConnectionType: equivalent | analogous | generalizes | contradicts | complements
# ActorType: human | ai_agent
# TrustLevel: admin | reviewer | contributor | observer
# EvidenceRelationship: supports | contradicts | partially_supports
```

### 完了条件

- [ ] すべてのPydanticスキーマが定義され、import可能
- [ ] すべてのサービスインターフェース（ABC）が定義済み
- [ ] TypeScript型定義がフロントエンドで利用可能
- [ ] `backend/pyproject.toml` と `frontend/package.json` が初期化済み
- [ ] `docker-compose.yml`（PostgreSQL）が起動可能

---

## Phase 1: 基盤レイヤー（3トラック並行）

### Track A: DBスキーマ + SQLAlchemyモデル

**参照spec**: `knowledge-graph/spec.md`

**入力契約**: Phase 0の `schemas/` の型定義

**担当ファイル**（排他）:
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
backend/alembic/
├── env.py
└── versions/
    └── 001_initial_schema.py
```

**作業内容**:
1. SQLAlchemyモデル定義（全エンティティ）
2. N:M関連テーブル（term_concepts, claim_contexts, claim_concepts, claim_evidence）
3. CHECK制約（enum値）、INDEX定義
4. Alembicマイグレーションファイル生成
5. `conftest.py` にテスト用DBセッションfixture作成

**出力契約**: `from app.models import Claim, Concept, ...` でインポート可能

**完了条件**:
- [ ] `alembic upgrade head` でスキーマ構築成功
- [ ] 全テーブルCREATE確認
- [ ] 全N:M関連テーブルが正しくJOIN可能

---

### Track B: Event Store基盤

**参照spec**: `event-store/spec.md`

**入力契約**: Phase 0の `interfaces/event_store.py`

**担当ファイル**（排他）:
```
backend/app/events/
├── __init__.py
├── store.py                # EventStore実装（PostgreSQL）
├── commands.py             # Command定義（ClaimCreated等）
├── projections.py          # Projection Engine
└── models.py               # Event SQLAlchemy model
backend/tests/test_events/
├── test_store.py
├── test_commands.py
└── test_projections.py
```

**作業内容**:
1. Eventテーブル SQLAlchemyモデル
2. EventStore クラス（append, query_by_aggregate, query_by_sequence）
3. Command定義（各event_type用のdataclass/Pydantic model）
4. Projection Engine（イベント再生→リードモデル更新）
5. ユニットテスト

**出力契約**: `IEventStore` インターフェースを実装した `EventStore` クラス

**完了条件**:
- [ ] イベントのappendとqueryが動作
- [ ] Projection再構築が動作
- [ ] sequence_numberの単調増加が保証されている

---

### Track C: Trust Model / ActorRef / 認証

**参照spec**: `trust-model/spec.md`

**入力契約**: Phase 0の `schemas/actor.py`, `interfaces/` の認証関連

**担当ファイル**（排他）:
```
backend/app/auth/
├── __init__.py
├── jwt.py                  # JWTトークン生成・検証
├── dependencies.py         # FastAPI Depends（get_current_actor等）
└── policy_engine.py        # PolicyEngine（権限チェック）
backend/app/services/
└── actor_service.py        # ActorRef CRUD
backend/tests/test_auth/
├── test_jwt.py
├── test_policy_engine.py
└── test_dependencies.py
```

**作業内容**:
1. JWT生成・検証ユーティリティ
2. FastAPI依存性注入（`get_current_actor`）
3. PolicyEngine（trust_level × 操作種別の権限マトリクス）
4. 自己レビュー禁止ロジック
5. 段階的自律性レベル設定（Level 0をデフォルト）
6. ActorRef CRUDサービス

**出力契約**: `Depends(get_current_actor)` でActorRefが取得可能

**完了条件**:
- [ ] JWTトークンの発行・検証が動作
- [ ] trust_level別の権限チェックが動作
- [ ] 自己レビュー禁止が動作

---

## Phase 2: ビジネスロジック（3トラック並行）

> Phase 1の3トラックがすべて完了後に開始

### Track D: ドメインサービス（CRUD）

**参照spec**: `knowledge-graph/spec.md`, `rest-api/spec.md`（エンティティCRUD部分）

**入力契約**: Track Aのモデル, Track Bの EventStore, Track Cの認証

**担当ファイル**（排他）:
```
backend/app/services/
├── __init__.py
├── claim_service.py        # ClaimService（CRUD + バージョニング）
├── concept_service.py      # ConceptService
├── context_service.py      # ContextService
├── evidence_service.py     # EvidenceService
├── term_service.py         # TermService
├── referent_service.py     # ReferentService
├── cir_service.py          # CIRService
├── connection_service.py   # CrossFieldConnectionService
└── search_service.py       # SearchService（横断検索）
backend/tests/test_services/
├── test_claim_service.py
├── test_concept_service.py
├── test_context_service.py
├── test_evidence_service.py
├── test_term_service.py
└── test_search_service.py
```

**作業内容**:
1. 各エンティティのCRUD（Create / Read / List with filter / Update）
2. Claim作成時にClaimCreatedイベントをEventStoreに記録
3. Claimバージョニング（更新時にversion++)
4. N:M関連の管理（Claim-Context, Claim-Concept, Claim-Evidence, Term-Concept）
5. 横断検索サービス（PostgreSQL FTS）
6. 各サービスのユニットテスト

**出力契約**: `IClaimService` 等のインターフェースを実装したサービスクラス群

**完了条件**:
- [ ] 全エンティティのCRUDが動作
- [ ] CRUD操作がEventStoreにイベントを記録する
- [ ] フィルタ付き一覧取得が動作
- [ ] 横断検索が動作

---

### Track E: Proposal/Reviewワークフロー

**参照spec**: `proposal-review/spec.md`

**入力契約**: Track Aのモデル, Track Bの EventStore, Track CのPolicyEngine

**担当ファイル**（排他）:
```
backend/app/services/
├── proposal_service.py     # ProposalService（ステートマシン）
└── review_service.py       # ReviewService
backend/app/workflows/
├── __init__.py
├── state_machine.py        # Proposalステートマシン
├── trust_transitions.py    # 信頼状態遷移ルール
└── change_applier.py       # Proposal承認時の変更適用
backend/tests/test_workflows/
├── test_state_machine.py
├── test_trust_transitions.py
├── test_change_applier.py
├── test_proposal_service.py
└── test_review_service.py
```

**作業内容**:
1. Proposalステートマシン（pending → in_review → approved/rejected/withdrawn）
2. Review作成・記録
3. Proposal承認時の変更適用（proposal_type別: create_claim, link_claims, update_trust, add_evidence, connect_concepts）
4. 信頼状態遷移ルール（ai_suggested → tentative → established ↔ disputed）
5. PolicyEngineとの連携（権限チェック、自己レビュー禁止）
6. 各ワークフローのユニットテスト

**出力契約**: `IProposalService`, `IReviewService` を実装したサービスクラス

**完了条件**:
- [ ] Proposalステートマシンの全遷移が動作
- [ ] 不正な状態遷移が拒否される
- [ ] 承認時に対象エンティティへの変更が正しく適用される
- [ ] 信頼状態遷移がルール通りに動作

---

### Track F: AI Linking Agent

**参照spec**: `linking-agent/spec.md`

**入力契約**: Track Aのモデル, Track DのClaimService/ConceptService（リード系のみ）, Track EのProposalService

**担当ファイル**（排他）:
```
backend/app/agent/
├── __init__.py
├── linking_agent.py        # LinkingAgent本体
├── trigger.py              # トリガーモジュール
├── context_collector.py    # コンテキスト収集
├── candidate_search.py     # 候補Claim検索（埋め込みベクトル含む）
├── candidate_generator.py  # LLM接続候補生成
├── proposal_formatter.py   # Proposal自動生成・重複チェック
├── prompts.py              # LLMプロンプトテンプレート
└── config.py               # 確信度閾値等の設定
backend/tests/test_agent/
├── test_linking_agent.py
├── test_context_collector.py
├── test_candidate_search.py
├── test_candidate_generator.py
└── test_proposal_formatter.py
```

**作業内容**:
1. トリガーモジュール（新規Claim/Concept検知、手動リクエスト）
2. コンテキスト収集（Claim/Concept起点で関連情報を収集）
3. 候補Claim検索（分野横断、意味的類似性）
4. LLM接続候補生成（プロンプト構築、API呼び出し、出力パース）
5. Proposal自動生成（確信度閾値フィルタ、重複チェック）
6. エラーハンドリング（リトライ、失敗ログ）
7. ユニットテスト（LLM呼び出しはモック）

**出力契約**: `ILinkingAgent` インターフェースを実装した `LinkingAgent` クラス

**注意**: Track Dのサービスのリード系メソッドに依存するが、Phase 0で定義したインターフェースに対してコーディングできるため、Track Dと同時開始可能。テスト時にはモックを使用する。

**完了条件**:
- [ ] 手動リクエストで接続候補が生成される
- [ ] 確信度閾値未満の候補がフィルタされる
- [ ] 重複Proposalが作成されない
- [ ] LLM APIエラー時にリトライが動作する

---

## Phase 3: インターフェース（4トラック並行）

> Phase 2の完了後に開始（ただしモック/スタブを使えばPhase 2と部分的に並行可能）

### Track G: REST APIエンドポイント

**参照spec**: `rest-api/spec.md`

**入力契約**: Phase 2の全サービスクラス, Track Cの認証Depends

**担当ファイル**（排他）:
```
backend/app/api/
├── __init__.py
├── router.py               # メインルーター（/api/v1 prefix）
├── claims.py               # /api/v1/claims
├── concepts.py             # /api/v1/concepts
├── contexts.py             # /api/v1/contexts
├── evidence.py             # /api/v1/evidence
├── terms.py                # /api/v1/terms
├── proposals.py            # /api/v1/proposals
├── agent.py                # /api/v1/agent
└── search.py               # /api/v1/search
backend/app/main.py          # FastAPIアプリ初期化
backend/tests/test_api/
├── test_claims_api.py
├── test_concepts_api.py
├── test_contexts_api.py
├── test_evidence_api.py
├── test_proposals_api.py
├── test_agent_api.py
└── test_search_api.py
```

**作業内容**:
1. 各エンティティのCRUDエンドポイント
2. Proposal/Reviewエンドポイント
3. Agent候補生成・一覧エンドポイント
4. 横断検索エンドポイント
5. ページネーション・フィルタリング
6. JWT認証ミドルウェア適用
7. 入力バリデーション・エラーレスポンス
8. 統合テスト

**完了条件**:
- [ ] 全エンドポイントがOpenAPI仕様に沿って動作
- [ ] 認証が全保護エンドポイントで機能
- [ ] バリデーションエラーが422で返される
- [ ] エラーレスポンスが統一フォーマット

---

### Track H: CLI

**参照spec**: `cli/spec.md`

**入力契約**: Track GのREST APIエンドポイント仕様（OpenAPI schema）

**担当ファイル**（排他）:
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
│       ├── auth.py         # cs auth login
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

**作業内容**:
1. Typer CLIフレームワーク初期化
2. APIクライアント（httpx使用）
3. 認証管理（`cs auth login`、config.toml保存）
4. 各コマンドグループ実装
5. テーブル表示（rich使用）とJSON出力モード
6. エラーハンドリング

**注意**: REST APIのOpenAPIスキーマさえあれば、APIが完成前でもクライアントコードを書ける。モックサーバーでテスト可能。

**完了条件**:
- [ ] 全コマンドがREST APIを正しく呼び出す
- [ ] `--json` モードが全コマンドで動作
- [ ] 認証設定が永続化される

---

### Track I: Web UI

**参照spec**: `web-ui/spec.md`

**入力契約**: Phase 0の `lib/types.ts`, Track GのREST APIエンドポイント仕様

**担当ファイル**（排他）:
```
frontend/
├── package.json
├── next.config.js
├── tailwind.config.js
├── src/
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx                    # ダッシュボード
│   │   ├── claims/
│   │   │   ├── page.tsx                # Claim一覧
│   │   │   └── [id]/page.tsx           # Claim詳細
│   │   ├── concepts/
│   │   │   ├── page.tsx
│   │   │   └── [id]/page.tsx
│   │   ├── contexts/
│   │   │   ├── page.tsx
│   │   │   └── [id]/page.tsx
│   │   ├── graph/page.tsx              # グラフビュー
│   │   ├── review/page.tsx             # レビューキュー
│   │   └── search/page.tsx             # 検索
│   ├── components/
│   │   ├── layout/
│   │   │   ├── Sidebar.tsx
│   │   │   ├── Header.tsx
│   │   │   └── StatsCard.tsx
│   │   ├── claims/
│   │   │   ├── ClaimCard.tsx
│   │   │   ├── ClaimTable.tsx
│   │   │   └── ClaimDetail.tsx
│   │   ├── evidence/
│   │   │   └── EvidenceCard.tsx
│   │   ├── proposals/
│   │   │   ├── ProposalCard.tsx
│   │   │   └── ReviewDialog.tsx
│   │   ├── graph/
│   │   │   └── ForceGraph.tsx
│   │   ├── common/
│   │   │   ├── FilterBar.tsx
│   │   │   ├── Pagination.tsx
│   │   │   ├── SearchBar.tsx
│   │   │   └── TrustBadge.tsx
│   │   └── cir/
│   │       └── CIRDisplay.tsx
│   └── lib/
│       ├── api.ts                      # APIクライアント
│       └── types.ts                    # 型定義（Phase 0で作成済み）
└── public/
```

**サブ分割（Track I内で更に並行可能）**:

| Sub-Track | 画面 | 担当ファイル |
|-----------|------|-------------|
| I-1 | レイアウト + ダッシュボード | `layout.tsx`, `page.tsx`, `Sidebar`, `Header`, `StatsCard` |
| I-2 | Claim一覧 + 詳細 | `claims/`, `ClaimCard`, `ClaimTable`, `ClaimDetail`, `EvidenceCard`, `CIRDisplay` |
| I-3 | Context + Concept画面 | `contexts/`, `concepts/`, `FilterBar`, `TrustBadge` |
| I-4 | レビューキュー | `review/`, `ProposalCard`, `ReviewDialog` |
| I-5 | グラフビュー | `graph/`, `ForceGraph` |
| I-6 | 検索 | `search/`, `SearchBar`, `Pagination` |

**作業内容**:
1. Next.js + Tailwind CSS 初期化
2. 共通レイアウト（サイドバー、ヘッダー）
3. APIクライアント（fetch wrapper）
4. 各画面の実装（上記サブトラック参照）
5. レスポンシブ対応（デスクトップ + タブレット）

**注意**: APIのモックデータ（MSW等）を使えば、バックエンド完成前に並行開発可能。

**完了条件**:
- [ ] 全9画面が動作
- [ ] フィルタリング・ページネーションが動作
- [ ] レビュー操作（Approve/Reject）が動作
- [ ] グラフビューでノード・エッジが表示される

---

### Track J: デモデータセット

**参照spec**: `demo-dataset/spec.md`

**入力契約**: Track Aのモデル, Track DのサービスまたはTrack GのREST API

**担当ファイル**（排他）:
```
backend/app/seeds/
├── __init__.py
├── entropy_dataset.py      # メインのSeedスクリプト
├── data/
│   ├── contexts.json       # Context定義データ
│   ├── terms.json          # Term定義データ
│   ├── concepts.json       # Concept定義データ
│   ├── claims.json         # Claim定義データ（100件+）
│   ├── evidence.json       # Evidence定義データ（30件+）
│   ├── connections.json    # Cross-field Connection定義データ
│   └── cir.json            # CIR定義データ
└── tests/
    └── test_seed.py
```

**作業内容**:
1. 5つのContext定義（Classical Thermodynamics, Statistical Mechanics, Shannon Info Theory, Quantum Info Theory, Algorithmic Info Theory）
2. Term / Concept マッピングデータ（英語・日本語）
3. 100件以上のClaim（各Context + 分野横断）
4. 30件以上のEvidence（教科書・論文）
5. Cross-field Connection初期データ（4件以上）
6. CIR例（3〜5件）
7. Seedスクリプト（冪等、CLI実行可能）

**注意**: JSONデータファイルの作成はモデルやAPIの完成を待たずに開始可能。Seedスクリプトの実装部分のみTrack A/Dに依存する。

**完了条件**:
- [ ] Seedスクリプトが冪等に実行できる
- [ ] 100件以上のClaim、30件以上のEvidence、5つのContextが投入される
- [ ] すべてのN:M関連が正しく設定される

---

## 並行度サマリー

| Phase | 並行トラック数 | 最大エージェント数 |
|-------|-----------|---------------|
| Phase 0 | 1 | 1 |
| Phase 1 | 3（A, B, C） | 3 |
| Phase 2 | 3（D, E, F） | 3 |
| Phase 3 | 4+（G, H, I, J）※Iは更に6分割可 | 4〜9 |

### 最大並行時（Phase 3）のファイル衝突マップ

各トラックが触るファイルが完全に分離されていることを確認:

```
Track G: backend/app/api/*,  backend/app/main.py
Track H: cli/*
Track I: frontend/*
Track J: backend/app/seeds/*
```

→ **衝突なし**: 4エージェントが同時に作業可能

---

## Phase間の移行条件

### Phase 0 → Phase 1

- [ ] `backend/app/schemas/` 全ファイルが作成済み
- [ ] `backend/app/interfaces/` 全ファイルが作成済み
- [ ] `frontend/src/lib/types.ts` が作成済み
- [ ] `docker-compose.yml` でPostgreSQLが起動可能
- [ ] `backend/pyproject.toml` と `frontend/package.json` が初期化済み

### Phase 1 → Phase 2

- [ ] Track A: `alembic upgrade head` が成功
- [ ] Track B: EventStoreの append/query テストがパス
- [ ] Track C: JWT認証 + PolicyEngineテストがパス

### Phase 2 → Phase 3

- [ ] Track D: 全エンティティCRUDテストがパス
- [ ] Track E: Proposalステートマシン全遷移テストがパス
- [ ] Track F: Linking Agent手動リクエストテストがパス（LLMモック）

### Phase 3 完了

- [ ] Track G: 全APIエンドポイントの統合テストがパス
- [ ] Track H: 全CLIコマンドがAPIを正しく呼び出すテストがパス
- [ ] Track I: 全画面がブラウザで表示・操作可能
- [ ] Track J: Seedスクリプトでデータ投入成功

---

## エージェントへの指示テンプレート

各トラックのエージェントに渡す指示の雛形:

```
あなたは CollectiveScience プロジェクトの [Track X: トラック名] を担当します。

## コンテキスト
- プロジェクト概要: prototype_design.md を参照
- 詳細仕様: openspec/specs/[capability]/spec.md を参照
- 共通型定義: backend/app/schemas/ を参照
- サービスインターフェース: backend/app/interfaces/ を参照

## あなたの担当範囲
[担当ファイル一覧]

## 触ってはいけないファイル
上記以外のすべてのファイル（他のトラックが担当）

## 作業内容
[作業内容リスト]

## 完了条件
[完了条件リスト]

## 依存関係
- 入力: [インポート可能なモジュール]
- 出力: [他トラックが使う成果物]
```

---

## クイックリファレンス: トラック→Spec対応

| Track | 主要参照Spec | 補助参照Spec |
|-------|------------|------------|
| A: DBスキーマ | knowledge-graph | — |
| B: Event Store | event-store | — |
| C: Trust Model | trust-model | — |
| D: ドメインサービス | knowledge-graph | event-store |
| E: Proposal/Review | proposal-review | trust-model, event-store |
| F: Linking Agent | linking-agent | proposal-review |
| G: REST API | rest-api | 全spec |
| H: CLI | cli | rest-api |
| I: Web UI | web-ui | rest-api |
| J: デモデータ | demo-dataset | knowledge-graph |
