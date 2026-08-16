# 旧バッチ ― CalcWeeklySavingReportEffectCommand（週間暖房効果算出機能）

## 概要

`CalcWeeklySavingReportEffectCommand` は、旧システム（EMINEL コンシェルジュサーバー）において**週1回**（日曜日）実行されるバッチで、各世帯について直近7日間の室内平均温度・延床面積・ガス契約種別をもとに、**ガス料金削減額（暖房・エコ効果により週間で節約できたガス料金）**を算出する。本バッチはDBの読み書きのみを行い（メール送信・ファイル出力は行わない）、結果は `s_105` テーブルに書き込まれる ― これは並行バッチ `CalcWeeklySavingReportUsingCommand`（週間の使用ガス量／電力量を算出）と同じテーブルである。計算式・業務定数・DB書き込みの仕組みの詳細は第2部で説明する。

## 第1部 ― 全体概要

| 項目 | 内容 |
|---|---|
| **役割** | 各世帯の7日間室内平均温度・延床面積・ガス契約種別から、**週間のガス料金削減額**（暖房・エコ効果）を算出し、結果を分類する（正常／下限未満／上限超過／算出不能）。 |
| **Input** | DB読み取りのみ、**外部API呼び出し・CSVファイル読み込みなし**：`t_101`（世帯一覧 ― 延床面積 `c015`、ガス契約種別 `c023`）＋ `s_103`（月次センサーデータ。既に他のバッチ／処理により集計済み ― 算出日より前7日間の室内平均温度と使用ガス量を取得）。 |
| **Output** | **DB書き込みのみ** ― 実行の都度、対象となる各世帯について `s_105`（entity `ConWeeklyEcoReport`、共通ライブラリ `EminelSvLib` 経由）へ**1行を書き込み／更新**し、「ガス料金削減額」関連カラムのみをsetする（「使用ガス量／電力量」関連カラムは `dirty=false` として触れない ― 並行バッチ `CalcWeeklySavingReportUsingCommand` の管轄）。メール送信・CSV出力は行わない。 |
| **処理概要** | 1. 「算出日」を決定する（入力パラメータ、または未指定の場合は当日）。<br>2. SQLを1本発行：各世帯について、算出日より前7日間の使用ガス量・室内平均温度を集計し、延床面積／ガス契約種別も併せて取得する。<br>3. 各世帯ごとに、データが揃っているか確認する（面積、ガス契約、使用ガス量＞下限値、平均温度が存在）→ 不足していれば結果はnull。<br>4. データが揃っていれば、物理式（Q値、補正係数、契約種別ごとのガス単価を使用）に基づきガス料金削減額を算出し、丸め処理を行った上で3つの閾値で分類する（下限未満／正常／上限超過1／上限超過2 → 算出不能）。<br>5. 結果（nullの場合も含む）を `s_105` に書き込む。バッチ全体を1つのトランザクションとして実行する。 |

## 第2部 ― 詳細

### 2.1 実行スケジュール・パラメータ

| 項目 | 内容 | 出典 |
|---|---|---|
| 実行スケジュール（cron） | `50 4 * * 7` ― 週1回、日曜04:50 | `docs/02_詳細設計/10_バッチ処理/mng-webap_cron設定_20241029.txt:73-74`（`#22.週間暖房効果算出機能` → `22_CalcWeeklySavingReportEffect.sh`） |
| 実行コマンド | `php cake.php CalcWeeklySavingReportEffect [算出日]`（パラメータ形式は `yyyy-MM-dd`） | `CalcWeeklySavingReportEffectCommand.php:20-21` |
| 「算出日」（`calcDate`、パラメータ未指定時） | 当日、フォーマット `yyyy/MM/dd` | `CalcWeeklySavingReportEffectCommand.php:56-62` |
| 並行バッチ | `CalcWeeklySavingReportUsingCommand` ― 同日、20分早く（`04:30`）実行され、週間の**使用済み**ガス量／電力量を算出し、**同じ `s_105` テーブルの同じ行**（`ems_sp` ＋日付で対応）に書き込む | `mng-webap_cron設定_20241029.txt:70-71`、`CalcWeeklySavingReportUsingCommand.php` |

### 2.2 データ取得SQL

```sql
SELECT customer_sensor.ems_sp                                        -- Mã hộ
     , customer_sensor.gas_contract                                  -- Loại hợp đồng gas
     , customer_sensor.floor_area                                    -- Diện tích sàn (mã phân loại)
     , SUM(CASE WHEN customer_sensor.device_type = 2                  -- device_type=2: lượng gas dùng
                THEN customer_sensor.month_target_day END) AS gas_using
     , ROUND(AVG(CASE WHEN customer_sensor.device_type = 6             -- device_type=6: nhiệt độ phòng
                     THEN customer_sensor.month_target_day END), 1) AS average_room_temperature
  FROM (
        SELECT customer.c001 AS ems_sp
             , month_sensor_sub.c002 AS device_type
             , customer.c023 AS gas_contract                          -- Loại hợp đồng gas
             , customer.c015 AS floor_area                            -- Diện tích sàn
             , month_sensor_sub.month_target_day                      -- Giá trị của đúng 1 ngày trong tháng (map theo CASE 1~31)
          FROM t_101 AS customer                                      -- Danh sách hộ
          LEFT JOIN (
                    SELECT month_sensor.c001, month_sensor.c002, month_sensor.c003, month_sensor.c004
                         , base_date.target_day
                         , CASE WHEN base_date.target_day = '01' THEN month_sensor.c011
                                WHEN base_date.target_day = '02' THEN month_sensor.c012
                                ...                                    -- lặp cho 31 ngày, cột c011~c041
                                ELSE null END AS month_target_day
                      FROM s_103 AS month_sensor                       -- Dữ liệu cảm biến theo tháng (đã tổng hợp sẵn)
                      INNER JOIN (
                                 SELECT date_trunc('month', :calcDate - serial_number ngày) AS target_ym
                                      , ngày trong tháng của (:calcDate - serial_number ngày) AS target_day
                                   FROM generate_series(1, 7) AS serial_number      -- 7 ngày trước calcDate
                                 ) AS base_date
                        ON base_date.target_ym = month_sensor.c004
                     WHERE (month_sensor.c002 = 6 AND month_sensor.c003 = 0)        -- nhiệt độ phòng, phòng/kênh số 0
                        OR month_sensor.c002 = 2                                   -- hoặc lượng gas dùng
           ) AS month_sensor_sub
            ON customer.c001 = month_sensor_sub.c001
         WHERE customer.c052 IS NULL                                   -- Hộ chưa bị xóa logic
    ) AS customer_sensor
 GROUP BY customer_sensor.ems_sp, customer_sensor.floor_area, customer_sensor.gas_contract
 ORDER BY customer_sensor.ems_sp
```
出典: `CalcWeeklySavingReportEffectCommand.php:69-118`（読みやすさのためCASE31日分は省略）。

**SQLで使用しているカラムの意味：**

| テーブル | カラム | 意味 | 備考 |
|---|---|---|---|
| `t_101` | `c001` | 世帯コード（EMS-SP） | 結合キー |
| `t_101` | `c015` | 延床面積（分類コード1〜6） | 標準面積テーブルの参照に使用 |
| `t_101` | `c023` | ガス契約種別（1または2） | ガス単価の参照に使用 |
| `t_101` | `c052` | 論理削除日時 | `IS NULL` = 有効な世帯 |
| `s_103` | `c001` | 世帯コード | 結合キー |
| `s_103` | `c002` | 機器／データ種別 | `2` = 使用ガス量、`6` = 室内温度 |
| `s_103` | `c003` | チャンネル／部屋 | 室内温度取得時は `= 0` で絞り込み |
| `s_103` | `c004` | データの年月 | 取得対象の7日間を含む月でJOIN |
| `s_103` | `c011`〜`c041` | 月内の各日の値（1日〜31日） | `target_day` に応じて `CASE` で該当日のカラムを選択 |

### 2.3 「ガス料金削減額」の算出式（世帯ごと）

```
① データ充足チェック ― 以下のいずれかに該当する場合 → gasReductionAmount = null として終了：
   - floor_area が空／0
   - gas_contract が空／0
   - gas_using（7日間の使用ガス量）が空
   - gas_using ≤ WEEKLY_GAS_USAGE_BOTTOM (1.0)
   - average_room_temperature が空

② floor_area のコード（1〜6）から標準延床面積（building_area）を引く：
   1→70㎡、2→80㎡、3→100㎡、4→120㎡、5→140㎡、6→151㎡
   （上記以外のコード → building_area = null → ステップ④で算出不能（null）となる）

③ gas_contract からガス単価（unitCharge）を引く：
   1（エコジョーズ）→ 93.90／2（マイホーム発電）→ 82.35

④ （①の）データが充足しており、かつ building_area・unitCharge のいずれも値がある場合：
     gasReductionAmount =
         (24 − average_room_temperature) × building_area × 1.6 × 24 × 3.6 / 45
         × 7 × unitCharge / 1000 × 0.7
     → 小数第3位以下を切り捨て（小数第2位まで保持、floor(x × 100) / 100）
   それ以外の場合 → gasReductionAmount = null

⑤ 百の位に丸める → gasReductionAmountJudgement（`round(x, -2)` を使用）
   gasReductionAmount が空の場合 → gasReductionAmountJudgement = null

⑥ gasReductionAmountJudgement に応じて結果を分類（gasReductionAmountResultCode）：
   - 空                                    → 4（算出不能）
   - < 100（WEEKLY_GAS_FEE_LIMIT_BOTTOM）   → 2（下限未満）
   - ≤ 900（WEEKLY_GAS_FEE_LIMIT_THRESHOLD） → 0（正常）
   - ≤ 1900（WEEKLY_GAS_FEE_LIMIT_TOP）     → 3（上限超過1）
   - それ以外（> 1900）                     → 4（算出不能）

⑦ 表示値（gasReductionAmountDisp）= gasReductionAmountJudgement
   resultCode = 0（正常）の場合のみ。それ以外 → null
```
出典: `CalcWeeklySavingReportEffectCommand.php:136-257`（`execute`）。

**業務定数**（`sources/conciergesv-develop/config/const.php:614-645`）：

| 定数 | 値 | 意味 |
|---|---|---|
| `UNIT_CHARGE_ECOJOZU` | 93.90 | ガス単価 ― 契約種別1（エコジョーズ） |
| `UNIT_CHARGE_MYHOME` | 82.35 | ガス単価 ― 契約種別2（マイホーム発電） |
| `WEEKLY_GAS_USAGE_BOTTOM` | 1.0 | 使用ガス量の下限値 ― これ未満はデータ不足とみなす |
| `WEEKLY_GAS_FEE_FLOOR_AREA_1`〜`_6` | 70 / 80 / 100 / 120 / 140 / 151 | コード1〜6に対応する標準延床面積 |
| `WEEKLY_GAS_FEE_TEMPERATURE` | 24 | 基準温度（EMINELを使用しないと仮定した場合の値） |
| `WEEKLY_GAS_FEE_Q_VALUE` | 1.6 | Q値係数（住宅の熱特性） |
| `WEEKLY_GAS_FEE_DAYS` | 7 | 週間の算出対象日数 |
| `WEEKLY_GAS_FEE_COEFFICIENT` | 0.7 | 補正係数 |
| `WEEKLY_GAS_FEE_LIMIT_BOTTOM` | 100 | 結果分類用の下限閾値 |
| `WEEKLY_GAS_FEE_LIMIT_THRESHOLD` | 900 | 「正常」の上限閾値 |
| `WEEKLY_GAS_FEE_LIMIT_TOP` | 1900 | 最上位の閾値 ― これを超えると算出不能とみなす |

### 2.4 結果の書き込み ― 対象テーブル `s_105`

- Entity：`ConWeeklyEcoReport`（共通ライブラリ `EminelSvLib`）、物理テーブル `s_105`、主キー `(c001, c002)` = （世帯コード、算出日）。
- 実行の都度、**クエリ結果に含まれる各世帯**について（算出条件を満たしているか否かに関わらず ― 満たさない場合もnull値で行を書き込む）、以下のカラムに対して**1行をINSERT/UPDATE（upsert）**する：`gas_reduction_amount → c016`、`gas_reduction_amount_result_code → c025`、`gas_reduction_amount_disp → c026`、`weekly_average_room_temperature → c031`、`total_floor_area → c032`、`gas_unit_price → c033`、`correction_factor → c034`；フラグ `GasReducedFeeCalculatedFlag (c042) = true` をセットする。
- 並行バッチ `CalcWeeklySavingReportUsingCommand` の管轄に属するカラム（使用済みガス量／電力量：`c011`〜`c014`、発出値：`c021`〜`c024`、フラグ `c041` ― `c041` のみfalseをset）は、entity作成時に**null／false値をsetした上で `setDirty(..., false)` を指定**してからsaveする → 該当行が既に存在する場合（並行バッチが先に実行済みの場合）、これらのカラムはUPDATE時に**上書きされない**。
- 全体が**バッチ全体で1つのトランザクション**にまとめられており、いずれかの世帯で書き込みに失敗した場合 → 全体を `rollback()` して `abort()` する。部分的な書き込みを許容する仕組みはない。
- 本バッチは**通知の送信・ファイル出力を行わない**。`s_105` 内のデータは API `GetWeeklyEcoReportController` によって読み取られ、ユーザーアプリへ返却される ― これは本コマンドの対象範囲外である。
