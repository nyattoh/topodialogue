# T08 — 論文初稿

- 推奨maker: GPT-5.6 Sol / xhigh
- 推奨checker: GPT-5.6 Sol / max、新規session
- 種別: evidence-bound synthesis
- 依存: T00–T07
- 次task: T09

## Objective

事前登録、実装、raw result、独立反証に拘束された論文初稿を作る。予定していたstoryへ結果を合わせない。

## Read first

1. `docs/topoload/00-paper-outline.md`
2. `docs/topoload/03-claim-boundaries.md`
3. `docs/topoload/research/claim-matrix.md`
4. `study/topoload/preregistration-v0.1.md`
5. latest run manifest and claim-evidence table
6. `reviews/topoload/falsification-v0.1.md`
7. `reviews/topoload/claim-verdict-v0.1.md`
8. `reviews/topoload/publication-gate-v0.1.md`
9. verified bibliography

## Required deliverables

- `paper/topoload-v0.1.md`
- `paper/topoload-v0.1-claim-ledger.md`
- `paper/topoload-v0.1-figures.md`
- `paper/topoload-v0.1-supplement.md`

## Draft rules

- British Englishを使う。
- Abstractは実測結果だけを書く。
- Introductionで咬合を動機として扱い、方法の証明にしない。
- Related workはoperation-level overlapを正面から示す。
- Methodsは再現可能なdetailを持つ。
- ResultsとDiscussionを分離する。
- null／negative resultを省略しない。
- simulatorとreal-model resultを明確に分ける。
- energy未計測ならenergy reductionを書かない。
- topologyという語は、数学的手法を使わない範囲ではseries名又はstate-space文脈へ限定する。

## Claim ledger

論文内の主要文ごとに:

- claim ID
- exact sentence
- source table／figure／primary citation
- scope
- uncertainty
- falsification finding
- permitted wording

を記録する。

## Required sections

1. Abstract
2. Introduction
3. Design inspiration and non-equivalence
4. Related work
5. Problem formulation
6. Direction-aware controller
7. Canonical-preserving damping
8. Experimental setup
9. Results
10. Error and failure analysis
11. Discussion
12. Limitations and ethics
13. Conclusion
14. Reproducibility statement

## Acceptance criteria

- 全数値がgenerated outputへtraceできる。
- claim ledgerに孤立claimがない。
- T07でinconclusive又はcontradictedのclaimを強く書いていない。
- quality非劣性を満たさないcost resultを成功扱いしていない。
- 咬合の医学的説明に一次資料がある。
- model／effort、snapshot、date、config hashがsupplementにある。
- negative resultがAbstract又はDiscussionで適切に触れられている。

## Checker focus

- causal overstatement
- novelty overstatement
- unsupported biological analogy
- result／discussion混在
- selective task family reporting
- missing uncertainty
- American spelling
- forbidden transfer terminology

## Hand over

未解決claim、追加runの必要性、人間承認箇所を`paper/T08-hand_over.md`へ記録する。
