# 旧バッチ ― RcvCntctCancellationCommand（Xzilla接点データ（電気解約）受信・買電売電計算停止フラグ設定）

## 概要

`RcvCntctCancellationCommand`（CLIコマンド `RcvCntctCancellation`、IF2249）は、旧システム（EMINEL コンシェルジュサーバー）において、中継サーバーXzillaから**電気解約のCSV**を受信し（1回の実行で当日のCSVファイルをちょうど1つ処理する）、電気契約種別 `PE624`/`PE625` に該当するレコードを抽出し、`ipf_cntct_cancellations` テーブルへupsertしたうえで、解約済みかつ処理期限に達した（`work_schedule_ymd <= 当日`）顧客に対して**買電売電計算停止フラグ**（`t_101.c065 = 1`）を設定するUPDATE文を1つ実行するバッチである。最後に、同じ日の支払者マスタファイル（IF2264）の受信も完了している場合には、顧客情報登録完了を通知するAPIを1つ追加で呼び出す。処理全体は1つのトランザクション内にある；詳細は第2部に示す。

## 第1部 ― 概要

| 項目 | 内容 |
|---|---|
| **役割** | Xzillaから電気解約のCSV（IF2249）を受信し、DBへ保存したうえで、解約済み顧客に買電売電計算停止フラグを設定する。 |
| **入力** | 中継サーバーXzilla上のCSVファイル（パスは環境変数 `XZILLA_RELATION_SERVER_CANCELLATION_URL` から取得）＋ `XzillaRelationLogs` テーブル（ファイル処理状態のログ。重複防止に用いる）＋ `ipf_cntct_cancellations` テーブル（以前に保存済みの解約レコード。update/insertの判別に用いる）。 |
| **出力** | `ipf_cntct_cancellations` テーブルへのupsert ＋ `t_101` テーブルのUPDATE（フラグ `c065`、時刻 `c054`）＋ `XzillaRelationLogs` へのログ書き込み ＋（条件付きで）顧客情報登録完了を通知するAPIの呼び出し。 |
| **処理概要** | 1. 中継サーバー上のファイル一覧を取得し、timestampが当日のCSVファイルを選択する。<br>2. ログを確認する ― ファイルが「処理中」または「完了済み」であれば停止する（重複防止）。<br>3. CSVファイルをlocalへ取得し、「処理中」のログを書き込む。<br>4. CSVを読み込み、契約種別 `PE624`/`PE625` のみを残すよう絞り込み、キー `ipf_use_cntr_num` でupsertする。<br>5. 解約期限に達した契約について、`t_101` の買電売電計算停止フラグをUPDATEする。<br>6. 「完了」のログを書き込む。当日のIF2264（支払者マスタ）も完了している場合は、通知APIを呼び出す。 |

## 第2部 ― 詳細

### 処理の全体図 ― 8ステップ、1トランザクション内

```
ステップ1  ファイル一覧の取得    → 中継ディレクトリを読み、.csvで絞り込み、timestamp降順にsort  §2.1
ステップ2  当日ファイルの選択    → timestamp ∈ 当日の [00:00:00, 23:59:59]                      §2.1
ステップ3  重複処理の防止        → (upload_type=3, file_name) でログ照会 ― status 0/1 → 停止    §2.2
ステップ4  ファイル取得＆ログ    → CSVをlocalへdownload、「処理中」ログをinsert/update          §2.3
ステップ5  絞り込み＆upsert      → PE624/PE625のみ残す、ipf_use_cntr_num でupsert               §2.4
ステップ6  計算停止フラグの設定  → 解約期限に達した契約に UPDATE t_101 SET c065=1               §2.5
ステップ7  完了ログの書き込み    → ログのstatusを 1 (completed) にupdate                        §2.6
ステップ8  API呼び出し（条件付） → 当日のIF2264 (payer) も完了している場合のみ                  §2.7
```

| ステップ | 内容 | 詳細箇所 |
|---|---|---|
| 1–2 | 中継サーバーのファイル一覧の取得、当日のCSVファイルの特定 | §2.1 |
| 3 | ログテーブルによる重複処理の防止 | §2.2 |
| 4 | ファイルの取得、「処理中」ログの書き込み | §2.3 |
| 5 | 契約種別による絞り込み、解約データのupsert | §2.4 |
| 6 | 買電売電計算停止フラグの設定 | §2.5 |
| 7 | 「完了」ログの書き込み | §2.6 |
| 8 | 通知APIの呼び出し ― IF2264に依存する条件付き | §2.7 |
| ― | `ipf_cntct_cancellations` へ書き出すデータ構造 | §2.4 |

---

### 2.1 処理対象のCSVファイルの特定

| 項目 | 内容 |
|---|---|
| ファイル一覧の取得元 | 中継サーバー上のディレクトリ。パスは環境変数 `XZILLA_RELATION_SERVER_CANCELLATION_URL` から取得する（[:72](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvCntctCancellationCommand.php#L72)） |
| ファイルの絞り込み条件 | ファイル名に `.csv` という文字列を含むもののみ受け付ける（`str_contains` ― 拡張子の厳密なチェックではない）（[:83](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvCntctCancellationCommand.php#L83)） |
| timestampのキー | ファイル名の末尾14文字（`.csv` を除く）― 形式は `yyyyMMddHHmmss`（[:85-89](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvCntctCancellationCommand.php#L85-L89)） |
| ファイルの選択方法 | timestampを降順にsortし（`krsort`）、`[当日 00:00:00, 当日 23:59:59]` の枠に入る**最初の**ファイルを取得する ― すなわち当日で最も新しいファイルである（[:92-107](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvCntctCancellationCommand.php#L92-L107)） |
| ファイルが存在しない場合 | ディレクトリにファイルが1つもない、または当日のファイルが1つもない場合 → ログを出力して `commit` ＋ `abort`（取り消すものがまだ何もないため、rollbackはしない）（[:74-79](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvCntctCancellationCommand.php#L74-L79)、[:109-113](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvCntctCancellationCommand.php#L109-L113)） |

本バッチは1回の実行で**ちょうど1ファイル**のみを処理する（当日で最も新しいファイル）― `CalcTenMinutesEnergyCommand` とは異なる（未処理の複数のウィンドウを補完する仕組みはない）。

### 2.2 ログテーブルによる重複処理の防止

ファイルを取得する前に、バッチは `XzillaRelationLogs` テーブルを `(upload_type = 3, file_name = <選択済みファイル>)` で照会する（[:118-124](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvCntctCancellationCommand.php#L118-L124)）：

| status | 意味 | 挙動 |
|---|---|---|
| `0` | 処理中（定数 `XZILLA_RELATION_LOGS_STAUS_PROCESSING = 0`。共用コンポーネント内で定義 ― [XzillaRelationComponent.php:28-29](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Controller/Component/XzillaRelationComponent.php#L28-L29)） | バッチを停止する（`commit` ＋ `abort`） |
| `1` | 完了済み（定数 `XZILLA_RELATION_LOGS_STAUS_COMPLETED`） | バッチを停止する（`commit` ＋ `abort`） |
| レコードが存在しない、またはレコードが `0`/`1` 以外 | 未処理 | 続行する |

ログテーブルの `upload_type` は、本バッチが対象とするXzillaのファイル2種類を区別する（[:33-36](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvCntctCancellationCommand.php#L33-L36)）：

| 定数 | 値 | 意味 |
|---|---:|---|
| `XZILLA_RELATION_LOGS_UPLOAD_TYPE_MASTER` | `2` | 地点ごとの契約支払者マスタファイル（IF2264）― §2.7で使用するものであり、本バッチが処理するファイルではない |
| `XZILLA_RELATION_LOGS_UPLOAD_TYPE_CANCELLAION` | `3` | 解約ファイル（IF2249）― まさに本バッチが処理するファイルである |

### 2.3 ファイルの取得と「処理中」ログの書き込み

- CSVを `DOWNLOAD_TO_LOCAL_DIRECTORY` ＝ `/var/data/xzilla/IF2249/` へ取得する（[:30](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvCntctCancellationCommand.php#L30)、[:146-153](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvCntctCancellationCommand.php#L146-L153)）。コード内のコメントに明記されている：確認のために古いCSVをそのまま残したい場合は、この取得のステップをcomment-outする必要がある（[:145](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvCntctCancellationCommand.php#L145)）― すなわちlocalのファイルは次回の実行で**上書きされる**。
- データをupsertする前に、`file_name=<ファイル>` のログを「処理中」の状態で書き込み、完了のステップで再利用するために `xzillaRalationLogsInsertId` を取得する（[:158-164](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvCntctCancellationCommand.php#L158-L164)）。留意点：`saveXzillaRelationLogs` のupdate分岐は、hardcodeにより `upload_type = 1` のレコードにしか一致しない（[XzillaRelationComponent.php:125](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Controller/Component/XzillaRelationComponent.php#L125) ― 旧システムのバグと思われる）；IF2249のファイルでは、実際には常に新規insertの分岐に入り、`upload_type=3` が書き込まれる。
- ファイル取得のステップでのエラー → `commit` ＋ `abort`、rollbackはしない（取り消すものがまだ何もない）（[:150-153](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvCntctCancellationCommand.php#L150-L153)）；「処理中」ログの書き込みでのエラー → トランザクション全体を `rollback` する（[:160-163](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvCntctCancellationCommand.php#L160-L163)）。

### 2.4 契約種別による絞り込みとupsert（`bulkInsertCancellationData`）

| 項目 | 内容 |
|---|---|
| 位置 | [RcvCntctCancellationCommand.php:229-298](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvCntctCancellationCommand.php#L229-L298) |
| ヘッダーの除外 | 先頭行（`$i == 0`）はskipされる（[:238-241](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvCntctCancellationCommand.php#L238-L241)） |
| 絞り込み条件 | 59列目（index `58`）が `'PE624'` または `'PE625'`（電気契約種別）である行のみ残す ― それ以外の行は読み飛ばされる（[:242-245](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvCntctCancellationCommand.php#L242-L245)） |
| update/insert判別のキー | 既存の `ipf_cntct_cancellations` テーブルと `ipf_use_cntr_num`（57列目、index `56`）で突き合わせる（[:247-249](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvCntctCancellationCommand.php#L247-L249)） |
| レコード照会でエラーの場合 | エラーログを出力して次のCSV行へ `continue` する ― バッチ全体をfailさせ**ない**（[:250-253](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvCntctCancellationCommand.php#L250-L253)） |
| save（updateまたはinsert）でエラーの場合 | 直ちに `false` を返す ― バッチ全体をfailさせ、rollbackに至る（[:268-273](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvCntctCancellationCommand.php#L268-L273)、[:288-294](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvCntctCancellationCommand.php#L288-L294)） |

CSVの列 → `ipf_cntct_cancellations` テーブルのフィールドの対応（使用されるのは7列。ファイルの総列数は不明 ― 突き合わせるためのインターフェース定義が存在しない）：

| CSVの列（index 0始まり） | フィールド | 備考 |
|---|---|---|
| `0` | `ipf_cntct_num` | |
| `27` | `work_schedule_ymd` | 解約実施の予定日 ― §2.5で `<= 当日` の比較に用いる |
| `36` | `work_progress_code` | 作業進捗コード ― §2.5で `'9'` を除外するために用いる |
| `53` | `create_datetime` | |
| `54` | `update_datetime` | |
| `56` | `ipf_use_cntr_num` | update/insert判別のキー；§2.5で `t_101.c063` へjoinするキーでもある |
| `58` | `cntr_clsfy_code` | 契約種別 ― `PE624`/`PE625` の絞り込み条件 |

### 2.5 買電売電計算停止フラグの設定（`updateCalculationStopFlag`）

`t_101` に対する単一のSQL UPDATE文であり、`ipf_use_cntr_num = c063` で `ipf_cntct_cancellations` とjoinする（[RcvCntctCancellationCommand.php:306-334](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvCntctCancellationCommand.php#L306-L334)）：

```sql
UPDATE t_101 SET c065 = 1, c054 = :update_time
   FROM ( SELECT cancel.ipf_use_cntr_num AS ipf_num, customer.c066
            FROM ipf_cntct_cancellations AS cancel
            INNER JOIN t_101 AS customer
                    ON cancel.ipf_use_cntr_num = customer.c063
           WHERE work_schedule_ymd <= :now
             AND work_progress_code NOT IN ('9')
             AND c066 = 0
        ) AS haishi
 WHERE c063 = haishi.ipf_num
```

| 同時に満たすべき条件 | 意味 |
|---|---|
| `work_schedule_ymd <= 当日` | 解約予定日に達している、または過ぎている |
| `work_progress_code NOT IN ('9')` | 進捗ステータスのコード `9` を除外する（*推定* ― コード `9` の具体的な意味は不明であり、コード内に注記がない） |
| `c066 = 0` | 更新が許可されている状態 ― `c066` は更新抑止フラグである（`C_UPDATE_DETER_FLAG`、[ConCustomer.php:81-82](e:/Projects/mui/legacy_eminel_docs-main/sources/eminel_sv_lib-develop/src/Model/Entity/ConCustomer.php#L81-L82)；同じ箇所で `c065` ＝ `C_SELL_BUY_CALC_STOP_FLAG` を確認）― 業務上の詳細な意味づけは依然として*推定*である |

結果：上記3条件を満たすすべての顧客に対して、`t_101.c065 = 1`（買電売電計算停止フラグ）と `t_101.c054`（更新時刻）が**1回のUPDATE**でセットされる（CSVの行ごとにループするわけではない）。

### 2.6 「完了」ログの書き込み

§2.3で保存した `xzillaRalationLogsInsertId` を再利用し、そのログレコードのstatusを完了（`XZILLA_RELATION_LOGS_STAUS_COMPLETED = 1`）へupdateする（[:185-188](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvCntctCancellationCommand.php#L185-L188)）。このステップでのエラー → 全体をrollbackする。

### 2.7 通知APIの呼び出し ― IF2264（payer master）に依存する条件

解約の処理を完了した後、バッチは別の条件で `XzillaRelationLogs` テーブルを続けて照会する（[:193-206](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvCntctCancellationCommand.php#L193-L206)）：

| ログ照会の条件 | 値 |
|---|---|
| `upload_type` | `2`（`XZILLA_RELATION_LOGS_UPLOAD_TYPE_MASTER` ― 支払者マスタファイル、IF2264） |
| `created` | 当日の `00:00:00`〜`23:59:59` の枠内 |
| `status` | `1`（完了） |

上記3条件をすべて満たすレコードが存在する場合に**限り**（すなわち：当日のIF2264を受信するバッチも実行を終えている場合）、`execCustomersUpdCompleteApi()` ― 顧客情報登録完了を通知するAPI ― を呼び出す（[:208-217](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvCntctCancellationCommand.php#L208-L217)）。条件を満たすレコードが存在しない場合、バッチはこのAPIを呼び出さ**ずに**正常終了する ― エラーではなく、単に条件がまだ揃っていないだけである。API呼び出しでのエラー → トランザクション全体をrollbackする（[:213-216](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvCntctCancellationCommand.php#L213-L216)）。

ここはバッチ#6（`RcvEmsPlsCntrPayerCommand`、IF2264）に直接依存する箇所である ― バッチ#5のこのステップが有効になるには、そのバッチが同じ日に**先に**実行され完了している必要がある。

### 2.8 トランザクション全体

8ステップ全体が、`execute()` 関数の冒頭で開始される1つのトランザクション内にある（[:64-65](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvCntctCancellationCommand.php#L64-L65)）：

| ケース | 挙動 |
|---|---|
| ファイルなし／当日のファイルなし／処理済みのファイル（§2.1、§2.2）・ファイル取得のエラー（§2.3）・IF2264のログ照会のエラー（§2.7） | `commit` してから `abort` ― rollbackはしない（§2.7のみ：upsert済みの部分はそのまま維持する） |
| 「処理中」ログの書き込み（§2.3）、upsert、フラグのupdate、完了ログの書き込み、API呼び出し（§2.4–§2.7）の各ステップでのエラー | 全体を `rollback` してから `abort` |
| 8ステップすべてが成功 | 最後に `commit`（[:220](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvCntctCancellationCommand.php#L220)） |

---

## 出典

| 内容 | 根拠 |
|---|---|
| 旧システムのロジック | `sources/conciergesv-develop/src/Command/RcvCntctCancellationCommand.php` |
| 定数（localのパス、ファイル種別、ログのstatus） | 本バッチの4つの定数はこのクラス内で直接定義されている（[:29-36](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvCntctCancellationCommand.php#L29-L36)）；API呼び出しのステップ（§2.7）で使用する `HTTP_STATUS_200` のみ、共用の定数ファイル [config/const.php:137](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/config/const.php#L137) から取得している |
