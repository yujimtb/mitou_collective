# デモデータセット

> **🇯🇵 日本語** | [English](#demo-dataset)

リポジトリには、エントロピーと複数分野にまたがる関連概念を中心としたシードデモデータセットが含まれています。

## 目的

このデータセットは、ユーザーがゼロからグラフを構築することなく、プラットフォームの価値を理解できるようにするものです。熱力学的エントロピー、統計的エントロピー、シャノンエントロピー、量子エントロピー、コルモゴロフ複雑性の間の分野横断的接続を実演します。

## 対象分野

| Context | 分野 | トピック |
|---------|------|---------|
| 古典熱力学 | 物理学 | 巨視的エントロピー、熱、仕事 |
| 統計力学 | 物理学 | ボルツマンエントロピー、ミクロ状態、分配関数 |
| シャノン情報理論 | 情報理論 | 情報エントロピー、通信路容量 |
| 量子情報理論 | 情報理論 | フォン・ノイマンエントロピー、量子もつれ |
| アルゴリズム情報理論 | 計算機科学 | コルモゴロフ複雑性、非圧縮性 |
| 分野横断 | cross_field | エントロピー概念の比較 |

## 含まれるデータ

| エンティティ | 件数 |
|-------------|------|
| Context | 6 |
| Term | 9 |
| Concept | 7 |
| Claim | 120 |
| Evidence | 33 |
| 分野横断接続 | 4 |
| CIR例 | 3 |

## Seedコマンド

```bash
cd backend
python manage.py seed
```

管理者ユーザーとJWTトークンも作成するには：

```bash
python manage.py create-admin
```

## データファイル

JSONソースファイルは `backend/app/seeds/data/` に格納：

```
contexts.json       # 6 Context（分野と前提条件付き）
terms.json          # 9 Term（英語/日本語ラベル付き）
concepts.json       # 7 Concept（Termにマッピング）
claims.json         # 24 base + 96 generated = 120 Claim
evidence.json       # 8 base + 25 generated = 33 Evidenceレコード
connections.json    # 4 分野横断接続
cir.json            # 3 CIR形式表現
```

## 設計上の注意

- Seedスクリプトは冪等 — 複数回実行しても重複データは作成されない
- エンティティ関係（Claim↔Context、Claim↔Concept、Claim↔Evidence）は明示的に再構築される
- データはデモとプロトタイプ評価用に設計されており、本番用知識ベースとしてではない

---

# Demo Dataset

> **🇬🇧 English** | [日本語](#デモデータセット)

The repository contains a seeded demo dataset centered on entropy and related concepts across multiple disciplines.

## Purpose

The dataset makes the value of the platform understandable without requiring users to build the graph from scratch. It demonstrates cross-field connections between thermodynamic entropy, statistical entropy, Shannon entropy, quantum entropy, and Kolmogorov complexity.

## Covered Fields

| Context | Field | Topic |
|---------|-------|-------|
| Classical Thermodynamics | physics | Macroscopic entropy, heat, work |
| Statistical Mechanics | physics | Boltzmann entropy, microstates, partition functions |
| Shannon Information Theory | information_theory | Information entropy, channel capacity |
| Quantum Information Theory | information_theory | Von Neumann entropy, entanglement |
| Algorithmic Information Theory | computer_science | Kolmogorov complexity, incompressibility |
| Cross-field | cross_field | Comparative entropy concepts |

## Included Data

| Entity | Count |
|--------|-------|
| Contexts | 6 |
| Terms | 9 |
| Concepts | 7 |
| Claims | 120 |
| Evidence | 33 |
| Cross-field Connections | 4 |
| CIR examples | 3 |

## Seed Command

```bash
cd backend
python manage.py seed
```

To also create an admin user with a JWT token:

```bash
python manage.py create-admin
```

## Data Files

JSON source files live under `backend/app/seeds/data/`:

```
contexts.json       # 6 contexts with fields and assumptions
terms.json          # 9 terms with English/Japanese labels
concepts.json       # 7 concepts mapped to terms
claims.json         # 24 base + 96 generated = 120 claims
evidence.json       # 8 base + 25 generated = 33 evidence records
connections.json    # 4 cross-field connections
cir.json            # 3 CIR formal representations
```

## Design Notes

- The seed script is idempotent — running it multiple times does not create duplicates
- Entity relationships (Claim↔Context, Claim↔Concept, Claim↔Evidence) are reconstructed explicitly
- The data is designed for demos and prototype evaluation, not as a production knowledge base