## Context

CollectiveScienceプロトタイプは`mvp-completion`チェンジでLLMクライアント統合とエンティティ作成フォームを完了し、バックエンドテスト69パス・フロントエンドビルド成功の状態にある。

しかしMVPデモの完成には12個のギャップが残っている:

1. **ContextフィルタバグCRITICAL** — フロントエンドがContext IDを送信するが、`claim_service.py`(L82-83)が`Context.name`で照合するためフィルタ結果が常に空
2. **Claim変更履歴が空白** — バックエンドが生イベント(`event_type`, `payload`, `actor_id`)を返すが、フロントエンドは`title`, `summary`, `actor_name`, `timestamp`を期待
3. **Term画面が未実装** — `frontend/src/app/terms/`が存在しない（バックエンドAPIは実装済み）
4. **Evidence画面が未実装** — `frontend/src/app/evidence/`が存在しない（`EvidenceCard.tsx`コンポーネントのみ）
5. **AI候補専用画面が未実装** — 候補はClaim詳細にのみ埋め込み。設計書は`/suggestions`ページを要求
6. **グラフビューが静的カード** — `ForceGraph.tsx`(56行)はCSS gridの`<article>`カード。SVG/Canvas/力指向グラフなし
7. **ダッシュボードの最新アクティビティが空** — `api.ts`(L215)が`recentActivity: []`を返す
8. **DELETEエンドポイントなし** — 全APIファイルに`@router.delete`がゼロ。`ClaimRetracted`イベントは存在するがAPIなし
9. **CLIコマンド不足** — `cs context`, `cs term`, `cs evidence`コマンドなし。`cs concept create`もなし
10. **Docker Compose不完全** — マイグレーションステップなし、シードステップなし、フロントエンドDockerfileにlock fileコピーなし
11. **E2E/フロントエンドテストゼロ** — バックエンド69テストあるが統合/E2Eテストなし、フロントエンドテストゼロ
12. **ProjectionEngine未使用** — 294行の実装があるがどのサービス・APIからもインポートされていない

並行開発ガイド（`parallel_dev_guide.md`）に従い、Agent 2（ビジネスロジック）、Agent 3（REST API）、Agent 5（Frontend）、Agent 6（CLI）が並行して作業可能な設計にする。

## Goals / Non-Goals

**Goals:**
- ContextフィルタのUUID/名前照合バグを修正し、フロントエンドからのフィルタリングを正常動作させる
- Claim変更履歴を人間可読な整形済み形式でフロントエンドに提供する
- Term一覧・詳細・作成画面を実装する
- Evidence一覧・詳細・作成画面を実装する
- AI候補専用一覧画面（`/suggestions`）を実装する
- グラフビューを力指向グラフ（force-directed graph）に置き換え、インタラクティブ操作を可能にする
- ダッシュボードに最新アクティビティを表示する
- Claimの撤回（論理削除）APIを追加する
- CLIにContext, Term, Evidence, Concept createコマンドを追加する
- Docker Composeを本番起動可能な状態にする
- 最低限のフロントエンドテスト・E2Eテストを追加する
- ProjectionEngineのMVP位置づけを明文化する

**Non-Goals:**
- ProjectionEngineのCQRS統合（MVP後に延期）
- 物理削除の実装（ソフトデリートのみ）
- フルCoverage（>90%）のテスト達成（最低限のスモークテストのみ）
- WebSocket/リアルタイム通知の実装
- 認証フロー（ログイン画面等）の追加
- 本番環境デプロイ設定（CDN, SSL等）

## Decisions

### Decision 1: ContextフィルタのUUID/名前判定戦略

**選択: バックエンド側でUUID形式判定し、UUID→ID照合、非UUID→名前照合にフォールバック**

```python
# claim_service.py
import uuid

if context_param := filters.get("context"):
    try:
        context_uuid = uuid.UUID(context_param)
        statement = statement.join(Claim.context_links).join(
            ClaimContext.context
        ).where(Context.id == context_uuid)
    except ValueError:
        statement = statement.join(Claim.context_links).join(
            ClaimContext.context
        ).where(Context.name == context_param)
```

**理由:**
- フロントエンドは既にContext IDをUUID形式で送信しており、バックエンド側の1箇所変更で修正完了
- 名前によるフィルタリングを後方互換として維持（CLIやテストで名前指定する可能性）
- フロントエンド側の変更不要

**代替案（不採用）:**
- フロントエンド側でContext名を送信するよう変更 → 名前は一意性が保証されておらず、ID照合が正しい設計
- 専用の`context_id`クエリパラメータを追加 → API破壊的変更となり、影響範囲が広い

### Decision 2: Claim変更履歴のバックエンド側整形

**選択: バックエンド（サービス層）で履歴イベントを整形済みオブジェクトに変換**

```python
# claim_service.py に history_formatted() メソッドを追加
def history_formatted(self, claim_id: UUID) -> list[dict]:
    events = self._event_store.query(aggregate_id=claim_id)
    return [
        {
            "title": EVENT_TYPE_LABELS.get(e.event_type, e.event_type),
            "summary": self._summarize_event(e),
            "actor_name": self._resolve_actor_name(e.actor_id),
            "timestamp": e.created_at.isoformat(),
            "event_type": e.event_type,
        }
        for e in events
    ]
```

**理由:**
- Actor名の解決にはDBアクセスが必要で、クライアント側で行うとN+1問題が発生
- イベント種別→人間可読タイトルのマッピングはドメイン知識であり、サービス層に属する
- フロントエンドの実装をシンプルに保てる（受け取ったデータをそのまま表示）

**代替案（不採用）:**
- フロントエンド側で変換 → actor_id→名前の解決に追加APIコールが必要、複雑化
- 専用のProjection → MVP後のCQRS統合で検討（Decision 7参照）

### Decision 3: グラフライブラリの選定

**選択: `react-force-graph-2d`（D3 forceのReactラッパー）**

**理由:**
- React/Next.jsとの統合が容易（`<ForceGraph2D>`コンポーネントとして使用）
- D3 force-simulationのフルパワーを活用しつつ、Canvas描画で大量ノードにも対応
- APIが直感的: `graphData={{ nodes, links }}` + コールバック（`onNodeClick`, `onNodeDrag`）
- 既存の`GraphData`型（`nodes: GraphNode[]`, `edges: GraphEdge[]`）と直接マッピング可能
- SSR非対応のためdynamic importが必要だが、グラフページは元からクライアントコンポーネント

**代替案（不採用）:**
- 生D3.js → Reactとの統合が複雑（DOM操作の二重管理）、実装コスト高
- Cytoscape.js → 豊富だがバンドルサイズが大きい（~400KB min）、Reactラッパーの品質が不安定
- Sigma.js → WebGL描画で高性能だが、学習コストが高くMVPには過剰

### Decision 4: Claim撤回のソフトデリート実装

**選択: `trust_status = "retracted"` への遷移 + `ClaimRetracted`イベント記録**

```python
# claim_service.py
def retract(self, claim_id: UUID, actor_id: UUID) -> ClaimRead:
    with self._session_factory() as session:
        claim = session.get(Claim, claim_id)
        if claim.trust_status == "retracted":
            raise ConflictError("Claim already retracted")
        claim.trust_status = "retracted"
        self._event_store.append(ClaimRetracted(...))
        session.commit()
        return self._to_schema(claim)
```

**理由:**
- Event Sourcing設計と一貫性がある（状態変更をイベントとして記録）
- `ClaimRetracted`イベント型が既に`projections.py`で定義済み
- 物理削除は参照整合性の問題を引き起こす（Evidence, Proposal, Connection等が参照）
- 撤回後もデータは残るため、グラフビューで「撤回済み」として表示可能

**代替案（不採用）:**
- 物理DELETE → 外部キー制約違反、イベント履歴の欠損
- `is_deleted`フラグ → 既に`trust_status`という状態フィールドがあるため、二重管理は不要

### Decision 5: 最新アクティビティAPIの実装戦略

**選択: Event Storeから直近Nイベントを直接クエリし、サーバー側で整形**

```python
# event_service に recent_events() を追加
def recent_events(self, limit: int = 10) -> list[dict]:
    events = self._event_store.query_recent(limit=limit)
    return [self._format_activity(e) for e in events]
```

**理由:**
- Event Storeに全操作が記録されているため、追加のテーブルやビューが不要
- サーバー側整形により、Actor名解決やhref生成をバックエンドで完結
- `limit`パラメータにより取得量を制御し、パフォーマンスを確保
- フロントエンドの`recentActivity: []`をAPIコールに置き換えるだけで完了

**代替案（不採用）:**
- 専用の`Activity`テーブル → スキーマ追加・マイグレーション必要、MVP過剰
- ProjectionEngine経由 → Decision 7でMVP延期を決定済み

### Decision 6: CLIコマンドのアーキテクチャ

**選択: 既存パターン踏襲 — Typerサブアプリ + httpx経由でREST APIを呼び出し**

```python
# cli/commands/context.py (新設)
import typer
app = typer.Typer()

@app.command("list")
def list_contexts(field: str = None, json_output: bool = False):
    response = client.get("/api/v1/contexts", params={"field": field})
    ...
```

**理由:**
- 既存の`claim.py`, `concept.py`コマンドと同一パターンで一貫性を維持
- REST API経由のため、CLI固有のビジネスロジックは不要
- テストもAPI呼び出しのモックで完結

### Decision 7: ProjectionEngineのMVP位置づけ

**選択: コードとテストを保持し、MVP後のCQRS統合向けとして明文化。読み取りAPIは直接SQLクエリを継続**

**理由:**
- 294行の実装と対応テストが既に存在し、削除するのはもったいない
- 現時点ではProjectionEngineを経由する読み取りパスがなく、導入するとテスト・デバッグの複雑さが増す
- MVP後にCQRS（Command Query Responsibility Segregation）パターンの導入を検討する際に即活用可能
- ドキュメントコメントの追記のみで対応でき、コード変更は最小限

### Decision 8: フロントエンドテストのツール選定

**選択: Vitest + @testing-library/react**

**理由:**
- VitestはViteベースで、Next.js 15との親和性が高い（SWCトランスフォーム対応）
- @testing-library/reactはユーザー視点のテスト（「ボタンが表示される」「クリックで呼ばれる」）に最適
- Jestより起動が速く、ESM対応も良好
- ForceGraph, FilterBar, ClaimDetailなどの主要コンポーネントのスモークテストに十分

**代替案（不採用）:**
- Jest → 設定が複雑（特にNext.js 15のESMモジュール対応）、起動が遅い
- Playwright/Cypress（E2E） → 重要だがMVP初期リリースにはセットアップコストが高い。将来追加を推奨

### Decision 9: Docker Composeのエントリーポイント戦略

**選択: `backend/entrypoint.sh`を新設し、マイグレーション→条件付きシード→uvicorn起動の3ステップ**

```bash
#!/bin/bash
set -e
alembic upgrade head
if [ "$SEED_ON_STARTUP" = "true" ]; then
    python -m backend.app.seeds.entropy_dataset
fi
exec uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
```

**理由:**
- コンテナ起動時にDBスキーマが自動的に最新化され、手動マイグレーション忘れを防止
- `SEED_ON_STARTUP`環境変数によりデモ環境でのみシードを実行（本番では無効）
- `exec`によりuvicornがPID 1となり、シグナルハンドリングが正しく機能

**代替案（不採用）:**
- docker-compose の`command`で`&&`チェイン → 可読性が低い、エラーハンドリングが困難
- Init Container（K8s風） → Docker Composeでは公式サポートなし、`depends_on`のconditionで近似可能だが複雑

## Risks / Trade-offs

- **[react-force-graph-2dのSSR非対応]** → `next/dynamic`の`ssr: false`でdynamic importする。グラフページ全体がクライアントレンダリングになるが、初期表示はローディングスピナーで対応
- **[イベント種別→人間可読タイトルのマッピング保守]** → 新しいイベント型追加時に`EVENT_TYPE_LABELS`辞書の更新を忘れる可能性。unknown event typeにはevent_typeそのものをフォールバック表示
- **[CLIコマンド数の増加]** → Context, Term, Evidenceの3コマンド追加でCLI全体のテスト量が増加。既存パターンの踏襲で実装コストを最小化
- **[Docker entrypoint.shのマイグレーション失敗]** → `set -e`により即座にコンテナが停止。docker-compose logs で原因確認可能。ヘルスチェック設定の追加を推奨
- **[E2Eテストの範囲限定]** → MVP完了のためスモークテストレベルに留める。カバレッジ不足は許容し、MVP後に拡充
- **[並行開発の競合]** → Agent 2(Services) と Agent 3(API) は `△（注意が必要）`の関係。Agent 2がサービスメソッド追加→Agent 3がエンドポイント追加の順序を推奨。Agent 5, 6は完全並行可能

## Open Questions

- `react-force-graph-2d`のバンドルサイズが許容範囲か → 約50KB (gzipped)、MVPでは許容
- Claim撤回後のグラフ表示ポリシー → 薄色表示 or 非表示。MVPではフィルタで非表示（`trust_status != retracted`）とし、詳細は運用で判断
