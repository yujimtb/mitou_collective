## Technical Decisions

### Server Actions for Authenticated Mutations

Next.js Server Actions (`"use server"`) を使用してブラウザ側ミューテーションをサーバーサイドに移動する。Route Handlers (`app/api/`) ではなく Server Actions を選択する理由:

- クライアントコンポーネントから直接呼び出せるため、既存のUI構造を大きく変更する必要がない
- `CS_API_TOKEN` はサーバープロセス内のみで参照され、ブラウザバンドルに含まれない
- Next.js が自動的にPOSTエンドポイントとCSRF保護を提供する

### APIエラー型の設計

`lib/api.ts` に `ApiError` クラスを追加し、HTTPステータスコードを保持する:

```typescript
class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
  }
}
```

既存の `api<T>()` ヘルパーは非2xxレスポンス時に `ApiError` をスローするよう変更する。

### 詳細ページのエラーハンドリングパターン

各詳細ページ（claims, concepts, contexts, evidence, terms）で統一するパターン:

```typescript
try {
  const data = await fetchDetail(id);
  return <DetailComponent data={data} />;
} catch (e) {
  if (e instanceof ApiError && e.status === 404) {
    notFound();
  }
  throw e; // Next.js error boundary が処理
}
```

`throw e;` によりNext.jsの `error.tsx` が処理するため、各ページに個別のエラーUIは不要。

## Architecture

```
Browser (Client Component)
  ↓ Server Action call
Server Action ("use server")
  ↓ process.env.CS_API_TOKEN
Backend API (Bearer auth)
```

### 影響ファイル

| ファイル | 変更内容 |
|---------|---------|
| `frontend/src/lib/api.ts` | `ApiError` クラス追加、`api<T>()` のエラーハンドリング改善 |
| `frontend/src/lib/actions.ts` (新規) | Server Actions (`createClaimAction`, `submitReviewAction`, `suggestConnectionsAction`) |
| `frontend/src/components/CreateClaimDialog.tsx` | 直接API呼び出し → Server Action呼び出しに変更 |
| `frontend/src/components/proposals/ReviewDialog.tsx` | 同上 |
| `frontend/src/components/claims/ClaimDetail.tsx` | 同上 |
| `frontend/src/app/claims/[id]/page.tsx` | `catch { notFound() }` → `ApiError` ベースの分岐 |
| `frontend/src/app/concepts/[id]/page.tsx` | 同上 |
| `frontend/src/app/contexts/[id]/page.tsx` | 同上 |
| `frontend/src/app/evidence/[id]/page.tsx` | 同上 |
| `frontend/src/app/terms/[id]/page.tsx` | 同上 |

## Implementation Approach

1. `ApiError` クラスを `lib/api.ts` に追加し、`api<T>()` を改修
2. `lib/actions.ts` に Server Actions を作成（既存 API ヘルパーをラップ）
3. 3つのクライアントコンポーネントを Server Action 呼び出しに変更
4. 5つの詳細ページのエラーハンドリングを改修
5. 全変更に対するテスト追加
