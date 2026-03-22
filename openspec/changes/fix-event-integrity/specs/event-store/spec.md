## MODIFIED Requirements

### Requirement: Command Algebra

システムはDOKPのCommand Algebraを拡張し、知識グラフドメインに適した書き込みコマンド体系を提供しなければならない（SHALL）。イベントペイロードは正確なデータを格納しなければならない（SHALL）。

#### Scenario: Claimコマンド

- **WHEN** Claimに対する操作が行われる
- **THEN** 以下のイベント種別のいずれかが記録される: `ClaimCreated`、`ClaimUpdated`、`ClaimTrustChanged`、`ClaimRetracted`

#### Scenario: Conceptコマンド

- **WHEN** Conceptに対する操作が行われる
- **THEN** 以下のイベント種別のいずれかが記録される: `ConceptCreated`、`ConceptUpdated`、`ConceptLinkedToClaim`

#### Scenario: Evidenceコマンド

- **WHEN** Evidenceに対する操作が行われる
- **THEN** 以下のイベント種別のいずれかが記録される: `EvidenceCreated`、`EvidenceLinkedToClaim`

#### Scenario: Contextコマンド

- **WHEN** Contextに対する操作が行われる
- **THEN** 以下のイベント種別のいずれかが記録される: `ContextCreated`、`ContextUpdated`

#### Scenario: Proposalコマンド

- **WHEN** Proposalに対する操作が行われる
- **THEN** 以下のイベント種別のいずれかが記録される: `ProposalCreated`、`ProposalApproved`、`ProposalRejected`

#### Scenario: Cross-field Connectionコマンド

- **WHEN** 分野間接続に対する操作が行われる
- **THEN** 以下のイベント種別のいずれかが記録される: `CrossFieldLinkProposed`、`CrossFieldLinkApproved`、`CrossFieldLinkRejected`

#### Scenario: イベントペイロード

- **WHEN** イベントが記録される
- **THEN** payloadフィールドにはJSONB形式で操作の詳細（変更前後の値、関連エンティティID等）が格納される

#### Scenario: ClaimCreatedイベントのcontext_names正確性

- **WHEN** `ClaimCreated`イベントが記録される
- **THEN** `context_names`フィールドには関連するContextの`name`値（人間可読ラベル）が格納される
- **THEN** Context IDやUUIDは`context_names`フィールドに格納されてはならない（SHALL NOT）

#### Scenario: イベントhrefの有効性

- **WHEN** イベントの`href`が生成される
- **THEN** `href`はフロントエンドに存在する有効なルートを指さなければならない（SHALL）
- **THEN** Proposalイベントの`href`は `/review` を指す（`/proposals/{id}` ではない）
