# ロードマップ

> **🇯🇵 日本語** | [English](#roadmap)

## 現在の状態

本プロジェクトは `mvp-completion` 後の動作するフルスタックプロトタイプですが、`prototype_design.md` セクション1.1に記述されたデモ対応MVPとなるには、もう1パスの集中的な作業が必要です。

### 実装済みベースライン

- **データモデル**: コア研究エンティティ用のSQLAlchemyモデルとAlembicマイグレーション
- **イベントストア**: テスト済みプロジェクションユーティリティを持つ追記専用イベントログ
- **認証・認可**: JWTログインと4段階信頼モデル、ポリシーチェック
- **ドメインサービス**: バックエンド全体のCRUD、検索、ワークフロー、イベント記録サービス
- **Proposalワークフロー**: 人間レビューによるpending/in-review/approved/rejectedライフサイクル
- **AIリンキングエージェント**: API準備チェック付きプロバイダーバック提案生成パイプライン
- **REST API**: ページネーション、フィルタリング、エラーハンドリング付き認証済みルートグループ
- **フロントエンド**: SSR、ダッシュボード、グラフビュー、Claim詳細、コアエンティティ作成ダイアログを備えたNext.jsアプリ
- **CLI**: テーブルおよびJSON出力を持つ既存の運用コマンドグループ
- **デモデータセット**: 複数研究分野にまたがるエントロピーテーマのシードコンテンツ
- **テスト**: バックエンド自動テストの実装と通過を確認
- **Docker Compose**: PostgreSQL、バックエンド、フロントエンドサービスをローカルで一括起動可能

## MVP仕上げ変更（`mvp-finish`）

`mvp-finish` 変更は、現在のプロトタイプとデモ可能なMVPの間の残り12のギャップを解消します。

1. Context IDを受け付けつつ名前ベースフォールバックを維持することで、壊れたContextフィルターを修正。
2. 人間可読なタイトル、サマリー、アクター名、タイムスタンプを持つフォーマット済みClaim履歴を返却。
3. 不足しているTerm一覧/詳細/作成UIを追加。
4. 不足しているEvidence一覧/詳細UIを追加。
5. 専用のAI提案ページを追加。
6. 静的グラフカードレイアウトをインタラクティブなフォースグラフに置き換え。
7. ダッシュボードのハードコードされた空のアクティビティフィードを実際の最新イベントデータに置き換え。
8. Claim撤回（`DELETE /api/v1/claims/{id}`）をソフトデリートスタイルワークフローとして追加。
9. 不足しているCLIコマンド（Context、Term、Evidence、`concept create`）を追加。
10. マイグレーション、オプショナルシード、ヘルスチェック、ロックファイル修正でDockerスタートアップをMVP安全に。
11. MVP信頼性に必要な最小限のフロントエンド/コンポーネントおよびE2Eスタイルテストカバレッジを追加。
12. `ProjectionEngine` がMVP後のCQRS基盤として保持されており、現在のリードパスの一部ではないことを明確化。

### 計画された実行フロー

- **Phase 1**: サービス修正、フロントエンド基盤作業、CLIコマンド、Agent 8ドキュメント更新
- **Phase 2**: 新しいサービスレイヤー動作に依存するREST API変更
- **Phase 3**: フロントエンド/API統合とDockerスタートアップ強化
- **Phase 4**: 実装完了後のフォローアップテストと仕様同期

### ProjectionEngineドキュメント注記

タスク `7.1` はAgent 8のドキュメント担当作業です。以下のモジュールコメントテキストは、実装エージェントがファイルを更新する際に `backend/app/events/projections.py` の先頭に適用する文言です：

```python
"""
ProjectionEngine is retained as a tested foundation for post-MVP CQRS integration.
During the MVP phase, read APIs continue to use direct SQLAlchemy queries rather
than projection-backed read models. Events are still recorded so projections can
be rebuilt later when the CQRS read path is introduced.
"""
```

## 近期目標

1. `mvp-finish` 変更を完了・検証し、プロダクトをMVPデモスコープに合致させる。
2. グラフ操作、フィルタリング、エンティティ作成フローのUXを改善する。
3. 初期MVPスモークテストを超えるCLIおよびフロントエンド自動カバレッジを拡大する。
4. より明確な運用ガイダンスとCompose設定でローカル環境の信頼性を向上する。
5. すべての実装タスク完了後にメインOpenSpecドキュメントの同期を準備する。

## 中期目標

1. MVPベースラインが安定したらCQRSバックリードモデルを導入する。
2. 候補検索にセマンティック類似性のためのベクトル埋め込みを導入する。
3. より豊富なエビデンスモデリングと来歴追跡をサポートする。
4. ユーザー登録とOAuth認証を追加する。
5. Proposal状態変更のリアルタイム通知を実装する。
6. デプロイと運用ガイダンスの正式化。
7. 分野横断リンク品質評価のための評価シナリオを構築する。

## 長期ビジョン

1. TermとClaimの多言語サポート。
2. 複数のTsumuGraphインスタンス間のフェデレーション。
3. AIエージェントの自律性レベル（全人間レビューから半自律まで）。
4. 協調編集と競合解決。
5. パブリックAPIとパートナー向けインテグレーション。

---

# Roadmap

> **🇬🇧 English** | [日本語](#ロードマップ)

## Current State

The project is a working full-stack prototype after `mvp-completion`, but it still needs one focused pass to become the demo-ready MVP described in `prototype_design.md` section 1.1.

### Implemented baseline

- **Data model**: SQLAlchemy models and Alembic migrations for the core research entities
- **Event store**: Append-only event log with tested projection utilities retained in the codebase
- **Authentication and authorization**: JWT login plus the four-tier trust model and policy checks
- **Domain services**: CRUD, search, workflow, and event recording services across the backend
- **Proposal workflow**: Pending/in-review/approved/rejected lifecycle with human review
- **AI linking agent**: Provider-backed proposal generation pipeline with API readiness checks
- **REST API**: Authenticated route groups with pagination, filtering, and error handling
- **Frontend**: Next.js app with SSR, dashboard, graph view, claim detail, and create dialogs for core entities
- **CLI**: Existing operational command groups with table and JSON output
- **Demo dataset**: Seed content for the entropy theme across multiple research fields
- **Testing**: Backend automated tests are in place and passing
- **Docker Compose**: PostgreSQL, backend, and frontend services can run together locally

## MVP Finish Change (`mvp-finish`)

The `mvp-finish` change closes the remaining 12 gaps between the current prototype and a demoable MVP.

1. Fix the broken Context filter by accepting Context IDs while preserving name-based fallback.
2. Return formatted Claim history with human-readable titles, summaries, actor names, and timestamps.
3. Add the missing Term list/detail/create UI.
4. Add the missing Evidence list/detail UI.
5. Add a dedicated AI suggestions page.
6. Replace the static graph card layout with an interactive force-directed graph.
7. Replace the dashboard's hard-coded empty activity feed with real recent-event data.
8. Add Claim retraction (`DELETE /api/v1/claims/{id}`) as a soft-delete style workflow.
9. Add the missing CLI commands for Context, Term, Evidence, and `concept create`.
10. Make Docker startup MVP-safe with migration, optional seed, health check, and lockfile fixes.
11. Add the minimum frontend/component and end-to-end style test coverage needed for MVP confidence.
12. Clarify that `ProjectionEngine` is retained as a post-MVP CQRS foundation rather than part of the current read path.

### Planned execution flow

- **Phase 1**: Service fixes, frontend foundation work, CLI commands, and Agent 8 documentation updates
- **Phase 2**: REST API changes that depend on the new service-layer behavior
- **Phase 3**: Frontend/API integration and Docker startup hardening
- **Phase 4**: Follow-up tests and spec sync after implementation is complete

### ProjectionEngine documentation note

Task `7.1` is documentation-owned work for Agent 8. The following module comment text is the wording to apply at the top of `backend/app/events/projections.py` when the implementation agent updates that file:

```python
"""
ProjectionEngine is retained as a tested foundation for post-MVP CQRS integration.
During the MVP phase, read APIs continue to use direct SQLAlchemy queries rather
than projection-backed read models. Events are still recorded so projections can
be rebuilt later when the CQRS read path is introduced.
"""
```

## Near-Term Goals

1. Finish and verify the `mvp-finish` change so the product matches the MVP demo scope.
2. Tighten the UX around graph interaction, filtering, and entity creation flows.
3. Expand CLI and frontend automated coverage beyond the initial MVP smoke tests.
4. Improve local environment reliability with clearer operational guidance and compose defaults.
5. Prepare the main OpenSpec documents for sync once all implementation tasks are done.

## Medium-Term Goals

1. Introduce CQRS-backed read models when the MVP baseline is stable.
2. Embed vectors for semantic similarity in candidate search.
3. Support richer evidence modeling and provenance tracking.
4. Add user registration and OAuth authentication.
5. Implement real-time notifications for proposal state changes.
6. Formalize deployment and operational guidance.
7. Build evaluation scenarios for cross-field link quality assessment.

## Long-Term Vision

1. Multi-language support for terms and claims.
2. Federation across multiple TsumuGraph instances.
3. AI agent autonomy levels, from human-review-all to semi-autonomous.
4. Collaborative editing and conflict resolution.
5. Public API and partner-facing integrations.
