## Tasks

### EventStore のセッション共有対応

- [x] `backend/app/interfaces/event_store.py` の `IEventStore.append()` に `session: Session | None = None` パラメータを追加
- [x] `backend/app/events/store.py` の `EventStore.append()` を改修: session が渡された場合はそのセッション内でINSERT（commitしない）
- [x] session が None の場合の後方互換動作を維持

### サービスのトランザクション境界修正

- [x] `backend/app/services/claim_service.py` の `create()` を改修: `session.commit()` をイベント書き込み後に移動し、session を `event_store.append()` に渡す
- [x] `backend/app/services/claim_service.py` の `update()` を同様に改修
- [x] `backend/app/services/claim_service.py` の `change_trust()` を同様に改修
- [x] `backend/app/services/concept_service.py` の `create()` / `update()` を同様に改修
- [x] `backend/app/services/context_service.py` の `create()` / `update()` を同様に改修
- [x] `backend/app/services/term_service.py` の `create()` / `update()` を同様に改修
- [x] `backend/app/services/proposal_service.py` の `create()` を同様に改修

### 関連IDバリデーション追加

- [x] `backend/app/services/claim_service.py` の `create()` / `update()` に context_ids、concept_ids、evidence_ids の全数検証を追加
- [x] `backend/app/services/concept_service.py` に term_ids、referent_id の検証を追加
- [x] `backend/app/services/term_service.py` に concept_ids の検証を追加
- [x] バリデーション失敗時に明確な `ValueError` または `400` レスポンスを返すことを確認

### テストと検証

- [x] トランザクション原子性のテスト追加（イベント書き込み失敗時にドメイン変更がロールバックされることを検証）
- [x] 関連IDバリデーションのテスト追加（存在しないIDでの400エラー検証）
- [x] 既存テストが全てパスすることを確認（`python -m pytest tests`）
