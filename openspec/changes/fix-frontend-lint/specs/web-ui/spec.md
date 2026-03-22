## MODIFIED Requirements

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

#### Scenario: ESLint自動実行対応

- **WHEN** `npm run lint` が実行される
- **THEN** ESLintが非インタラクティブモードで実行され、ゼロ終了コード（またはwarningsのみ）で完了する
- **THEN** Next.jsのESLintセットアップウィザードが起動しない
