# AGENTS.md — TopoDialogue research prototype

## Mission
Build the smallest falsifiable prototype of **TopoDialogue / 対話位相検索**: detect recurrent semantic loops in long-horizon human–LLM dialogue, then choose a transformation operator that changes the conversational coordinate system and tests whether the user generates genuinely new semantic states.

## Read first
1. `README.md`
2. `docs/index.md`
3. `docs/00-research-scope.md`
4. `docs/03-architecture.md`
5. `docs/04-data-schema.md`
6. `docs/05-loop-detection.md`
7. `docs/06-transformation-operators.md`
8. `docs/07-evaluation.md`
9. `CODEX_TASK.md`

The `source/` directory contains the original conceptual materials. Treat them as source context, not as directly executable specifications.

## Non-negotiable research constraints
- **Phase 1 only unless explicitly asked otherwise.** Do not add multi-agent orchestration, GraphRAG, persistent homology, wearable/body sensors, or a production UI in the first implementation.
- The word **topology** is a research metaphor/structural hypothesis in Phase 1. The initial detector is semantic recurrence + temporal graph analysis. Do not pretend that graph cycles alone are topological invariants.
- Preserve provenance: every extracted state/node must record whether it came from the user, assistant, heuristic, or model inference.
- Never turn inferred psychological states into facts. Store confidence and evidence span.
- Do not optimize for “agreement with the assistant.” Optimize for measurable semantic progress and user-originated novelty.
- Raw personal dialogue must not be required for tests. Use synthetic/anonymized fixtures.
- Core tests must run without network access and without paid APIs.
- LLM and embedding providers must sit behind interfaces. Include deterministic test doubles.
- Do not claim research novelty in code or docs. Use “novelty hypothesis” until a systematic literature review is complete.

## Implementation preferences
- Python 3.11+
- Pydantic v2 for schemas
- NetworkX for Phase-1 temporal graph calculations
- NumPy / SciPy / scikit-learn where appropriate
- SQLite for local experiment storage
- `pytest` for tests
- Optional `sentence-transformers` adapter; tests use a deterministic fake embedder
- Optional local/remote LLM adapters; tests use a rule-based or fixture-backed generator

## Required quality gates
- Type-checkable, documented modules.
- Unit tests for recurrence, novelty, loop thresholding, operator selection, provenance, and cooldown behavior.
- Golden tests using `examples/formative-case.jsonl`.
- Reproducible experiment config with random seeds.
- `README` must explain exact commands to run tests and the demo.

## Scope boundary
The research target is **dialogue control**, not therapy, diagnosis, or clinical decision-making. Safety logic must avoid escalating vulnerable users into increasingly intense introspection when the system detects distress or uncertainty.

<!-- develop-control-plane:shared-policy:begin -->
## Shared control-plane policy (managed)

This project belongs to the portable workspace whose marker is
.workspace-root.json. Locate that marker by walking upward; do not depend on
an absolute drive path.

- Create and keep project implementation only in the workspace's works
  directory.
- Before work, consult this file, project memory, and the shared verified rules
  embedded below.
- When the user corrects an agent or an independent checker rejects work,
  record the failure with .workspace/runtime/record-feedback.ps1.
- Promote only verified, reusable lessons with
  .workspace/runtime/promote-rule.ps1; promotion synchronizes every project.
- Checkpoint before compaction and at planning, implementation, verification,
  and hand over boundaries.
- Never store secrets or raw conversation transcripts in logs or memory.

### Shared verified rules

# RULES — distill 済み一般化ルール（consult 対象）

> `LEDGER.md` で `verified: true` になった失敗から昇格した、一般化ルール置き場。
> **maker / checker は毎 run 冒頭でこのファイルを読む**（consult）。ここに書いてあることは
> もう再導出しない ── 読んで即適用する。
>
> ルールは「命令形の1行 + なぜ + どう適用」で書く。抽象論ではなく行動で書く。

---

## フォーマット

```markdown
### <anchor>: <命令形の1行ルール>
- **なぜ**: どの失敗から来たか（LEDGER の日付/タイトル）。
- **どう適用**: 次回、具体的に何をするか。
```

---

## ルール

<!-- 昇格したルールをここに追記する。例を1つ残しておく（削除可）。 -->

### config-verify-before-commit: 他ツールの設定を書いたら、そのツールで実際にロードして検証してから確定する
- **なぜ**: 調査サンプルと実スキーマの乖離で、未検証のまま採用してパースエラーを繰り返した。
- **どう適用**: 設定ファイル・プラグイン定義を書いたら、`<tool> validate` / `--help` /
  実ロードで exit 0 を確認してからコミット候補にする。推測で正しいと見なさない。

### stop-only-on-gate: 完了は gate.sh の exit code だけで判定する。自己申告で止まらない
- **なぜ**: 「直りました」「review OK」での完了は Ralph Wiggum 失敗（幻の完了）。
- **どう適用**: maker も checker も、停止前に必ず `gate.sh` を自分で実行し exit code を見る。

### control-plane-over-entrypoint: 入口のskillやCLI設定を正本にせず、共有memory・state・runtimeを正本にする
- **なぜ**: 単一skillへ目的を縮小すると、CLIやディレクトリが変わった時に改善履歴と動作が分断される。
- **どう適用**: プロバイダー固有機能は薄いアダプターとして扱い、検証済みルールと状態はルート検出可能な共有コントロールプレーンへ保存して全プロジェクトへ同期する。

### canonical-assets-with-pointers: 共有skill・role・provider設定は.workspace内だけに正本を置き、検出用パスはjunctionまたは生成アダプターにする
- **なぜ**: 自動検出ディレクトリごとに実体を置くと、修正先が分散してCLI間で内容がずれる。
- **どう適用**: .workspace/skills、providers、rolesを編集元とし、ルートはjunction、プロジェクトは共有skillへのjunctionと中央templateからの保護付き生成物だけにする。

### verify-junction-target-before-delete: junctionを含むディレクトリを移動・削除するときはリンク先と正本の残存を検証してから複製を消す
- **なぜ**: Windowsの移動操作がjunctionを期待どおり保持せず、リンク先を実体化または巻き込む場合がある。
- **どう適用**: 移動前後にGet-ItemのLinkType/Targetと正本ファイルを確認し、validatorを通すまで旧実体や複製を削除しない。

### discriminate-jsonl-events: 複数種類のイベントを同じJSONLへ保存するときはtypeまたはプロパティ存在を確認してから読む
- **なぜ**: 異なるイベント形状を同一スキーマとして扱うとStrictModeや集計処理が途中で停止する。
- **どう適用**: readerはevent typeで分岐し、optional propertyへアクセスする前に存在確認する。API overloadは実データで通し実行する。

### normalize-powershell-collections: PowerShellで0件・1件・複数件を同じように扱うcollectionは代入全体を@(...)で正規化する
- **なぜ**: 内側だけを@()で包んでもif式やpipeline境界で1件がscalarへ展開され、追加やCount処理が壊れる。
- **どう適用**: $items = @(if (...) { ... }) の形で境界を正規化し、0件・1件・2件のテストを行う。

### delimit-powershell-interpolation: PowerShellの文字列補間で変数直後にコロンや識別文字を置くときは${name}で境界を明示する
- **なぜ**: $name:suffixは意図した文字列連結ではなく別の変数参照として解釈され、値が消える場合がある。
- **どう適用**: マーカー・パス・ID生成では${name}:suffixを使い、生成結果の開始・終了・件数を実データで検証する。

### generated-files-must-be-idempotent: 同期・生成スクリプトは同じ入力で2回実行してもファイルhashを変えない
- **なぜ**: 改行や並び順だけの差分でも作業ツリーを汚し、本当の変更とユーザー編集を見分けにくくする。
- **どう適用**: 出力を正規化して書き、生成→hash取得→再生成→hash比較を検証に含める。

### tracked-files-override-copy-exclusions: プロジェクトコピーでは生成物ディレクトリ除外よりGit追跡済みファイルの保持を優先する
- **なぜ**: buildやdistという名前でも設定・plugin・fixtureなどの正本が追跡されている場合がある。
- **どう適用**: 除外コピー後にgit ls-filesで除外prefix内の追跡済みファイルを列挙・復元し、同期前statusを元と比較する。

### choose-substrate-from-native-capabilities: 既存prototypeの技術基盤を前提にせず、要求されたnative能力からdesktop・Code OSS・webの基盤を選び直す
- **なぜ**: Web試作へ機能を足す計画に固定し、複数PTY terminal、shell/WSL profile、native explorerという初期要件をGoalから落とした。
- **どう適用**: native filesystem、複数PTY、shell profile、WSL、editor workbenchが主要要件なら、実装前にCode OSS distribution、VS Code extension、Electron独自実装を比較し、prototypeの再利用量より要件適合を優先する。

### use-hand-over-for-transfer: 引継ぎを表すときは hand over を使い、handoff と hand off は禁止する
- **なぜ**: 誤った引継ぎ表現が共通テンプレート、イベント名、ログ見出しへ拡散し、全CLI・AIが同じ不適切な英語を再生成した。
- **どう適用**: 人やAI間の引継ぎは本文で hand over、識別子で hand_over、定数で HAND_OVER と書く。禁止語は、この禁止規則自体を説明するとき以外は、新規文書、コード、状態、ログ、ユーザー向け出力に生成しない。

### write-approval-materials-in-japanese: ユーザーの確認・承認が必要な文書と質問は日本語で書く
- **なぜ**: 技術識別子を英語で維持する必要性と、ユーザー向け説明言語を混同し、承認対象の理解コストを上げた。
- **どう適用**: PRD、設計判断、選択肢、受入条件、承認質問は日本語にする。API名、コード識別子、規格名など原語が必要な箇所だけ英語を残し、日本語で意味を補う。

### update-human-readable-state-on-checkpoint: checkpointごとに機械可読状態と人が読めるSTATE.mdを同時に更新する
- **なぜ**: current.jsonだけが更新されSTATE.mdが存在しなかったため、stateディレクトリが停止しているように見え、再開時の現在地も人が確認できなかった。
- **どう適用**: checkpoint runtimeはstate/current.jsonを常に更新し、state/STATE.mdを未作成なら初期化して現在日時・段階・対象・概要を日本語で更新する。プロジェクト指定時はproject checkpointも同時に更新する。

### mirror-human-decisions-to-review-queue: ユーザーの確認・承認待ちはstateのREVIEW_QUEUEへ同時に登録する
- **なぜ**: 計画文書が承認待ちでもREVIEW_QUEUEが空だと、stateだけを見た人や別AIが人の判断待ちを見落として実装開始条件を誤る。
- **どう適用**: PRD承認、設計判断、選択肢確認、checkerの判断要項目が発生したらupdate-review.ps1で安定ID付きopen項目を登録する。ユーザー判断後はdecided、反映と検証後はdoneへ更新する。

### redact-before-observing-credential-pages: 認証情報が表示され得る画面ではfull snapshotを出力せず、対象状態を検証して資格情報を伏せた限定読み取りだけを使う
- **なぜ**: SPA遷移の失敗を見落としてBot TokenをDOM snapshotへ含めた。
- **どう適用**: APIキー・Token・OAuth codeを扱う画面ではURLだけで遷移成功と見なさず、active peerや安全な状態信号を確認する。本文が必要ならcredential regexで伏せてから限定範囲だけ返す。

### redact-ellipsized-token-previews: 認証情報を含む画面の限定読み取りでは、完全なTokenだけでなく省略表示されたToken previewも出力前に伏せる
- **なぜ**: BotFatherのToken再発行後、完全なTokenは伏せたがsidebar previewの省略Token prefixが出力に残った。
- **どう適用**: Telegram Bot Tokenなどは完全形 regex に加えて、数字ID + colon + 英数字prefix + ellipsis/三点リーダ/末尾省略を検出して伏せる。必要な本文だけを対象要素から読む場合も、周辺preview/sidebarを含めた出力には同じ redaction をかける。

### verify-wsl-vm-liveness-for-daemons: WSL上の常駐daemonをWindowsから使わせる時は、systemd serviceのactive確認だけでなくWSL VM自体を保持する仕組みと実受信を検証する
- **なぜ**: systemd lingerはWSL VMの常時起動を保証せず、foreground WSL client終了後にTelegram gatewayが止まり、BotへのDMが未処理で残った。
- **どう適用**: WSL内サービスを外部Webhook/polling用途にする場合、Windows側keepaliveまたは自動起動タスクを用意し、getUpdates conflictや実DM応答など外部から到達可能な証拠で確認する。

### redact-messaging-destination-identifiers: メッセージ送信検証では宛先IDを出力しない
- **なぜ**: Hermes sendなどの成功出力にはchat_idやuser/channel IDが含まれ、ユーザー識別子を不要に transcript へ露出する。
- **どう適用**: Telegram/Discord/Slack等の送信検証はstdoutを破棄するか、成功/失敗だけを出すラッパーで実行する。必要な場合も宛先IDは伏せ、TokenやAPIキーと同じくログ・最終回答へ再掲しない。

### virtualized-export-e2e: 仮想化された一覧や会話のエクスポートは、表示中DOMの単発取得で完了扱いにしない。
- **なぜ**: 長い履歴では画面外ノードが破棄・再利用されるため、見えている件数だけの取得でも一見成功してしまう。hidden属性もコンポーネントCSSに上書きされ得る。
- **どう適用**: 上端から下端まで重なりを持って走査し、順序を保って蓄積する。実拡張を読み込むE2EでDOM再利用、全件一致、終了上限、進捗オーバーレイ消去を検証し、[hidden]のdisplay:noneを明示する。

### provider-ui-label-exclusion: 会話エクスポートではサイト固有のUI見出しを発話本文に含めない。
- **なぜ**: 役割判定が正しくても、UIラベル混入は検索・要約・類似度計算・可視化ラベルを汚染する。
- **どう適用**: 本文の意味的ノードを外側コンテナより優先し、外側しか取得できない場合は既知ラベルを先頭一致かつ区切り確認付きで限定除去する。E2EではUIラベルをfixtureに含め、出力本文に残らないことを明示検証する。

### prefer-current-browser-runtime: Codexのブラウザ接続では利用可能な同梱クライアントを比較し、現行setupBrowserRuntimeを優先して実タブ取得まで検証する
- **なぜ**: 古いbrowser-use 0.1.0-alpha1のsetupAtlasRuntimeは現在の保護processとバックエンド探索に不整合があり、再起動しても接続できなかった。
- **どう適用**: browser-clientの版と更新日時を確認し、現行setupBrowserRuntimeから対象URLに適したbrowserを選ぶ。成功判定はopenTabs、claimTab、URL、title、DOMの実取得で行い、旧クライアントの初期化失敗をユーザー側の再起動不足と見なさない。

### preserve-split-mail-routing: メール連携を変更する前に受信経路と既存connectorの役割を確認し、別アカウント追加のために既存業務アカウントや配送設定を切り替えない
- **なぜ**: 分割配送と単一connector制約を統合せず、仕事用接続を失う提案と不要なDNS・転送変更を招いた。
- **どう適用**: profile、転送元・転送先、用途、複数アカウント可否をread-onlyで確認し、既存経路を保存した独立connectorまたはread-only bridgeを追加する。
<!-- develop-control-plane:shared-policy:end -->
