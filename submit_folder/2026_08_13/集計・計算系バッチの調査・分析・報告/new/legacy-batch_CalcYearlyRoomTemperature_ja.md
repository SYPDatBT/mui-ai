# 旧バッチ ― CalcYearlyRoomTemperatureCommand（年毎室温データ算出）

## 概要

`CalcYearlyRoomTemperatureCommand` は旧システム（EMINEL コンシェルジュサーバー）で**月1回**実行されるバッチであり、日次室温平均値テーブル（`s_103`、事前に `CalcMonthlyRoomTemperatureCommand` バッチが書き込み済み）の**1か月分の31日カラム**を、世帯×センサー位置（E0/E1）ごとに**1つの月次平均値**へ集約し、年次テーブル `s_104`（1行＝12カラム＝年内1か月ごとに1カラム）へ書き込む。対象月（デフォルトは前月）に加えて、後から到着／修正されるソースデータを補うため、その**直前の1か月分のみ**をさらに再計算（再集計）し、処理済みの `s_103` ソース行を「集計済み」として再度マーキングする。バッチはDBの読み書きのみを行う（メール送信・ファイル出力なし）。バッチ名に「Yearly」とあるのは、出力先テーブルが1行＝1世帯×1年×12月カラムという単位で**保存**するためであり、本バッチの**計算**単位はあくまで1か月である（1回の実行で計算・書き込みするのは常に2つの月カラム：対象月＋直前月）。実行スケジュール・SQL文・計算式、および本結果を再利用する他バッチの詳細は第2部に記載する。

## 第1部 ― 全体概要

| 項目 | 内容 |
|---|---|
| **役割** | 1か月分の日次室温平均値（`s_103` に既存）を世帯×センサー位置ごとに集約（多→一）して1つの月次平均値とし、アプリの年間室温履歴画面のソースデータとする。 |
| **Input** | DBの読み取りのみ、**外部API呼び出しなし・CSVファイル読み込みなし**：`t_101`（世帯一覧）＋ `s_103`（各世帯の日次室温平均値。`CalcMonthlyRoomTemperatureCommand` バッチが事前に算出済み、条件 `device_type=6`）＋ コマンドライン引数 `--yearmonth`。 |
| **Output** | **DB書き込みのみ** ― 結果のある世帯×センサー位置ごとに、`s_104`（エンティティ `ConSensorMonthlyValue`、共通ライブラリ `EminelSvLib` 経由）の**1つの年次行**内の**1つの月カラム**を書き込み／更新する。同時に `s_103` 上の `need_agg_complete_flag` フラグを更新し、集計済みの月次行としてマーキングする。メール送信・CSV出力なし。 |
| **処理概要** | 1. 「対象月」を決定する（パラメータ `--yearmonth`、デフォルト＝当月から1か月引いた月）。フォーマット不正の場合は即座にabort。<br>2. 対象月について、世帯×センサー位置ごとに `s_103` の31日カラムの合計値＋データのある日数をクエリで取得する。クエリエラーの場合は即座にabort（トランザクション未開始）。<br>3. トランザクションを開始し、データのある各世帯について、月次平均＝合計値／データのある日数を計算し、`s_104` の年次行の該当月カラムへ書き込む。取得済みの `s_103` 各行を集計済みとしてマーキングする。<br>4. 手順2〜3と同じ処理を、対象月の**直前1か月**についてのみ繰り返す（再計算）。<br>5. 手順3＋4はすべて1つのトランザクション内で実行し、トランザクション内のいずれかの書き込み／クエリ手順でエラーが発生した場合はrollbackする。 |

## 第2部 ― 詳細

### 2.1 実行スケジュールとパラメータ

| 項目 | 内容 | 出典 |
|---|---|---|
| 実行スケジュール（cron） | `20 5 1 * *`（/etc/cron.d形式、実行ユーザーは `root`）― 月1回、1日05:20に実行、**年間を通して**実行（季節による制限なし） | `docs/02_詳細設計/10_バッチ処理/mng-webap_cron設定_20241029.txt:52`（`#15.年毎室温データ算出` → `15_CalcYearlyRoomTemperature.sh`） |
| 実行コマンド | `php cake.php CalcYearlyRoomTemperature [--yearmonth=<yyyy-MM>]` | `CalcYearlyRoomTemperatureCommand.php:46,63` |
| `yearmonth` パラメータ（未指定時） | `現在 − 1か月`、フォーマット `yyyy/MM/01` | `CalcYearlyRoomTemperatureCommand.php:66-68` |
| `yearmonth` パラメータ（指定時） | 正規表現 `^[0-9]{4}-(0[1-9]|1[0-2])$` で `yyyy-MM` フォーマットを検証。フォーマット不正の場合 → ALERTログを出力後 `abort('failed validateCalcMonth')`（DBに触れる前） | `CalcYearlyRoomTemperatureCommand.php:70-81,414-425` |
| 対象月本体（`calculationMonth`） | ちょうど1か月分（その月の01日）で、`s_103` の月次行のキーとして使用 | `CalcYearlyRoomTemperatureCommand.php:88` |

### 2.2 対象月のデータ取得（`getSensorMonthlyValue`）

```sql
SELECT ConSensorDailyValues.c001, ConSensorDailyValues.c002, ConSensorDailyValues.c003, ConSensorDailyValues.c004
     , ConCustomers.c012 AS c111, ConCustomers.c042 AS c112
     , ConCustomers.c015 AS c113, ConCustomers.c016 AS c114, ConCustomers.c024 AS c115
     , COALESCE(c011,0)+COALESCE(c012,0)+ ... +COALESCE(c041,0) AS total        -- 31日カラムの合計、NULLは0扱い
     , (CASE WHEN c011 IS NULL THEN 0 ELSE 1 END)+ ... +(CASE WHEN c041 IS NULL THEN 0 ELSE 1 END) AS totalNumber  -- データのある日数
  FROM t_101 ConCustomers, s_103 ConSensorDailyValues
 WHERE ConCustomers.c001 = ConSensorDailyValues.c001
   AND ConSensorDailyValues.c002 = 6                    -- device_type = ROOM_TEMPERATURE
   AND ConSensorDailyValues.c004 = :targetDate          -- 対象月の月次行に一致 (yyyy/MM/01)
   AND ConCustomers.c052 IS NULL                          -- 論理削除されていない世帯
 ORDER BY ConSensorDailyValues.c001
```
出典: `CalcYearlyRoomTemperatureCommand.php:352-406`（31日カラムを合計するSQL文字列の生成は359-373行目、SQL文自体は375-393行目）。

**SQL文で使用するカラムの意味:**

| テーブル | カラム | 意味 |
|---|---|---|
| `t_101` | `c001` | 世帯コード（EMS-SP）― 結合キー |
| `t_101` | `c012`,`c042`,`c015`,`c016`,`c024` | 世帯グループの5属性（建物構造、暖房能力、床面積、人数、ガス自家発電）― そのまま `s_104` の `c111`〜`c115` にコピー |
| `t_101` | `c052` | 論理削除日時 ― `IS NULL` の場合は世帯が有効 |
| `s_103` | `c001` | 世帯コード ― 結合キー |
| `s_103` | `c002` | 機器種別 ― 固定で `= 6` を絞り込み |
| `s_103` | `c003` | センサー位置（0 = E0、1 = E1）― 1世帯につき最大2行、位置ごとに1行 |
| `s_103` | `c004` | 月次行 ― 対象月に一致するものを絞り込み |
| `s_103` | `c011`〜`c041` | 31個の日次平均温度値（月の1〜31日）、NULLの場合あり |

SQL文がエラーになった場合 → `resultCode = false` → **`io->abort('failed getSensorMonthlyValue')` を即座に実行、トランザクション開始前**（トランザクション内でのエラー時は `abort()` ではなく `rollback()` のみを呼ぶ点が異なる ― 2.6節を参照）。

### 2.3 平均値の算出と結果の書き込み ― 出力先テーブル `s_104`（`updateSensorYearlyValue`）

```
各結果行（1世帯×1センサー位置）について:
① total = 0 または totalnumber = 0 の場合 → スキップ、書き込みなし（コードは total ≠ 0 かつ totalnumber ≠ 0 の場合のみ書き込む。データのある日が存在しても合計がちょうど0の月はスキップされる）
② それ以外 → 月次平均 = total / totalnumber（最低データ日数のしきい値チェックは無し）
③ s_104 へ書き込み:
   - キー: ems_sp, device_type (= 6、s_103 の行から取得), room_id (0/1、s_103 の行から取得),
     date = calculationMonth を含む年（整数 yyyy）
   - 対応する月カラム: c0(calculationMonthの月 + 10) = 月次平均
     （例: calculationMonth = 3月 → カラム c013；12月 → カラム c022）
   - group_attr1〜5 = t_101 から取得した5つのグループ属性（2.2節）
   - modified = 現在時刻
④ 1世帯の書き込みでエラー（exception）が発生した場合 → ALERTログを出力、resultCode = false、ループは停止せず ― 残りの世帯への書き込みを継続
```
出典: `CalcYearlyRoomTemperatureCommand.php:292-344`。

ループ終了後、**`resultCode` が引き続き `true` の場合** → `updateSourceData`（2.4節）を呼び出し、ソースをマーキングする。すでに `false` の場合はソースマーキングの手順をスキップする。

### 2.4 ソース `s_103` の集計済みマーキング（`updateSourceData`）

```
クエリ手順（2.2節または2.5.1節）で取得した全ての行に対して実行する ―
2.3節／2.5.2節で total=0 または totalnumber=0 のためスキップされた行も含む:
① s_103（ConSensorDailyValue、s_104ではない）へ書き込み:
   - キー: ems_sp, device_type (= 定数 ROOM_TEMPERATURE = 6、固定値 ― データ行からは取得しない),
     room_id (データ行から取得), date = データ行の月次行そのもの (yyyy/MM/01)
   - need_agg_complete_flag = 2
   - modified = 現在時刻
② 1世帯の書き込みでエラー（exception）が発生した場合 → ALERTログを出力、resultCode = false、ループは停止せず ― 残りの世帯を継続
```
出典: `CalcYearlyRoomTemperatureCommand.php:187-217`。この関数は2つの分岐 ― `updateSensorYearlyValue`（2.3節）の後、および `updateRecalculationData`（2.5.2節）の後 ― の両方で共通して使用される。

### 2.5 直前1か月分の再計算

#### 2.5.1 再計算データの取得（`getRecalculationData`）

```sql
-- SQL構造は2.2節と同一、月の絞り込み条件のみ異なる:
...
   AND ConSensorDailyValues.c004 = :targetDate     -- (calculationMonth の月 − 1か月) の01日
...
```
- `targetDate` = (`calculationMonth` の月 − 1か月) の01日。`calculationMonth` が1月の場合、月の減算は自動的に前年12月へ繰り下がる。
- 取得するのは（範囲ではなく）**ちょうど1つの月次行**のみ ― `CalcMonthlyRoomTemperatureCommand`（「今月＋前月」の範囲を再計算）とは異なり、本バッチは正確に1か月分だけ遡る。

出典: `CalcYearlyRoomTemperatureCommand.php:225-283`（targetDateは230行目、SQL文は252-270行目）。

#### 2.5.2 再計算結果の `s_104` への書き込み（`updateRecalculationData`）

```
各結果行（1世帯×1センサー位置、calculationMonthの直前月に属する）について:
① total = 0 または totalnumber = 0 の場合 → スキップ、書き込みなし（コードは total ≠ 0 かつ totalnumber ≠ 0 の場合のみ書き込む。データのある日が存在しても合計がちょうど0の月はスキップされる）
② それ以外 → 月次平均 = total / totalnumber
③ s_104 へ書き込み（2.3節と同じキー／カラム構成）、ただし:
   - date = データ行の日付を含む年（そのデータ行自身のc004から取得、calculationMonthではない）
   - 対応する月カラム = c0(データ行の月 + 10)
④ 1世帯の書き込みでエラー（exception）が発生した場合 → CRITICALログを出力、resultCode = false、ループは停止せず ― 残りの世帯への書き込みを継続
```
出典: `CalcYearlyRoomTemperatureCommand.php:126-179`。

ループ終了後、`resultCode` が引き続き `true` であれば → `updateSourceData`（2.4節）を再度呼び出し、今度は**直前月**の `s_103` 行をマーキングする。

### 2.6 トランザクション

```
1. getSensorMonthlyValue（2.2節）― SQLエラーの場合 → 即座に io->abort()、トランザクション未開始、以降の手順は実行しない
2. トランザクション開始
3. updateSensorYearlyValue（2.3節、updateSourceData 2.4節を含む）― エラー → rollback（abort() は呼ばない。execute() 関数は最後まで実行を継続し「end」をログ出力）
4. getRecalculationData（2.5.1節）― エラー → rollback（abortなし）
5. updateRecalculationData（2.5.2節、updateSourceData 2.4節を含む）― エラー → rollback（abortなし）
6. 手順3〜5がすべて成功 → commit
```
出典: `CalcYearlyRoomTemperatureCommand.php:88-115`。

### 2.7 集計フローと結果利用機能

```
s_103  "ConSensorDailyValue"    1行/世帯/センサー位置/月  × 31日カラム   (device_type=6, room_id=0/1)
   │  CalcMonthlyRoomTemperatureCommand が書き込み（1日1回実行）
   │
   │  CalcYearlyRoomTemperatureCommand  (☚ 本分析対象のバッチ ― 月1回実行)
   │  (s_103の1か月分の日カラムを1つの月次平均値へ集約し、
   │   対象月分を計算＋直前1か月分を再計算)
   ▼
s_104  "ConSensorMonthlyValue"   1行/世帯/センサー位置/年  × 12か月カラム   (device_type=6, room_id=0/1)
   │
   │  GetUsageController (「使用量」画面／アプリ上の利用履歴API)
   │  device_type=ROOM_TEMPERATURE でs_104を読み取り、年間室温データを返却
   ▼
アプリ上に年間室温グラフを表示
```
出典: `GetUsageController.php:1961-2110`（`EminelSvLib.ConSensorMonthlyValues` を読み取り、`device_type = ROOM_TEMPERATURE` で絞り込み、view `YEARLY` に使用）。

本バッチは**通知を自ら送信することも、ポイント／報酬を自ら計算することもない** ― 設定温度系のフロー（`CalcYearlyPresetTemperatureCommand` → `DistributeMonthlyEcoPointsCommand`）とは異なり、本バッチの結果は表示用途にのみ使われる。
