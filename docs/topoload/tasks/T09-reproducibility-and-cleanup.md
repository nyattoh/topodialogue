# T09 — 再現性、index、公開前整備

- 推奨maker: GPT-5.6 Luna / medium
- 推奨checker: GPT-5.6 Terra / high
- 種別: mechanical consolidation with executable verification
- 依存: T08

## Objective

研究判断を変えず、clean environmentから文書・test・experiment・tableを再生成できる状態へ整える。

## Read first

1. `AGENTS.md`
2. project gate／release rules
3. `paper/T08-hand_over.md`
4. `reviews/topoload/publication-gate-v0.1.md`
5. all run manifests

## Required work

- README index更新
- exact quickstart
- dependency lock確認
- licence／notice確認
- bibliography key整合
- internal link確認
- generated file policy
- artefact manifest
- data／fixture provenance
- clean-room run script
- spelling／terminology統一
- sensitive data scan
- secret scan
- stale output検出

## Required outputs

- `docs/topoload/reproducibility.md`
- `docs/topoload/publication-manifest.md`
- `scripts/verify_topoload_release.*`
- `output/topoload/release-manifest.json`
- updated root／TopoLoad README

## Verification gates

最低限:

1. fresh environment install
2. unit tests
3. type／lint gate, configuredの場合
4. fixture regeneration twice
5. smoke experiment
6. full offline experiment
7. table／figure regeneration
8. link check
9. no dirty generated diff after second run
10. manifest hash comparison

## Non-goals

- claimの追加
- equation変更
- threshold変更
- result再解釈
- failing testの削除
- independent review findingの非表示化

## Acceptance criteria

- exact commandsとexit codeが残る。
- second generationでtracked file hashが変わらない。
- paper数値とtableが一致する。
- publication manifestがincluded／excluded artefactを列挙する。
- personal dialogue、secret、credentialが含まれない。
- checkerがfresh checkoutからgateを実行する。

## Hand over

公開可能範囲、未解決finding、実行済みgate、未実行gateを日本語で`docs/topoload/T09-hand_over.md`へ記録する。完了は自己申告ではなくgateのexit codeで判定する。
