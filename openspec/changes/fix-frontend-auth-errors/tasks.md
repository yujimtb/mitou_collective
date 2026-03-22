## Tasks

### ApiError クラスとエラー伝播

- [x] `frontend/src/lib/api.ts` に `ApiError` クラスを追加（status と message を保持）
- [x] `api<T>()` ヘルパーで非2xxレスポンス時に `ApiError` をスローするよう変更
- [x] 既存の全 API ヘルパー関数が `ApiError` を正しくスローすることを確認

### Server Actions の作成

- [x] `frontend/src/lib/actions.ts` を新規作成（`"use server"` ディレクティブ付き）
- [x] `createClaimAction` Server Action を実装（`createClaim` API ヘルパーをラップ）
- [x] `submitReviewAction` Server Action を実装（`submitReview` API ヘルパーをラップ）
- [x] `suggestConnectionsAction` Server Action を実装（AI提案 API ヘルパーをラップ）

### クライアントコンポーネントの移行

- [x] `frontend/src/components/CreateClaimDialog.tsx` を Server Action 呼び出しに変更
- [x] `frontend/src/components/proposals/ReviewDialog.tsx` を Server Action 呼び出しに変更
- [x] `frontend/src/components/claims/ClaimDetail.tsx` の AI提案呼び出しを Server Action に変更

### 詳細ページのエラーハンドリング修正

- [x] `frontend/src/app/claims/[id]/page.tsx` のエラーハンドリングを `ApiError` ベースに変更（404のみ `notFound()`）
- [x] `frontend/src/app/concepts/[id]/page.tsx` のエラーハンドリングを同様に変更
- [x] `frontend/src/app/contexts/[id]/page.tsx` のエラーハンドリングを同様に変更
- [x] `frontend/src/app/evidence/[id]/page.tsx` のエラーハンドリングを同様に変更
- [x] `frontend/src/app/terms/[id]/page.tsx` のエラーハンドリングを同様に変更

### テストと検証

- [x] Server Actions のユニットテストを追加
- [x] `ApiError` のエラー伝播テストを追加
- [x] `npm run build` が成功することを確認
- [x] `npm run typecheck` が成功することを確認
