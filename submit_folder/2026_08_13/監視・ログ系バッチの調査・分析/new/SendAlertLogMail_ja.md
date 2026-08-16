# SendAlertLogMailCommand（アラートログメール送信）

## 概要

`SendAlertLogMailCommand` は、旧システム（`conciergesv`、`mng-webap` グループ）において5分ごとに実行されるバッチであり、同一リポジトリ内の他のバッチ／処理が失敗時に出力する `alert` レベルのログファイルを読み取り、直近5分以内の最新の行を最大10行まで抽出し、`mb_send_mail()` を通じて1通の警告メールを送信する。`syp-eminelstandard-backend`（EMINEL-smart）では、この機能は**すでに存在し、同等であり ― さらに広い範囲をカバーしている**が、まったく異なるアーキテクチャによる：ファイルをcronで走査して直接メールを送信する方式に代えて、**CloudWatch Logs Subscription Filter（event-driven）＋ SNS** を用いており、ほぼすべてのLambdaバッチ＋Step Functionsに適用され、旧システムにはないノイズ除去のステップとメール件名の分類が加わっている。

---

# 第A部 ― 旧システム

## A.1 全体概要

| 項目 | 内容 |
|---|---|
| **バッチ名** | クラス：`SendAlertLogMailCommand`・cronスクリプト：`32_SendAlertLogMail.sh`・cron上の日本語名：`32 アラートメール送信`。 |
| **役割** | 他のバッチ／処理が重大なエラー時に出力する `alert` レベルのログを集約し、運用者へメールを送信する ― `conciergesv` 全体を対象とする集中型の警告機構である。 |
| **入力** | `LOGS` 内のログファイル `{Ymd}_alert.log` を読み取る（0時直後に実行された場合は前日のファイルも読む）。DBは読まず、外部APIも呼び出さない。オプション `--datetime`（デフォルト `now`）がある。 |
| **出力** | env `ALERT_LOG_MAIL_TO` に設定されたアドレス宛に `mb_send_mail()` でメールを送信する。DBへの書き込み、ファイルへの書き込みは行わない。 |
| **処理概要** | 1. 処理の基準時点を確定する。<br>2. 読み取るべきログファイルを確定する（当日分、0時を過ぎた直後であれば前日分も追加）。<br>3. 2つのファイルがいずれも存在しない場合→終了。<br>4. 2つのファイルの内容を読み取り、連結する（存在する場合）。<br>5. タイムスタンプが `[基準時点 − 5分, 基準時点]` の範囲内にあり、かつ `'alert:'` を含む行を抽出する。末尾から遡って走査し、最大10行。<br>6. 該当する行がない場合→終了。<br>7. 見つかった行を含む1通のメールを、有効なすべてのアドレスへ送信する。 |

## A.2 詳細

### A.2.1 実行スケジュールとパラメータ

| 項目 | 内容 | 出典 |
|---|---|---|
| 実行スケジュール（cron） | `*/5 * * * *` ― 5分ごと | `docs/02_詳細設計/10_バッチ処理/mng-webap_cron設定_20241029.txt:122-123` |
| コマンドライン引数 | `--datetime`（任意、デフォルト `'now'`）― 「バッチ実行時点」の基準であり、テスト／再実行に用いる。 | `SendAlertLogMailCommand.php:26,31` |
| 深夜0時をまたぐ基準時点の処理 | `(基準時点 − 5分)` が基準時点と異なる日付になる場合→前日の `_alert.log` ファイルも、存在すれば読み取る。 | `SendAlertLogMailCommand.php:40-48` |

### A.2.2 データソース ― ログファイル `{Ymd}_alert.log`

- このファイルは **`SendAlertLogMailCommand` が出力するものではない** ― CakePHPのログエンジン `'alert'`（`levels => ['alert']`、`scopes => false`）が自動的に出力しており、設定は `config/app.php:427-434` にあらかじめ記載されている：アプリケーション全体における `alert` レベルのログ呼び出し（`Log::write('alert', ...)`／`$this->log($msg, 'alert')`）はすべて `FileLog` によって `LOGS` 内の `{現在日付Ymd}_alert.log` へ書き込まれる。
- **精度の更新**（前回の監査ではクォート付きの文字列 `'alert'` のみをgrepしており、PSR-3の定数 `LogLevel::ALERT` を経由する呼び出し方を見落としていた）：2つの呼び出し方（`'alert'` と `LogLevel::ALERT`）の両方を `conciergesv-develop/src` 全体に対してgrepすると **34ファイル**が該当し、以前記載していた8ファイルではない ― `Calc*Command` 群（10分／日／月／年）の大半、`Delete*Command`、`CreateCsvAndZip*Command`、`RcvCntctCancellationCommand`、`RankingCreationCommand`、`CreateGroupSummaryCommand`、`CreateTablePartitionCommand`、`WatchNotificationCommand`（`WatchNotification.md` 参照）、`PutLogFileCommand`、`CreateZipsTrait`、そして `SendAlertLogMailCommand` 自身が含まれる。すなわち `alert` の警告機構は **`conciergesv` の主要な業務バッチのほぼ全体**をカバーしており、当初の要件資料が記載しているような削除／CSV／Xzillaのグループに限られない ― 要件資料（下記の項）は古くなっているか、あるいは執筆時点の最小限の範囲のみを記載したものである可能性があり、実際のコードは他の多くのCommandへ拡張されている。
- 認識される行のフォーマット：行頭のタイムスタンプ `YYYY-MM-DD HH:MM:SS` ＋ `'alert:'` を含むこと。（`SendAlertLogMailCommand.php:81-87,162-168`）

**関連する業務要件資料**（`docs/02_詳細設計/09_アラート/アプリケーションベース/システムアラート/`；`斉藤メモ.txt` はShift-JIS／コードページ932であり、デコードしなければ読めない。`北ガスEMINELシステムアラートメールの要件概要.txt` はUTF-8であり、そのまま読める）：

- `北ガスEMINELシステムアラートメールの要件概要.txt` ― コードと完全に一致する：受信者はenvで設定し、複数アドレスに対応する；件名は `EMINELシステムアラート`；頻度は5分に1回；1通あたり最大10行。資料にはさらに「追加を検討中」の2項目（積算バッチの失敗、ユーザーデータ不足による重大なエラー）が明記されている。より網羅的にgrepし直した結果（34ファイル、上記参照）― 「積算バッチの失敗」の項目は**すでにコード化されている**：`Calc*Command` 群（10分／日／月／年）はいずれもエラー時に `alert` ログを呼び出している。「ユーザーデータ不足による重大なエラー」の項目は**依然として確認できていない** ― 34ファイルの一覧の中に、これを明確に示す名前のCommandは存在しない。
- `斉藤メモ.txt` ― アルゴリズムを詳細に記述している（1分ずつ最大5分まで遡って探索し、10行に達するか5分を使い切った時点で停止する）；現在のコードは同じ考え方を時間範囲の直接比較によって実装しており、より単純で結果は同等である。

### A.2.3 ログの抽出と制限のロジック（`sliceRecentAlertLogs`）

1. ファイル末尾の行から逆方向に走査する（新しいログが先）。
2. タイムスタンプがパースできない、または タイムスタンプが `[基準時点 − 5分, 基準時点]` の範囲外である行は除外する。
3. 残った行のうち、`'alert:'` を含む行のみを保持する。
4. 10行に達した時点で停止する（ハードリミットであり、コード内のリテラル）。（`SendAlertLogMailCommand.php:64,72-96`）
5. `config/const.php` の定数は一切使用しない ― すべてのパラメータはコード内のリテラルである。

### A.2.4 結果の書き込み ― `mb_send_mail()` によるメール送信

- 送信者：env `ALERT_LOG_MAIL_FROM`。受信者：env `ALERT_LOG_MAIL_TO`（`,` 区切り、各アドレスをバリデーションする；不正なものは除外したうえで `alert` ログを出力する；有効なアドレスが1つもなくなった場合→`RuntimeException`）。（`SendAlertLogMailCommand.php:98-133`）
- 件名は `"EMINELシステムアラート"` で固定；本文は `"アラート内訳:\n\n"` ＋ ログの各行。（`SendAlertLogMailCommand.php:69,144-146`）
- `mb_send_mail()`（PHPネイティブ、OSのsendmail／SMTP経由）― キューなし、リトライなし、トランザクションなし。1つのアドレスでエラーが発生した場合→`alert` ログを出力し、残りのアドレスへの送信を継続する。（`SendAlertLogMailCommand.php:151-155`）

### A.2.5 特記事項／リスク

- **1つのcross-cutting concern（`alert` レベルのロギング）における最後の環である** ― 多数の他のCommandにまたがっているため、機能を正しく移植するには、新システムにおいて `alert` ログが発生するすべての箇所を先に特定する必要があり、このファイルのみを個別に移植すればよいわけではない。
- バッチが遅延したり1回スキップされたりした場合（サーバーが5分を超えてダウン）→ その間のログは**メールで補って送信されることはない**。走査ウィンドウはちょうど5分だけ遡って見るものであり、「どこまで送信済みか」を追跡していないためである。
- メール送信に `mb_send_mail()` を用いており ― OS側で設定されたメールサーバーに依存し、外部のメールサービス（SES、SendGridなど）は使用しない ― serverlessへ移植する際にはやり方を根本的に変える必要がある点である。

---

# 第B部 ― EMINEL-smart（新システム）との対照

## B.1 バッチ名とコード上の位置

| 仕組み | 場所（Lambda） | State Machine／トリガー | データソース | 出力先 |
|---|---|---|---|---|
| ログエラーの集約と通知 | `src/functions/push-notification-error-log/app.ts` | **cronバッチではない** ― 監視用のLambdaであり、ほぼすべての `batch-*` Lambda＋`LogGroupStateMachine`（Step Functions）のロググループに付与された `AWS::Logs::SubscriptionFilter` によってトリガーされる | CloudWatch Logs（他のLambda／state machineのログイベント） | `AWS::SNS::Topic`（`SnsTopic`）への `PublishCommand` |

| 項目 | 内容 |
|---|---|
| トリガーの仕組み | `AWS::Logs::SubscriptionFilter` ― `FilterPattern` に一致する新しいログ行が発生した時点で、CloudWatchがLambdaを即座に呼び出す（event-drivenであり、cron／pollingではない）。例：`template.yaml:334-340`（state machine）、`template.yaml:1040-1046`（特定の1バッチ）。 |
| カバー範囲（推定ではなく実数） | `template.yaml` 内の `FilterPattern:` をgrep：**77リソース**が `FilterPattern: 'ERROR'` を使用（個々の `batch-*` Lambdaに付与）、**1リソース**が `FilterPattern: 'error'` を使用（`LogGroupStateMachine`、すべてのStep Functions executionの共通ロググループに付与）― 合計78個のsubscription filterであり、いずれも `DestinationArn` は同一の `PushNotificationErrorLogFunction` を指している。 |
| 多数のバッチで使用されるエラーログのhelper | `src/layers/common/nodejs/business-logic/log-error-batch.ts` ― `logErrorBatch()`。使用例は `batch-common-read-csv/app.ts:1,151`（`throw` の前に呼び出し、Lambdaランタイムがfilter patternに一致する "ERROR..." を自ら出力するようにする）。 |

## B.2 全体概要

| 項目 | 内容 |
|---|---|
| **役割** | CloudWatchからエラーログを受け取り（subscription filterが付与されたすべてのバッチ／state machine）、ノイズを除去し、分類したうえで、SNS経由で運用者へ通知を送信する。 |
| **入力** | CloudWatch Logsからのログイベントのpayload（gzip＋base64）。デコードすると `logGroup`、`logStream`、`logEvents[]` を含むJSONになる。 |
| **出力** | `AWS::SNS::Topic`（`SnsTopic`、`template.yaml:306-309`）への `PublishCommand` ― 実際のsubscriber（メールその他）は**この `template.yaml` 内に宣言が見当たらない**ため、IaCの外で管理されている可能性がある。*(推測であり、実際のsubscriberは確認できていない)* この仕組みはブランチ `feat/kitagas-batch-import-error-notification`（コミット `b087399c`〜`68d7a5fc`、2026-08-11〜14）で拡張されたところである：日次のデータ取込バッチ群のエラーは、専用のtopic `SnsTopicKitaGas` へも追加でpublishされる（調査時点で `gw-syp-dev` へ未マージ）。 |
| **処理概要** | 1. CloudWatchからログイベントを受け取り、デコードする。<br>2. `retryErrors`（一時的／ネットワーク由来の16種類のエラー ― `ResourceNotFoundException`、`RequestTimeout`、`SlowDown` など）および `ignoredErrors`（`'Global error listener:'`）に一致するログを除外する。<br>3. 残ったものを `logGroup` によってグループ分けする：`STATE_MACHINE_ERROR`（ロググループが `'LogGroupStateMachine'` を含む場合）／`DEVICE_ERROR_MASTER_NOT_FOUND`（messageに対応するmessage codeを含む場合）／`ERROR`（それ以外、デフォルト）。<br>4. 内容のある各グループについて、それぞれ1件のSNSメッセージをpublishする。件名はグループごとに異なる（`MAIL_SUBJECT_NOTIFICATION.*`、`constants.ts:215-219`：`ERROR`="【EMINEL-smart】バッチ停止エラーの通知"、`STATE_MACHINE_ERROR`="【EMINEL-smart】ステートマシン停止エラーの通知"、`DEVICE_ERROR_MASTER_NOT_FOUND`="【EMINEL-smart】機器エラーマスタ未存在通知"）。 |

**旧システムとの比較**：ノイズ除去のステップが追加されている（旧システムはエラーの種別を区別せず `alert:` の行をすべて送信していた）、3つの異なる件名による分類がある（旧システムは `EMINELシステムアラート` という固定の件名1つ）、カバー範囲はsubscription filterによって**個々のLambda単位**である（旧システムは自ら `alert` ログを出力する34個のCommandに限られ、警告の発生源を1つ追加するたびにコードの修正が必要だった ― 新システムはIaCに `SubscriptionFilter` を1つ追加するだけでよい）、1通あたりの行数に制限がない（旧システムは10行で固定）。

---

## まとめ

**同じ仕組みのまま直接移植したものではなく、「検知＋エラー通知」のやり方を、質的に異なるインフラの層へ全面的に置き換えたものであり、同時にカバー範囲も拡大している：**

- **エラー発生源の検知方法**：旧システムは**コード内での手動のopt-in**である ― 警告の対象としたいCommandは自ら `$this->log($msg, 'alert')` を呼び出す必要がある（34個のCommandがそうしている。grepによる実数、A.2.2参照）；呼び出しを忘れれば何も通知されない。新システムは**インフラによるopt-out**である ― すべての `batch-*` Lambda＋state machineには、同一の監視用Lambdaを指す `AWS::Logs::SubscriptionFilter` があらかじめ用意されており（78個のfilter、`template.yaml` 内の `FilterPattern:` のgrepによる実数、B.1参照）― Lambdaがpatternに一致する `"ERROR..."` を自ら出力しさえすれば捕捉され、「alertログ」という概念を知っている必要はまったくない。
- **検知の周期**：旧システムは5分ごとにファイルを走査するcronである（サーバーが5分を超えてダウンした場合に盲点となるウィンドウがある。A.2.5参照）；新システムは実際のログ行ごとのevent-drivenであり、「走査ウィンドウ」という概念がない。
- **通知前の処理**：旧システムはそのまま送信し、エラーの種別によるフィルタリングを行わない；新システムは通知の前に一時的／ネットワーク由来のエラー（`retryErrors`、16種類）を除外するステップがある ― ノイズを削減できるが、旧システムはログ行を集めるだけでエラー内容を解析しないため、これを行えなかった。
- **通知のルーティング**：旧システムはあらゆる種別のエラーに対して固定のメール件名1つ；新システムは3つのグループ（`ERROR`／`STATE_MACHINE_ERROR`／`DEVICE_ERROR_MASTER_NOT_FOUND`）に分け、グループごとに異なる件名を用いる。

**トレードオフ ― 得たもの、失ったもの、そして確認できていない部分：**

- 得たもの：カバー範囲がはるかに広い（34個のCommandに対して78個のLambda／state machine）、警告の発生源を1つ追加するのにアプリケーションのコードを修正する必要がない（IaCのリソースを1つ追加するだけでよい）、1通あたり10行というハードリミットがなくなった。
- 失った／変わったもの：通知の受信チャネルが、直接のメール（`.env` に明記された `ALERT_LOG_MAIL_TO`）からSNSへ変わった ― **`SnsTopic` の実際のsubscriberは、読んだ範囲の `template.yaml` 内に宣言が見当たらない** *(推測：IaCの外か、まだ読んでいない別のserviceで設定されている可能性があり、最終的に誰／どのチャネルが実際に通知を受け取るのかは確認できていない)*。受信者をコード内で明確に示していた旧システムとは異なる。
- 旧システムにおける「バッチが遅延するとログが失われる」という仕組み（サーバーが5分を超えてダウン→その区間は補って送信されない）は、周期的なファイル走査に依存しなくなったため、新システムでは**同じかたちでは当てはまらない** ― ただし、CloudWatch／Lambdaの層における同等のリスク（throttle、監視用Lambdaのinvokeの失敗）は、本監査の範囲では確認できていない。

---

## 出典

| 区分 | 内容 | 根拠 |
|---|---|---|
| 旧システム | メインロジック | `sources/conciergesv-develop/src/Command/SendAlertLogMailCommand.php` |
| 旧システム | ログエンジン `'alert'` の設定 | `sources/conciergesv-develop/config/app.php:427-434` |
| 旧システム | メールのfrom／toのenv | `sources/conciergesv-develop/config/.env.prod:73,76` |
| 旧システム | 実行スケジュール（cron） | `docs/02_詳細設計/10_バッチ処理/mng-webap_cron設定_20241029.txt:122-123` |
| 旧システム | 業務要件資料 | `docs/02_詳細設計/09_アラート/アプリケーションベース/システムアラート/北ガスEMINELシステムアラートメールの要件概要.txt`, `.../斉藤メモ.txt` |
| 新システム | 集約Lambdaのロジック | `src/functions/push-notification-error-log/app.ts` |
| 新システム | Subscription filter（例＋総数の集計） | `template.yaml:334-340`, `:1040-1046`, ファイル全体の `FilterPattern:` の集計 |
| 新システム | SNS Topic | `template.yaml:306-309` |
| 新システム | グループごとのメール件名 | `src/layers/common/nodejs/variables/constants.ts:215-219` |
| 新システム | バッチで使用されるエラーログのhelper | `src/layers/common/nodejs/business-logic/log-error-batch.ts` |
