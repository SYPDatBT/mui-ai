# 旧バッチ ― CalcCarbonDioxideEmissionsCommand（CO2排出量算出）

## 概要

`CalcCarbonDioxideEmissionsCommand` は、旧システム（EMINEL コンシェルジュサーバー）で**月1回**実行されるバッチであり、`s_104` テーブルにすでに存在する月次のガス・電気使用量データから、各世帯の**1か月間のCO2排出量**（ガス分・電気分・合計）を算出する ― ガス／電気を別々に計算したうえで合算する。結果は同じ `s_104` テーブルに（CO2専用の3つの機器種別コードを用いて）書き戻され、旧システム内の他の2箇所で利用される：API `GetCo2ReductionReportController`（前年同期比のCO2削減量をアプリに表示するレポート）と `Co2ReducedPublisher`（CO2の増減に基づく省エネアドバイスの定期配信）。本バッチはDBの読み書きのみを行い、メール送信・CSV出力は行わない。詳細は第2部を参照。

## 第1部 ― 全体概要

| 項目 | 内容 |
|---|---|
| **役割** | `s_104` にすでに存在する月次のガス・電気使用量から、その月の世帯ごとのCO2排出量（ガス／電気／合計）を算出し、`s_104` に書き戻す。アプリ上のCO2レポートおよび省エネアドバイスに利用するため。 |
| **入力** | DBの読み取りのみ、**外部API呼び出しなし、CSV読み込みなし**：`t_101`（世帯一覧）＋ `s_104`（自分自身 ― 世帯・年ごとに3行の元データ：売電（電気販売）、買電（電気購入）、ガス消費量。いずれも処理対象の月カラムに存在し、3つとも `CalcYearlyAccumulatedValueCommand` が書き込んだもの ― [2.5](#25-s_104-内データの出所入力に使う3種類) を参照）。 |
| **出力** | **DBへの書き込みのみ** ― `s_104` テーブルに3行（ガスCO2、電気CO2、合計CO2）× 1つの月カラムを書き込み／上書きする（エンティティ `ConSensorMonthlyValue`、共通ライブラリ `EminelSvLib` 経由）。メール送信・CSV出力は行わない。 |
| **処理概要** | 1. パラメータ `--yearmonth`（デフォルト＝当月の前月の1日）を取得し、手動指定された場合は `yyyy-MM` 形式かどうかをバリデートする。<br>2. SQLを1本実行：論理削除されていない各世帯について、処理対象の月カラム（`s_104` から取得）の買電量から売電量を差し引いた値、およびガス消費量を取得し、それぞれ対応するCO2係数を掛ける。処理対象の月にちょうど新規登録された世帯は除外する。<br>3. 取得できた各世帯について：`s_104` に3行を書き込む（`device_type` ＝ 合計／ガス／電気のCO2）。処理対象の1つの月カラムに算出値をセットする。<br>4. バッチ全体を通して1つのトランザクションとする ― いずれか1世帯の書き込みでエラーが発生した場合は直ちに停止し、全体をロールバックする。 |

## 第2部 ― 詳細

### 2.1 実行スケジュール・パラメータ

| 項目 | 内容 | 出典 |
|---|---|---|
| 実行スケジュール（cron） | `10 6 1 * *` ― 月1回、1日の午前6時10分 | `docs/02_詳細設計/10_バッチ処理/mng-webap_cron設定_20241029.txt:64-65` (`#19.CO2排出量算出バッチ` → `19_CalcCarbonDioxideEmissions.sh`) |
| 実行コマンド | `php cake.php CalcCarbonDioxideEmissions [--yearmonth=yyyy-MM]` | `CalcCarbonDioxideEmissionsCommand.php:22,36` |
| `--yearmonth` デフォルト（未指定時） | （当月 − 1か月）の1日 | `CalcCarbonDioxideEmissionsCommand.php:57-60` |
| `--yearmonth` 手動指定時 | 形式は `yyyy-MM`（正規表現 `/^[0-9]{4}-(0[1-9]|1[0-2])$/`）。形式が不正な場合はALERTログを出力し、`commit()`（空のトランザクション）の後 `abort()` でバッチを停止する | `CalcCarbonDioxideEmissionsCommand.php:62-70, 245-256` |
| `s_104` 上の対象／元カラム | `c0<番号>` ＝ 月＋10 → 1月は `c011`、12月は `c022` | `CalcCarbonDioxideEmissionsCommand.php:85, 212` |

### 2.2 データ取得SQL

```sql
WITH gas_elec_co2 AS (
    SELECT customer.c001 AS ems_sp                                       -- 世帯ID
         , customer.c012 AS build_type                                  -- 住宅タイプ
         , customer.c042 AS heater_power                                -- 暖房出力
         , customer.c015 AS floor_space                                 -- 床面積
         , customer.c016 AS family_size                                 -- 人数
         , customer.c024 AS gas_cogeneration                            -- コジェネレーションタイプ
         , customer.c051 AS regist_date                                 -- 世帯登録日
         , baiden.c003   AS room_id                                     -- = 0（フィルタ条件により固定）
         , baiden.c004   AS target_year                                 -- 対象年
         , TRUNC(SUM((kaiden.<月カラム> - baiden.<月カラム>) * :electricCoefficient), 0) AS elec_co2
         , TRUNC(SUM(gas.<月カラム> * :gasCoefficient), 0)             AS gas_co2
      FROM t_101 AS customer
      LEFT JOIN s_104 AS baiden                                         -- 売電（電気販売）、room=0
             ON customer.c001 = baiden.c001
      LEFT JOIN s_104 AS kaiden                                         -- 買電（電気購入）、room=0、対象年
             ON customer.c001 = kaiden.c001 AND kaiden.c002 = 11 AND kaiden.c003 = 0 AND kaiden.c004 = :year
      LEFT JOIN s_104 AS gas                                            -- ガス消費量、room=0、対象年
             ON customer.c001 = gas.c001 AND gas.c002 = 2 AND gas.c003 = 0 AND gas.c004 = :year
     WHERE baiden.c002 = 10 AND baiden.c003 = 0 AND baiden.c004 = :year -- 対象年の売電行を持つ世帯であること
       AND customer.c052 IS NULL                                       -- 論理削除されていない世帯
     GROUP BY customer.c001, customer.c012, customer.c042, customer.c015
            , customer.c016, customer.c024, baiden.c003, baiden.c004
)
SELECT co2.ems_sp, co2.build_type, co2.heater_power, co2.floor_space, co2.family_size, co2.gas_cogeneration
     , co2.room_id, co2.target_year, co2.elec_co2, co2.gas_co2, (co2.elec_co2 + co2.gas_co2) AS total_co2
  FROM gas_elec_co2 AS co2
 WHERE regist_date NOT BETWEEN :fistOfMonth AND :endOfMonth            -- 処理対象の月にちょうど登録された世帯を除外
```
出典: `CalcCarbonDioxideEmissionsCommand.php:87-152`（実際の月カラムは `c0<月+10>` であり、上記では `<月カラム>` と省略表記している ― 2.1参照）。

**フィルタ／JOINに使用するコードの意味**（`AGGREGATION_TYPE_YEARLY` に準拠。`CalcYearlyAccumulatedValueCommand` のドキュメントと同じ一覧）：

| テーブル／エイリアス | `c002`（種別）| `c003`（部屋）| 意味 |
|---|---|---|---|
| `baiden` | `10`（SALE_ELECTRIC）| `0` | 売電量 ― その年に系統へ売電した電力量。この行がある世帯のみ計算対象となる |
| `kaiden` | `11`（BUY_ELECTRIC）| `0` | 買電量 ― その年に系統から買電した電力量 |
| `gas` | `2`（GAS_CO_TYPE_CONSUMPTION）| `0` | ガス総合消費量 ― その年のガス消費量の合計 |

`t_101.c051` ＝ 世帯登録日、`t_101.c052` ＝ 論理削除日（`IS NULL` ＝ 有効な世帯）。

### 2.3 算出式（世帯ごと、処理対象の1つの月カラムについて）

```
elec_co2  = (その月の買電量 − その月の売電量) × ELECTRIC_CO2_EMISSION_COEFFICIENT、小数点以下切り捨て（TRUNC）
gas_co2   = (その月のガス消費量) × GAS_CO2_EMISSION_COEFFICIENT、小数点以下切り捨て（TRUNC）
total_co2 = elec_co2 + gas_co2
```
出典: `CalcCarbonDioxideEmissionsCommand.php:97-98, 135`。

**業務定数**（`sources/conciergesv-develop/config/const.php`）：

| 定数 | 値 | 行 |
|---|---|---|
| `ELECTRIC_CO2_EMISSION_COEFFICIENT` | 0.499（kg/kWh）| `const.php:649` |
| `GAS_CO2_EMISSION_COEFFICIENT` | 2.09（MJ/m3）| `const.php:651` |
| `TOTAL_CO2_EMISSIONS` | 18 ― `device_type` に合計CO2として書き込む値 | `const.php:204` |
| `GAS_CO2_EMISSIONS` | 19 ― `device_type` にガス由来CO2として書き込む値 | `const.php:206` |
| `ELE_CO2_EMISSIONS` | 20 ― `device_type` に電気由来CO2として書き込む値 | `const.php:208` |

### 2.4 結果の書き込み ― 出力先テーブル `s_104`（入力に使用したのと同じテーブル）

- エンティティ：`ConSensorMonthlyValue`（共通ライブラリ `EminelSvLib`）、物理テーブルは `s_104` ― 2.2で読み取ったのと同じテーブル。
- SQL結果に含まれる**各世帯**について、`device_type` = 18, 19, 20（合計／ガス／電気）ごとに繰り返す：新規エンティティを1件作成し ― キーは（世帯ID、`device_type`、`room_id = 0`、`target_year`）― 世帯の5つの属性項目（`c111`〜`c115` ＝ 住宅タイプ、暖房出力、床面積、人数、コジェネレーションタイプ）をコピーし、処理対象の月カラム（`c0<月+10>`）に対応するCO2値（文字列型に変換）をセットし、`c031` ＝ 現在時刻をセットしたうえで `save()` する（主キーによるupsert）。
- バッチ全体を通して**1つのトランザクション**とする：いずれかの世帯／`device_type` で `save()` がエラーになった場合 → 直ちに停止し、`rollback()` で全体を取り消し、`abort()` する ― 残りの世帯への書き込みは継続しない。
- 2.2のSQLが0件を返した場合：infoログを出力するのみでロールバックはせず、バッチは `commit()` する（空のトランザクション）。
- 本バッチは**通知の自動送信は行わず、他の値を追加で算出することもない** ― `device_type` 18/19/20 のデータは、旧システム内の他の2箇所で後から読み取られる：API `GetCo2ReductionReportController`（前年同期との比較）と `Co2ReducedPublisher`（省エネアドバイスの定期配信）― この2つは本コマンドの対象範囲外である。

### 2.5 `s_104` 内データの出所（入力に使う3種類）

本バッチが読み取る `s_104` の3行（売電=10、買電=11、ガス総合=2）はいずれも **`CalcYearlyAccumulatedValueCommand`**（年次集計バッチ、月1回実行、`s_103` の31個の日カラムを `s_104` の1つの月カラムに積算する）が書き込んだものである。`s_103` に至るまで、各種別はそれぞれ異なるバッチの流れを経ている：

```text
ガス総合（type 2）:
  t_202（生ECHONET、ガスメーター）
     │  CalcTenMinutesEnergyCommand              （10分ごと）
     ▼
  s_101  （10分、type 2/3/4）
     │  CalcDailyEnergyConsumptionCommand         （毎時 ―「業務1: gasConsumptionSummary」）
     ▼
  s_102  （時間、type 2/3/4）
     │  CalcMonthlyAccumulatedValueCommand        （毎日）
     ▼
  s_103  （日、type 2/3/4）
     │  CalcYearlyAccumulatedValueCommand         （毎月）
     ▼
  s_104  （月、type 2）  ← CO2バッチがここを読み取る（alias "gas"）

売電（type 10）／買電（type 11）― 並行する2系統がいずれも s_102 に書き込む:
  (a) t_202（生ECHONET、売電方向 ― 太陽光パネルがある世帯のみ）
         │  CalcDailyAccumulatedValueCommand      （毎時；太陽光パネルがある世帯の場合にtype 10を書き込む）
         ▼
      s_102
  (b) CSV Xzilla IF1156、30分（外部システムXzillaが提供）
         │  RcvHalfHourElectricPowerCommand       （10分ごと ― cron `*/10 * * * *`；type 11は常に書き込み、太陽光パネルが無い世帯の場合はtype 10も書き込む）
         ▼
      s_102
  s_102  （時間、type 10/11）  ← (a)+(b) の2系統が合流
     │  CalcMonthlyAccumulatedValueCommand        （毎日）
     ▼
  s_103  （日、type 10/11）
     │  CalcYearlyAccumulatedValueCommand         （毎月）
     ▼
  s_104  （月、type 10/11）  ← CO2バッチがここを読み取る（alias "baiden"/"kaiden"）
```

出典: `legacy-batch_CalcTenMinutesEnergy.md`（2.1項）、`legacy-batch_CalcDailyEnergyConsumption.md`（2.2〜2.3項）、`legacy-batch_CalcDailyAccumulatedValueCommand.md`（2.3.1項）、`legacy-batch_CalcMonthlyAccumulatedValueCommand.md`（2.2, 2.8項）、`legacy-batch_CalcYearlyAccumulatedValueCommand.md`（2.2〜2.3, 2.7項）― 同一ドキュメント群。
