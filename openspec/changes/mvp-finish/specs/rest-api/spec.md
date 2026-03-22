# REST API Specification — Delta

## MODIFIED Requirements

### Requirement: Claim API

システムはClaimに対するCRUD操作および関連情報の取得をREST APIで提供しなければならない（SHALL）。

#### Scenario: Claim一覧のContextフィルタ（ID指定）

- **WHEN** `GET /api/v1/claims?context={context_id}` がContext IDをクエリパラメータとしてリクエストされる
- **THEN** `context` パラメータがUUID形式の場合、Context IDとして照合し、当該Contextに属するClaimのみが返される
- **THEN** `context` パラメータがUUID形式でない場合、Context名として照合する（後方互換）

#### Scenario: Claim撤回（論理削除）

- **WHEN** `DELETE /api/v1/claims/{id}` がリクエストされる
- **THEN** Claimのtrust_statusが `retracted` に遷移し、`ClaimRetracted` イベントがEvent Storeに記録される
- **THEN** 200 OKとともに撤回済みClaimが返される
- **THEN** 既に `retracted` 状態のClaimに対してリクエストされた場合、409 Conflictが返される

#### Scenario: Claim変更履歴取得（整形済み）

- **WHEN** `GET /api/v1/claims/{id}/history` がリクエストされる
- **THEN** 各イベントが以下のフィールドを持つ整形済みオブジェクトとして返される: `title`（イベント種別の人間可読名）、`summary`（変更概要）、`actor_name`（実行者名）、`timestamp`（ISO 8601形式）、`event_type`（元のイベント種別）
- **THEN** Actor名はactor_idからActorテーブルを参照して解決される

## ADDED Requirements

### Requirement: 最新アクティビティAPI

システムはプラットフォーム全体の最新イベントを取得するAPIを提供しなければならない（SHALL）。

#### Scenario: 最新アクティビティ取得

- **WHEN** `GET /api/v1/events/recent` がリクエストされる
- **THEN** Event Storeから直近のイベントが最大20件、時系列降順でJSON形式で返される
- **THEN** 各イベントは以下のフィールドを持つ: `id`、`kind`（イベントカテゴリ: claim_created / proposal_created / review_completed / connection_added）、`title`（人間可読なタイトル）、`summary`（変更概要）、`actor_name`（実行者名）、`timestamp`（ISO 8601形式）、`href`（該当エンティティへのパス）
- **THEN** クエリパラメータ `limit`（デフォルト: 10、最大: 50）で取得件数を制御できる
