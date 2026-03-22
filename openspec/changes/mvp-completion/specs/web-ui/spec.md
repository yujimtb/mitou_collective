## ADDED Requirements

### Requirement: Claim作成フォーム

システムはWeb UIからClaimを新規作成できるフォームを提供しなければならない（SHALL）。

#### Scenario: Claim作成フォーム表示

- **WHEN** ユーザーがClaim一覧画面の「新規作成」ボタンをクリックする
- **THEN** Claim作成フォームがモーダルまたは専用画面として表示される
- **THEN** フォームにはstatement（テキストエリア）、claim_type（セレクト：definition / theorem / empirical / conjecture / meta）、Context選択（マルチセレクト、既存Context一覧から選択）、Concept選択（マルチセレクト、既存Concept一覧から選択）が含まれる

#### Scenario: Claim作成の送信

- **WHEN** ユーザーがClaim作成フォームに必要事項を入力し「作成」ボタンをクリックする
- **THEN** `POST /api/v1/claims` にリクエストが送信され、成功時に作成されたClaimの詳細画面に遷移する
- **THEN** エラー時にはフォーム上にフィールド単位のバリデーションエラーが表示される

#### Scenario: Claim作成の入力バリデーション

- **WHEN** statementが未入力の状態で送信を試みる
- **THEN** フォーム上に「statementは必須です」というエラーメッセージが表示され、送信がブロックされる

### Requirement: Concept作成フォーム

システムはWeb UIからConceptを新規作成できるフォームを提供しなければならない（SHALL）。

#### Scenario: Concept作成フォーム表示

- **WHEN** ユーザーがConcept一覧画面の「新規作成」ボタンをクリックする
- **THEN** Concept作成フォームが表示される
- **THEN** フォームにはlabel（テキスト入力）、description（テキストエリア）、field（テキスト入力またはセレクト）、Term選択（マルチセレクト、既存Term一覧から選択）が含まれる

#### Scenario: Concept作成の送信

- **WHEN** ユーザーがConcept作成フォームに必要事項を入力し「作成」ボタンをクリックする
- **THEN** `POST /api/v1/concepts` にリクエストが送信され、成功時にConcept一覧が再読み込みされる

### Requirement: Context作成フォーム

システムはWeb UIからContextを新規作成できるフォームを提供しなければならない（SHALL）。

#### Scenario: Context作成フォーム表示

- **WHEN** ユーザーがContext一覧画面の「新規作成」ボタンをクリックする
- **THEN** Context作成フォームが表示される
- **THEN** フォームにはname（テキスト入力）、description（テキストエリア）、field（テキスト入力）、assumptions（タグ入力またはテキストエリア）、parent_context（オプション、既存Context一覧から選択）が含まれる

#### Scenario: Context作成の送信

- **WHEN** ユーザーがContext作成フォームに必要事項を入力し「作成」ボタンをクリックする
- **THEN** `POST /api/v1/contexts` にリクエストが送信され、成功時にContext一覧が再読み込みされる
- **THEN** name重複時（409 Conflict）にはフォーム上にエラーメッセージが表示される

### Requirement: Evidence作成フォーム

システムはWeb UIからEvidenceを新規作成できるフォームを提供しなければならない（SHALL）。

#### Scenario: Evidence作成フォーム表示

- **WHEN** ユーザーがEvidence一覧画面またはClaim詳細画面の「Evidence追加」ボタンをクリックする
- **THEN** Evidence作成フォームが表示される
- **THEN** フォームにはtitle（テキスト入力）、evidence_type（セレクト：textbook / paper / experiment / proof / expert_opinion）、source（テキスト入力）、excerpt（テキストエリア、オプション）、reliability（セレクト：high / medium / low / unverified）、Claim紐付け（マルチセレクト）が含まれる

#### Scenario: Evidence作成の送信

- **WHEN** ユーザーがEvidence作成フォームに必要事項を入力し「作成」ボタンをクリックする
- **THEN** `POST /api/v1/evidence` にリクエストが送信され、成功時に関連画面が再読み込みされる

### Requirement: AI接続候補の手動トリガー

システムはWeb UIから特定のClaimに対してAI接続候補の生成を手動でリクエストできるUIを提供しなければならない（SHALL）。

#### Scenario: 手動トリガーボタン表示

- **WHEN** Claim詳細画面が表示される
- **THEN** 「AI接続候補を生成」ボタンが表示される

#### Scenario: 手動トリガーの実行

- **WHEN** ユーザーが「AI接続候補を生成」ボタンをクリックする
- **THEN** `POST /api/v1/agent/suggest-connections` に`source_entity_type="claim"` と `source_entity_id` が送信される
- **THEN** ボタンがローディング状態になり、生成完了後にAI接続候補セクションが更新される

#### Scenario: トリガー結果の表示

- **WHEN** AI接続候補生成が完了する
- **THEN** 生成された候補がClaim詳細画面のAI接続候補セクションに即座に反映される
- **THEN** 候補が0件の場合は「候補が見つかりませんでした」のメッセージが表示される

### Requirement: レビューフロー後のUI反映

システムはApprove/Reject操作後にUIを適切に更新しなければならない（SHALL）。

#### Scenario: 承認後のUI更新

- **WHEN** ユーザーがProposalを承認し、レビューが正常に送信される
- **THEN** 当該ProposalカードがレビューキューからFade-outで消え、成功トーストメッセージが表示される
- **THEN** Claim詳細画面のAI接続候補セクションからも当該候補が消え、承認された接続が関連Claim一覧に反映される

#### Scenario: 却下後のUI更新

- **WHEN** ユーザーがProposalを却下し、レビューが正常に送信される
- **THEN** 当該ProposalカードがレビューキューからFade-outで消え、却下通知トーストメッセージが表示される

#### Scenario: レビューエラー時のフィードバック

- **WHEN** レビュー送信がネットワークエラーまたはサーバーエラーで失敗する
- **THEN** エラートーストメッセージが表示され、Proposalカードは元の状態のまま維持される
