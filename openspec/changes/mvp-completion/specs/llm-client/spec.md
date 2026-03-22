## ADDED Requirements

### Requirement: LLMプロバイダーアダプター

システムはOpenAI APIおよびAnthropic APIに対してHTTPリクエストを送信し、テキスト生成レスポンスを受信できるLLMクライアントを提供しなければならない（SHALL）。

#### Scenario: OpenAI APIへのリクエスト送信

- **WHEN** LLMクライアントがOpenAIプロバイダーで初期化され、プロンプトが送信される
- **THEN** OpenAI Chat Completions API (`POST https://api.openai.com/v1/chat/completions`) にsystem messageとuser messageを含むリクエストが送信され、レスポンスからassistant messageのcontentが返される

#### Scenario: Anthropic APIへのリクエスト送信

- **WHEN** LLMクライアントがAnthropicプロバイダーで初期化され、プロンプトが送信される
- **THEN** Anthropic Messages API (`POST https://api.anthropic.com/v1/messages`) にsystem promptとuser messageを含むリクエストが送信され、レスポンスからtext contentが返される

#### Scenario: レスポンス形式の統一

- **WHEN** いずれかのプロバイダーからレスポンスが返される
- **THEN** 統一された `LLMResponse(content: str, model: str, usage: TokenUsage)` 形式に変換される

### Requirement: LLM設定管理

システムは環境変数ベースでLLMプロバイダーとモデルの設定を管理しなければならない（SHALL）。

#### Scenario: 環境変数によるプロバイダー選択

- **WHEN** 環境変数 `LLM_PROVIDER` に `openai` または `anthropic` が設定される
- **THEN** 対応するプロバイダーのLLMクライアントが初期化される

#### Scenario: APIキーの設定

- **WHEN** 環境変数 `OPENAI_API_KEY` または `ANTHROPIC_API_KEY` が設定される
- **THEN** 対応するプロバイダーの認証にそのAPIキーが使用される

#### Scenario: APIキー未設定時のエラー

- **WHEN** 選択されたプロバイダーのAPIキーが設定されていない
- **THEN** アプリケーション起動時に明確なエラーメッセージを出力し起動を中断する

#### Scenario: モデルとパラメータの設定

- **WHEN** 環境変数 `LLM_MODEL` が設定される
- **THEN** 指定されたモデルがLLMリクエストに使用される
- **WHEN** `LLM_MODEL` が未設定の場合
- **THEN** プロバイダーごとのデフォルトモデル（OpenAI: `gpt-4o`、Anthropic: `claude-sonnet-4-20250514`）が使用される

### Requirement: プロンプトメッセージ構造化

システムはLLM APIに送信するプロンプトをsystem/userメッセージ構造で構成しなければならない（SHALL）。

#### Scenario: system messageの構成

- **WHEN** 接続候補生成プロンプトが構築される
- **THEN** system messageには「学際的知識の専門家」としてのロール定義、出力形式の指定（JSON）、接続種別の定義（equivalent / analogous / generalizes / contradicts / complements）が含まれる

#### Scenario: user messageの構成

- **WHEN** 接続候補生成プロンプトが構築される
- **THEN** user messageには対象エンティティの文脈情報（statement、Context、Concept、Evidence）と候補Claim群の情報がJSON形式で含まれる

#### Scenario: temperature設定

- **WHEN** LLMリクエストが送信される
- **THEN** temperature=0.3（低ランダム性、一貫性重視）がデフォルトで設定される

### Requirement: LLMエラーハンドリングとリトライ統合

システムはLLM APIの呼び出し失敗時に既存のリトライポリシーと統合してエラー処理を行わなければならない（SHALL）。

#### Scenario: レート制限エラー

- **WHEN** LLM APIが429 Too Many Requestsを返す
- **THEN** `Retry-After`ヘッダーまたは指数バックオフに基づいてリトライが実行される

#### Scenario: タイムアウト

- **WHEN** LLM APIが60秒以内にレスポンスを返さない
- **THEN** リクエストがタイムアウトし、リトライポリシーに従って再試行される

#### Scenario: APIキー無効エラー

- **WHEN** LLM APIが401 Unauthorizedを返す
- **THEN** リトライせずに即座にエラーを返し、ログにAPIキー無効の旨を記録する
