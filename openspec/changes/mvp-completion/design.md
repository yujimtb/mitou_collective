## Context

CollectiveScienceプロトタイプは全レイヤー（Models, Events, Auth, Services, Workflows, Agent, API, CLI, Web UI, Seeds）が実装済みで、バックエンドテスト61/61パス、フロントエンドビルド成功の状態にある。

しかしMVPデモ完成には2つのギャップが残る:

1. **AI Linking Agentの`_noop_llm`問題** — `main.py`の`_wire_services`内で`CandidateGenerator`に空辞書を返すno-opが渡されており、実際のLLMによる接続候補生成が動作しない。`LLMCallable = Callable[[str], Awaitable[LLMResponse]]`のインターフェースは定義済みで、`prompts.py`がJSON形式のプロンプトを構築し、`CandidateGenerator`がリトライ付きで呼び出す構造は整っているが、実HTTPクライアントが存在しない。

2. **Web UIの読み取り専用問題** — 11ページ・15コンポーネントが実装済みだが、すべて閲覧・レビュー用。Claim/Concept/Context/Evidenceの作成フォーム、AI候補の手動トリガーUIが未実装。APIクライアント(`lib/api.ts`)にもPOST系の作成関数がない。

並行開発ガイド（`parallel_dev_guide.md`）に従い、Agent 4（AI Linking Agent）とAgent 5（Frontend）が並行して作業可能な設計にする。

## Goals / Non-Goals

**Goals:**
- 実LLM（OpenAI GPT-4o / Anthropic Claude）に接続し、設計書どおりの接続候補生成を動作させる
- Web UIからClaim・Concept・Context・Evidenceの作成が可能になる
- Web UIからAI接続候補の手動トリガーが可能になる
- Approve/Reject後のUI反映を改善する
- 2エージェントが並行開発できるタスク分割を実現する

**Non-Goals:**
- 自動トリガー（新規Claim作成時の自動候補生成）の実装（手動トリガーのみ）
- ベクトル埋め込みによる意味的類似性検索（既存のtoken-based searchを維持）
- ストリーミングレスポンス対応
- 認証UIの実装（既存のトークンベース認証を維持）
- 本番環境デプロイ設定

## Decisions

### Decision 1: LLMクライアントのアダプターパターン

**選択: Protocol + 個別アダプター実装**

```
LLMClient (Protocol)
├── OpenAIAdapter     → openai.AsyncOpenAI
└── AnthropicAdapter  → anthropic.AsyncAnthropic
```

`backend/app/agent/llm_client.py`に統一プロトコルと2つのアダプターを配置する。

**理由:**
- 既存の`LLMCallable = Callable[[str], Awaitable[LLMResponse]]`シグネチャと互換性を保つ
- `CandidateGenerator`の変更を最小限に抑える（`llm_client`引数にアダプターの`.generate()`メソッドを渡すだけ）
- テスト時にモックと差し替えが容易

**代替案（不採用）:**
- LangChain/LiteLLM経由 → 依存が重い、学習コスト、MVP過剰
- 直接httpx呼び出し → SDK更新追従が手間

### Decision 2: プロンプトのsystem/user構造化

**選択: 既存JSON propmtをuser messageとして維持し、system messageを前段で追加**

```python
# llm_client.py内
SYSTEM_PROMPT = """あなたは学際的知識の専門家です。...（ロール定義・出力フォーマット指示）"""

# adapter.generate() 内でsystem + user messageに構成
messages = [
    {"role": "system", "content": SYSTEM_PROMPT},
    {"role": "user", "content": existing_json_prompt}
]
```

**理由:**
- `prompts.py`の既存コードを変更せずに済む（JSONプロンプト構築はそのまま）
- system messageでロール・出力形式を統一的に指示
- `CandidateGenerator._invoke_with_retries`が受け取るprompt文字列はuser message部分のみで、system promptはアダプター側で付加

### Decision 3: LLM設定の環境変数管理

**選択: `backend/app/agent/config.py`にLLM設定dataclassを追加**

```python
@dataclass
class LLMConfig:
    provider: str = "openai"          # "openai" | "anthropic"  
    model: str | None = None          # None → provider default
    api_key: str = ""                 # 必須for production
    temperature: float = 0.3
    max_tokens: int = 4096
    timeout_seconds: float = 60.0
```

環境変数: `LLM_PROVIDER`, `LLM_MODEL`, `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `LLM_TEMPERATURE`

**理由:**
- 既存の`LinkingAgentConfig`と同じファイルに配置し一貫性を保つ
- `_wire_services`内でconfigを読んでアダプターを注入する、変更箇所が最小

### Decision 4: main.pyの`_noop_llm`置換

**選択: `_wire_services`内で条件分岐し、APIキーがあれば実LLM、なければno-opを維持**

```python
def _wire_services(session_factory):
    ...
    llm_config = LLMConfig.from_env()
    if llm_config.api_key:
        llm_adapter = create_llm_client(llm_config)
        candidate_generator = CandidateGenerator(llm_client=llm_adapter.generate)
    else:
        candidate_generator = CandidateGenerator(llm_client=_noop_llm)
    ...
```

**理由:**
- APIキー未設定でもアプリが起動する（テスト・開発時の利便性）
- APIキー設定時は自動的に実LLMに切り替わる
- Agent APIでLLM未設定時は503を返す（フロントエンドに明確なフィードバック）

### Decision 5: フロントエンドフォームのアーキテクチャ

**選択: モーダルダイアログ + `useRouter().refresh()` による再読み込み**

```
CreateClaimDialog    → POST /api/v1/claims    → router.refresh()
CreateConceptDialog  → POST /api/v1/concepts  → router.refresh()
CreateContextDialog  → POST /api/v1/contexts  → router.refresh()
CreateEvidenceDialog → POST /api/v1/evidence  → router.refresh()
```

各フォームは独立したClient Componentとし、既存のリスト表示ページに「新規作成」ボタンを追加する。

**理由:**
- 既存ページのSSR構造を変更せずにClient Component（'use client'）をインクリメンタルに追加できる
- モーダル方式により画面遷移が不要で、作成→一覧復帰がスムーズ
- `router.refresh()`でReact Server Componentの再レンダリングをトリガーし、データの再取得が自然

**代替案（不採用）:**
- 専用の作成ページ → 画面数が増えすぎ、MVPには過剰
- React Hook Form + Zod → 良い選択肢だが、4フォーム程度ならネイティブform + 手動バリデーションで十分

### Decision 6: API POSTリクエスト用のクライアント関数

**選択: `lib/api.ts`に `apiMutate<T>` ヘルパーとPOST関数群を追加**

```typescript
async function apiMutate<T>(path: string, body: unknown): Promise<T> {
  // no cache, no revalidate for mutations
  return api<T>(path, { method: "POST", body: JSON.stringify(body), cache: "no-store" });
}

export async function createClaim(data: ClaimCreateInput): Promise<ClaimRead> { ... }
export async function createConcept(data: ConceptCreateInput): Promise<ConceptRead> { ... }
export async function triggerAgentSuggestions(claimId: string): Promise<{ job_id: string }> { ... }
```

### Decision 7: トースト通知

**選択: シンプルな自前Toast Component**

レビュー成功/失敗のフィードバックに使用。React portalで画面右上に表示、3秒後に自動消去。

**理由:**
- 外部ライブラリ（react-hot-toast等）の追加依存を回避
- MVPに必要な機能は成功/エラーの2種のみ

## Risks / Trade-offs

- **[LLM APIコスト]** → GPT-4oの利用でデモ時にコストが発生する。`temperature=0.3`, `max_tokens=4096`でコスト抑制。デモ回数の目安を事前に見積もる
- **[LLMレスポンスのJSON解析失敗]** → LLMが指定フォーマットと異なるJSONを返す可能性。既存の`CandidateGenerator._parse_candidates`がrobustに実装済み（パース失敗時は空リスト返却）。system promptでフォーマットを強調
- **[APIキー漏洩]** → 環境変数管理のみで、フロントエンドに露出しない設計。`.env`ファイルを`.gitignore`に追加
- **[フォームバリデーション不足]** → クライアント側の基本チェック（必須フィールド）+ サーバー側の422エラー表示。MVP後に型安全バリデーション（Zod等）を検討
- **[並行開発の競合]** → Agent 4はbackendのみ、Agent 5はfrontendのみに閉じるため、ファイル競合は発生しない。`lib/api.ts`へのフロントエンド側POST関数追加はAgent 5が担当

## Open Questions

- Anthropic APIの利用がデモ予算内に収まるか → OpenAIデフォルトで進め、切り替えは設定変更のみで対応
