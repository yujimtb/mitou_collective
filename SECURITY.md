# セキュリティポリシー

> **🇯🇵 日本語** | [English](#security-policy)

## 報告方法

セキュリティ上の問題を発見した場合、エクスプロイトの詳細を含む公開Issueの作成は避けてください。

可能であれば、プライベートチャンネルを通じてメンテナーに直接ご連絡ください。プライベートチャンネルがまだ利用できない場合は、セキュリティ上の懸念を発見した旨のみを記載した最小限の公開Issueを作成し、プライベートな連絡手段を依頼してください。

## 対象範囲

本リポジトリは研究プロトタイプです。セキュリティ強化は完了しておらず、インターフェースは急速に変更される可能性があります。

特に注意が必要な領域：

- 認証とトークン処理
- 提案およびレビューの認可ルール
- API入力バリデーション
- シードおよびデモデータの実行パス

## 期待事項

- Issueに認証情報や機密データを公開しないでください
- 修正が利用可能になるまで概念実証のエクスプロイトコードを公開しないでください
- 報告時には再現手順、影響範囲、影響を受けるパスを含めてください

---

# Security Policy

> **🇬🇧 English** | [日本語](#セキュリティポリシー)

## Reporting

If you discover a security issue, please avoid opening a public issue with exploit details.

Instead, contact the maintainer directly through a private channel if one is available. If no private channel is available yet, open a minimal public issue that only states that you found a security concern and request a private contact path.

## Scope

This repository is a research prototype. Security hardening is not complete, and interfaces may change quickly.

Areas that deserve particular care include:

- authentication and token handling
- proposal and review authorization rules
- API input validation
- seed and demo-data execution paths

## Expectations

- do not publish credentials or sensitive data in issues
- do not publish proof-of-concept exploit code until a fix is available
- include reproduction steps, impact, and affected paths when reporting