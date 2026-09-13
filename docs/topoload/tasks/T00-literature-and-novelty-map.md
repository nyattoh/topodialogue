# T00 — 文献・新規性地図

- 推奨maker: GPT-5.6 Sol / xhigh
- 推奨checker: GPT-5.6 Sol / max、新規session
- 種別: research gate
- 依存: なし
- 次task: T01, T02

## Objective

TopoLoadの各操作を先行研究へ分解して照合し、「名前が違うだけの既存方式」を新規と誤認しないoperation-level evidence mapを作成する。

## Read first

1. `AGENTS.md`
2. `docs/topoload/README.md`
3. `docs/topoload/00-paper-outline.md`
4. `docs/topoload/01-formal-model.md`
5. `docs/topoload/03-claim-boundaries.md`
6. `docs/02-related-work.md`
7. `references.bib`

## Research lanes

最低限、次を一次資料中心に調べる。

1. model routing／cascades／cost-quality optimisation
2. speculative execution／verification
3. agent loop detection／circuit breakers／budget termination
4. goal-conditioned planning／progress monitoring
5. state-space projection／directional deviation
6. semantic recurrence／information gain／multi-turn recovery
7. queueing／admission control／rate limiting／burst smoothing
8. context compression／memory provenance／loss declaration
9. canonical event stores／derived views
10. occlusion biomechanics: canine guidance、group function、periodontal ligament、load direction
11. biologically inspired computing／control architecture

## Required deliverables

### A. `docs/topoload/research/related-work-map.md`

各文献について:

- bibliographic entry
- stable URL／DOI
- exact operation
- input signal
- control action
- measured outcome
- overlap with TopoLoad
- difference, if any
- evidence strength
- unresolved question

### B. `docs/topoload/research/claim-matrix.md`

TopoLoadのclaimを行単位にし、次へ分類する。

- already established
- combination hypothesis
- implementation contribution
- evaluation contribution
- unsupported／remove
- unresolved after search

### C. `docs/topoload/research/search-log.md`

- database／search engine
- exact query
- search date
- inclusion／exclusion criteria
- backward／forward citation search
- unavailable source

### D. `references-topoload.bib`

採用資料だけを追加し、title、author、year、venue、DOI／URLを検証する。

## Non-goals

- 論文本文を書くこと
- 新規性を肯定するためだけの検索
- blog、marketing page、二次要約だけでclaimを支えること
- 咬合比喩の正しさを証明すること

## Acceptance criteria

- TopoLoadの各componentに少なくとも一つの近接研究又は「見つからなかった」というsearch recordがある。
- direct noveltyではなくoperation overlapが比較されている。
- Flash Attentionとsparse attention、speculative decodingの役割を混同していない。
- canine guidanceを普遍的唯一の咬合として扱っていない。
- energy claimの一次測定条件が区別されている。
- claim matrixから、T01で残す数式と削る比喩が判断できる。

## Checker prompt

makerの結論を確認するのではなく、次を探す。

- 同じoperationを別名で実装した先行研究
- citationがclaimを実際には支えていない箇所
- publish dateとevent dateの混同
- review paperだけを根拠にした重要claim
- negative又はcontradictory evidenceの欠落
- TopoDialogue／TopoPhase既存成果との自己重複

## Hand over

完了時に、残ったnovelty hypothesis、棄却したclaim、T01へ固定してよい定義、未解決点を日本語で`docs/topoload/research/T00-hand_over.md`へ記録する。
