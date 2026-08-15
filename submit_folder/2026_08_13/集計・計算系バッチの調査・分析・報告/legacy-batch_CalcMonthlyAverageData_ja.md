# 旧バッチ ― CalcMonthlyAverageDataCommand（月毎平均データ算出）

## 概要

`CalcMonthlyAverageDataCommand` は、旧システム（EMINEL コンシェルジュサーバー）において**1日1回**（cron 15:10）実行されるバッチである。4種類の指標（ガス総合消費量/ガス給湯消費量/消費電力量/室内温度）のそれぞれについて、本バッチは**同じ住宅属性を持つ非常に多くの世帯**（住宅種別、暖房能力、床面積、世帯人数、コジェネレーション種別）**の「直前に終了した1日」分の消費量を1つの平均値に集約し、グループ全体を代表する数値とする**――同系統のバッチ`CalcDailyAverageDataCommand`（時間単位で実行、別資料参照）と同じ仕組みであり、集計単位が「時間」ではなく「日」である点のみが異なる。本バッチはDBの読み書きのみを行い（メール送信・ファイル出力はなし）、当日分の平均算出に加えて、以前データが不足していた日を補うために最大約1か月前まで**遡及（retroactive）**して再計算する。SQL・計算式・業務定数の詳細は第2部に記載する。

## 第1部 ― 概要

| 項目 | 内容 |
|---|---|
| **役割** | 4種類の消費指標のうち1つについて、**同じ住宅属性を持つ多数の世帯を1日単位で1つの平均値に集約する**（世帯ごとに個別算出するのではない）――この数値はアプリが特定の1世帯の実消費量と比較するための「グループのベンチマーク」であり、あわせて世帯データの到着が遅れた場合には過去の日付を遡って再計算する。 |
| **Input** | DBの読み取りのみ（**外部API呼び出しなし、CSVファイル読み込みなし**）：`s_103`（**世帯ごと**の日次値、別バッチで算出済み、`t_101`から非正規化された5つのグループ属性付き）＋ **同じ** `s_113` テーブル（該当日における各グループの「グループ分母」＝所属世帯数を参照するために再利用、条件 `device_type=16`）＋ コマンドライン引数 `--type`、`--datetime`。 |
| **Output** | `s_113`（エンティティ `ConSensorDailyAveValue`）へ書き込む。各レコードは**1つの類似世帯グループ×1か月**であり、平均値は該当する日付カラムに書き込まれる。**これは日次の「あなたと似た世帯の平均」データそのもの**であり、アプリが特定世帯の消費量と比較する際に使用する――本バッチはこの数値を生成するのみで、`s_113`を読み取ってアプリへ表示するのは別のAPI／バッチの役割（本コマンドの対象外）。メール送信・CSV出力はなし。 |
| **処理概要** | 1. パラメータ `type`（指標種別）＋ `datetime`（未指定時＝システム現在日 − 1日）を受け取り、バリデーションを行う。<br>2. トランザクションを開始し、`s_103`から**詳細グループ**（5属性、バケット化あり）単位で該当日カラムの平均を算出する。書き込むのは、報告世帯数が`s_113`から参照した「グループ分母」の70%以上の場合のみ。<br>3. 続けて**より粗いグループ**（5属性のうち3属性を省略し「999」グループへ集約）単位で平均を算出する――こちらは**閾値チェックなし**で書き込み、フォールバックとする。<br>4. 最大約1か月前まで遡及：日付カラムがNULLのままのグループについて、該当期間の`s_103`から平均を再計算し更新する。<br>5. 全ステップが成功した場合のみコミット、失敗時は全体をロールバックする。 |

## 第2部 ― 詳細

### 2.1 実行スケジュールとパラメータ

| 項目 | 内容 | 出典 |
|---|---|---|
| 実行スケジュール（cron） | `10 15 * * *` ― 1日1回、15:10（4種類すべて対象、`type2_3_5_6`） | `docs/02_詳細設計/10_バッチ処理/mng-webap_cron設定_20241029.txt:36-37` (`#11.月毎平均データ算出` → `11_CalcMonthlyAverageData_type2_3_5_6.sh`) |
| 実行コマンド | `php cake.php CalcMonthlyAverageData --type=<集計種別> [--datetime=<算出日時>]` | `CalcMonthlyAverageDataCommand.php:39-45` |
| パラメータ `type` | 1文字――次の4種類の値のいずれか1つのみ：`2`=ガス総合消費量、`3`=ガス給湯消費量、`5`=消費電力量、`6`=室内温度 | `CalcMonthlyAverageDataCommand.php:89-109`、定数は`config/const.php:176,178,182,184` |
| パラメータ `datetime` | フォーマットは`yyyy-MM-dd`。省略時→`現在 − 1日`（`yyyy-MM-dd`） | `CalcMonthlyAverageDataCommand.php:62-65,101-107` |
| バリデーション | `type`が不正、または`datetime`のフォーマットが不正 → `checkValidate()`が`false`を返す → `io->abort()`、バッチは即座に停止 | `CalcMonthlyAverageDataCommand.php:68-72,89-112` |
| メイン処理 | `CalcCommonAverageDataCommand::executeCommon($type, $dateTime, 2)`を呼び出す――パラメータ`2`は「月内の日単位」の集計単位を表す（時間／年単位のバッチとコードを共通化しており、その場合は`1`／`3`を渡す） | `CalcMonthlyAverageDataCommand.php:74-77` |

### 2.2 「月」単位（`aggregationUnit = 2`）に対応する集計パラメータ

| パラメータ | 値 | 意味 |
|---|---|---|
| `targetDateTime` | パラメータ`datetime`に文字列`'00:00:00'`をそのまま（間にスペースを入れず）連結してからパースする。`datetime`が空の場合は`現在 − 1日` | 平均を算出する対象日 |
| `targetDateCondition` | `targetDateTime`の`yyyy/MM/01` | `s_113`内で更新対象となる月の行 |
| `aggregateColumn` | `c0{日+10}`（1日→`c011`、31日→`c041`） | 平均値を書き込む日付カラム |
| `sourceTable` | `s_103`（`ConSensorDailyValue`、世帯ごとの日次値） | 平均算出に使用するデータソース |
| `destinationTable` | `s_113`（`ConSensorDailyAveValue`） | 結果を書き込む対象テーブル |
| `retroactiveTable` | `s_113`（書き込み先と同一テーブル） | 前日分のデータが不足しているグループを検索するために使用 |
| `previousColum` | `targetDateTime`の直前の日付カラム | 遡及対象グループを絞り込む条件 |

出典：`CalcCommonAverageDataCommand.php:1267-1291`。

### 2.3 5つのグループ属性（`c111`~`c115`）の意味

`s_103`の各日次レコードには、類似世帯グループへの集約に用いる5つの属性――住宅種別、暖房能力、床面積、世帯人数、コジェネレーション種別（それぞれ`c111`~`c115`にマッピング）――が、世帯情報`t_101`から非正規化された形であらかじめ付与されている。平均を算出する際は、`GROUP BY`の前にこれらの属性がより粗い**バケット**へ集約される（2.4参照）。

出典：`sources/eminel_sv_lib-develop/src/Model/Entity/ConSensorDailyValue.php`（`c111`~`c115`の宣言）。

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
  FROM {sourceTable}   -- s_103
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

**書き込み前のデータ充足チェック**（`checkGroupDataNum`、このステップにのみ適用）：
- 各グループについて、「グループ分母」（そのグループに属する世帯の総数、別バッチで算出済み）を**同じ**`s_113`テーブルから参照する――条件は`device_type = 16`（「世帯数」を表す擬似コード）、5つのグループ属性の一致、月の行（`yyyy/MM/01`）＋該当する日付カラム。
- `count`（報告済み世帯数）／グループ分母 × 100 < `AVERAGE_CALCULATION_THRESHOLD`（**70**）の場合 → ステップ1では、このグループを**スキップし書き込まない**。
- グループ分母 = 0 の場合 → 同様にスキップする。

出典：`CalcCommonAverageDataCommand.php:1066-1149`。定数`AVERAGE_CALCULATION_THRESHOLD`は`config/const.php:599`。

閾値を満たしたグループ → `s_113`へ1レコードを書き込み／更新する（キー：`device_type`、`room_id`、月の行（`c003`）、バケット化済みの5つのグループ属性）。平均値は該当する日付カラム（`aggregateColumn`）にセットする。

### 2.5 ステップ2 ― より粗いグループの平均（`updatePartGroupAverage`）

ステップ1の直後に実行され、**より粗い**集約方法を用いる：`c111`はそのまま保持し、`c112`は`1/2/3`または`201`へ集約する。**`c113`、`c114`、`c115`は固定で`999`**（無視し、同じ住宅種別のすべての世帯を1つの広いグループとみなす）。このステップは**70%の閾値チェックを行わず**、常に広いグループを上書きする――ステップ1の詳細グループでデータが不足している場合のフォールバックとなる。

出典：`CalcCommonAverageDataCommand.php:868-943`（`updatePartGroupAverage`、`getPartGroupAverageCalculation`）。

### 2.6 ステップ3 ― 最大約1か月前までの遡及（`retroactiveMonthly`）

- 算出中の日付の**直前**の日付カラムが`NULL`のままになっている`s_113`内のグループ一覧を取得する（`getTargetGroup`、条件`previousColum IS NULL`）。
- 各グループについて、1日ずつ遡り（ループの技術的な上限は62日だが、実際の上限は`retroactiveLimit` ＝［算出中の月 − 1か月］の01日で打ち切られる）、データが不足している日を探す。
- 別の月へ遡る際は、`s_113`内の該当する月の行を読み直し（`getAggregationTarget`）、その月のどの日付カラムが`NULL`のままかを確認する。
- データが不足している日については、該当する月・グループについて`s_103`から平均を再計算し（`getRetroactiveData`――ステップ1と同じグループ別AVGロジックだが、`s_113`にすでに保存されているグループ属性の条件をそのまま使い、バケット化はし直さない）、`s_113`へ上書きする（`updateRetroactiveData`）。
- あるグループについて、データが存在する日（`NULL`でない日）に到達した時点で、そのグループの遡りは即座に停止する。

出典：`CalcCommonAverageDataCommand.php:112-132,226-310,591-815`。

### 2.7 トランザクションと業務定数

- 3つのステップ（2.4→2.6）はすべて、**1回の実行につき1つのトランザクション**の中で行われる：いずれかのステップがエラーを返した場合→`rollback()`。3ステップすべてが成功した場合のみ`commit()`。
- 本バッチは**自ら通知を送信しない**。`s_113`のデータは、アプリ上で「類似世帯との比較」を表示するために他のAPI／バッチから読み取られる（本コマンドの対象外）。
- テーブル`s_113`（エンティティ`ConSensorDailyAveValue`、コード中のコメントは「月毎平均センサ情報 Entity」）は**月**単位で格納される（1行＝1か月×31の日付カラム）――`CalcDailyAccumulatedValueCommand`（資料`legacy-batch_CalcDailyAccumulatedValueCommand.md`のTóm tắt項目を参照）と同様に、格納単位（算出単位ではない）に基づいた命名となっている。本バッチが算出・書き込みを行う値の粒度は**日**であり、1回の実行につきちょうど1カラムを更新する。

| 定数 | 値 | 出典 |
|---|---|---|
| `GAS_CO_TYPE_CONSUMPTION` | 2 — ガス総合消費量 | `const.php:176` |
| `GAS_WATER_HEAT_RATE` | 3 — ガス給湯消費量 | `const.php:178` |
| `POWER_CONSUMPTION` | 5 — 消費電力量 | `const.php:182` |
| `ROOM_TEMPERATURE` | 6 — 室内温度 | `const.php:184` |
| `AVERAGE_CALCULATION_THRESHOLD` | 70（%） ― 詳細グループを書き込むためのデータ充足閾値 | `const.php:599` |
