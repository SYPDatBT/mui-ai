# CreateTablePartitionCommand（テーブルパーティション作成）

## 概要

`CreateTablePartitionCommand` は、`conciergesv` サーバー上で毎日（23:20）実行されるcronバッチである。システム
全体で共用される10個の大規模time-seriesテーブル（時間／日／月／年ごとのセンサー、日／月／年ごとの平均、週間
省エネレポート、ランキング、機器状態）について、PostgreSQLのdeclarative partitionの子パーティションを**事前
作成（pre-create）**する ―― 既定では今後14日分、またはパラメータで指定した特定の1日分を作成する。これは
PostgreSQL declarative partitioningにおける必須の回避策である：子パーティションがまだ存在しない日／月／年の
範囲にINSERTが入るとPostgreSQLは即座にエラーを返すため、これらのテーブルへ実際に書き込むCommand（参照して
いる他の28個のCommandの大半。grepによる実数）がinsertエラーにならないよう、本バッチを先に実行しておく必要が
ある。新リポジトリ `syp-eminelstandard-backend` では、**同等機能は不要であり、存在もしない** ―― 移植時の
漏れではなく、ストレージ基盤をDynamoDBへ全面的に変更したためである：最大規模のtime-seriesテーブル4つ
（`DeviceAccumulatedHistoryTable`, `DeviceDailyUsageHistoryTable`, `DeviceMonthlyUsageHistoryTable`,
`DeviceStatusHistoryTable`）はいずれも**単一のテーブルであり、恒久的に存在する**ことを確認済みである。
DynamoDBはハッシュキーに基づいて内部の物理パーティションへデータを自動的に振り分ける ―― アプリケーションから
は完全に透過的であり、PostgreSQLのdeclarative partitioningのように日付単位でパーティションを「事前作成」する
APIは存在しない。したがって、旧バッチが回避するために存在していた "no partition of relation found for row"
というエラーのリスクは存在しない。

---

# 第A部 ― 旧システム

## A.1 全体概要

| 項目 | 内容 |
|---|---|
| **バッチ名** | クラス：`CreateTablePartitionCommand`（`BaseCommand` を継承）・呼び出しコマンド名：`create_table_partition` *(CakePHP 4 の規約からの推定であり、ファイル内に明示的なoverrideはない)*・cronスクリプト：`13_CreateTablePartition.sh`・cron上の日本語名：「13.テーブルパーティション作成」。 |
| **役割** | DBインフラの保守 ― 実データの書き込みが必要になる前に、10個のPostgreSQL partitionedテーブルへ子パーティションを事前作成し、"no partition of relation found for row" というinsertエラーを回避する。 |
| **入力** | DBの読み取りなし、ファイルの読み込みなし。コマンドライン引数 `--date`（作成対象日の指定、任意）のみ。 |
| **出力** | 10個の異なる親テーブルに対して `CREATE TABLE IF NOT EXISTS ... PARTITION OF ... FOR VALUES FROM (...) TO (...)` を実行する ― データは書き込まず、テーブル構造（空の子パーティション）を作成するのみ。 |
| **処理概要** | 1. パーティションを作成すべき日付の一覧を決定する（A.2.1参照）。<br>2. 10個の親テーブルそれぞれについて、その日付一覧をループし、対応する子パーティション名＋rangeを算出して `CREATE TABLE IF NOT EXISTS ... PARTITION OF` を実行する。<br>3. パーティションの粒度が日より粗い（月／年）10個中6個のテーブルについては、1回の実行内で同じパーティションを重複して作成しないよう重複排除（dedup）のステップがある。<br>4. 1つのパーティション（特定のテーブル／日付）でエラーが発生しても `alert` ログを出力するのみで、バッチは停止しない ― 残りのパーティションの作成を継続する。 |

## A.2 詳細

### A.2.1 実行スケジュールとパーティション作成対象日一覧の決定

| 項目 | 内容 | 出典 |
|---|---|---|
| 実行スケジュール（cron） | `20 23 * * *` ― 毎日23:20、コメントは「13.テーブルパーティション作成」 | `docs/02_詳細設計/10_バッチ処理/mng-webap_cron設定_20241029.txt:45-46` |
| `--date` パラメータ | 未指定→**今後14日分**のパーティションを作成する（`翌日`..`翌日+13`、すなわち `本日+1`..`本日+14`）― 本日は含まない。指定した場合→正規表現 `yyyy-MM-dd` に一致する必要があり、フォーマットが不正であればバリデーションエラーとなる。指定したちょうどその1日分のみを作成する。 | `CreateTablePartitionCommand.php:463-481`；定数 `CREATE_PARTITION_RANGE_DAYS=14`（`const.php:720`） |

既定の実行スケジュール（毎日23:20、常に今後14日分）では、バッチは実データより常に少なくとも13日「先行」する ―
バッチが13日を超えて連続で停止しない限り、翌日分のパーティションが不足することは決してないだけの余裕がある。

### A.2.2 10個のパーティションの対応表 ― テーブル名、rangeの狭さ／広さ、その理由

10個の関数はすべて同じ型を共有する：子パーティション名を組み立てる → `FOR VALUES FROM...TO...` の範囲を
組み立てる → `CREATE TABLE IF NOT EXISTS ... PARTITION OF {親テーブル}` → try/catchでエラー時は `alert`
ログを出力する（バッチは停止しない）。異なるのは**親テーブル**、**ループの単位**（一覧内の各日ごとか、月／年で
重複排除するか）、および **rangeの幅**である。rangeの幅は、そのテーブルのpartition-keyカラムが常に1期あたり
1つの値に固定されているか（単位が月／年であってもrangeは1日ちょうどの狭さでよい）、それとも期の中で日ごとに
実際に変動するか（rangeは期全体をカバーする幅が必要）によって決まる ― 推測ではなく、対応するentityを読んで
確認した。

| 関数 | 親テーブル（Model/Table） | テーブルの意味 | パーティション単位 | 重複排除の基準 | Range | rangeが狭い／広い理由 |
|---|---|---|---|---|---|---|
| `diffSensorInfo` | `s_101`（`ConSensorMemoryValue`） | 差分センサ情報 ― センサーの差分値 | 日 | なし（1日につき1パーティション） | `[当日, 当日+1)` | 日付カラム（`c004`）は各レコードの実際の値であり、日ごとに変動する → ちょうど1日分のrangeが必要 |
| `dailySensorInfo` | `s_102`（`ConSensorHourlyValue`） | 日毎センサ情報 ― 時間別のセンサー値、1日1行（24個の時間カラム） | 日 | なし | `[当日, 当日+1)` | `c004` カラム（`FrozenDate`）は実際の日付ごとに変動する（`Entity/ConSensorHourlyValue.php:17`） |
| `monthlySensorInfo` | `s_103`（`ConSensorDailyValue`） | 月毎センサ情報 ― 日別のセンサー値、1か月1行（31個の日カラム） | 月 | あり（一覧内の直前の日と同じ月であればスキップ） | `[月初, 月初+1日)` ― **狭い**、01日ちょうどのみ | 行の日付カラムは常に月初の01日に固定される（`s_113` でも同じパターンを確認。`CreateGroupSummary.md` 参照）― 実際の値が01日以外になることは決してないため、狭いrangeでも過不足なく一致する |
| `yearlySensorInfo` | `s_104`（`ConSensorMonthlyValue`） | 年毎センサ情報 ― 月別のセンサー値、1年1行（12個の月カラム） | 年 | あり（同じ年であればスキップ） | `[当年, 当年+1)` | 年カラム（`c004`、`int` 型）は1年につき1つの値しか持たない（`Entity/ConSensorMonthlyValue.php:16`）→ ちょうど1年分のrangeで過不足ない |
| `dailyAverageSensorInfo` | `s_112`（`ConSensorHourlyAveValue`） | 日毎平均センサ情報 ― 時間別の平均、1日1行 | 日 | なし | `[当日, 当日+1)` | `s_102` の平均版であり、日付カラムが実際の日付ごとに変動する構造も同じ |
| `monthlyAverageSensorInfo` | `s_113`（`ConSensorDailyAveValue`） | 月毎平均センサ情報 ― 日別の平均、1か月1行（31個の日カラム） | 月 | あり | `[月初, 月初+1日)` ― **狭い** | `c003` カラムは常に月初の01日 ― `CreateGroupSummaryCommand` の調査で直接確認済み（日次分岐がpopulationを書き込む対象テーブル） |
| `yearlyAverageSensorInfo` | `s_114`（`ConSensorMonthlyAveValue`） | 年毎平均センサ情報 ― 月別の平均、1年1行（12個の月カラム） | 年 | あり | `[当年, 当年+1)` | `c003` カラムは `int` 型で、1年につき1つの値のみ ― `CreateGroupSummaryCommand` の調査で確認済み（月次分岐の対象テーブル） |
| `weeklyEnergySavingReport` | `s_105`（`ConWeeklyEcoReport`） | 週間省エネレポート情報 | 月 | あり | `[月初, 翌月初)` ― **広い、1か月分をすべてカバー** | 日付カラム（`c002`、`FrozenTime`）は月内の具体的なレポート日ごとに変動する（`Entity/ConWeeklyEcoReport.php:14`）― rangeが狭いと月内の他の日のデータが失われる |
| `rankingInfo` | `s_121`（`ConRanking`） | ランキング情報 | 年 | あり | `[当年, 当年+1)` | `c002` カラム（`C_YEAR`、`int` 型 ― `Entity/ConRanking.php:14,45`）は1年につき1つの値に固定される（`RankingCreationCommand.php:349`）― `s_104`／`s_114` と同じパターンであり、1年分のrangeがちょうど一致する |
| `deviceStatus` | `t_202`（`ConDeviceStatus`） | 機器状態情報 ― 機器の状態（`hemssv-develop` のAPI `InstructionController` 経由で書き込まれる ― GWのデータを受け付けるサーバーであり、バッチだけではない） | 日 | なし | `[当日, 当日+1)` | 状態データは機器から受信した実時刻に沿って継続的に書き込まれる |

出典：`CreateTablePartitionCommand.php:83-455`（10個の関数すべて）；PK／テーブル名の対照は
`sources/eminel_sv_lib-develop/src/Model/Table/{ConSensorMemoryValuesTable,ConSensorHourlyValuesTable,
ConSensorDailyValuesTable,ConSensorMonthlyValuesTable,ConSensorHourlyAveValuesTable,
ConSensorDailyAveValuesTable,ConSensorMonthlyAveValuesTable,ConWeeklyEcoReportsTable,ConRankingsTable,
ConDeviceStatusesTable}.php`。

**重複排除（dedup）のロジック**（10個中6個の関数で使用：`monthlySensorInfo`, `yearlyAverageSensorInfo`,
`weeklyEnergySavingReport`, `rankingInfo`, `yearlySensorInfo`, `monthlyAverageSensorInfo`）：現在の日付の
月／年の部分を、一覧内の直前の日（`$this->createdate[$index - 1]`）と比較し、一致すればスキップする ― 日付
一覧は常に連続して昇順に組み立てられる（今後14日分、または単一の1日）ため、同一の実行内で重複したパーティション
を作らないようにするには、直前の要素と比較するだけで十分である；月単位で重複排除する際に年を追加で比較しては
いないが、14日間のウィンドウで異なる2つの年の同じ月番号が繰り返されることは決してないため、無害である。
（`CreateTablePartitionCommand.php:178-182,215-219,252-256,289-293,326-330`）

### A.2.3 エラー処理 ― パーティションごとに独立、ロールバックなし

- `CREATE TABLE IF NOT EXISTS ...` の各実行は、それぞれ独立したtry/catchの中にある ― 1つのパーティション
  （特定の1テーブル、特定の1日／月／年）でエラーが発生しても、テーブル名＋エラーとなったrangeを添えて `alert`
  ログを出力するのみで、外部へthrowせず、残りのパーティション（同じテーブルの別の日、あるいは別のテーブルを
  含む）を停止させない。（`:124-135`、他の9個の関数も同様）
- トランザクションは使用しない ― `IF NOT EXISTS` により、再度の呼び出し（cronが過去13日間にすでに作成済みの
  日付に重ねて実行されることによる）は無害であり、エラーにならず、何も上書きしない（パーティションが既に存在
  する場合はスキップされる）。
- エラーとなったパーティションのための専用のリトライ機構はない ― ある実行で日付Nのパーティション作成が失敗した
  場合、翌日の実行（日付Nがまだ今後14日間のウィンドウ内にある場合）でのみ再作成される。あるいは `--date` を
  用いて手動で補う必要がある。

### A.2.4 特記事項／リスク

- **本バッチは非常に多くの他バッチの土台となるインフラバッチである** ― `conciergesv` の `src/Command/` に対して
  `EminelSvLib.ConSensor*`／`ConWeeklyEcoReports`／`ConRankings`／`ConDeviceStatuses` をgrepすると、この10個の
  テーブルのいずれかを参照する**他の28個のCommandファイル**が該当し、そのうち大半（`Calc*Command` 群、
  `RankingCreationCommand`、`CreateGroupSummaryCommand`、`DistributeMonthlyEcoPointsCommand` など）は実際に
  書き込みを行う ― パーティションが不足した際のinsertエラーのリスクを負うのは書き込み側のみである；特に `t_202`
  （機器状態）については、`hemssv-develop` の**API** `InstructionController` 経由でも書き込まれる（GWのデータを
  受け付けるサーバーであり、バッチではない）― つまり、機器データをリアルタイムに受信するAPIも、cronバッチだけ
  でなく、本バッチが当日分のパーティションを事前作成済みであることに依存している。
- **実運用上のリスク**：本バッチが13日を超えて連続して停止し（サーバーダウン、デプロイ不具合など）、誰も
  `--date` で手動の補完実行を行わなかった場合、上記のバッチ／APIは、パーティションが存在しない日付に到達した
  時点でinsertエラー（PostgreSQL の "no partition of relation found for row"）を起こし始める ― エラーは本
  バッチ自体ではなく、非常に多くの異なるバッチで同時に現れるため、この仕組みを知らない場合は根本原因の特定が
  困難になる。
- **アプリケーション層での多重起動防止機構**（本バッチ固有のものではない。`CreateGroupSummary.md` も参照）
  ― `BaseCommand` がPIDに基づく `.lock` ファイルを作成する。`conciergesv` 内の他の18個のCommandと共用されて
  いる（本バッチを含めると19個のCommand）。
  （`BaseCommand.php:21-38`）
- 月／年単位の10個中3個のテーブル（`s_103`, `s_113`, `s_114`）における狭いrange（1日ちょうどのみ）は**バグ
  ではない** ― これらのテーブルの日付／年カラムが常に1期あたり1つの値に固定されることを直接確認済みであり
  （A.2.2の表を参照）、狭いrangeでも実データの100%に一致する；ただし、対象テーブルの実際のカラム構造を確認せず
  に流し読みすると「データ欠落のバグ」と誤解されやすい、という点のみ注意が必要である。

---

# 第B部 ― EMINEL-smart（新システム）との対照

> 同等のLambda／仕組みは見つからなかった ― 未移植だからではなく、ストレージ基盤の変更によって元の課題そのもの
> が存在しなくなったためである。以下の表は、調査した領域と具体的な根拠である（B.1/B.2の代わり）。

## 確認済み

| 領域／候補 | 結果 |
|---|---|
| `template-dynamodb.yaml` 内の最大規模のtime-seriesテーブル4つのキー構造 | `DeviceAccumulatedHistoryTable`（1113-1143行）：PK=`receive_date`（HASH）、SK=`history_id`（RANGE）、GSI `gsi_tagtag_kaiin_bango`。`DeviceDailyUsageHistoryTable`（:1145-1175）、`DeviceMonthlyUsageHistoryTable`（:1177-1207）、`DeviceStatusHistoryTable`（:1209-1239）― キー構造は同一。4つともすべて `BillingMode: PAY_PER_REQUEST` であり、`TimeToLiveSpecification`（属性 `ttl`）を持つ。`receive_date` はパーティションキーの値（通常の文字列）にすぎず、事前にプロビジョニングが必要な「子テーブル」／パーティションオブジェクトではない。 |
| `src/functions/`、`src/statemachine/`、`src/` 全体に対する `partition`／`CreateTable`／`create-table`／`provision-table`／`provision.?capacity` のgrep | 関連する結果は0件（`write-multiple-transaction.ts:34` にthroughputに関するコメントが1行あるのみで、パーティションの作成／プロビジョニングとは無関係）。 |
| `template.yaml` 内の `ScheduleV2`／`cron(...)` すべて | システム全体でcronスケジュールは3つのみ（`BatchRunSequentiallyStateMachine`、`BatchMigrationIntegratedDataStateMachine`、`BatchGetErrorDeviceInfoOfRinnaiStateMachine`）― 3つともすべて業務データを処理するバッチ（import/export/migration）であり、「インフラ」的な性格を持つfunction（テーブル作成、capacity設定、パーティション作成）は存在しない。 |

---

## まとめ

**旧バッチが解決していた元の課題は、新アーキテクチャには存在しない。見落とされたわけではない：**

- 旧バッチが存在していたのは、PostgreSQLのdeclarative partitioningが、そのrangeに該当するレコードが発生する
  前に子パーティションを作成しておくことを要求するためである ― これはPostgreSQLのパーティション機構に固有の
  技術的制約であり、ストレージ基盤に依存しない業務要件ではない。
- DynamoDB（新システムのストレージ基盤）には「事前に作成しておく必要のある時間単位の子パーティション」という
  概念がない ― DynamoDBのパーティションはハッシュキーに基づく自動的な内部機構であり、アプリケーションからは
  完全に透過的である。直接確認した内容：最大規模のtime-seriesテーブル4つはいずれも単一のテーブルであり恒久的
  に存在し、`template.yaml`／`template-dynamodb.yaml` 全体を通じて、runtime時に動的に作成されるテーブル／
  リソースは一切ない。
- したがってこれは、通常の意味での「質的に異なる1つの仕組みが同じ役割を置き換えた」ケース（`SendAlertLogMail`
  のような）ではない ― その役割自体が**もはや不要になった**のであり、別のストレージ基盤を選択したことで、この
  役割を最初に生み出していた技術的制約が根本から取り除かれたためである。

**旧システムの「対」の仕組み（事前作成 ↔ 事後削除）と比較する際の留意点：**

- 旧システムでは、`CreateTablePartitionCommand`（パーティションの事前作成）は `DeleteDataCommand`
  （`DROP TABLE {partitionName}` ― `DeleteDataCommand.php:91,116,187` で直接確認）と対になっており、後者は
  逆の役割を担う：保持期限切れのデータを整理するために古いパーティションを削除する。2つのバッチはいずれも同一の
  PostgreSQL partitioningという1つの仕組みを軸としている ― 一方が作成し、もう一方が削除する。
- 新システムでは、この2つの役割（書き込みを可能にするための事前作成＋保持期限切れのための事後削除）はいずれも、
  **DynamoDBの単一の自動機構**に置き換えられている：`ttl` 属性（`TimeToLiveSpecification`）が期限切れレコードを
  自動的に削除するため、整理のために定期実行するバッチは不要であり、「即座に書き込める」ことについても事前の
  準備は一切必要ない。ここが総括すべき点である：機能が欠けたために1つのバッチが消えたのではなく、旧システムの
  2つのバッチ（作成＋削除）がまとめてスキーマ上の1つの静的な宣言属性に置き換えられたのであり ― 直接比較できる
  対応するLambda／cronはもはや存在しない。

---

## 出典

| 区分 | 内容 | 根拠 |
|---|---|---|
| 旧システム | メインロジック | `sources/conciergesv-develop/src/Command/CreateTablePartitionCommand.php` |
| 旧システム | 多重起動防止のロック機構（共用） | `sources/conciergesv-develop/src/Command/BaseCommand.php` |
| 旧システム | 事前作成する日数範囲の定数 | `sources/conciergesv-develop/config/const.php:720` |
| 旧システム | 10個のパーティションテーブルのPK構造／テーブル名 | `sources/eminel_sv_lib-develop/src/Model/Table/{ConSensorMemoryValuesTable,ConSensorHourlyValuesTable,ConSensorDailyValuesTable,ConSensorMonthlyValuesTable,ConSensorHourlyAveValuesTable,ConSensorDailyAveValuesTable,ConSensorMonthlyAveValuesTable,ConWeeklyEcoReportsTable,ConRankingsTable,ConDeviceStatusesTable}.php` |
| 旧システム | 各テーブルの日付カラムの意味（rangeが狭いか広いか） | `sources/eminel_sv_lib-develop/src/Model/Entity/{ConSensorHourlyValue,ConSensorDailyValue,ConSensorMonthlyValue,ConWeeklyEcoReport,ConRanking}.php` |
| 旧システム | これらのテーブルを参照する他の28個のCommand（横断的、実数） | `sources/conciergesv-develop/src/Command/` に対する `EminelSvLib.ConSensor*`／`ConWeeklyEcoReports`／`ConRankings`／`ConDeviceStatuses` のgrep |
| 旧システム | APIも `t_202` へ書き込む（バッチ以外） | `sources/hemssv-develop/src/Controller/InstructionController.php:635` |
| 旧システム | 実行スケジュール（cron） | `docs/02_詳細設計/10_バッチ処理/mng-webap_cron設定_20241029.txt:45-46` |
| 旧システム | バッチ一覧（日本語の説明、サーバー区分） | `docs/03_API仕様/04_バッチ一覧.md:75` |
| 新システム | 最大規模のtime-seriesテーブル4つのキー構造（事前パーティションが不要であることの確認） | `template-dynamodb.yaml:1113-1239`（`DeviceAccumulatedHistoryTable`, `DeviceDailyUsageHistoryTable`, `DeviceMonthlyUsageHistoryTable`, `DeviceStatusHistoryTable`） |
| 新システム | 期限切れ自動削除の仕組み（`DeleteDataCommand` のDROP partition側の代替） | `template-dynamodb.yaml` ― 上記4テーブルの `TimeToLiveSpecification`（属性 `ttl`） |
| 新システム | システム内のcronスケジュール全体（同様のインフラ的役割を担うcronが存在しないことの確認） | `template.yaml`（`BatchRunSequentiallyStateMachine:877-882`, `BatchMigrationIntegratedDataStateMachine:2228-2234`, `BatchGetErrorDeviceInfoOfRinnaiStateMachine:2974-2980`） |
| 旧システム | 古いパーティションの削除機構（作成／削除の対における「事後整理」側の対照） | `sources/conciergesv-develop/src/Command/DeleteDataCommand.php:91,116,187` |
