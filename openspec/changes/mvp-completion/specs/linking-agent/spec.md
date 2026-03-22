## MODIFIED Requirements

### Requirement: LLM接続候補生成

Linking AgentはLLM（大規模言語モデル）を活用して、候補Claim間の接続関係を分析・生成しなければならない（SHALL）。

#### Scenario: LLMへの入力構成

- **WHEN** LLMに接続候補の分析を依頼する
- **THEN** 以下の情報をsystem/userメッセージ構造のプロンプトとして構成する: 対象Claimとその文脈情報（statement、Context、Concept、Evidence）、候補となる他分野のClaim群（各Claimのstatement、Context、Concept）

#### Scenario: LLMからの出力形式

- **WHEN** LLMが接続候補を返す
- **THEN** 各候補について以下の構造化データを出力する: 接続先claim_id、connection_type（equivalent / analogous / generalizes / contradicts / complements）、接続理由（自然言語、2〜3文）、確信度スコア（0.0〜1.0）、注意点（前提条件の差異等）

#### Scenario: 確信度閾値

- **WHEN** LLMが確信度スコアを出力する
- **THEN** 設定された閾値（デフォルト: 0.3）以上の候補のみがProposalとして作成される

#### Scenario: LLMエラーハンドリング

- **WHEN** LLM APIの呼び出しが失敗する（タイムアウト、レート制限、APIエラー等）
- **THEN** システムはリトライ（指数バックオフ、最大3回）を行い、すべてのリトライが失敗した場合はジョブをfailedとしてログに記録する

## ADDED Requirements

### Requirement: LLMクライアント依存注入

システムはLinking Agentに対してLLMクライアントを依存注入により提供しなければならない（SHALL）。

#### Scenario: アプリケーション起動時のLLMクライアント初期化

- **WHEN** FastAPIアプリケーションが起動する
- **THEN** 環境変数に基づいてLLMクライアントが初期化され、`app.state`に格納される

#### Scenario: Linking AgentへのLLMクライアント注入

- **WHEN** Linking Agentが接続候補生成を実行する
- **THEN** `app.state`から取得したLLMクライアントの`generate`メソッドが`CandidateGenerator`のllm_clientとして渡される

#### Scenario: LLMクライアント未設定時の動作

- **WHEN** LLMクライアントが初期化されていない状態（APIキー未設定等）でAgent APIが呼び出される
- **THEN** 503 Service Unavailable（`{"error": {"code": "llm_unavailable", "message": "LLM service is not configured"}}`）が返される
