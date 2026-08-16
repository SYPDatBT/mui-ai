# DeleteLogicalDeletedDevicesCommand（論理削除済みデバイス削除）

## 概要

`DeleteLogicalDeletedDevicesCommand` は、旧システムの `conciergesv` において**毎日05:15にcron実行されるバッチ**（`DeleteData` とラッパーシェルを共用）であるが、操作の対象は3サーバーすべてで共用されるHEMSドメインの基幹テーブル（`Devices`/`DeviceDatas`/`ErrorDeviceDatas`/`Instructions`）である：**ソフトデリート**された機器（`delete_flg=true` ― GWが機器はもう存在しないと報告した際に `hemssv` のAPI `NotifyDeviceListController` が設定する）のうち、ソフトデリートから30日を超えたものを抽出し、関連する計測データ／エラーデータ／制御指令のすべてと当該機器のレコード自体を、1つのトランザクションの中で**ハードデリート**（物理削除）する。これはIoT機器の取り外しライフサイクルにおいて、30日間の猶予期間（grace period）の後に行われる「本当の掃除」のステップである。新リポジトリ `syp-eminelstandard-backend` において、本バッチは**「本質的に別の仕組みへの置き換え」**に該当する ― 両面ともにそうである：(1) 機器テーブル（`DeviceTable`、`MuiDeviceTable`）には `delete_flg` に相当するソフトデリートフラグが一切ない。「ソース側に存在しなくなった機器を取り外す」という概念は、同期して即削除する形で存在する ― 機器一覧APIがDBとメーカーサーバー（RINNAI/NORITZ/DAIKIN）を突き合わせ、一覧に存在しなくなったレコードを即Deleteする（`get-list-remote-control-device.ts:199-222`）。(2) 新システムでの機器削除は複数の経路（ユーザーによるAPI呼び出し、一覧の同期、メーカー連携の解除、会員資格の喪失／ガス契約の終了時に動く定期バッチ `batch-remove-integration-expired`）で即ハードデリートされ、ソフトデリート＋30日の猶予期間を経る仕組みは一切ない。新アーキテクチャに存在しないのは、「GWから消失の報告を受けた時点で機器をソフトデリートし、30日待ってから完全に削除する」という業務概念（猶予期間＋機器ごとの定期クリーンアップバッチ）だけである。

---

# 第A部 ― 旧システム

## A.1 全体概要

| 項目 | 内容 |
|---|---|
| **バッチ名** | クラス：`DeleteLogicalDeletedDevicesCommand`（`BaseCommand` ではなく `Command` を直接 extends）・実際の呼び出しコマンド名：`DeleteLogicalDeletedDevices` *（本番のラッパースクリプト `12_CreateCsvAndDeleteData_day1.sh:35` による）*・**毎日05:15のcron**（`mng-webap_cron設定_20241029.txt:39-41` ― cronは `eminel-mng-webap.20240909.tgz` 内のラッパー `12_CreateCsvAndDeleteData_day1.sh`／`day2to31.sh` を呼び出し、ラッパーの内部で `DeleteData` の直後に本バッチを呼び出している。バッチ名はスクリプトの内部にしか現れないため、2つのcron設定 `.txt` ファイルを直接grepしても見つからない）。 |
| **役割** | 世帯から取り外された（ずっと以前にソフトデリートされた）機器のデータを物理的に掃除する ― 3サーバー間で共用されるテーブルに「幽霊機器」のレコードが無限に滞留することを避けるため。 |
| **入力** | `Devices` テーブルを読み取る ― `delete_flg=true` AND `update_datetime < (--datetime − 30日)` で絞り込む。コマンドライン引数 `--datetime`（デフォルトは `now`）。 |
| **出力** | 4つのテーブルに対する物理`DELETE`：`DeviceDatas`、`ErrorDeviceDatas`、`Instructions`（機器ごと）、その後 `Devices`（本体レコード）。新規データの書き込みは行わない。 |
| **処理概要** | 1. `--datetime` から30日を引いた基準時点 `keepDays` を算出する。<br>2. その基準時点より前にソフトデリートされた機器をすべて抽出する。<br>3. リスト全体に対してトランザクションを1つだけ開始する。<br>4. 各機器について：関連する `DeviceDatas`、`ErrorDeviceDatas`、`Instructions`（`ems_sp_no`＋`node_id`＋`eoj` による）を削除し、その後 `Devices` の本体レコードを削除する。<br>5. 1台の機器で `Devices` の削除に失敗した場合→トランザクション全体をロールバックし（同じ実行の中でそれ以前に削除に成功した機器も含む）、直ちに停止する。そうでなければ→リストをすべて処理し終えた後にコミットする。 |

## A.2 詳細

### A.2.1 抽出条件と `delete_flg` の発生元

| 項目 | 内容 | 出典 |
|---|---|---|
| 削除対象機器の抽出条件 | `delete_flg = true` AND `update_datetime < (--datetime − 30日)` | `DeleteLogicalDeletedDevicesCommand.php:64-71` |
| 機器1台の識別 | `ems_sp_no`（世帯／EMS-SPのコード）＋ `node_id` ＋ `eoj`（ECHONET Lite Object ― 機器種別コード）の組み合わせ | `Entity/Device.php:11-13` |
| `delete_flg=true` の発生元 | **hemssv**（conciergesvではない）のAPI `NotifyDeviceListController` ― GWが現存する機器の一覧を報告した際、DBに保存済みの機器がGWの報告した一覧に現れなくなっていれば→`Devices->updateAll(['delete_flg'=>true,'update_datetime'=>now], ...)`。`DeviceDatas` も同様にソフトデリートされる（ただし独立しており、専用の `delete_flg` を持つ ― 本バッチは `DeviceDatas` 側のこのフラグを再確認せず、機器のキーによってそのままハードデリートする）。 | `sources/hemssv-develop/src/Controller/NotifyDeviceListController.php:661-666,676-679` |
| 共用の範囲 | 4つのテーブル（`Devices`,`DeviceDatas`,`ErrorDeviceDatas`,`Instructions`）はいずれも、3サーバーすべて（`hemssv`,`eminelsv`,`conciergesv` ＋ lib ― grepによる実測）にまたがる他の24個のコードファイル（本バッチを含めて25個の .php ファイル、＋ README 1個）から読み書きされている ― これらがシステム全体で共用されるHEMSドメインの中核データであり、`conciergesv` 固有のものではないことを裏付けている。 | grep `EminelSvLib.(Devices\|DeviceDatas\|ErrorDeviceDatas\|Instructions)` を `sources/` に対して実行 |

### A.2.2 機器ごとの関連データ削除

A.2.1の条件に合致する各機器について（逐次ループであり、バッチ／バルク処理ではない）：

1. `DeviceDatas->deleteAll(['ems_sp_no'=>..., 'node_id'=>..., 'eoj'=>...])` ― 機器の最新の計測／状態データ（`latest_node_operating_state`、`latest_device_fault_content`,...）を削除する。（`Entity/DeviceData.php:14-24`）
2. `ErrorDeviceDatas->deleteAll([同じ条件])` ― 機器のエラー履歴を削除する。
3. `Instructions->deleteAll([同じ条件])` ― GWが取りに来るのを待っている制御／ポーリングの指令を削除する（機器が取り外された以上、その機器に対する古い指令はもはや意味を持たない）。（`Entity/Instruction.php:11-19`）
4. `Devices->delete($device)` ― 機器の本体レコードを削除する。結果が確認されるのはこのステップのみ（`if`/`else`）であり、先行する3つの削除ステップは影響行数も個別のエラーも確認していない。

出典：`DeleteLogicalDeletedDevicesCommand.php:73-103`。

### A.2.3 トランザクションとエラー処理

- 機器のリスト全体（複数の機器／複数の異なる世帯にまたがりうる）が**1つのトランザクション**の中で実行される。トランザクションは `deleteInstructions()` 関数の冒頭で開始され、ループがすべて完了した後に末尾でコミットされる。（`:60-62,104`）
- リスト内のいずれかの機器で `Devices->delete($device)` が `false`（削除失敗）を返した場合：`alert` ログを出力し、`rollback()` して直ちに `return` する ― トランザクション内の変更をすべて破棄する。**同じ実行の中で、それ以前のループですでに削除に成功した機器も含めてである**。（`:96-102`）
- `deleteAll`／`delete` の各命令を囲むtry/catchは存在しない ― 3つの `deleteAll` ステップ（A.2.2のステップ1〜3）のいずれかが例外を投げた場合（例：接続エラー、外部キー制約）、その例外はここで捕捉されず、そのまま `execute()` の外へ投げられる ― トランザクションはコード上で明示的に `rollback()` されない（例外により接続が突然閉じられた際にCakePHP／PostgreSQLがトランザクションを自動的に破棄する可能性はあるが、それはフレームワーク／DBの挙動であり、本リポジトリ内で直接確認することはできない）。

### A.2.4 特記事項／リスク

- **毎日05:15にcron実行されるバッチ**であり、`DeleteDataCommand` と同じ `#12.DBデータ削除` のグループに属する（ラッパーも同一）。cronはバッチを直接呼び出さず、ラッパーシェル `12_CreateCsvAndDeleteData_day1.sh`（1日）／`day2to31.sh`（毎日）を呼び出す ― ラッパーの内部ではCSV／削除の各バッチを順に実行し、`DeleteData` の直後に本バッチが実行される（`day1.sh:35`、`day2to31.sh:29`）。
- **機器1台のエラーで全体をロールバックする**（A.2.3参照） ― リストにN台の機器があり、K番目の機器で削除エラーが発生した場合、それ以前に削除に成功したN-1台も一緒に破棄され、次回の実行でリスト全体を最初からやり直すことになる（「処理できた分だけ残す」という仕組みはなく、機器ごとに個別のトランザクションを張る方式でもない）。
- `BaseCommand` を extends していない → 多重起動を防ぐPIDロックの仕組みがない（`DeleteData.md` での指摘と同様）。ラッパー側には多重起動を防ぐ `flock -n` があるが（`day1.sh:4-9`）、スクリプトファイルごとにしか効かない。1日には `day1` と `day2to31` の両方が05:15に設定されており（cron `:40-41`）、flockは異なる2つのスクリプトファイルの間では相互に効かないため ― 2つのプロセスが同じ時点で本バッチを同時に実行する可能性がある。
- `Devices` を削除する前に3つの子テーブルを削除する（`Devices` を先に削除してcascadeさせる方式ではない） ― 3つの子テーブルから `Devices` へのFK制約が存在する場合に外部キー制約違反を避けられるという意味で、この順序は妥当である。ただし、読んだ範囲のTableクラスにFKの明示的な宣言は見当たらなかった。

---

# 第B部 ― EMINEL-smart（新システム）との対照

> そのままの形（ソフトデリート＋30日の猶予期間）で対応するLambdaや仕組みは存在しない。「ソース側に存在しなくなった機器を取り外す」機能は、本質的に別の仕組みへ置き換えられている。以下の表は、調査した領域／候補／削除の経路と、その一致度である（B.1／B.2に代えて示す）。

## 確認済み

| 領域／候補 | 一致しない理由 |
|---|---|
| `DeviceTable`（`template-dynamodb.yaml:525-548`、モデル `src/layers/common/nodejs/models/Device.ts`） | `is_deleted`／`delete_flag`／`deleted_at` のようなフィールドは1つも存在しない。意味的に最も近いフィールドは `error_flag` であるが、これは機器のエラーを示すフラグであり、「家から取り外された」ことを示すフラグではない。 |
| `MuiDeviceTable`（`template-dynamodb.yaml:1495-1511`、モデル `src/layers/common/nodejs/models/MuiDevice.ts`） | こちらにも `delete_flg`／`deleted_at` は存在しない。`availability`（赤外線リモコン制御に対する即時の利用可否）はあるが、「GWから恒久的に取り外されたと報告された」という性質とは異なる。 |
| `src/` 全体に対する `NotifyDeviceList`／`delete_flg` のgrep | 0件 ― `NotifyDeviceListController` に相当する、ソフトデリートのマークだけを行うAPIは存在しない。「ソース側に存在しなくなった機器」の検知は、すぐ下の行にある同期の経路にある（マークせず即削除する）。 |
| `src/functions/api-device/get-list-remote-control-device.ts:199-222` | 業務の本質という点で最も近い候補（トリガー：同期）：機器一覧APIが呼ばれた際にDBとメーカーサーバー（RINNAI/NORITZ/DAIKIN）の一覧を突き合わせ、一覧に存在しなくなった機器は `DeviceTable` のレコードを即 `Delete` する。相違点：ソフトデリートを経ずに即削除する、30日の猶予期間がない、定期バッチではなくAPI呼び出しのたびに実行される。 |
| `src/functions/api-device/delete-sensor.ts:54-121` | ユーザーが能動的に行う削除の経路の1つ（トリガー：user）：`MuiSensor` ＋ 配下の `MuiDevice` を1つのトランザクションで削除し、ソフトデリート＋猶予期間を経ずに即ハードデリートする。`DeviceDatas`／`ErrorDeviceDatas`／`Instructions` に相当する計測データ／エラーデータ／保留中の指令は削除しない（新システムの計測データは、すでにTTLが設定された別のテーブル ― `DeviceMonthlyUsageHistoryTable`,... ― を用いており、機器ごとに手動で掃除する必要がない）。 |
| `src/functions/api-device/delete-infrared-remote.ts:40-56` | ユーザーによる赤外線リモコンの削除の経路（トリガー：user）：`MuiDevice` を即ハードデリートしたうえで `infraredRemoteService.removeConnectedDevice` を呼び出し、外部サービスがエラーになった場合はロールバック（再Put）する。 |
| メーカー連携の解除／アカウントのリセット／会員のインポート（`api-integration/get-access-token-integration.ts:292,317`、`batch-reset-account/app.ts:275-284`、`batch-if2241-import-tagtag-kaiin/app.ts:902-909`） | アカウント／連携のイベントに応じて `DeviceTable` のレコードを削除する経路（トリガー：連携の終了／アカウントのリセット／会員の変更） ― 即ハードデリートするものであり、機器ごとのライフサイクルに従うものではない。 |
| `src/functions/batch-remove-integration-expired`（`app.ts:44-53,92` → `get-transaction-reset-integration.ts:145-176`） | ユーザーが会員資格を喪失した場合、またはガス契約が終了した場合に、機器レコードと機器のエラーデータ（`TABLE_DEVICE`＋`TABLE_DEVICE_ERROR` ― 旧システムの `Devices`＋`ErrorDeviceDatas` の組に相当）をハードデリートする定期バッチ ― すなわち契約／連携のライフサイクルに従った削除であり、旧バッチのような機器ごとのライフサイクルに従ったものではない。 |
| `DeviceTable`／`MuiDeviceTable` 上の `TimeToLiveSpecification` | 存在しない ― この2つのテーブルは `template-dynamodb.yaml` のいずれのTTLブロックにも含まれていない（すでにTTLが設定されている使用量履歴系のテーブルとは異なる。`DeleteData.md` を参照）。 |
| `src/functions/` 内の81個の `batch-*` ディレクトリ | 「delete-device」／「hard-delete」／「device-cleanup」／「purge-device」／「delete-logical」に関連する名前は1つもない ― ただし内容で見ると、`batch-remove-integration-expired`（上の行）が機器レコードのハードデリートを行っている。 |

---

## まとめ

1対1の対応は存在しない ― 旧システム側は単純な処理フローが1本あるだけであり（分岐や並列アルゴリズムはない）、新システムにおいて本バッチは**「本質的に別の仕組みへの置き換え」**に該当する：「ソース側に存在しなくなった機器を取り外す」という概念は、一覧API（`get-list-remote-control-device`）を呼び出した際に同期して即削除する形で存在し、加えて契約／連携のライフサイクルに従う削除の経路（`batch-remove-integration-expired`,...）がある ― 第B部の「確認済み」の表に、経路ごとの内容と一致度を示した。注目すべき点：新アーキテクチャに存在しないのは機器の削除そのものではなく、「GWから接続断の報告を受けた時点でソフトデリートし、30日間の猶予期間を置いてから完全に削除する」というライフサイクルの方針である ― `DeleteData.md` で `ConEcoPoints` について記録したギャップと同種のものである（データはあるがライフサイクルの方針が欠けている。本件では削除はいずれも存在するものの即時削除であり、猶予期間が欠けている）。

---

## 出典

| 区分 | 内容 | 根拠 |
|---|---|---|
| 旧システム | メインロジック | `sources/conciergesv-develop/src/Command/DeleteLogicalDeletedDevicesCommand.php` |
| 旧システム | `Device` のカラムの意味 | `sources/eminel_sv_lib-develop/src/Model/Entity/Device.php:11-24` |
| 旧システム | `DeviceData` のカラムの意味 | `sources/eminel_sv_lib-develop/src/Model/Entity/DeviceData.php:11-24` |
| 旧システム | `Instruction` のカラムの意味 | `sources/eminel_sv_lib-develop/src/Model/Entity/Instruction.php:11-19` |
| 旧システム | `delete_flg=true` の発生元（別サーバーのAPI） | `sources/hemssv-develop/src/Controller/NotifyDeviceListController.php:661-666,676-679` |
| 旧システム | 3サーバーでの共用範囲（実測） | grep `EminelSvLib.(Devices\|DeviceDatas\|ErrorDeviceDatas\|Instructions)` を `sources/` に対して実行 ― 25個の .php ファイル（本バッチを含む）＋ README 1個 |
| 旧システム | 毎日05:15のcron（ラッパースクリプト経由） | `docs/02_詳細設計/10_バッチ処理/mng-webap_cron設定_20241029.txt:39-41` ＋ `cron実行用シェルスクリプト/eminel-mng-webap.20240909.tgz` → `12_CreateCsvAndDeleteData_day1.sh:35`、`day2to31.sh:29` |
| 旧システム | バッチ一覧（日本語の説明、サーバーのグループ） | `docs/03_API仕様/04_バッチ一覧.md:77` |
| 新システム | 機器テーブル（ソフトデリートフラグがないことを確認） | `template-dynamodb.yaml:525-548`（`DeviceTable`）、`src/layers/common/nodejs/models/Device.ts` |
| 新システム | MUI機器テーブル（ソフトデリートフラグがないことを確認） | `template-dynamodb.yaml:1495-1511`（`MuiDeviceTable`）、`src/layers/common/nodejs/models/MuiDevice.ts` |
| 新システム | 機器削除の各経路（ソフトデリートを経ず即ハードデリート） | `src/functions/api-device/get-list-remote-control-device.ts:199-222`、`delete-sensor.ts:54-121`、`delete-infrared-remote.ts:40-56`、`api-integration/get-access-token-integration.ts:292,317`、`batch-reset-account/app.ts:275-284`、`batch-remove-integration-expired/app.ts:44-53` |
| 新システム | TTLを持つテーブルとの対照（`DeviceTable`／`MuiDeviceTable` にはないことを示すため） | `docs/legacy-batch-review/DeleteData.md` |
