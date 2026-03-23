# CLI Specification

## Purpose

TsumuGraphのREST APIをコマンドラインから操作するためのCLIツール（`cs`コマンド）を定義する。研究者やエンジニアがスクリプトやシェルからClaim操作、レビュー、AI接続候補生成を効率的に実行できるようにする。

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

#### Scenario: Concept作成

- **WHEN** `cs concept create --label "..." --field "..." --description "..."` が実行される
- **THEN** 指定された内容でConceptが作成され、作成されたConceptのIDが標準出力に表示される
- **THEN** オプション `--term <id>` で関連Termを指定できる（複数回指定可）
- **THEN** オプション `--referent <id>` でReferentを指定できる

### Requirement: Context CLIコマンド

CLIはContextに対する操作コマンドを提供しなければならない（SHALL）。

#### Scenario: Context一覧表示

- **WHEN** `cs context list` が実行される
- **THEN** Context一覧がテーブル形式で標準出力に表示される（ID、name、field、Claim数）
- **THEN** オプション `--field <name>` によるフィルタリングが可能
- **THEN** オプション `--json` を指定するとJSON形式で出力される

#### Scenario: Context詳細表示

- **WHEN** `cs context get <id>` が実行される
- **THEN** Contextの全詳細（name、description、field、assumptions一覧、子Context一覧、属するClaim数）が整形されて標準出力に表示される

#### Scenario: Context作成

- **WHEN** `cs context create --name "..." --field "..." --description "..."` が実行される
- **THEN** 指定された内容でContextが作成され、作成されたContextのIDが標準出力に表示される
- **THEN** オプション `--assumptions "A1,A2,A3"` でカンマ区切りの前提条件を指定できる
- **THEN** オプション `--parent <id>` で親Contextを指定できる

### Requirement: Term CLIコマンド

CLIはTermに対する操作コマンドを提供しなければならない（SHALL）。

#### Scenario: Term一覧表示

- **WHEN** `cs term list` が実行される
- **THEN** Term一覧がテーブル形式で標準出力に表示される（ID、surface_form、language、field_hint、関連Concept数）
- **THEN** オプション `--language <code>` によるフィルタリングが可能
- **THEN** オプション `--search <query>` による表層形検索が可能
- **THEN** オプション `--json` を指定するとJSON形式で出力される

#### Scenario: Term詳細表示

- **WHEN** `cs term get <id>` が実行される
- **THEN** Termの全詳細（surface_form、language、field_hint、関連Concept一覧）が整形されて標準出力に表示される

#### Scenario: Term作成

- **WHEN** `cs term create --surface-form "..." --language "en"` が実行される
- **THEN** 指定された内容でTermが作成され、作成されたTermのIDが標準出力に表示される
- **THEN** オプション `--field-hint <name>` で分野ヒントを指定できる
- **THEN** オプション `--concept <id>` で関連Conceptを指定できる（複数回指定可）

### Requirement: Evidence CLIコマンド

CLIはEvidenceに対する操作コマンドを提供しなければならない（SHALL）。

#### Scenario: Evidence一覧表示

- **WHEN** `cs evidence list` が実行される
- **THEN** Evidence一覧がテーブル形式で標準出力に表示される（ID、title、evidence_type、reliability、関連Claim数）
- **THEN** オプション `--type <evidence_type>` によるフィルタリングが可能
- **THEN** オプション `--json` を指定するとJSON形式で出力される

#### Scenario: Evidence詳細表示

- **WHEN** `cs evidence get <id>` が実行される
- **THEN** Evidenceの全詳細（title、evidence_type、source、excerpt、reliability、関連Claim一覧）が整形されて標準出力に表示される

#### Scenario: Evidence作成

- **WHEN** `cs evidence create --title "..." --type paper --source "..."` が実行される
- **THEN** 指定された内容でEvidenceが作成され、作成されたEvidenceのIDが標準出力に表示される
- **THEN** オプション `--excerpt "..."` で引用箇所を指定できる
- **THEN** オプション `--reliability <level>` で信頼度を指定できる（デフォルト: unverified）
- **THEN** オプション `--claim <id>` で関連Claimを指定できる（複数回指定可）

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
