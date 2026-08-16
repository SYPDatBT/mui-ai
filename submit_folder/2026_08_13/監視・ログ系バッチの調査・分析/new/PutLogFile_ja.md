# PutLogFileCommand（ログファイル出力）

## 概要

`PutLogFileCommand` は、`conciergesv` サーバー上で1日1回（00:00）実行されるcronバッチであり、「アプリログ送信機能(to Xzilla)」に属する ―― モバイルアプリのログ `.zip` ファイル（アプリがAPI `GetLogFileController` 経由でアップロードし、`APP_LOG_SAVE_DIR_PATH/xzilla/` ディレクトリへあらかじめコピーされたもの）のうち処理対象日に名前が一致するものを集め、解凍し、その中の各 `.tsv` ファイルのフォーマットを検証し（1行目はヘッダー、以降の行は日付 `YYYY/MM/DD` で始まらなければならない）、妥当な `.tsv` ファイルをXzilla連携システムに属する外部サーバーへSFTP PUTし、その後ローカルの一時ファイル／フォルダを削除する。新リポジトリ `syp-eminelstandard-backend` では、同等のLambdaや仕組みは見つからなかった：`XZILLA_RELATION_SERVER_HOST`／`PUT_LOG_TARGET_DIR_PATH` に関連する環境変数・secret・コードは一切存在せず、最も近いSFTPバッチ（`batch-export-kyutoki-*`, `batch-export-sekigaisen-rimokon`, `batch-forward-csv-from-sftp-server-to-s3`）もいずれも本質が異なる ―― これらはDBから新たにデータをgenerateするか、逆方向（基幹（xzilla/DWH）からS3へファイルを受け取る）であり、既存のアプリログzipファイルを読み直して解凍／検証しXzillaへ送信するものではない。「アプリログをXzillaへ送信する」機能は、新システムへまだ移植されていないと見られる。

---

# 第A部 ― 旧システム

## A.1 全体概要

| 項目 | 内容 |
|---|---|
| **バッチ名** | クラス／コマンド：`PutLogFileCommand` ・サーバー：`conciergesv` ・cronスクリプト：`31_PutLogFile.sh` ・cron上の日本語名：「アプリログ送信機能(to Xzilla)」。CLIのコマンド名は `Application.php` 内で明示的にoverrideされていない（独自名の登録は見つからなかった）―― CakePHPの規約に従い、コマンド名はクラス名から自動生成される（`Command` の接尾辞を除き、snake_caseへ変換）。 |
| **役割** | モバイルアプリの動作ログ（アプリが専用のAPI経由でサーバーへアップロードしたもの）を、日次のスケジュールでSFTPにより外部連携システム「Xzilla」へ送出する。 |
| **入力** | ローカルディレクトリ `env('APP_LOG_SAVE_DIR_PATH') . 'xzilla' . DS` に既に存在する `.zip` ファイルを読み取り、ファイル名の日付部分に基づいてfilter対象日（既定は昨日）で絞り込む。DBの読み取りは行わない。 |
| **出力** | （zipから解凍し、検証済みの）`.tsv` ファイルを、外部サーバー上の `env('PUT_LOG_TARGET_DIR_PATH')` へSFTP PUTする。DBへの書き込みは行わない。1つのzipのアップロードが完了した後：一時的な解凍フォルダを削除＋ローカルの元zipファイルを削除する。 |
| **処理概要** | 1. filter対象日（パラメータ `--datetime` または昨日）を決定する。 2. `xzilla` ディレクトリ内のローカルの `.zip` ファイルを一覧化する；ファイルが1つもない→alert＋早期終了。 3. private keyでSFTPへ接続する（ファイルがある場合のみ）。 4. filter対象日に一致する各zipについて（ファイル名からparseする）：システムの一時ディレクトリへ解凍する。 5. その中の各 `.tsv` について：フォーマットを検証し、妥当であればSFTP PUTする。 6. 1つのzipの処理が終わった後、一時ディレクトリを削除＋ローカルのzipを削除する。 |

## A.2 詳細

### A.2.1 実行スケジュールとパラメータ

| 項目 | 内容 | 出典 |
|---|---|---|
| 実行スケジュール（cron） | `00 00 * * *` ― 1日1回、00:00に実行、コメントは「#31.アプリログ送信機能(to Xzilla)」 | `docs/02_詳細設計/10_バッチ処理/mng-webap_cron設定_20241029.txt:119-120` |
| コマンドラインパラメータ | `--datetime`（既定は `'now'`）― 昨日ではなく、処理対象とするfilter対象日を指定できる | `sources/conciergesv-develop/src/Command/PutLogFileCommand.php:20-25` |
| 算出の基準時刻 | `--datetime` が渡されない、または `'now'` の場合→昨日を取る（`FrozenTime::now()->subDays(1)`）；そうでなければ渡された文字列をparseする。基準時刻は `Ymd` 形式にフォーマットされ、ファイル名照合用のfilterとして使われる | `PutLogFileCommand.php:30-39` |

### A.2.2 データソース ― アプリログのzipファイル、生成するのは別のAPI（本バッチではない）

本バッチはzipファイルを**自ら作成することはなく**、既に存在するファイルを読み取るのみである。実際のデータ生成の流れ：

1. モバイルアプリがAPI `GetLogFileController::index()`（route「ログ送信API」）を呼び出し、リクエストに `send_time`, `id`（EMS-SP）, `uuid` を添えてログファイル（`.zip`）をアップロードする。
2. Controllerはファイルを同時に2か所へ保存する：
   - 月ごとのディレクトリ：`env('APP_LOG_SAVE_DIR_PATH') . {Ym} . DS`（`GetLogFileController.php:50,53`）
   - `xzilla` ディレクトリ：`env('APP_LOG_SAVE_DIR_PATH') . 'xzilla' . DS`（`GetLogFileController.php:56,81`）
   - ファイル名：`"{emsSp}_{sendTime:YmdHisv}_{uuid}.zip"`（`GetLogFileController.php:76`）
3. `PutLogFileCommand` はその後、この `xzilla` ディレクトリ内の `*.zip` すべてを `glob()` し（`PutLogFileCommand.php:50`）、ファイル名を `_` で分割して日付部分を取り出し（`substr($fileNameParts[1], 0, 8)`、すなわち `YmdHisv` の部分の先頭8文字）、filter対象日に一致するものを絞り込む（`PutLogFileCommand.php:66-75`）。

出典：`sources/conciergesv-develop/src/Controller/GetLogFileController.php:27-94`、`sources/conciergesv-develop/src/Command/PutLogFileCommand.php:49-75`。

`conciergesv-develop/src/Command/` 内の他のCommandや、`eminel_sv_lib-develop/src/` 内の共用serviceで、この `xzilla` ディレクトリへzipファイルを作成するものは存在しない ―― 2つのソースツリー全体に対して "xzilla" をgrep済みであり、そのディレクトリへ書き込んでいるのは `GetLogFileController`（API）のみである。

### A.2.3 検証とファイル送信 ― TSVフォーマットのチェック、XzillaへのSFTP PUT

1. filter対象日に一致する各zipファイルについて、`ZipArchive` を用いて `sys_get_temp_dir()/{拡張子なしファイル名}` へ解凍する（`PutLogFileCommand.php:78-86`）。zipのオープンに失敗した場合→`alert` ログ「ZIPファイル解凍失敗」を出力してそのファイルをスキップし、他のzipファイルの処理を続行する（`:83-85`）。
2. 解凍先ディレクトリ内の `*.tsv` すべてを取得する（`:88`）。
3. 各 `.tsv` ファイルについて、`validateTsvFile()` で検証する（`:94, 125-152`）：
   - 1行目を読み取ってスキップする（ヘッダーとみなし、チェックしない）（`:135`）。
   - 2行目以降、**すべての**行 ―― 空行も含む。空行をskipする分岐（`:139-141`）は実際には発動しないためである（`fgets` は `"\n"` を返し、`empty()` では空とみなされない）―― は正規表現 `^\d{4}\/\d{2}\/\d{2}` に一致しなければならない（`YYYY/MM/DD` 形式の日付で始まる）；いずれか1行でも一致しない場合→ファイル全体が不正とみなされ、直ちにチェックを打ち切る（`break`）；ファイルの途中に空行を含むTSVも不正とみなされる（`:137-147`）。
   - 不正なファイル→`notice` ログ「不正な TSV ファイル」を出力し、**そのファイルのみをskipする**（zip全体ではない）（`:95-96`）。
4. 妥当なファイル→`env('PUT_LOG_TARGET_DIR_PATH') . DS . {ファイル名}` へSFTP PUTする（`:100`）。
   - PUTに失敗した場合：`alert` ログ「ファイルアップロード失敗」を出力し、処理中のzipの一時解凍ディレクトリ全体を削除したうえで、**`continue 2`** ―― 現在のzipを完全に打ち切り（ローカルの元zipファイルは削除せず、そのzip内の残りの `.tsv` も処理しない）、次のzipへ移る（`:100-107`）。
5. zip内のすべての `.tsv` の処理が完了し（不正のためskipされたファイルがあっても）、PUTのエラーが1件もなかった場合：一時解凍ディレクトリを削除＋ローカルの元zipファイルを削除する（`:110-115`）。

**業務上の定数**：定数は存在しない（`Configure::read`／`self::CONST` を使用していない）；接続パラメータ／パスはすべて環境変数から直接取得している ―― `config/const.php` に関連する定義がないことを確認済みである（大文字小文字を区別しない "xzilla"／"log_file"／"log_save" のgrepで結果なし）。

環境ごとの `env()` 変数の値：

| 変数 | .env.dev | .env.local | .env.prod | .env.stage |
|---|---|---|---|---|
| `APP_LOG_SAVE_DIR_PATH` | `/var/data/AppOpeLog/`（47行目） | 46行目 | 47行目 | 47行目 |
| `PUT_LOG_TARGET_DIR_PATH` | `./EMN/`（46行目） | `/var/www/vhost/conciergesv/tmp/EMN/`（45行目） | `./EMN/`（46行目） | `./EMN/`（46行目） |
| `XZILLA_RELATION_SERVER_HOST` | `localhost`（51行目） | `localhost`（50行目） | `kglip111.kitagas-aws.local`（51行目） | `kglip015.kitagas-aws.local`（51行目） |
| `XZILLA_RELATION_SERVER_PORT` | `22`（52行目） | `22`（51行目） | `52996`（52行目） | `52996`（52行目） |
| `XZILLA_SEND_SFTP_USER` | `ec2-user`（60行目） | `vagrant`（59行目） | `sftpemn2`（60行目） | `sftpemn2`（60行目） |
| `XZILLA_SEND_SFTP_SECRET_KEY_PATH` | `/var/data/key/sftpemn2_id_rsa`（59行目） | 58行目 | 59行目 | 59行目 |

出典：`sources/conciergesv-develop/config/.env.dev`、`.env.local`（57行目のコメント「# Xzilla へデータ送信するための設定」を含む）、`.env.prod`、`.env.stage` ―― 行番号は各ファイルにおいて上表のとおりである。

### A.2.4 結果の書き込み ― 外部サーバーへのSFTP PUT＋ローカルファイルの削除、DBへの書き込みなし

- 送信先：`.tsv` ファイルは外部SFTPサーバー（`XZILLA_RELATION_SERVER_HOST`）上の `PUT_LOG_TARGET_DIR_PATH` ディレクトリへPUTされる。出力先のDBテーブルはない ―― 本バッチはDBと一切やり取りしない。
- DBのトランザクションは使用しない。安全性の単位は **zipファイル** ごとである：zip内の1ファイルのPUTが失敗した場合、そのzipの残り全体（未処理の他の `.tsv` を含む）が `continue 2` によってスキップされ、ローカルのzipファイルはそのまま残り（削除されず）、次回の再実行が可能となる；同一の実行内の他のzipは影響を受けない。
- 本バッチが他のバッチを起動することはなく、その結果を読み直すバッチも存在しない（ここがデータフローの終端であり、外部システムXzillaへ送出する）。
- エラーログの仕組み（`$this->log(..., 'alert')`）はシステム全体で共用されている：`alert` を呼び出したすべてのCommandは `LOGS` ディレクトリ内の `{Ymd}_alert.log` ファイルへ書き込まれ、`SendAlertLogMailCommand` が5分ごとにスキャン＋警告メールを送信する ―― これは `PutLogFileCommand` 固有の仕組みでは**なく**、このalert-mailの仕組みを共用する多数のCommandのうちの1つにすぎない（`sources/conciergesv-develop/src/Command/SendAlertLogMailCommand.php:33-35` が `{Ymd}_alert.log` を読み取る；5分ごとのスキャンスケジュールは `mng-webap_cron設定_20241029.txt:122-123` による）。

### A.2.5 特記事項／リスク

- 本バッチは、事前に**別のAPI**（`GetLogFileController`）が作成した入力ファイルを読み取るのみで、自らデータを生成することはない ―― 移植の際は、送信バッチが起動される前にファイル／データを「受け箱」へ書き込む同等の流れを確保する必要がある。そうでなければ常に「ファイルなし」の分岐に入ることになる（`PutLogFileCommand.php:52-55`、`alert` ログ「指定された日に該当するファイルがありません。」を出力してから早期に `return` する ―― abortではなく正常終了だが、`alert` レベルのログであるため `SendAlertLogMailCommand` 経由で警告メールが発火する（A.2.4）：アプリログが1件もない日にも警告メールが発生することになる）。
- ファイル名による絞り込み（`substr($fileNameParts[1], 0, 8)`）は、`GetLogFileController.php:76` が生成する固定のファイル名形式 `"{emsSp}_{YmdHisv}_{uuid}.zip"` に強く依存している ―― ファイル作成側でファイル名形式が変更され、こちら側が追随しなかった場合、日付による絞り込みはずれるか、1件も一致しなくなる。
- filter対象日に一致しないzipファイルは、その実行内では `continue` によって恒久的にスキップされるが、**削除はされない** ―― ディスク上に残り続け、自身のfilter対象日にあたる実行（または `--datetime` による手動実行）を待って初めて処理される；つまりcronが漏れなく継続して実行されることを保証する必要があり、1日でも実行が漏れた場合は `--datetime` パラメータによる手動の補完実行が必要となる。本バッチは1回の実行で複数日分を自ら「まとめて補う」ことはしないためである。
- 一時解凍ディレクトリには `sys_get_temp_dir()` を使用している（アプリケーション専用のディレクトリではない）―― （拡張子を除いて）同名のzipファイルが2つ同時に存在した場合（ファイル名に `uuid` が含まれるため本来起こらないはずである）、互いに上書きし合う可能性がある；ファイル名にUUIDが含まれるためリスクは低い。

---

# 第B部 ― EMINEL-smart（新システム）との対照

> 本質的に同等のLambda／仕組みは見つからなかった。以下の表は、`src/functions/` 内で調査した領域／候補と、一致しない理由である（B.1/B.2の代わり）。

## 確認済み

| 領域／候補 | 一致しない理由 |
|---|---|
| `src/functions/api-*`、`authorizer/app.ts`、`batch-if2241-import-tagtag-kaiin/app.ts`、`batch-update-selecting-place-no/app.ts`、`give-badge-after-xzilla-link.ts`、`models/Kaiin.ts` において `xzilla` というキーワードを含む約140行／45ファイルすべて | すべて `is_not_data_xzilla`／`checkIsNotDataXzilla` フラグを軸としたものである ―― 会員（kaiin）がXzilla経由でデータ連携しているか否かを判定し、アプリ側のauthorization／business logicに供するものである。`PutLogFileCommand` の「SFTPでXzillaへログを出力する」という本質とはまったく異なる。 |
| `src/functions/batch-export-kyutoki-accumulated`、`-daily-usage`、`-device-property`、`-device-status-history`、`-monthly-usage`、`batch-export-sekigaisen-rimokon` | 実際のSFTP PUTがある（`src/layers/common/nodejs/services/upload-data-backup-to-sftp.ts`、secret `sftp_server_info_eminel`、送信先 `/EST`）が、データは**DBから新たにgenerateされる**（機器をqueryしてCSVへconvertする）ものであり、既存のアプリログzipファイルを読み直すことはなく、ヘッダー＋日付に基づく解凍／TSV検証のステップもない。e-smartの実際の送信先はsecret内にあり、コードからは特定できない（Xzilla/DWHと同一のサーバーではないかと見ており、muiの確認待ちである）；本質の違いはデータにある：DBからgenerateする機器のCSV ≠ 既存のアプリログzipを読み直して解凍／検証／送信すること ―― 「外部へSFTP PUTする」という技術的な水準でのみ一致している。 |
| `src/functions/batch-forward-csv-from-sftp-server-to-s3`、`batch-get-list-file-name-from-sftp-server`、`batch-delete-data-temp-sftp` | **逆方向**である：基幹（xzilla/DWH）のSFTPサーバー**から** `.dat` ファイル（IF2241/DM1040/IF2242/IF2016/IF2023/IF2024/IF2029/IF2223）を読み取ってS3**へ**importするものであり、アプリログをXzilla**へ**送信するものではない ―― データの向きが異なる；プロジェクトのdocsによれば連携相手はまさにxzilla/DWHである（`eminel_gw_project/docs/eminel-smart/02_product_overview.md:30,64`）が、データの種類と向きがまったく異なるため、やはり `PutLogFileCommand` の移植版ではない。 |
| `src/` 全体に対する `XZILLA_RELATION_SERVER_HOST`、`PUT_LOG_TARGET_DIR_PATH`、`APP_LOG_SAVE_DIR_PATH` の直接のgrep | 結果0件 ―― `PutLogFileCommand` に固有の環境変数は新リポジトリに存在しない。 |

「アプリログをSFTPでXzillaへ送信する」機能が `syp-eminelstandard-backend` へ移植されたことを示す痕跡（コード、環境変数、`template.yaml` 内のリソース名）は一切ない。`GetLogFileController` に相当するAPI（アプリからzipログを受け取るもの）も `src/functions/api-*` 内には見つからなかった（本バッチの調査範囲には含まれないが、両側を移植する必要がある場合には入力データソースに直接関わる）。

---

## まとめ

該当なし ―― 旧システムには処理の流れが1つしかなく（分岐や並列のアルゴリズムはない）、新システムには対比すべきものが**何も見つからなかった**（「別の仕組みに置き換えられた」ケースではない）―― 第B部の「確認済み」の表に、各候補が一致しない理由を十分に示している。

---

## 出典

| 区分 | 内容 | 根拠 |
|---|---|---|
| 旧システム | メインロジック | `sources/conciergesv-develop/src/Command/PutLogFileCommand.php` |
| 旧システム | 入力ファイルの生成元（アプリからログを受け取るAPI） | `sources/conciergesv-develop/src/Controller/GetLogFileController.php` |
| 旧システム | 共用のalert-mailの仕組み（横断的） | `sources/conciergesv-develop/src/Command/SendAlertLogMailCommand.php:33-35` |
| 旧システム | 環境変数／環境ごとの値 | `sources/conciergesv-develop/config/.env.dev`, `.env.local`, `.env.prod`, `.env.stage` |
| 旧システム | `config/const.php`（grep済み ― 関連する定数なし） | `sources/conciergesv-develop/config/const.php` |
| 旧システム | 実行スケジュール（cron） | `docs/02_詳細設計/10_バッチ処理/mng-webap_cron設定_20241029.txt:119-123` |
| 旧システム | バッチ一覧（日本語の説明、サーバー区分） | `docs/03_API仕様/04_バッチ一覧.md:89` |
| 旧システム | 用語 Xzilla／To_Xzilla | `docs/用語集.md:19,84` |
| 旧システム | docs⇔sources のマッピング（本バッチ専用の行がないことを確認） | `README.md:113,157,161` |
| 旧システム | 関連資料、内容は未読（binary） | `docs/02_詳細設計/06_情報共通基盤連携/To_Xzilla/アプリログ送信/アプリログ送信バッチ仕様書.xlsx`, `アプリログ取得API仕様書.xlsx` |
| 新システム | `src/functions/` のgrep／調査の結果（同等のものは見つからなかった） | `src/functions/batch-export-kyutoki-*`, `batch-export-sekigaisen-rimokon`, `batch-forward-csv-from-sftp-server-to-s3`, `batch-get-list-file-name-from-sftp-server`, `batch-if2241-import-tagtag-kaiin`, `batch-update-selecting-place-no`, `authorizer/app.ts`, `give-badge-after-xzilla-link.ts`, `models/Kaiin.ts` |
| 新システム | 共用のSFTP service（本質が異なる） | `src/layers/common/nodejs/services/upload-data-backup-to-sftp.ts` |
