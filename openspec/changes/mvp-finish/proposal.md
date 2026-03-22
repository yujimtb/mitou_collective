## Why

CollectiveScienceプロトタイプは `mvp-completion` changeにより LLM接続とエンティティ作成フォームが追加されたが、`prototype_design.md` Section 1.1 のMVP要件と照合すると以下の12ギャップが残っている。これらが未解決のままでは「研究者・企業担当者にデモ可能な動くWebプロトタイプ」の基準を満たせない。

1. **Context絞り込みが動作しない（バグ）** — フロントエンドがContext IDを送信するが、バックエンドはContext名で照合しており、フィルタ結果が常に空になる
2. **Claim変更履歴が空白表示** — バックエンドが生イベントを返すが、フロントエンドが `title`/`summary`/`actor_name` を期待しており不一致
3. **Term一覧・詳細UIが未実装** — バックエンドAPIは存在するがフロントエンドページがない
4. **Evidence一覧・詳細UIが未実装** — 同上
5. **AI候補専用ページがない** — Claim詳細に埋め込まれているのみで設計書のAI候補一覧画面が欠落
6. **グラフビューが静的カード表示** — 設計書が要求するインタラクティブ力指向グラフ（D3.js / Cytoscape.js）になっていない
7. **ダッシュボードの最新アクティビティが空** — `recentActivity: []` がハードコードされている
8. **DELETE系エンドポイントがゼロ** — Claim撤回（ClaimRetracted）がイベント定義済みだがAPIが存在しない
9. **CLIにContext/Term/Evidence/Concept作成コマンドがない** — 設計書のCRUD要件を満たしていない
10. **Docker Compose起動時にマイグレーション・シードが走らない** — 初回起動が失敗する
11. **E2Eテスト・フロントエンドテストがゼロ** — 設計書Week 7-8の要件
12. **ProjectionEngineが接続されていない** — 実装済みだがAPIから参照されておらず、設計書のCQRS意図から乖離

## What Changes

### Backend — バグ修正・API拡張

- Claim一覧のContextフィルタをID照合に修正（`claim_service.py`）
- Claim変更履歴エンドポイントを整形済みレスポンスに改修（`claim_service.py`, `claims.py`）
- `DELETE /api/v1/claims/{id}` Claim撤回エンドポイントを追加
- `GET /api/v1/events/recent` 最新アクティビティエンドポイントを追加
- Docker Composeのbackendエントリポイントにマイグレーション・シードステップを追加

### Frontend — 画面追加・グラフ刷新

- Term一覧・詳細ページ（`/terms`, `/terms/[id]`）を新設
- Evidence一覧・詳細ページ（`/evidence`, `/evidence/[id]`）を新設
- AI候補一覧ページ（`/suggestions`）を新設
- ForceGraphコンポーネントをD3.js力指向グラフに置換
- ダッシュボードの最新アクティビティを実APIから取得
- Claim詳細の変更履歴表示を修正

### CLI — コマンド追加

- `cs context list/get/create` コマンドを追加
- `cs term list/get/create` コマンドを追加
- `cs evidence list/get/create` コマンドを追加
- `cs concept create` サブコマンドを追加

### テスト・インフラ

- バックエンドE2Eテスト（Claim作成→Agent提案→レビュー承認の通しフロー）
- フロントエンドコンポーネントテスト（ForceGraph, FilterBar, ClaimDetail）
- Docker Composeマイグレーション・シード自動化

## Capabilities

### New Capabilities

なし（新しいspec領域の追加はない）

### Modified Capabilities

- `rest-api`: Context IDフィルタ修正、Claim撤回エンドポイント、最新アクティビティAPI、変更履歴整形
- `web-ui`: Term/Evidence/AI候補ページ追加、力指向グラフ、ダッシュボード・履歴修正
- `cli`: Context/Term/Evidence/Concept作成コマンド追加
- `event-store`: ProjectionEngineの位置づけ明文化（MVP後の統合を前提）

## Impact

- **Agent 2（ビジネスロジック）**: `claim_service.py` のContextフィルタ修正、履歴整形メソッド追加
- **Agent 3（REST API）**: `claims.py` にDELETEエンドポイント追加、イベントAPI新設、履歴レスポンス修正
- **Agent 5（Frontend）**: 新規3ページ、ForceGraph置換、ダッシュボード・履歴修正、`api.ts`/`types.ts` 更新
- **Agent 6（CLI）**: 新規3コマンドモジュール + concept create追加
- **環境変数**: 追加なし（既存のLLM設定とDB設定で完結）
- **依存パッケージ**: Frontend に `d3`/`@types/d3` または `react-force-graph-2d` を追加。Frontend テスト用に `vitest` + `@testing-library/react` を追加
- **テスト**: バックエンドE2Eテスト新設、フロントエンドテスト新設
- **Docker**: `backend/entrypoint.sh` 新設、`docker-compose.yml` 更新
