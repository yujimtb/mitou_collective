## MODIFIED Requirements

### Requirement: Claim Entity（中心ノード）

システムはClaim（主張）を知識グラフの中心ノードとして管理しなければならない（SHALL）。Claimは特定の文脈における知識の主張を表し、Concept、Context、Evidenceと多対多で関連する。関連IDの指定時は全IDの存在を検証しなければならない（SHALL）。

#### Scenario: Claim作成

- **WHEN** ユーザーがstatement（自然言語記述）、claim_type、関連するContext、関連するConceptを指定してClaimを作成する
- **THEN** システムはUUID、statement、claim_type、trust_status（デフォルト: tentative）、version（デフォルト: 1）、created_at、created_byを持つClaimレコードを永続化する

#### Scenario: Claim種別（claim_type）

- **WHEN** Claimが作成される
- **THEN** claim_typeは以下のいずれかでなければならない: `definition`（定義）、`theorem`（定理）、`empirical`（経験的事実）、`conjecture`（推測）、`meta`（メタ主張）

#### Scenario: 信頼状態（trust_status）

- **WHEN** Claimが存在する
- **THEN** trust_statusは以下のいずれかでなければならない: `established`（確立済み）、`tentative`（暫定的）、`disputed`（論争中）、`ai_suggested`（AI提案）

#### Scenario: Claim-Context関連付け

- **WHEN** ClaimがContextに関連付けられる
- **THEN** claim_contexts関連テーブルに（claim_id, context_id）の組が記録される
- **THEN** 1つのClaimが複数のContextに属すること、1つのContextに複数のClaimが属することを許容する（N:M）

#### Scenario: Claim-Concept関連付け

- **WHEN** ClaimがConceptに関連付けられる
- **THEN** claim_concepts関連テーブルに（claim_id, concept_id, role）の組が記録される
- **THEN** roleのデフォルト値は "related" とする

#### Scenario: Claimバージョニング

- **WHEN** Claimが更新される
- **THEN** versionフィールドがインクリメントされる
- **THEN** 変更はEvent Storeにイベントとして記録され、過去の状態を復元可能とする

#### Scenario: 存在しない関連ID指定の拒否

- **WHEN** Claim作成または更新時に、存在しないContext ID、Concept ID、Evidence IDが指定される
- **THEN** システムはリクエスト全体を拒否し、400エラーを返す
- **THEN** 部分的な関連付けは行わない（全IDが有効な場合のみコミットする）

#### Scenario: 関連ID存在検証（Concept）

- **WHEN** Concept作成または更新時に、存在しないTerm IDまたはReferent IDが指定される
- **THEN** システムはリクエスト全体を拒否し、400エラーを返す

#### Scenario: 関連ID存在検証（Term）

- **WHEN** Term作成または更新時に、存在しないConcept IDが指定される
- **THEN** システムはリクエスト全体を拒否し、400エラーを返す
