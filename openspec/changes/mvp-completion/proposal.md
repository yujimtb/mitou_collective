## Why

CollectiveScienceプロトタイプは全レイヤーの土台が実装済みだが、MVPとしてデモ可能な状態にするには2つの重要なギャップがある。

1. **AI Linking Agentが実LLMに未接続** — `CandidateGenerator`はcallable `llm_client`を受け取る設計だが、OpenAI/Claude等の実APIクライアント実装が存在せず、設計書の「AIで接続候補提案」を動作させられない。
2. **Web UIにエンティティ作成フォームがない** — Claim、Concept、Context、Evidenceの閲覧・レビューは機能するが、作成フォームやProposal手動送信UIがなく、デモ時にUIだけで操作が完結しない。

未踏プロジェクトのデモ期限に向け、この2点を並行実装してMVPを完成させる。

## What Changes

### AI Linking Agent — 実LLM接続

- LLMクライアントモジュールを新設し、OpenAI API（GPT-4o）およびClaude API（claude-sonnet）に対応するアダプターを実装
- 環境変数ベースのAPIキー設定と、モデル選択・パラメータ設定のconfigを追加
- 既存のJSON propmtをLLM APIのsystem/user message構造にラップするプロンプトアダプターを実装
- FastAPIアプリ起動時にLLMクライアントを初期化し、`LinkingAgent`にDI（依存注入）する
- 既存のリトライ・エラーハンドリングと統合

### Web UI — 操作完結性

- Claim作成フォーム（statement、claim_type、Context選択、Concept選択）を実装
- Concept作成フォーム（label、description、field、Term選択）を実装
- Context作成フォーム（name、description、field、assumptions）を実装
- Evidence作成フォーム（title、source、excerpt、evidence_type、reliability、Claim紐付け）を実装
- AI接続候補の手動トリガーボタン（Claim詳細画面から「AI候補を生成」）を実装
- Approve/Rejectフロー後のUI反映（楽観的更新、成功/エラーフィードバック）の磨き込み

## Capabilities

### New Capabilities

- `llm-client`: LLMプロバイダー（OpenAI、Anthropic）へのHTTPクライアント実装とモデル設定管理

### Modified Capabilities

- `linking-agent`: LLMクライアントDIの統合、プロンプトのmessage構造化、アプリ初期化フローの追加
- `web-ui`: エンティティ作成フォーム群、AI候補手動トリガーUI、レビューフロー後のUI更新の追加
- `rest-api`: フロントエンドから利用するCRUDエンドポイントのレスポンス整備（既存APIは実装済みだが、フロントエンド連携の観点で追加のシナリオが必要）

## Impact

- **Backend**: `backend/app/agent/`に`llm_client.py`を新設。`config.py`にLLM設定を追加。`main.py`の起動処理変更
- **Frontend**: `frontend/src/components/`にフォーム系コンポーネント4種を追加。既存ページに作成ボタン・トリガーボタンを配置
- **環境変数**: `OPENAI_API_KEY`、`ANTHROPIC_API_KEY`、`LLM_PROVIDER`、`LLM_MODEL`の追加
- **依存パッケージ**: `openai`、`anthropic` Pythonパッケージの追加
- **テスト**: LLMクライアントのモック統合テスト、フォームコンポーネントの動作テスト
