# Trust Model Specification

## Purpose

人間とAIエージェントを統一的に扱うアクターモデルと、段階的自律性レビューを可能にする信頼水準モデルを定義する。レビュアーを「人間」にハードコードせず、AIの能力向上に応じてレビュー権限を段階的に拡大できるアーキテクチャを実現する。

## Requirements

### Requirement: ActorRef（行為者参照）

システムは人間とAIエージェントを統一的なActorRef（行為者参照）で管理しなければならない（SHALL）。

#### Scenario: 人間Actorの登録

- **WHEN** 人間ユーザーがシステムに登録される
- **THEN** actor_type="human"、name、trust_level、created_atを持つActorレコードが作成される
- **THEN** agent_modelフィールドはNULLとなる

#### Scenario: AIエージェントActorの登録

- **WHEN** AIエージェントがシステムに登録される
- **THEN** actor_type="ai_agent"、name、trust_level、agent_model（例: "gpt-4o", "claude-3.5-sonnet"）、created_atを持つActorレコードが作成される

#### Scenario: Actor識別の一貫性

- **WHEN** Event Store、Proposal、Reviewにおいてactor_idが記録される
- **THEN** すべてのケースで同一のActorRefテーブルを参照し、人間/AIの区別なく一貫したIDで追跡可能とする

### Requirement: 信頼水準（Trust Level）

システムは段階的な信頼水準を管理し、各Actorの操作権限を制御しなければならない（SHALL）。

#### Scenario: 信頼水準の定義

- **WHEN** Actorの信頼水準が参照される
- **THEN** trust_levelは以下のいずれかである: `admin`（管理者）、`reviewer`（レビュアー）、`contributor`（貢献者）、`observer`（閲覧者）

#### Scenario: admin権限

- **WHEN** Actorのtrust_level="admin" である
- **THEN** すべてのCRUD操作、Proposalの作成・レビュー、他Actorの信頼水準変更、Projectionの再構築を実行できる

#### Scenario: reviewer権限

- **WHEN** Actorのtrust_level="reviewer" である
- **THEN** すべてのCRUD操作、Proposalの作成・レビュー（Approve / Reject）を実行できる
- **THEN** 他Actorの信頼水準変更はできない

#### Scenario: contributor権限

- **WHEN** Actorのtrust_level="contributor" である
- **THEN** エンティティの閲覧、Proposalの作成、自身のProposalの取り下げを実行できる
- **THEN** Proposalのレビュー（Approve / Reject）はできない

#### Scenario: observer権限

- **WHEN** Actorのtrust_level="observer" である
- **THEN** すべてのエンティティの閲覧のみ可能であり、変更操作はできない

### Requirement: 段階的自律性レビューモデル

システムはAIエージェントのレビュー権限を段階的に拡大できるレビュー自律性レベルを管理しなければならない（SHALL）。

#### Scenario: Level 0（MVPデフォルト）

- **WHEN** レビュー自律性がLevel 0に設定されている
- **THEN** すべてのProposalは人間のレビュアーによるレビューを必要とする
- **THEN** AIエージェントのtrust_levelは最大で "contributor" に制限される

#### Scenario: Level 1（AIフィルタリング）

- **WHEN** レビュー自律性がLevel 1に設定されている
- **THEN** AIエージェントは低品質候補（確信度が閾値未満）の自動却下が可能となる
- **THEN** 残りのProposalは人間によるレビューを必要とする

#### Scenario: Level 2（AI部分自律）

- **WHEN** レビュー自律性がLevel 2に設定されている
- **THEN** AIエージェントはリスク分類が"low"のProposal（例: Evidence追加、既存Claimへのタグ付け）を自動承認できる
- **THEN** リスク分類が"high"のProposal（例: Claim新規作成、Cross-field Connection）は人間によるレビューを必要とする

#### Scenario: Level 3（将来拡張）

- **WHEN** レビュー自律性がLevel 3に設定されている
- **THEN** AIエージェントはContext内の通常Proposalを自律的にレビュー・承認できる
- **THEN** Context間接続、構造変更等の高次の判断は人間によるレビューを必要とする

### Requirement: 権限チェック（PolicyEngine転用）

システムはすべての操作に対して権限チェックを実行しなければならない（SHALL）。DOKPのPolicyEngineを転用し、ActorRefのtrust_levelと操作種別に基づいてアクセス制御する。

#### Scenario: 操作の権限チェック

- **WHEN** 任意のActor（人間またはAI）が操作を要求する
- **THEN** システムはActorのtrust_levelと要求された操作種別を照合し、権限がない場合は操作を拒否してエラーを返す

#### Scenario: AIエージェントのレビュー操作チェック

- **WHEN** AIエージェントがProposalのレビュー（Approve / Reject）を要求する
- **THEN** システムは現在のレビュー自律性レベルとProposalのリスク分類を確認し、権限範囲内であれば操作を許可する

#### Scenario: 自己レビューの禁止

- **WHEN** Proposalの提案者と同一のActorがそのProposalのレビューを試みる
- **THEN** システムはその操作を拒否する（提案者は自身のProposalをレビューできない）
