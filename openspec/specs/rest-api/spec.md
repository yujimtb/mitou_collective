# REST API Specification

## Purpose

CollectiveScienceのすべての機能を外部から利用可能にするREST APIを定義する。Claim中心知識グラフのCRUD操作、Proposal/Reviewワークフロー、AI Linking Agent、検索機能をHTTPエンドポイントとして提供する。

## Requirements

### Requirement: Claim API

システムはClaimに対するCRUD操作および関連情報の取得をREST APIで提供しなければならない（SHALL）。

#### Scenario: Claim一覧取得

- **WHEN** `GET /api/v1/claims` がリクエストされる
- **THEN** Claim一覧がJSON形式で返される
- **THEN** クエリパラメータ `context`（Context名）、`field`（分野名）、`trust_status`（信頼状態）、`claim_type`（Claim種別）、`search`（全文検索クエリ）、`page`（ページ番号）、`per_page`（1ページあたり件数、デフォルト: 20、最大: 100）によるフィルタリングとページネーションをサポートする
- **THEN** レスポンスにはtotal_count、current_page、items（Claim配列）が含まれる

#### Scenario: Claim作成

- **WHEN** `POST /api/v1/claims` がリクエストボディ（statement、claim_type、context_ids、concept_ids）と共にリクエストされる
- **THEN** Claimが作成され、201 Createdとともに作成されたClaimのJSON表現が返される
- **THEN** `ClaimCreated` イベントがEvent Storeに記録される

#### Scenario: Claim詳細取得

- **WHEN** `GET /api/v1/claims/{id}` がリクエストされる
- **THEN** Claim詳細（statement、claim_type、trust_status、version、関連Concept一覧、属するContext一覧、紐づくEvidence一覧、CIR）がJSON形式で返される
- **THEN** 指定されたIDが存在しない場合、404 Not Foundが返される

#### Scenario: Claim更新

- **WHEN** `PUT /api/v1/claims/{id}` がリクエストボディ（statement、claim_type等の更新フィールド）と共にリクエストされる
- **THEN** Claimが更新され、versionがインクリメントされ、200 OKとともに更新後のClaimが返される

#### Scenario: Claim変更履歴取得

- **WHEN** `GET /api/v1/claims/{id}/history` がリクエストされる
- **THEN** 当該ClaimのEvent Store内のイベント一覧が時系列順でJSON形式で返される

### Requirement: Concept API

システムはConceptに対するCRUD操作をREST APIで提供しなければならない（SHALL）。

#### Scenario: Concept一覧取得

- **WHEN** `GET /api/v1/concepts` がリクエストされる
- **THEN** Concept一覧がJSON形式で返される
- **THEN** クエリパラメータ `field`（分野名）、`search`（ラベル検索）によるフィルタリングをサポートする

#### Scenario: Concept作成

- **WHEN** `POST /api/v1/concepts` がリクエストボディ（label、description、field、term_ids、referent_id）と共にリクエストされる
- **THEN** Conceptが作成され、201 Createdとともに作成されたConceptが返される

#### Scenario: Concept詳細取得

- **WHEN** `GET /api/v1/concepts/{id}` がリクエストされる
- **THEN** Concept詳細（label、description、field、関連Term一覧、紐づくClaim一覧、Referent情報）がJSON形式で返される

#### Scenario: Concept間接続一覧取得

- **WHEN** `GET /api/v1/concepts/{id}/connections` がリクエストされる
- **THEN** 当該Conceptに関連するClaimを経由した異分野接続（Cross-field Connection）一覧がJSON形式で返される

### Requirement: Context API

システムはContextに対するCRUD操作をREST APIで提供しなければならない（SHALL）。

#### Scenario: Context一覧取得

- **WHEN** `GET /api/v1/contexts` がリクエストされる
- **THEN** Context一覧（name、field、Claim数）がJSON形式で返される

#### Scenario: Context作成

- **WHEN** `POST /api/v1/contexts` がリクエストボディ（name、description、field、assumptions、parent_context_id）と共にリクエストされる
- **THEN** Contextが作成され、201 Createdとともに作成されたContextが返される
- **THEN** nameが一意でない場合、409 Conflictが返される

#### Scenario: Context詳細取得

- **WHEN** `GET /api/v1/contexts/{id}` がリクエストされる
- **THEN** Context詳細（name、description、field、assumptions、属するClaim一覧、子Context一覧）がJSON形式で返される

### Requirement: Evidence API

システムはEvidenceに対するCRUD操作をREST APIで提供しなければならない（SHALL）。

#### Scenario: Evidence一覧取得

- **WHEN** `GET /api/v1/evidence` がリクエストされる
- **THEN** Evidence一覧がJSON形式で返される
- **THEN** クエリパラメータ `evidence_type`、`reliability`、`search` によるフィルタリングをサポートする

#### Scenario: Evidence作成

- **WHEN** `POST /api/v1/evidence` がリクエストボディ（evidence_type、title、source、excerpt、claim_ids、relationship）と共にリクエストされる
- **THEN** Evidenceが作成され、指定されたClaimとの関連が記録され、201 Createdが返される

#### Scenario: Evidence詳細取得

- **WHEN** `GET /api/v1/evidence/{id}` がリクエストされる
- **THEN** Evidence詳細（evidence_type、title、source、excerpt、reliability、関連Claim一覧）がJSON形式で返される

### Requirement: Term API

システムはTermに対するCRUD操作をREST APIで提供しなければならない（SHALL）。

#### Scenario: Term一覧取得

- **WHEN** `GET /api/v1/terms` がリクエストされる
- **THEN** Term一覧がJSON形式で返される
- **THEN** クエリパラメータ `search`（表層形検索）、`language`（言語コード）によるフィルタリングをサポートする

#### Scenario: Term作成

- **WHEN** `POST /api/v1/terms` がリクエストボディ（surface_form、language、field_hint、concept_ids）と共にリクエストされる
- **THEN** Termが作成され、指定されたConceptとの関連が記録され、201 Createdが返される

#### Scenario: Term詳細取得

- **WHEN** `GET /api/v1/terms/{id}` がリクエストされる
- **THEN** Term詳細（surface_form、language、field_hint、関連Concept一覧）がJSON形式で返される

### Requirement: Proposal / Review API

システムはProposal/Reviewワークフロー操作をREST APIで提供しなければならない（SHALL）。

#### Scenario: Proposal一覧取得

- **WHEN** `GET /api/v1/proposals` がリクエストされる
- **THEN** Proposal一覧がJSON形式で返される
- **THEN** クエリパラメータ `status`（pending / in_review / approved / rejected / withdrawn）、`proposed_by`（Actor ID）、`proposal_type` によるフィルタリングをサポートする

#### Scenario: Proposal作成

- **WHEN** `POST /api/v1/proposals` がリクエストボディ（proposal_type、target_entity_type、target_entity_id、payload、rationale）と共にリクエストされる
- **THEN** Proposalが作成され、status="pending" で201 Createdが返される

#### Scenario: Proposal詳細取得

- **WHEN** `GET /api/v1/proposals/{id}` がリクエストされる
- **THEN** Proposal詳細（proposal_type、proposed_by、target情報、payload、rationale、status、関連Review一覧）がJSON形式で返される

#### Scenario: Proposalレビュー投稿

- **WHEN** `POST /api/v1/proposals/{id}/review` がリクエストボディ（decision、comment、confidence）と共にリクエストされる
- **THEN** Reviewが記録され、decisionに応じてProposalのステートが遷移する
- **THEN** decision="approve" の場合、payloadに基づいて知識グラフへの変更が適用される
- **THEN** 提案者自身がレビューを試みた場合、403 Forbiddenが返される

### Requirement: AI Linking Agent API

システムはAI Linking Agentの操作をREST APIで提供しなければならない（SHALL）。

#### Scenario: 接続候補生成リクエスト

- **WHEN** `POST /api/v1/agent/suggest-connections` がリクエストボディ（source_entity_type、source_entity_id、target_field）と共にリクエストされる
- **THEN** Linking Agentによる接続候補生成ジョブが開始され、202 Acceptedとともにjob_idが返される

#### Scenario: 生成済み候補一覧取得

- **WHEN** `GET /api/v1/agent/suggestions` がリクエストされる
- **THEN** AI Linking Agentが生成した接続候補（Proposal）一覧がJSON形式で返される
- **THEN** クエリパラメータ `status`、`min_confidence`（最低確信度） によるフィルタリングをサポートする

### Requirement: 検索API

システムは全エンティティ横断の検索機能をREST APIで提供しなければならない（SHALL）。

#### Scenario: 横断検索

- **WHEN** `GET /api/v1/search?q={query}` がリクエストされる
- **THEN** Claim、Concept、Term、Context、Evidenceを横断的に検索し、マッチしたエンティティをスコア順でJSON形式で返される
- **THEN** クエリパラメータ `scope`（claims / concepts / terms / contexts / evidence）で検索対象を限定できる

### Requirement: API共通仕様

すべてのAPIエンドポイントは以下の共通仕様に従わなければならない（SHALL）。

#### Scenario: 認証

- **WHEN** 認証が必要なエンドポイントにリクエストされる
- **THEN** AuthorizationヘッダーにBearer JWTトークンが必要であり、トークンが無効または欠落している場合は401 Unauthorizedが返される

#### Scenario: 入力バリデーション

- **WHEN** リクエストボディが不正な場合（必須フィールド欠落、型不一致等）
- **THEN** 422 Unprocessable Entityとともにフィールド単位のエラーメッセージがJSON形式で返される

#### Scenario: レスポンス形式

- **WHEN** 任意のAPIエンドポイントがレスポンスを返す
- **THEN** Content-TypeはすべてのケースでJSON（application/json）とする

#### Scenario: エラーレスポンス形式

- **WHEN** APIエラーが発生する
- **THEN** レスポンスボディには `{"error": {"code": "<error_code>", "message": "<human_readable>", "details": {}}}` の統一フォーマットが使用される
