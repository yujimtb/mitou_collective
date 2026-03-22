## Tasks

### ESLint 設定追加

- [x] `frontend/eslint.config.mjs` を作成（`next/core-web-vitals` + `next/typescript` 拡張）
- [x] 必要な devDependency（`@eslint/eslintrc` 等）を `package.json` に追加し `npm install`
- [x] `npm run lint` が非インタラクティブに実行されることを確認

### Lint エラー修正

- [x] `npm run lint` で検出されたエラーを修正（warnings は許容）
- [x] `npm run build` が引き続き成功することを確認
- [x] `npm run typecheck` が引き続き成功することを確認
