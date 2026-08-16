# 旧バッチ ― ControlDrOperationCommand（DR 指令制御）

## 概要

`ControlDrOperationCommand` は**毎分**（cron `* * * * *`）実行され、あらかじめスケジュールされた **DR（Demand Response）** の指令を実際に実行する箇所である ― `Instructions` テーブル（`hemssv` と共用のテーブルであり、実際に指令をGWへ送り出す箇所）を経由して**「暖房制御ユニット」（`device_id=1001`、北ガス独自クラス）**へECHONET Liteの指示を送り、そのうえで状態を更新してアプリへ通知する。1件のDR指令は**独立した2つの「フェーズ」**を持ち（フェーズごとに指令種別・時刻・温度・状態を個別に持つ）― E-GW要件に挙げられた2種類の指示の方式をいずれも表現するために用いられる：*「サーバーが開始時と終了時の両方で指令を送る」*（ON/OFF）と、*「サーバーが開始時に終了時刻をあらかじめ含めて指令を送る」*（温度変更 ― 機器が自ら復帰するため2回目の指令は不要）である。**本バッチが制御するのはちょうど1種類の機器（暖房制御ユニット）のみ**であり ― 要件に挙げられたDRの範囲全体（エアコン、コレモ、蓄電池、エコキュート）ではない；詳細は第2部に示す。

## 第1部 ― 概要

| 項目 | 内容 |
|---|---|
| **役割** | `ConDrOperations` にスケジュールされた時刻ちょうどに、暖房機器を制御するECHONET Liteの指令（ON/OFFまたは温度変更）を送信し、状態を追跡し、期限切れの指令をクローズし、アプリへ通知する。 |
| **入力** | `ConDrOperations` + `ConDrOperationDestinations`（DRのスケジュール、EMS-SP単位、2フェーズ）＋ `HemsGws`（世帯のGW）＋ `ConDevices` ＝ 物理テーブル `t_201`（世帯の暖房機器＋アプリ機器）＋ `ConDeviceStatuses` ＝ `t_202`（現在の温度、オフセットが必要な場合）＋ `ConDeviceControls` ＝ `t_301`（5分以内の重複送信の防止）― 物理テーブル名は `setTable()` による（`ConDevicesTable.php:41`・`ConDeviceStatusesTable.php:41`・`ConDeviceControlsTable.php:41`）。 |
| **出力** | `Instructions` へのInsert（`hemssv` を経由してGWへ送る指令）＋ `ConDeviceControls`（指令の履歴）＋ `ConDrOperationDestinations` の `status_1`/`status_2` の更新 ＋ `ConMessages`/`ConMessageDestinations`（アプリへの「DR を開始しました」通知）。 |
| **処理概要** | 1. 各フェーズ（1および2）について：開始時刻に達したdestination（`start_at_N <= now <= end_at_N`、`status_N=SCHEDULED`）を探し、指令を送信し、状態を更新し、送信に成功したEMS-SPの一覧をアプリへの通知のためにまとめる。<br>2. 各フェーズについて：終了時刻を過ぎている（`end_at_N < now`）にもかかわらず `SCHEDULED`/`RUNNING` のままであるdestinationを探し、`FAILED`/`COMPLETE` としてクローズする。 |

## 第2部 ― 詳細

### 処理の全体図 ― 毎分実行

```
execute():
  startOperations(now, phase=1)    → 時刻に達したフェーズ1の指令を送信           §2.3
  startOperations(now, phase=2)    → 時刻に達したフェーズ2の指令を送信           §2.3
  finishOperations(now, phase=1)   → 終了時刻を過ぎたフェーズ1の指令をクローズ   §2.7
  finishOperations(now, phase=2)   → 終了時刻を過ぎたフェーズ2の指令をクローズ   §2.7
```

| ステップ | 内容 | 詳細箇所 |
|---|---|---|
| ― | 実行スケジュールとパラメータ | §2.1 |
| ― | 1件のDR指令の構造 ― 独立した2つのフェーズ | §2.2 |
| 1 | 時刻に達した指令の検索と送信（`startOperations`） | §2.3 |
| 1a | 5分以内の重複送信の防止 | §2.4 |
| 1b | 実際のECHONET指示の組み立てと送信（`dispatchOperation`） | §2.5 |
| 1c | アプリへの「DR を開始しました」通知 | §2.6 |
| 2 | 期限切れの指令のクローズ（`finishOperations`） | §2.7 |

---

### 2.1 実行スケジュールとパラメータ

| 項目 | 内容 |
|---|---|
| 実行スケジュール | Cron `* * * * *` ― 毎分（[mng-webap_cron設定_20241029.txt:77](legacy_eminel_docs/docs/02_詳細設計/10_バッチ処理/mng-webap_cron設定_20241029.txt#L77)） |
| パラメータ `--send_time` | 処理の基準時刻を上書きできる ― `getOption('send_time')` によって**正しく読み取っており**、宣言 `addOption('send_time')` と一致している（[:66-75](legacy_eminel_docs/sources/conciergesv-develop/src/Command/ControlDrOperationCommand.php#L66-L75)）― 先に調査した2つのバッチ（`DispatchPushMessagesCommand`、`DistributeMonthlyEcoPointsCommand`）とは異なる：それらでは同様のパラメータが誤った型で宣言されており機能していない |
| `$allowDuplicateExec = true` | `BaseCommand` のデフォルトのlock-fileをオーバーライドする（[:38](legacy_eminel_docs/sources/conciergesv-develop/src/Command/ControlDrOperationCommand.php#L38)）― バッチが毎分実行されるため妥当である：1回の実行が1分を超えた場合（DBが遅い場合）、lock-fileは重複した実行を許す代わりに**1分ぶんの処理を丸ごと落とす**ことになるためである |

### 2.2 1件のDR指令の構造 ― 独立した2つのフェーズ

`ConDrOperation` はいずれも同じ形の2組のフィールドを持ち、`_1`/`_2` の番号が付けられており、状態は `ConDrOperationDestination`（`status_1`, `status_2`）において個別に追跡される：

| フィールド（フェーズ別） | 意味 |
|---|---|
| `operation_N` | `ON` / `OFF` / `CHANGE_TEMP` |
| `start_at_N` / `end_at_N` | 当該フェーズの有効時間帯 |
| `temp_N` | 温度（`operation_N=CHANGE_TEMP` の場合のみ使用）― 絶対値の場合と**オフセット**の場合がある |
| `temp_origin_N` | `ZERO`（temp_N は絶対値）または `CURRENT`（temp_N は指令送信時点で設定されている温度に対する**差分**）（[ConDrOperation.php:38-39](legacy_eminel_docs/sources/eminel_sv_lib-develop/src/Model/Entity/ConDrOperation.php#L38-L39)） |
| `status_N` | `SCHEDULED` → `RUNNING`/`COMPLETE` → または `FAILED`/`CANCELED`（[ConDrOperationDestination.php:25-29](legacy_eminel_docs/sources/eminel_sv_lib-develop/src/Model/Entity/ConDrOperationDestination.php#L25-L29)） |

`operation_2`/`start_at_2`/... はいずれも**nullable**であり ― 1件のDR指令がフェーズ1のみを使用することもありうる。2つのフェーズの使い方は、E-GW要件（UC-05 01-3）に挙げられた2種類のDR指示の方式と一致する：**ON/OFF** は「終了」の指令として独立したフェーズ2を必要とする（期限が来た時点で明示的に送信する）一方、**CHANGE_TEMP** はフェーズ1の指令の中に終了時刻をあらかじめ埋め込む（§2.5参照）ため、機器が自ら復帰し、フェーズ2を必要としない。

### 2.3 時刻に達した指令の検索と送信（`startOperations`）

各フェーズについて、`status_N=SCHEDULED` であり、かつ `start_at_N <= now <= end_at_N` の範囲内にある `ConDrOperationDestination` を取得する（[:84-97](legacy_eminel_docs/sources/conciergesv-develop/src/Command/ControlDrOperationCommand.php#L84-L97)）。destinationごとに `dispatchOperation()`（§2.5）を呼び出す；送信に成功した場合（[:105-121](legacy_eminel_docs/sources/conciergesv-develop/src/Command/ControlDrOperationCommand.php#L105-L121)）：

| 指令種別 | 新しい状態 |
|---|---|
| `ON` / `OFF` | 直ちに `COMPLETE` ― 送信した時点で完了とみなす |
| `CHANGE_TEMP` | `RUNNING` ― まだ完了ではなく、`end_at_N` を過ぎた時点の `finishOperations` で初めて `COMPLETE` としてクローズする |

`dispatchOperation()` が `false` を返した場合（重複により遮断された、GW／機器が存在しない、その他のエラー）→ **`SCHEDULED` のまま**とし、何も記録しない ― destinationは引き続き条件に合致するため、次の分の実行が自動的に再試行し、成功するか `end_at_N` が過ぎる（`finishOperations` により `FAILED` としてクローズされる）まで続く。この実行の中で送信に成功したEMS-SPはすべてまとめられ、アプリへの通知に用いられる（§2.6）。

### 2.4 重複送信の防止 ― `checkConflicting`

新しい指令を組み立てる前に、同一のEMS-SP＋暖房機器（`device_id=1001`）の `ConDeviceControl` のうち、**直近5分以内**に作成され、かつ**結果がまだ返ってきておらず**（`result_received IS NULL`）、**HEMSのエラーとしてまだ記録されていない**（`send_result_kind IS NULL`）ものが存在するかを確認する（[:130-139](legacy_eminel_docs/sources/conciergesv-develop/src/Command/ControlDrOperationCommand.php#L130-L139)）― 存在する場合は今回の実行をスキップする（destinationは `SCHEDULED` のままとし、次の分に再試行する）。

### 2.5 実際の指示の組み立てと送信（`dispatchOperation`）

1. 世帯の `gw_id` を `HemsGws` から取得する；存在しない場合 → スキップする（[:160-169](legacy_eminel_docs/sources/conciergesv-develop/src/Command/ControlDrOperationCommand.php#L160-L169)）。
2. 世帯の**2つの機器**を取得する：暖房機器（`device_id=1001`）と、**任意の「アプリ」機器1台**（`device_id` が `0000-0009` の範囲）― どちらか一方でも欠けている場合 → スキップする（[:171-198](legacy_eminel_docs/sources/conciergesv-develop/src/Command/ControlDrOperationCommand.php#L171-L198)）。
3. `operation_N` に従ってECHONETの指令内容を組み立てる（[:223-271](legacy_eminel_docs/sources/conciergesv-develop/src/Command/ControlDrOperationCommand.php#L223-L271)）：

| `operation` | EPC | `edt` の内容 |
|---|---|---|
| `ON` | `80` | `30` |
| `OFF` | `80` | `31` |
| `CHANGE_TEMP` | `B0` | `31` + 温度（符号付きhex）+ **終了時刻**（`end_at_N`、`edt` に直接埋め込む形式） |

   `CHANGE_TEMP` の場合、`temp_origin_N=CURRENT` であれば：現在の設定温度を `ConDeviceStatuses` から読み取り（EPC `A1`、符号付きhexをデコードする）、そこに `temp_N` を**加算した**値を最終値とする ― データが存在しない場合 → スキップする（[:242-261](legacy_eminel_docs/sources/conciergesv-develop/src/Command/ControlDrOperationCommand.php#L242-L261)）。
4. `ConDeviceControls`（履歴。§2.4の重複防止に使用する）+ `Instructions`（実際の指令のキュー。`instruction_type=1`＝「宅外制御指示」。`hemssv` と共用してGWへ送り出す）を1つのトランザクションの中で保存する（[:283-294](legacy_eminel_docs/sources/conciergesv-develop/src/Command/ControlDrOperationCommand.php#L283-L294)）。

> ⚠️ **指示は「アプリになりすます」必要がある**：コード内の元のコメントに *「ユーザのアプリ端末からの操作のように見せかけないとゲートウェイが指令を無視する」* と明記されている ― そのためECHONETの指令は `nid` に**アプリ機器**のnode IDを用いており、サーバー／DRのnode IDではない（[:172-190, :226](legacy_eminel_docs/sources/conciergesv-develop/src/Command/ControlDrOperationCommand.php#L172-L226)）― GWハードウェア上のworkaroundの1つであり、業務レイヤーにおける意図的な設計ではない。

### 2.6 アプリへの通知 ― 「DR を開始しました」

フェーズの中で1つ以上のEMS-SPへの送信が完了した後、`ConRegularMessages` の**固定id = 8**（`category=DR`、内容は *「DR を開始しました。」*、[ConRegularMessagesSeed.php:115-128](legacy_eminel_docs/sources/eminelsv-develop/config/Seeds/ConRegularMessagesSeed.php#L115-L128)）から `ConMessage` を1件作成し、この実行の中で指令の送信に成功したすべてのEMS-SPへ送る（[:303-325](legacy_eminel_docs/sources/conciergesv-develop/src/Command/ControlDrOperationCommand.php#L303-L325)）― `ConMessages`/`ConMessageDestinations` の仕組みを用いており、`ConEcoMissions`（省エネアドバイスに使用する）とは異なるが、「内容のレコード1件＋n件の宛先」という同じモデルである。

### 2.7 期限切れの指令のクローズ（`finishOperations`）

各フェーズについて、`end_at_N < now` でありながら `SCHEDULED` または `RUNNING` のままであるdestinationを探す（[:332-347](legacy_eminel_docs/sources/conciergesv-develop/src/Command/ControlDrOperationCommand.php#L332-L347)）：

| 変更前の状態 | 変更後の状態 | 意味 |
|---|---|---|
| `SCHEDULED` | `FAILED` | 期限が来るまでに指令を**一度も送信できなかった**（conflict／機器の欠如／継続的なエラーによる） |
| `RUNNING` | `COMPLETE` | `CHANGE_TEMP` の指令の送信に成功しており、終了時刻に達した → 完了とみなす（機器は§2.5で埋め込まれた時刻に従って自ら温度を復帰させるため、バッチが追加の指令を送る必要はない） |

---

## 出典

| 内容 | 根拠 |
|---|---|
| バッチのメインロジック | `legacy_eminel_docs/sources/conciergesv-develop/src/Command/ControlDrOperationCommand.php` |
| cronスケジュール（毎分） | `legacy_eminel_docs/docs/02_詳細設計/10_バッチ処理/mng-webap_cron設定_20241029.txt:77` |
| 2フェーズのDR指令の構造 | `legacy_eminel_docs/sources/eminel_sv_lib-develop/src/Model/Entity/ConDrOperation.php`, `src/Model/Entity/ConDrOperationDestination.php`, `src/Model/Table/ConDrOperationsTable.php` |
| 機器制御の履歴（重複防止） | `legacy_eminel_docs/sources/eminel_sv_lib-develop/src/Model/Entity/ConDeviceControl.php` |
| 「DR を開始しました」通知の内容 | `legacy_eminel_docs/sources/eminelsv-develop/config/Seeds/ConRegularMessagesSeed.php` |
| GWと共用する指令キューのテーブル | `legacy_eminel_docs/sources/eminel_sv_lib-develop/src/Model/Table/InstructionsTable.php`, `legacy_eminel_docs/sources/hemssv-develop/src/Model/Table/InstructionsTable.php` |
| E-GW側の対応する要件 | `eminel_gw_project/docs/eminel/3_requirements/00_integrated_requirements_v1.2.md` ― `[F-ES-07/08] 機器制御DR`、UC-05 01-3 |
