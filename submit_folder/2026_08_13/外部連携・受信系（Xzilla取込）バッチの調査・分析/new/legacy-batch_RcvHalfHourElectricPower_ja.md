# 旧バッチ ― RcvHalfHourElectricPowerCommand（Xzilla 30分電力量データ受信・買電売電時間値算出）

## 概要

`RcvHalfHourElectricPowerCommand`（CLIコマンド`RcvHalfHourElectricPower`、IF1156）は、旧システム（EMINELコンシェルジュサーバー）において、Xzillaから**30分電力量データ**（1計測地点あたり1日48コマ）を受信し、ステージングテーブルへ全削除して再投入し、確定区分フラグ（`fixed_div`）によって**速報（fast）**と**確定（confirm）**に振り分け、さらに速報側から**30分コマを2つずつ合算して24個の時間値とし**、**顧客ごとの買電量／売電量**を算出して`ConSensorHourlyValues`（`s_102`）へ書き込むバッチである――アプリの電力量グラフを直接支えるデータである。先に調査した2つのXzilla受信バッチ（`RcvCntctCancellationCommand`、`RcvEmsPlsCntrPayerCommand`――マスタ／フラグの更新のみ）とは異なり、本バッチは**エンドユーザーに表示される数値そのものを生成し**、**1回の実行で複数のCSVファイルを処理し得る**；詳細は第2部に示す。

## 第1部 ― 概要

| 項目 | 内容 |
|---|---|
| **役割** | Xzillaから30分電力量CSV（IF1156）を受信し、速報／確定に振り分け、顧客ごとの時間別の買電量／売電量を算出する。 |
| **Input** | Xzilla中継サーバー上のCSV（env `XZILLA_RELATION_SERVER_ELECTRIC_POWER_URL`）＋`XzillaRelationLogs`テーブル（重複防止）＋`emn_all_electric_powers`／`emn_fast_electric_powers`（投入直後のデータを同一実行内でそのまま読み直す）＋算出停止フラグ、太陽光発電／コジェネレーションのフラグ、グループ属性情報を取得するための`ConCustomers`（`t_101`）。 |
| **Output** | `emn_all_electric_powers`＋`emn_fast_electric_powers`を全削除して再投入する；`emn_confirm_electric_powers`へは**append**（削除しない）；`ConSensorHourlyValues`（`s_102`、`device_type` 10=売電、11=買電）へinsertする＋`XzillaRelationLogs`へログを記録する。 |
| **処理概要** | 1. 当日のCSVファイルを**すべて**取得する（最新の1件のみではない）；ログにより処理済みのファイルは除外する。<br>2. 各ファイルについて：ダウンロードし、全体テーブルを全削除して再投入し、速報／確定に振り分ける。<br>3. データが存在するすべての顧客について買電量を算出する。<br>4. 売電量を算出する――太陽光発電を持たず（GWが個別に算出する）、かつXzilla連携のコジェネレーション設定を持つ顧客のみが対象である。 |

## 第2部 ― 詳細

### 処理マップ ― トランザクション1つ、当日分のCSVファイルごとにループ

```
ステップ1  ファイル一覧の取得   → 中継ディレクトリを読み、.csv で絞り込む                          §2.1
ステップ2  当日ファイルの選択   → 当日のtimestampを持つファイルを全件保持（1件のみではない）       §2.1
ステップ3  重複処理の防止       → ログ（upload_type=1）が処理中／完了のファイルを除外              §2.2
ステップ4  残った各ファイルについて：
        4a. ダウンロード＆「処理中」ログの記録                                                  §2.3
        4b. emn_all_electric_powers を削除＋再投入（1日48コマの30分値）                         §2.4
        4c. emn_fast_electric_powers を削除＋再投入 ＝ fixed_div が空の行                       §2.5
        4d. emn_confirm_electric_powers へAPPEND ＝ fixed_div='1' の行（削除しない）            §2.5
        4e. 30分コマを2つずつ合算 → 24個の時間値、買電量を算出（device_type 11）                 §2.6-2.7
        4f. 売電量を算出（device_type 10）――条件あり                                           §2.6-2.7
        4g. このファイルについて「完了」ログを記録                                              §2.3
```

| ステップ | 内容 | 詳細 |
|---|---|---|
| 1–3 | 当日のCSVファイルを特定し、ファイルごとに重複処理を防止する | §2.1 · §2.2 |
| 4a | ファイルをダウンロードし、「処理中」ログを記録する | §2.3 |
| 4b–4d | 30分データを投入し、速報／確定に振り分ける | §2.4 · §2.5 |
| 4e–4f | コマを合算して時間値とし、買電／売電を算出する――**2つの算出元条件** | §2.6 · §2.7 |
| ― | `ConSensorHourlyValues`へ書き出すレコードの構造 | §2.8 |

---

### 2.1 処理対象CSVファイルの選択 ― 他の2つのXzillaバッチとの相違点

| 項目 | 内容 |
|---|---|
| ファイルの絞り込み条件 | `.csv`ファイルのみを受け付け、ファイル名末尾14文字のtimestampをキーとする（[:90-100](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvHalfHourElectricPowerCommand.php#L90-L100)） |
| ファイルの選択方法 | 当日の範囲のtimestampを持つファイルを**全件保持**する（`RcvCntctCancellationCommand`/`RcvEmsPlsCntrPayerCommand`のように最初の1件で止めない）――`$todayFileNames[]`は`break`しない（[:107-115](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvHalfHourElectricPowerCommand.php#L107-L115)） |
| ファイルが存在しない場合 | 当日のファイルが1件もない → `commit` + `abort`（[:117-122](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvHalfHourElectricPowerCommand.php#L117-L122)） |

妥当な理由：旧cronは本バッチを10分毎にpollしており（`mng-webap_cron設定_20241029.txt:109-110`）、1日に複数のファイルが存在し得る；Xzillaからの実際の提供周期とフォーマットは移行報告のQA A-3として未確定の懸案である――そのため、バッチ1回の実行で未処理の新規ファイルをすべて拾い切る必要があり、1件のみでは足りない。

### 2.2 重複処理の防止 ― ファイルごとに個別に判定

他の2つのバッチ（1ファイルにつきログを1回引く）とは異なり、本バッチは当日一覧内の**各ファイルについてログを引き**、ログが存在しないファイル、またはログが「処理中」／「完了」（`upload_type=1`）ではないファイルのみを残す（[:124-153](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvHalfHourElectricPowerCommand.php#L124-L153)）。絞り込みの結果ファイルが1件も残らない → `commit` + `abort`（[:155-160](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvHalfHourElectricPowerCommand.php#L155-L160)）。

### 2.3 ファイルのダウンロードとログ記録 ― ファイルごとに繰り返す

残った各ファイルについて：`/var/data/xzilla/IF1156/`へダウンロードし、「処理中」ログ（`upload_type=1`）を記録し、そのファイルの処理が終わった時点で直ちに「完了」ログを記録する――**全ファイルの終了を待ってからログを記録するのではない**（[:163-260](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvHalfHourElectricPowerCommand.php#L163-L260)）。ただし**ファイルのダウンロード**でのエラー → `commit` + `abort`となり、同一実行内でそれ以前に処理を終えたファイルの結果は保持される（[:169-176](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvHalfHourElectricPowerCommand.php#L169-L176)）；「処理中」ログの記録／全削除・再投入／算出のステップ以降でのエラー → **トランザクション全体**を`rollback`し、それ以前に処理を終えたファイルも含めて巻き戻される（`$connection->begin()`は`execute()`の冒頭で1回しか呼ばれないため）。

### 2.4 30分データの投入（`bulkInsert30MinElectricPowerAll`）

`emn_all_electric_powers`を全件削除し（[:189-199](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvHalfHourElectricPowerCommand.php#L189-L199)）、`explode("\n"/",")`でCSVを読み（`fgetcsv`は使用しない）、55カラム（index 0-54）をマッピングする（[:273-351](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvHalfHourElectricPowerCommand.php#L273-L351)）：

| カラム | Field | 意味（migrationのコメントによる） |
|---|---|---|
| `0` | `spl_pw_spt_srno` | EMS‑SP ― `ConCustomers.c001`へ直接joinするキーであり、マッピングテーブルを介さない |
| `1` | `lct_ctgr` | 供給_受電区分 ― migrationのコメントにはカラム名しかない；`calcKaidenBaidenAmount`の`WHERE`条件によれば、値`1`=買電、`2`=売電（[:852-858](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvHalfHourElectricPowerCommand.php#L852-L858)） |
| `2` | `ymd` | 年月日 |
| `3` | `splsptidntno` | 供給地点特定番号 |
| `4` | `pw_spt_srno` | 受電地点特定番号 |
| `5`‑`52` | `kwh_0000_0030`…`kwh_2330_2400` | 1日48個の30分コマ |
| `53` | `fixed_div` | 確定区分 ― 空／NULL＝速報、`1`＝確定 |
| `54` | `dwh_updatetime` | ソースDWH側の更新時刻 |

ロット単位のbulk insert――**`RcvEmsPlsCntrPayerCommand`で見られたものと同じoff‑by‑oneの誤り**：`$query->values()`が`$splitCount==10`の判定より先に実行されるため、1ロットは実際には**11レコード**であり、コメントにある10ではない（[:412-435](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvHalfHourElectricPowerCommand.php#L412-L435)）。

### 2.5 速報／確定への振り分け ― 1つのテーブルは削除されない

| テーブル | 実行ごとの挙動 | データ取得条件 |
|---|---|---|
| `emn_fast_electric_powers` | **全件削除してから再投入**（[:210-220](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvHalfHourElectricPowerCommand.php#L210-L220)） | `fixed_div IS NULL OR fixed_div = ''` ― 速報データ（[:452, :570](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvHalfHourElectricPowerCommand.php#L570)） |
| `emn_confirm_electric_powers` | 実行ごとに**削除せず、APPENDのみ** | `fixed_div = '1'` ― 確定データ（[:594, :712](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvHalfHourElectricPowerCommand.php#L594-L712)） |

いずれも`INSERT INTO ... SELECT ... FROM emn_all_electric_powers`によりinsertする（SQL 1文であり、行ごとのループはない）。

### 2.6 30分コマの合算 → 時間値

`calcKaidenBaidenAmount`では、隣接する30分コマの各ペアがSELECT文の中でそのまま合算されて1つの時間コマとなり、2つのコマのいずれかがNULLであれば結果はNULLとなる（算出しない）（[:776-848](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvHalfHourElectricPowerCommand.php#L776-L848)）：

```text
kwh_HHOO_HH+1_OO = kwh_HH00_HH30 + kwh_HH30_HH+1_00
(2つのコマのいずれかがNULLの場合はNULL)
```

データソースは常に**`emn_fast_electric_powers`**（速報）である――`emn_confirm_electric_powers`（確定）のデータは§2.5で保存されるが、この算出ステップでは**再利用されない**。

### 2.7 買電量／売電量の算出条件

`emn_fast_electric_powers`と`ConCustomers`を`spl_pw_spt_srno = c001`でjoinし、**未削除**（`c052 IS NULL`）かつ**算出停止されていない**（`c065 = 0` ― 契約終了時に`RcvEmsPlsCntrPayerCommand`/`RcvCntctCancellationCommand`がセットするフラグ）顧客のみを対象とする（[:849-860](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvHalfHourElectricPowerCommand.php#L849-L860)）。

**売電量**の算出元を決定する2つの条件（[:876-882](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvHalfHourElectricPowerCommand.php#L876-L882)）：

| 条件 | 値 | 意味 |
|---|---|---|
| `calcFromGw` | `has_solar_cell (c034) == 1` | 太陽光発電を持つ顧客 → GW/HEMSが自ら計測済みであり、売電量は別の**日次**バッチが算出するため、本バッチは対象外とする |
| `calcFromXzilla` | `!has_solar_cell && gas_cogeneration (c024)==1 && juden_point_number (c064)`が空でない | コジェネレーション／燃料電池を持つ顧客（太陽光発電なし） → 売電量の数値はXzillaにしか存在しない |

| 算出対象 | ケース | 挙動 |
|---|---|---|
| 買電（`11`） | 条件なしで常に算出する | コマを合算し、`device_type=11`で書き込む |
| 買電（`11`） | `calcFromGw`でも`calcFromXzilla`でも**ない**場合 | 売電量＝`0`のレコード（`device_type=10`）を**追加で**書き込む――他のどのソースからも算出され得ないことが確実であるため（[:891-963](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvHalfHourElectricPowerCommand.php#L891-L963)） |
| 売電（`10`） | `calcFromGw` | 完全にスキップする――算出も書き込みも一切行わない（0すら書かない）（[:884-887](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvHalfHourElectricPowerCommand.php#L884-L887)） |
| 売電（`10`） | `calcFromXzilla` | コマを合算し、`device_type=10`で書き込む |
| 売電（`10`） | `calcFromGw`でも`calcFromXzilla`でもない | 何も書き込まない――買電のケースとは**異なり**、ここには`0`を補って書き込むステップがない（[:1036-1039](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvHalfHourElectricPowerCommand.php#L1036-L1039)） |

### 2.8 `ConSensorHourlyValues`（`s_102`）へ書き出すレコード

| カラム | エンティティ定数 | 値のソース |
|---|---|---|
| `c001` | `C_EMS_SP` | `spl_pw_spt_srno` |
| `c002` | `C_DEVICE_TYPE` | `11`=買電 または `10`=売電 |
| `c003` | `C_ROOM_ID` | 常に`0` |
| `c004` | `C_DATE` | `ymd` |
| `c008`/`c009` | `C_NEED_ELE_COMPLETE_FLAG`/`C_NEED_AGG_COMPLETE_FLAG` | 常に`2` |
| `c111`‑`c115` | `C_GROUP_ATTR_1..5` | 顧客の`c012`(建物種別)/`c042`(暖房熱源)/`c015`(床面積)/`c016`(家族人数)/`c024`(gas_cogeneration) |
| `c011`‑`c034` | `C_VALUE_0..23` | §2.6で合算した24個の時間値、または`'0'`（§2.7の補填ケース） |
| `c041` | `C_MODIFIED` | バッチの実行時刻 |

本テーブルの主キーは**`(c001, c002, c003, c004)`**である（[ConSensorHourlyValuesTable.php:41-43](e:/Projects/mui/legacy_eminel_docs-main/sources/eminel_sv_lib-develop/src/Model/Table/ConSensorHourlyValuesTable.php#L41-L43)）。

### ⚠️ 旧システムにおける注意点

**① 新規エンティティによるinsertであり、upsertではない――主キー違反を起こし得る。** 各レコードは`newEmptyEntity()`で生成してから`save()`する（[:896, :969](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvHalfHourElectricPowerCommand.php#L969)）――事前に主キーで既存レコードを引くことはしない。同一日内に同じ`(ems_sp, device_type, room=0, date)`に対してバッチが2回実行された場合（本バッチは**1日に複数のファイル**を処理するため十分に起こり得る――§2.1）、2回目の書き込みは主キー違反となり、`catch`で捕捉され（[:1041-1044](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvHalfHourElectricPowerCommand.php#L1041-L1044)）、**その実行のトランザクション全体**が`rollback`される――同一実行内でそれ以前に処理を終えた他のCSVファイルも含めてである（§2.3）。

**② `emn_confirm_electric_powers`は無限に蓄積する。** CSVに関連する3つのテーブルのうち、実行ごとに`deleteAll`されない唯一のテーブルである――一方で`emn_all`/`emn_fast`は常に全件を削除して再投入する。この確報データは`CalcFixedValueCommand`（固定値計算 ― 手動実行の再集計）が読み直す（[CalcFixedValueCommand.php:203, :252](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/CalcFixedValueCommand.php#L203)）――蓄積は`ymd`単位で確報の履歴を残すという意図によるものだが、purgeが存在しないため、移植の際には保持期間/TTLの方針を併せて定める必要がある（new_2 §6.3 ステップ3、SVC-03に一致）。

**③ 売電量算出時の非対称性。** 売電量の算出条件を満たさない顧客について：**買電量**の算出回であれば`0`が補われて書き込まれるが、**売電量**の算出回であれば何も書き込まれない（§2.7）――業務上は同一の状況でありながら、どちらの関数呼び出しが先に到達するかによって2つの異なる結果になる。

---

## 出典

| 内容 | 根拠 |
|---|---|
| バッチのメインロジック | `sources/conciergesv-develop/src/Command/RcvHalfHourElectricPowerCommand.php` |
| `emn_all_electric_powers`の構造＋カラムコメント | `sources/eminelsv-develop/config/Migrations/20240409095924_CreateElectricPowerAll.php` |
| `emn_fast_electric_powers` / `emn_confirm_electric_powers`テーブルの構造 | `sources/eminelsv-develop/config/Migrations/20240410002142_CreateElectricPowerFast.php` / `20240410003631_CreateElectricPowerConfirm.php` |
| `ConSensorHourlyValues`（`s_102`）のテーブル＋カラム定数 | `sources/eminel_sv_lib-develop/src/Model/Table/ConSensorHourlyValuesTable.php`, `src/Model/Entity/ConSensorHourlyValue.php` |
| `ConCustomers`（`t_101`）のカラム名＋定数 | `sources/eminel_sv_lib-develop/src/Model/Entity/ConCustomer.php` |
| 関連バッチ（共用の`c065`フラグ） | `investigate/eminel-gw/legacy-batch_RcvCntctCancellation.md`, `investigate/eminel-gw/legacy-batch_RcvEmsPlsCntrPayer.md` |
