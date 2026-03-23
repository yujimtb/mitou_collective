# 品質監査

> **🇯🇵 日本語** | [English](#quality-audit)

## 対象範囲

本ドキュメントは、最新の修正パス後のリポジトリ全体の品質監査の現在の状態を記録したものです。既に修正済みの不具合の過去のリストではなく、プロトタイプの現在の検証済みステータスを反映しています。

監査スナップショット：

- バックエンド: `python -m ruff check .` および `python -m pytest tests` → 102テスト合格
- CLI: `python -m pytest` → 16テスト合格
- フロントエンド: `npm run lint`、`npm run typecheck`、`npm run test -- --run`、`npm run build` 合格

## 現在の状態

以前報告されたフロントエンド認証境界、詳細ページエラー隠蔽、バックエンドイベント書き込みのアトミック性、関連IDバリデーション、Proposalアクティビティルーティング、Claimイベントペイロード整合性、フロントエンドlint自動化に関する重大な問題は、現在のコードベースで修正済みです。

今回の更新では、確認された活発な高確信度のアプリケーション不具合はありません。

## 解決済み検出事項

| 状態 | 領域 | 現在の状況 |
| --- | --- | --- |
| 解決済み | フロントエンド認証 | ブラウザトリガーのミューテーションは `frontend/src/lib/actions.ts` のサーバーアクション経由で行われるようになり、クライアントコンポーネントが `CS_API_TOKEN` を直接読み取ることに依存しなくなった。 |
| 解決済み | フロントエンドエラー処理 | 詳細ページは実際の `404` APIレスポンスに対してのみ `notFound()` を呼び出し、他の障害は再スローするようになった。 |
| 解決済み | バックエンド一貫性 | サービスは同一のSQLAlchemyセッションおよびコミット境界内でイベントを追加してから書き込みを永続化するようになった。 |
| 解決済み | 関連IDバリデーション | Claim、Concept、Term、Evidence、Context、Connection、CIRの書き込みパスが、部分的な変更適用の代わりに欠落した関連IDを明示的に拒否するようになった。 |
| 解決済み | フロントエンドナビゲーション | ProposalおよびCross-fieldアクティビティリンクが `/review` や `/suggestions` など既存のフロントエンド遷移先を指すようになった。 |
| 解決済み | イベントペイロード整合性 | `ClaimCreated.context_names` がContext IDではなくリンクされた `Context.name` の値から取得されるようになった。 |
| 解決済み | フロントエンドlint自動化 | `npm run lint` は現在のフロントエンドセットアップで自動化に対応し、typecheck、テスト、ビルドと共に通過する。 |
| 解決済み | APIスキーマ型付け | Proposal詳細レスポンスが広い `object` フィールドを公開する代わりに、型付きの `ProposalRead` 契約を拡張するようになった。 |

## 残存する検出事項

### 1. Pytestが Python 3.14 非推奨警告を出力

**重大度**

低

**根拠**

- `backend` と `cli` の現在のローカル検証実行で、`pytest_asyncio` がPython 3.14における `asyncio.get_event_loop_policy()` と `asyncio.set_event_loop_policy()` に関する非推奨警告を出力。

**影響**

アプリケーションコード自体は通過しますが、警告ノイズにより検証出力が読みにくくなり、PythonがこれらのAPIを削除した際の将来の互換性作業が必要であることを示しています。

**推奨修正**

互換性のある `pytest-asyncio` パスが選択されたら非同期テストツールスタックをアップグレードまたは調整するか、非推奨のポリシー呼び出しを避けるインタープリター/ツールの組み合わせを固定する。

## 備考

- 本ファイルは修正前の状態ではなく、現在のコードと検証ベースラインを反映しています。
- 更新されたベースラインには、トランザクショナルイベント書き込み、厳密なリレーションシップバリデーション、型付きProposal詳細レスポンス、追加のロールバック回帰テストに関する最近のバックエンド修正が含まれます。

---

# Quality Audit

> **🇬🇧 English** | [日本語](#品質監査)

## Scope

This document records the current repository-wide quality audit state after the latest remediation pass. It reflects the present validated status of the prototype rather than the historical list of already-fixed defects.

Audit snapshot:

- Backend: `python -m ruff check .` and `python -m pytest tests` -> 102 tests passed
- CLI: `python -m pytest` -> 16 tests passed
- Frontend: `npm run lint`, `npm run typecheck`, `npm run test -- --run`, and `npm run build` passed

## Current Status

The previously reported critical issues around frontend authentication boundaries, detail-page error masking, backend event-write atomicity, related-ID validation, proposal activity routing, claim event payload integrity, and frontend lint automation have been remediated in the current codebase.

No active high-confidence application defects were confirmed during this refresh.

## Resolved Findings

| Status | Area | Current state |
| --- | --- | --- |
| Resolved | Frontend auth | Browser-triggered mutations now go through server actions in `frontend/src/lib/actions.ts`, so client components no longer depend on reading `CS_API_TOKEN` directly. |
| Resolved | Frontend error handling | Detail pages now call `notFound()` only for real `404` API responses and rethrow other failures. |
| Resolved | Backend consistency | Services now append events inside the same SQLAlchemy session and commit boundary before persisting writes. |
| Resolved | Related-ID validation | Claim, concept, term, evidence, context, connection, and CIR write paths now reject missing related IDs explicitly instead of partially applying changes. |
| Resolved | Frontend navigation | Proposal and cross-field activity links now point to existing frontend destinations such as `/review` and `/suggestions`. |
| Resolved | Event payload integrity | `ClaimCreated.context_names` is populated from linked `Context.name` values rather than context IDs. |
| Resolved | Frontend lint automation | `npm run lint` is automation-safe in the current frontend setup and passes alongside typecheck, tests, and build. |
| Resolved | API schema typing | Proposal detail responses now extend the typed `ProposalRead` contract instead of exposing broad `object` fields. |

## Remaining Findings

### 1. Pytest emits Python 3.14 deprecation warnings

**Severity**

Low

**Evidence**

- Current local validation runs for `backend` and `cli` emit `pytest_asyncio` deprecation warnings referencing `asyncio.get_event_loop_policy()` and `asyncio.set_event_loop_policy()` under Python 3.14.

**Why this matters**

The application code still passes, but warning noise makes validation output harder to read and signals future compatibility work once Python removes these APIs.

**Recommended fix**

Upgrade or adjust the async test tooling stack once a compatible `pytest-asyncio` path is selected, or pin an interpreter/tooling combination that avoids the deprecated policy calls.

## Notes

- This file reflects the current code and validation baseline, not the pre-remediation state captured by earlier audits.
- The refreshed baseline includes the recent backend fixes for transactional event writes, stricter relationship validation, typed proposal detail responses, and additional rollback regression tests.
