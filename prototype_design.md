# CollectiveScience プロトタイプ設計書

## 1. 概要

学問分野を横断する知識を構造化・接続・検証するためのClaim中心知識グラフプラットフォーム「CollectiveScience」のプロトタイプ設計。人類とエージェンティックAIの集合知により、異分野間の概念対応関係を継続的に構築する。

### 1.1 プロトタイプの目標（Phase 1: MVP）

- Claim中心データモデルの実装（Term / Concept / Claim / Context / Evidence / Proposal / Review）
- CRUD操作と一覧・詳細表示UI
- AIによる異分野間接続候補提案機能（Linking Agent MVP）
- Approve / Reject レビューワークフロー（レビュアーの抽象化含む）
- エントロピー概念を題材としたデモデータセット投入
- 研究者・企業担当者にデモ可能な動くWebプロトタイプ

---

## 2. アーキテクチャ概要

```
┌─────────────────────────────────────────────────┐
│                   Frontend (Web UI)              │
│   React / Next.js                                │
│   ┌──────────┐ ┌──────────┐ ┌────────────────┐  │
│   │Claim一覧 │ │詳細表示  │ │レビューパネル  │  │
│   │& 絞り込み│ │& 関連表示│ │Approve/Reject  │  │
│   └──────────┘ └──────────┘ └────────────────┘  │
└──────────────────┬──────────────────────────────┘
                   │ REST API / GraphQL
┌──────────────────▼──────────────────────────────┐
│                 Backend (API Server)              │
│   Rust (Axum) or Python (FastAPI)                │
│   ┌──────────┐ ┌──────────┐ ┌────────────────┐  │
│   │Domain    │ │Proposal/ │ │Linking Agent   │  │
│   │Service   │ │Review    │ │(AI接続候補)    │  │
│   │(CRUD)    │ │Workflow  │ │                │  │
│   └────┬─────┘ └────┬─────┘ └───────┬────────┘  │
│        │             │               │            │
│   ┌────▼─────────────▼───────────────▼────────┐  │
│   │         Event Store (Append-only)         │  │
│   │         DOKP 転用層                        │  │
│   └────────────────┬──────────────────────────┘  │
└────────────────────┼────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────┐
│              Database (PostgreSQL)                │
│   Events Table / Projections / Search Index      │
└─────────────────────────────────────────────────┘
```

### 2.1 技術スタック

| レイヤー | 技術選定 | 理由 |
|---------|---------|------|
| Frontend | Next.js (React) + TypeScript | SSR対応、豊富なエコシステム |
| Backend API | Python (FastAPI) | LLM連携の容易さ、迅速なMVP開発 |
| Event Store | PostgreSQL + Append-only設計 | DOKP設計の転用、信頼性 |
| Knowledge Graph Store | PostgreSQL + pg_graphql or Neo4j | グラフクエリ最適化 |
| 全文検索 | PostgreSQL FTS or Meilisearch | Claim/Term検索 |
| AI/LLM | OpenAI API / Claude API | 接続候補生成、構造化支援 |
| CLI | Python (Click/Typer) | API連携、スクリプタブル |

---

## 3. データモデル設計

### 3.1 コアエンティティ

```
┌──────────┐      ┌───────────┐      ┌──────────┐
│  Term    │──N:M─│  Concept  │──N:M─│ Referent │
│ (語)     │      │ (意味)    │      │ (対象)   │
└──────────┘      └─────┬─────┘      └──────────┘
                        │ N:M
                  ┌─────▼─────┐
                  │  Claim    │
                  │ (主張)    │
                  └──┬────┬───┘
               N:M  │    │  N:M
          ┌─────────▼┐  ┌▼──────────┐
          │ Context  │  │ Evidence  │
          │ (文脈)   │  │ (根拠)    │
          └──────────┘  └───────────┘
```

### 3.2 エンティティ定義

#### Term（語）

```yaml
Term:
  id: UUID
  surface_form: string          # 表層形（例: "entropy", "エントロピー"）
  language: string              # 言語コード（en, ja, etc.）
  field_hint: string?           # 分野ヒント（例: "thermodynamics"）
  created_at: datetime
  created_by: ActorRef
```

#### Concept（意味）

```yaml
Concept:
  id: UUID
  label: string                 # 概念ラベル（例: "Thermodynamic Entropy"）
  description: string           # 概念の説明
  field: string                 # 所属分野（例: "thermodynamics"）
  terms: Term[]                 # この概念を指すTerm群（N:M）
  referent_id: UUID?            # 対象世界の指示物（あれば）
  created_at: datetime
  created_by: ActorRef
```

#### Referent（指示物）

```yaml
Referent:
  id: UUID
  label: string                 # 指示物ラベル（例: "Physical quantity: disorder measure"）
  description: string
  created_at: datetime
  created_by: ActorRef
```

#### Claim（主張）— 中心ノード

```yaml
Claim:
  id: UUID
  statement: string             # 主張の自然言語記述
  claim_type: enum              # definition | theorem | empirical | conjecture | meta
  trust_status: enum            # established | tentative | disputed | ai_suggested
  contexts: Context[]           # 属するContext群（N:M）
  concepts: Concept[]           # 関連するConcept群（N:M）
  evidence: Evidence[]          # 根拠群（N:M）
  cir: CIR?                    # 構造化中間表現（オプション）
  created_at: datetime
  created_by: ActorRef
  version: integer
```

#### Context（理論文脈）

```yaml
Context:
  id: UUID
  name: string                  # 文脈名（例: "Classical Thermodynamics"）
  description: string
  field: string                 # 分野名
  assumptions: string[]         # 前提条件リスト
  parent_context_id: UUID?      # 親文脈（階層構造用）
  created_at: datetime
  created_by: ActorRef
```

#### Evidence（根拠）

```yaml
Evidence:
  id: UUID
  evidence_type: enum           # textbook | paper | experiment | proof | expert_opinion
  title: string                 # 根拠タイトル
  source: string                # 出典情報（DOI, ISBN, URL等）
  excerpt: string?              # 関連引用箇所
  reliability: enum             # high | medium | low | unverified
  claims: Claim[]               # 支持するClaim群（N:M）
  created_at: datetime
  created_by: ActorRef
```

#### Proposal（提案）

```yaml
Proposal:
  id: UUID
  proposal_type: enum           # create_claim | link_claims | update_trust | add_evidence | connect_concepts
  proposed_by: ActorRef         # 提案者（人間 or AIエージェント）
  target_entity_type: string    # 対象エンティティ種別
  target_entity_id: UUID?       # 対象エンティティID（既存の場合）
  payload: JSON                 # 提案内容（型はproposal_typeによる）
  rationale: string             # 提案理由
  status: enum                  # pending | approved | rejected | withdrawn
  created_at: datetime
  reviewed_at: datetime?
  reviewed_by: ActorRef?
```

#### Review（レビュー）

```yaml
Review:
  id: UUID
  proposal_id: UUID             # 対象Proposal
  reviewer: ActorRef            # レビュアー（人間 or AIエージェント）
  decision: enum                # approve | reject | request_changes
  comment: string?              # コメント
  confidence: float?            # 判断の確信度（0.0〜1.0）
  created_at: datetime
```

#### ActorRef（行為者参照）— レビュアー抽象化

```yaml
ActorRef:
  id: UUID
  actor_type: enum              # human | ai_agent
  name: string
  trust_level: enum             # admin | reviewer | contributor | observer
  agent_model: string?          # AIの場合のモデル名
```

### 3.3 CIR（Controlled Intermediate Representation）

```yaml
CIR:
  claim_id: UUID
  context: string               # Context名参照
  subject: string               # 主語（型付き）
  relation: string              # 関係述語
  object: string?               # 目的語（あれば）
  conditions: Condition[]       # 前提条件リスト
  units: string?                # 単位（あれば）
  definition_refs: UUID[]       # 参照する定義Claim
```

```yaml
Condition:
  predicate: string             # 条件述語（例: "isolated"）
  argument: string              # 対象（例: "system"）
  negated: boolean              # 否定かどうか
```

**CIR例 — 「孤立系ではエントロピーは減少しない」:**

```yaml
cir:
  context: "Thermodynamics_Classical"
  subject: "entropy(system)"
  relation: "non_decreasing_over_time"
  conditions:
    - predicate: "isolated"
      argument: "system"
      negated: false
    - predicate: "macroscopic"
      argument: "system"
      negated: false
  definition_refs: [<entropy_definition_claim_id>]
```

---

## 4. Event Store 設計（DOKP転用）

### 4.1 Command Algebra

DOKPから転用するAppend-onlyイベントストア設計。すべての変更をイベントとして記録する。

```yaml
Event:
  id: UUID
  sequence_number: bigint       # グローバル通番
  event_type: string            # コマンド種別
  aggregate_type: string        # 対象集約種別（Claim, Concept, etc.）
  aggregate_id: UUID            # 対象集約ID
  payload: JSON                 # イベントデータ
  actor: ActorRef               # 実行者
  timestamp: datetime
  proposal_id: UUID?            # 対応するProposal（あれば）
```

**イベント種別:**

| カテゴリ | イベント |
|---------|---------|
| Claim | ClaimCreated, ClaimUpdated, ClaimTrustChanged, ClaimRetracted |
| Concept | ConceptCreated, ConceptUpdated, ConceptLinkedToClaim |
| Evidence | EvidenceCreated, EvidenceLinkedToClaim |
| Context | ContextCreated, ContextUpdated |
| Proposal | ProposalCreated, ProposalApproved, ProposalRejected |
| Connection | CrossFieldLinkProposed, CrossFieldLinkApproved, CrossFieldLinkRejected |

### 4.2 Projection パイプライン

イベントストリームから現在の状態ビューを構築する。

```
Events → Projection Engine → Read Models (PostgreSQL Views / Materialized Views)
                                ├── ClaimListView（一覧用）
                                ├── ClaimDetailView（詳細用）
                                ├── ConceptGraphView（グラフ表示用）
                                ├── ProposalQueueView（レビュー待ち一覧）
                                └── CrossFieldConnectionView（分野間接続一覧）
```

---

## 5. APIエンドポイント設計

### 5.1 REST API

```
# --- Claim ---
GET    /api/v1/claims                    # Claim一覧（フィルタ: context, field, trust_status, search）
POST   /api/v1/claims                    # Claim作成
GET    /api/v1/claims/{id}               # Claim詳細（関連Concept, Evidence, Context含む）
PUT    /api/v1/claims/{id}               # Claim更新
GET    /api/v1/claims/{id}/history       # Claim変更履歴

# --- Concept ---
GET    /api/v1/concepts                  # Concept一覧
POST   /api/v1/concepts                  # Concept作成
GET    /api/v1/concepts/{id}             # Concept詳細（関連Term, Claim含む）
GET    /api/v1/concepts/{id}/connections # 異分野接続一覧

# --- Context ---
GET    /api/v1/contexts                  # Context一覧
POST   /api/v1/contexts                  # Context作成
GET    /api/v1/contexts/{id}             # Context詳細（属するClaim一覧含む）

# --- Evidence ---
GET    /api/v1/evidence                  # Evidence一覧
POST   /api/v1/evidence                  # Evidence作成
GET    /api/v1/evidence/{id}             # Evidence詳細

# --- Term ---
GET    /api/v1/terms                     # Term一覧（検索対応）
POST   /api/v1/terms                     # Term作成
GET    /api/v1/terms/{id}               # Term詳細（関連Concept一覧）

# --- Proposal / Review ---
GET    /api/v1/proposals                 # Proposal一覧（フィルタ: status, proposed_by）
POST   /api/v1/proposals                 # Proposal作成
GET    /api/v1/proposals/{id}            # Proposal詳細
POST   /api/v1/proposals/{id}/review     # Review投稿（Approve / Reject）

# --- AI Linking Agent ---
POST   /api/v1/agent/suggest-connections # 接続候補生成リクエスト
GET    /api/v1/agent/suggestions         # 生成済み候補一覧
```

### 5.2 CLI

```bash
# Claim操作
cs claim list [--context <name>] [--field <name>] [--trust <status>]
cs claim get <id>
cs claim create --statement "..." --context <name> --type <type>
cs claim history <id>

# Concept操作
cs concept list [--field <name>]
cs concept get <id>
cs concept connections <id>

# Proposal操作
cs proposal list [--status pending]
cs proposal review <id> --approve [--comment "..."]
cs proposal review <id> --reject --comment "..."

# AI接続候補
cs agent suggest --concept <id> [--target-field <name>]
cs agent suggestions [--status pending]

# 検索
cs search "entropy" [--scope claims|concepts|terms]
```

---

## 6. AI Linking Agent 設計

### 6.1 アーキテクチャ

```
┌──────────────────────────────────────────────────┐
│               Linking Agent                       │
│                                                   │
│  ┌──────────┐   ┌─────────────┐   ┌───────────┐ │
│  │Trigger   │──▶│Candidate    │──▶│Proposal   │ │
│  │Module    │   │Generator    │   │Formatter  │ │
│  │(新規Claim│   │(LLM + Graph │   │(Proposal  │ │
│  │ 検知)    │   │ Traversal)  │   │ 生成)     │ │
│  └──────────┘   └─────────────┘   └───────────┘ │
└──────────────────────────────────────────────────┘
```

### 6.2 接続候補生成フロー

1. **トリガー**: 新規Claim作成、新規Concept追加、手動リクエスト
2. **コンテキスト収集**: 対象Claimの関連Concept、Context、既存Evidence、隣接Claimを収集
3. **候補生成（LLM）**:
   - 対象Claimと同一/類似Conceptが存在する他分野のClaimを検索
   - LLMに以下を入力:
     - 対象Claimとその文脈情報
     - 候補となる他分野のClaim群
   - LLMに以下を出力させる:
     - 接続の種類（equivalent / analogous / generalizes / contradicts / complements）
     - 接続の理由（自然言語）
     - 確信度スコア（0.0〜1.0）
4. **Proposal生成**: 候補をProposalとしてキューに投入
5. **レビュー**: 人間（またはAI）がApprove / Reject

### 6.3 LLMプロンプト設計（概要）

```
あなたは学際的知識の専門家です。以下のClaimについて、他分野との接続候補を提案してください。

【対象Claim】
- Statement: {claim.statement}
- Context: {context.name} ({context.field})
- Related Concepts: {concepts}

【候補となる他分野のClaim群】
{candidate_claims}

各候補について以下を出力してください:
1. 接続先Claim ID
2. 接続種別: equivalent / analogous / generalizes / contradicts / complements
3. 接続理由（2-3文）
4. 確信度（0.0〜1.0）
5. 注意点・前提条件の差異
```

---

## 7. レビューワークフロー設計

### 7.1 段階的自律性モデル

```
Level 0: 全Proposalを人間がレビュー（MVP デフォルト）
Level 1: AIが事前フィルタリング（低品質候補の自動却下）
Level 2: AIが低リスクProposalを自動承認（人間は高リスクのみ）
Level 3: AIがContext内の通常Proposalを自律レビュー（人間はContext間・構造変更のみ）
```

### 7.2 Proposalステートマシン

```
                    ┌──────────┐
    作成 ──────────▶│ pending  │
                    └────┬─────┘
                         │ レビュー
                    ┌────▼─────┐
              ┌─────│ in_review│─────┐
              │     └──────────┘     │
              ▼                      ▼
       ┌──────────┐          ┌──────────┐
       │ approved │          │ rejected │
       └────┬─────┘          └──────────┘
            │ イベント適用
       ┌────▼─────┐
       │ applied  │
       └──────────┘
```

### 7.3 信頼状態遷移

```
ai_suggested ──(レビュー承認)──▶ tentative
tentative ──(追加Evidence)──▶ established
established ──(反証Evidence)──▶ disputed
disputed ──(解決)──▶ established or retracted
```

---

## 8. フロントエンド画面設計

### 8.1 画面一覧

| 画面 | 概要 | 主要コンポーネント |
|------|------|-------------------|
| ダッシュボード | 全体概要、最新Proposal、統計 | Stats Cards, Recent Activity |
| Claim一覧 | Context・分野・信頼状態でフィルタ可能な一覧 | FilterBar, ClaimTable, Pagination |
| Claim詳細 | Claim本文、関連Concept、Evidence、変更履歴 | ClaimHeader, ConceptTags, EvidenceCards, HistoryTimeline |
| Context一覧 | 理論文脈の一覧と階層表示 | ContextTree, ClaimCount |
| グラフビュー | Claim/Conceptの関係をインタラクティブグラフで表示 | ForceGraph (D3.js / Cytoscape.js) |
| レビューキュー | Pending Proposalの一覧とレビューUI | ProposalCard, ApproveRejectButtons, CommentBox |
| AI候補一覧 | AIが生成した接続候補一覧 | SuggestionCard, ConfidenceBar, AcceptRejectButtons |
| Evidence詳細 | Evidence情報と関連Claim | EvidenceDetail, LinkedClaims |
| 検索 | 全エンティティ横断検索 | SearchBar, FilteredResults |

### 8.2 主要UIフロー

#### Claim閲覧 → AI候補確認 → レビュー

```
Claim一覧 ──(Claim選択)──▶ Claim詳細
    │                          │
    │                     [AI接続候補] セクション
    │                          │
    │                     候補カード（接続先Claim、理由、確信度）
    │                          │
    │                     [承認] / [却下] ボタン
    │                          │
    │                     ──▶ レビューダイアログ（コメント入力）
    │                          │
    └──────────────────────── ◀─┘
```

#### Evidence カード表示

```
┌─────────────────────────────────────────────┐
│ 📄 Evidence: Second Law of Thermodynamics   │
│                                             │
│ Type: textbook                              │
│ Source: Callen, H.B. "Thermodynamics..."    │
│ Reliability: ●●●○ high                     │
│                                             │
│ "The entropy of an isolated system never    │
│  decreases..."                              │
│                                             │
│ Supports:                                   │
│  • [Claim] 孤立系のエントロピー非減少       │
│  • [Claim] 第二法則のKelvin表現             │
└─────────────────────────────────────────────┘
```

---

## 9. デモデータセット設計（エントロピー概念）

### 9.1 Context（3つ以上）

| Context | Field | 説明 |
|---------|-------|------|
| Classical Thermodynamics | 熱力学 | マクロ的熱・仕事の理論 |
| Statistical Mechanics | 統計力学 | 微視的状態からのマクロ量導出 |
| Shannon Information Theory | 情報理論 | 通信における不確実性の定量化 |
| Quantum Information Theory | 量子情報 | 量子系の情報エントロピー |
| Algorithmic Information Theory | 計算理論 | Kolmogorov複雑性と記述長 |

### 9.2 Term / Concept マッピング例

| Term | Concept | Context |
|------|---------|---------|
| entropy | Thermodynamic Entropy (S) | Classical Thermodynamics |
| entropy | Boltzmann Entropy (S = k ln W) | Statistical Mechanics |
| entropy | Shannon Entropy (H = -Σ p log p) | Shannon Information Theory |
| entropy | Von Neumann Entropy (S = -Tr(ρ ln ρ)) | Quantum Information Theory |
| エントロピー | (上記各Conceptの日本語Term) | (各Context) |

### 9.3 Claim例（抜粋）

| # | Claim | Context | Type | Trust |
|---|-------|---------|------|-------|
| 1 | 孤立系のエントロピーは減少しない（第二法則） | Classical Thermodynamics | theorem | established |
| 2 | S = k_B ln W（Boltzmannの関係式） | Statistical Mechanics | definition | established |
| 3 | マクロ的エントロピーは微視的状態数の対数に比例する | Statistical Mechanics | theorem | established |
| 4 | H(X) = -Σ p(x) log p(x)（Shannon entropy） | Shannon Information Theory | definition | established |
| 5 | エントロピーは情報の欠如の尺度である | Shannon Information Theory | meta | tentative |
| 6 | Boltzmannエントロピーの極限でShannonエントロピーと対応する | Cross-field | conjecture | ai_suggested |
| 7 | Jaynesの最大エントロピー原理は統計力学と情報理論を統一する | Cross-field | claim | tentative |
| 8 | Von Neumannエントロピーは量子系におけるShannonエントロピーの一般化 | Quantum Information Theory | theorem | established |

### 9.4 Evidence例（抜粋）

| Evidence | Type | Supports |
|----------|------|----------|
| Callen "Thermodynamics and an Introduction to Thermostatistics" | textbook | Claim 1, 3 |
| Boltzmann 1877年論文 | paper | Claim 2 |
| Shannon "A Mathematical Theory of Communication" (1948) | paper | Claim 4, 5 |
| Jaynes "Information Theory and Statistical Mechanics" (1957) | paper | Claim 7 |
| Nielsen & Chuang "Quantum Computation and Quantum Information" | textbook | Claim 8 |

---

## 10. データベーススキーマ（PostgreSQL）

```sql
-- Actor（行為者）
CREATE TABLE actors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    actor_type VARCHAR(20) NOT NULL CHECK (actor_type IN ('human', 'ai_agent')),
    name VARCHAR(255) NOT NULL,
    trust_level VARCHAR(20) NOT NULL DEFAULT 'contributor',
    agent_model VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Event Store（append-only）
CREATE TABLE events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sequence_number BIGSERIAL UNIQUE,
    event_type VARCHAR(100) NOT NULL,
    aggregate_type VARCHAR(50) NOT NULL,
    aggregate_id UUID NOT NULL,
    payload JSONB NOT NULL,
    actor_id UUID REFERENCES actors(id),
    proposal_id UUID,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_events_aggregate ON events(aggregate_type, aggregate_id);
CREATE INDEX idx_events_sequence ON events(sequence_number);

-- Term
CREATE TABLE terms (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    surface_form VARCHAR(500) NOT NULL,
    language VARCHAR(10) DEFAULT 'en',
    field_hint VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES actors(id)
);

-- Concept
CREATE TABLE concepts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    label VARCHAR(500) NOT NULL,
    description TEXT,
    field VARCHAR(100),
    referent_id UUID,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES actors(id)
);

-- Term ↔ Concept (N:M)
CREATE TABLE term_concepts (
    term_id UUID REFERENCES terms(id),
    concept_id UUID REFERENCES concepts(id),
    PRIMARY KEY (term_id, concept_id)
);

-- Context
CREATE TABLE contexts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    field VARCHAR(100),
    assumptions JSONB DEFAULT '[]',
    parent_context_id UUID REFERENCES contexts(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES actors(id)
);

-- Claim
CREATE TABLE claims (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    statement TEXT NOT NULL,
    claim_type VARCHAR(20) NOT NULL CHECK (claim_type IN ('definition', 'theorem', 'empirical', 'conjecture', 'meta')),
    trust_status VARCHAR(20) NOT NULL DEFAULT 'tentative' CHECK (trust_status IN ('established', 'tentative', 'disputed', 'ai_suggested')),
    version INTEGER DEFAULT 1,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES actors(id)
);

-- Claim ↔ Context (N:M)
CREATE TABLE claim_contexts (
    claim_id UUID REFERENCES claims(id),
    context_id UUID REFERENCES contexts(id),
    PRIMARY KEY (claim_id, context_id)
);

-- Claim ↔ Concept (N:M)
CREATE TABLE claim_concepts (
    claim_id UUID REFERENCES claims(id),
    concept_id UUID REFERENCES concepts(id),
    role VARCHAR(50) DEFAULT 'related',
    PRIMARY KEY (claim_id, concept_id)
);

-- Evidence
CREATE TABLE evidence (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    evidence_type VARCHAR(20) NOT NULL CHECK (evidence_type IN ('textbook', 'paper', 'experiment', 'proof', 'expert_opinion')),
    title VARCHAR(500) NOT NULL,
    source TEXT,
    excerpt TEXT,
    reliability VARCHAR(20) DEFAULT 'unverified',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES actors(id)
);

-- Claim ↔ Evidence (N:M)
CREATE TABLE claim_evidence (
    claim_id UUID REFERENCES claims(id),
    evidence_id UUID REFERENCES evidence(id),
    relationship VARCHAR(20) DEFAULT 'supports' CHECK (relationship IN ('supports', 'contradicts', 'partially_supports')),
    PRIMARY KEY (claim_id, evidence_id)
);

-- CIR (Controlled Intermediate Representation)
CREATE TABLE cir (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    claim_id UUID REFERENCES claims(id) UNIQUE,
    context_ref VARCHAR(255),
    subject VARCHAR(500),
    relation VARCHAR(255),
    object VARCHAR(500),
    conditions JSONB DEFAULT '[]',
    units VARCHAR(100),
    definition_refs JSONB DEFAULT '[]',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Proposal
CREATE TABLE proposals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    proposal_type VARCHAR(30) NOT NULL,
    proposed_by UUID REFERENCES actors(id),
    target_entity_type VARCHAR(50),
    target_entity_id UUID,
    payload JSONB NOT NULL,
    rationale TEXT,
    status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'in_review', 'approved', 'rejected', 'withdrawn')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    reviewed_at TIMESTAMPTZ,
    reviewed_by UUID REFERENCES actors(id)
);

-- Review
CREATE TABLE reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    proposal_id UUID REFERENCES proposals(id),
    reviewer_id UUID REFERENCES actors(id),
    decision VARCHAR(20) NOT NULL CHECK (decision IN ('approve', 'reject', 'request_changes')),
    comment TEXT,
    confidence FLOAT CHECK (confidence >= 0 AND confidence <= 1),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Cross-field Connections（分野間接続）
CREATE TABLE cross_field_connections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_claim_id UUID REFERENCES claims(id),
    target_claim_id UUID REFERENCES claims(id),
    connection_type VARCHAR(20) NOT NULL CHECK (connection_type IN ('equivalent', 'analogous', 'generalizes', 'contradicts', 'complements')),
    description TEXT,
    confidence FLOAT,
    proposal_id UUID REFERENCES proposals(id),
    status VARCHAR(20) DEFAULT 'proposed',
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

## 11. ディレクトリ構成

```
collective-science/
├── README.md
├── docker-compose.yml
├── backend/
│   ├── pyproject.toml
│   ├── app/
│   │   ├── main.py                  # FastAPI app entry
│   │   ├── config.py                # 設定管理
│   │   ├── models/                  # SQLAlchemy / Pydantic models
│   │   │   ├── term.py
│   │   │   ├── concept.py
│   │   │   ├── claim.py
│   │   │   ├── context.py
│   │   │   ├── evidence.py
│   │   │   ├── proposal.py
│   │   │   ├── review.py
│   │   │   ├── actor.py
│   │   │   └── cir.py
│   │   ├── events/                  # Event Store (DOKP転用)
│   │   │   ├── store.py
│   │   │   ├── commands.py
│   │   │   └── projections.py
│   │   ├── api/                     # APIルーター
│   │   │   ├── claims.py
│   │   │   ├── concepts.py
│   │   │   ├── contexts.py
│   │   │   ├── evidence.py
│   │   │   ├── proposals.py
│   │   │   └── agent.py
│   │   ├── services/                # ビジネスロジック
│   │   │   ├── claim_service.py
│   │   │   ├── proposal_service.py
│   │   │   └── review_service.py
│   │   ├── agent/                   # AI Linking Agent
│   │   │   ├── linking_agent.py
│   │   │   ├── candidate_generator.py
│   │   │   └── prompts.py
│   │   └── seeds/                   # デモデータ
│   │       └── entropy_dataset.py
│   ├── tests/
│   └── alembic/                     # DBマイグレーション
├── frontend/
│   ├── package.json
│   ├── src/
│   │   ├── app/                     # Next.js App Router
│   │   │   ├── page.tsx             # ダッシュボード
│   │   │   ├── claims/
│   │   │   ├── concepts/
│   │   │   ├── contexts/
│   │   │   ├── graph/
│   │   │   ├── review/
│   │   │   └── search/
│   │   ├── components/
│   │   │   ├── ClaimCard.tsx
│   │   │   ├── EvidenceCard.tsx
│   │   │   ├── ProposalCard.tsx
│   │   │   ├── GraphView.tsx
│   │   │   ├── FilterBar.tsx
│   │   │   └── ReviewDialog.tsx
│   │   └── lib/
│   │       ├── api.ts               # APIクライアント
│   │       └── types.ts             # TypeScript型定義
│   └── public/
├── cli/
│   ├── pyproject.toml
│   └── cs/
│       ├── main.py
│       └── commands/
└── docs/
    ├── architecture.md
    ├── data-model.md
    └── api-reference.md
```

---

## 12. 開発優先順位（MVP Phase 1）

### Week 1-2: 基盤構築

- [ ] プロジェクト初期化（Backend: FastAPI, Frontend: Next.js, DB: PostgreSQL）
- [ ] Docker Compose環境構築
- [ ] データベーススキーマ作成 & マイグレーション
- [ ] Event Store基本実装（DOKP転用）
- [ ] Actor / 認証の最小実装

### Week 3-4: コアCRUD

- [ ] Claim / Concept / Context / Term / Evidence のCRUD API
- [ ] Claim一覧画面（フィルタ: Context, field, trust_status）
- [ ] Claim詳細画面（関連Concept, Evidence表示）
- [ ] Context一覧・詳細画面

### Week 5-6: AI接続候補 & レビュー

- [ ] Linking Agent MVP（LLM接続候補生成）
- [ ] Proposalの作成・一覧API
- [ ] Review（Approve / Reject）ワークフロー実装
- [ ] レビューキューUI

### Week 7-8: デモデータ & 統合

- [ ] エントロピーデモデータセット投入（100+ Claims, 30+ Evidence, 3+ Contexts）
- [ ] グラフビュー（Claim/Concept関係の可視化）
- [ ] Evidence カード表示改善
- [ ] 検索機能（全エンティティ横断）
- [ ] E2Eテスト・デモ準備

---

## 13. 非機能要件（MVP）

| 項目 | 要件 |
|------|------|
| パフォーマンス | Claim一覧ロード < 2秒、検索応答 < 3秒 |
| データ整合性 | Event Storeのappend-only保証、Projection再構築可能 |
| 可用性 | ローカル開発優先、シンプルなDocker Compose構成 |
| セキュリティ | API認証（JWT）、入力バリデーション、SQLインジェクション防止 |
| 監査性 | 全変更がEvent Storeに記録、Actor追跡可能 |
| 拡張性 | レビュアー抽象化により将来のAIレビュアー追加が容易 |

---

## 14. DOKP転用マッピング

| DOKP要素 | CollectiveScience対応 | 転用方針 |
|----------|----------------------|---------|
| Append-only Event Store | Events テーブル | そのまま転用 |
| Command Algebra (CreateFact / CorrectFact / RetractFact) | ClaimCreated / ClaimUpdated / ClaimRetracted etc. | 修正して転用（ドメインスキーマに合わせ拡張） |
| Proposal → Review → Approve/Reject | Proposals + Reviews テーブル | そのまま転用 |
| Projection パイプライン | Read Models (Materialized Views) | そのまま転用 |
| PolicyEngine | ActorRef.trust_level による権限制御 | 修正して転用（レビュアー抽象化を追加） |
| Authority Model | Actor + trust_level + actor_type | 修正して転用（AI/Human の区別を追加） |
| 監査ログ | Event Storeが監査ログを兼ねる | そのまま転用 |
