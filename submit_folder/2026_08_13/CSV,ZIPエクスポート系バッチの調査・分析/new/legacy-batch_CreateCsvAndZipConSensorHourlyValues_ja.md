# 旧バッチ調査 — CreateCsvAndZipConSensorHourlyValuesCommand（センサー時間別値 CSV/ZIP 生成）

## 概要

`CreateCsvAndZipConSensorHourlyValuesCommand` は旧システム（EMINEL コンシェルジュサーバー）で **毎日 05:15** に実行されるバッチである。日毎センサ情報テーブル `s_102` の **8日前の日別パーティション**を読み出し、**契約者（EMS-SP）ごとに1本の CSV** として週単位フォルダへ書き出す。

毎日の実行で「8日前」を1日ずつ書き足していき、**毎週月曜のみ**、書き終えた週のフォルダを ZIP 圧縮してフォルダごと削除する。1レコード＝1日分で、**24時間分の値が 00時台〜23時台の24列に横並び**で入っている点が特徴。処理の骨格は機器状態バッチ（`CreateCsvAndZipConDeviceStatusesCommand`）と同一で、対象テーブルと列構成だけが異なる。

**4バッチの位置づけ**（名称が紛らわしいため先に整理する）：

| バッチ | テーブル | モデル名 | 1レコード＝ | 1マスの値＝ | 実行周期 |
|---|---|---|---|---|---|
| DeviceStatuses | `t_202` | 機器状態情報 | 1回の収集 | — | 毎日 05:15 |
| **HourlyValues（本書）** | `s_102` | 日毎センサ情報 | **1日** | **1時間（24列）** | 毎日 05:15 |
| DailyValues | `s_103` | 月毎センサ情報 | 1か月 | 1日（31列） | 毎月1日 05:15 |
| DailyAveValues | `s_113` | 月毎平均センサ情報 | 1か月 | 1日・平均（31列） | 毎月1日 05:15 |

⚠️ 名称の注意：「1時間値」は**値の粒度**（1マス＝1時間）を指し、**実行頻度ではない**。バッチ名（Hourly）とモデル名（日毎センサ情報）が逆に見えるのは、バッチ名が「出力する値の単位」を、モデル名が「1レコードが表す期間」を指しているため。

> **本書の範囲**：旧システムの挙動調査のみ。本書には「E-GW での代替設計・移行手順・新旧対応表」は含まない。
> **参考までに総括表での判定**：結論＝**「バッチとしては不要」**、新システム側の対応機能＝**F-AD-09（データダウンロード：管理者が期間を指定した時点で生成する方式）**。根拠と全47バッチの一覧は別紙の移行調査総括表を参照。

## Part 1 — 概要

| 項目 | 内容 |
|---|---|
| **役割** | DB の保持期間（**14日**）を過ぎると消えるセンサー時間別値を、消える前に **CSV → ZIP でファイル化**して残す。**値の計算・集計は一切行わない**（詳細 2.5）。 |
| **Input** | DB テーブル `s_102` の日別パーティション `s_102_YYYYMMDD`（対象日 = 実行日 − 8日）。⚠️ コードは `TableRegistry::getTableLocator()->get('EminelSvLib.' . $partitionTableName)` でパーティション名を直接エイリアスに渡しており（`…Command.php:39, 41`）、共通ライブラリの `ConSensorHourlyValuesTable` / エンティティ `ConSensorHourlyValue`（物理テーブル `s_102`、モデル説明「日毎センサ情報」。`legacy_eminel_docs/sources/eminel_sv_lib-develop/src/Model/Table/ConSensorHourlyValuesTable.php:41`）**そのものは経由しない**。列名は Command 内にハードコードされている（同 `:108-113`）。 |
| **Output** | ローカルファイルシステム上の CSV／ZIP。<br>・CSV：`{CON_SENSOR_HOURLY_VALUES_CSV_FILES_PATH}/{週開始}_{週終了}/{EMS-SP}_{週開始}_{週終了}_1時間値.csv`<br>・ZIP：月曜のみ、上記フォルダを圧縮した `{週開始}_{週終了}.zip` |
| **処理概要** | 1. 対象日 T = 実行日 − 8日 を決め、パーティション `s_102_{T:Ymd}` の存在を確認する（無ければ alert ログを出して終了）。<br>2. そのパーティションに含まれる **EMS-SP の一覧**を取得する。<br>3. 契約者ごとに CSV を開き（追記モード）、初回のみ UTF-8 BOM と 36 列のヘッダー行を書く。<br>4. 4,000件ずつページングしながら全レコードを読み、日時列だけ書式変換して1行ずつ書き出す。<br>5. **実行日が月曜の場合のみ**、当該フォルダ内の CSV を ZIP 化し、フォルダごと削除する。 |

## Part 2 — 詳細

### 2.1 実行スケジュールと対象日

| 項目 | 内容 | 出典 |
|---|---|---|
| 実行スケジュール（cron） | `15 5 * * *`（日次シェル）**と** `15 5 1 * *`（月初シェル）— 本バッチは**両シェルに記述**されており、05:15 に毎日起動する。※ 毎月1日の挙動は下の「毎月1日に何が起きるか」を参照 | `legacy_eminel_docs/docs/02_詳細設計/10_バッチ処理/mng-webap_cron設定_20241029.txt:40-41`（節見出し `#12.DBデータ削除` は `:39`） |
| 実行コマンド | `sudo -u apache php /var/www/vhost/conciergesv/bin/cake.php CreateCsvAndZipConSensorHourlyValues`（apache ユーザーで実行） | `legacy_eminel_docs/docs/02_詳細設計/10_バッチ処理/cron実行用シェルスクリプト/eminel-mng-webap.20240909.tgz` 内 `12_CreateCsvAndDeleteData_day2to31.sh`（同 `_day1.sh` にも同一行あり） |
| 引数 | `--datetime`（既定値 `'now'`） | `legacy_eminel_docs/sources/conciergesv-develop/src/Command/CreateCsvAndZipConSensorHourlyValuesCommand.php:28, 36` |
| **対象日 T** | `実行日時 − 8日`。パーティション名 `s_102_{T:Ymd}` を組み立てる | 同 `:39` |
| 出力先フォルダの期間 | T が属する週の **月曜〜日曜**（`startOfWeek()` / `endOfWeek()`） | 同 `:56-58` |
| ZIP 化のタイミング | **実行日が月曜のときのみ**（`isMonday()`）。対象は「T が属する週」のフォルダ＝実行日から見て**前々週** | 同 `:137-145` |

⚠️ ソース内のコメント（同 `:136`「先週の CSV ファイル」）は「先週」と書かれているが、実際に圧縮されるのは**前々週**のフォルダである（機器状態バッチにも同一のコメントがある）。

月曜の実行では、そのフォルダの最終日（T＝日曜）分を書き終えた直後に圧縮するため、常に7日分が揃った状態で固められる。

**cron の読み方**：5つの欄は `分 時 日 月 曜日`。`15 5 * * *` = 05:15 に**毎日**／`15 5 1 * *` = 05:15 に**1日だけ**。

**毎月1日に何が起きるか** — 3点：

1. ファイル名 `…day2to31.sh` は**紛らわしい**。日の欄が `*` なので実際は **1〜31日すべて**動く（「2日から」ではない）。
2. したがって **毎月1日だけ本バッチは2回実行される**（`_day1.sh` と `_day2to31.sh` が同時刻に起動）。
3. `flock` はこの2重実行を**防げない**（理由は下記）。🔸 CSV は追記モードのため同一データが二重に書かれる可能性がある — **推定・実機未検証。必要なら mui 側へ照会**。

**ファイル化から削除までの猶予**：

| バッチ | ファイル化 | DB の DROP | 猶予 |
|---|---|---|---|
| DeviceStatuses（`t_202`、保持8日） | ある日 D の D+8日 | D+9日 | 1日 |
| **HourlyValues（`s_102`、保持14日、本書）** | **D+8日** | **D+15日** | **7日** |
| DailyValues / DailyAveValues（`s_103`/`s_113`） | 前々月 | 同じ前々月・同一実行内 | 0 |

`s_102` の保持期間は機器状態（`t_202` = 8日）より長いが、CSV 化は同じ「8日前」で行うため、結果として削除の7日前にはファイルが出来上がっている。🔸それが意図的な設計かはコード・設計書に記述が無く不明。

> 出典：`legacy_eminel_docs/sources/conciergesv-develop/src/Command/DeleteDataCommand.php:49`（`$this->dropDailyTable('s_102', $dateTimeForDay, 14);`）、削除対象日は同 `:85`（`$dateTime->subDays($keepDays + 1)`）。`t_202` は同 `:47`、`s_103`/`s_113` は同 `:53, 54`・`:110`。

**多重起動防止と中断時の挙動**：シェル側で `flock -n` による多重起動チェックを行う。ただしロック対象は `exec {my_fd}< "$0"` すなわち**スクリプトファイル自身**であるため、防げるのは「同一シェルの多重起動」だけで、**`_day1.sh` と `_day2to31.sh` が同時起動する毎月1日のケースは防げない**。あわせて `set -eu` により **いずれかのコマンドが失敗した時点で以降を実行しない**ため、CSV 生成が失敗すれば後続の `DeleteData` に到達しない。

> 出典：同 tgz 内 `12_CreateCsvAndDeleteData_day2to31.sh`（`flock -n ${my_fd}` / `set -eu` / `trap error_handler ERR`）
> 設計意図は `legacy_eminel_docs/docs/02_詳細設計/10_バッチ処理/cron設定概要.txt:29-32` 補足1 に明記（引用は `:32`）：「CSV作成が失敗した場合はDBのデータを消去するコマンドは実施されない。」

### 2.2 データ取得

このバッチは SQL を直接書かず、CakePHP の ORM で読み出す。下のコードは2点を示す：⓪ ORM を**対象日の子テーブルそのもの**に向けていること、①② 契約者ごとに 4,000 件ずつページングしていること。

```php
// ⓪ 対象日からパーティション名を組み立て、ORM をその子テーブルに向ける
$partitionTableName    = 's_102_' . $dateTime->subDays(8)->format('Ymd');
$conSensorHourlyValues = TableRegistry::getTableLocator()->get('EminelSvLib.' . $partitionTableName);

// ① 対象パーティションに存在する EMS-SP の一覧
$c001Values = $conSensorHourlyValues->find()
    ->select(['c001'])
    ->distinct(['c001'])
    ->all();

// ② 契約者ごとに 4,000 件ずつページングして全件取得
$targetDatas = $conSensorHourlyValues->find()
    ->where(['c001' => $c001Value->c001])
    ->limit($pageSize)      // $pageSize = 4000
    ->page($page)
    ->all();
```
出典：`legacy_eminel_docs/sources/conciergesv-develop/src/Command/CreateCsvAndZipConSensorHourlyValuesCommand.php:39, 41`（⓪）・`:49-52`（①）・`:98-102`（②）・`:55`（`$pageSize = 4000`）。

**日付での絞り込みが無い理由**：対象テーブル自体が `s_102_YYYYMMDD` という**1日1枚の日別パーティション**であり、テーブルを選んだ時点で対象日が確定しているため。

**CSV 列と DB 列の対応**（コード内の `$columnNames` と `$headers` が同じ順序で並ぶことから導出）：

| CSV 列名 | DB 列 | 意味 |
|---|---|---|
| EMS-SP | `c001` | 契約者番号（EMS-SP-NO） |
| 機器種別 | `c002` | 機器の種別コード |
| 設置場所 | `c003` | 機器の設置場所コード |
| 対象年月日 | `c004` | このレコードが表す**日付**（**日時型 → 書式変換対象**） |
| 消費電力量遡及フラグ | `c008` | 消費電力量側の遡及フラグ。定数名は `C_NEED_ELE_COMPLETE_FLAG`（`legacy_eminel_docs/sources/eminel_sv_lib-develop/src/Model/Entity/ConSensorHourlyValue.php:57`、`_accessible` は `:100`）。🔸 `conciergesv-develop/src`・`eminel_sv_lib-develop/src` を検索しても**この定数を読み書きする箇所は無く**、値の意味は未検証（要 mui 確認） |
| 集計遡及フラグ | `c009` | 過去日の再計算を上位集計へ知らせる**作業フラグ**。**1＝要再集計 → 2＝上位集計反映済み**。定数名は `C_NEED_AGG_COMPLETE_FLAG`（同 `:58`）。状態遷移は `legacy_eminel_docs/sources/conciergesv-develop/src/Command/CalcMonthlyAccumulatedValueCommand.php:220`（`= 1` で抽出）→ `:213`（`= 2` を set）。※ 同ファイル `:267`・`:282` でも `= 1` を設定するが、対象は `ConSensorDailyValue`（`s_103` の `c009`）である |
| グループ属性1〜5 | `c111`〜`c115` | 他世帯比較（グルーピング）に使う属性5項目 |
| 00時台〜23時台 | `c011`〜`c034` | **1日24時間分の時間別値が24列に横並び** |
| 更新日時 | `c041` | レコード更新日時（**日時型 → 書式変換対象**） |

> 出典：同 `:84-90`（CSV ヘッダー 36 列）・`:108-113`（DB 列名 36 個）。
> 列数の内訳：6 + 5 + 24 + 1 = **36 列**。

**データ構造の注意点**：`s_102` は「1レコード＝1契約者・1機器・1日」であり、24時間分の値が縦（24行）ではなく**横（24列）**に持たれている。移行先で同じデータを扱う場合、この横持ち構造をそのまま踏襲するのか、時刻ごとの縦持ちに変えるのかで設計が変わる。

### 2.3 CSV 生成ロジック

```
① 出力フォルダを決める:  {CON_SENSOR_HOURLY_VALUES_CSV_FILES_PATH}/{週開始Ymd}_{週終了Ymd}
   └ 無ければ mkdir（パーミッション 0777、umask を一時的に 0 にして作成）

② 契約者ごとにループ:
   ファイル名 = {EMS-SP}_{週開始Ymd}_{週終了Ymd}_1時間値.csv
   fopen(..., 'a')  ← 追記モード（毎日実行され、同じ週フォルダに1週間分を積み増すため）

   ├ ファイルが新規、またはサイズ 0 の場合のみ:
   │    UTF-8 BOM（\xEF\xBB\xBF）を書き込む — ファイル先頭3バイトの符号化目印
   │       （🔸 コメントは「UTF-8 BOM 形式」のみ。Excel の文字化け対策という解釈は推定）
   │    36 列のヘッダー行を書き込む
   │
   └ 4,000 件ずつページングしながら全レコードを1行ずつ書き込む:
        c004（対象年月日）と c041（更新日時）のみ
            'Y-m-d H:i:s.v' + タイムゾーン先頭3文字に整形
            → 例: 2024-09-02 05:15:00.123 +09（`.v` はミリ秒）
        それ以外の列は値をそのまま出力

③ 実行日が月曜の場合のみ: フォルダ内の *.csv を ZIP 化（2.4 参照）
```
出典：`legacy_eminel_docs/sources/conciergesv-develop/src/Command/CreateCsvAndZipConSensorHourlyValuesCommand.php:56-65`（①）・`:68-82`（②のファイル名と BOM、コメントは `:81`）・`:116-132`（行の書き出しと日時整形）・`:137-145`（③）。

**業務定数・環境変数**：

| 名称 | 値 | 出典 |
|---|---|---|
| `CON_SENSOR_HOURLY_VALUES_CSV_FILES_PATH` | `/var/data/ConSensorHourlyValues/` | `legacy_eminel_docs/sources/conciergesv-develop/config/.env.prod:63`（`.env.dev` / `.env.stage` / `.env.local` も同値） |
| `$pageSize` | 4000（コメント：「一度に処理するレコードの量、vagrant は4000個が限界」） | `…/CreateCsvAndZipConSensorHourlyValuesCommand.php:54-55` |
| 対象日オフセット | 8日 | 同 `:39` |

### 2.4 出力先とファイル化（ZIP）

**ディレクトリ構成**：

```
/var/data/ConSensorHourlyValues/            ← 実行を重ねると週別 ZIP が並ぶ（過去分は消えない）
├── 20240902_20240908/                      ← 週フォルダ（月曜〜日曜）
│   ├── 00000000001_20240902_20240908_1時間値.csv
│   ├── 00000000002_20240902_20240908_1時間値.csv
│   └── …（契約者数だけ CSV が並ぶ）
└── 20240826_20240901.zip                   ← 一つ前の週フォルダ。その週の最終データ（日曜分）を
    │                                          書き終えた月曜に圧縮済み（フォルダは削除される）
    └─ 中身: 00000000001_20240826_20240901_1時間値.csv.zip
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
③ 個別 ZIP をすべてまとめて 1つのフォルダ ZIP に格納 → {週フォルダ}.zip
④ exec("rm -rf {週フォルダ}") でフォルダごと削除
   └ 各段階で失敗したら alert ログを出して Exception を投げる（部分的な成功で終わらせない）
→ ④ の後にディスクに残るのは {週}.zip 1本のみ。データは失われない
   （フォルダ ZIP の中に CSV 個別 ZIP が入る二重構造）
```
出典：`legacy_eminel_docs/sources/conciergesv-develop/src/Command/CreateZipsTrait.php:23-72`（`rm -rf` は `:64`。削除対象は週フォルダのみで、上位の `.zip` 群は残る）。

**生成されたファイルの利用者**：旧管理画面 `eminelsv` の「過去データ」ダウンロード機能。選択肢 `previous_hour_value`（画面表示名「1時間値（過去データ）」）が、このバッチの出力先ディレクトリを参照する。

> 出典：`legacy_eminel_docs/sources/eminelsv-develop/src/Controller/DownloadController.php:73`（選択肢の表示名）・`:418`（`'previous_hour_value' => env('HOUR_VALUE_DIRECTORY')`）・`legacy_eminel_docs/sources/eminelsv-develop/config/.env.prod:86`（`HOUR_VALUE_DIRECTORY = "/var/data/ConSensorHourlyValues/"` — バッチ側と同一パス）。
> 管理画面側は既存の ZIP を日付・EMS-SP で絞り込み、再梱包して返す（同 `:236` `createPreviousDataZip()` — 4選択肢で共通のメソッド。走査は `:298` の `RecursiveDirectoryIterator`、日付での絞り込みは `:277-282`）。**新たに DB から作り直すのではなく、このバッチが作ったファイルを配るだけ**である点が重要。

### 2.5 確認：本バッチは集計・計算を行わない

このバッチは値の計算・集計を一切行わない。`s_102` に既に集計済みの時間別値をそのまま CSV に転記するだけである（時間別値そのものを作るのは別の集計系バッチ）。したがって移行時の論点は **「保持期間（14日）を超えたデータをどう残すか」** に絞られる。

> 判定（バッチとして残すか・新システムでの代替方式）は別紙の移行調査総括表の該当行を参照。本バッチの結論は「バッチとしては不要」。
