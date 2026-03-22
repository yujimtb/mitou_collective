## Technical Decisions

### Proposal event href → `/review`

`event_href()` の proposal 分岐を `/proposals/{id}` から `/review` に変更する。フロントエンドに proposal 詳細ページは存在しないが、レビュー画面 (`/review`) は存在し、proposal 一覧が表示されるため妥当な遷移先である。

### ClaimCreated.context_names の修正

`claim_service.py` の `create()` メソッド内で、`ClaimCreated` イベント構築時に `context_names=schema.context_ids` となっている箇所を、実際の `Context.name` 値のリストに置き換える。セッション内で Context オブジェクトは既に取得済みのため、追加クエリは不要。

## Architecture

影響範囲は2ファイルのみの局所的な修正:

```
backend/app/events/formatting.py  →  proposal href: "/review"
backend/app/services/claim_service.py  →  context_names: [ctx.name for ctx]
```

### 影響ファイル

| ファイル | 変更内容 |
|---------|---------|
| `backend/app/events/formatting.py` | `event_href()` の proposal 分岐を `/review` に変更 |
| `backend/app/services/claim_service.py` | `ClaimCreated` 構築時に `context_names` を Context.name リストに修正 |

## Implementation Approach

1. `formatting.py` の `event_href()` を修正
2. `claim_service.py` の `create()` 内で context names を正しく取得
3. 既存テストの更新・追加
