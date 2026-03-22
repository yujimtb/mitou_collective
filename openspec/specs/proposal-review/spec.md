# Proposal-Review Workflow Specification

## Purpose

AIエージェントと人間の協調編集をシステムの書き込みセマンティクスとして実装する。AIの提案（Proposal）はレビューを経てApprove / Rejectされ、この過程でレビュアーは「人間」にハードコードせず、信頼水準に応じてAIにも委任可能な抽象的レビュアーとして設計する。

## Requirements

### Requirement: Proposal作成

システムはProposal（提案）を作成・管理しなければならない（SHALL）。ProposalはAIまたは人間による知識グラフへの変更提案を構造化して記録する。

#### Scenario: Proposal作成（手動）

- **WHEN** ユーザーがproposal_type、target_entity_type、target_entity_id（既存の場合）、payload、rationaleを指定してProposalを作成する
- **THEN** システムはUUID、proposal_type、proposed_by（ActorRef）、target_entity_type、target_entity_id、payload（JSONB）、rationale、status="pending"、created_atを持つProposalレコードを永続化する
- **THEN** `ProposalCreated` イベントがEvent Storeに記録される

#### Scenario: Proposal作成（AI Linking Agent）

- **WHEN** AI Linking Agentが異分野間の接続候補を生成する
- **THEN** proposal_type="connect_concepts" のProposalが自動的に作成される
- **THEN** proposed_byにはAIエージェントのActorRefが設定される

#### Scenario: Proposal種別

- **WHEN** Proposalが作成される
- **THEN** proposal_typeは以下のいずれかでなければならない: `create_claim`（Claim新規作成）、`link_claims`（Claim間リンク）、`update_trust`（信頼状態変更）、`add_evidence`（Evidence追加）、`connect_concepts`（Concept間接続）

### Requirement: Proposalステートマシン

Proposalは厳密なステートマシンに従って状態遷移しなければならない（SHALL）。

#### Scenario: 初期状態

- **WHEN** Proposalが作成される
- **THEN** statusは "pending" に設定される

#### Scenario: レビュー開始

- **WHEN** レビュアーがpending状態のProposalのレビューを開始する
- **THEN** statusは "in_review" に遷移する

#### Scenario: 承認（Approve）

- **WHEN** レビュアーがin_review状態のProposalを承認する
- **THEN** statusは "approved" に遷移する
- **THEN** `ProposalApproved` イベントがEvent Storeに記録される
- **THEN** payloadに基づいて対象エンティティへの変更が適用される（対応するイベントが記録される）

#### Scenario: 却下（Reject）

- **WHEN** レビュアーがin_review状態のProposalを却下する
- **THEN** statusは "rejected" に遷移する
- **THEN** `ProposalRejected` イベントがEvent Storeに記録される
- **THEN** 対象エンティティへの変更は適用されない

#### Scenario: 取り下げ（Withdraw）

- **WHEN** 提案者本人がpendingまたはin_review状態のProposalを取り下げる
- **THEN** statusは "withdrawn" に遷移する

#### Scenario: 不正な状態遷移の拒否

- **WHEN** approved、rejected、またはwithdrawn状態のProposalに対して状態遷移が要求される
- **THEN** システムはその操作を拒否し、エラーを返す

### Requirement: Review記録

システムはReview（レビュー記録）を永続化しなければならない（SHALL）。

#### Scenario: Review作成

- **WHEN** レビュアーがProposalに対してレビューを行う
- **THEN** システムはUUID、proposal_id、reviewer_id（ActorRef）、decision、comment、confidence、created_atを持つReviewレコードを永続化する

#### Scenario: Reviewの決定種別

- **WHEN** Reviewが作成される
- **THEN** decisionは以下のいずれかでなければならない: `approve`（承認）、`reject`（却下）、`request_changes`（修正要求）

#### Scenario: Review確信度

- **WHEN** Reviewが作成される
- **THEN** オプションのconfidenceフィールドに0.0〜1.0の範囲でレビュアーの確信度を記録できる

#### Scenario: 複数レビュー

- **WHEN** 1つのProposalに対して複数のレビュアーがReviewを提出する
- **THEN** システムはすべてのReviewを個別に記録し、最終的な決定は設定されたポリシーに従って決定される

### Requirement: Proposal承認時の変更適用

Proposalが承認された場合、payloadに基づいて知識グラフへの変更が自動的に適用されなければならない（SHALL）。

#### Scenario: create_claim Proposal承認

- **WHEN** proposal_type="create_claim" のProposalが承認される
- **THEN** payloadに含まれるstatement、claim_type、context_ids、concept_idsに基づいてClaimが作成される
- **THEN** `ClaimCreated` イベントがEvent Storeに記録され、proposal_idが紐づけられる

#### Scenario: link_claims Proposal承認

- **WHEN** proposal_type="link_claims" のProposalが承認される
- **THEN** payloadに含まれるsource_claim_id、target_claim_id、connection_typeに基づいてCross-field Connectionが作成される
- **THEN** `CrossFieldLinkApproved` イベントがEvent Storeに記録される

#### Scenario: update_trust Proposal承認

- **WHEN** proposal_type="update_trust" のProposalが承認される
- **THEN** 対象Claimのtrust_statusが指定の値に更新される
- **THEN** `ClaimTrustChanged` イベントがEvent Storeに記録される

#### Scenario: add_evidence Proposal承認

- **WHEN** proposal_type="add_evidence" のProposalが承認される
- **THEN** Evidenceが作成され、対象Claimとの関連が記録される
- **THEN** `EvidenceCreated` および `EvidenceLinkedToClaim` イベントがEvent Storeに記録される

#### Scenario: connect_concepts Proposal承認

- **WHEN** proposal_type="connect_concepts" のProposalが承認される
- **THEN** payloadに含まれる情報に基づいてCross-field Connectionが作成される
- **THEN** `CrossFieldLinkApproved` イベントがEvent Storeに記録される

### Requirement: 信頼状態遷移ルール

Claimのtrust_statusは定義された遷移ルールに従わなければならない（SHALL）。

#### Scenario: AI提案から暫定へ

- **WHEN** trust_status="ai_suggested" のClaimに対するレビューが承認される
- **THEN** trust_statusは "tentative" に遷移する

#### Scenario: 暫定から確立へ

- **WHEN** trust_status="tentative" のClaimに追加のEvidence（reliability="high"）が紐づけられ、レビューで承認される
- **THEN** trust_statusは "established" に遷移可能とする

#### Scenario: 確立から論争中へ

- **WHEN** trust_status="established" のClaimに反証Evidence（relationship="contradicts"）が紐づけられる
- **THEN** trust_statusは "disputed" に遷移可能とする

#### Scenario: 論争の解決

- **WHEN** trust_status="disputed" のClaimについて論争が解決される
- **THEN** trust_statusは "established" に遷移する、または当該Claimが撤回（`ClaimRetracted` イベント）される
