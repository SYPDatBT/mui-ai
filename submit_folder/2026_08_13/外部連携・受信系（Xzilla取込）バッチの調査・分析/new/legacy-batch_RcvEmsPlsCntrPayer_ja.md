# 旧バッチ ― RcvEmsPlsCntrPayerCommand（Xzilla場所契約支払者マスタ受信・契約終了判定・顧客連携番号更新）

## 概要

`RcvEmsPlsCntrPayerCommand`（CLIコマンド `RcvEmsPlsCntrPayer`、IF2264）は、旧システム（EMINELコンシェルジュサーバー）において、中継サーバーXzillaから**場所契約支払者マスタCSV**（EMS‑SPごとに紐づく情報）を受信するバッチである。1回の実行で当日のCSVファイルちょうど1件を処理する：`ipf_ems_pls_cntr_payers` テーブルの旧データを**全件削除**したうえで、規定の7つの契約種別コードに該当するレコードのみを**再登録**し、その後、取得した各EMS‑SPについて**契約が終了しているか否かを判定する3つの条件**を適用して次のように決定する：終了している場合→各連携番号を削除し（お客様番号はそのまま保持）、`ConCustomers` 上の売買電計算停止フラグを立てる；終了していない場合→各連携番号をすべて更新し、計算停止フラグを下ろす。最後に、同日の電力契約解約ファイル（IF2249、`RcvCntctCancellationCommand`）も完了済みであれば、バッチはさらに顧客情報登録完了通知APIを1回呼び出す ― これは**双方向**の条件であり、当日中に2つのバッチのうち**後**に実行を終えた側がAPIの呼び出し元となる。全体は1つのトランザクション内にある；詳細は第2部に示す。

## 第1部 ― 概要

| 項目 | 内容 |
|---|---|
| **役割** | Xzillaから場所契約支払者マスタCSV（IF2264）を受信し、`ipf_ems_pls_cntr_payers` テーブルを全件置き換えたうえで、契約終了を判定して `ConCustomers` 上の売買電の連携番号および計算停止フラグを更新する。 |
| **入力** | 中継サーバーXzilla上のCSVファイル（パスは環境変数 `XZILLA_RELATION_SERVER_MASTER_URL` から取得）＋ `XzillaRelationLogs` テーブル（重複防止）＋ `ipf_ems_pls_cntr_payers` テーブル（登録したばかりのデータを同一実行内で読み直す）。 |
| **出力** | `ipf_ems_pls_cntr_payers` テーブルの**全件削除＋再登録**＋ `ConCustomers` テーブルのUPDATE（`c061`/`c062`/`c063`/`c064`/`c065`/`c054`）＋ `XzillaRelationLogs` へのログ書き込み＋（条件付きで）完了通知APIの呼び出し。 |
| **処理概要** | 1. 中継サーバー上の当日のCSVファイルを選択する；ログにより重複処理を防止する。<br>2. CSVをダウンロードし、「処理中」のログを書き込む。<br>3. `ipf_ems_pls_cntr_payers` を全件削除し、規定の7つの契約コードのみを再登録する。<br>4. 各EMS‑SPについて：契約終了を判定し（3条件）→ `ConCustomers` を更新する。<br>5. 「完了」のログを書き込む。当日のIF2249（電力契約解約）も完了済みであれば、通知APIを呼び出す。 |

## 第2部 ― 詳細

### 処理フローのマップ ― 1つのトランザクション内

```
ステップ1  ファイル一覧の取得     → 中継ディレクトリを読み、.csv で絞り込み、timestamp降順でsort   §2.1
ステップ2  当日ファイルの選択     → timestamp が当日の [00:00:00, 23:59:59] の範囲内             §2.1
ステップ3  重複処理の防止         → (upload_type=2, file_name) でログを照会 ― status 0/1 → 停止  §2.2
ステップ4  ファイル取得＆ログ書込 → CSVをローカルへダウンロード、「処理中」ログをinsert/update   §2.3
ステップ5  旧マスタの全件削除     → ipf_ems_pls_cntr_payers に対し deleteAll('1=1')              §2.4
ステップ6  絞り込み＆再登録       → 7つの契約コードのみを残し、ロット単位でbulk insert            §2.4
ステップ7  契約終了の判定         → 3条件、PE/PGのグループごとに集約                             §2.5
ステップ8  顧客情報の更新         → ConCustomers をUPDATE（連携番号／計算停止フラグ）            §2.5
ステップ9  完了ログの書き込み     → ログのstatusを 1 (completed) に更新                          §2.6
ステップ10 API呼び出し（条件付き）→ 当日のIF2249（契約解約）も完了済みの場合のみ                 §2.6
```

| ステップ | 内容 | 詳細箇所 |
|---|---|---|
| 1–3 | 当日のCSVファイルを特定し、ログテーブルにより重複処理を防止する | §2.1 · §2.2 |
| 4 | ファイルを取得し、「処理中」のログを書き込む | §2.3 |
| 5–6 | 全件削除＋7つの契約コードに基づくマスタの再登録 | §2.4 |
| 7–8 | 契約終了の判定、顧客の連携情報の更新 | §2.5 |
| 9–10 | 「完了」のログ書き込み、API呼び出し ― IF2249との双方向の条件 | §2.6 |
| — | CSVの構造 → `ipf_ems_pls_cntr_payers` テーブル | §2.7 |

---

### 2.1 処理対象CSVファイルの特定

| 項目 | 内容 |
|---|---|
| ファイル一覧の取得元 | 中継サーバー上のディレクトリ。パスは環境変数 `XZILLA_RELATION_SERVER_MASTER_URL` から取得する ([:74](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvEmsPlsCntrPayerCommand.php#L74)) |
| ファイルの絞り込み条件 | ファイル名に `.csv` という文字列を**含む**ファイルのみを受け付ける（`str_contains` ― 拡張子を厳密にチェックしていない） ([:85](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvEmsPlsCntrPayerCommand.php#L85)) |
| timestampのキー | ファイル名の末尾14文字（`.csv` を除く）― 形式は `yyyyMMddHHmmss` ([:87-91](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvEmsPlsCntrPayerCommand.php#L87-L91)) |
| ファイルの選択方法 | timestampを降順にsortし（`krsort`）、`[当日 00:00:00, 当日 23:59:59]` の範囲に入る**最初**のファイルを取得する ([:95-109](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvEmsPlsCntrPayerCommand.php#L95-L109)) |
| ファイルが存在しない場合 | ディレクトリにファイルが1つもない、または当日のファイルが1つもない場合 → ログを出力してから `commit` ＋ `abort`（取り消すべきものがまだ存在しないため、rollbackはしない） ([:76-81](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvEmsPlsCntrPayerCommand.php#L76-L81), [:111-115](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvEmsPlsCntrPayerCommand.php#L111-L115)) |

ファイル一覧はSFTP経由で取得する（`XzillaRelationComponent::getCsvFileLists()` → `SFTP::nlist()`、秘密鍵でログインする ― 環境変数 `XZILLA_RELATION_SERVER_HOST`/`PORT`/`USER`/`SECRETKEY_PATH`）([XzillaRelationComponent.php:39-57](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Controller/Component/XzillaRelationComponent.php#L39-L57), [:64-77](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Controller/Component/XzillaRelationComponent.php#L64-L77))。

### 2.2 ログテーブルによる重複処理の防止

ファイルを取得する前に、バッチは `XzillaRelationLogs` テーブルを `(upload_type = 2, file_name = <選択したファイル>)` で照会する ([:117-131](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvEmsPlsCntrPayerCommand.php#L117-L131))：

| status | 意味 | 挙動 |
|---|---|---|
| `0` | 処理中（*推定* ― 本コマンド内に専用の定数名はなく、コメント「ステータスが処理中」と値 `0`/`1` の対照から推定した；定数 `XZILLA_RELATION_LOGS_STAUS_PROCESSING=0` は `XzillaRelationComponent` に定義がある ([:29](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Controller/Component/XzillaRelationComponent.php#L29))） | バッチを停止（`commit` ＋ `abort`） |
| `1` | 完了済み（定数 `XZILLA_RELATION_LOGS_STAUS_COMPLETED`） | バッチを停止（`commit` ＋ `abort`） |
| レコードなし、または `0`/`1` 以外のレコード | 未処理 | 続行 ([:132-140](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvEmsPlsCntrPayerCommand.php#L132-L140)) |

`upload_type` は、本バッチに関係するXzillaの2種類のファイルを区別する ([:34-36](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvEmsPlsCntrPayerCommand.php#L34-L36))：

| 定数 | 値 | 意味 |
|---|---:|---|
| `XZILLA_RELATION_LOGS_UPLOAD_TYPE_MASTER` | `2` | 場所契約支払者マスタファイル（IF2264）― 本バッチが処理するファイルそのもの |
| `XZILLA_RELATION_LOGS_UPLOAD_TYPE_CANCELLAION` | `3` | 電力契約解約ファイル（IF2249）― §2.6で使用する。本バッチが処理するファイルではない |

### 2.3 ファイルの取得と「処理中」ログの書き込み

- CSVを `DOWNLOAD_TO_LOCAL_DIRECTORY` = `/var/data/xzilla/IF2264/` へSFTPでダウンロードし、ディレクトリが存在しない場合は作成する（`mkdir(..., 0777)`）([:30](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvEmsPlsCntrPayerCommand.php#L30), [:144-154](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvEmsPlsCntrPayerCommand.php#L144-L154), [XzillaRelationComponent.php:87-109](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Controller/Component/XzillaRelationComponent.php#L87-L109))。
- `upload_type=2, file_name=<file>` のログを「処理中」の状態で書き込み（insert/update）、完了ステップで再利用するために `xzillaRalationLogsInsertId` を取得する ([:156-165](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvEmsPlsCntrPayerCommand.php#L156-L165), [XzillaRelationComponent.php:117-155](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Controller/Component/XzillaRelationComponent.php#L117-L155))。
- ファイル取得のエラー → `commit` ＋ `abort`（ファイルが存在しない場合と同様 ― DBにはまだ何も書き込んでいない）([:152-153](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvEmsPlsCntrPayerCommand.php#L152-L153))。
- 「処理中」ログの書き込みのエラー → トランザクション全体を `rollback` する ([:161-164](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvEmsPlsCntrPayerCommand.php#L161-L164))。

> ⚠️ **`saveXzillaRelationLogs()` の内部では、「ログが既に存在するか」を確認するクエリに `upload_type = 1` がハードコードされている** ([XzillaRelationComponent.php:124-127](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Controller/Component/XzillaRelationComponent.php#L124-L127))。一方、実際のレコードは引数として渡された `upload_type` の値（ここでは `2`）で**insert**される ([:142](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Controller/Component/XzillaRelationComponent.php#L142))。本バッチ（`$uploadType = 2`）では、この確認クエリが正しい種別に一致することは決してない ― **ファイル名が同一**の `upload_type=1` のレコードが存在する場合（別のIF）、この関数は新規insertではなくそのレコードを誤って上書きする；ファイル名が一致しない場合、この関数は常にinsertの分岐に入る。本バッチの実際のフローでは、§2.2に独立した重複防止のステップがあるためリスクは低いが、これは旧システムのコードに元から存在するcopy‑pasteのミスである（本来はリテラルの `1` ではなく `$uploadType` を使うべきである）。

### 2.4 マスタの全件削除＋再登録（`bulkInsertMasterData`）

| 項目 | 内容 |
|---|---|
| 旧データの削除 | `deleteAll('1=1')` ― 登録の前に `ipf_ems_pls_cntr_payers` テーブルを**全件**削除する。キーによるupsertではない ([:167-177](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvEmsPlsCntrPayerCommand.php#L167-L177)) |
| 登録関数の位置 | [RcvEmsPlsCntrPayerCommand.php:245-363](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvEmsPlsCntrPayerCommand.php#L245-L363) |
| ヘッダーの除外 | 1行目（`$i == 0`）はskipされる ([:252-257](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvEmsPlsCntrPayerCommand.php#L252-L257)) |
| 絞り込み条件 | `cntr_clsfy_code`（22列目、index `21`）が `{PE624, PE625, PE650, PE651, PE652, PG077, PG079}` に含まれる行のみを残す ― それ以外の行は完全に無視され、insertされない ([:318-329](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvEmsPlsCntrPayerCommand.php#L318-L329)) |
| EMS‑SPの収集 | 残った各行の `ems_sp` を `$emsSpNos` に追加し、その後 `array_unique` で重複を除去する（CSVには同一のEMS‑SPの行が複数存在するため） ([:331-332](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvEmsPlsCntrPayerCommand.php#L331-L332), [:355-356](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvEmsPlsCntrPayerCommand.php#L355-L356)) |
| insertの方法 | ロット単位のbulk insert。`$splitCount == 10` になるまで1つのquery objectを使い回し、そこで初めて `execute()` する ([:334-353](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvEmsPlsCntrPayerCommand.php#L334-L353)) |

> ⚠️ **コメントには「10件ずつBULK INSERT」と書かれているが、1ロットは実際には11レコードである。** `$query->values($values)` が `$splitCount == 10` のチェック**より前**に実行されるため、カウンタが `10` に到達した時点でqueryにはすでに11行（`0` から数えるため）が蓄積されており、その後に `execute()` される ([:339-348](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvEmsPlsCntrPayerCommand.php#L339-L348)) ― コメントとは1件ずれているが、結果に影響はない（データは漏れなくinsertされる）。ただしバッチサイズのロジックを読み直す際には知っておく必要がある。

### 2.5 契約終了の判定と顧客情報の更新（`updateCustomerData`）

コード内に記載されたspecの原文 ([:373-385](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvEmsPlsCntrPayerCommand.php#L373-L385)) ― 契約終了を判定する3つの条件：

| # | 条件 | 判定範囲 |
|---|---|---|
| ① | サービスポイント＿適用終了年月日 (`reg_end_ymd_sp`) が **`99991231` ではない** | 同じ接頭辞（`PE...` または `PG...`）の契約グループ内での**最大**値 |
| ② | 契約終了年月日 (`cntr_end_ymd`) が **`99991231` ではない** | 同一グループ内での**最大**値 |
| ③ | 電力契約（`PE624`/`PE625`）でありながら、供給地点特定番号 (`supply_point_num`) または IPF使用契約番号 (`ipf_use_cntr_num`) が**欠落**している | `PE624`/`PE625` の契約が存在する場合のみ |

**①、②または③**のいずれかがいずれかのグループで成立する場合 → **契約終了**とみなす。

#### EMS‑SPごとの処理

```
emsSpNos 内の各 ems_sp について：
  1. この ems_sp の ipf_ems_pls_cntr_payers のレコードをすべて取得し、
     cntr_clsfy_code, reg_end_ymd_sp, cntr_end_ymd の順でsortする（asc）  [:389-398]
  2. レコードがない場合 → この ems_sp をスキップする                     [:400-403]
  3. グループ（cntr_clsfy_code の先頭2文字 = "PE" または "PG"）ごとに集約：
     - グループ内で最大の reg_end_ymd_sp
     - グループ内で最大の cntr_end_ymd
     - customerNo   ← PG のレコードの links_cus_num（最大値を追跡）
     - supplyPointNo, ipfContractNo ← PE624/PE625 のレコードの
       supply_point_num / ipf_use_cntr_num（最大値を追跡）
     - receivePointNo ← PE650/651/652 のレコードの supply_point_num
       （最大値を追跡。このレコードが存在しない場合もある）               [:405-556]
  4. 上記の3条件 ①②③ を判定する
     成立   → supplyPointNo/ipfContractNo/receivePointNo = NULL、
              customerNo はそのまま保持、sellBuyCalcStopFlag = 1（計算停止）
     不成立 → 4つの連携番号をすべて更新、sellBuyCalcStopFlag = 0（計算実行） [:558-619]
  5. UPDATE ConCustomers WHERE c001 = ems_sp AND c066 = 0
```

> グループごとの集約の処理（ステップ3）は、コード上では `reg_end_ymd_sp` と `cntr_end_ymd` に対するほぼ重複した2つの `if/else if/else` の塊になっており、各塊の先頭の分岐の条件は、グループ／フィールドごとに個別に確認するのではなく `empty($arrayPerContracts)`（配列全体）を確認している ([:422-488](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvEmsPlsCntrPayerCommand.php#L422-L488), [:490-555](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvEmsPlsCntrPayerCommand.php#L490-L555)) ― ループ内の位置によって通る分岐は異なるが、手作業で対照した限り、最終的な結果は関数の冒頭のspecに記載されたとおり「各グループの最大値」が正しく得られる。結果の齟齬は検出されなかった。ループの書き方が煩雑で冗長であるというだけである。

#### `ConCustomers` の更新（`execCustomerUpdateForTerminate` / `execCustomerUpdateForDuaring`）

モデル `ConCustomers` は物理テーブル `t_101` を指しており（`setTable('t_101')` ― [ConCustomersTable.php:41](e:/Projects/mui/legacy_eminel_docs-main/sources/eminel_sv_lib-develop/src/Model/Table/ConCustomersTable.php#L41)）、以下の `c0xx` の各カラムは `t_101` の物理カラムである。

| `ConCustomers` のカラム | 意味（entityによる） | **終了**の場合 | **有効**の場合 |
|---|---|---|---|
| `c061` (`C_PROVIDE_POINT_NUMBER`) | 供給地点特定番号 | `NULL` | `supplyPointNo` |
| `c063` (`C_SELL_BUY_SOURCE_NUMBER`) | IPF使用契約番号 (`ipfContractNo`) を保持する | `NULL` | `ipfContractNo` |
| `c064` (`C_PROVIDE_ELE_POINT_NUMBER`) | 受電地点特定番号 (`receivePointNo`) を保持する | `NULL` | `receivePointNo` |
| `c062` (`C_CUSTOMER_NUMBER`) | お客様番号 | **変更なし**（`execCustomerUpdateForTerminate` には含まれない） | `customerNo` |
| `c065` (`C_SELL_BUY_CALC_STOP_FLAG`) | 売買電の計算停止フラグ（0=無効, 1=有効） | `1` | `0` |
| `c054` (`C_MODIFIED`) | 更新日時 | `now()` | `now()` |

([execCustomerUpdateForTerminate: :628-658](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvEmsPlsCntrPayerCommand.php#L628-L658), [execCustomerUpdateForDuaring: :660-690](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvEmsPlsCntrPayerCommand.php#L660-L690))

2つの関数はいずれも `WHERE c001 = <ems_sp> AND c066 = 0` である ― `c066`（`C_UPDATE_DETER_FLAG`）が `0` の顧客のみを更新する。`c066` の具体的な意味は本ファイル内では確認できていない（*推定* ― 定数名と、entity `ConCustomer` 内のラベル `0=無効／1=有効` から、「自動更新がブロックされている」ことを示すフラグである可能性がある）。

`updateCustomerData` 内のいずれかの更新ステップでエラーが発生した場合 → `false` を返す → コマンドはトランザクション全体を `rollback` する ([:191-194](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvEmsPlsCntrPayerCommand.php#L191-L194))。

### 2.6 完了ログの書き込みとAPI呼び出し ― IF2249との双方向の条件

§2.3で保持した `xzillaRalationLogsInsertId` を再利用し、そのログレコードのstatusを完了へ更新する ([:196-202](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvEmsPlsCntrPayerCommand.php#L196-L202), [XzillaRelationComponent.php:162-175](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Controller/Component/XzillaRelationComponent.php#L162-L175))。

その後、バッチは別の条件で `XzillaRelationLogs` をさらに照会する ([:204-220](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvEmsPlsCntrPayerCommand.php#L204-L220))：

| ログ照会の条件 | 値 |
|---|---|
| `upload_type` | `3`（`XZILLA_RELATION_LOGS_UPLOAD_TYPE_CANCELLAION` ― 電力契約解約ファイル、IF2249） |
| `created` | 当日 `00:00:00` 以降 |
| `modified` | 当日 `23:59:59` 以前 |
| `status` | `1`（完了） |

上記4つの条件をすべて満たすレコードが存在する場合に**のみ**、`execCustomersUpdCompleteApi()` ― 顧客情報登録完了通知API ― を呼び出す ([:222-231](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvEmsPlsCntrPayerCommand.php#L222-L231), [XzillaRelationComponent.php:182-220](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Controller/Component/XzillaRelationComponent.php#L182-L220))。条件を満たすレコードがない場合 → バッチは正常に終了し、APIは呼び出さない ― エラーではない。API呼び出しのエラー → 全体を `rollback` する。

これは `RcvCntctCancellationCommand`（IF2249）との**双方向**の条件である：当該バッチも、自身のAPIを呼び出す前に逆に `upload_type=2` のログ（本バッチ）を照会する。そのため、当日実行される2つのバッチのうち、**後に完了した側**が実際に通知APIを呼び出す側となる ― どちらのバッチが常に呼び出すかは固定されていない。

10ステップ全体は、`execute()` 関数の冒頭で開始される1つのトランザクション内にある ([:65-67](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvEmsPlsCntrPayerCommand.php#L65-L67)、最後のcommitは [:233-234](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvEmsPlsCntrPayerCommand.php#L233-L234))。

### 2.7 CSVカラム → `ipf_ems_pls_cntr_payers` テーブルのマッピング

CSVの全24カラム（0始まりのindex）が1:1でマッピングされ、除外されるカラムはない ([:258-283](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvEmsPlsCntrPayerCommand.php#L258-L283))：

| カラム | フィールド | | カラム | フィールド |
|---|---|---|---|---|
| `0` | `ems_sp` | | `12` | `source_pay_cntr_num` |
| `1` | `ipf_use_place_num` | | `13` | `reg_start_ymd_pay` |
| `2` | `source_use_place_num` | | `14` | `reg_end_ymd_pay` |
| `3` | `ipf_sp_num` | | `15` | `payer_cus_meigi_num` |
| `4` | `source_sp_num` | | `16` | `source_cus_meigi_num` |
| `5` | `reg_start_ymd_sp` | | `17` | `links_cus_num` |
| `6` | `reg_end_ymd_sp` | | `18` | `oc_z_cus_identity_no` |
| `7` | `ipf_use_cntr_num` | | `19` | `supply_point_num` |
| `8` | `source_use_cntr_num` | | `20` | `sp_divcod` |
| `9` | `reg_start_ymd_use` | | `21` | `cntr_clsfy_code` |
| `10` | `reg_end_ymd_use` | | `22` | `cntr_start_ymd` |
| `11` | `ipf_pay_cntr_num` | | `23` | `cntr_end_ymd` |

`cntr_clsfy_code`（カラム `21`）が§2.4に挙げた7つの値のいずれかである行のみがinsertされる。それ以外の行は登録のステップの時点で完全に除外され、バッチの実行後の `ipf_ems_pls_cntr_payers` テーブルには存在しない。

---

## 出典

| 内容 | 根拠 |
|---|---|
| バッチのメインロジック | `sources/conciergesv-develop/src/Command/RcvEmsPlsCntrPayerCommand.php` |
| 共通関数（SFTP、ログ、API） | `sources/conciergesv-develop/src/Controller/Component/XzillaRelationComponent.php` |
| `ipf_ems_pls_cntr_payers` テーブルの構造 | `sources/eminel_sv_lib-develop/src/Model/Table/IpfEmsPlsCntrPayersTable.php` |
| `xzilla_relation_logs` テーブルの構造 | `sources/eminel_sv_lib-develop/src/Model/Table/XzillaRelationLogsTable.php` |
| `ConCustomers` のentity＋カラム名／定数 | `sources/eminel_sv_lib-develop/src/Model/Entity/ConCustomer.php` |
| 関連バッチ（双方向のAPI呼び出し条件） | `investigate/eminel-gw/legacy-batch_RcvCntctCancellation.md` |
