# Event Store Specification

## Purpose

DOKPから転用するAppend-only Event Storeを定義する。すべてのデータ変更をイベントとして不可逆に記録し、完全な監査証跡と状態の再構築を可能にする。Command Algebraにより書き込みセマンティクスを厳密に制御し、Projectionパイプラインによってリードモデルを構築する。

## Requirements

### Requirement: Append-only Event記録

システムはすべてのデータ変更をAppend-onlyのイベントとして記録しなければならない（SHALL）。イベントは一度記録されたら削除・修正されない。

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

### Requirement: Command Algebra

システムはDOKPのCommand Algebraを拡張し、知識グラフドメインに適した書き込みコマンド体系を提供しなければならない（SHALL）。

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

### Requirement: Projection パイプライン

システムはイベントストリームからリードモデル（Projection）を構築しなければならない（SHALL）。Projectionはイベントの再生によりいつでも再構築可能とする。

#### Scenario: ClaimListView Projection

- **WHEN** Claim関連イベント（Created / Updated / TrustChanged / Retracted）が記録される
- **THEN** ClaimListView（Claim一覧用リードモデル）が更新され、id、statement（先頭N文字）、claim_type、trust_status、所属Context名一覧、関連Concept数、Evidence数が一覧取得可能になる

#### Scenario: ClaimDetailView Projection

- **WHEN** 特定ClaimのID指定で詳細が要求される
- **THEN** ClaimDetailView（Claim詳細用リードモデル）から、statement全文、claim_type、trust_status、version、関連Concept一覧、属するContext一覧、紐づくEvidence一覧、CIR（存在する場合）、変更履歴が取得可能になる

#### Scenario: ConceptGraphView Projection

- **WHEN** Concept/Claim間の関連イベントが記録される
- **THEN** ConceptGraphView（グラフ表示用リードモデル）が更新され、ノード（Concept/Claim）とエッジ（関連・接続）のデータが取得可能になる

#### Scenario: ProposalQueueView Projection

- **WHEN** Proposal関連イベントが記録される
- **THEN** ProposalQueueView（レビュー待ち一覧リードモデル）が更新され、status="pending" のProposal一覧が取得可能になる

#### Scenario: CrossFieldConnectionView Projection

- **WHEN** Cross-field Connection関連イベントが記録される
- **THEN** CrossFieldConnectionView（分野間接続一覧リードモデル）が更新され、接続元Claim、接続先Claim、接続種別、確信度、承認状態が一覧取得可能になる

#### Scenario: Projection再構築

- **WHEN** 管理者がProjectionの再構築を要求する
- **THEN** システムはeventsテーブルのイベントをsequence_number順に再生し、すべてのリードモデルをスクラッチから再構築する

### Requirement: 監査証跡

Event Storeは完全な監査証跡として機能しなければならない（SHALL）。

#### Scenario: 変更者の追跡

- **WHEN** イベントが記録される
- **THEN** actor_idフィールドにより、誰（人間またはAIエージェント）がその変更を行ったかが常に追跡可能である

#### Scenario: Proposal由来の追跡

- **WHEN** Proposalの承認によってエンティティが変更される
- **THEN** イベントのproposal_idフィールドにより、どのProposalに基づく変更かが追跡可能である

#### Scenario: 任意時点の状態復元

- **WHEN** 特定のsequence_numberまたはタイムスタンプが指定される
- **THEN** その時点までのイベントを再生することで、知識グラフの過去の状態を復元できる

#### Scenario: エンティティ変更履歴

- **WHEN** 特定エンティティ（Claim等）の履歴が要求される
- **THEN** (aggregate_type, aggregate_id)で絞り込んだイベント一覧が時系列順で返される
