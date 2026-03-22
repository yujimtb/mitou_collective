## MODIFIED Requirements

### Requirement: Claim詳細画面

システムはClaimの全情報を閲覧できる詳細画面を提供しなければならない（SHALL）。取得失敗時はHTTPステータスコードに応じた適切なエラー状態を表示しなければならない（SHALL）。

#### Scenario: Claim基本情報表示

- **WHEN** ユーザーがClaim詳細画面にアクセスする
- **THEN** statement全文、claim_type（バッジ表示）、trust_status（色分けバッジ）、versionが表示される

#### Scenario: 関連Concept表示

- **WHEN** Claim詳細画面が表示される
- **THEN** 関連するConceptがタグ形式で表示される（label、field情報付き）
- **THEN** Conceptタグをクリックすると当該Conceptの詳細に遷移できる

#### Scenario: 属するContext表示

- **WHEN** Claim詳細画面が表示される
- **THEN** 当該Claimが属するContext一覧がバッジ形式で表示される
- **THEN** Contextバッジをクリックすると当該Contextの詳細に遷移できる

#### Scenario: Evidenceカード表示

- **WHEN** Claim詳細画面が表示される
- **THEN** 紐づくEvidence一覧がカード形式で表示される
- **THEN** 各EvidenceカードにはTitle、evidence_type（アイコン）、source、excerpt（あれば）、reliability（インジケーター）、relationship（supports / contradicts / partially_supports）が表示される

#### Scenario: CIR表示

- **WHEN** ClaimにCIRが設定されている場合
- **THEN** CIRの構造化表現（context_ref、subject、relation、conditions等）が整形されて表示される

#### Scenario: 存在しないClaimへのアクセス

- **WHEN** 存在しないClaim IDで詳細画面にアクセスする
- **THEN** APIが404を返した場合のみ `notFound()` が呼び出され、Next.jsの404ページが表示される

#### Scenario: 認証エラー時のエラー表示

- **WHEN** Claim詳細の取得で401または403が返される
- **THEN** システムは認証エラー専用のエラー状態を表示する（404ページではない）

#### Scenario: サーバーエラー時のエラー表示

- **WHEN** Claim詳細の取得で500または503が返される
- **THEN** システムはサーバーエラー専用のエラー状態を表示する（404ページではない）

## ADDED Requirements

### Requirement: サーバーサイド認証境界

システムはブラウザから実行される認証付きミューテーション（作成・レビュー・AI提案）をNext.jsサーバーサイド境界（Server ActionsまたはRoute Handlers）経由で実行しなければならない（SHALL）。`CS_API_TOKEN`はサーバーサイドのみで使用する。

#### Scenario: Claim作成のサーバーサイド実行

- **WHEN** ユーザーがCreateClaimDialogからClaimを作成する
- **THEN** リクエストはNext.js Server Action経由でバックエンドAPIに送信される
- **THEN** `CS_API_TOKEN`はサーバーサイドプロセス内でのみ使用され、ブラウザには露出しない

#### Scenario: Review送信のサーバーサイド実行

- **WHEN** ユーザーがReviewDialogからレビューを送信する
- **THEN** リクエストはNext.js Server Action経由でバックエンドAPIに送信される
- **THEN** `CS_API_TOKEN`はサーバーサイドプロセス内でのみ使用され、ブラウザには露出しない

#### Scenario: AI提案リクエストのサーバーサイド実行

- **WHEN** ユーザーがClaim詳細画面からAI接続候補を要求する
- **THEN** リクエストはNext.js Server Action経由でバックエンドAPIに送信される
- **THEN** `CS_API_TOKEN`はサーバーサイドプロセス内でのみ使用され、ブラウザには露出しない

### Requirement: APIエラー型の伝播

システムはAPIレスポンスのHTTPステータスコードを保持するエラー型を提供し、下流のコンポーネントがステータスに基づいて適切なエラーハンドリングを行えるようにしなければならない（SHALL）。

#### Scenario: 404レスポンスのエラー伝播

- **WHEN** APIリクエストが404レスポンスを返す
- **THEN** エラーオブジェクトにステータスコード404が含まれ、呼び出し元で `notFound()` と判別可能

#### Scenario: 非404エラーレスポンスの伝播

- **WHEN** APIリクエストが401、403、500、503などの非404エラーを返す
- **THEN** エラーオブジェクトにステータスコードが含まれ、呼び出し元で適切なエラーUI表示に利用可能

#### Scenario: 全詳細ページでのエラーハンドリング統一

- **WHEN** Claim、Concept、Context、Evidence、Term の各詳細ページでフェッチエラーが発生する
- **THEN** 全ページで同一のエラーハンドリングロジックが適用され、404のみ `notFound()` に変換し、それ以外はエラー状態として表示する
