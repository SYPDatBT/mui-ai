# CreateGroupSummaryCommand（グループサマリー作成）

## 概要

`CreateGroupSummaryCommand` は、`conciergesv` サーバー上で毎日（02:10）実行されるcronバッチである：全顧客を世帯属性5項目（住宅タイプ、暖房能力、床面積、世帯人数、ガスコージェネレーションの有無 ― 各属性は `CASE WHEN` によって値の少ないグループへ「バケット化」される）の組み合わせでセグメント分けし、各セグメントの**顧客数**（population）を算出したうえで、共通のsensor-valueテーブルへ `device_type=16`（「グループ母数」＝各グループのpopulation（顧客数）。正式な `device_type` の1つであり、ハックではない）というコードで保存し、あわせて**顧客ごとの月次セグメント履歴**も保存する。これは、アプリに表示される「類似顧客グループとの使用量比較」機能の基礎データである（`GetUsageController.php` で確認 ― グループ平均を算出するために、まさにこの2つのテーブルを読み直している）。新リポジトリ `syp-eminelstandard-backend` には、**同等の機能は見つからない**：グループ／特別な `device_type` の組み合わせで保存するDynamoDBテーブルは存在せず（`template-dynamodb.yaml` の53テーブルすべてを確認済み）、「グループ別のaverage」を算出するLambdaも存在せず（`src/` 全体に対する `average`/`Average` のgrepは0件）、現存する唯一の世帯属性の仕組み（`app_household_num`、`app_total_floor_area`、`IAttributeCondition`）は**プッシュ通知の送信対象を絞り込む**ため（targeting）だけに使われており、population/averageを算出してユーザーに比較を表示するためのものではない。「類似グループとの使用量比較」機能は、新システムへ移植されていないと思われる。

---

# 第A部 ― 旧システム

## A.1 総括

| 項目 | 内容 |
|---|---|
| **バッチ名** | クラス：`CreateGroupSummaryCommand`（`BaseCommand` を継承）・呼び出しコマンド名：`CreateGroupSummary` *(tgz内の実際のcronシェルスクリプトによる：`sudo -u apache php /var/www/vhost/conciergesv/bin/cake.php CreateGroupSummary` ― CakePHPはCamelCase形式とsnake_case形式のどちらも解決できる)* ・cronスクリプト：`14_CreateGroupSummary.sh` ・cron内の日本語名：「14.グループ集計情報登録機能」。 |
| **役割** | 世帯属性5項目により顧客をセグメント分けし、各セグメントのpopulationを算出するとともに、顧客ごとのセグメント履歴を保存する ― アプリの「類似グループとの比較」機能の基礎データである。 |
| **入力** | 顧客テーブル `t_101`（`ConCustomers`）を2本の別々のSQLで読み取る（絞り込み条件が異なる ― A.2.2参照）。コマンドライン引数：`--date`（算出日、デフォルトは当日）、`--aggregateFlag`（daily/monthly実行フラグ、デフォルトは両方）。 |
| **出力** | dailyフラグが有効な場合、`s_113`（`ConSensorDailyAveValues`、月内の日ごとのカラム）へ書き込む；monthlyフラグが有効な場合、`s_114`（`ConSensorMonthlyAveValues`、年内の月ごとのカラム）＋ `s_151`（`ConUserGroupHistories`、顧客1件・1か月につき1行）へ書き込む。すべて1つのトランザクション内で行う。 |
| **処理概要** | 1. 引数のパース＋バリデーション → 実際の算出日と、実行すべきdaily/monthlyフラグを決定する（分岐あり、決定木A.2.1参照）。<br>2. トランザクションを開始する。<br>3. 顧客セグメントごとのpopulationを算出する（population aggregation。有効レンジで絞り込んだ顧客集合を用いる）。<br>4. dailyフラグの場合：populationを `s_113` の日ごとのカラムへ書き込む。<br>5. monthlyフラグの場合：populationを `s_114` の月ごとのカラムへ書き込み、次に未削除の全顧客を取得し（属性のレンジでは絞り込まない）、顧客ごとのセグメント履歴を `s_151` へ書き込む。<br>6. 全ステップが正常であればcommit、いずれかのステップでエラーが発生した場合はrollbackする。 |

## A.2 詳細

**算出方法のマップ ― 4ステップ、population算出ステップを共用する2つの独立した書き込みフロー：**

```
[--date, --aggregateFlag]
        │
        ▼
  checkValidate() ── 決定木 (A.2.1) ── 出力: 実際の算出日 + フラグ [daily?, monthly?]
        │
        ▼
  populationAggregation() (A.2.2) ── t_101 に対する SQL COUNT+GROUP BY、有効レンジで絞り込み
        │  → 各行: (population, device_type=16, room_id=0, 日付, バケット化済みの5つの group-attr)
        │
        ├─ daily フラグの場合  ──▶ updateMonthlyAverage() (A.2.3) ──▶ s_113 の日カラムへ書き込み
        │
        └─ monthly フラグの場合 ─▶ updateYearlyAverage() (A.2.4) ──▶ s_114 の月カラムへ書き込み
                              │
                              ▼
                          getCustomers() ── 別の SQL、レンジで絞り込まない (未削除のみで絞り込み)
                              │
                              ▼
                          updateGroupHistory() (A.2.4) ──▶ s_151 へ顧客1件につき1行を書き込み
```

| ステップ | 詳細項目 |
|---|---|
| 引数のバリデーション＋日付／フラグの決定木 | §A.2.1 |
| セグメント別のpopulation算出 | §A.2.2 |
| 日単位のpopulation書き込み（daily分岐） | §A.2.3 |
| 月単位のpopulation書き込み＋顧客ごとの履歴（monthly分岐） | §A.2.4 |

### A.2.1 引数のバリデーションと、算出日＋実行フラグを決定する決定木

| 項目 | 内容 | 出典 |
|---|---|---|
| 実行スケジュール（cron） | `10 2 * * *` ― 毎日02:10、コメントは「14.グループ集計情報登録機能」 | `docs/02_詳細設計/10_バッチ処理/mng-webap_cron設定_20241029.txt:48-49` |
| `--aggregateFlag` パラメータ | 未指定 → デフォルト `[1,2]`（daily=`DAILY_AGGREGATION` と monthly=`MONTHLY_AGGREGATION` の両方）。指定あり → `,` 区切りの `int` 文字列としてパースする；各値は `1` または `2` でなければならず、不正な場合 → バリデーションエラー。 | `CreateGroupSummaryCommand.php:376-387`；定数は `const.php:609,611` |
| `--date` パラメータ | 未指定 → 当日（`FrozenDate::now()`）。指定あり → 正規表現 `^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])$`（`yyyy-MM-dd`）に一致する必要があり、フォーマットが不正な場合 → バリデーションエラー。 | `:389-402` |

有効な日付（`checkDateTime`）と有効なフラグが得られた後、コードは分岐して**バッチ全体で実際に使用する算出日**（`returnDateTime`）を決定する：

```
                    ┌─ monthly フラグが ACTIVE? ──── はい ──▶ returnDateTime = checkDateTime (そのまま)
                    │
有効な日付 ─────────┤
                    │                          はい ──▶ returnDateTime = checkDateTime を1か月前に戻す
                    └─ monthly フラグが OFF? ──── 日 = "01"? ──▶ monthly フラグをフラグ一覧に強制追加
                                             │
                                             いいえ (日 ≠ "01")
                                             ▼
                                       returnDateTime = '' (空 ― 下記 ⚠️ を参照)
```

| 分岐 | 条件 | 結果 | 意味 |
|---|---|---|---|
| 1 | monthlyフラグが一覧に含まれる（デフォルトのフラグ＝両方であるため、デフォルトでは常に該当する） | `returnDateTime` ＝ バリデーション済みの日付、そのまま | monthlyを実行する場合、指定された日付の月をそのまま算出対象の月とする |
| 2 | monthlyフラグが**含まれず**、バリデーション済みの日付が**01**日である | `returnDateTime` ＝ バリデーション済みの日付を**1か月前に戻した**もの。あわせて `MONTHLY_AGGREGATION` を自動的にフラグへ追加する | 月初1日にdaily-onlyを指定した場合 → システムは「ちょうど終わった月（前月）も集計する必要がある」と解釈し、monthlyも強制的に実行する |
| 3 | monthlyフラグが**含まれず**、バリデーション済みの日付が01日**以外**である | `returnDateTime` ＝ 空文字列 `''` | 下記の**⚠️ 異常点**を参照 |

出典：`CreateGroupSummaryCommand.php:405-418`。

**⚠️ 旧システムの異常点 ― 分岐3で `returnDateTime` が空のまま残る：**

- 再現条件：`--aggregateFlag=1`（dailyのみ、monthlyを無効化）を指定し、**月初1日以外**の任意の日にコマンドを実行する ― 例：`--aggregateFlag=1 --date=2026-08-15`。
- コードは3つの組み合わせのうち2つ（monthly有効；monthly無効＋日=01）しか明示的に処理していない ― 「monthly無効＋日≠01」に対する `else` 分岐が欠けているため、変数 `$returnDateTime` は初期値である空文字列のまま残り（`:405`）、それ以降の算出ステップ全体で `$this->dateTime = ''` が使われることになる（`populationAggregation()`、`updateMonthlyAverage()` はいずれも `FrozenDate::parse($this->dateTime)` を呼び出す）。
- 具体的な影響 *(CakePHP/Chronosの公開されている挙動に基づく推測 ― フレームワークが本リポジトリに含まれていないため、このリポジトリ内では検証できない)*：`FrozenDate::parse('')` は現在日時を返す可能性が高い（空文字列をパースした場合のPHP `DateTime`/Chronosのデフォルト挙動）― つまり、ユーザーが渡した `--date` 引数は**黙って無視され**、エラーを出すことも、バリデーション済みの値を正しく使うこともなく、`--date` を渡していないかのようにバッチが実行される。
- 実際のcronスケジュールには影響しない（cronは引数なし、またはデフォルトフラグのみで実行される → 常にmonthlyが有効 → 常に分岐1に該当する）― 1日以外の特定の日について `--aggregateFlag=1` で手動のデータ補填を実行する運用時にのみ生じるリスクである。

### A.2.2 顧客セグメント別のpopulation算出（population aggregation）

```sql
-- Sub-query: bucket hóa 4/5 thuộc tính, lọc khách hàng nằm trong "range hợp lệ"
SELECT
  customers.c001, customers.c012,
  CASE WHEN customers.c042 IN (1, 2, 3) THEN customers.c042 ELSE 201 END AS c042,
  CASE WHEN customers.c015 IN (1, 2, 3) THEN 301
       WHEN customers.c015 IN (5, 6) THEN 302
       ELSE customers.c015 END AS c015,
  CASE WHEN customers.c016 IN (1, 2) THEN 401
       WHEN customers.c016 IN (3, 4) THEN 402
       ELSE 403 END AS c016,
  CASE WHEN customers.c024 IN (1, 2) THEN customers.c024 ELSE 501 END AS c024
FROM t_101 AS customers
WHERE (
  c012 IN (1, 2) AND c042 IN (1, 2, 3, 4, 9) AND c015 IN (1, 2, 3, 4, 5, 6) AND
  c016 IN (1, 2, 3, 4, 5, 6) AND c024 IN (1, 2, 9, 10) AND c052 IS NULL)

-- Outer query: đếm population theo tổ hợp 5 thuộc tính đã bucket
SELECT COUNT(groupSub.c001) AS population,
  16 AS c001, 0 AS c002, '{ngày tính}' AS c003,
  groupSub.c012, groupSub.c042, groupSub.c015, groupSub.c016, groupSub.c024
FROM (...) AS groupSub
GROUP BY groupSub.c012, groupSub.c042, groupSub.c015, groupSub.c016, groupSub.c024
```
出典：`CreateGroupSummaryCommand.php:220-264`。

| `t_101` のカラム | 意味 | バケット化の方法（`group_attr#` として使用） |
|---|---|---|
| `c001`（`C_EMS_SP`） | 顧客コード | グループ化には使用せず、COUNTのみに使用する |
| `c012`（`C_BUILD_TYPE`） | 住宅タイプ | **バケット化しない** ― 元の値をそのまま保持 → `group_attr1`。WHEREで値1または2のみに限定される（それ以外の種別はpopulationから完全に除外される） |
| `c042`（`C_HEATER_POWER`） | 暖房能力 | `{1,2,3}` はそのまま維持、それ以外（有効レンジ `{1,2,3,4,9}` の中では `4` と `9` のみ）→ バケット `201` → `group_attr2` |
| `c015`（`C_GROSS_FLOOR_SPACE`） | 床面積 | `{1,2,3}`→`301`、`{5,6}`→`302`、それ以外（有効レンジ `{1..6}` により `4` のみ）→ `4` のまま維持 → `group_attr3` |
| `c016`（`C_FAMILY_SIZE`） | 世帯人数 | `{1,2}`→`401`、`{3,4}`→`402`、それ以外（有効レンジ `{1..6}` により `{5,6}`）→`403` → `group_attr4` |
| `c024`（`C_GAS_COGENERATION`） | ガスコージェネレーションの有無 | `{1,2}` はそのまま維持、それ以外（有効レンジ `{1,2,9,10}` により `9,10` のみ）→`501` → `group_attr5` |
| `c052`（`C_DELETED`） | 削除日時 | `IS NULL` で絞り込む ― 論理削除されていない顧客のみを算出対象とする |

**手計算の例** *(数値は説明用の仮定値であり、実データではない)* ― 顧客4件：

| 顧客 | c012 | c042 | c015 | c016 | c024 | c052 |
|---|---|---|---|---|---|---|
| 顧客1 | 1 | 2 | 2 | 1 | 1 | NULL |
| 顧客2 | 1 | 9 | 5 | 3 | 9 | NULL |
| 顧客3 | 2 | 1 | 4 | 2 | 2 | NULL |
| 顧客4 | **3** | 1 | 1 | 1 | 1 | NULL |

- 顧客1 → バケット `(1, 2, 301, 401, 1)`、population = 1。
- 顧客2 → バケット `(1, 201, 302, 402, 501)`、population = 1。
- 顧客3 → バケット `(2, 1, 4, 401, 2)`、population = 1。
- **顧客4はこのSQLから完全に除外される** ― `c012=3` が `WHERE c012 IN (1,2)` に含まれないため、（削除されていない有効な顧客であるにもかかわらず）どのバケットのpopulationにも寄与しない。影響は §A.2.5 を参照。

### A.2.3 日単位のpopulation書き込み（daily分岐）― `s_113` テーブル

- `DAILY_AGGREGATION` フラグが有効な場合にのみ実行される。A.2.2で算出した各population行について：`targetDate` ＝ 算出対象月の01日（`yyyy/MM/01`）；`dayColumnName` ＝ `c` ＋ `(月内の日 + 10)` を3桁ゼロ埋めしたもの ― 例えば12日→`c022`、1日→`c011`、31日→`c041`（エンティティ `ConSensorDailyAveValue` のカラム定数 `C_VALUE_1..C_VALUE_31` と一致する）。
- `new ConSensorDailyAveValue()` を生成する：`device_type=16`（固定値 ― `docs/02_詳細設計/02_データ生成・アプリ通信(旧コンシェルジュ踏襲)/補足資料/機器種別一覧.txt` によれば、コード16 ＝ **「グループ母数」** ＝「グループのpopulation」― これは**正式な** `device_type` コードであり、独自に作られたマジックナンバーではない）、`room_id=0`（定数 `DETECT_LIVING=0`（`const.php:228`）を再利用したもの ― 本来はリビングの人感センサー用の部屋コードだが、ここでは「特定の部屋に紐づかない」ことを示すプレースホルダーとしてのみ使用される）、`datetime=targetDate`、`group_attr1..5` ＝ バケット化済みの5つの値、`{dayColumnName}` ＝ populationのcount。
- `s_113` テーブルに対して `->save()` する ― テーブルのPKは `(c001,c002,c003,c111,c112,c113,c114,c115)` ＝ `(device_type, room_id, 月, group_attr 5項目)` であり、**PKに日カラムは含まれない** ― つまり同じ月の各日はいずれも**同一の1行**へ書き込まれ（セットされる `{dayColumnName}` カラムだけが異なる）、1行（1か月×1セグメント）の中に31個の日カラムが順次蓄積されていく。*(insertとupdateの挙動は、CakePHP ORMのデフォルトである「save前にPKで存在チェックを行う」仕組みに依存する ― リポジトリ内に明示的な `beforeSave`/upsertは存在せず、これはフレームワークの知識に基づく推測であり、フレームワークのコードがリポジトリに含まれていないため直接検証はできない。)*
- ループ内のいずれかの行でエラーが発生した場合（try/catchで捕捉し、`alert` でログ出力）→ daily分岐全体を失敗とみなし、rollbackして直ちにバッチを終了する（monthly分岐は実行しない）。（`:99-119,321-362`）

### A.2.4 月単位のpopulation書き込み＋顧客ごとの履歴（monthly分岐）― `s_114` ＋ `s_151` テーブル

- `MONTHLY_AGGREGATION` フラグが有効な場合にのみ実行される。
- **`s_114` への書き込み**（`updateYearlyAverage`。関数名には「Yearly」が使われているが、書き込み先テーブルのクラス名には「Monthly」が含まれる ― 命名規則の説明は本項末尾を参照）：`targetYear` ＝ 算出日の年（`int` 型であり、`FrozenDate` を用いる `s_113` とは異なる）；`monthColumnName` ＝ `c` ＋ `(月 + 10)` を3桁ゼロ埋めしたもの ― 1月→`c011`（＝1月）、8月→`c018`（＝8月）で、エンティティ `ConSensorMonthlyAveValue` の定数 `C_VALUE_JANUARY..C_VALUE_DECEMBER` と一致する。`s_114` テーブルのPKは `(device_type, room_id, 年, group_attr 5項目)` ― `s_113` と同じくカラム単位で蓄積する仕組みだが、蓄積の単位は1年内の月である（1か月内の日ではない）。（`CreateGroupSummaryCommand.php:272-313`）
- **紛らわしい命名規則** *(バグではなく、2つの層の間で命名がずれているだけである)*：`ConSensorDailyAveValue`（daily分岐の書き込み先、`s_113` テーブル）には日本語のdocコメント「月毎平均センサ情報」が付いており、`ConSensorMonthlyAveValue`（monthly分岐の書き込み先、`s_114` テーブル）には「年毎平均センサ情報」というdocコメントが付いている。英語のクラス名はカラムの単位（daily＝日ごとのカラム、monthly＝月ごとのカラム）に従って付けられ、日本語のdocコメントは1行の単位（1行＝1か月、または1行＝1年）で記述されている ― 2つの呼び方が1段階ずれており、流し読みすると誤解しやすい。
- **`s_151` への書き込み**（`updateGroupHistory`）：`s_114` への書き込みが成功した後、`getCustomers()` を呼び出す ― これはA.2.2のSQLとは**異なる**SQLであり、`WHERE c052 IS NULL`（未削除）のみで絞り込み、5属性の有効レンジでは**絞り込まない**（`CreateGroupSummaryCommand.php:192-200`）。返却された顧客1件ごとに `ConUserGroupHistory` の行を1件生成する：`ems_sp`＝顧客コード、`month`＝算出対象月の01日、`group_attr1..5` ＝ 顧客の**バケット化前の元の値**（`c012,c042,c015,c016,c024` をそのまま使用し、`CASE WHEN` は一切通さない ― 5属性のうち4つのみをバケット化するA.2.2とは異なる）。`s_151` テーブルのPKは `(ems_sp, month)` → 顧客1件につき1か月あたり履歴は1行のみであり、同じ月で再実行した場合は上書きされる *(upsertの仕組みについては上記と同じ推測)*。（`:151-181,188-213`）
- `s_151` テーブルの最終的な目的は、エンティティのdocコメントで確認できる：「アプリのグループ平均表示のための情報。該当ユーザの過去月に所属したグループを保持する。」― さらに、`s_113`/`s_114` の2つのテーブルを読み取っている箇所を探すことでも確認した：`GetUsageController.php`（アプリ向けにusageを取得するAPI）には2つの独立したJOIN分岐がある ― 年単位の比較を行う分岐は `ConUserGroupHistories`（`s_151`）と `ConSensorMonthlyAveValues`（`s_114`）をjoinする；日／月単位の比較を行う分岐は **`s_151` を使わず**、`ConSensorDailyValues`（`s_103` ― ユーザー単位の月次センサーテーブルであり、別のバッチが各行に `group_attr1..5` をあらかじめ書き込み済み；`ConSensorDailyValuesTable.php:41`）と `ConSensorDailyAveValues`（`s_113`）をjoinする。2つの分岐はいずれも `device_type=16` ＋ 同じ `group_attr` の組み合わせで絞り込み（JOIN句の中で再度バケット化しており、A.2.2のロジックとまったく同じである）、顧客に表示するグループ平均値を取得する。移植設計上の注意点（`s_113` の世帯間平均に関するQ-G6-1）：dailyのフローは `s_151` だけに依存するのではなく、`s_103` の各行に `group_attr` が書き込まれることにも依存する。（`GetUsageController.php:356-442,745-826`）

### A.2.5 特記事項／リスク

- **2つのSQLの間での顧客フィルタの非対称性** ― `populationAggregation()`（A.2.2）は、5つの属性がすべて「有効レンジ」に収まっている顧客からのみpopulationを算出する（`c012 IN(1,2)` が最も厳しい）；`getCustomers()`（A.2.4の `s_151` の部分）は未削除の顧客をすべて取得し、そのレンジでは絞り込まない。その結果：属性が「外れている」顧客（例えば `c012=3` で1/2ではないもの ― A.2.2の顧客4の例を参照）も `s_151` に `group_attr1=3` でグループ履歴の行が1件書き込まれるが、`s_113`/`s_114` には **`group_attr1=3` に一致するpopulationのバケットが存在しない**（最初からpopulationから除外されているため）→ アプリがこの顧客のグループ平均を取得しようとjoinしても、結果は空／NULLになる（LEFT JOINが一致しない）― グループ履歴は存在するのに、対応するグループ平均の数値を見ることは決してできない顧客が生じる。
- **アプリケーション層での多重起動防止の仕組み**（本バッチに限らない）― `BaseCommand`（親クラス）が `TMP` 配下にクラス名に基づく `.lock` ファイルを作成し、実行前にPIDが生存しているかを確認する；前のインスタンスがまだ生存している場合、新しいインスタンスは**直ちにexitし、明確なエラーログは出力されない**（本バッチについては、cronシェルスクリプト `14_CreateGroupSummary.sh` にshell層の `flock` もあるため → shell層とアプリケーション層の二重の多重起動防止となる）。このlockの仕組みは `conciergesv` 内の他の18個のCommandと共用されており（本バッチを含めて合計19個。grep `extends BaseCommand` で実際に数えた）、本バッチ専用のものではない ― `Calc*Command` 群（10分／日／月／年）、`RankingCreationCommand`、`WatchNotificationCommand`、`ControlDrOperationCommand` などを含む。（`BaseCommand.php:21-38`）
- daily・monthlyの2つの分岐全体が**単一のPostgreSQLトランザクション**の中で実行される ― どこかでエラーが発生した場合（`s_151` への書き込みで顧客1件がエラーになった場合も含む）**全体**がrollbackされ、同じ実行回で `s_113`/`s_114` に書き込みが成功していたpopulationも巻き戻される。（`:101-143`）

---

# 第B部 ― EMINEL-smart（新システム）との対照

> 本質的に同等のLambda／仕組みは見つからなかった。以下の表は、`src/functions/`、`src/layers/`、`template.yaml`、`template-dynamodb.yaml` の中で調査した領域／candidateと、一致しない理由である（B.1/B.2の代わり）。

## 確認済み

| 領域／candidate | 一致しない理由 |
|---|---|
| `src/layers/common/nodejs/interfaces/IAttributeCondition.ts`、`business-logic/check-user-matches-condition-attribute.ts`、`Kaiin.ts`/`IF2024CustomerInfo.ts` 内の `household_num`/`building_type`/`app_household_num`/`app_total_floor_area` フィールド | 類似の世帯属性（住宅タイプ、面積、人数…）は確かに存在するが、**プッシュ通知を受け取る顧客を絞り込む／targetingする**ために使われている（`batch-send-news`、`batch-send-tip`、`batch-send-survey`、`batch-send-dr`、`batch-send-contents-to-updated-user`）― グループ別のpopulation/averageを算出せず、グループ履歴も保存せず、ユーザーに表示する比較機能も存在しない。本質が異なる：コンテンツのtargeting ≠ benchmarking／比較。 |
| `create-data-segment-for-push-notice.ts`、`split-data-to-segments.ts`、`create-data-segment.ts` | ここでの「segment」という語は、S3/SQS経由で処理するためにファイル／ユーザー一覧をロット（chunk）へ分割することを意味する ― 純粋に一括処理上の技術的なものであり、属性による顧客のセグメント分けとは関係がない。 |
| `get-ranking-by-total-badge.ts`、`api-user/get-ranking-of-user.ts`、`api-point/get-point-badge-stats.ts`、`PointBadgeStatsTable`/`UserBadgeSummaryTable` | 合計ポイント／バッジによる個人ランキング（gamification）― 世帯属性によるグループ分けとは関係がなく、グループ別の平均も算出しない。 |
| `get-monthly-report-of-user.ts`（`api-dashboard`） | TagTag APIから取得するガス／電気の請求金額レポート（bill_amount, latest_payment_month）― グループとの使用量比較ではない。 |
| `template-dynamodb.yaml` 全体（53テーブル） | 名前に "Group"/"Segment"/"Population" を含むテーブルは存在しない；usage系テーブル（`DeviceDailyUsageHistoryTable`、`DeviceMonthlyUsageHistoryTable`）のPKは `receive_date`＋`history_id` であり、ユーザー単位の問い合わせはGSI `gsi_tagtag_kaiin_bango` 経由で行う ― `s_113`/`s_114` のように5属性の組み合わせや特別な `device_type` に基づくキー／カラムは存在しない。 |
| `src/` 全体に対する `average`/`Average`/`compare`/`comparison`/`population`/`GroupSummary`/`GroupAve`/`UserGroupHistory`/`SensorDailyAveValue`/`SensorMonthlyAveValue`/`device_type.*16` のgrep | 業務に関連する結果は0件（`localeCompare` のみ ― 技術的なものであり、業務上のものではない）。 |
| `template.yaml` ― `ScheduleExpression`（cron）全体 | 新システム全体でcronスケジュールは3件のみ（`cron(5 0-7 * * ? *)`、`cron(0 8 * * ?)` ×2）― 旧バッチの実行時刻02:10に対応するスケジュールは存在しない。 |

「世帯属性による顧客のセグメント分け → グループ別のpopulation/average算出 → ユーザー向けの比較」という機能が `syp-eminelstandard-backend` へ移植されたことを示す痕跡（DBテーブル、Lambda、`template.yaml` 内のリソース名）は一切見つからない。

---

## まとめ

該当なし ― 旧版はパイプラインが1つのみであり（本質的に異なる2つの並列アルゴリズムではない；daily/monthlyの分岐は、同一のpopulation算出フローにおける2つの異なる書き込みステップであり、同じ処理に対する2通りの算出方法ではない）、新システムには対照すべきものが**何も見つからない**（「別の仕組みに置き換えられた」というケースではない）― 第B部の「調査済み」の表に、各candidateが一致しない理由を十分に示した。

---

## 出典

| 区分 | 内容 | 根拠 |
|---|---|---|
| 旧システム | メインロジック | `sources/conciergesv-develop/src/Command/CreateGroupSummaryCommand.php` |
| 旧システム | 多重起動防止のlockの仕組み（共用） | `sources/conciergesv-develop/src/Command/BaseCommand.php` |
| 旧システム | `t_101`（顧客）のカラムの意味 | `sources/eminel_sv_lib-develop/src/Model/Entity/ConCustomer.php:49-79` |
| 旧システム | `s_113` テーブル ― PK、テーブル名 | `sources/eminel_sv_lib-develop/src/Model/Table/ConSensorDailyAveValuesTable.php:37-44`、`Entity/ConSensorDailyAveValue.php` |
| 旧システム | `s_114` テーブル ― PK、テーブル名 | `sources/eminel_sv_lib-develop/src/Model/Table/ConSensorMonthlyAveValuesTable.php:41-43`、`Entity/ConSensorMonthlyAveValue.php` |
| 旧システム | `s_151` テーブル ― PK、テーブル名、目的 | `sources/eminel_sv_lib-develop/src/Model/Table/ConUserGroupHistoriesTable.php:12-46`、`Entity/ConUserGroupHistory.php` |
| 旧システム | 集計フラグの定数 | `sources/conciergesv-develop/config/const.php:607-611` |
| 旧システム | `device_type=16` ＝「グループ母数」 | `docs/02_詳細設計/02_データ生成・アプリ通信(旧コンシェルジュ踏襲)/補足資料/機器種別一覧.txt`（Shift-JISをデコード） |
| 旧システム | 定数 `DETECT_LIVING=0` | `sources/conciergesv-develop/config/const.php:228` |
| 旧システム | `s_113`/`s_114`/`s_151` を読み取っている箇所（＋`s_103`、consumer、目的の確認） | `sources/conciergesv-develop/src/Controller/GetUsageController.php:356-442,745-826` |
| 旧システム | 実行スケジュール（cron） | `docs/02_詳細設計/10_バッチ処理/mng-webap_cron設定_20241029.txt:48-49` |
| 旧システム | バッチ一覧（日本語の説明、サーバーのグループ） | `docs/03_API仕様/04_バッチ一覧.md:74` |
| 旧システム | 関連資料。内容は未読（バイナリ） | `docs/02_詳細設計/00_データベース設計/コンシェルジュ_バッチ機能CRUD図.xlsx`、`docs/02_詳細設計/02_データ生成・アプリ通信(旧コンシェルジュ踏襲)/16_コンシェルジェSV_詳細設計書別紙_グルーピング.docx` |
| 新システム | 世帯属性の仕組み（本質が異なる ― プッシュのtargeting用であり、benchmarkingではない） | `src/layers/common/nodejs/interfaces/IAttributeCondition.ts`、`business-logic/check-user-matches-condition-attribute.ts`、`models/Kaiin.ts`、`models/IF2024CustomerInfo.ts` |
| 新システム | バッジによる個人ランキング（本質が異なる） | `src/layers/common/nodejs/business-logic/get-ranking-by-total-badge.ts`、`src/functions/api-user/get-ranking-of-user.ts`、`src/functions/api-point/get-point-badge-stats.ts` |
| 新システム | DynamoDBテーブルの全一覧（同等のテーブルは存在しない） | `template-dynamodb.yaml` |
| 新システム | cronスケジュール（02:10に対応するスケジュールは存在しない） | `template.yaml`（`ScheduleExpression` 全体） |
