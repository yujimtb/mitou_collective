# Demo Dataset Specification

## Purpose

プロトタイプのデモンストレーションおよびユーザー試用に使用する「エントロピー」概念を中心としたデモデータセットを定義する。熱力学・統計力学・情報理論にまたがる100〜150件のClaim、30〜50件のEvidence、3つ以上のContextを構造化し、Claim中心知識グラフの価値を具体的に示す。

## Requirements

### Requirement: Context定義

デモデータセットには最低5つのContextが含まれなければならない（SHALL）。

#### Scenario: Classical Thermodynamics Context

- **WHEN** デモデータが投入される
- **THEN** name="Classical Thermodynamics"、field="thermodynamics"、description="マクロ的な熱・仕事の現象論的理論。系の微視的構造を仮定せず、状態変数と状態方程式から出発する。"、assumptions=["macroscopic_system", "equilibrium_states", "no_microscopic_detail"] のContextが存在する

#### Scenario: Statistical Mechanics Context

- **WHEN** デモデータが投入される
- **THEN** name="Statistical Mechanics"、field="statistical_mechanics"、description="微視的状態（ミクロ状態）の統計からマクロ量を導出する理論。確率論と力学の結合。"、assumptions=["large_number_of_particles", "ergodic_hypothesis", "probability_distributions"] のContextが存在する

#### Scenario: Shannon Information Theory Context

- **WHEN** デモデータが投入される
- **THEN** name="Shannon Information Theory"、field="information_theory"、description="通信における不確実性の定量化。離散確率分布上の情報量を扱う。"、assumptions=["discrete_probability_distribution", "communication_channel", "encoding_decoding"] のContextが存在する

#### Scenario: Quantum Information Theory Context

- **WHEN** デモデータが投入される
- **THEN** name="Quantum Information Theory"、field="quantum_information"、description="量子力学的系における情報の定量化。密度行列とフォン・ノイマンエントロピーを中心とする。"、assumptions=["quantum_mechanics", "density_matrix", "hilbert_space"] のContextが存在する

#### Scenario: Algorithmic Information Theory Context

- **WHEN** デモデータが投入される
- **THEN** name="Algorithmic Information Theory"、field="computer_science"、description="Kolmogorov複雑性に基づく情報定量化。文字列の最短記述長で情報量を定義する。"、assumptions=["turing_machine", "algorithmic_complexity", "incompressibility"] のContextが存在する

### Requirement: Term / Concept マッピング

デモデータセットにはエントロピー関連のTerm/Conceptマッピングが含まれなければならない（SHALL）。

#### Scenario: 英語Term "entropy" の多義性

- **WHEN** デモデータが投入される
- **THEN** surface_form="entropy"、language="en" のTermが少なくとも1つ存在する
- **THEN** このTermは以下のConceptに関連付けられる: "Thermodynamic Entropy (S)"（field=thermodynamics）、"Boltzmann Entropy (S = k ln W)"（field=statistical_mechanics）、"Shannon Entropy (H = -Σ p log p)"（field=information_theory）、"Von Neumann Entropy (S = -Tr(ρ ln ρ))"（field=quantum_information）、"Kolmogorov Complexity"（field=computer_science）

#### Scenario: 日本語Term

- **WHEN** デモデータが投入される
- **THEN** surface_form="エントロピー"、language="ja" のTermが存在し、上記の各Conceptに関連付けられる

#### Scenario: 関連Term

- **WHEN** デモデータが投入される
- **THEN** 以下の追加Termが存在する: "disorder"（field_hint=thermodynamics）、"information"（field_hint=information_theory）、"uncertainty"（field_hint=information_theory）、"第二法則"（language=ja, field_hint=thermodynamics）

### Requirement: Claim投入

デモデータセットには100件以上のClaimが含まれなければならない（SHALL）。以下は代表的なClaimの例である。

#### Scenario: 熱力学の基本Claim群

- **WHEN** デモデータが投入される
- **THEN** Classical Thermodynamics Contextに以下のClaimを含む（例）:
  - statement="孤立系のエントロピーは減少しない（熱力学第二法則）"、claim_type=theorem、trust_status=established
  - statement="熱力学的エントロピーは状態関数である"、claim_type=theorem、trust_status=established
  - statement="可逆過程ではエントロピー変化はゼロである"、claim_type=theorem、trust_status=established
  - statement="不可逆過程ではエントロピーは増大する"、claim_type=theorem、trust_status=established
  - statement="エントロピーの次元は [エネルギー]/[温度] である"、claim_type=definition、trust_status=established
  - statement="Clausiusの不等式: ∮δQ/T ≤ 0"、claim_type=theorem、trust_status=established

#### Scenario: 統計力学の基本Claim群

- **WHEN** デモデータが投入される
- **THEN** Statistical Mechanics Contextに以下のClaimを含む（例）:
  - statement="S = k_B ln W（Boltzmannの関係式）"、claim_type=definition、trust_status=established
  - statement="マクロ的エントロピーは微視的状態数の対数に比例する"、claim_type=theorem、trust_status=established
  - statement="ギブスエントロピー: S = -k_B Σ p_i ln p_i"、claim_type=definition、trust_status=established
  - statement="等確率の原理: 孤立系のミクロ状態は等確率で出現する"、claim_type=conjecture、trust_status=tentative

#### Scenario: 情報理論の基本Claim群

- **WHEN** デモデータが投入される
- **THEN** Shannon Information Theory Contextに以下のClaimを含む（例）:
  - statement="H(X) = -Σ p(x) log p(x)（Shannon entropy）"、claim_type=definition、trust_status=established
  - statement="エントロピーは情報の欠如の尺度である"、claim_type=meta、trust_status=tentative
  - statement="Shannonエントロピーは離散確率分布上の不確実性の一意な尺度である（Khinchinの公理化）"、claim_type=theorem、trust_status=established
  - statement="相互情報量 I(X;Y) = H(X) - H(X|Y)"、claim_type=definition、trust_status=established

#### Scenario: 分野横断Claim群

- **WHEN** デモデータが投入される
- **THEN** 以下のような分野横断的Claimを含む:
  - statement="Boltzmannエントロピーの極限でShannonエントロピーと対応する"、context=Cross-field、claim_type=conjecture、trust_status=ai_suggested
  - statement="Jaynesの最大エントロピー原理は統計力学と情報理論を統一する"、context=Cross-field、claim_type=theorem、trust_status=tentative
  - statement="Von Neumannエントロピーは量子系におけるShannonエントロピーの一般化である"、context=Quantum Information Theory、claim_type=theorem、trust_status=established

### Requirement: Evidence投入

デモデータセットには30件以上のEvidenceが含まれなければならない（SHALL）。

#### Scenario: 教科書Evidence

- **WHEN** デモデータが投入される
- **THEN** 以下のような教科書Evidenceを含む:
  - title="Thermodynamics and an Introduction to Thermostatistics"、evidence_type=textbook、source="Callen, H.B. (1985) Wiley"、reliability=high
  - title="Statistical Mechanics"、evidence_type=textbook、source="Pathria, R.K. & Beale, P.D. (2011) Academic Press"、reliability=high
  - title="Quantum Computation and Quantum Information"、evidence_type=textbook、source="Nielsen, M.A. & Chuang, I.L. (2000) Cambridge University Press"、reliability=high

#### Scenario: 論文Evidence

- **WHEN** デモデータが投入される
- **THEN** 以下のような原著論文Evidenceを含む:
  - title="A Mathematical Theory of Communication"、evidence_type=paper、source="Shannon, C.E. (1948) Bell System Technical Journal"、reliability=high
  - title="Information Theory and Statistical Mechanics"、evidence_type=paper、source="Jaynes, E.T. (1957) Physical Review"、reliability=high
  - title="Über die Beziehung zwischen dem zweiten Hauptsatze der mechanischen Wärmetheorie und der Wahrscheinlichkeitsrechnung"、evidence_type=paper、source="Boltzmann, L. (1877)"、reliability=high

#### Scenario: Evidence-Claim関連付け

- **WHEN** デモデータが投入される
- **THEN** 各EvidenceはrelationshipをもってClaimに関連付けられる（例: CallenのテキストはClaimの「孤立系のエントロピーは減少しない」をsupportsする）
- **THEN** 1つのEvidenceは複数のClaimをサポートできる

### Requirement: Cross-field Connection初期データ

デモデータセットにはAI提案を模した分野間接続の初期データが含まれなければならない（SHALL）。

#### Scenario: 初期接続候補

- **WHEN** デモデータが投入される
- **THEN** 以下のようなCross-field Connection（status="proposed"またはstatus="approved"）を含む:
  - BoltzmannエントロピーとShannonエントロピーの間のanalogous接続（confidence=0.85）
  - ギブスエントロピーとShannonエントロピーの間のequivalent接続（confidence=0.92）
  - Von NeumannエントロピーとShannonエントロピーの間のgeneralizes接続（confidence=0.88）
  - Kolmogorov複雑性とShannonエントロピーの間のcomplements接続（confidence=0.65）

### Requirement: CIR初期データ

デモデータセットには3〜5件のCIR例が含まれなければならない（SHALL）。

#### Scenario: 第二法則のCIR

- **WHEN** デモデータが投入される
- **THEN** 「孤立系のエントロピーは減少しない」ClaimにCIR（context_ref="Thermodynamics_Classical"、subject="entropy(system)"、relation="non_decreasing_over_time"、conditions=[{predicate:"isolated", argument:"system", negated:false}, {predicate:"macroscopic", argument:"system", negated:false}]）が設定される

#### Scenario: BoltzmannエントロピーのCIR

- **WHEN** デモデータが投入される
- **THEN** 「S = k_B ln W」ClaimにCIR（context_ref="Statistical_Mechanics"、subject="S"、relation="equals"、object="k_B * ln(W)"、conditions=[{predicate:"microcanonical_ensemble", argument:"system", negated:false}]、units="J/K"）が設定される

#### Scenario: ShannonエントロピーのCIR

- **WHEN** デモデータが投入される
- **THEN** 「H(X) = -Σ p(x) log p(x)」ClaimにCIR（context_ref="Shannon_Information_Theory"、subject="H(X)"、relation="equals"、object="-sum(p(x) * log(p(x)))"、conditions=[{predicate:"discrete_distribution", argument:"X", negated:false}, {predicate:"finite_support", argument:"X", negated:false}]、units="bits"）が設定される

### Requirement: デモデータ投入スクリプト

デモデータセットはスクリプト化され、再現可能に投入できなければならない（SHALL）。

#### Scenario: Seedスクリプト実行

- **WHEN** `python -m app.seeds.entropy_dataset` が実行される
- **THEN** すべてのContext、Term、Concept、Claim、Evidence、Cross-field Connection、CIRが正しい関連付けとともにデータベースに投入される

#### Scenario: 冪等性

- **WHEN** Seedスクリプトが複数回実行される
- **THEN** 既存データと重複するレコードは作成されず、冪等に動作する
