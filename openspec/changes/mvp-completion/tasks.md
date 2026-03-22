## 1. Agent 4: LLMクライアント基盤（Backend — AI Linking Agent）

- [x] 1.1 `backend/app/agent/llm_client.py`を新設し、`LLMClient` Protocol、`LLMResponse` dataclass（content, model, usage）、`TokenUsage` dataclass（prompt_tokens, completion_tokens）を定義する
- [x] 1.2 `backend/app/agent/llm_client.py`に`SYSTEM_PROMPT`定数を追加する。ロール定義（学際的知識の専門家）、出力フォーマット指示（JSONのみ）、接続種別定義（equivalent / analogous / generalizes / contradicts / complements）を含める
- [x] 1.3 `backend/app/agent/llm_client.py`に`OpenAIAdapter`クラスを実装する。`openai.AsyncOpenAI`を使い、system message + user messageの構成で`chat.completions.create`を呼び出し、レスポンスを`LLMResponse`に変換する。タイムアウト設定、レスポンスのcontent抽出を含める
- [x] 1.4 `backend/app/agent/llm_client.py`に`AnthropicAdapter`クラスを実装する。`anthropic.AsyncAnthropic`を使い、system prompt + user messageの構成で`messages.create`を呼び出し、レスポンスを`LLMResponse`に変換する
- [x] 1.5 `backend/app/agent/llm_client.py`に`create_llm_client(config: LLMConfig) -> LLMClient`ファクトリ関数を実装する。providerに応じて適切なアダプターを返す

## 2. Agent 4: LLM設定と依存注入（Backend — AI Linking Agent）

- [x] 2.1 `backend/app/agent/config.py`に`LLMConfig` dataclassを追加する。provider、model、api_key、temperature（default 0.3）、max_tokens（default 4096）、timeout_seconds（default 60.0）フィールドと、`from_env()`クラスメソッドで環境変数読み込みを実装する
- [x] 2.2 `backend/app/main.py`の`_wire_services`関数を修正する。`LLMConfig.from_env()`でconfigを読み込み、`api_key`があれば`create_llm_client`で実アダプターを生成、なければ既存の`_noop_llm`を維持する。生成した`llm_client`のgenerateメソッドを`CandidateGenerator`に渡す
- [x] 2.3 `backend/app/main.py`の`_wire_services`戻り値に`llm_config`を追加し、`app.state.llm_config`としてセットする（Agent APIで503判定に使用）
- [x] 2.4 `backend/app/api/agent.py`のsuggest-connectionsエンドポイントに、`app.state.llm_config`のapi_keyが空の場合に503 Service Unavailableを返すガードを追加する

## 3. Agent 4: LLMクライアントのテスト（Backend — AI Linking Agent）

- [x] 3.1 `backend/tests/test_agent/test_llm_client.py`を新設し、`OpenAIAdapter`のユニットテストを実装する。`openai.AsyncOpenAI`をモックし、正常レスポンス・タイムアウト・401エラーのケースをテストする
- [x] 3.2 `backend/tests/test_agent/test_llm_client.py`に`AnthropicAdapter`のユニットテストを追加する
- [x] 3.3 `backend/tests/test_agent/test_llm_client.py`に`create_llm_client`ファクトリのテスト（OpenAI/Anthropic選択、不正provider時のエラー）を追加する
- [x] 3.4 `backend/tests/test_agent/test_llm_client.py`に`LLMConfig.from_env()`のテスト（環境変数設定、未設定、デフォルト値）を追加する
- [x] 3.5 `backend/pyproject.toml`の依存に`openai`と`anthropic`パッケージを追加する

## 4. Agent 5: APIクライアント拡張（Frontend — Web UI）

- [x] 4.1 `frontend/src/lib/types.ts`にフォーム入力用の型（`ClaimCreateInput`, `ConceptCreateInput`, `ContextCreateInput`, `EvidenceCreateInput`）を追加する
- [x] 4.2 `frontend/src/lib/api.ts`に`apiMutate<T>`ヘルパー関数を追加し、POSTリクエストを`no-store`で送信する
- [x] 4.3 `frontend/src/lib/api.ts`にCRUD用POST関数群を追加する: `createClaim`, `createConcept`, `createContext`, `createEvidence`
- [x] 4.4 `frontend/src/lib/api.ts`に`triggerAgentSuggestions(entityType: string, entityId: string)`関数を追加する（`POST /api/v1/agent/suggest-connections`を呼び出す）
- [x] 4.5 `frontend/src/lib/api.ts`にリファレンスデータ取得関数`getReferenceData()`を追加する（Context・Concept・Term一覧を並列取得）

## 5. Agent 5: エンティティ作成フォーム（Frontend — Web UI）

- [x] 5.1 `frontend/src/components/CreateClaimDialog.tsx`を新設する。モーダルダイアログ形式で、statement（テキストエリア）、claim_type（セレクト）、Context選択（マルチセレクト）、Concept選択（マルチセレクト）のフォームを実装する。送信時に`createClaim`を呼び出し、成功時に`router.refresh()`する
- [x] 5.2 `frontend/src/components/CreateConceptDialog.tsx`を新設する。label、description、field、Term選択のフォームを実装する
- [x] 5.3 `frontend/src/components/CreateContextDialog.tsx`を新設する。name、description、field、assumptions（カンマ区切りテキスト→配列変換）、parent_context選択のフォームを実装する
- [x] 5.4 `frontend/src/components/CreateEvidenceDialog.tsx`を新設する。title、evidence_type（セレクト）、source、excerpt、reliability（セレクト）、Claim紐付け（マルチセレクト）のフォームを実装する
- [x] 5.5 `frontend/src/components/Toast.tsx`を新設する。成功（緑）・エラー（赤）の2種を画面右上にReact portalで表示し、3秒後に自動消去する

## 6. Agent 5: 既存ページへのフォーム統合（Frontend — Web UI）

- [x] 6.1 `frontend/src/app/claims/page.tsx`に「新規Claim作成」ボタンと`CreateClaimDialog`を統合する
- [x] 6.2 `frontend/src/app/concepts/page.tsx`に「新規Concept作成」ボタンと`CreateConceptDialog`を統合する
- [x] 6.3 `frontend/src/app/contexts/page.tsx`に「新規Context作成」ボタンと`CreateContextDialog`を統合する
- [x] 6.4 Claims詳細画面（`frontend/src/app/claims/[id]/page.tsx`）のEvidenceセクションに「Evidence追加」ボタンと`CreateEvidenceDialog`を統合する

## 7. Agent 5: AI候補トリガーとレビューUI改善（Frontend — Web UI）

- [x] 7.1 Claims詳細画面（`frontend/src/app/claims/[id]/page.tsx`）に「AI接続候補を生成」ボタンを追加する。クリック時に`triggerAgentSuggestions`を呼び出し、ローディング状態を表示、完了後にAI接続候補セクションを更新する
- [x] 7.2 `frontend/src/components/ProposalCard.tsx`のApprove/Reject操作後にToast通知を表示し、カードをFade-outアニメーションで非表示にする
- [x] 7.3 `frontend/src/components/ReviewDialog.tsx`のエラー処理を改善する。ネットワークエラー・サーバーエラー時にエラーToastを表示し、Proposalカードを元の状態に維持する
- [x] 7.4 Claims詳細画面のAI接続候補セクションで、承認された接続が関連Claim一覧に反映されるよう、レビュー成功後に`router.refresh()`を呼び出す

## 8. 統合確認

- [ ] 8.1 `docker-compose.yml`にLLM関連の環境変数（`LLM_PROVIDER`, `OPENAI_API_KEY`等）のplaceholderを追加する
- [ ] 8.2 `.env.example`ファイルを新設し、必要な環境変数の一覧とデフォルト値を記載する
- [ ] 8.3 Backend全テスト（`pytest backend/tests/`）がパスすることを確認する
- [x] 8.4 Frontend ビルド（`npm run build`）が成功することを確認する
