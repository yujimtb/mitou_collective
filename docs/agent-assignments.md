# エージェント割り当て表

マルチエージェント開発時のエージェント一覧、担当範囲、および同時作業の可否を示す。

---

## エージェント一覧

| # | 名前 | 担当領域 | 排他ディレクトリ |
|---|------|---------|-----------------|
| 1 | **データ基盤** | SQLAlchemyモデル、Alembicマイグレーション、Event Store、JWT認証、PolicyEngine | `backend/app/models/` `backend/app/events/` `backend/app/auth/` `backend/alembic/` |
| 2 | **ビジネスロジック** | 12個のドメインサービス（CRUD・検索）、Proposalステートマシン、信頼状態遷移、変更適用 | `backend/app/services/` `backend/app/workflows/` |
| 3 | **REST API** | FastAPIエンドポイント（9ルート）、DI設定、エラーハンドラー、アプリ初期化 | `backend/app/api/` `backend/app/main.py` |
| 4 | **AI Agent** | LLMリンク提案パイプライン（トリガー、コンテキスト収集、候補検索、プロンプト、重複チェック） | `backend/app/agent/` |
| 5 | **Frontend** | Next.js 15 Web UI（6画面グループ、15コンポーネント、APIクライアント） | `frontend/` |
| 6 | **CLI** | Typer + httpx CLIツール（6コマンドグループ、認証管理、出力フォーマッタ） | `cli/` |
| 7 | **デモデータ** | Seedスクリプト、JSONデータファイル（6 Context, 120 Claim, 33 Evidence 等） | `backend/app/seeds/` |
| 8 | **仕様・ドキュメント** | OpenSpec仕様書（9領域）、アーキテクチャドキュメント、README | `openspec/` `docs/` ルート直下の `.md` |

---

## 並行作業 総当り表

**◯** = 安全に並行可能　**△** = 通知ルールあり　**—** = 同一エージェント

|  | 1 データ基盤 | 2 ビジネスロジック | 3 REST API | 4 AI Agent | 5 Frontend | 6 CLI | 7 デモデータ | 8 仕様・Docs |
|--|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| **1 データ基盤** | — | △ | ◯ | ◯ | ◯ | ◯ | △ | ◯ |
| **2 ビジネスロジック** | △ | — | △ | △ | ◯ | ◯ | ◯ | ◯ |
| **3 REST API** | ◯ | △ | — | ◯ | ◯ | ◯ | ◯ | ◯ |
| **4 AI Agent** | ◯ | △ | ◯ | — | ◯ | ◯ | ◯ | ◯ |
| **5 Frontend** | ◯ | ◯ | ◯ | ◯ | — | ◯ | ◯ | ◯ |
| **6 CLI** | ◯ | ◯ | ◯ | ◯ | ◯ | — | ◯ | ◯ |
| **7 デモデータ** | △ | ◯ | ◯ | ◯ | ◯ | ◯ | — | ◯ |
| **8 仕様・Docs** | ◯ | ◯ | ◯ | ◯ | ◯ | ◯ | ◯ | — |

---

## △（注意が必要）の詳細

| 組み合わせ | 依存の方向 | 何が起きうるか | 対処方法 |
|-----------|-----------|--------------|---------|
| **1↔2** データ基盤 × ビジネスロジック | 2 が 1 のモデルをインポート | Agent 1 がカラム追加・型変更すると Agent 2 のサービスが壊れる | モデル変更後に Agent 2 へ変更内容を通知。マイグレーション適用を忘れずに |
| **2↔3** ビジネスロジック × REST API | 3 が 2 のサービスをDI | Agent 2 がサービスメソッドのシグネチャを変えると Agent 3 のエンドポイントが壊れる | メソッド追加は安全。シグネチャ変更時のみ Agent 3 へ通知 |
| **2↔4** ビジネスロジック × AI Agent | 4 が 2 のサービス（リード系）を利用 | Agent 2 がリード系メソッドのシグネチャを変えると Agent 4 のパイプラインが壊れる | リード系メソッドの変更時に Agent 4 へ通知 |
| **1↔7** データ基盤 × デモデータ | 7 が 1 のモデルを直接利用してSeedする | Agent 1 がテーブル構造を変えると Seedスクリプトが壊れる | テーブル変更後に Agent 7 へ通知。JSONデータ自体の編集は常に安全 |

---

## ◯（安全な並行）の理由

| 組み合わせ | 安全な理由 |
|-----------|-----------|
| **1 × 5, 6** データ基盤 × Frontend/CLI | ファイルが完全分離。Frontend/CLI は HTTP 経由でのみバックエンドと通信 |
| **3 × 4** REST API × AI Agent | 別ディレクトリ（`api/` vs `agent/`）。同じサービスを参照するがファイル排他 |
| **3 × 5, 6** REST API × Frontend/CLI | API仕様が変わらなければ完全に独立。レスポンス形式の変更時のみ注意 |
| **5 × 6** Frontend × CLI | 完全に独立（`frontend/` vs `cli/`）。どちらもAPIをHTTP経由で利用 |
| **5 × 7** Frontend × デモデータ | 完全に独立（`frontend/` vs `seeds/`） |
| **6 × 7** CLI × デモデータ | 完全に独立（`cli/` vs `seeds/`） |
| **8 × 全て** 仕様・Docs × 全Agent | 仕様とドキュメントはコードを変更しないため、常に安全に並行可能 |

---

## 共有契約ファイル（変更時は全体に影響）

以下のファイルは複数エージェントが参照する**境界契約**。変更する場合は単一エージェントが責任を持ち、関連エージェントに通知する。

| ファイル群 | 責任エージェント | 影響を受けるエージェント |
|-----------|----------------|----------------------|
| `backend/app/schemas/` (Pydanticスキーマ) | 変更内容に最も近いエージェント | 1, 2, 3, 4, 7 |
| `backend/app/interfaces/` (サービスABC) | 変更内容に最も近いエージェント | 1, 2, 3, 4 |
| `frontend/src/lib/types.ts` (TypeScript型) | 5 Frontend | 5 のみ（バックエンドスキーマ追従） |
| `backend/tests/conftest.py` (テストfixture) | 3 REST API | 1, 2, 3, 4, 7（統合テスト利用時） |

### 変更の安全度

| 操作 | 安全度 | 通知 |
|------|-------|------|
| スキーマにOptionalフィールド追加 | 安全 | 不要 |
| スキーマのフィールド名変更・削除 | **危険** | **全関連Agent必須** |
| インターフェースにメソッド追加 | 安全 | 実装側Agentに通知 |
| インターフェースのメソッドシグネチャ変更 | **危険** | **全関連Agent必須** |
| types.ts に型追加 | 安全 | 不要 |
| types.ts のプロパティ名変更 | **危険** | **Agent 5 全画面に影響** |

---

## エージェント詳細説明

### Agent 1: データ基盤（Models / Events / Auth）

プロジェクトの最下層を担当する。すべての永続化ロジック（SQLAlchemyモデル12個、Alembicマイグレーション）、イベントソーシング基盤（Event Store、Command定義、Projection Engine）、認証・認可（JWT生成/検証、PolicyEngine権限マトリクス、FastAPI依存性注入）を管理する。

**主要な成果物:**
- 12個のSQLAlchemyモデル（Claim, Concept, Context, Evidence, Term, CIR, Actor 等）
- N:M関連テーブル（claim_contexts, claim_concepts, claim_evidence, term_concepts）
- EventStoreクラス（イベントのappend/query、sequence_number管理）
- JWT認証（python-jose使用、trust_level埋め込み）
- PolicyEngine（trust_level × 操作種別の権限チェック、自己レビュー禁止）

**このエージェントの変更が他に影響するケース:**
- カラム追加/変更 → Agent 2（サービス）、Agent 7（Seed）に影響
- イベント型追加 → Agent 2（サービスからイベント発行）に影響
- 認証ロジック変更 → Agent 3（APIエンドポイント）に影響

---

### Agent 2: ビジネスロジック（Services / Workflows）

ドメインの中核ロジックを担当する。12個のサービスクラスがエンティティのCRUD、検索、バージョニング、イベント記録を行い、ワークフローモジュールがProposalのステートマシン、信頼状態遷移、変更適用を制御する。

**主要な成果物:**
- ClaimService（CRUD + バージョニング + イベント記録）
- ConceptService, ContextService, EvidenceService, TermService 等のCRUD
- SearchService（横断検索、ILIKE）
- ProposalService（ステートマシン: pending → in_review → approved/rejected）
- ReviewService（レビュー作成、自己レビュー禁止チェック）
- ChangeApplier（Proposal承認時にエンティティへの変更を適用）
- TrustTransitions（ai_suggested → tentative → established ↔ disputed）

**このエージェントの変更が他に影響するケース:**
- サービスメソッドのシグネチャ変更 → Agent 3（API）、Agent 4（AI Agent）に影響
- 新しいサービスメソッド追加 → Agent 3 のエンドポイントから呼べるようにDI設定が必要

---

### Agent 3: REST API（API Routes + main.py）

HTTPインターフェース層を担当する。9つのAPIルートグループ（claims, concepts, contexts, evidence, terms, proposals, agent, search + auth）を管理し、FastAPIアプリの初期化、ルーター登録、CORS設定、DI設定、エラーハンドリングを行う。

**主要な成果物:**
- 9つのAPIルーターモジュール（各エンティティのCRUD + フィルタ + ページネーション）
- `dependencies.py`（サービスクラスのFastAPI DI設定）
- `errors.py`（LookupError→404、ValueError→400、PermissionError→403 のマッピング）
- `main.py`（FastAPIアプリ、ルーター登録、CORSミドルウェア、ライフスパン）

**このエージェントの変更が他に影響するケース:**
- APIレスポンス形式の変更 → Agent 5（Frontend）、Agent 6（CLI）に影響
- 新しいエンドポイント追加 → Agent 5、6 から利用可能になる

---

### Agent 4: AI Agent（Linking Agent パイプライン）

LLMを使った分野横断リンク提案の自動化パイプラインを担当する。新しいClaimやConceptが追加されたときに、他分野の関連Claimを検索し、接続提案（Proposal）を自動生成する。

**主要な成果物:**
- LinkingAgent本体（パイプライン全体の調整）
- Trigger（新規Claim/Concept検知、手動リクエスト受付）
- ContextCollector（対象Claim/Conceptの周辺情報収集）
- CandidateSearch（分野横断での候補Claim検索）
- CandidateGenerator（LLMプロンプト構築、API呼び出し、出力パース）
- ProposalFormatter（確信度閾値フィルタ、重複チェック、Proposal生成）

**このエージェントの変更が他に影響するケース:**
- LLMプロバイダー変更 → 環境変数の追加が必要
- 出力フォーマット変更 → Agent 3 の `/api/v1/agent` レスポンスに影響する可能性

---

### Agent 5: Frontend（Next.js Web UI）

ユーザー向けWeb UIを担当する。Next.js 15のApp Router + React 19 + Tailwind CSS 3.4で構成。全ページがサーバーサイドレンダリング（SSR）で、`CS_API_TOKEN` 環境変数を使ってバックエンドAPIをfetchする。

**主要な画面:**
- ダッシュボード（統計サマリー + 最新Claim/Proposal）
- Claim一覧・詳細（フィルタ、テーブル、カード、Evidence表示、CIR表示）
- Context一覧・詳細
- Concept一覧・詳細
- レビューキュー（Proposal一覧、Approve/Reject操作）
- グラフビュー（D3.js Force Graph）
- 検索

**サブ分割可能（最大6並行）:**
レイアウト、Claim画面、Context/Concept画面、レビュー、グラフ、検索の6トラックに更に分割できる。

---

### Agent 6: CLI（コマンドラインツール）

開発者・管理者向けのCLIツールを担当する。Typerフレームワーク + httpxクライアントで構成。REST APIをHTTP経由で呼び出す。

**主要コマンド:**
- `cs auth login` / `cs auth create-admin` — 認証管理
- `cs claim list/get/create/history` — Claim操作
- `cs concept list/get/connections` — Concept操作
- `cs proposal list/review` — Proposal操作
- `cs agent suggest/suggestions` — AI Agent操作
- `cs search` — 横断検索

---

### Agent 7: デモデータ（Seeds / Data）

デモンストレーション用のデータセットとSeedスクリプトを担当する。「エントロピー」をテーマに、古典熱力学・統計力学・情報理論・量子情報・アルゴリズム情報の5分野にまたがるデータを管理する。

**データ規模:**
- 6 Context（5分野 + Cross-field）
- 9 Term / 7 Concept
- 120 Claim（24 base + 96 generated）
- 33 Evidence（8 base + 25 generated）
- 4 Cross-field Connection
- 3 CIR（形式化Claim表現）

---

### Agent 8: 仕様・ドキュメント（Specs / Docs）

仕様書とドキュメントを担当する。コードには**一切触れない**。OpenSpec形式の仕様書（9領域）、アーキテクチャ文書、README等を管理する。

**管理対象:**
- `openspec/specs/` 配下の9つの仕様: knowledge-graph, event-store, trust-model, proposal-review, linking-agent, rest-api, cli, web-ui, demo-dataset
- `openspec/changes/` 配下の変更提案
- `docs/` 配下のアーキテクチャ文書、ロードマップ
- ルート直下の README.md, CONTRIBUTING.md, CODE_OF_CONDUCT.md, SECURITY.md
