# Linking Agent Specification

## Purpose

AIエージェント（Linking Agent）が知識グラフ内のClaim/Conceptを分析し、異分野間の接続候補を自律的に提案する機能を定義する。生成された候補はProposalとしてレビューキューに投入され、人間（または信頼されたAIレビュアー）による採否判断を経て知識グラフに反映される。

## Requirements

### Requirement: 接続候補生成トリガー

Linking Agentは定義されたトリガー条件に基づいて接続候補の生成を開始しなければならない（SHALL）。

#### Scenario: 新規Claim作成トリガー

- **WHEN** 新しいClaimが知識グラフに登録される
- **THEN** Linking Agentは当該Claimに関連する他分野のClaimとの接続候補を自動的に探索するジョブをキューに追加する

#### Scenario: 新規Concept追加トリガー

- **WHEN** 新しいConceptが登録される
- **THEN** Linking Agentは当該Conceptと類似または関連する他分野のConceptとの対応候補を探索するジョブをキューに追加する

#### Scenario: 手動リクエストトリガー

- **WHEN** ユーザーが特定のClaim IDまたはConcept IDを指定して接続候補の生成をAPIまたはCLI経由でリクエストする
- **THEN** Linking Agentは指定されたエンティティを起点として接続候補生成を実行する

#### Scenario: オプションの対象分野指定

- **WHEN** 手動リクエストにtarget_field（対象分野）が指定される
- **THEN** Linking Agentは指定された分野のClaim/Conceptのみを候補対象として探索する

### Requirement: コンテキスト収集

Linking Agentは接続候補生成の前に、対象エンティティの関連情報を収集しなければならない（SHALL）。

#### Scenario: Claim起点のコンテキスト収集

- **WHEN** Claimを起点として接続候補を生成する
- **THEN** 以下の情報を収集する: 当該Claimのstatement・claim_type・trust_status、関連するConcept一覧（label、field）、属するContext一覧（name、field、assumptions）、紐づくEvidence一覧（title、excerpt）、隣接するClaim（同一Contextまたは同一Conceptを共有するClaim）

#### Scenario: Concept起点のコンテキスト収集

- **WHEN** Conceptを起点として接続候補を生成する
- **THEN** 以下の情報を収集する: 当該Conceptのlabel・description・field、関連するTerm一覧、紐づくClaim一覧、他分野で類似labelまたは類似descriptionを持つConcept一覧

### Requirement: 候補Claim検索

Linking Agentは接続候補となる他分野のClaimを効率的に検索しなければならない（SHALL）。

#### Scenario: 分野横断検索

- **WHEN** 対象Claimの属する分野と異なる分野のClaimが検索される
- **THEN** 以下の条件を組み合わせて候補を絞り込む: Conceptのlabelまたはdescriptionの意味的類似性、Termのsurface_formの一致または類似、Claimのstatementの意味的類似性（埋め込みベクトルによる近傍検索）

#### Scenario: 候補数の制限

- **WHEN** 候補Claim検索が実行される
- **THEN** 上位N件（設定可能、デフォルト: 20件）の候補Claimが返される

### Requirement: LLM接続候補生成

Linking AgentはLLM（大規模言語モデル）を活用して、候補Claim間の接続関係を分析・生成しなければならない（SHALL）。

#### Scenario: LLMへの入力構成

- **WHEN** LLMに接続候補の分析を依頼する
- **THEN** 以下の情報をプロンプトとして構成する: 対象Claimとその文脈情報（statement、Context、Concept、Evidence）、候補となる他分野のClaim群（各Claimのstatement、Context、Concept）

#### Scenario: LLMからの出力形式

- **WHEN** LLMが接続候補を返す
- **THEN** 各候補について以下の構造化データを出力する: 接続先claim_id、connection_type（equivalent / analogous / generalizes / contradicts / complements）、接続理由（自然言語、2〜3文）、確信度スコア（0.0〜1.0）、注意点（前提条件の差異等）

#### Scenario: 確信度閾値

- **WHEN** LLMが確信度スコアを出力する
- **THEN** 設定された閾値（デフォルト: 0.3）以上の候補のみがProposalとして作成される

#### Scenario: LLMエラーハンドリング

- **WHEN** LLM APIの呼び出しが失敗する（タイムアウト、レート制限、APIエラー等）
- **THEN** システムはリトライ（指数バックオフ、最大3回）を行い、すべてのリトライが失敗した場合はジョブをfailedとしてログに記録する

### Requirement: Proposal自動生成

Linking Agentは生成した接続候補をProposalとして自動的にキューに投入しなければならない（SHALL）。

#### Scenario: 接続候補からProposal生成

- **WHEN** LLMが接続候補を出力し、確信度閾値を超えている
- **THEN** proposal_type="connect_concepts"、proposed_by=AIエージェントのActorRef、payload={source_claim_id, target_claim_id, connection_type, confidence, rationale, caveats}、rationale=LLMが生成した接続理由 のProposalが作成される

#### Scenario: 重複チェック

- **WHEN** 新しいProposalが生成される
- **THEN** 同じsource_claim_idとtarget_claim_idの組み合わせでpendingまたはin_review状態のProposalが既に存在する場合、新しいProposalは作成されない

#### Scenario: バッチ生成

- **WHEN** 1回の接続候補生成で複数の候補が見つかる
- **THEN** 各候補に対して個別のProposalが作成される

### Requirement: 接続候補の一覧・管理

システムは生成された接続候補を一覧・管理する機能を提供しなければならない（SHALL）。

#### Scenario: 候補一覧取得

- **WHEN** ユーザーが接続候補一覧をリクエストする
- **THEN** status（pending / approved / rejected）、確信度、提案日時でフィルタリング可能な候補一覧が返される

#### Scenario: 候補の詳細表示

- **WHEN** ユーザーが特定の接続候補の詳細をリクエストする
- **THEN** 接続元Claim（statement、Context、Concept）、接続先Claim（同）、connection_type、確信度、接続理由、注意点が表示される
