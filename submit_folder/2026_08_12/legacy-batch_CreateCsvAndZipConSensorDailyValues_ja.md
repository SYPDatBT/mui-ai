# 旧バッチ調査 — CreateCsvAndZipConSensorDailyValuesCommand（センサー日別値 CSV/ZIP 生成）

## 概要

`CreateCsvAndZipConSensorDailyValuesCommand` は旧システム（EMINEL コンシェルジュサーバー）で **毎月1日 05:15 のみ**実行されるバッチである。月毎センサ情報テーブル `s_103` の **前々月**の月別パーティションを読み出し、**契約者（EMS-SP）ごとに1本の CSV** を書き出したうえで、**実行のたびに必ず ZIP 圧縮**してフォルダごと削除する。

1レコード＝1か月分で、**31日分の値が「1日」〜「31日」の31列に横並び**で入っている。同じシェル内で後続の `DeleteDataCommand` が**同じ前々月のパーティションを DROP** するため、このバッチは「消える直前の最後のバックアップ」にあたる。

**4バッチの位置づけ**（名称が紛らわしいため先に整理する）：

| バッチ | テーブル | モデル名 | 1レコード＝ | 1マスの値＝ | 実行周期 |
|---|---|---|---|---|---|
| DeviceStatuses | `t_202` | 機器状態情報 | 1回の収集 | — | 毎日 05:15 |
| HourlyValues | `s_102` | 日毎センサ情報 | 1日 | 1時間（24列） | 毎日 05:15 |
| **DailyValues（本書）** | `s_103` | 月毎センサ情報 | **1か月** | **1日（31列）** | 毎月1日 05:15 |
| DailyAveValues | `s_113` | 月毎平均センサ情報 | 1か月 | 1日・平均（31列） | 毎月1日 05:15 |

⚠️ 名称の注意：「1日値」は**値の粒度**（1マス＝1日）を指し、**実行頻度ではない**。本バッチは月1回のみ実行される。

> **本書の範囲**：旧システムの挙動調査のみ。本書には「E-GW での代替設計・移行手順・新旧対応表」は含まない。
> **参考までに総括表での判定**：結論＝**「バッチとしては不要」**、新システム側の対応機能＝**F-AD-09（データダウンロード：管理者が期間を指定した時点で生成する方式）**。根拠と全47バッチの一覧は別紙の移行調査総括表を参照。

## Part 1 — 概要

| 項目 | 内容 |
|---|---|
| **役割** | DB の保持期間（**2か月**）を過ぎると消える月別センサーデータを、消える直前に **CSV → ZIP でファイル化**して残す。**値の計算・集計は一切行わない**（詳細 2.5）。 |
| **Input** | DB テーブル `s_103` の月別パーティション `s_103_YYYYMM`（対象月 = 実行日 − 32日 が属する月 = **前々月**）。⚠️ コードは `TableRegistry::getTableLocator()->get('EminelSvLib.' . $partitionTableName)` でパーティション名を直接エイリアスに渡しており（`…Command.php:39, 41`）、共通ライブラリの `ConSensorDailyValuesTable` / エンティティ `ConSensorDailyValue`（物理テーブル `s_103`、モデル説明「月毎センサ情報」。`legacy_eminel_docs/sources/eminel_sv_lib-develop/src/Model/Table/ConSensorDailyValuesTable.php:41`）**そのものは経由しない**。列名は Command 内にハードコードされている（同 `:110-115`）。 |
| **Output** | ローカルファイルシステム上の CSV／ZIP。<br>・CSV：`{CON_SENSOR_DAILY_VALUES_CSV_FILES_PATH}/{月初}_{月末}/{EMS-SP}_{月初}_{月末}_1日値.csv`<br>・ZIP：**毎回**、上記フォルダを圧縮した `{月初}_{月末}.zip` |
| **処理概要** | 1. 対象月 M = （実行日 − 32日）が属する月 を決め、パーティション `s_103_{M:Ym}` の存在を確認する（無ければ alert ログを出して終了）。<br>2. そのパーティションに含まれる **EMS-SP の一覧**を取得する。<br>3. 契約者ごとに CSV を開き（追記モード）、初回のみ UTF-8 BOM と 42 列のヘッダー行を書く。<br>4. 対象月の月初日と一致するレコードのみを 4,000件ずつページングして読み、日時列だけ書式変換して書き出す。<br>5. **曜日判定なしで必ず** ZIP 化し、フォルダごと削除する。 |

## Part 2 — 詳細

### 2.1 実行スケジュールと対象月

| 項目 | 内容 | 出典 |
|---|---|---|
| 実行スケジュール（cron） | `15 5 1 * *` — **毎月1日 05:15 のみ**。月初シェル `12_CreateCsvAndDeleteData_day1.sh` にのみ含まれ、日次シェル `_day2to31.sh` には**含まれない** | `legacy_eminel_docs/docs/02_詳細設計/10_バッチ処理/mng-webap_cron設定_20241029.txt:41`（節見出し `#12.DBデータ削除` は `:39`） |
| 実行コマンド | `sudo -u apache php /var/www/vhost/conciergesv/bin/cake.php CreateCsvAndZipConSensorDailyValues`（apache ユーザーで実行） | `legacy_eminel_docs/docs/02_詳細設計/10_バッチ処理/cron実行用シェルスクリプト/eminel-mng-webap.20240909.tgz` 内 `12_CreateCsvAndDeleteData_day1.sh` |
| 引数 | `--datetime`（既定値 `'now'`） | `legacy_eminel_docs/sources/conciergesv-develop/src/Command/CreateCsvAndZipConSensorDailyValuesCommand.php:28, 36` |
| **対象月 M** | `（実行日時 − 32日）が属する月` → パーティション名 `s_103_{M:Ym}` | 同 `:39` |
| 出力先フォルダの期間 | M の **月初〜月末**（`startOfMonth()` / `endOfMonth()`） | 同 `:56-58` |
| ZIP 化のタイミング | **毎回**（曜日判定なし） | 同 `:138-144` |

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
| **DailyValues（`s_103`、保持2か月、本書）** | **前々月** | **同じ前々月・同一実行内** | **0** |

つまり **同じ日の同じシェルの中で、「前々月を CSV/ZIP 化 → その前々月のパーティションを DROP」** という順序で完結する。日次バッチが数日の余裕を持つのに対し、こちらは**猶予がなく、書き出しと削除が連続する**。

> 出典：`legacy_eminel_docs/sources/conciergesv-develop/src/Command/DeleteDataCommand.php:53`（`$this->dropMonthlyTable('s_103', $dateTimeForMonth, 2);`）・同 `:110`（`$targetDateForDrop = $dateTime->subMonths($keepMonths);` → 実行日の2か月前）。`t_202` は同 `:47`、`s_102` は同 `:49`、削除対象日の計算は同 `:85`。

**多重起動防止と中断時の安全性**：シェル側で `flock -n` により多重起動を防ぐ。ロック対象は `exec {my_fd}< "$0"` すなわちスクリプトファイル自身だが、**本バッチは `_day1.sh` にしか記述されていないため、これで十分**である（毎日実行される2バッチのように、毎月1日に2つのシェルが同時起動して2回走るという問題は起きない）。あわせて `set -eu` により CSV/ZIP 生成が失敗した時点で処理が止まり、後続の `DeleteData` に到達しない。**猶予が無い設計であっても「ファイル化されないまま DROP される」ことは起きない。**

> 出典：同 tgz 内 `12_CreateCsvAndDeleteData_day1.sh`（`flock -n ${my_fd}` / `set -eu` / `trap error_handler ERR`。シェル内の実行順は DeviceStatuses → HourlyValues → **本バッチ** → DailyAveValues → `DeleteData` → `DeleteLogicalDeletedDevices` で、本バッチは `DeleteData` より前）
> 設計意図は `legacy_eminel_docs/docs/02_詳細設計/10_バッチ処理/cron設定概要.txt:29-32` 補足1 に明記（引用は `:32`）：「CSV作成が失敗した場合はDBのデータを消去するコマンドは実施されない。」

### 2.2 データ取得

このバッチは SQL を直接書かず、CakePHP の ORM で読み出す。下のコードは2点を示す：⓪ ORM を**対象月の子テーブルそのもの**に向けていること、①② 契約者ごとに 4,000 件ずつページングしていること。

```php
// ⓪ 対象月からパーティション名を組み立て、ORM をその子テーブルに向ける
$partitionTableName   = 's_103_' . $dateTime->subDays(32)->format('Ym');
$conSensorDailyValues = TableRegistry::getTableLocator()->get('EminelSvLib.' . $partitionTableName);

// ① 対象パーティションに存在する EMS-SP の一覧
$c001Values = $conSensorDailyValues->find()
    ->select(['c001'])
    ->distinct(['c001'])
    ->all();

// ② 契約者ごとに、対象月のレコードだけを 4,000 件ずつページング
$targetDatas = $conSensorDailyValues->find()
    ->where([
        'c001' => $c001Value->c001,
        'c004' => $prevMonthStart->format('Ymd')   // 対象年月＝月初日で絞り込み
    ])
    ->limit($pageSize)      // $pageSize = 4000
    ->page($page)
    ->all();
```
出典：`legacy_eminel_docs/sources/conciergesv-develop/src/Command/CreateCsvAndZipConSensorDailyValuesCommand.php:39, 41`（⓪）・`:49-52`（①）・`:97-104`（②）・`:55`（`$pageSize = 4000`）。

**日次バッチとの違い**：機器状態・時間別値のバッチは `c001` のみで絞るのに対し、こちらは **`c004`（対象年月）も条件に加える**。月別パーティション内に他月のレコードが混在しうることを想定した防御的な絞り込みと思われる（🔸*推定* — コードに説明コメントは無い。必要なら mui 側へ照会）。

**CSV 列と DB 列の対応**（コード内の `$columnNames` と `$headers` が同じ順序で並ぶことから導出）：

| CSV 列名 | DB 列 | 意味 |
|---|---|---|
| EMS-SP | `c001` | 契約者番号（EMS-SP-NO） |
| 機器種別 | `c002` | 機器の種別コード |
| 設置場所 | `c003` | 機器の設置場所コード |
| 対象年月 | `c004` | このレコードが表す**月**（**日時型 → 書式変換対象**） |
| 集計遡及フラグ | `c009` | 過去の集計値が再計算されたことを上位集計へ知らせる**作業フラグ**（1＝要再集計）。定数名は `C_NEED_AGG_COMPLETE_FLAG` — `legacy_eminel_docs/sources/eminel_sv_lib-develop/src/Model/Entity/ConSensorDailyValue.php:63`。設定箇所は `legacy_eminel_docs/sources/conciergesv-develop/src/Command/CalcMonthlyAccumulatedValueCommand.php:267, 282` |
| グループ属性1〜5 | `c111`〜`c115` | 他世帯比較（グルーピング）に使う属性5項目 |
| 1日〜31日 | `c011`〜`c041` | **1か月31日分の日別値が31列に横並び** |
| 更新日時 | `c051` | レコード更新日時（**日時型 → 書式変換対象**） |

> 出典：同 `:84-89`（CSV ヘッダー 42 列）・`:110-115`（DB 列名 42 個）。
> 列数の内訳：5 + 5 + 31 + 1 = **42 列**。

**データ構造の注意点**：31列が固定で存在するため、30日以下の月では末尾の列が未使用のまま残る。この横持ち構造は時間別値テーブル（`s_102` の24列）と同じ設計思想である。

### 2.3 CSV 生成ロジック

```
① 出力フォルダを決める:  {CON_SENSOR_DAILY_VALUES_CSV_FILES_PATH}/{月初Ymd}_{月末Ymd}
   └ 無ければ mkdir（パーミッション 0777、umask を一時的に 0 にして作成）

② 契約者ごとにループ:
   ファイル名 = {EMS-SP}_{月初Ymd}_{月末Ymd}_1日値.csv
   fopen(..., 'a')  ← 追記モード
      ※ 月1回のみ実行され、実行の最後にフォルダごと削除されるため、実際には毎回新規作成となる。
        追記＋BOM 判定は日次バッチと同一の書き方（🔸*推定*：コード流用。コード上に説明は無い）。
        ⚠️ `--datetime` で手動再実行する際、旧ファイルが残っていると追記されて重複する点に注意

   ├ ファイルが新規、またはサイズ 0 の場合のみ:
   │    UTF-8 BOM（\xEF\xBB\xBF）を書き込む — ファイル先頭3バイトの符号化目印
   │       （🔸 コメントは「UTF-8 BOM 形式」のみ。Excel の文字化け対策という解釈は推定）
   │    42 列のヘッダー行を書き込む
   │
   └ 4,000 件ずつページングしながら対象月のレコードを1行ずつ書き込む:
        c004（対象年月）と c051（更新日時）のみ
            'Y-m-d H:i:s.v' + タイムゾーン先頭3文字に整形
            → 例: 2024-07-01 05:15:00.123 +09（`.v` はミリ秒）
        それ以外の列は値をそのまま出力

③ 曜日判定なしで必ず: フォルダ内の *.csv を ZIP 化（2.4 参照）
```
出典：`legacy_eminel_docs/sources/conciergesv-develop/src/Command/CreateCsvAndZipConSensorDailyValuesCommand.php:56-65`（①）・`:68-82`（②のファイル名と BOM、コメントは `:81`）・`:118-130`（行の書き出しと日時整形）・`:138-144`（③）。

**業務定数・環境変数**：

| 名称 | 値 | 出典 |
|---|---|---|
| `CON_SENSOR_DAILY_VALUES_CSV_FILES_PATH` | `/var/data/ConSensorDailyValues/` | `legacy_eminel_docs/sources/conciergesv-develop/config/.env.prod:64`（`.env.dev` / `.env.stage` / `.env.local` も同値） |
| `$pageSize` | 4000（コメント：「一度に処理するレコードの量、vagrant は4000個が限界」） | `…/CreateCsvAndZipConSensorDailyValuesCommand.php:54-55` |
| 対象月オフセット | 32日（＝前々月に着地させるための値） | 同 `:39` |

### 2.4 出力先とファイル化（ZIP）

**ディレクトリ構成**：

```
/var/data/ConSensorDailyValues/             ← 実行を重ねると月別 ZIP が並ぶ（過去分は消えない）
├── 20240601_20240630.zip
└── 20240701_20240731.zip                   ← 月フォルダを圧縮したもの（フォルダは毎回削除される）
    └─ 中身: 00000000001_20240701_20240731_1日値.csv.zip
             00000000002_20240701_20240731_1日値.csv.zip
             …（契約者数だけ個別 ZIP が並ぶ）
```

※ EMS-SP は**最低11桁**として検証される（`legacy_eminel_docs/sources/eminel_sv_lib-develop/src/Model/Table/EmsSpNosTable.php:69` — `minLength('ems_sp_no', 11, …)`、メッセージは「有効な11桁の数字を入力してください」。`maxLength` ルールは無い）。管理画面はファイル名の先頭11文字で絞り込むため、実用上は11桁として扱われる（`legacy_eminel_docs/sources/eminelsv-develop/src/Controller/DownloadController.php:338`）。

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
   （フォルダ ZIP の中に CSV 個別 ZIP が入る二重構造）
```
出典：`legacy_eminel_docs/sources/conciergesv-develop/src/Command/CreateZipsTrait.php:23-72`（`rm -rf` は `:64`。削除対象は月フォルダのみで、上位の `.zip` 群は残る）。**日次バッチと違い曜日判定が無く、実行のたびに必ず圧縮される。**

**生成されたファイルの利用者**：旧管理画面 `eminelsv` の「過去データ」ダウンロード機能。選択肢 `previous_day_value`（画面表示名「1日値（過去データ）」）が、このバッチの出力先ディレクトリを参照する。

> 出典：`legacy_eminel_docs/sources/eminelsv-develop/src/Controller/DownloadController.php:74`（選択肢の表示名）・`:415`（`'previous_day_value' => env('DAY_VALUE_DIRECTORY')`）・`legacy_eminel_docs/sources/eminelsv-develop/config/.env.prod:80`（`DAY_VALUE_DIRECTORY = "/var/data/ConSensorDailyValues/"` — バッチ側と同一パス）。
> 管理画面側は既存の ZIP を日付・EMS-SP で絞り込み、再梱包して返す（同 `:236` `createPreviousDataZip()` — 4選択肢で共通のメソッド。走査は `:298` の `RecursiveDirectoryIterator` でこのディレクトリを起点に再帰、日付での絞り込みは `:277-282`。**月次 ZIP が蓄積していることが前提**）。**新たに DB から作り直すのではなく、このバッチが作ったファイルを配るだけ**である点が重要。

### 2.5 確認：本バッチは集計・計算を行わない

このバッチは値の計算・集計を一切行わない。`s_103` に既に集計済みの日別値をそのまま CSV に転記するだけである。したがって移行時の論点は **「保持期間（2か月）を超えたデータをどう残すか」** に絞られる。

> 判定（バッチとして残すか・新システムでの代替方式）は別紙の移行調査総括表の該当行を参照。本バッチの結論は「バッチとしては不要」。
