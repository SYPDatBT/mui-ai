# 旧バッチ ― CalcYearlyPresetTemperatureCommand（年毎平均設定温度算出）

## まとめ

`CalcYearlyPresetTemperatureCommand` は、旧システム（EMINEL コンシェルジュサーバー）内で**月1回、暖房シーズン中のみ**（1月・2月・3月・4月の1日 16:10）実行されるバッチである。実行のたびに、日次設定温度平均テーブル（`s_103`。`CalcMonthlyAverageSetTemperatureCommand` バッチが事前に書き込む）の**1か月分・31個の日カラム全体**を、**世帯ごとに1個の月間平均値**へ集約する ― ただし、当月内でデータが欠損している日数が十分少ない場合（10日未満）に限り計算する。本バッチはDBの読み書きのみを行い（メール送信・ファイル出力は行わない）、結果は`s_104`テーブルに書き込まれる。バッチ名に「Yearly」とあるのは、書き込み先テーブルが「1行 = 1世帯 × 1年 × 12個の月カラム」という構成になっているためであり、これは**保存**の単位である。一方、本バッチの**計算**単位はあくまで1か月であり（1回の実行につき、計算・書き込みを行うのはちょうど1個の月カラムのみ）。実行スケジュール・SQL文・計算式、およびこの結果を利用する他バッチの詳細はPart 2に記載する。

## Part 1 — 概要

| 項目 | 内容 |
|---|---|
| **役割** | 1か月分の日次設定温度平均値（`s_103`に既存）を、世帯ごとに集約（多→一）して1個の月間平均値にまとめ、月次の「エコ暖房」ポイント付与機能のソースデータとする。 |
| **Input** | DBの読み取りのみ、**外部API呼び出し・CSVファイル読み込みなし**：`t_101`（世帯一覧）＋ `s_103`（各世帯の日次設定温度平均値。`CalcMonthlyAverageSetTemperatureCommand`バッチが事前に計算済み、条件`device_type=17`）＋ コマンドライン引数`--yearmonth`。 |
| **Output** | **DB書き込みのみ** ― 実行のたびに、結果が得られた各世帯について、`s_104`（エンティティ`ConSensorMonthlyValue`、共通ライブラリ`EminelSvLib`経由）の**1個の年行**の中の**1個の月カラム**を書き込み／更新する。メール送信・CSV出力は行わない。 |
| **処理概要** | 1. 「計算対象月」を決定する（引数`--yearmonth`、未指定時のデフォルト＝現在の月の1か月前）。<br>2. SQLを1本発行：有効な各世帯について、`s_103`の該当する月行の31個の日カラムを合計し、データが存在する日数をカウントする。<br>3. データ欠損日数が閾値（10日）未満であれば → 月間平均＝合計 ÷ データが存在する日数、小数点第1位で切り捨て；それ以外は → NULL。<br>4. 結果に含まれる各世帯について、`s_104`に1レコードを書き込み／更新する ― 該当する年行の対応する月カラムをセットする。<br>5. すべて1つのトランザクション内で行う。書き込み段階でのエラー → rollbackして停止；クエリ段階でのエラー → commit（rollbackしない）して停止。 |

## Part 2 — 詳細

### 2.1 実行スケジュールとパラメータ

| 項目 | 内容 | 出典 |
|---|---|---|
| 実行スケジュール（cron） | 2行あり、いずれも`17_CalcYearlyPresetTemperature.sh`を**16:10**に実行：`10 16 1 1,2,3 *`（1月／2月／3月の1日）、`10 16 1 4 *`（4月1日のみ別行） | `docs/02_詳細設計/10_バッチ処理/mng-webap_cron設定_20241029.txt:57-59` (`#17.年毎平均設定温度算出` → `17_CalcYearlyPresetTemperature.sh`) |
| 実行コマンド | `php cake.php CalcYearlyPresetTemperature [--yearmonth=<yyyy-MM>]` | `CalcYearlyPresetTemperatureCommand.php:35,58-61` |
| パラメータ`yearmonth`（未指定時） | `現在 − 1か月`、フォーマット`yyyy-MM` | `CalcYearlyPresetTemperatureCommand.php:58-61` |
| cronが1・2・3・4月の4か月連続で実行される理由 | デフォルトパラメータは実行日から常に1か月前を指すため、暖房シーズン全体（12月～3月）を計算し切るには実行日が1/1・1/2・1/3・1/4である必要がある（それぞれ12月・1月・2月・3月分を計算）― `CalcMonthlyAverageSetTemperatureCommand`バッチと同様の理由でcron行を分割する必要がある | ― |

### 2.2 集計SQL文

```sql
WITH calc_monthly AS (
  SELECT monthly.c001 AS ems_sp                        -- 世帯コード
       , monthly.c002 AS device_type
       , monthly.c003 AS location
       , :calcYear AS target_year
       , (CASE WHEN monthly.c011 IS NULL THEN 0 ELSE monthly.c011 END
          + CASE WHEN monthly.c012 IS NULL THEN 0 ELSE monthly.c012 END
          + ... -- c012～c041まで合算（計31個の日カラム）
         ) AS temp_sum                                  -- データが存在する日の日次設定温度平均値の合計
       , (CASE WHEN monthly.c011 IS NULL THEN 0 ELSE 1 END
          + CASE WHEN monthly.c012 IS NULL THEN 0 ELSE 1 END
          + ... -- c012～c041までカウント
         ) AS total_days                                -- 当月内でデータが存在する日数
       , EXTRACT(DAY FROM DATE_TRUNC('MONTH', :calcDate::DATE) + INTERVAL '1 MONTH' - INTERVAL '1 day') AS days  -- 当月の総日数
    FROM t_101 AS customer
    INNER JOIN s_103 AS monthly
       ON customer.c001 = monthly.c001
      AND monthly.c002 = 17                             -- device_type = ROOM_TEMP_SETTING
      AND monthly.c004 = :calcDate                       -- 計算対象の月行（当月の01日）
   WHERE customer.c052 IS NULL                           -- 論理削除されていない世帯
)
SELECT calc_monthly.ems_sp
     , calc_monthly.device_type
     , calc_monthly.location
     , calc_monthly.target_year
     , CASE WHEN (calc_monthly.days - calc_monthly.total_days) < :summaryThreshould
         THEN trunc((calc_monthly.temp_sum / calc_monthly.total_days), 1)
         ELSE NULL
       END AS sensor
  FROM calc_monthly
```
出典: `CalcYearlyPresetTemperatureCommand.php:64-112`（SQL文字列は`for ($i = 12; $i <= 41; $i++)`ループで組み立てられており、上記ブロックは読みやすさのため簡略化したもの）。

渡されるパラメータの意味:

| パラメータ | 値 | 意味 |
|---|---|---|
| `:calcDate` | `<yearmonth>-01`（'yyyy-MM-dd'形式。コード上は '-01 00:00:00' でparse後、日付のみにフォーマット） | `s_103`内で読み取るべき月行のキー（`CalcMonthlyAverageSetTemperatureCommand`が書き込む方式と一致：`datetime` = 計算対象日を含む月の01日） |
| `:calcYear` | `yearmonth`の先頭4文字 | 年 ― `s_104`へ書き込む際の年行のキーとして使用 |
| `:summaryThreshould` | 定数`NOT_SUMMARY_DATE_COUNT` = 10 | データ欠損日数がこの値以上なら集計しない（許容される欠損は最大9日） |

出典: `CalcYearlyPresetTemperatureCommand.php:103-110`；定数は`const.php:595`。

**SQL文で使用するカラムの意味:**

| テーブル | カラム | 意味 | 備考 |
|---|---|---|---|
| `t_101` | `c001` | 世帯コード（EMS-SP） | 結合キー |
| `t_101` | `c052` | 論理削除日時 | `IS NULL` = 有効な世帯 |
| `s_103` | `c001` | 世帯コード | 結合キー |
| `s_103` | `c002` | 機器種別（device_type） | 固定で`= 17`（`ROOM_TEMP_SETTING`）に絞り込み |
| `s_103` | `c003` | Room id／位置 | そのまま取得（`location`）、絞り込みなし |
| `s_103` | `c004` | 月行のDatetime | 計算対象のちょうど1か月に絞り込み（`= :calcDate`） |
| `s_103` | `c011`～`c041` | 31個の日カラム ― 日次設定温度平均値（`CalcMonthlyAverageSetTemperatureCommand`が事前に書き込む） | ⭐ 月間平均の計算に使用する値 |

### 2.3 計算式（世帯ごと、月全体を集約）

```
① temp_sum   = c011～c041のうちNULLでないカラムの合計（NULLは0とみなす）
② total_days = c011～c041のうちNULLでないカラムの個数
③ days       = 計算対象月の実際の日数（28／29／30／31）
④ (days − total_days) < NOT_SUMMARY_DATE_COUNT (10) の場合
       → 月間平均 = trunc(temp_sum / total_days, 1)
   それ以外（当月内のデータ欠損日数が多すぎる場合）
       → 結果 = NULL
```
出典: `CalcYearlyPresetTemperatureCommand.php:96-101`。

異常値／有効範囲外の値を除外するステップはない ― 本計算式はデータが存在する日数のみに基づいており、個々の温度値が妥当かどうかは判定しない。

### 2.4 結果の書き込み ― 対象テーブル`s_104`

- エンティティ: `ConSensorMonthlyValue`（共通ライブラリ`EminelSvLib`）、物理テーブル`s_104` ― 1行 = 1世帯 × 1年、12個の月カラム（`c011`～`c022`、月カラム = `c0` + (月数 + 10)）。
- 2.2のSQLが1行以上の結果を返した場合のみ書き込みステップを実行する。バッチは書き込み前に`sensor`の値がNULLかどうかを個別にチェック**しない** ― `sensor`がNULLであれば、該当する月カラムもNULLとしてそのままセットされる（既存の値があれば上書きされる）。
- 結果に含まれる各世帯について：`ems_sp`、`device_type = 17`、`room_id = 0`、`datetime = target_year`（整数形式の年、年行のキーとして使用）を設定し、対応する月カラム（`c0` + (計算対象月 + 10)）に値をセットし、`modified`を更新する。
- すべて**バッチ全体で1つのトランザクション**内で行われる：いずれかの世帯で書き込みに失敗した場合 → 全体を`rollback()`し`abort()`する。部分的な書き込みの仕組みはない。
- 2.2の集計SQLでエラーが発生した場合 → バッチは`commit()`を呼び出し（`rollback()`は**呼ばない**）、直ちに`abort()`する ― これは結果書き込み時のエラー分岐（`rollback()`を使用）とは異なる。`CalcMonthlyAverageSetTemperatureCommand`バッチと同様の不整合である。

出典: `CalcYearlyPresetTemperatureCommand.php:113-152`。

### 2.5 集計チェーンと結果を利用する機能

本バッチは、設定温度の集計チェーンにおける2番目の要素である（`CalcMonthlyAverageSetTemperatureCommand`の後）:

```
s_103  "ConSensorDailyValue"    1行/世帯/月  × 31個の日カラム   (device_type=17, room_id=0)
   │  CalcMonthlyAverageSetTemperatureCommandが書き込む（1日1回実行、暖房シーズン中）
   │
   │  CalcYearlyPresetTemperatureCommand  (☚ 本ドキュメントで分析しているバッチ ― 月1回実行)
   │  (s_103の1か月分の日カラムを1個の月間平均値へ集約する。
   │   データが存在する日数 >（当月の日数 − 10）の場合のみ計算する（＝欠損日数が10日未満）)
   ▼
s_104  "ConSensorMonthlyValue"   1行/世帯/年  × 12個の月カラム   (device_type=17, room_id=0)
   │
   │  DistributeMonthlyEcoPointsCommand
   │  (月1回実行、s_104の直前の月カラムを読み取り、
   │   値が22.0℃以下であれば → 世帯に「エコ暖房」ポイント250点を付与、
   │   理由ログ"monthly_eco_points_YYYYMM"により重複付与を防止)
   ▼
世帯にConEcoPoints / PointInfinity経由でecoポイントが付与される
```

出典: `DistributeMonthlyEcoPointsCommand.php:33,79-114`（`BENEFIT_POINTS=250`）。

注記: `GetEcoPointsController`（アプリ向けにecoポイントを表示するAPI）は`s_104`を**読み取らない** ― 表示の際に月間平均を自ら再計算するため、`s_103`（`ConSensorDailyValues`）の月行を直接読み取っており、本バッチが書き込む結果とは独立している。

出典: `GetEcoPointsController.php:106-118`。
