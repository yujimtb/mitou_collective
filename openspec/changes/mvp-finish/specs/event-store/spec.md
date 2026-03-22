# Event Store Specification — Delta

## ADDED Requirements

### Requirement: ProjectionEngineのMVP位置づけ

MVPにおいてProjectionEngineはテスト済みの将来基盤として保持し、読み取りAPIは直接SQLクエリを使用するものとする（SHALL）。

#### Scenario: MVP読み取りパス

- **WHEN** 読み取り系APIエンドポイント（Claim一覧、Concept一覧等）がリクエストされる
- **THEN** SQLAlchemyによる直接クエリでデータを取得する（ProjectionEngineは経由しない）

#### Scenario: ProjectionEngine保持

- **WHEN** ProjectionEngineのコードが存在する
- **THEN** `backend/app/events/projections.py` のコードとテスト（`test_events/test_projections.py`）は削除せず保持する
- **THEN** コードベースにProjectionEngineがMVP後のCQRS統合向けである旨のドキュメントコメントを追記する

#### Scenario: イベント記録の継続

- **WHEN** Claim作成、Claim更新、Proposal作成等の書き込み操作が行われる
- **THEN** Event Storeへのイベント記録は引き続き実行される（将来のProjection再構築に備える）
