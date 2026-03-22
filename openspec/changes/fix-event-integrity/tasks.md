## Tasks

### Proposal event href 修正

- [x] `backend/app/events/formatting.py` の `event_href()` で `aggregate_type == "proposal"` の分岐を `/proposals/{aggregate_id}` から `/review` に変更
- [x] `event_href` のテストを追加または更新（proposal タイプが `/review` を返すことを検証）

### ClaimCreated.context_names 修正

- [x] `backend/app/services/claim_service.py` の `create()` メソッドで、`ClaimCreated` イベント構築時の `context_names=schema.context_ids` を `context_names=[ctx.name for ctx in contexts]` に修正
- [x] context_names が正しく Context.name を含むことを検証するテストを追加

### 検証

- [x] 既存テストが全てパスすることを確認（`python -m pytest tests`）
