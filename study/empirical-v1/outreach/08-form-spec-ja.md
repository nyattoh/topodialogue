# 入力フォーム仕様

## フォーム1：説明確認・同意

必須項目：

1. 研究用ID（短文）
2. 説明文version（固定表示）
3. `04-consent-annotation-ja.md` の各確認項目（個別チェック）
4. 「参加に同意する」（必須チェック）
5. 同意日時（送信日時で記録）

氏名、メール、Googleアカウント、IPアドレスを分析データに取り込まない設定を
優先します。フォームサービスが自動収集する項目は、募集前に確認します。

## フォーム2：発話注釈

固定項目：

- schema version：`topodialogue-independent-annotation-v1`
- codebook version：`1`
- case ID
- annotator ID
- independent before adjudication：`true`

発話ごとの項目：

- turn ID（編集不可）
- 発話本文（参照表示）
- revisit / repair / rejection / adoption / handover / reframing / pause
- notes（任意）

区間ごとの項目：

- start turn ID / end turn ID
- trajectory label（単一選択）
- evidence turn IDs
- notes（任意）

## フォーム3：表示比較

既存の `templates/display-response.json` と同じ項目を使います。conditionと
presentation orderは割付ファイルから自動設定し、参加者に手入力させません。

## データ分離

- 連絡先表：連絡先 ↔ 研究用ID
- 同意表：研究用ID、version、同意日時
- 回答表：研究用IDと回答のみ

三つを別ファイルまたは別権限で管理します。
