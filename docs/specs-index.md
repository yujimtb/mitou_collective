# 仕様書インデックス

> **🇯🇵 日本語** | [English](#specification-index)

本リポジトリには、主要サブシステムの意図された動作を記述するOpenSpecドキュメントが含まれています。すべての仕様は実装およびテスト済みです。

## メイン仕様

| 仕様 | パス | 対象 |
|------|------|------|
| ナレッジグラフ | `openspec/specs/knowledge-graph/spec.md` | データモデル、エンティティ、関係 |
| イベントストア | `openspec/specs/event-store/spec.md` | 追記専用イベント、プロジェクション |
| 信頼モデル | `openspec/specs/trust-model/spec.md` | アクタータイプ、信頼レベル、権限 |
| 提案レビュー | `openspec/specs/proposal-review/spec.md` | Proposalステートマシン、レビューワークフロー |
| リンキングエージェント | `openspec/specs/linking-agent/spec.md` | AI分野横断リンク提案 |
| REST API | `openspec/specs/rest-api/spec.md` | HTTPエンドポイント、認証、ページネーション |
| CLI | `openspec/specs/cli/spec.md` | コマンドラインインターフェースコマンド |
| Web UI | `openspec/specs/web-ui/spec.md` | フロントエンドページとインタラクション |
| デモデータセット | `openspec/specs/demo-dataset/spec.md` | シードデータ（エントロピーテーマ） |

## 読み方

1. **knowledge-graph** でデータモデル（エンティティ、関係、制約）を確認
2. **trust-model** と **proposal-review** でガバナンス（誰が何をできるか、変更のレビュー方法）を確認
3. **rest-api**、**cli**、**web-ui** で3つのインターフェースレイヤーを確認
4. **linking-agent** でAI支援の分野横断発見パイプラインを確認
5. **event-store** で履歴とイベントソーシングアーキテクチャを確認
6. **demo-dataset** でシード済み評価コーパスを確認

## 変更ディレクトリ

アクティブおよびアーカイブ済みの変更は `openspec/changes/` に格納されています。各変更はOpenSpecアーティファクトワークフロー（proposal → delta specs → design → tasks）に従います。

---

# Specification Index

> **🇬🇧 English** | [日本語](#仕様書インデックス)

This repository includes OpenSpec documents describing the intended behavior of major subsystems. All specifications are implemented and tested.

## Main Specifications

| Spec | Path | Covers |
|------|------|--------|
| Knowledge Graph | `openspec/specs/knowledge-graph/spec.md` | Data model, entities, relationships |
| Event Store | `openspec/specs/event-store/spec.md` | Append-only events, projections |
| Trust Model | `openspec/specs/trust-model/spec.md` | Actor types, trust levels, permissions |
| Proposal Review | `openspec/specs/proposal-review/spec.md` | Proposal state machine, review workflow |
| Linking Agent | `openspec/specs/linking-agent/spec.md` | AI cross-field link suggestions |
| REST API | `openspec/specs/rest-api/spec.md` | HTTP endpoints, auth, pagination |
| CLI | `openspec/specs/cli/spec.md` | Command-line interface commands |
| Web UI | `openspec/specs/web-ui/spec.md` | Frontend pages and interactions |
| Demo Dataset | `openspec/specs/demo-dataset/spec.md` | Seed data (entropy theme) |

## How to Read Them

1. Start with **knowledge-graph** for the data model (entities, relationships, constraints)
2. Read **trust-model** and **proposal-review** for governance (who can do what, how changes are reviewed)
3. Read **rest-api**, **cli**, and **web-ui** for the three interface layers
4. Read **linking-agent** for the AI-assisted cross-field discovery pipeline
5. Read **event-store** for the history and event sourcing architecture
6. Read **demo-dataset** for the seeded evaluation corpus

## Changes Directory

Active and archived changes live under `openspec/changes/`. Each change follows the OpenSpec artifact workflow: proposal → delta specs → design → tasks.