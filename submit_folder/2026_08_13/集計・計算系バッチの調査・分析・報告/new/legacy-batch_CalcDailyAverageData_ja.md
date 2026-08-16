# 旧バッチ ― CalcDailyAverageDataCommand（日毎平均データ算出）

## 概要

`CalcDailyAverageDataCommand` は、旧システム（EMINELコンシェルジュサーバー）において毎時（55分）定期的に実行されるバッチである。4種類の指標（ガス総合消費量/ガス給湯消費量/消費電力量/室内温度）のそれぞれについて、このバッチは**直前に終了した1時間分の消費量を、同じ住宅属性（住宅タイプ、暖房能力、床面積、世帯人数、コジェネレーションの種類）を持つ非常に多数の世帯から集約し、そのグループを代表する1つの平均値にまとめる**――これは世帯同士を比較するものではなく、アプリが特定の1世帯の消費量を類似グループの平均値と並べて表示する際に用いる「あなたと似た世帯の平均」という指標を作り出すものである。バッチはDBの読み書きのみを行う（メール送信・ファイル出力は行わない）。現在時刻分の平均計算に加えて、以前データが不足していた過去の時間帯を補うため、バッチは最大7日前まで**遡及（retroactive）**して再計算を行う。SQL・計算式・業務上の定数の詳細は第2部に示す。

## 第1部 ― 概要

| 項目 | 内容 |
|---|---|
| **役割** | 4種類の消費指標のうち1つについて、**同じ住宅属性を持つ多数の世帯を、時間単位で1つの平均値に集約する**（各世帯ごとに個別計算するのではない）――この数値はアプリが特定の1世帯の実際の消費量と比較するための「グループのベンチマーク」である。あわせて、世帯データが遅れて到着した場合には過去の時間帯を遡って再計算する。 |
| **入力** | DBの読み取りのみ、**外部APIは呼び出さず、CSVファイルも読み込まない**：`s_102`（**各世帯**の時間別の値。別バッチによって事前に算出済みで、`t_101`から非正規化された5つのグループ属性が付随する）＋ `s_113`（`ConSensorDailyAveValue`――グループ別の日毎平均テーブルで、「グループの母数」の置き場を兼ねる：グループ集計情報登録バッチ（CreateGroupSummaryCommand）がdevice_type=16の行として各グループの世帯数を事前に書き込み、本バッチはしきい値判定のためにその行を読み取るのみ）＋ コマンドライン引数 `--type`, `--datetime`。 |
| **出力** | `s_112`（エンティティ`ConSensorHourlyAveValue`）へ書き込む。各レコードは**類似世帯グループ1つ × 1日**に対応し、平均値は該当する時間帯のカラムに書き込まれる。**これがまさにアプリで「あなたと似た世帯の平均」として使われる数値**であり、特定の1世帯の消費量と比較する際に用いられる――本バッチは数値を生成するのみであり、`s_112`を読み取ってアプリに表示する処理は別のAPI/バッチが担う（本コマンドの対象外）。メール送信・CSV出力は行わない。 |
| **処理概要** | 1. 引数`type`（指標種別）＋`datetime`（デフォルト＝現在のシステム時刻 − 1時間）を受け取り、バリデーションを行う。<br>2. トランザクションを1つ開始し、`s_102`から**詳細グループ**（5属性、バケット丸めあり）ごとに該当時間カラムの平均を計算する。報告済み世帯数が`s_113`から引いた「グループの母数」の70%以上の場合のみ書き込む。<br>3. 続けて**より広く集約したグループ**（5属性のうち3つを省略し「999」グループにまとめる）の平均を計算する――このステップは**しきい値チェックなしで**常に書き込み、フォールバック手段とする。<br>4. 最大7日前まで遡及する：該当カラムがまだNULLのグループについては、その時間帯の平均を`s_102`から再計算して更新する。<br>5. すべてのステップが成功すればコミットし、そうでなければ全体をロールバックする。 |

## 第2部 ― 詳細

### 2.1 実行スケジュールとパラメータ

| 項目 | 内容 | 出典 |
|---|---|---|
| 実行スケジュール（cron） | `55 * * * *` ― 毎時55分にcronが1回起動し、シェルスクリプト内でコマンドを4回逐次実行（`--type=2→3→5→6`、各回1種別） | `docs/02_詳細設計/10_バッチ処理/mng-webap_cron設定_20241029.txt:21-22`（`#7.日毎平均データ算出` → `7_CalcDailyAverageData_type2_3_5_6.sh`） |
| 実行コマンド | `php cake.php CalcDailyAverageData --type <集計種別> [--datetime <算出日時>]` | `CalcDailyAverageDataCommand.php:39-45` |
| `type`パラメータ | 1文字――4つの値のいずれか1つのみ受け付ける：`2`=ガス総合消費量, `3`=ガス給湯消費量, `5`=消費電力量, `6`=室内温度 | `CalcDailyAverageDataCommand.php:96-114`、定数は`config/const.php:176,178,182,184` |
| `datetime`パラメータ | 形式`yyyy-MM-ddTHH:00:00+09:00`；省略した場合→`現在時刻 − 1時間` | `CalcDailyAverageDataCommand.php:62-66,104-113` |
| バリデーション | `type`が不正、または`datetime`のフォーマットが不正な場合→`checkValidate()`が`false`を返す→`io->abort()`によりバッチは直ちに停止する | `CalcDailyAverageDataCommand.php:68-75,92-117` |
| メイン処理 | `CalcCommonAverageDataCommand::executeCommon($type, $dateTime, 1)`を呼び出す――引数`1`は集計単位「日内の時間別」を意味する（月次／年次バッチとコードを共用しており、それぞれ`2`／`3`を渡す） | `CalcDailyAverageDataCommand.php:77-80` |

### 2.2 単位「日」（`aggregationUnit = 1`）に対応する集計パラメータ

| パラメータ | 値 | 意味 |
|---|---|---|
| `targetDateTime` | パラメータ`datetime`、または空の場合`現在時刻 − 1h` | 平均を計算する対象の時間 |
| `targetDateCondition` | `targetDateTime`の`yyyy/MM/dd` | `s_112`で更新すべき日付 |
| `aggregateColumn` | `c0{時+11}`（0時→`c011`、23時→`c034`） | 平均値を書き込むべき時間カラム |
| `sourceTable` | `s_102`（`ConSensorHourlyValue`、各世帯の時間別の値） | 平均計算のためのデータソース |
| `destinationTable` | `s_112`（`ConSensorHourlyAveValue`） | 結果を書き込む先のテーブル |
| `retroactiveTable` | `s_112`（出力先テーブルと同一） | 前の時間帯のデータがまだ不足しているグループを探すために使用 |
| `previousColum` | `targetDateTime`の直前の時間カラム | 遡及対象グループを絞り込む条件 |

出典：`CalcCommonAverageDataCommand.php:1235-1265`。

### 2.3 5つのグループ属性（`c111`~`c115`）の意味

`s_102`の各時間別レコードには、（記録時点の世帯プロファイル`t_101`から非正規化された）5つの属性があらかじめ付随しており、類似世帯グループへの集約に用いられる：住宅タイプ、暖房能力、床面積、世帯人数、コジェネレーションの種類（それぞれ`c111`~`c115`にマッピングされる）。平均を計算する際、これらの属性は`GROUP BY`の前に、より粗い**バケットへ丸め込まれる**（2.4節参照）。

### 2.4 ステップ1 ― 詳細グループの平均（`updateGroupAverage`）

```sql
-- サブクエリ：各グループ属性のバケット丸め・正規化
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
  FROM {sourceTable}   -- s_102
 WHERE c002 = :type
   AND {periodColumn} = :targetDateCondition
   AND c111 IN (1,2) AND c112 IN (1,2,3,4,9) AND c113 IN (1,2,3,4,5,6)
   AND c114 IN (1,2,3,4,5,6) AND c115 IN (1,2,9,10)
   AND {aggregateColumn} IS NOT NULL

-- 外側クエリ：バケット丸め後のグループごとにAVG + COUNT
SELECT c002, c003, {periodColumn}, c111, c112, c113, c114, c115,
       AVG({aggregateColumn}) AS {aggregateColumn},
       COUNT({aggregateColumn}) AS count
  FROM (<上記サブクエリ>) AS sensorInfo
 GROUP BY c002, c003, {periodColumn}, c111, c112, c113, c114, c115
```
出典：`CalcCommonAverageDataCommand.php:1156-1228`（`getGroupAverageCalculation`）。

**書き込み前のデータ充足チェック**（`checkGroupDataNum`、このステップにのみ適用）：
- 各グループについて、`s_113`テーブルから「グループの母数」（そのグループに属する世帯の総数。別バッチで事前に算出済み）を引く――条件は`device_type = 16`（「世帯数」を表す疑似コード）、5つのグループ属性が一致すること、該当する日付カラムであること。
- `count`（報告済み世帯数）／グループの母数 × 100 が `AVERAGE_CALCULATION_THRESHOLD`（**70**）未満の場合→ステップ1ではこのグループを**スキップし、書き込まない**。
- グループの母数が0の場合も同様にスキップする。

出典：`CalcCommonAverageDataCommand.php:1039-1149`；定数`AVERAGE_CALCULATION_THRESHOLD`は`config/const.php:599`。

しきい値を満たしたグループ→`s_112`へ1レコードを書き込み／更新する（キー：`device_type`, `room_id`, `date`、バケット丸め後の5つのグループ属性）。平均値は該当する時間カラム（`aggregateColumn`）にセットされる。

### 2.5 ステップ2 ― より広く集約したグループの平均（`updatePartGroupAverage`）

ステップ1の直後に続けて実行され、**より粗い**集約方法を用いる：`c111`はそのまま維持し、`c112`は`1/2/3`または`201`に丸める；**`c113`, `c114`, `c115`は固定で`999`**とする（無視して、同じ住宅タイプの全世帯を1つの広いグループとみなす）。このステップでは**70%のしきい値チェックは行わず**――常に広いグループへ上書きし、ステップ1の詳細グループでデータが不足している場合のフォールバック手段とする。

出典：`CalcCommonAverageDataCommand.php:868-943`（`updatePartGroupAverage`, `getPartGroupAverageCalculation`）。

### 2.6 ステップ3 ― 過去7日間の遡及（`retroactiveDaily`）

- `s_112`の中で、現在計算中の時間の**直前**の時間カラムがまだ`NULL`のままのグループ一覧を取得する（`getTargetGroup`、条件は`previousColum IS NULL`）。
- 各グループについて、1時間ずつ遡り（ループ上限192回。ただし実効上限は`retroactiveLimit`＝7日前の00:00で、実際は最大約168〜191時間）、データが不足している時間帯を探す。
- データが不足している時間帯については：該当する日付＋グループについて`s_102`から平均を再計算し（`getRetroactiveData`――ステップ1と同じグループ別AVGロジックだが、`s_112`にすでに保存されているグループ属性の条件を用い、バケットの丸め直しは行わない）、`s_112`へ上書きする（`updateRetroactiveData`）。
- あるグループについて、データが存在する時間（NULLでない）に到達した時点で、それ以上の遡りを停止する。

出典：`CalcCommonAverageDataCommand.php:112-132,317-407,591-815`。

### 2.7 トランザクションと業務上の定数

- 3つのステップ（2.4→2.6）はすべて、**実行1回につき1つのトランザクション**の中で行われる：いずれかのステップでエラーが返された場合→`rollback()`；3ステップすべてが成功して初めて`commit()`する。
- 本バッチは**自ら通知を送信することはない**；`s_112`のデータは、アプリ上で「類似世帯との比較」を表示するために他のAPI/バッチによって読み取られる（本コマンドの対象範囲外）。

| 定数 | 値 | 出典 |
|---|---|---|
| `GAS_CO_TYPE_CONSUMPTION` | 2 ― ガス総合消費量 | `const.php:176` |
| `GAS_WATER_HEAT_RATE` | 3 ― ガス給湯消費量 | `const.php:178` |
| `POWER_CONSUMPTION` | 5 ― 消費電力量 | `const.php:182` |
| `ROOM_TEMPERATURE` | 6 ― 室内温度 | `const.php:184` |
| `AVERAGE_CALCULATION_THRESHOLD` | 70（%）― 詳細グループを書き込むためのデータ充足しきい値 | `const.php:599` |
