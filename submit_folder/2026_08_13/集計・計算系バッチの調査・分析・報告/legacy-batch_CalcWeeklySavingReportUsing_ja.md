# 旧バッチ ― CalcWeeklySavingReportUsingCommand（ガス・電気週間使用量算出機能）

## 概要

`CalcWeeklySavingReportUsingCommand` は、旧システム（EMINEL コンシェルジュサーバー）において**週1回（日曜日）**実行されるバッチで、月次センサーデータから積み上げて**世帯が直近7日間に使用したガス使用量・電気使用量の合計**を算出する（週単位で直接計測するメーターが存在しないため）。同時に、前回実行時に算出した「先週」の値を今回実行分の「先々週」として"シフト"し、新しいレポート行が比較対象として2時点分のデータを持てるようにする。本バッチはDBの読み書きのみを行い（メール送信・ファイル出力なし）、結果は`s_105`テーブルに書き込まれる ― これは並走バッチ`CalcWeeklySavingReportEffectCommand`（ガス節約金額を算出、20分後に実行）と同じテーブルである。計算式・SQL文・DB書き込み処理の詳細は第2部に記載する。

## 第1部 ― 概要

| 項目 | 内容 |
|---|---|
| **役割** | 世帯にはガス・電気を週単位で計測するメーターが存在しないため、**日次センサーデータ（月次に集約済み）から積み上げる**ことで直近7日間のガス使用量・電気使用量の合計を算出する。同時に、直近のレポート行（前回実行分）の「先週」の値を新しいレポート行の「先々週」として引き継ぐ。これは、実行のたびに直近1週間分のみを再計算し、過去分は再計算しないためである。 |
| **Input** | DB読み取りのみで、**外部API呼び出し・CSVファイル読み込みは行わない**：`t_101`（世帯一覧。論理削除されていない世帯を絞り込むために使用）＋`s_103`（月次センサーデータ。集約済み ― 算出日から遡って7日間分のガス／電気使用量合計を取得）＋`s_105`（書き込み先テーブル自身 ― 算出日より前の直近レポート行を読み取り、「先週」の値を「先々週」として引き継ぐ）＋時間別センサーテーブル（エンティティ`ConSensorHourlyValue`。ガスデータの欠損有無を確認するために使用）。 |
| **Output** | **DB書き込みのみ** ― 実行のたびに、算出結果に含まれる各世帯について、`s_105`（エンティティ`ConWeeklyEcoReport`、共通ライブラリ`EminelSvLib`経由）に1行をINSERT/UPDATE（upsert）する。設定するのは「使用ガス量／電気量」に関連するカラムのみ（並走バッチ`CalcWeeklySavingReportEffectCommand`が担当するカラムは`dirty=false`に設定 ― 触れない）。メール送信・CSV出力は行わない。 |
| **処理概要** | 1. 「算出日」（`calcDate` ― 入力パラメータ、未指定時は現在日）を決定する。<br>2. `s_103`を検索し、`calcDate`から遡って7日間分のガス使用量合計（device_type=2）と電気使用量合計（device_type=5）を世帯ごとに取得する（実際にデータが存在する日数も併せて取得）。<br>3. `s_105`を検索し、各世帯の直近レポート行（先週分）を取得し、その行の「先週のガス／電気使用量」を、これから書き込む行の「先々週のガス／電気使用量」に変換する。<br>4. 各世帯について：ガスデータが7日分揃っており、かつ時間データの欠損がない場合（時間別センサーテーブルの`calcDate`前日23時のデータで追加チェック）→ 先週のガス使用量（丸め処理）＋表示用の値を算出する。電気についても同様（ただし時間チェックのステップはなし）。条件を満たさない場合はnullとする。<br>5. 世帯ごとに1行を`s_105`へINSERT/UPDATE（並走バッチが担当するカラムはそのまま維持）。これらすべてをバッチ全体で1つのトランザクションとして実行する。 |

## 第2部 ― 詳細

### 2.1 実行スケジュール・パラメータ

| 項目 | 内容 | 出典 |
|---|---|---|
| 実行スケジュール（cron） | `30 4 * * 7` ― 週1回、日曜日04:30 | `docs/02_詳細設計/10_バッチ処理/mng-webap_cron設定_20241029.txt:70-71`（`#21.ガス・電気週間使用量算出機能` → `21_CalcWeeklySavingReportUsing.sh`） |
| 実行コマンド | `php cake.php CalcWeeklySavingReportUsing [算出日]`（パラメータは`yyyy-MM-dd`形式） | `CalcWeeklySavingReportUsingCommand.php:21-23` |
| 「算出日」（`calcDate`、パラメータ未指定時） | 現在日、`yyyy/MM/dd`形式 | `CalcWeeklySavingReportUsingCommand.php:58-64` |
| 並走バッチ | `CalcWeeklySavingReportEffectCommand` ― 同日、20分後（`04:50`）に実行され、ガス節約金額を算出し、**同じ`s_105`テーブルの同じ行**（`ems_sp`＋日付で一致）に書き込む | `mng-webap_cron設定_20241029.txt:73-74`、`CalcWeeklySavingReportEffectCommand.php` |

### 2.2 データ取得SQL

**SQL 1 ― `calcDate`から遡って7日間のガス使用量合計（device_type = 2）:**

```sql
SELECT sensor.ems_sp
     , SUM(sensor.month_target_day) AS gas_using
     , COUNT(sensor.month_target_day) AS gas_using_day
  FROM (
        SELECT month_sensor.c001 AS ems_sp
             , base_date.target_ym
             , base_date.target_day
             , CASE
                 WHEN base_date.target_day = '01' THEN month_sensor.c011
                 WHEN base_date.target_day = '02' THEN month_sensor.c012
                 ...                                              -- 31日分繰り返し、カラムc011~c041
                 ELSE null END AS month_target_day
          FROM s_103 AS month_sensor                              -- 月次センサーデータ（集約済み）
            INNER JOIN (
                SELECT date_trunc('month', :calcDate - serial_number 日) AS target_ym
                     , (:calcDate - serial_number 日) の日にち AS target_day
                  FROM generate_series(1, 7) AS serial_number       -- calcDateから遡って7日間
            ) AS base_date
              ON base_date.target_ym = month_sensor.c004
            LEFT JOIN t_101 AS customer
              ON customer.c001 = month_sensor.c001
         WHERE customer.c052 IS NULL                                -- 論理削除されていない世帯
           AND month_sensor.c002 = 2                                -- device_type = 2（ガス）
  ) AS sensor
 GROUP BY sensor.ems_sp
```
出典: `CalcWeeklySavingReportUsingCommand.php:71-105`（読みやすさのため31日分の`CASE`は省略済み）。

**SQL 2 ― `calcDate`から遡って7日間の電気使用量合計（device_type = 5）:** 構造はSQL 1と全く同じで、条件`month_sensor.c002 = 5`（電気）のみが異なる。出典: `CalcWeeklySavingReportUsingCommand.php:129-163`。

**SQL 3 ― `s_105`から直近レポート行（先週分）を取得:**

```sql
SELECT weekly_energy.c001 AS ems_sp
     , weekly_energy.c011 AS last_week_gas
     , weekly_energy.c012 AS last_week_elec
     , weekly_energy.c021 AS last_week_gas_disp
     , weekly_energy.c022 AS last_week_elec_disp
  FROM s_105 AS weekly_energy
      LEFT JOIN t_101 AS customer
        ON customer.c001 = weekly_energy.c001
 WHERE customer.c052 IS NULL
   AND weekly_energy.c002 = (
           SELECT MAX(weekly_energy_sub.c002)
             FROM s_105 AS weekly_energy_sub
                 LEFT JOIN t_101 AS customer_sub
                   ON customer_sub.c001 = weekly_energy_sub.c001
            WHERE customer_sub.c052 IS NULL
              AND weekly_energy_sub.c002 < :calcDate               -- 算出日より前の直近行
       )
```
出典: `CalcWeeklySavingReportUsingCommand.php:187-210`。

**3つのSQLで使用するカラムの意味:**

| テーブル | カラム | 意味 | 備考 |
|---|---|---|---|
| `t_101` | `c001` | 世帯コード（EMS-SP） | 結合キー |
| `t_101` | `c052` | 論理削除日時 | `IS NULL` = 有効な世帯 |
| `s_103` | `c001` | 世帯コード | 結合キー |
| `s_103` | `c002` | 機器種別／データ種別 | `2` = ガス使用量、`5` = 電気使用量 |
| `s_103` | `c004` | データの年月 | 取得対象の7日間を含む月で結合 |
| `s_103` | `c011`〜`c041` | 月内各日の値（1日〜31日） | `target_day`に応じて`CASE`で該当日のカラムを選択 |
| `s_105` | `c001` | 世帯コード | 結合キー |
| `s_105` | `c002` | 算出日（`c001`とともに主キー） | `calcDate`より前の直近行を探すために使用 |
| `s_105` | `c011` / `c012` | 先週使用したガス量／電気量（当該行の値） | 新しい行では「先々週」の値になる |
| `s_105` | `c021` / `c022` | 先週使用したガス量／電気量 ― 表示用の値（当該行の値） | 新しい行では「先々週」（表示用の値）になる |

### 2.3 計算式（世帯ごと）

**① 「先週」→「先々週」へのシフト**（SQL 3に該当するすべての世帯に適用）:
```
gas_using_week_before_last          = last_week_gas       （空でなければ、そうでなければnull）
electric_using_week_before_last     = last_week_elec       （空でなければ、そうでなければnull）
gas_using_week_before_last_disp     = last_week_gas_disp   （空でなければ、そうでなければnull）
electric_using_week_before_last_disp= last_week_elec_disp  （空でなければ、そうでなければnull）
```

**② 「先週使用したガス量」の算出**（世帯ごと、SQL 1の結果に基づく）:
```
① 時間別センサーテーブル（ConSensorHourlyValue）から、device_type=2、room_id=0、
   calcDate前日の23時台のレコードを取得する（データ欠損を検知するために使用 ―
   日中の時間帯のデータは補間・穴埋めされている可能性があるためチェックには使用しない）
② gas_using_day ≠ 7  または  ①のステップの時間レコードが空の場合
      → gas_using_last_week = null、gas_using_last_week_disp = null
   それ以外の場合：
      gas_using_last_week = floor(gas_using × 100) / 100   （gas_using > 0の場合。そうでなければnull）
      gas_usingが空、または0未満、または999超の場合
          → gas_using_last_week_disp = null
      それ以外の場合
          → gas_using_last_week_disp = intval(gas_using)
```

**③ 「先週使用した電気量」の算出**（世帯ごと、SQL 2の結果に基づく）― ②と同じ計算式だが、**時間データのチェック手順はない**:
```
electric_using_day ≠ 7 の場合
      → electric_using_last_week = null、electric_using_last_week_disp = null
   それ以外の場合：
      electric_using_last_week = floor(electric_using × 100) / 100   （electric_using > 0の場合。そうでなければnull）
      electric_usingが空、または0未満、または999超の場合
          → electric_using_last_week_disp = null
      それ以外の場合
          → electric_using_last_week_disp = intval(electric_using)
```
出典: `CalcWeeklySavingReportUsingCommand.php:220-313`（`execute`）。

### 2.4 結果の書き込み ― 書き込み先テーブル`s_105`

- エンティティ: `ConWeeklyEcoReport`（共通ライブラリ`EminelSvLib`）、物理テーブル`s_105`、主キー`(c001, c002)` = （世帯コード、算出日）。
- 実行のたびに、**ガスまたは電気の算出結果に含まれる各世帯**について、以下のカラムで**1行をINSERT/UPDATE（upsert）**する: `used_last_week_gas → c011`、`used_last_week_ele → c012`、`used_week_before_last_gas → c013`、`used_week_before_last_ele → c014`、`report_used_last_week_gas → c021`、`report_used_last_week_ele → c022`、`report_used_week_before_last_gas → c023`、`report_used_week_before_last_ele → c024`。また、フラグ`GasEleCalculatedFlag（c041） = true`を設定する。
- 並走バッチ`CalcWeeklySavingReportEffectCommand`の担当範囲に属するカラム（`reduced_gas_fee`、`gas_fee_reduce_code`、`report_reduced_gas_fee`、`weekly_ave_temp`、`gross_floor_space`、`gas_fee_unit`、`correcting_factor`、フラグ`GasReducedFeeCalculatedFlag`）は、**エンティティ生成時にnull／falseを設定するが、保存前に`setDirty(..., false)`を指定**する → 該当行が既に存在する場合（並走バッチが先に実行されていた場合）、これらのカラムはUPDATE時に**上書きされない**。
- 全体を**バッチ全体で1つのトランザクション**として実行する: いずれかの世帯で書き込みに失敗した場合 → 全体を`rollback()`し`abort()`する。部分的な書き込みの仕組みはない。
- 本バッチは**通知の自送信・ファイル出力を行わない**。`s_105`内のデータはAPI`GetWeeklyEcoReportController`が読み取り、利用者アプリへ返却する ― これは本コマンドの対象範囲外である。
