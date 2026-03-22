# CLI Specification

## Purpose

CollectiveScienceのREST APIをコマンドラインから操作するためのCLIツール（`cs`コマンド）を定義する。研究者やエンジニアがスクリプトやシェルからClaim操作、レビュー、AI接続候補生成を効率的に実行できるようにする。

## Requirements

### Requirement: Claim CLIコマンド

CLIはClaimに対する操作コマンドを提供しなければならない（SHALL）。

#### Scenario: Claim一覧表示

- **WHEN** `cs claim list` が実行される
- **THEN** Claim一覧がテーブル形式で標準出力に表示される（ID、statement先頭50文字、claim_type、trust_status、Context名）
- **THEN** オプション `--context <name>`、`--field <name>`、`--trust <status>`、`--type <claim_type>` によるフィルタリングが可能
- **THEN** オプション `--json` を指定するとJSON形式で出力される

#### Scenario: Claim詳細表示

- **WHEN** `cs claim get <id>` が実行される
- **THEN** Claimの全詳細（statement、claim_type、trust_status、version、関連Concept、Context、Evidence、CIR）が整形されて標準出力に表示される

#### Scenario: Claim作成

- **WHEN** `cs claim create --statement "..." --context <name> --type <claim_type>` が実行される
- **THEN** 指定された内容でClaimが作成され、作成されたClaimのIDが標準出力に表示される
- **THEN** オプション `--concept <id>` で関連Conceptを指定できる（複数回指定可）

#### Scenario: Claim変更履歴表示

- **WHEN** `cs claim history <id>` が実行される
- **THEN** 当該Claimの変更イベント一覧が時系列順で標準出力に表示される（タイムスタンプ、イベント種別、Actor名、変更概要）

### Requirement: Concept CLIコマンド

CLIはConceptに対する操作コマンドを提供しなければならない（SHALL）。

#### Scenario: Concept一覧表示

- **WHEN** `cs concept list` が実行される
- **THEN** Concept一覧がテーブル形式で標準出力に表示される
- **THEN** オプション `--field <name>` によるフィルタリングが可能

#### Scenario: Concept詳細表示

- **WHEN** `cs concept get <id>` が実行される
- **THEN** Conceptの全詳細（label、description、field、関連Term、紐づくClaim）が表示される

#### Scenario: Concept接続一覧表示

- **WHEN** `cs concept connections <id>` が実行される
- **THEN** 当該Conceptに関連する異分野接続一覧が表示される

### Requirement: Proposal CLIコマンド

CLIはProposal/Reviewに対する操作コマンドを提供しなければならない（SHALL）。

#### Scenario: Proposal一覧表示

- **WHEN** `cs proposal list` が実行される
- **THEN** Proposal一覧がテーブル形式で表示される（ID、proposal_type、status、proposed_by、created_at）
- **THEN** オプション `--status <status>` によるフィルタリングが可能

#### Scenario: Proposal承認

- **WHEN** `cs proposal review <id> --approve` が実行される
- **THEN** 指定されたProposalが承認され、結果メッセージが表示される
- **THEN** オプション `--comment "..."` でコメントを追加できる

#### Scenario: Proposal却下

- **WHEN** `cs proposal review <id> --reject --comment "..."` が実行される
- **THEN** 指定されたProposalが却下され、結果メッセージが表示される
- **THEN** `--reject` の場合、`--comment` は必須とする

### Requirement: Agent CLIコマンド

CLIはAI Linking Agentの操作コマンドを提供しなければならない（SHALL）。

#### Scenario: 接続候補生成リクエスト

- **WHEN** `cs agent suggest --concept <id>` が実行される
- **THEN** 指定されたConceptを起点としたAI接続候補生成が開始され、ジョブIDが表示される
- **THEN** オプション `--target-field <name>` で対象分野を限定できる
- **THEN** `--claim <id>` で Claim起点の候補生成も可能

#### Scenario: 生成済み候補一覧表示

- **WHEN** `cs agent suggestions` が実行される
- **THEN** AI Linking Agentが生成した候補一覧がテーブル形式で表示される
- **THEN** オプション `--status <status>` によるフィルタリングが可能

### Requirement: 検索CLIコマンド

CLIは横断検索コマンドを提供しなければならない（SHALL）。

#### Scenario: 横断検索

- **WHEN** `cs search "entropy"` が実行される
- **THEN** Claim、Concept、Term、Context、Evidenceを横断的に検索した結果がテーブル形式で表示される
- **THEN** オプション `--scope <claims|concepts|terms|contexts|evidence>` で検索対象を限定できる

### Requirement: CLI共通仕様

CLIは以下の共通仕様に従わなければならない（SHALL）。

#### Scenario: 認証設定

- **WHEN** CLIが初めて使用される
- **THEN** `cs auth login` コマンドでAPIトークンを設定する
- **THEN** トークンは `~/.cs/config.toml` に安全に保存される

#### Scenario: API接続先設定

- **WHEN** CLIがAPIサーバーに接続する
- **THEN** デフォルトの接続先は `http://localhost:8000` とし、`--api-url` オプションまたは環境変数 `CS_API_URL` で変更可能とする

#### Scenario: エラー表示

- **WHEN** APIエラーが発生する
- **THEN** エラーメッセージが標準エラー出力に表示され、非ゼロの終了コードが返される

#### Scenario: JSON出力モード

- **WHEN** 任意のコマンドに `--json` オプションが付与される
- **THEN** 出力がJSON形式（APIレスポンスと同一構造）で標準出力に出力され、他のツールへのパイプが容易になる
