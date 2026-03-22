## Technical Decisions

### トランザクション境界の統一: セッション共有アプローチ

Outboxパターンではなく、EventStoreの `append()` メソッドに既存のSQLAlchemyセッションを渡す方式を採用する。

理由:
- 現在の `EventStore.append()` は内部で独立セッションを使用しているが、呼び出し元のサービスセッションを受け取れるようシグネチャを拡張すれば最小限の変更で済む
- Outboxパターンは非同期メッセージングが必要な分散システム向けであり、現在の単一DB構成では過剰
- セッション共有により、`session.commit()` 一回でドメイン書き込みとイベント書き込みが同時にコミットされる

### EventStore.append() のシグネチャ変更

```python
# Before
async def append(self, **kwargs) -> Event:
    # 内部でセッション作成・コミット

# After
async def append(self, *, session: Session | None = None, **kwargs) -> Event:
    # session が渡された場合はそのセッション内でINSERT（commitしない）
    # session が None の場合は従来通り内部セッション使用（後方互換）
```

### 関連IDバリデーション: カウント比較方式

リクエストで指定されたIDの数と、DBから取得できたエンティティの数を比較する:

```python
if payload.context_ids:
    contexts = session.scalars(
        select(Context).where(Context.id.in_(parsed_ids))
    ).all()
    if len(contexts) != len(payload.context_ids):
        missing = set(payload.context_ids) - {str(c.id) for c in contexts}
        raise ValueError(f"Context IDs not found: {missing}")
```

この方式は既存のクエリパターンに最小限の追加で実装でき、全サービスで統一的に適用できる。

## Architecture

```
Service.create()
  ├─ session.add(entity)        # ドメイン書き込み
  ├─ session.flush()            # ID取得
  ├─ validate_related_ids()     # 関連ID全数検証
  ├─ event_store.append(session=session, ...)  # イベント書き込み（同一セッション）
  └─ session.commit()           # 一括コミット
```

### 影響ファイル

| ファイル | 変更内容 |
|---------|---------|
| `backend/app/events/store.py` | `append()` に `session` パラメータ追加 |
| `backend/app/services/claim_service.py` | セッション共有 + IDバリデーション |
| `backend/app/services/concept_service.py` | 同上 |
| `backend/app/services/context_service.py` | 同上 |
| `backend/app/services/term_service.py` | 同上 |
| `backend/app/services/proposal_service.py` | セッション共有 |
| `backend/app/interfaces/event_store.py` | インターフェースにsessionパラメータ追加 |

## Implementation Approach

1. `IEventStore` インターフェースと `EventStore` 実装に `session` パラメータを追加
2. 各サービスの `create()` / `update()` メソッドで `session.commit()` をイベント書き込み後に移動
3. 各サービスに関連IDバリデーションロジックを追加
4. 既存テストの更新と新規バリデーションテストの追加
