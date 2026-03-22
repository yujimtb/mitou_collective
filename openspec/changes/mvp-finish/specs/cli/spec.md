# CLI Specification — Delta

## ADDED Requirements

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

### Requirement: Concept作成CLIコマンド

CLIはConceptの作成コマンドを追加で提供しなければならない（SHALL）。

#### Scenario: Concept作成

- **WHEN** `cs concept create --label "..." --field "..." --description "..."` が実行される
- **THEN** 指定された内容でConceptが作成され、作成されたConceptのIDが標準出力に表示される
- **THEN** オプション `--term <id>` で関連Termを指定できる（複数回指定可）
- **THEN** オプション `--referent <id>` でReferentを指定できる
