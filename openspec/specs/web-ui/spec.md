# Web UI Specification

## Purpose

TsumuGraphのClaim中心知識グラフを研究者および企業R&D部門が直感的に操作できるWebアプリケーションを定義する。Claim一覧・詳細表示、Contextによる絞り込み、Evidenceカード表示、AI接続候補のレビュー、グラフビューを提供する。

## Requirements

### Requirement: ダッシュボード画面

システムはプラットフォーム全体の概要を表示するダッシュボード画面を提供しなければならない（SHALL）。

#### Scenario: 統計カード表示

- **WHEN** ユーザーがダッシュボード画面にアクセスする
- **THEN** 以下の統計が数値カードとして表示される: 総Claim数、総Concept数、総Context数、総Evidence数、pendingのProposal数

#### Scenario: 最新アクティビティ表示

- **WHEN** ダッシュボード画面が表示される
- **THEN** `GET /api/v1/events/recent` から取得した直近のイベントが時系列順で最大10件表示される
- **THEN** 各アクティビティにはタイトル、概要、実行者名、タイムスタンプ、該当エンティティへのリンクが含まれる

#### Scenario: pendingのProposalへのショートカット

- **WHEN** pendingのProposal数カードをクリックする
- **THEN** レビューキュー画面に遷移する

### Requirement: Claim一覧画面

システムはClaimのフィルタリング・検索・一覧表示画面を提供しなければならない（SHALL）。

#### Scenario: Claim一覧表示

- **WHEN** ユーザーがClaim一覧画面にアクセスする
- **THEN** Claim一覧がテーブルまたはカード形式で表示される（statement先頭部分、claim_type、trust_status、Context名バッジ）

#### Scenario: Contextによる絞り込み

- **WHEN** ユーザーがフィルターバーでContext（例: "Classical Thermodynamics"）を選択する
- **THEN** 選択されたContextに属するClaimのみが一覧に表示される

#### Scenario: 分野による絞り込み

- **WHEN** ユーザーがフィルターバーで分野（例: "熱力学"）を選択する
- **THEN** 選択された分野のContextに属するClaimのみが一覧に表示される

#### Scenario: 信頼状態による絞り込み

- **WHEN** ユーザーがフィルターバーでtrust_status（例: "ai_suggested"）を選択する
- **THEN** 指定された信頼状態のClaimのみが一覧に表示される

#### Scenario: テキスト検索

- **WHEN** ユーザーが検索ボックスにキーワード（例: "entropy"）を入力する
- **THEN** statementにキーワードを含むClaimが一覧に表示される

#### Scenario: ページネーション

- **WHEN** Claim一覧の件数が1ページの表示上限を超える
- **THEN** ページ送りコントロールが表示され、次ページ・前ページの遷移が可能

#### Scenario: Claim選択による詳細遷移

- **WHEN** ユーザーがClaim一覧の項目をクリックする
- **THEN** 当該ClaimのClaim詳細画面に遷移する

### Requirement: Claim詳細画面

システムはClaimの全情報を閲覧できる詳細画面を提供しなければならない（SHALL）。

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

#### Scenario: AI接続候補セクション

- **WHEN** 当該Claimに関連するpendingのCross-field Connection Proposalが存在する場合
- **THEN** AI接続候補セクションに候補Claim（statement、Context、確信度バー）が表示され、各候補に「承認」「却下」ボタンが配置される

#### Scenario: 変更履歴タイムライン

- **WHEN** ユーザーが「履歴」タブをクリックする
- **THEN** `GET /api/v1/claims/{id}/history` から取得した整形済みイベントがタイムライン形式で表示される（タイトル、概要、実行者名、タイムスタンプ）
- **THEN** 各イベントのタイトルはイベント種別に対応する人間可読テキストで表示される

### Requirement: Context一覧・詳細画面

システムはContext（理論文脈）の一覧・詳細表示画面を提供しなければならない（SHALL）。

#### Scenario: Context一覧表示

- **WHEN** ユーザーがContext一覧画面にアクセスする
- **THEN** Context一覧がツリー形式またはリスト形式で表示される（name、field、Claim数、assumptions概要）
- **THEN** 親子関係がある場合はインデントまたはツリー構造で階層が表現される

#### Scenario: Context詳細表示

- **WHEN** ユーザーがContextを選択する
- **THEN** Context詳細（name、description、field、assumptions一覧、子Context一覧）と、当該Contextに属するClaim一覧が表示される

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

### Requirement: グラフビュー画面

システムはClaim/Conceptの関係をインタラクティブなグラフとして可視化する画面を提供しなければならない（SHALL）。

#### Scenario: ノードとエッジの表示

- **WHEN** ユーザーがグラフビュー画面にアクセスする
- **THEN** Claim/Conceptがノードとして、それらの関連・接続がエッジとしてD3.js系の力指向グラフ（force-directed graph）で表示される
- **THEN** ノードの種類（Claim / Concept）が色またはアイコンで区別される
- **THEN** グラフはマウスホイールによるズーム、ドラッグによるパン操作をサポートする

#### Scenario: ノードの操作

- **WHEN** ユーザーがグラフ上のノードをクリックする
- **THEN** ノードの概要情報（Claimのstatement先頭部分、またはConceptのlabel）がツールチップまたはパネルで表示される
- **THEN** 概要情報内から詳細画面へのリンクが提供される

#### Scenario: ノードのドラッグ

- **WHEN** ユーザーがノードをドラッグする
- **THEN** ノードが追従し、力指向レイアウトがリアルタイムに再計算される

### Requirement: AI候補一覧画面

システムはAI Linking Agentが生成した接続候補の専用一覧画面を提供しなければならない（SHALL）。

#### Scenario: AI候補一覧表示

- **WHEN** ユーザーがAI候補一覧画面（`/suggestions`）にアクセスする
- **THEN** `GET /api/v1/agent/suggestions` から取得した候補一覧がカード形式で表示される
- **THEN** 各カードにはproposal_type、接続元Claim、接続先Claim、connection_type、確信度、rationale概要が表示される

#### Scenario: AI候補のフィルタリング

- **WHEN** ユーザーがstatusまたは最低確信度でフィルタリングする
- **THEN** 選択条件に合致する候補のみが表示される

#### Scenario: AI候補のインラインレビュー

- **WHEN** ユーザーが候補カードの「承認」または「却下」ボタンをクリックする
- **THEN** レビュー入力UIが表示され、コメント送信後に候補のステータスが更新される
- **THEN** 成功時にフィードバックが表示される

### Requirement: レビューキュー画面

システムはpendingのProposal一覧とレビュー操作UIを提供しなければならない（SHALL）。

#### Scenario: レビュー待ちProposal一覧表示

- **WHEN** ユーザーがレビューキュー画面にアクセスする
- **THEN** status="pending" のProposal一覧がカード形式で表示される（proposal_type、proposed_by、rationale概要、created_at）

#### Scenario: Proposalカード詳細展開

- **WHEN** ユーザーがProposalカードをクリックする
- **THEN** Proposalの詳細（payload内容、対象エンティティ情報、rationale全文、確信度）が展開表示される

#### Scenario: レビュー操作（承認）

- **WHEN** ユーザーがProposalカードの「承認」ボタンをクリックする
- **THEN** コメント入力ダイアログが表示され、確認後にReview（decision="approve"）が送信される

#### Scenario: レビュー操作（却下）

- **WHEN** ユーザーがProposalカードの「却下」ボタンをクリックする
- **THEN** コメント入力ダイアログ（必須）が表示され、確認後にReview（decision="reject"）が送信される

#### Scenario: レビュー完了フィードバック

- **WHEN** レビューが正常に送信される
- **THEN** 当該ProposalカードがUIから消え（またはステータスが更新され）、成功メッセージが表示される

### Requirement: 検索画面

システムは全エンティティを横断的に検索できる画面を提供しなければならない（SHALL）。

#### Scenario: 検索実行

- **WHEN** ユーザーが検索バーにクエリを入力しEnterを押す
- **THEN** Claim、Concept、Term、Context、Evidenceを横断的に検索した結果がエンティティ種別ごとにグループ化されて表示される

#### Scenario: 検索結果フィルタリング

- **WHEN** 検索結果が表示されている状態で、ユーザーがエンティティ種別フィルター（例: "Claims only"）を選択する
- **THEN** 選択された種別の結果のみが表示される

#### Scenario: 検索結果からの遷移

- **WHEN** ユーザーが検索結果の項目をクリックする
- **THEN** 当該エンティティの詳細画面に遷移する

### Requirement: レスポンシブデザイン

Web UIは主要な画面サイズで適切に表示されなければならない（SHALL）。

#### Scenario: デスクトップ表示

- **WHEN** 画面幅が1024px以上の環境でアクセスする
- **THEN** すべての画面がフル機能で表示される（サイドバーナビゲーション、テーブル表示等）

#### Scenario: タブレット表示

- **WHEN** 画面幅が768px〜1023pxの環境でアクセスする
- **THEN** サイドバーが折りたたみ可能になり、テーブルがカード形式表示に切り替わる等、最低限の操作性が確保される
