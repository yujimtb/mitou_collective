# Knowledge Graph Data Model Specification

## Purpose

CollectiveScienceの中核データモデルを定義する。Claim（主張）を中心ノードとし、Term（語）/ Concept（意味）/ Referent（指示物）の三層分離、Context（理論文脈）による多元的構造、Evidence（根拠）による信頼性の裏付け、CIR（Controlled Intermediate Representation）による構造化表現を統合的に扱う知識グラフである。

## Requirements

### Requirement: Term Entity

システムはTerm（語）エンティティを管理しなければならない（SHALL）。Termは自然言語における表層形（surface form）を表し、同一の概念が異なる語で表現される場合、および同一の語が異なる概念を指す場合の両方を構造的に扱う。

#### Scenario: Term作成

- **WHEN** ユーザーが表層形（surface_form）、言語コード（language）、オプションの分野ヒント（field_hint）を指定してTermを作成する
- **THEN** システムはUUID、surface_form、language、field_hint、created_at、created_by を持つTermレコードを永続化する

#### Scenario: 同一表層形の複数Term

- **WHEN** 同じsurface_form（例: "entropy"）で異なるfield_hint（例: "thermodynamics" と "information_theory"）を持つTermが作成される
- **THEN** システムはそれぞれ独立したTermレコードとして保持し、それぞれが異なるConceptに紐づくことを許容する

#### Scenario: 多言語Term

- **WHEN** 同一Conceptに対して異なるlanguage（例: "en" → "entropy", "ja" → "エントロピー"）のTermが登録される
- **THEN** システムは各Termを個別に保持し、term_concepts関連テーブルを介して同一Conceptに紐づける

### Requirement: Concept Entity

システムはConcept（意味）エンティティを管理しなければならない（SHALL）。Conceptは特定の分野における意味的単位を表し、Termとは多対多で関連する。

#### Scenario: Concept作成

- **WHEN** ユーザーがlabel、description、field、オプションのreferent_idを指定してConceptを作成する
- **THEN** システムはUUID、label、description、field、referent_id、created_at、created_byを持つConceptレコードを永続化する

#### Scenario: Concept-Term関連付け

- **WHEN** ConceptとTermの関連付けが行われる
- **THEN** システムはterm_concepts関連テーブルに（term_id, concept_id）の組を記録する
- **THEN** 1つのConceptに複数のTerm、1つのTermに複数のConceptが紐づくことを許容する（N:M）

#### Scenario: 同一語・異なる意味の区別

- **WHEN** "entropy" というTermが "Thermodynamic Entropy" Conceptと "Shannon Entropy" Conceptの両方に関連づけられている
- **THEN** システムはそれぞれの関連を独立に保持し、Concept経由で意味の違いを明確に区別できる

### Requirement: Referent Entity

システムはReferent（指示物）エンティティを管理しなければならない（SHALL）。Referentは対象世界における指示物を表し、Conceptが何を指しているかを明示する。

#### Scenario: Referent作成

- **WHEN** ユーザーがlabel、descriptionを指定してReferentを作成する
- **THEN** システムはUUID、label、description、created_at、created_byを持つReferentレコードを永続化する

#### Scenario: Concept-Referent関連付け

- **WHEN** ConceptにReferentが設定される
- **THEN** Conceptのreferent_idフィールドにReferentのidが記録される
- **THEN** 複数のConceptが同一のReferentを共有できる

### Requirement: Claim Entity（中心ノード）

システムはClaim（主張）を知識グラフの中心ノードとして管理しなければならない（SHALL）。Claimは特定の文脈における知識の主張を表し、Concept、Context、Evidenceと多対多で関連する。

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

### Requirement: Context Entity

システムはContext（理論文脈）エンティティを管理しなければならない（SHALL）。Contextは特定の理論的枠組み・前提条件の集合を表し、competing theoriesの共存を構造的に可能にする。

#### Scenario: Context作成

- **WHEN** ユーザーがname、description、field、assumptions（前提条件リスト）、オプションのparent_context_idを指定してContextを作成する
- **THEN** システムはUUID、name（一意）、description、field、assumptions（JSON配列）、parent_context_id、created_at、created_byを持つContextレコードを永続化する

#### Scenario: Context階層構造

- **WHEN** Contextにparent_context_idが設定される
- **THEN** 親子関係を辿ることでContextの階層構造を表現できる（例: "Statistical Mechanics" → "Quantum Statistical Mechanics"）

#### Scenario: Competing Theories の共存

- **WHEN** 同一の物理量について異なる理論的立場のContextが存在する（例: "Classical Thermodynamics" と "Statistical Mechanics"）
- **THEN** それぞれのContextに属するClaimは独立に管理され、どちらのContextも正当な文脈として共存する

### Requirement: Evidence Entity

システムはEvidence（根拠）エンティティを管理しなければならない（SHALL）。EvidenceはClaimの信頼性を裏付ける根拠情報を表す。

#### Scenario: Evidence作成

- **WHEN** ユーザーがevidence_type、title、source、オプションのexcerptを指定してEvidenceを作成する
- **THEN** システムはUUID、evidence_type、title、source、excerpt、reliability（デフォルト: unverified）、created_at、created_byを持つEvidenceレコードを永続化する

#### Scenario: Evidence種別（evidence_type）

- **WHEN** Evidenceが作成される
- **THEN** evidence_typeは以下のいずれかでなければならない: `textbook`（教科書）、`paper`（論文）、`experiment`（実験）、`proof`（証明）、`expert_opinion`（専門家意見）

#### Scenario: Evidence信頼性（reliability）

- **WHEN** Evidenceが存在する
- **THEN** reliabilityは以下のいずれかでなければならない: `high`、`medium`、`low`、`unverified`

#### Scenario: Evidence-Claim関連付け

- **WHEN** EvidenceがClaimに関連付けられる
- **THEN** claim_evidence関連テーブルに（claim_id, evidence_id, relationship）の組が記録される
- **THEN** relationshipは以下のいずれか: `supports`（支持）、`contradicts`（反証）、`partially_supports`（部分的支持）

### Requirement: CIR（Controlled Intermediate Representation）

システムはCIR（制約付き中間表現）を管理しなければならない（SHALL）。CIRは自然言語Claimの構造化表現であり、型・単位・定義参照・前提条件の整合性を検査可能にする。

#### Scenario: CIR作成

- **WHEN** Claimに対してCIRが作成される
- **THEN** システムはUUID、claim_id（一意）、context_ref、subject、relation、object、conditions（JSON配列）、units、definition_refs（JSON配列）、created_atを持つCIRレコードを永続化する

#### Scenario: CIR Condition構造

- **WHEN** CIRのconditionsが設定される
- **THEN** 各conditionは predicate（条件述語）、argument（対象）、negated（否定フラグ）を持つオブジェクトの配列である

#### Scenario: CIRの例（エントロピー第二法則）

- **WHEN** 「孤立系ではエントロピーは減少しない」というClaimのCIRが作成される
- **THEN** context_ref="Thermodynamics_Classical"、subject="entropy(system)"、relation="non_decreasing_over_time"、conditions=[{predicate: "isolated", argument: "system", negated: false}, {predicate: "macroscopic", argument: "system", negated: false}] が記録される

#### Scenario: Claim-CIR一意制約

- **WHEN** 1つのClaimに対してCIRが作成される
- **THEN** 1つのClaimには最大1つのCIRのみが関連付けられる（claim_idはCIRテーブルで一意）

### Requirement: Cross-field Connection

システムは異分野間接続（Cross-field Connection）を明示的に管理しなければならない（SHALL）。

#### Scenario: 接続の作成

- **WHEN** 2つの異なるContextに属するClaim間の接続が作成される
- **THEN** システムはUUID、source_claim_id、target_claim_id、connection_type、description、confidence、proposal_id、status、created_atを持つレコードを永続化する

#### Scenario: 接続種別（connection_type）

- **WHEN** Cross-field Connectionが作成される
- **THEN** connection_typeは以下のいずれかでなければならない: `equivalent`（同値）、`analogous`（類似）、`generalizes`（一般化）、`contradicts`（矛盾）、`complements`（補完）

#### Scenario: 接続の信頼度

- **WHEN** AI Linking Agentが接続を提案する
- **THEN** 0.0〜1.0の範囲でconfidence（確信度）スコアが付与される
