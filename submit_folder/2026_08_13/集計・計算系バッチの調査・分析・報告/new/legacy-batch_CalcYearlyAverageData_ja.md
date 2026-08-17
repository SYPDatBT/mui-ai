# 旧バッチ ― CalcYearlyAverageDataCommand（年毎平均データ算出）

## 概要

`CalcYearlyAverageDataCommand` は、旧システム（EMINEL コンシェルジュサーバー）において**月1回**（cron: 毎月1日 16:10）実行されるバッチである。消費量指標の種類のうち1つ（ガス総合消費量／ガス給湯消費量／消費電力量／室内温度。コード上はエネルギー消費量も許容）について、**住宅属性（住宅種別、暖房能力、床面積、世帯人数、コージェネレーションの種類）が同じ非常に多数の世帯**の、直前に終了した**月**の消費量の値を**1つの代表平均値に集約**する――同系統の2バッチ `CalcDailyAverageDataCommand`（時間単位で算出、毎時実行）・`CalcMonthlyAverageDataCommand`（日単位で算出、毎日実行）と同じ仕組みであり、異なるのは保存単位が日／月ではなく**年**（月カラム12列）である点のみである。本バッチはDBの読み書きのみを行う（メール送信・ファイル出力は無し）。当月分の平均算出に加えて、過去のデータが不足していた月を補うため、最大で約1年前まで遡って再計算する**遡及（retroactive）処理**も行う。SQL・計算式・業務上の定数の詳細は第2部に記載する。

## 第1部 ― 概要

| 項目 | 内容 |
|---|---|
| **役割** | 消費量指標の種類のうち1つについて、**住宅属性が同じ多数の世帯を1つの代表平均値に月単位で集約する**（個々の世帯ごとに算出するのではない）――この数値はアプリが特定の世帯の実際の消費量と比較するための「グループのベンチマーク」となる値である。あわせて、世帯データの到着が遅れた場合に過去の月を遡って再計算する。 |
| **Input** | DBの読み取りのみで、外部APIの呼び出しやCSVファイルの読み込みは無い： `s_104`（**各世帯**の月ごとの値。他のバッチで算出済みであり、`t_101` から非正規化された5つのグループ属性を伴う）＋ `s_114` **自身のテーブル**（「グループの母数」――該当月に各グループへ属する世帯数を照会するために再利用。条件は `device_type=16`）＋ コマンドライン引数 `--type`、`--datetime`。 |
| **Output** | `s_114`（エンティティ `ConSensorMonthlyAveValue`）へ書き込む。各レコードは**類似世帯グループ1つ×1年**に対応し、平均値は該当する月カラムに書き込まれる。**これがまさにアプリが特定世帯の消費量と比較するために使う「あなたと似た世帯の平均」の月次データ**である――本バッチはこの数値を生成するのみであり、`s_114` を読み取ってアプリへ表示する処理は別のAPI／バッチが担う（本コマンドの対象範囲外）。メール送信・CSV出力は無い。 |
| **処理概要** | 1. パラメータ `type`（指標の種類）＋ `datetime`（デフォルト＝システムの現在月の1か月前）を受け取り、バリデーションを行う。<br>2. トランザクションを1つ開始し、`s_104` から**詳細グループ**（5属性、バケット統合あり）単位で該当する月カラムの平均を算出する。ただし報告済み世帯数が `s_114` から照会した「グループの母数」の70%以上の場合のみ書き込む。<br>3. 続けて、**より広く統合したグループ**（5属性のうち3属性を省略し「999」グループへ統合）単位の平均を算出する――こちらは閾値チェックなしで書き込み、フォールバック手段とする。<br>4. 最大約1年前まで遡及：月カラムが `NULL` のままのグループについて、該当する月の期間で `s_104` から平均を再計算し更新する。<br>5. 全ステップが成功すればコミットし、失敗した場合は全体をロールバックする。 |

## 第2部 ― 詳細

### 2.1 実行スケジュールとパラメータ

| 項目 | 内容 | 出典 |
|---|---|---|
| 実行スケジュール（cron） | `10 16 1 * *` ― 月1回、毎月1日16:10（`type2_3_5_6` の種別向け） | `docs/02_詳細設計/10_バッチ処理/mng-webap_cron設定_20241029.txt:61-62` (`#18.年毎平均データ算出` → `18_CalcYearlyAverageData_type2_3_5_6.sh`) |
| 実行コマンド | `php cake.php CalcYearlyAverageData --type=<集計種別> [--datetime=<算出日時>]` | `CalcYearlyAverageDataCommand.php:39-45` |
| パラメータ `type` | 1文字 ― コード（`checkValidate`）上は次の5つの値を受け付ける：`1`=エネルギー消費量、`2`=ガス総合消費量、`3`=ガス給湯消費量、`5`=消費電力量、`6`=室内温度。ただしcronを実行するシェルスクリプトのファイル名（`type2_3_5_6`）には`2,3,5,6`の4つの値のみが記載されており、`1`は含まれない | `CalcYearlyAverageDataCommand.php:89-113`; 定数は `config/const.php:174,176,178,182,184` |
| パラメータ `datetime` | 書式 `yyyy-MM`。省略した場合 → 現在 − 1か月（`yyyy-MM`） | `CalcYearlyAverageDataCommand.php:62-65,102-108` |
| バリデーション | `type` が不正（上記5つの値に該当しない、または1文字でない）、または `datetime` の書式が不正な場合 → `checkValidate()` が `false` を返す → `io->abort()` により、バッチは即座に停止する | `CalcYearlyAverageDataCommand.php:67-72,89-113` |
| 主処理 | `CalcCommonAverageDataCommand::executeCommon($type, $dateTime, 3)` を呼び出す ― 引数 `3` は「年の中の月単位」という集計単位を表す（時間／日単位のバッチとコードを共有しており、それらは `1`／`2` を渡す） | `CalcYearlyAverageDataCommand.php:74-77` |

### 2.2 「年」単位に対応する集計パラメータ（`aggregationUnit = 3`）

| パラメータ | 値 | 意味 |
|---|---|---|
| `targetDateTime` | パラメータ `datetime` に文字列 `'-01 00:00:00'` を連結してパースする。`datetime` が空の場合は現在 − 1か月とする | 平均を算出する対象月 |
| `targetDateCondition` | `targetDateTime` の `yyyy` | `s_114` で更新すべき年の行 |
| `aggregateColumn` | `c0{月+10}`（1月 → `c011`、12月 → `c022`） | 平均値を書き込む月カラム |
| `sourceTable` | `s_104`（`ConSensorMonthlyValue`、各世帯の月ごとの値） | 平均算出のためのデータ元 |
| `destinationTable` | `s_114`（`ConSensorMonthlyAveValue`） | 結果を書き込む先のテーブル |
| `retroactiveTable` | `s_114`（書き込み先テーブル自身） | 前月分のデータが不足しているグループを検索するために使用 |
| `previousColum` | `targetDateTime` の直前の月カラム | 遡及対象のグループを絞り込む条件 |

出典：`CalcCommonAverageDataCommand.php:1292-1317`。

### 2.3 5つのグループ属性（`c111`~`c115`）の意味

`s_104` の各月次レコードには、類似世帯グループへの統合に用いる5つの属性――住宅種別、暖房能力、床面積、世帯人数、コージェネレーションの種類（それぞれ `c111`~`c115` にマッピング）――が（世帯情報 `t_101` から非正規化されて）あらかじめ付与されている。平均を算出する際、これらの属性は `GROUP BY` の前に、より粗いバケットへ統合される（2.4参照）――バケット統合のロジックは同系統の2バッチ（Daily／Monthly）とまったく同じである。

### 2.4 ステップ1 ― 詳細グループの平均（`updateGroupAverage`）

```sql
-- Truy vấn con: chuẩn hoá/gộp bucket cho từng thuộc tính nhóm
SELECT c002, c003, {periodColumn},
       c111,
       CASE WHEN c112 IN (1,2,3) THEN c112 ELSE 201 END AS c112,
       CASE WHEN c113 IN (1,2,3) THEN 301
            WHEN c113 IN (5,6)   THEN 302
            ELSE c113 END AS c113,
       CASE WHEN c114 IN (1,2) THEN 401
            WHEN c114 IN (3,4) THEN 402
            ELSE 403 END AS c114,
       CASE WHEN c115 IN (1,2) THEN c115 ELSE 501 END AS c115,
       {aggregateColumn}
  FROM {sourceTable}   -- s_104
 WHERE c002 = :type
   AND {periodColumn} = :targetDateCondition
   AND c111 IN (1,2) AND c112 IN (1,2,3,4,9) AND c113 IN (1,2,3,4,5,6)
   AND c114 IN (1,2,3,4,5,6) AND c115 IN (1,2,9,10)
   AND {aggregateColumn} IS NOT NULL

-- Truy vấn ngoài: AVG + COUNT theo nhóm đã gộp bucket
SELECT c002, c003, {periodColumn}, c111, c112, c113, c114, c115,
       AVG({aggregateColumn}) AS {aggregateColumn},
       COUNT({aggregateColumn}) AS count
  FROM (<truy vấn con trên>) AS sensorInfo
 GROUP BY c002, c003, {periodColumn}, c111, c112, c113, c114, c115
```
出典：`CalcCommonAverageDataCommand.php:1156-1228`（`getGroupAverageCalculation`）。

**書き込み前のデータ充足チェック**（`checkGroupDataNum`、このステップのみに適用）：
- 各グループについて、`s_114` **自身のテーブル**から「グループの母数」（グループに属する世帯の総数。他のバッチで算出済み）を照会する ― 条件は `device_type = 16`（「世帯数」を表す疑似コード）、5つのグループ属性の一致、年の行（整数型の年の値）＋該当する月カラム。
- `count`（報告済み世帯数）／グループの母数 × 100 が `AVERAGE_CALCULATION_THRESHOLD`（**70**）未満の場合 → このグループはステップ1でスキップし、書き込まない。
- グループの母数が0の場合 → 同様にスキップする。

出典：`CalcCommonAverageDataCommand.php:1039-1149`（年の分岐（`case 3`）は`1086-1092`）；定数 `AVERAGE_CALCULATION_THRESHOLD` は `config/const.php:599`。

閾値を満たしたグループ → `s_114` へ1レコードを書き込み／更新する（キー：`device_type`、`room_id`、年の行（`c003`、整数型にキャストしたもの ― 日付型の日・月の行を書き込むDaily／Monthlyとは異なる）、バケット統合済みの5つのグループ属性）。平均値は該当する月カラム（`aggregateColumn`）にセットする。

### 2.5 ステップ2 ― より広く統合したグループの平均（`updatePartGroupAverage`）

ステップ1の直後に続けて実行され、より粗い統合方法を用いる：`c111` はそのまま保持し、`c112` は `1/2/3` または `201` へ統合、**`c113`、`c114`、`c115` は固定で `999`**（無視し、住宅種別が同じ世帯はすべて1つの広いグループとみなす）。このステップは**70%の閾値チェックを行わない**――広いグループには常に上書きで書き込み、ステップ1の詳細グループでデータが不足している場合のフォールバックとする。

出典：`CalcCommonAverageDataCommand.php:868-943`（`updatePartGroupAverage`、`getPartGroupAverageCalculation`）。

### 2.6 ステップ3 ― 最大約1年前までの遡及（`retroactiveYearly`）

- `s_114` の中で、算出対象月の直前の月カラムがまだ `NULL` のままであるグループの一覧を取得する（`getTargetGroup`、条件は `previousColum IS NULL`）。
- 各グループについて、1か月ずつ遡って（ループの技術的な上限は24か月だが、実際は `retroactiveLimit` = [算出対象年 − 1] の年で打ち切られる）、データが不足している月を探す。
- 別の年に遡る際は、`s_114` の該当する年の行を改めて読み込み（`getAggregationTarget`）、その年のどの月カラムがまだ `NULL` かを確認する。
- データが不足している月については：該当する年＋グループについて `s_104` から平均を再計算し（`getRetroactiveData` ― ステップ1と同じグループ単位のAVGロジックだが、`s_114` にすでに保存されているグループ属性の条件を用い、バケットの再統合は行わない。時間条件は**年**のみで一致を見て、月では区切らない）、`s_114` へ上書きする（`updateRetroactiveData`、不足している月カラムの範囲を更新）。
- あるグループについて、データが存在する月（`NULL` でない月）に遭遇した時点で、それ以上遡るのを停止する。

出典：`CalcCommonAverageDataCommand.php:139-219`（`retroactiveYearly`）、`550-573`（`getRetroactiveUpdatePeriod`、年の分岐）、`645-658`（`getRetroactiveData`、年の分岐）、`758-815`（`getAggregationTarget`）。

### 2.7 トランザクションと業務定数

- 3つのステップ（2.4 → 2.6）はすべて、実行1回につき**1つのトランザクション**の中で行われる：いずれかのステップがエラーを返した場合 → `rollback()`；3ステップすべてが成功した場合のみ `commit()`。
- 本バッチは自ら通知を送信しない。`s_114` のデータは、アプリ上で「類似世帯との比較」を表示するために他のAPI／バッチが読み取る（本コマンドの対象範囲外）。
- テーブル `s_114`（エンティティ `ConSensorMonthlyAveValue`）は**年**単位で保存される（1行＝1年×月カラム12列）――同系統の2バッチと同様、命名は算出単位ではなく保存単位に基づく。本バッチが算出・書き込みを行う粒度は**月**であり、実行1回につきちょうど1カラムである。
- Daily／Monthly（この2バッチは「グループの母数」の照会元として共通の1テーブル `s_113` を使用する）とは異なり、Yearlyバッチは「グループの母数」を `s_114` **自身のテーブル**から照会し、`s_113` は使用しない。

| 定数 | 値 | 出典 |
|---|---|---|
| `ENERGY_CONSUMPTION` | 1 ― エネルギー消費量（`checkValidate` では許容されるが、cronを実行するシェルスクリプトのファイル名には含まれない） | `const.php:174` |
| `GAS_CO_TYPE_CONSUMPTION` | 2 ― ガス総合消費量 | `const.php:176` |
| `GAS_WATER_HEAT_RATE` | 3 ― ガス給湯消費量 | `const.php:178` |
| `POWER_CONSUMPTION` | 5 ― 消費電力量 | `const.php:182` |
| `ROOM_TEMPERATURE` | 6 ― 室内温度 | `const.php:184` |
| `AVERAGE_CALCULATION_THRESHOLD` | 70（%） ― 詳細グループを書き込むためのデータ充足閾値 | `const.php:599` |
