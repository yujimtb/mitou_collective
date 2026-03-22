## Technical Decisions

### ESLint Flat Config (`eslint.config.mjs`)

Next.js 15 + ESLint 9 の組み合わせでは flat config (`eslint.config.mjs`) を使用する。`.eslintrc.json` ではなく flat config を選択する理由:

- ESLint 9 のデフォルト設定形式
- Next.js は `eslint-config-next` を提供しており、flat config でも使用可能
- セットアップウィザードの起動を回避するには、設定ファイルが存在すれば十分

### 最小構成

```javascript
import { dirname } from "path";
import { fileURLToPath } from "url";
import { FlatCompat } from "@eslint/eslintrc";

const __dirname = dirname(fileURLToPath(import.meta.url));
const compat = new FlatCompat({ baseDirectory: __dirname });

export default [...compat.extends("next/core-web-vitals", "next/typescript")];
```

`eslint-config-next` は Next.js インストール時に含まれているため、追加の devDependency は `@eslint/eslintrc` のみ（flat config 互換レイヤー）。

## Architecture

設定ファイル追加のみ。ソースコード変更なし。

### 影響ファイル

| ファイル | 変更内容 |
|---------|---------|
| `frontend/eslint.config.mjs` (新規) | ESLint flat config |
| `frontend/package.json` | `@eslint/eslintrc` devDependency 追加（必要に応じて） |

## Implementation Approach

1. `frontend/eslint.config.mjs` を作成
2. 必要な devDependency を追加
3. `npm run lint` が非インタラクティブに実行されることを確認
4. lint エラーがあれば修正（warnings は許容）
