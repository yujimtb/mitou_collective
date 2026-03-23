# コントリビューティング

> **🇯🇵 日本語** | [English](#contributing)

ご関心をお寄せいただきありがとうございます。

## 対象範囲

本リポジトリは研究プロトタイプです。コントリビューションは歓迎しますが、変更は現在のアーキテクチャ方針と仕様書に沿ったものである必要があります。

## プルリクエストの前に

以下をお願いいたします：

1. 大きな変更の場合は、事前にIssueまたはDiscussionを開いてください
2. 変更はレビューしやすいよう、焦点を絞ってください
3. 動作が変わる場合はテストを追加・更新してください
4. セットアップや動作が変わる場合はドキュメントを更新してください

## 開発ワークフロー

### バックエンド

```bash
cd backend
pip install -e .[dev]
python manage.py seed          # デモデータの投入
python manage.py create-admin  # 管理者 + JWTトークンの作成
python manage.py serve         # 開発サーバー起動（ポート8000）
python -m pytest tests         # 61テスト実行
```

### フロントエンド

```bash
cd frontend
npm install
CS_API_TOKEN="<token>" npm run dev   # 開発サーバー起動（ポート3000）
npm run build                        # 型チェック + ビルド
```

### CLI

```bash
cd cli
pip install -e .[dev]
python -m pytest tests
```

### Docker Compose（フルスタック）

```bash
docker compose up --build
```

## マルチエージェント開発

本プロジェクトは複数のコーディングエージェントによる並行開発をサポートしています。トラック割り当ては [parallel_dev_guide.md](../parallel_dev_guide.md)、衝突マップは [docs/agent-assignments.md](docs/agent-assignments.md) を参照してください。

## スタイルの方針

- 小さく、レビューしやすい変更を推奨
- 既存の命名規則と構造をできるだけ維持
- フィーチャーやフィックスのブランチでは無関係なリファクタリングを避ける
- ドキュメントと仕様書を実装と一致した状態に保つ

## 仕様書

主要な動作は `openspec/specs/` に記述されています。変更がシステムの動作やパブリックインターフェースに影響する場合は、関連する仕様書を更新するか、仕様書の変更が不要な理由を説明してください。

---

# Contributing

> **🇬🇧 English** | [日本語](#コントリビューティング)

Thank you for your interest in contributing.

## Scope

This repository is a research prototype. Contributions are welcome, but changes should remain aligned with the current architectural direction and specification documents.

## Before Opening a Pull Request

Please:

1. open an issue or discussion if the change is large
2. keep changes focused and easy to review
3. add or update tests when behavior changes
4. update public documentation when setup or behavior changes

## Development Workflow

### Backend

```bash
cd backend
pip install -e .[dev]
python manage.py seed          # seed demo data
python manage.py create-admin  # create admin + JWT token
python manage.py serve         # start dev server (port 8000)
python -m pytest tests         # run 61 tests
```

### Frontend

```bash
cd frontend
npm install
CS_API_TOKEN="<token>" npm run dev   # start dev server (port 3000)
npm run build                        # type-check + build
```

### CLI

```bash
cd cli
pip install -e .[dev]
python -m pytest tests
```

### Docker Compose (full stack)

```bash
docker compose up --build
```

## Multi-Agent Development

This project supports parallel development by multiple coding agents. See [parallel_dev_guide.md](../parallel_dev_guide.md) for track assignments and [docs/agent-assignments.md](docs/agent-assignments.md) for the collision map.

## Style Expectations

- prefer small, reviewable changes
- preserve existing naming and structure where practical
- avoid unrelated refactors in feature or fix branches
- keep docs and specs consistent with implementation

## Specifications

Major behavior is described in `openspec/specs/`. If a change affects system behavior or public interfaces, update the relevant spec or explain why the spec does not need to change.