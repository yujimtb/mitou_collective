## MODIFIED Requirements

### Requirement: Append-only Event記録

システムはすべてのデータ変更をAppend-onlyのイベントとして記録しなければならない（SHALL）。イベントは一度記録されたら削除・修正されない。イベント書き込みはドメインデータの書き込みと単一トランザクション境界内で実行されなければならない（SHALL）。

#### Scenario: イベントの永続化

- **WHEN** 任意のエンティティに対する変更操作が実行される
- **THEN** システムはイベントレコード（id、sequence_number、event_type、aggregate_type、aggregate_id、payload、actor_id、proposal_id、created_at）をeventsテーブルにINSERTする
- **THEN** sequence_numberは厳密に単調増加する

#### Scenario: イベントの不変性

- **WHEN** eventsテーブルに記録されたイベントが存在する
- **THEN** そのイベントのUPDATEおよびDELETEは許可されない（SHALL NOT）

#### Scenario: 高速検索用インデックス

- **WHEN** イベントが記録される
- **THEN** (aggregate_type, aggregate_id) および (sequence_number) にインデックスが存在し、特定集約のイベント一覧取得とグローバル順序での走査が高速に行える

#### Scenario: ドメイン書き込みとイベント書き込みの原子性

- **WHEN** サービスがドメインデータをDBにコミットし、対応するイベントを記録する
- **THEN** ドメイン書き込みとイベント書き込みは同一トランザクション内で実行される
- **THEN** イベント書き込みが失敗した場合、ドメイン書き込みもロールバックされる

#### Scenario: イベント書き込み失敗時のロールバック

- **WHEN** ドメインデータのコミット後にイベント書き込みが失敗する
- **THEN** ドメインデータの変更もロールバックされ、データとイベントの整合性が維持される
