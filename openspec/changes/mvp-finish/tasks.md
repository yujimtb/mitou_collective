## 1. Agent 2: ビジネスロジック修正・追加（Backend — Services）

- [x] 1.1 `backend/app/services/claim_service.py`の`list()`メソッド（L82-83）を修正する。`context`パラメータがUUID形式の場合は`Context.id`で照合し、UUID形式でない場合は`Context.name`で照合するフォールバック処理を実装する
- [x] 1.2 `backend/app/services/claim_service.py`に`history_formatted(claim_id: UUID) -> list[dict]`メソッドを追加する。Event Storeからイベントを取得し、`title`（EVENT_TYPE_LABELSによる人間可読名）、`summary`（変更概要）、`actor_name`（actor_idからActorテーブルで解決）、`timestamp`（ISO 8601）、`event_type`を含む整形済みオブジェクトのリストを返す
- [x] 1.3 `backend/app/services/claim_service.py`に`EVENT_TYPE_LABELS`辞書を追加する。`claim_created` → "Claim作成"、`claim_updated` → "Claim更新"、`claim_retracted` → "Claim撤回"、`trust_status_changed` → "信頼状態変更"、`evidence_linked` → "Evidence紐付け"等のマッピングを定義する
- [x] 1.4 `backend/app/services/claim_service.py`に`retract(claim_id: UUID, actor_id: UUID) -> ClaimRead`メソッドを追加する。`trust_status`を`retracted`に変更し、`ClaimRetracted`イベントをEvent Storeに記録する。既に`retracted`の場合は`ConflictError`を発生させる
- [x] 1.5 Event Store関連サービスに`recent_events(limit: int = 10) -> list[dict]`メソッドを追加する。直近Nイベントを時系列降順で取得し、`id`、`kind`、`title`、`summary`、`actor_name`、`timestamp`、`href`を含む整形済みオブジェクトのリストを返す
- [x] 1.6 `backend/tests/test_services/`にContextフィルタ修正のテストを追加する（UUID指定、名前指定、不正UUID指定の3ケース）
- [x] 1.7 `backend/tests/test_services/`に`history_formatted()`のテスト（イベントあり、イベントなし、actor名解決）を追加する
- [x] 1.8 `backend/tests/test_services/`に`retract()`のテスト（正常撤回、二重撤回409、存在しないClaim404）を追加する

## 2. Agent 3: REST APIエンドポイント追加・修正（Backend — API）

- [x] 2.1 `backend/app/api/claims.py`に`DELETE /api/v1/claims/{id}`エンドポイントを追加する。`ClaimService.retract()`を呼び出し、成功時に200 + 撤回済みClaimを返す。`ConflictError`は409にマッピングする
- [x] 2.2 `backend/app/api/claims.py`の`GET /api/v1/claims/{id}/history`エンドポイントを修正し、`ClaimService.history_formatted()`を呼び出して整形済みレスポンスを返すようにする
- [x] 2.3 `backend/app/api/`に最新アクティビティ用エンドポイント`GET /api/v1/events/recent`を追加する。クエリパラメータ`limit`（デフォルト10、最大50）を受け取り、整形済みイベントリストを返す
- [x] 2.4 `backend/app/api/errors.py`に`ConflictError` → 409のマッピングを追加する（既存パターンに追従）
- [x] 2.5 `backend/app/main.py`のルーター登録にeventsルーターを追加する（必要な場合）
- [x] 2.6 `docker-compose.yml`にバックエンドのヘルスチェック設定を追加する。`entrypoint.sh`でのマイグレーション→条件付きシード→uvicorn起動の3ステップエントリーポイントを設定する
- [x] 2.7 `backend/entrypoint.sh`を新設する。`alembic upgrade head` → `SEED_ON_STARTUP=true`時のシード実行 → `exec uvicorn`の3ステップ
- [x] 2.8 `docker-compose.yml`のフロントエンドサービスにlock fileコピーの修正を適用する
- [x] 2.9 `backend/tests/test_api/`にClaim撤回エンドポイントのテスト（正常撤回200、二重撤回409、存在しないClaim404）を追加する
- [x] 2.10 `backend/tests/test_api/`に最新アクティビティエンドポイントのテスト（デフォルトlimit、カスタムlimit、空リスト）を追加する

## 3. Agent 5: フロントエンド新規画面（Frontend — Web UI）

- [x] 3.1 `frontend/src/app/terms/page.tsx`を新設する。Term一覧をテーブル形式で表示し（surface_form、language、field_hint、関連Concept数）、検索ボックスと言語フィルターを実装する
- [x] 3.2 `frontend/src/app/terms/[id]/page.tsx`を新設する。Term詳細表示（surface_form、language、field_hint、関連Conceptタグ一覧）を実装する
- [x] 3.3 Term一覧画面に「新規Term作成」モーダルダイアログを追加する。surface_form（必須）、language（セレクト）、field_hint、関連Concept（マルチセレクト）のフォームを実装する
- [x] 3.4 `frontend/src/app/evidence/page.tsx`を新設する。Evidence一覧をカード形式で表示し（title、evidence_type、source概要、reliability、関連Claim数）、evidence_typeとreliabilityによるフィルタリングを実装する
- [x] 3.5 `frontend/src/app/evidence/[id]/page.tsx`を新設する。Evidence詳細表示（title、evidence_typeバッジ、sourceリンク、excerpt引用ブロック、reliabilityインジケーター、関連Claimカード一覧with関係バッジ）を実装する
- [x] 3.6 `frontend/src/app/suggestions/page.tsx`を新設する。AI候補一覧をカード形式で表示し（proposal_type、接続元/先Claim、connection_type、確信度バー、rationale概要）、status・最低確信度スライダーによるフィルタリング、インラインApprove/Reject操作を実装する

## 4. Agent 5: フロントエンド既存画面修正（Frontend — Web UI）

- [x] 4.1 `frontend/src/components/graph/ForceGraph.tsx`を`react-force-graph-2d`ベースに全面書き換える。`next/dynamic`で`ssr: false`のdynamic importを使用し、既存の`GraphData`型からノード・リンクデータを変換する。ノード種類（Claim/Concept）の色分け、クリックでツールチップ表示、ドラッグ対応、ズーム/パン操作を実装する
- [x] 4.2 `frontend/src/lib/api.ts`の`getDashboardData()`を修正する。`recentActivity: []`のハードコードを`GET /api/v1/events/recent`のAPIコールに置き換える
- [x] 4.3 ダッシュボード画面（`frontend/src/app/page.tsx`または`dashboard/page.tsx`）の最新アクティビティセクションを修正する。APIから取得したアクティビティを時系列順で表示し、各項目にタイトル・概要・実行者名・タイムスタンプ・リンクを含める
- [x] 4.4 Claim詳細画面（`frontend/src/app/claims/[id]/page.tsx`）の履歴セクションを修正する。整形済み履歴APIレスポンス（title、summary、actor_name、timestamp）をタイムライン形式で表示する
- [x] 4.5 `frontend/src/lib/types.ts`にTerm関連の型（`TermRead`, `TermCreateInput`）、Evidence関連の型（`EvidenceRead`拡張）、アクティビティ型（`RecentActivity`）、整形済み履歴型（`FormattedHistoryEvent`）を追加する
- [x] 4.6 `frontend/src/lib/api.ts`にTerm CRUD関数（`listTerms`, `getTerm`, `createTerm`）、Evidence CRUD関数（`listEvidence`, `getEvidence`）、`getRecentActivity()`、`retractClaim()`を追加する
- [x] 4.7 ナビゲーションメニューに「Terms」「Evidence」「AI Suggestions」のリンクを追加する

## 5. Agent 5: フロントエンドテスト（Frontend — Web UI）

- [x] 5.1 `frontend/`にVitest + @testing-library/reactの設定を追加する。`vitest.config.ts`、`vitest.setup.ts`（@testing-library/jest-dom拡張）を新設する
- [x] 5.2 `frontend/src/components/graph/__tests__/ForceGraph.test.tsx`を新設する。GraphDataを渡してレンダリングされること、ノードクリックでツールチップが表示されることをテストする
- [x] 5.3 主要コンポーネント（FilterBar, ClaimCard等）のスモークテストを追加する。正常なpropsでエラーなくレンダリングされることを確認する
- [x] 5.4 `package.json`に`"test": "vitest"`スクリプトを追加し、`devDependencies`にvitest、@testing-library/react、@testing-library/jest-domを追加する

## 6. Agent 6: CLIコマンド追加（CLI）

- [x] 6.1 `cli/commands/context.py`を新設する。`list`（テーブル表示、`--field`フィルタ、`--json`出力）、`get <id>`（詳細表示）、`create`（`--name`, `--field`, `--description`, `--assumptions`, `--parent`）コマンドを実装する
- [x] 6.2 `cli/commands/term.py`を新設する。`list`（テーブル表示、`--language`フィルタ、`--search`、`--json`出力）、`get <id>`（詳細表示）、`create`（`--surface-form`, `--language`, `--field-hint`, `--concept`複数指定）コマンドを実装する
- [x] 6.3 `cli/commands/evidence.py`を新設する。`list`（テーブル表示、`--type`フィルタ、`--json`出力）、`get <id>`（詳細表示）、`create`（`--title`, `--type`, `--source`, `--excerpt`, `--reliability`, `--claim`複数指定）コマンドを実装する
- [x] 6.4 既存の`cli/commands/concept.py`に`create`コマンドを追加する。`--label`, `--field`, `--description`, `--term`（複数指定）, `--referent`オプションを実装する
- [x] 6.5 `cli/main.py`（またはアプリ登録箇所）に`context`, `term`, `evidence`サブアプリを登録する
- [x] 6.6 `cli/tests/`にContext, Term, Evidence, Concept createコマンドのテストを追加する（API呼び出しのモック、正常系・エラー系）

## 7. Agent 8: 仕様・ドキュメント更新（Specs / Docs）

- [x] 7.1 `backend/app/events/projections.py`の先頭にProjectionEngineがMVP後のCQRS統合向けである旨のドキュメントコメントを追記する（Agent 8がopenspec/docs担当のため、コメント文案をドキュメントとして提供し、実装エージェントに適用を委譲）
- [x] 7.2 `docs/roadmap.md`を更新し、`mvp-finish`チェンジの内容（12ギャップの解消）を反映する
- [x] 7.3 `openspec/specs/rest-api/spec.md`にデルタスペックの内容（Context IDフィルタ、Claim撤回、整形済み履歴、最新アクティビティAPI）を反映する（mvp-finish完了後のspec sync時）
- [x] 7.4 `openspec/specs/web-ui/spec.md`にデルタスペックの内容（Term画面、Evidence画面、AI候補画面、グラフ修正、ダッシュボード修正）を反映する（mvp-finish完了後のspec sync時）
- [x] 7.5 `openspec/specs/cli/spec.md`にデルタスペックの内容（Context, Term, Evidence, Concept createコマンド）を反映する（mvp-finish完了後のspec sync時）

## 依存関係と推奨実行順序

**Phase 1（並行実行可能）:**
- Agent 2: タスク 1.1〜1.5（サービス層の修正・追加）
- Agent 5: タスク 3.1〜3.6, 4.5〜4.7, 5.1, 5.4（新規画面、型定義、テスト基盤 — APIモックで開発可能）
- Agent 6: タスク 6.1〜6.5（CLIコマンド — 既存APIを利用）
- Agent 8: タスク 7.1〜7.2（ドキュメント更新）

**Phase 2（Agent 2完了後）:**
- Agent 3: タスク 2.1〜2.5, 2.9〜2.10（APIエンドポイント — Agent 2のサービスメソッドに依存）

**Phase 3（Agent 3完了後）:**
- Agent 5: タスク 4.1〜4.4, 4.6（既存画面修正・APIクライアント — 実APIレスポンス形式に依存）
- Agent 3: タスク 2.6〜2.8（Docker Compose — API安定後）

**Phase 4（全実装完了後）:**
- Agent 5: タスク 5.2〜5.3（コンポーネントテスト）
- Agent 6: タスク 6.6（CLIテスト）
- Agent 8: タスク 7.3〜7.5（spec sync）
