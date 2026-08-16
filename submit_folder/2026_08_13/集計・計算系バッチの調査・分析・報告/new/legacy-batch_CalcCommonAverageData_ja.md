# 旧バッチ ― CalcCommonAverageDataCommand（平均データ算出 ― Common、Daily/Monthly/Yearly共通）

## 概要

`CalcCommonAverageDataCommand` は独自の実行スケジュール（cron）を持つバッチではない ― このクラスの `execute()` メソッドは空であり、cron設定全体（`mng-webap_cron設定_20241029.txt`）の中にもこのバッチをCLI経由で呼び出す行は存在しない。これは**共通アルゴリズムを格納するクラス**であり、他の3つのバッチがインスタンス化し、`executeCommon($type, $dateTime, $aggregationUnit)` メソッド経由で呼び出す：`CalcDailyAverageDataCommand`（`aggregationUnit=1` を渡し、時間単位で計算 ― 個別の資料を参照）、`CalcMonthlyAverageDataCommand`（`aggregationUnit=2` を渡し、日単位で計算 ― 個別の資料を参照）、`CalcYearlyAverageDataCommand`（`aggregationUnit=3` を渡し、月単位で計算 ― 個別の資料を参照）。3つのバッチはいずれも、このクラス内にあるまったく同一の3ステップアルゴリズム（詳細グループ平均の算出 → より広いグループへの集約平均の算出 → データ欠損のある過去期間の遡及処理）を実行する。異なるのは `aggregationUnit` によって決まるソーステーブル／デスティネーションテーブル／カラム名のパラメータセットのみである。バッチはDBの読み書きのみを行う（メール送信・ファイル出力なし）。本資料はその共通アルゴリズムを詳細に記述する。cronスケジュール、コマンドライン引数、および各単位固有の消費指標種別の定数については、これを呼び出す3つのバッチの資料に記載する。

## 第1部 ― 総括

| 項目 | 内容 |
|---|---|
| **役割** | 共通アルゴリズム（3ステップ：詳細グループ平均 → 広域集約グループ平均 → 欠損している過去期間の遡及処理）を提供し、同じ住宅属性を持つ多数の世帯を1つのグループ平均値に集約する。時間／日／月の3単位すべてで共通利用される。 |
| **入力** | コマンドライン引数を自ら受け取ることはない ― 呼び出し元3バッチのいずれかから `executeCommon($type, $dateTime, $aggregationUnit)` 関数呼び出しを通じてのみ値を受け取る。DBの読み取りのみ：単位に対応する世帯別数値テーブル（`s_102`/`s_103`/`s_104`）＋グループ集計先テーブル（`s_112`/`s_113`/`s_114`。データ欠損期間の検索にも再利用する）＋グループ母数参照テーブル：unit=1・2は `s_113`、unit=3は `s_114`（unit=1のみ自身の格納先 `s_112` とは別テーブルを参照する — 2.4参照）。 |
| **出力** | `aggregationUnit` に応じて `s_112`/`s_113`/`s_114` のいずれか1つのグループ集計テーブルへ書き込む ― メール送信・CSV出力なし。 |
| **処理概要** | 1. 呼び出し元バッチから `type`＋`dateTime`＋`aggregationUnit` を受け取り、対応するソーステーブル／デスティネーションテーブル／カラムのパラメータセットを導出する。<br>2. 全体を1つのトランザクションで開始する。<br>3. 詳細グループ単位で平均を算出する（住宅属性5項目、グループ母数の70%以上を満たす場合のみ書き込む）。<br>4. 続けてより広い集約グループ単位で平均を算出する（5項目のうち3項目を除外、閾値チェックなし）。フォールバック案として使用する。<br>5. データが欠損している過去期間を遡及処理する（単位に応じて最大約7日／1か月／1年）。全ステップが成功した場合はcommit、そうでなければ全体をrollbackする。 |

## 第2部 ― 詳細

### 2.1 独自の実行スケジュールを持たない ― 他の3バッチからのみ呼び出される

| 呼び出し元バッチ | 渡される `aggregationUnit` | 平均計算の単位 | 詳細資料（cronスケジュール、CLI引数、指標種別の定数） |
|---|---|---|---|
| `CalcDailyAverageDataCommand` | `1` | 時間単位 | `docs/CalcDailyAverageDataCommand/legacy-batch_CalcDailyAverageData.md` |
| `CalcMonthlyAverageDataCommand` | `2` | 日単位 | `docs/CalcMonthlyAverageDataCommand/legacy-batch_CalcMonthlyAverageData.md` |
| `CalcYearlyAverageDataCommand` | `3` | 月単位 | `docs/CalcYearlyAverageDataCommand/legacy-batch_CalcYearlyAverageData.md` |

3つのバッチはいずれも `new CalcCommonAverageDataCommand()` をインスタンス化してから `executeCommon($type, $dateTime, $aggregationUnit)` を呼び出す ― このクラスに対するCLIルート（`cake.php CalcCommonAverageData ...`）は存在しない。このクラスの `buildOptionParser()`/`execute()` に宣言されている `type`/`datetime` 引数は実際には使用されない。

出典: `CalcCommonAverageDataCommand.php:62-105`; `CalcDailyAverageDataCommand.php:77-80`; `CalcMonthlyAverageDataCommand.php:74-77`; `CalcYearlyAverageDataCommand.php:74-77`。

### 2.2 `aggregationUnit` によるパラメータ化テーブル（`getAggregationUnitParameters`）

| パラメータ | `aggregationUnit=1`（時間） | `aggregationUnit=2`（日） | `aggregationUnit=3`（月） |
|---|---|---|---|
| `targetDateTime` のデフォルト値（`dateTime` 未指定時） | 現在時刻 − 1時間 | 現在時刻 − 1日 | 現在時刻 − 1か月 |
| `targetDateCondition` | `targetDateTime` の `yyyy/MM/dd` | `targetDateTime` の `yyyy/MM/01` | `targetDateTime` の `yyyy` |
| `aggregateColumn` | `c0{時+11}`（0時→`c011`、23時→`c034`） | `c0{日+10}`（1日→`c011`、31日→`c041`） | `c0{月+10}`（1月→`c011`、12月→`c022`） |
| `sourceTable` | `s_102`（`ConSensorHourlyValue`） | `s_103`（`ConSensorDailyValue`） | `s_104`（`ConSensorMonthlyValue`） |
| `destinationTable` | `s_112`（`ConSensorHourlyAveValue`） | `s_113`（`ConSensorDailyAveValue`） | `s_114`（`ConSensorMonthlyAveValue`） |
| `periodColumn` | `c004` | `c004` | `c004` |
| `retroactiveTable` | `s_112`（デスティネーションテーブル自身） | `s_113`（デスティネーションテーブル自身） | `s_114`（デスティネーションテーブル自身） |
| `previousColum` | 直前の時間のカラム | 直前の日のカラム | 直前の月のカラム |

出典: `CalcCommonAverageDataCommand.php:1235-1334`。

### 2.3 呼び出し元バッチごとの具体例

同一のアルゴリズムだが、実際に読み書きするカラムは `aggregationUnit` によって異なる。以下の3つの例はいずれも `type=5`（`POWER_CONSUMPTION` ― 消費電力量／電力消費）について計算するものとする：

**`CalcDailyAverageDataCommand` が `aggregationUnit=1` で呼び出す場合** ― 例：`--datetime=2024-06-15T08:00:00+09:00`：
- `targetDateTime` = `2024-06-15 08:00:00` → `targetDateCondition` = `2024/06/15`；計算対象の時刻 = **08時** → `aggregateColumn` = `c0(8+11)` = **`c019`**。
- ステップ1は `s_102`（別のバッチにより世帯ごとに事前計算済み）から読み取る：カラム `c002`（device_type=5）、`c003`（room_id）、`c004`（=`2024/06/15`）、`c111`～`c115`（住宅属性5項目）、および**`c019`**（各世帯の08時台の電力消費値） ― `c004 = '2024/06/15'` かつ `c019 IS NOT NULL` で絞り込む。
- `s_112` へ書き込む：グループごとに1行（キー `c001=5, c002=room_id, c003='2024/06/15', c111~c115`）、**`c019`**（08時のカラム）に平均値をセットする。
- ステップ3は `s_112` の直前の時刻のカラム（07時 → `c018`）がまだ `NULL` かどうかを確認し、`NULL` であれば最大192時間（約8日）遡ってbackfillする。

**`CalcMonthlyAverageDataCommand` が `aggregationUnit=2` で呼び出す場合** ― 例：`--datetime=2024-06-15`：
- `targetDateTime` = `2024-06-15 00:00:00` → `targetDateCondition` = `2024/06/01`（`s_103` は1か月につき1行を保存するため）；計算対象の日 = **15日** → `aggregateColumn` = `c0(15+10)` = **`c025`**。
- ステップ1は `s_103` から読み取る：カラム `c002`（device_type=5）、`c003`（room_id）、`c004`（=`2024/06/01`）、`c111`～`c115`、および**`c025`**（各世帯の15日の電力消費値） ― `c004 = '2024/06/01'` かつ `c025 IS NOT NULL` で絞り込む。
- `s_113` へ書き込む：グループごとに1か月1行（キー `c001=5, c002=room_id, c003='2024/06/01', c111~c115`）、**`c025`**（15日のカラム）に平均値をセットする。
- ステップ3は `s_113` の直前の日のカラム（14日 → `c024`）がまだ `NULL` かどうかを確認し、`NULL` であれば最大62日遡る。実際の下限は2024年5月1日（1か月前）となる。

**`CalcYearlyAverageDataCommand` が `aggregationUnit=3` で呼び出す場合** ― 例：`--datetime=2024-06`：
- `targetDateTime` = `2024-06-01 00:00:00` → `targetDateCondition` = `2024`（`s_104` は1年につき1行を保存するため）；計算対象の月 = **06月** → `aggregateColumn` = `c0(6+10)` = **`c016`**。
- ステップ1は `s_104` から読み取る：カラム `c002`（device_type=5）、`c003`（room_id）、`c004`（=`2024`）、`c111`～`c115`、および**`c016`**（各世帯の6月の電力消費値） ― `c004 = '2024'` かつ `c016 IS NOT NULL` で絞り込む。
- `s_114` へ書き込む：グループごとに1年1行（キー `c001=5, c002=room_id, c003=2024, c111~c115`）、**`c016`**（6月のカラム）に平均値をセットする。
- ステップ3は `s_114` の直前の月のカラム（05月 → `c015`）がまだ `NULL` かどうかを確認し、`NULL` であれば最大24か月遡る。実際の下限は2023年（1年前）となる。

共通点：読み書きするテーブルは異なるものの、**「時間単位の値」からカラム名への変換式は常に `c0{単位の値 + オフセット定数}` の形式であり、単位の最小値が常に `c011` カラムに対応するようになっている** ― 時間は0始まり（0～23）のためオフセットは`+11`（`0+11=11`）；日（1～31）と月（1～12）は1始まりのためオフセットは`+10`（`1+10=11`）。

### 2.4 ステップ1 ― 詳細グループ平均（`updateGroupAverage` → `getGroupAverageCalculation`）

3単位すべてで同一のSQLを共用し、2.2の表に従って `{sourceTable}`/`{periodColumn}`/`{aggregateColumn}` のみを置き換える：

```sql
-- Truy vấn con: chuẩn hoá/gộp bucket cho từng thuộc tính nhóm (c111~c115)
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
  FROM {sourceTable}
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
出典: `CalcCommonAverageDataCommand.php:1156-1228`。

グループ属性5項目 `c111`～`c115`（世帯プロフィール `t_101` からソーステーブルへあらかじめ非正規化されたもの）：住宅種別、暖房能力、床面積、世帯人数、コージェネレーション種別。

**書き込み前のデータ充足チェック**（`checkGroupDataNum`、このステップのみに適用）：

| | `aggregationUnit=1` | `aggregationUnit=2` | `aggregationUnit=3` |
|---|---|---|---|
| 「グループ母数」参照テーブル | `s_113` | `s_113` | `s_114` |
| `device_type` 条件 | `16`（「世帯数」を模した疑似コード。ハードコード ― 渡された `type` からは取得しない） | `16` | `16` |
| 照合カラム | `c0{dateTimeの日 + 10}` | `c0{dateTimeの日 + 10}` | `c0{dateTimeの月 + 10}` |

`count`（報告済み世帯数）／グループ母数 × 100 < `AVERAGE_CALCULATION_THRESHOLD`（**70**）、またはグループ母数 = 0 の場合 → スキップし、このステップではそのグループを書き込まない。

閾値を満たすグループ → `destinationTable` へ1レコードを書き込み／更新する（キー：`device_type`、`room_id`、期間（`c003`）、バケット化済みのグループ属性5項目）。該当する `aggregateColumn` に平均値をセットする。

出典: `CalcCommonAverageDataCommand.php:1039-1149`；定数 `AVERAGE_CALCULATION_THRESHOLD` は `config/const.php:599`。

### 2.5 ステップ2 ― より広い集約グループの平均（`updatePartGroupAverage` → `getPartGroupAverageCalculation`）

ステップ1の直後に実行され、ソース／デスティネーションテーブルは同じだが、バケット化は**より粗く**なる：`c111` はそのまま保持し、`c112` は `1/2/3` または `201` に集約する；**`c113`、`c114`、`c115` は固定で `999`**（同じ住宅種別の世帯はすべて1つの広域グループとみなし、暖房能力／床面積／世帯人数／コージェネレーションは無視する）。このステップは**`checkGroupDataNum` を呼び出さない** ― 常に上書きし、ステップ1の詳細グループが70%の閾値を満たさない場合のフォールバック案として機能する。

出典: `CalcCommonAverageDataCommand.php:868-943`。

### 2.6 ステップ3 ― データ欠損のある過去期間の遡及処理（`retroactiveAdjustment`）

現在期間についてステップ1～2が完了した後、`retroactiveAdjustment()` は `aggregationUnit` に応じて3つの関数のうち1つを選択する ― 処理フレームは共通で、時間を遡る単位のみが異なる：

| | `retroactiveDaily()` (unit=1) | `retroactiveMonthly()` (unit=2) | `retroactiveYearly()` (unit=3) |
|---|---|---|---|
| 1回あたりの遡及ステップ | 1時間（`subHours`） | 1日（`subDays`） | 1か月（`subMonths`） |
| 最大遡及回数（ループ上限） | 192 | 62 | 24 |
| 実際の下限（`retroactiveLimit`） | `targetDateTime − 7日` | [計算対象月 − 1か月]の01日 | [計算対象年 − 1]年 |
| 書き込み時のカラムオフセット（`columnAdjusted`） | `+11`（時） | `+10`（日） | `+10`（月） |
| 結果を書き込むEntity | `ConSensorHourlyAveValue` | `ConSensorDailyAveValue` | `ConSensorMonthlyAveValue` |

共通の仕組み（`getTargetGroup` → 順次遡及 → `getAggregationTarget` → `getRetroactiveData` → `updateRetroactiveData`）：
1. `getTargetGroup()`：`retroactiveTable` の中で、直前期間のカラム（`previousColum`）がまだ `NULL` であるグループの一覧を取得する ― 条件 `c111 IN (1,2)`、`c112 IN (1,2,3,201)`、`c113 IN (301,4,302,999)`、`c114 IN (401,402,403,999)`、`c115 IN (1,2,501,999)`（ステップ1の詳細グループとステップ2の広域グループの両方に一致する）。
2. 各グループについて、上表のステップ単位で順次遡り、`retroactiveLimit` を超えない。
3. 現在行とは異なる保存期間の行（別の日／月／年）に遡った場合、`getAggregationTarget()` を呼び出して `retroactiveTable` 内の該当期間の行を読み直し、どのカラムがまだ `NULL` かを把握する。
4. 欠損している区間について：`getRetroactiveData()` が該当グループに対して `sourceTable` から `AVG` を再計算する（`retroactiveTable` にすでに保存済みの属性5項目をそのまま利用し、バケットの再集約は行わない）。対象は欠損している時間枠。`updateRetroactiveData()` が結果を `retroactiveTable` へ上書きする ― 遡及対象の時間枠が隣接する2つの期間行にまたがる場合は、書き込むべきカラム範囲を自動的に再計算する（`getRetroactiveUpdatePeriod`）。
5. あるグループについて、すでにデータが存在する（`NULL` でない）期間に到達した時点で、それ以上の遡及を停止する。

出典: `CalcCommonAverageDataCommand.php:112-407`（`retroactiveDaily/Monthly/Yearly` の3関数）、`418-861`（`updateRetroactiveData`、`getRetroactiveUpdatePeriod`、`getRetroactiveData`、`getAggregationTarget`、`getTargetGroup`）。

### 2.7 トランザクションと業務定数

- ステップ1 → ステップ2 → ステップ3は、**`executeCommon` の呼び出し1回につき唯一のトランザクション**の中で実行される：いずれかのステップがエラーを返した場合 → 全体を `rollback()` する；3ステップすべてが成功した場合のみ `commit()` する。
- このクラスは**自ら通知を送信することも、表示用にデータを読み取ることもしない** ― 書き込まれたデータ（`s_112`/`s_113`/`s_114`）は、アプリ上で「類似世帯との比較」を表示するために別のAPI／バッチが読み取る（このコマンドの対象範囲外）。

| 定数 | 値 | 出典 |
|---|---|---|
| `AVERAGE_CALCULATION_THRESHOLD` | 70（%） ― ステップ1で詳細グループを書き込むためのデータ充足閾値 | `const.php:599` |

`type` 引数（消費指標の種別）の有効値一覧は、呼び出し元バッチごとに異なる（`GAS_CO_TYPE_CONSUMPTION`、`GAS_WATER_HEAT_RATE`、`POWER_CONSUMPTION`、`ROOM_TEMPERATURE`；`CalcYearlyAverageDataCommand` のみさらに `ENERGY_CONSUMPTION` も受け付ける） ― `checkValidate()` は呼び出し元の3コマンド側にあり、`CalcCommonAverageDataCommand` には含まれないため。詳細は2.1項に挙げた3つの資料を参照。
