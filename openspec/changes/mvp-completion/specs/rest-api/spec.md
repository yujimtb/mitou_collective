## ADDED Requirements

### Requirement: フロントエンド向けリファレンスデータAPI

システムはフロントエンドのフォームで使用するリファレンスデータ取得エンドポイントを提供しなければならない（SHALL）。

#### Scenario: Context選択肢一覧取得

- **WHEN** `GET /api/v1/contexts?fields=id,name,field` がリクエストされる
- **THEN** フォームのセレクトボックス用に軽量なContext選択肢リスト（id、name、field）がJSON形式で返される

#### Scenario: Concept選択肢一覧取得

- **WHEN** `GET /api/v1/concepts?fields=id,label,field` がリクエストされる
- **THEN** フォームのセレクトボックス用に軽量なConcept選択肢リスト（id、label、field）がJSON形式で返される

#### Scenario: Term選択肢一覧取得

- **WHEN** `GET /api/v1/terms?fields=id,surface_form,language` がリクエストされる
- **THEN** フォームのセレクトボックス用に軽量なTerm選択肢リスト（id、surface_form、language）がJSON形式で返される

### Requirement: CORS設定

システムはフロントエンドからのクロスオリジンリクエストを許可するCORS設定を提供しなければならない（SHALL）。

#### Scenario: ローカル開発時のCORS

- **WHEN** `http://localhost:3000` からAPIリクエストがされる
- **THEN** CORSプリフライトリクエストが成功し、実リクエストが処理される
