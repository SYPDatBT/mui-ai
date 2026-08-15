# 旧バッチ調査 — CreateCsvAndZipConSensorDailyAveValuesCommand（センサー日別平均値 CSV/ZIP 生成）

## 概要

`CreateCsvAndZipConSensorDailyAveValuesCommand` は旧システム（EMINEL コンシェルジュサーバー）で **毎月1日 05:15 のみ**実行されるバッチである。月毎平均センサ情報テーブル `s_113` の **前々月**の月別パーティションを読み出し、**CSV を1本だけ**書き出したうえで、**実行のたびに必ず ZIP 圧縮**してフォルダごと削除する。

他の3バッチと決定的に違うのは、**契約者（EMS-SP）ごとにファイルを分けない**点である。`s_113` は個々の世帯の値ではなく「機器種別 × 設置場所 × グループ属性」で束ねた**平均値**を持つテーブルであり、そもそも EMS-SP 列を持たないためである。

**4バッチの位置づけ**（名称が紛らわしいため先に整理する）：

| バッチ | テーブル | モデル名 | 1レコード＝ | 1マスの値＝ | 実行周期 |
|---|---|---|---|---|---|
| DeviceStatuses | `t_202` | 機器状態情報 | 1回の収集 | — | 毎日 05:15 |
| HourlyValues | `s_102` | 日毎センサ情報 | 1日 | 1時間（24列） | 毎日 05:15 |
| DailyValues | `s_103` | 月毎センサ情報 | 1か月 | 1日（31列） | 毎月1日 05:15 |
| **DailyAveValues（本書）** | `s_113` | 月毎平均センサ情報 | **1か月** | **1日・平均（31列）** | 毎月1日 05:15 |

⚠️ 名称の注意（2点）：① 「平均値」とあるが**本バッチは平均を計算しない**（別の集計系バッチが `s_113` に書き済み）。② 「1日平均値」は**値の粒度**（1マス＝1日）であり**実行頻度ではない** — 本バッチは月1回のみ実行される。

> **本書の範囲**：旧システムの挙動調査のみ。本書には「E-GW での代替設計・移行手順・新旧対応表」は含まない。
> **参考までに総括表での判定**：結論＝**「バッチとしては不要」**、新システム側の対応機能＝**F-AD-09（データダウンロード：管理者が期間を指定した時点で生成する方式）**。根拠と全47バッチの一覧は別紙の移行調査総括表を参照。

## Part 1 — 概要

| 項目 | 内容 |
|---|---|
| **役割** | DB の保持期間（**2か月**）を過ぎると消える月別の平均センサーデータを、消える直前に **CSV → ZIP でファイル化**して残す。**値の計算・集計は一切行わない**（詳細 2.5）。 |
| **Input** | DB テーブル `s_113` の月別パーティション `s_113_YYYYMM`（対象月 = 実行日 − 32日 が属する月 = **前々月**）。⚠️ コードは `TableRegistry::getTableLocator()->get('EminelSvLib.' . $partitionTableName)` でパーティション名を直接エイリアスに渡しており（`…Command.php:39, 41`）、共通ライブラリの `ConSensorDailyAveValuesTable` / エンティティ `ConSensorDailyAveValue`（物理テーブル `s_113`、モデル説明「月毎平均センサ情報」。`legacy_eminel_docs/sources/eminel_sv_lib-develop/src/Model/Table/ConSensorDailyAveValuesTable.php:41`）**そのものは経由しない**。列名は Command 内にハードコードされている（同 `:102-107`）。 |
| **Output** | ローカルファイルシステム上の CSV／ZIP。<br>・CSV：`{CON_SENSOR_DAILY_AVE_VALUES_CSV_FILES_PATH}/{月初}_{月末}/{月初}_{月末}_1日平均値.csv` — **1ファイルのみ**<br>・ZIP：**毎回**、上記フォルダを圧縮した `{月初}_{月末}.zip` |
| **処理概要** | 1. 対象月 M = （実行日 − 32日）が属する月 を決め、パーティション `s_113_{M:Ym}` の存在を確認する（無ければ alert ログを出して終了）。<br>2. **契約者ループを行わず**、CSV を1本だけ開き、初回のみ UTF-8 BOM と 40 列のヘッダー行を書く。<br>3. 対象月の月初日と一致するレコードのみを 4,000件ずつページングして読み、日時列だけ書式変換して書き出す。<br>4. **曜日判定なしで必ず** ZIP 化し、フォルダごと削除する。 |

## Part 2 — 詳細

### 2.1 実行スケジュールと対象月

| 項目 | 内容 | 出典 |
|---|---|---|
| 実行スケジュール（cron） | `15 5 1 * *` — **毎月1日 05:15 のみ**。月初シェル `12_CreateCsvAndDeleteData_day1.sh` にのみ含まれ、日次シェル `_day2to31.sh` には**含まれない** | `legacy_eminel_docs/docs/02_詳細設計/10_バッチ処理/mng-webap_cron設定_20241029.txt:41`（節見出し `#12.DBデータ削除` は `:39`） |
| 実行コマンド | `sudo -u apache php /var/www/vhost/conciergesv/bin/cake.php CreateCsvAndZipConSensorDailyAveValues`（apache ユーザーで実行） | `legacy_eminel_docs/docs/02_詳細設計/10_バッチ処理/cron実行用シェルスクリプト/eminel-mng-webap.20240909.tgz` 内 `12_CreateCsvAndDeleteData_day1.sh`（4本の CSV バッチのうち最後に実行される） |
| 引数 | `--datetime`（既定値 `'now'`） | `legacy_eminel_docs/sources/conciergesv-develop/src/Command/CreateCsvAndZipConSensorDailyAveValuesCommand.php:28, 36` |
| **対象月 M** | `（実行日時 − 32日）が属する月` → パーティション名 `s_113_{M:Ym}` | 同 `:39` |
| 出力先フォルダの期間 | M の **月初〜月末**（`startOfMonth()` / `endOfMonth()`） | 同 `:50-52` |
| ZIP 化のタイミング | **毎回**（曜日判定なし） | 同 `:129-135` |

**cron の読み方**：5つの欄は `分 時 日 月 曜日`。`15 5 1 * *` = 05:15 に**1日だけ**。

**「32日前」が必ず前々月になる理由**：本バッチは毎月**1日**にしか動かない。1日から32日さかのぼると、前月をまるごと飛び越して**必ず前々月に着地する**。

```
実行日 2026-03-01 − 32日 → 2026-01-28  → 対象月 = 2026年1月（＝前々月）
実行日 2026-05-01 − 32日 → 2026-03-30  → 対象月 = 2026年3月（＝前々月）
実行日 2026-01-01 − 32日 → 2025-11-30  → 対象月 = 2025年11月（＝前々月）
※ 直前の月が28日/29日/30日/31日のいずれであっても、1日から32日引けば前月を必ず通り越す
```

**ファイル化から削除までの猶予**：

| バッチ | ファイル化 | DB の DROP | 猶予 |
|---|---|---|---|
| DeviceStatuses（`t_202`、保持8日） | ある日 D の D+8日 | D+9日 | 1日 |
| HourlyValues（`s_102`、保持14日） | D+8日 | D+15日 | 7日 |
| **DailyAveValues（`s_113`、保持2か月、本書）** | **前々月** | **同じ前々月・同一実行内** | **0** |

**同一実行内で「前々月を CSV/ZIP 化 → その前々月を DROP」** が連続する点は `CreateCsvAndZipConSensorDailyValues`（`s_103`）とまったく同じである：同じく前々月を対象とし、毎回 ZIP 化し、その実行内で DROP される。

> 出典：`legacy_eminel_docs/sources/conciergesv-develop/src/Command/DeleteDataCommand.php:54`（`$this->dropMonthlyTable('s_113', $dateTimeForMonth, 2);`）・同 `:110`（`$targetDateForDrop = $dateTime->subMonths($keepMonths);`）。`t_202` は同 `:47`、`s_102` は同 `:49`、削除対象日の計算は同 `:85`。

**多重起動防止と中断時の安全性**：シェル側で `flock -n` により多重起動を防ぐ。ロック対象は `exec {my_fd}< "$0"` すなわちスクリプトファイル自身だが、**本バッチは `_day1.sh` にしか記述されていないため、これで十分**である（毎日実行される2バッチのように、毎月1日に2つのシェルが同時起動して2回走るという問題は起きない）。あわせて `set -eu` により CSV/ZIP 生成が失敗した時点で処理が止まり、後続の `DeleteData` に到達しない。**猶予が無い設計であっても「ファイル化されないまま DROP される」ことは起きない。**

> 出典：同 tgz 内 `12_CreateCsvAndDeleteData_day1.sh`（`flock -n ${my_fd}` / `set -eu` / `trap error_handler ERR`。シェル内の実行順は DeviceStatuses → HourlyValues → DailyValues → **本バッチ** → `DeleteData` → `DeleteLogicalDeletedDevices` で、本バッチは `DeleteData` より前）
> 設計意図は `legacy_eminel_docs/docs/02_詳細設計/10_バッチ処理/cron設定概要.txt:29-32` 補足1 に明記（引用は `:32`）：「CSV作成が失敗した場合はDBのデータを消去するコマンドは実施されない。」

### 2.2 データ取得

このバッチは SQL を直接書かず、CakePHP の ORM で読み出す。**契約者一覧の取得（`distinct('c001')`）が無い**のが他3バッチとの構造的な違い。

```php
// ⓪ 対象月からパーティション名を組み立て、ORM をその子テーブルに向ける
$partitionTableName   = 's_113_' . $dateTime->subDays(32)->format('Ym');
$conSensorDailyValues = TableRegistry::getTableLocator()->get('EminelSvLib.' . $partitionTableName);

// ① 対象月のレコードを 4,000 件ずつページング（契約者による分割なし）
$targetDatas = $conSensorDailyValues->find()
    ->where([
        'c003' => $prevMonthStart->format('Ymd')   // 対象年月＝月初日で絞り込み
    ])
    ->limit($pageSize)      // $pageSize = 4000
    ->page($page)
    ->all();
```
出典：`legacy_eminel_docs/sources/conciergesv-develop/src/Command/CreateCsvAndZipConSensorDailyAveValuesCommand.php:39, 41`（⓪）・`:90-96`（①）・`:48-49`（`$pageSize = 4000`）。

> 補足：変数名は `$conSensorDailyValues` だが、取得しているテーブルは `s_113`（平均値）である（同 `:39, 41`）。`s_103` を扱う別バッチからのコード流用と思われる（🔸*推定* — コード上に説明は無い。必要なら mui 側へ照会）。読む際に混同しないよう注意。

**CSV 列と DB 列の対応**（コード内の `$columnNames` と `$headers` が同じ順序で並ぶことから導出）：

| CSV 列名 | DB 列 | 意味 |
|---|---|---|
| 機器種別 | `c001` | 機器の種別コード ⚠️ **他3テーブルの `c001`（EMS-SP）とは意味が違う** |
| 設置場所 | `c002` | 機器の設置場所コード |
| 対象年月 | `c003` | このレコードが表す**月**（**日時型 → 書式変換対象**） |
| グループ属性1〜5 | `c111`〜`c115` | 他世帯比較（グルーピング）に使う属性5項目 |
| 1日〜31日 | `c011`〜`c041` | **1か月31日分の日別平均値が31列に横並び** |
| 更新日時 | `c051` | レコード更新日時（**日時型 → 書式変換対象**） |

> 出典：同 `:77-82`（CSV ヘッダー 40 列）・`:102-107`（DB 列名 40 個）。
> 列数の内訳：3 + 5 + 31 + 1 = **40 列**。

列番号の意味はテーブルごとに異なる。`s_113` では `c001` が「機器種別」、`c003` が「対象年月」だが、`s_103`／`s_102`／`t_202` では `c001` が「EMS-SP」、`c003` は「設置場所」または「通信種別」を指す。移行時にテーブル横断でマッピングを組むときは、列番号ではなくテーブルごとの定義に従う必要がある。

**このテーブルが「平均値」である意味**：`s_113` は個々の世帯の実測値ではなく、機器種別・設置場所・グループ属性の組み合わせごとに集計された平均値を保持する。アプリの「他世帯との比較」表示や、レポートの平均線を描くための基礎データにあたる。そのため EMS-SP 列が存在せず、CSV も世帯ごとに分割されない。

### 2.3 CSV 生成ロジック

```
① 出力フォルダを決める:  {CON_SENSOR_DAILY_AVE_VALUES_CSV_FILES_PATH}/{月初Ymd}_{月末Ymd}
   └ 無ければ mkdir（パーミッション 0777、umask を一時的に 0 にして作成）

② CSV を1本だけ作成（契約者ループなし）:
   ファイル名 = {月初Ymd}_{月末Ymd}_1日平均値.csv     ← EMS-SP がファイル名に付かない
   fopen(..., 'a')  ← 追記モード

   ├ ファイルが新規、またはサイズ 0 の場合のみ:
   │    UTF-8 BOM（\xEF\xBB\xBF）を書き込む — ファイル先頭3バイトの符号化目印
   │       （🔸 コメントは「UTF-8 BOM 形式」のみ。Excel の文字化け対策という解釈は推定）
   │    40 列のヘッダー行を書き込む
   │
   └ 4,000 件ずつページングしながら対象月のレコードを1行ずつ書き込む:
        c003（対象年月）と c051（更新日時）のみ
            'Y-m-d H:i:s.v' + タイムゾーン先頭3文字に整形
            → 例: 2024-07-01 05:15:00.123 +09（`.v` はミリ秒）
        それ以外の列は値をそのまま出力

③ 曜日判定なしで必ず: フォルダ内の *.csv を ZIP 化（2.4 参照）
```
出典：`legacy_eminel_docs/sources/conciergesv-develop/src/Command/CreateCsvAndZipConSensorDailyAveValuesCommand.php:50-59`（①）・`:62-85`（②のファイル名と BOM、コメントは `:74`）・`:110-122`（行の書き出しと日時整形）・`:129-135`（③）。

**業務定数・環境変数**：

| 名称 | 値 | 出典 |
|---|---|---|
| `CON_SENSOR_DAILY_AVE_VALUES_CSV_FILES_PATH` | `/var/data/ConSensorDailyAveValues/` | `legacy_eminel_docs/sources/conciergesv-develop/config/.env.prod:65`（`.env.dev` / `.env.stage` / `.env.local` も同値） |
| `$pageSize` | 4000（コメント：「一度に処理するレコードの量、vagrant は4000個が限界」） | `…/CreateCsvAndZipConSensorDailyAveValuesCommand.php:48-49` |
| 対象月オフセット | 32日（＝前々月に着地させるための値） | 同 `:39` |

### 2.4 出力先とファイル化（ZIP）

**ディレクトリ構成**：

```
/var/data/ConSensorDailyAveValues/          ← 実行を重ねると月別 ZIP が並ぶ（過去分は消えない）
├── 20240601_20240630.zip
└── 20240701_20240731.zip                   ← 月フォルダを圧縮したもの（フォルダは毎回削除される）
    └─ 中身: 20240701_20240731_1日平均値.csv.zip     ← 1本だけ
```

**ZIP 化の手順**（共通 trait `CreateZipsTrait::createZip`）：

```
① CSV を1本ずつ個別に ZIP 化 → {ファイル名}.csv.zip
   └ ZIP 内のファイル名は SJIS に変換（mb_convert_encoding(..., 'SJIS', 'UTF-8')）
      ← 🔸変換の意図はコードにコメントが無く推定。Windows 標準の解凍ソフトで
         日本語ファイル名が壊れないようにするためと考えられる
② 元の CSV を unlink（削除）
③ 個別 ZIP をすべてまとめて 1つのフォルダ ZIP に格納 → {月フォルダ}.zip
④ exec("rm -rf {月フォルダ}") でフォルダごと削除
   └ 各段階で失敗したら alert ログを出して Exception を投げる（部分的な成功で終わらせない）
→ ④ の後にディスクに残るのは {月}.zip 1本のみ。データは失われない
   （CSV が1本しかないため、フォルダ ZIP の中に個別 ZIP が1つだけ入る二重圧縮になる）
```
出典：`legacy_eminel_docs/sources/conciergesv-develop/src/Command/CreateZipsTrait.php:23-72`（`rm -rf` は `:64`。削除対象は月フォルダのみで、上位の `.zip` 群は残る）。**日次バッチと違い曜日判定が無く、実行のたびに必ず圧縮される。**

**生成されたファイルの利用者**：旧管理画面 `eminelsv` の「過去データ」ダウンロード機能。選択肢 `previous_day_ave`（画面表示名「1日値（平均値）」）が、このバッチの出力先ディレクトリを参照する。

> 出典：`legacy_eminel_docs/sources/eminelsv-develop/src/Controller/DownloadController.php:75`（選択肢の表示名）・`:416`（`'previous_day_ave' => env('DAY_VALUE_AVE_DIRECTORY')`）・`legacy_eminel_docs/sources/eminelsv-develop/config/.env.prod:82`（`DAY_VALUE_AVE_DIRECTORY = "/var/data/ConSensorDailyAveValues/"` — バッチ側と同一パス）。
> 管理画面側は既存の ZIP を日付で絞り込み、再梱包して返す（同 `:236` `createPreviousDataZip()` — 4選択肢で共通のメソッド。走査は `:298` の `RecursiveDirectoryIterator` でこのディレクトリを起点に再帰、日付での絞り込みは `:277-282`。**月次 ZIP が蓄積していることが前提**）。**新たに DB から作り直すのではなく、このバッチが作ったファイルを配るだけ**である点が重要。

### 2.5 確認：本バッチは平均の計算を行わない

名前に「平均値」とあるが、このバッチは平均を**計算しない**。平均値そのものは集計系バッチ `CalcCommonAverageDataCommand` が `s_113` に書き込んでおり（`legacy_eminel_docs/sources/conciergesv-develop/src/Command/CalcCommonAverageDataCommand.php:1283` で書き込み先を `EminelSvLib.ConSensorDailyAveValues` に指定、保存は同 `:468, 1013`）、本バッチはそれを CSV に転記するだけである。したがって移行時の論点は **「保持期間（2か月）を超えたデータをどう残すか」** に絞られる。

> 判定（バッチとして残すか・新システムでの代替方式）は別紙の移行調査総括表の該当行を参照。本バッチの結論は「バッチとしては不要」。
