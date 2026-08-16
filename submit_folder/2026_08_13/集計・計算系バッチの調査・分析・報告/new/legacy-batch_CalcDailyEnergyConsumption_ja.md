# 旧バッチ ― CalcDailyEnergyConsumptionCommand（日毎エネルギー使用量算出）

## 概要

`CalcDailyEnergyConsumptionCommand`は旧システム（EMINEL コンシェルジュサーバー）内で**1時間に1回**実行されるバッチで、2つの処理を行う。(1) 10分値のガスデータ（`s_101`に既に格納済み）を時間値に集約する処理、および(2) **世帯の消費電力量合計**（`消費電力量`）を時間ごとに算出する処理である。世帯には「消費電力量合計」を直接計測する電力量計は存在しない――家庭内で使用される電力は、系統からの買電＋自家発電（太陽光、ガス発電）＋蓄電池からの放電を合算し、そこから逆潮流（売電）分と蓄電池への充電分を差し引いたものであるため、この値は**個別に計測された6つの電力の流れを加減算する計算式によって導出**する必要があり、単一のセンサーから直接読み取ることはできない。この6つの電力の流れは、本バッチが実行される前に**別の2つのバッチ**（`CalcDailyAccumulatedValueCommand`、`RcvHalfHourElectricPowerCommand`）によって`s_102`に書き込まれる。本バッチはDBの読み書きのみを行い（メール送信・ファイル出力なし）、結果は`s_102`へ書き込まれる。実行スケジュール、SQL、計算式、業務定数の詳細は第2部に記載する。

## 第1部 ― 概要

| 項目 | 内容 |
|---|---|
| **役割** | (1) **ガス10分値→時間値**の集約（合計／給湯／暖房）。(2) 世帯の**消費電力量合計**（`消費電力量`）を時間ごとに算出――世帯にはこの量を直接計測する計器がないため、個別に計測された6つの電力の流れ（買電、売電、太陽光、ガス発電、蓄電池放電、蓄電池充電）を加減算する計算式によって値を導出する：`消費電力量合計 = 太陽光 + ガス発電 + 蓄電池放電 − 蓄電池充電 + 買電 − 売電`。この2つの処理はデータ上は独立しているが、1つのクラスにまとめられている。 |
| **入力** | DBの読み取りのみ、**外部API呼び出しなし、CSVファイル読み込みなし**：`t_101`（顧客一覧＋5つのグループ属性）＋`s_101`（ガス10分値、`CalcTenMinutesEnergyCommand`が書き込み）＋`s_102`（電力の時間値、`CalcDailyAccumulatedValueCommand`と`RcvHalfHourElectricPowerCommand`が書き込み）。 |
| **出力** | **DBへの書き込みのみ** — `s_102`（エンティティ`ConSensorHourlyValue`、共通ライブラリ`EminelSvLib`経由）：ガスの時間値（`c002 IN (2,3,4)`）および消費電力量合計の時間値（`c002 = 5`）。メール送信なし、CSV出力なし。 |
| **処理概要** | 1. `calculationTime`を決定する（デフォルトは`現在時刻−1時間`、または`--datetime`パラメータで指定）。<br>2. `gasConsumptionSummary()`：**193時間**（約8日間）分を遡って走査し、日付が変わるたびに`sum()`によるガス10分値→時間値の集約PIVOT SQLを1回実行し、`s_102`を上書きする。<br>3. (2)が成功した場合のみ、`calcPowerConsumption()`：顧客ごとに**24時間**分を遡って走査し、消費電力量合計の値が既にある時間帯はスキップする。<br>4. まだ値がない時間帯ごとに、`s_102`に既に存在する6つの構成要素（太陽光／ガス発電／蓄電池放電／蓄電池充電／買電／売電）を集め、6つ全て揃っていれば計算式を適用し、不足があれば`null`を書き込む。<br>5. 結果を`s_102`へ書き込む。顧客ごとに個別のトランザクションとする（いずれかの顧客でエラーが発生しても、ロールバックはその顧客に限定される）。 |

## 第2部 ― 詳細

### 2.1 実行スケジュールとパラメータ

| 項目 | 内容 | 出典 |
|---|---|---|
| 実行スケジュール（cron） | `45 * * * *` — 1時間に1回、45分に実行 | `docs/02_詳細設計/10_バッチ処理/mng-webap_cron設定_20241029.txt:19`（`6_CalcDailyEnergyConsumption.sh`） |
| 実行コマンド | `php cake.php CalcDailyEnergyConsumption [--datetime]` | `CalcDailyEnergyConsumptionCommand.php:43-48` |
| `calculationTime`のデフォルト基準 | `現在時刻 − 1時間` | `CalcDailyEnergyConsumptionCommand.php:64-66` |
| 再実行用パラメータ | `--datetime`（`yyyy-MM-ddTHH:mm:ss+09:00`形式）、正規表現でバリデーション、フォーマット不正時は`io->abort()` | `CalcDailyEnergyConsumptionCommand.php:67-74, 704-715` |
| 1回の実行内での順序 | `gasConsumptionSummary()` → `true`を返した場合のみ`calcPowerConsumption($calculationTime, 24)`を実行 | `CalcDailyEnergyConsumptionCommand.php:81-86` |

### 2.2 処理1 ― ガス10分値→時間値の集約（`gasConsumptionSummary`）

| 項目 | 内容 |
|---|---|
| 参照元 | `s_101`（`ConSensorMemoryValue`、10分値 — ガス合計／給湯／暖房、`c002 IN (2,3,4)`、`c003 = 0`） |
| 書き込み先 | `s_102`（`ConSensorHourlyValues`）、時間カラム`c011`~`c034`（00時台=c011 … 23時台=c034）に上書き。SQL集約結果の`measurement00`~`measurement23`はSELECT句のエイリアスであり、`s_102`の物理カラム名ではない |
| 再走査範囲 | 実行のたびに**193時間**（約8日間）分を遡る。SQLの再実行は**日付**が変わるタイミングのみ — 1回の実行あたり9回（193時間は9暦日にまたがる） | `CalcDailyEnergyConsumptionCommand.php:452-480` |
| トランザクション | 処理1全体が**単一のトランザクション**内で行われる — どの日付でエラーが発生しても`gasConsumptionSummary()`全体がロールバックされる | `CalcDailyEnergyConsumptionCommand.php:448-486` |

**集約SQL（`dailyDateAggregate`）** — 本質的には**`CASE WHEN`による時間別PIVOT**であり、対象日1日分について全顧客に対して実行される：

```sql
SELECT S.c001, S.c002, S.c003, S.c012, S.c042, S.c015, S.c016, S.c024,
       sum(S.c006_00) AS measurement00,   -- giờ 00
       sum(S.c006_01) AS measurement01,   -- giờ 01
       ...
       sum(S.c006_23) AS measurement23    -- giờ 23
  FROM (
        SELECT ConCustomers.c001, ConSensorMemoryValue.c002, ConSensorMemoryValue.c003,
               ConCustomers.c012, ConCustomers.c042, ConCustomers.c015,
               ConCustomers.c016, ConCustomers.c024,
               CASE WHEN date_part('hour', ConSensorMemoryValue.c004) = 0
                    THEN ConSensorMemoryValue.c006 ELSE null END AS c006_00,
               ... (lặp lại cho giờ 1 → 23) ...
          FROM t_101 ConCustomers
          JOIN s_101 ConSensorMemoryValue
            ON ConSensorMemoryValue.c002 IN (2, 3, 4)
           AND ConSensorMemoryValue.c003 = 0
           AND ConSensorMemoryValue.c004 >= :fromDate
           AND ConSensorMemoryValue.c004 <  :toDate
         WHERE ConCustomers.c001 = ConSensorMemoryValue.c001
           AND ConCustomers.c052 IS NULL
       ) AS S
 GROUP BY (S.c001, S.c002, S.c003, S.c012, S.c042, S.c015, S.c016, S.c024)
```
出典: `CalcDailyEnergyConsumptionCommand.php:574-696`。

1時間には最大6件の10分値レコード（`:00,:10,:20,:30,:40,:50`）が存在するため、`sum(c006_XX)`は**その時間内の6つの10分値の合計**であり — 平均値でも期末値でもない。

**遡及フラグ（`aggCompleteFlag`）** — `CalcDailyEnergyConsumptionCommand.php:499-508`:

```
calculationTimeとtargetDateの日付が異なる場合  → flag = 1  （遡及あり ― 過去日を補完中）
calculationTimeとtargetDateの日付が同じ場合    → flag = 2  （遡及なし ― 当日分）
```

ループ`for ($subHour = 0; $subHour < 193; $subHour++)`（`CalcDailyEnergyConsumptionCommand.php:452`）は、日付が変わるたびに`dailyDateAggregate()`を再度呼び出す。1回の呼び出しはその日全体について全顧客を対象とした`t_101 JOIN s_101`のスキャンであり、新規データがある顧客かどうかによる絞り込みは行わない — そのため実行のたびに（1時間ごとに）、バッチは直近8日分のガス値を全顧客分について再計算・上書きする。`s_101`は遅延してデータを受け取ることがあるため、実行のたびに8日分を再集計することで、時間値が常に最新の10分値データと整合する。

### 2.3 処理2 ― 消費電力量合計の算出（`calcPowerConsumption`）

世帯には「消費電力量合計」を直接計測する計器は1つも存在しない — 各電力の流れ（系統からの買電、逆潮流による売電、太陽光／ガスコージェネレーションによる自家発電、蓄電池の放電／充電）はそれぞれ専用の計器／センサーを持ち、別のバッチによって計測・差分計算され、時間単位で`s_102`に書き込まれる。`calcPowerConsumption`は顧客ごとにこの6つの時間値を読み取り、エネルギー収支の計算式に従って加減算し、その時間帯の消費電力量合計を算出する。

**計算式**（`calcConsumptionPower`、`CalcDailyEnergyConsumptionCommand.php:323-341`）：

```php
powerConsumption = device09        // 太陽光発電電力量 — mặt trời
                  + device08       // ガス発電電力量 — gas phát điện (Collemo/Enefarm)
                  + device12       // 蓄電池(放電量) — pin XẢ
                  - device13       // 蓄電池(充電量) — pin SẠC
                  + device11       // 買電量 — mua điện
                  - device10;      // 売電量 — bán điện
```

**6つの構成要素のうちいずれか1つでも**`null`の場合 → `powerConsumption = null`（推測しない、`0`に強制しない） — `CalcDailyEnergyConsumptionCommand.php:326-329`。

**6つの構成要素の出所**（`setRecalculationData`、`CalcDailyEnergyConsumptionCommand.php:351-405`）：

| # | 構成要素 | `device_type` | `s_102`への書き込みバッチ | 算出条件（顧客ごと） |
|---|---|---|---|---|
| 1 | 太陽光発電 | 9 | `CalcDailyAccumulatedValueCommand` | `c034`（太陽光パネル有無）`= 1`の場合のみ算出、それ以外はデフォルトの`0`を維持 |
| 2 | ガス発電 | 8 | `CalcDailyAccumulatedValueCommand` | `c024`（ガスコージェネレーション）`∈ {1,2}`の場合のみ算出、それ以外はデフォルトの`0`を維持 |
| 3 | 蓄電池放電 | 12 | `CalcDailyAccumulatedValueCommand` | `c035`（蓄電池有無）`= 1`の場合のみ算出、それ以外はデフォルトの`0`を維持 |
| 4 | 蓄電池充電 | 13 | `CalcDailyAccumulatedValueCommand` | 蓄電池がある場合のみ算出、それ以外はデフォルトの`0`を維持 |
| 5 | 買電 | 11 | `RcvHalfHourElectricPowerCommand`（Xzilla） | **必須、常にXzillaから** — `AGGREGATION_TYPE`内でtype 11を書き込むECHONET系統は存在しない |
| 6 | 売電 | 10 | `CalcDailyAccumulatedValueCommand` **または** `RcvHalfHourElectricPowerCommand` | `c034`（太陽光パネル）による — 太陽光パネルがある場合はECHONETから取得（逆方向計測）。太陽光なしの場合、`c024 = 1`（コレモ）かつ`c064`（受電地点特定番号）ありのときのみXzillaから取得し、それ以外は売電量を`0`として登録する |

構成要素1〜4は条件を満たさない場合、デフォルトで`0`となる（`CalcDailyEnergyConsumptionCommand.php:358-363`）。構成要素5〜6はデフォルトで`null`となる。

**再走査ループ：24時間、「入力が揃うまで待つ」方式** — `calcPowerConsumption($calculationTime, 24)`は最大24時間分を遡って走査する（`CalcDailyEnergyConsumptionCommand.php:98, 124-178`）。各時間帯について：

1. その時間帯の`device_type = 5`（消費電力量合計）に**既に値がある**場合 → スキップし、再計算しない（`setRecalculationData`は即座に`false`を返す — `CalcDailyEnergyConsumptionCommand.php:367-371`）。
2. まだない場合 → その時間帯について`s_102`に既に存在する6つの構成要素を集め、揃っていれば計算式を適用し、不足があれば`null`を書き込む。

ある構成要素が最終的に届かなかった場合（例：XzillaがCSVを送信しない）、その時間帯の`device_type = 5`は`null`のまま維持される — 一定の待機時間が経過した後に自動的に状態を遷移させる仕組みは存在しない。

**`roomId`には`DETECT_LIVING`の値が書き込まれる** — 消費電力量合計のレコードを書き込む際、コードは`setRoomId(DETECT_LIVING)`を呼び出す（`CalcDailyEnergyConsumptionCommand.php:218`）。`DETECT_LIVING`は人感センサー用のリビング（居間）を表す定数（値は`0`）であり、電力レコードにおいてこの値はリビングを意味しない — 電力の時間値レコードには「部屋」という概念自体が存在しない。

**グループ属性（`c111`~`c115`）** — すべての時間値レコードには、**書き込み時点**での顧客の5つのグループ属性が付与される：住宅タイプ（`c012`→`c111`）、暖房能力（`c042`→`c112`）、床面積（`c015`→`c113`）、世帯人数（`c016`→`c114`）、コージェネレーションタイプ（`c024`→`c115`） — `CalcDailyEnergyConsumptionCommand.php:220-224, 518-522`；カラムのマッピングは`eminel_sv_lib-develop/src/Model/Entity/ConSensorHourlyValue.php:59-63`で確認済み。これは**非正規化**データである — マスタデータを各ファクト行にコピーすることで、ランキング／グループ比較のレポートが読み取りのたびに`t_101`へJOINして戻る必要がないようにしている。

### 2.4 依存する2つのバッチ（概要のみ記載 ― 本バッチの対象範囲外）

`CalcDailyEnergyConsumptionCommand`は**最終的な組み立て地点**であり、電力データの発生源ではない。`s_102`に既に存在する6つのカラムを読み取り、計算式に従って加減算するだけであり、それには以下の2つのバッチによって6つ全てが埋められていることが前提となる：

| バッチ | 役割 | 差分計算方法 |
|---|---|---|
| `CalcDailyAccumulatedValueCommand` | 時間値を書き込む対象：ガス発電、太陽光、蓄電池放電／充電、（一部の）売電 — `t_202`（ECHONET生データ）を参照 | **2つのスナップショット**（時間の開始時点・終了時点）間の差分、`s_101`は経由しない |
| `RcvHalfHourElectricPowerCommand` | 時間値を書き込む対象：買電、（一部の）売電 — Xzillaの30分値CSV（`IF1156`）を取り込み | 30分単位の2区間を**単純加算**して1時間分にまとめる、ECHONETは経由しない |

### 2.5 関連する業務定数

| 定数 | 値 | 出典 |
|---|---|---|
| `device_type`（機器種別） | `5`=消費電力量, `8`=ガス発電, `9`=太陽光発電, `10`=売電, `11`=買電, `12`=蓄電池放電, `13`=蓄電池充電 | `const.php:182,186,188,190,192,194,196` |
| `AGGREGATION_TYPE` | `[GAS_POWER, SOLAR_GENERATION, SALE_ELECTRIC, BATTERY_DISCHARGE, DETECT_CNT]` — `BUY_ELECTRIC`は含まれない | `const.php:655` |
| 電力のCO2 | `0.499 kg/kWh`（`ELECTRIC_CO2_EMISSION_COEFFICIENT`） | `const.php:649` |
| ガスのCO2 | `2.09`（`GAS_CO2_EMISSION_COEFFICIENT`、単位は定数の原文のまま、使用時に要確認） | `const.php:651` |
| ガスの再走査ループ | 193時間（約8日間） | `CalcDailyEnergyConsumptionCommand.php:452` |
| 電力の再走査ループ | 24時間 | `CalcDailyEnergyConsumptionCommand.php:85` |

---

## 本資料の根拠

| 内容 | 根拠 |
|---|---|
| 処理1のロジック（ガス時間値） | `sources/conciergesv-develop/src/Command/CalcDailyEnergyConsumptionCommand.php::gasConsumptionSummary`（443-489行、574-696行） |
| 処理2のロジック（電力の組み立て） | `sources/conciergesv-develop/src/Command/CalcDailyEnergyConsumptionCommand.php::calcPowerConsumption`（98-341行、351-405行） |
| 実行スケジュール（cron） | `docs/02_詳細設計/10_バッチ処理/mng-webap_cron設定_20241029.txt:19` |
| 業務定数 | `sources/conciergesv-develop/config/const.php` |
| 書き込み先エンティティ | `sources/eminel_sv_lib-develop/src/Model/Entity/ConSensorHourlyValue.php` |
