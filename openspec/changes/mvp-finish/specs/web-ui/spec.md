# Web UI Specification — Delta

## ADDED Requirements

### Requirement: Term一覧・詳細画面

システムはTerm（語）の一覧・詳細表示画面を提供しなければならない（SHALL）。

#### Scenario: Term一覧表示

- **WHEN** ユーザーがTerm一覧画面（`/terms`）にアクセスする
- **THEN** Term一覧がテーブルまたはカード形式で表示される（surface_form、language、field_hint、関連Concept数）
- **THEN** 検索ボックスによるsurface_form検索、言語フィルターが提供される

#### Scenario: Term詳細表示

- **WHEN** ユーザーがTerm一覧から項目を選択し、Term詳細画面（`/terms/[id]`）にアクセスする
- **THEN** surface_form、language、field_hintが表示される
- **THEN** 関連するConcept一覧がタグ形式で表示され、各Conceptをクリックすると`/concepts/[id]`に遷移できる

#### Scenario: Term作成

- **WHEN** ユーザーがTerm一覧画面の「新規Term作成」ボタンをクリックする
- **THEN** モーダルダイアログが表示され、surface_form（必須）、language（セレクト）、field_hint、関連Concept（マルチセレクト）を入力できる
- **THEN** 送信成功後にTerm一覧が更新される

### Requirement: Evidence一覧・詳細画面

システムはEvidence（根拠）の一覧・詳細表示画面を提供しなければならない（SHALL）。

#### Scenario: Evidence一覧表示

- **WHEN** ユーザーがEvidence一覧画面（`/evidence`）にアクセスする
- **THEN** Evidence一覧がカード形式で表示される（title、evidence_type、source概要、reliability、関連Claim数）
- **THEN** evidence_type、reliability によるフィルタリングが提供される

#### Scenario: Evidence詳細表示

- **WHEN** ユーザーがEvidence一覧から項目を選択し、Evidence詳細画面（`/evidence/[id]`）にアクセスする
- **THEN** title、evidence_type（バッジ）、source（リンク付き）、excerpt（引用ブロック）、reliability（インジケーター）が表示される
- **THEN** 関連するClaim一覧がカード形式で表示され、各ClaimをクリックするとClaim詳細に遷移できる
- **THEN** 各Claimとの関係（supports / contradicts / partially_supports）がバッジで表示される

### Requirement: AI候補一覧画面

システムはAI Linking Agentが生成した接続候補の専用一覧画面を提供しなければならない（SHALL）。

#### Scenario: AI候補一覧表示

- **WHEN** ユーザーがAI候補一覧画面（`/suggestions`）にアクセスする
- **THEN** `GET /api/v1/agent/suggestions` から取得した候補一覧がカード形式で表示される
- **THEN** 各カードにはproposal_type、接続元Claim（statement先頭部分）、接続先Claim（statement先頭部分）、connection_type、確信度（バー表示）、rationale概要が表示される

#### Scenario: AI候補のフィルタリング

- **WHEN** ユーザーがstatus（pending / approved / rejected）または最低確信度スライダーでフィルタリングする
- **THEN** 選択条件に合致する候補のみが表示される

#### Scenario: AI候補のインラインレビュー

- **WHEN** ユーザーが候補カードの「承認」または「却下」ボタンをクリックする
- **THEN** ReviewDialogが表示され、コメント入力後にレビューが送信される
- **THEN** 成功時にToast通知が表示され、カードのステータスが更新される

## MODIFIED Requirements

### Requirement: グラフビュー画面

システムはClaim/Conceptの関係をインタラクティブなグラフとして可視化する画面を提供しなければならない（SHALL）。

#### Scenario: ノードとエッジの表示

- **WHEN** ユーザーがグラフビュー画面にアクセスする
- **THEN** Claim/Conceptがノードとして、それらの関連・接続がエッジとしてD3.jsまたはCytoscape.jsによる力指向グラフ（force-directed graph）で`<svg>`または`<canvas>`要素内に描画される
- **THEN** ノードの種類（Claim / Concept）が色またはアイコンで区別される
- **THEN** グラフはマウスホイールによるズーム、ドラッグによるパン操作をサポートする

#### Scenario: ノードの操作

- **WHEN** ユーザーがグラフ上のノードをクリックする
- **THEN** ノードの概要情報（Claimのstatement先頭部分、またはConceptのlabel）がツールチップまたはパネルで表示される
- **THEN** 概要情報内から詳細画面へのリンクが提供される

#### Scenario: ノードのドラッグ

- **WHEN** ユーザーがノードをドラッグする
- **THEN** ノードが追従し、力指向レイアウトがリアルタイムに再計算される

### Requirement: ダッシュボード画面

システムはプラットフォーム全体の概要を表示するダッシュボード画面を提供しなければならない（SHALL）。

#### Scenario: 最新アクティビティ表示

- **WHEN** ダッシュボード画面が表示される
- **THEN** `GET /api/v1/events/recent` から取得した直近のイベントが時系列順で最大10件表示される
- **THEN** 各アクティビティにはタイトル、概要、実行者名、タイムスタンプ、該当エンティティへのリンクが含まれる

### Requirement: Claim詳細画面

システムはClaimの全情報を閲覧できる詳細画面を提供しなければならない（SHALL）。

#### Scenario: 変更履歴タイムライン

- **WHEN** ユーザーがClaim詳細画面の「履歴」セクションを閲覧する
- **THEN** `GET /api/v1/claims/{id}/history` から取得した整形済みイベントがタイムライン形式で表示される（タイトル、概要、実行者名、タイムスタンプ）
- **THEN** 各イベントのタイトルはイベント種別に対応する人間可読テキスト（例: "Claim作成"、"信頼状態変更"）で表示される
