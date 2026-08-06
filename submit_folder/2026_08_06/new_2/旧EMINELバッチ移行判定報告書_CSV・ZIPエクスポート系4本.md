# 調査報告: CSV・ZIPエクスポート系グループ（4バッチ #8〜#11）— 新システムへ移植すべきか
| | |
|---|---|
| 対象 | 4バッチ `legacy_eminel_docs/sources/conciergesv-develop/src/Command/CreateCsvAndZipConDeviceStatuses / ConSensorHourlyValues / ConSensorDailyValues / ConSensorDailyAveValuesCommand`（#8〜#11）— `legacy_eminel_docs/docs/03_API仕様/04_バッチ一覧.md` の CSV・ZIPエクスポート系。`conciergesv` 上で稼働 |
| 調査範囲 | `legacy_eminel_docs`@`ccd8f56` ・ `eminel_gw_project`@`fbc0af0`（調査実施は `788b438`。本書引用資料は両コミットで同一 — §11）・ `syp-eminelstandard-backend`@`dc39aa39` ・ `syp-eminelstandard-web-admin`@`e550326`（branch `gw-syp-dev`・2026-08-06 の origin と一致） |
| 日付／作成者 | 調査 2026-08-04 ・ 作成 2026-08-06 ・ Bui Trong Dat（SYP）＋AI |
| 分冊／関連 | 全11本・3分冊の1冊（#1〜#11 は通し番号・日越共通）。他分冊: 配信・通知系（#1〜#4）・外部連携・受信系（#5〜#7）・越語版: `report_batch_nhom_csv_zip.md`（1-1 対応） |

**記号**:
| 記号 | 意味 |
|---|---|
| spec [I]／別表① | 管理画面データダウンロード仕様 `eminel_gw_project/docs/eminel/4_spec/admin/I_data_download.md`（DRAFT）／その別表① — ダウンロード種別一覧 |
| SVC-03 | 未決事項: 性能・可用性・運用・移行要件が未記載（`eminel_gw_project/docs/eminel/2_management/20_open_issues.md:86`。保持期間・バックアップは同:87） |
| F-ES-10 | 統合要件 v1.2 の「Xzilla連携」 |
| t_202/s_102/s_103/s_113 | 機器状態／時間値／日値／日平均値 ・ EMS-SP-NO = 設置地点番号（≈世帯） |
| 質問表／QAデータベース | 北ガス様向け質問一覧 `mui-ai/requirements/qa_kitagas.md`／mui との内部QA（Notion） |
| 確実／*推定*／※推定（未確認） | コードで確認済み／根拠ある推測／未検証の仮説 ・ コード内 `...` = 省略 |

目次: 結論 ・ I: §1 理由 ・ §2 新側の受け皿 ・ §3 要確認 ・ §4 誤解されやすい点 ・ §5 次アクション ・ II: §6 詳細 ・ §7 共通基盤 ・ §8 データ対照 ・ §9 案A/B ・ §10 QA ・ §11 根拠
## 結論
> **4バッチ（#8〜#11）はすべて廃止 — 「運用者がデータをファイルで取り出せること」は維持。**
> 実態は**削除前バックアップ**（CSV/ZIP へ退避してからパーティション削除）で、旧 DB の 8〜14日保持方針と一体。spec [I] は**保持期間 24ヶ月（T.B.D）・随時ダウンロード**を要求 — 旧前提は消滅。
> **代替**: 新 retention — DynamoDB TTL＋必要なら S3 退避、spec [I]＋SVC-03 確定待ち — に既存2出力経路（管理画面ダウンロード 17 エンドポイント／SFTP `/EST`）を組み合わせる。確定前の確認事項 **5点**（→ §3）。
# 第I部 — 報告編
## 1. なぜこの結論か
| 観点 | 旧システム | 新システム |
|---|---|---|
| 細粒度データの保持 | **8〜14日（テーブルによる）**（`t_202` 8日・`s_102` 14日 — `legacy_eminel_docs/sources/conciergesv-develop/src/Command/DeleteDataCommand.php:47-50`） | spec [I]: **24ヶ月（T.B.D）**・TTL が掃除 |
| 削除前の「救出」 | 4バッチが CSV → ZIP → サーバーディスク | 不要 — 保持期間中 DB にあり続ける。バックアップ = PITR |
| 運用者のファイル取得 | 事前作成 ZIP を旧管理画面（`eminelsv`）から DL | 要求時生成（17 EP＋presigned URL）。定期は SFTP パターン |

**6つの中核処理 → 新システムでも必要か？**
| # | 処理 | 要否 | 理由 |
|---|---|---|---|
| 1 | パーティションの CSV 出力（`t_202`/`s_102`/`s_103`/`s_113`） | ❌ | 保持期間中 DynamoDB にあり続ける |
| 2 | 週次／月次 ZIP の事前作成 | ❌ | オンデマンド生成（`BatchDownloadFunction` → JSZip → S3） |
| 3 | バックアップ後の削除（`DeleteData`） | ❌ | TTL が自動削除 |
| 4 | 安全弁 `set -eu`（CSV 失敗なら削除しない） | ❌（同等物あり） | 役割は PITR へ |
| 5 | 運用者がファイルで取り出せること | ✅ | 既存ダウンロード機構に E-GW 種別を追加するだけ |
| 6 | 定期的にファイルが置かれる運用（慣習） | ⚠️ 顧客次第 | [I] 未決 — 必要なら `/EST` パターン（§9-B） |
## 2. 新システムでの受け皿
| 旧の仕事 | 新側の場所 | 種別 |
|---|---|---|
| 管理者向け CSV/ZIP ダウンロード | `syp-eminelstandard-backend/src/functions/api-download/app.ts` → `syp-eminelstandard-backend/src/functions/batch-download/` → S3 `BUCKET_DOWNLOAD` → presigned URL。画面 `syp-eminelstandard-web-admin/pages/other/data-management/index.vue` | 既存 — 種別追加のみ（§6.5-3） |
| 保持期間の管理・期限削除 | `syp-eminelstandard-backend/template-dynamodb.yaml` の TTL（E-GW 計測テーブルは新設） | 要追記（§6.5-2） |
| バックアップ | PITR（有効化済み） | 既存 |
| 定期ファイル（希望時） | `syp-eminelstandard-backend/src/layers/common/nodejs/services/upload-data-backup-to-sftp.ts` パターン＋新規 `ScheduleV2` | 未作成 — 要否確定後のみ（§9-B） |

データの流れ — **旧**: cron 05:15 → **4** Command → パーティション `t_202`/`s_102`/`s_103`/`s_113`（PostgreSQL）→ CSV → ZIP → ディスク → DeleteData → DeleteLogicalDeletedDevices **↔ 新**: 管理者 → api-download（**17** エンドポイント）→ BatchDownloadFunction → ZIP → S3 BUCKET_DOWNLOAD → presigned URL **600秒**（＋`/EST` 分岐: **6** CSV・8:00）。保持 = TTL・バックアップ = PITR（図: §6.3/§6.5）。
- 思想: 旧 =「削除するためのバックアップ」（DB が窮屈）、新 =「DB に長く置き必要時に取り出す」。名前の罠: `legacy_eminel_docs/sources/conciergesv-develop/src/Command/CreateCsvAndZip…` は削除プロセスの前段（cron「#12.DBデータ削除」）でありエクスポート機能ではない。`CsvDownloadHistory` は**受信方向**（SFTP 取得の二重取込防止）で管理者 DL 履歴ではない（§11）。
## 3. 確定前に確認すべき点
| # | 論点 | 旧 | 新／計画 | 重要度 |
|---|---|---|---|---|
| 1 | 保持期間 | 8〜14日（＋月次2ヶ月） | spec [I] 24ヶ月も全行 T.B.D（`eminel_gw_project/docs/eminel/4_spec/admin/I_data_download.md:43-52`） | 🔴 |
| 2 | SVC-03 | — | 方針未定 → TTL 値・S3 退避を確定できない | 🔴 |
| 3 | 定期ファイル受領の慣習 | 週次／月次 ZIP 自動作成 | 基本オンデマンド。定期作成は [I] 未決 | 🟡 |
| 4 | SFTP `/EST` の宛先 | — | secret 管理・Xzilla/DWH か未確認（※推定（未確認）） | 🟡 |
| 5 | CSV 列形式 | 旧形式（列一覧は [I] 現行EMINEL節に抽出済み） | 互換維持を推奨（*推定* — 運用慣習） | 🟡 |

北ガス様向け（PM 経由）— **質問表への追加を提案**（内部論点 = spec [I]＋SVC-03。送付文面は内部 ID を含めない）:
> 「新システムにおける計測データ・各種履歴の**保持期間**について、管理画面のデータダウンロード仕様では**24ヶ月（未確定）**とされています。この値で確定してよいでしょうか。あわせて、保持期間・バックアップを含む**運用要件全般**の方針のご提示をお願いいたします。」
> 「現行システムでは週次／月次で ZIP ファイルが自動作成・保管される運用ですが、新システムでは**必要時に管理画面からダウンロードする方式**を基本と考えています。従来どおり**定期的にファイルが作成・保管される運用**の継続をご希望でしょうか（ご希望の場合は定期エクスポート機能を追加実装します）。」（前提: 新方式の説明／デモを先にご覧いただく）

mui 様向け（QAデータベース。外部連携・受信系分冊と共通設問・1回で足りる — 完全版は同分冊 §3。以下は短縮形）:
> 「SFTP `/EST` フォルダの宛先は Xzilla/DWH でしょうか（接続先が secret 管理のためコードから確認できず）。」
## 4. 説明時に誤解されやすい点
| 誤解 | 正しくは |
|---|---|
| 「4本は運用者向けダウンロード機能」 | 削除前バックアップ。ファイル取得は副産物（§6.1） |
| 「廃止するとデータを取り出せなくなる」 | ニーズは維持され既存オンデマンド DL＋任意の定期エクスポートへ（§9） |
| 「`CsvDownloadHistory` = 管理者 DL 履歴」 | 受信方向 — SFTP 取得の二重取込防止。ESTA 調査資料が誤解を招く（§11） |
| 「#10/#11 は前月パーティション」 | **前々月** — 毎月1日 05:15 の −32日 は必ず2ヶ月前の月。`DeleteData` の保持2ヶ月と一致（§6.3） |
## 5. 次のアクション
| # | 内容 | 担当 |
|---|---|---|
| 1 | spec [I]＋SVC-03 の確定を [I] レビュー時に提起。質問表への設問追加を提案（§3） | SYP（＋PM） |
| 2 | `/EST` 宛先を mui 様へ確認（§3。Xzilla 分冊と共通） | SYP |
| 3 | #1 確定後: retention 設計 — `syp-eminelstandard-backend/template-dynamodb.yaml` に TTL、S3 退避は集計系グループのデータ量見積りで判断 | SYP Dev |
| 4 | E-GW 種別へのダウンロード拡張（4レイヤー — §6.5-3） | SYP Dev |
| 5 | 顧客が定期ファイル希望なら `/EST` パターンでエクスポートバッチ（§9-B） | SYP Dev |
| 6 | Notion 分割時: 4本は「廃止、retention＋DL／エクスポートで代替」— 約46本の母数に算入しない | SYP＋PM |
| 7 | QA「旧Eminel基盤継承＋独立デプロイ」内の設問「既存システムを使い続けたほうがいい機能」への回答 — ① 旧EMINEL: 使い続ける価値のあるバッチなし ・ ② e-smart: 4候補（3分冊共通）— 本グループからは管理画面ダウンロード／エクスポート機構（§7.2/§7.3） | SYP（QAデータベースへ直接回答） |
> **方針（教訓）**: *ニーズを移植する。解決策を移植しない* — 消えた制約（DB が窮屈 → バックアップして削除）から生まれた機構は制約もろとも廃止。持ち込むのはニーズ（ファイルで取り出せること）と同等の安全弁（`set -eu` の代わりの PITR）。
# 第II部 — 技術詳細編
## 6. 4バッチの詳細（#8〜#11 一括 — 違いは対象テーブルと周期のみ）
**6.1 目的**: 細粒度データを**パーティション削除前に** CSV/ZIP へ退避 — DB は 8〜14日保持でも過去データを参照可能にする。ダウンロード機能ではない。

**6.2 判定**（方向性は確実・詳細は T.B.D 待ち）: **4本廃止 — ニーズ維持 — 新 retention＋既存2経路で代替。**
- 廃止: バックアップ後削除機構（4バッチ＋shell 2本＋`DeleteDataCommand`）。維持: ファイル取得ニーズ → spec [I] の管理画面 DL（列互換: §6.5-5）。代替: 保持 = TTL（＋S3 — §6.5-2）、取得 = 経路①オンデマンド（＋② 定期は顧客希望時 — §9）。理由: ① 保持前提が変われば機構ごと存在理由を失う。② [I] は 24ヶ月＋随時 DL（§6.4）。③ e-smart にバックアップ後削除はなく出力2経路が完備（§7.2/§7.3）。

**6.3 旧システムのフロー**（確実）:
| # | Class | テーブル | 対象パーティション | 周期／shell |
|---|---|---|---|---|
| 8 | `legacy_eminel_docs/sources/conciergesv-develop/src/Command/CreateCsvAndZipConDeviceStatusesCommand` | `t_202` | 8日経過（日） | 毎日 05:15（`day2to31.sh`）＋1日（`day1.sh`）。月曜に週次 ZIP |
| 9 | `legacy_eminel_docs/sources/conciergesv-develop/src/Command/CreateCsvAndZipConSensorHourlyValuesCommand` | `s_102` | 8日経過（日） | #8 と同じ |
| 10 | `legacy_eminel_docs/sources/conciergesv-develop/src/Command/CreateCsvAndZipConSensorDailyValuesCommand` | `s_103` | **前々月**（月・約2ヶ月経過） | 毎月1日 05:15（`day1.sh`）・即 ZIP |
| 11 | `legacy_eminel_docs/sources/conciergesv-develop/src/Command/CreateCsvAndZipConSensorDailyAveValuesCommand` | `s_113` | **前々月** — 全体1ファイル | 毎月1日 05:15（`day1.sh`）・即 ZIP |

`--datetime` default `'now'`（`legacy_eminel_docs/sources/conciergesv-develop/src/Command/CreateCsvAndZipConSensorDailyValuesCommand.php:28`）。CSV は EMS-SP-NO 単位（#11 のみ全体1本）。ZIP は `ZipArchive`・SJIS 名（`legacy_eminel_docs/sources/conciergesv-develop/src/Command/CreateZipsTrait.php:23-72`）。2 shell とも末尾で `DeleteData` → `DeleteLogicalDeletedDevices`（tgz 内実物で確認）。
```
cron 05:15（#12.DBデータ削除 — cron:39-41）: 毎日 day2to31.sh(#8/#9) ／ 1日 day1.sh(#8〜#11 全4本)
  ※ 毎月1日は両 shell が同時刻に起動（day2to31 の cron = 15 5 * * * で1日を除外していない）
  → CreateCsvAndZip*Command: パーティション読出し（t_202/s_102: 8日前 ・ s_103/s_113: 前々月 約2ヶ月）
  → CSV 生成（EMS-SP-NO 単位。#11 は全体1本）→ ディスク（CON_DEVICE_CSV_FILES_PATH — …DeviceStatusesCommand.php:58）
  → ZIP 圧縮（#8/#9 の週次 ZIP は月曜のみ — isMonday :182）
  → DeleteData: 保持超過分を DROP（#8/#9: 9/15日経過 = keepDays+1 — :85、前回以前に export 済み; #10/#11: 当回 export 分・保持2ヶ月 — :110-112）→ DeleteLogicalDeletedDevices
  ※ set -eu: CSV 失敗なら削除に到達しない（安全弁）→ 運用者は旧管理画面（eminelsv）から DL
```
**旧・1行**: cron 05:15 → 4 Command → パーティション `t_202`/`s_102`/`s_103`/`s_113` → CSV（EMS-SP-NO 単位）→ ZIP → ディスク → DeleteData → DeleteLogicalDeletedDevices。*（図中の省略表記の完全パスは §11 出典表。）*

キーコード — パーティション指定は4ファイルとも**同じ39行目**＋削除側の保持期間:
```php
$partitionTableName = 't_202_' . $dateTime->subDays(8)->format('Ymd');   // #8: 日・8日前   (各 CreateCsvAndZip*Command.php:39)
$partitionTableName = 's_102_' . $dateTime->subDays(8)->format('Ymd');   // #9: 日・8日前
$partitionTableName = 's_103_' . $dateTime->subDays(32)->format('Ym');   // #10: 月 — 必ず前々月
$partitionTableName = 's_113_' . $dateTime->subDays(32)->format('Ym');   // #11: 月 — 必ず前々月
// --- DeleteDataCommand.php:46-50（月次 s_103/s_113 は 53–54 行・2ヶ月） ---
// 日単位削除処理
$this->dropDailyTable('t_202', $dateTimeForDay, 8);    // 8日で削除
$this->dropDailyTable('s_101', $dateTimeForDay, 8);
$this->dropDailyTable('s_102', $dateTimeForDay, 14);   // 14日で削除（t_202 と異なる！）
$this->dropDailyTable('s_112', $dateTimeForDay, 8);
```
*（前々月の証明: default `'now'`＋毎月1日 05:15 → −32日 は必ず2ヶ月前の月。例 8/1−32日=6/30→`s_103_202606`。削除側 `dropMonthlyTable(…,2)`=`subMonths(2)` — `legacy_eminel_docs/sources/conciergesv-develop/src/Command/DeleteDataCommand.php:110-112` と整合。）*

| 異常系 | 挙動 | 出典 |
|---|---|---|
| CSV 生成失敗 | `set -eu` で停止 → 削除されない | `legacy_eminel_docs/docs/02_詳細設計/10_バッチ処理/cron設定概要.txt:26-37`・補足1「CSV作成後に問題なければデータを消去」 |
| パーティション不存在 | alert ログを出して終了 | `legacy_eminel_docs/sources/conciergesv-develop/src/Command/CreateCsvAndZipConDeviceStatusesCommand.php:42-45` |
| 月曜以外（#8/#9） | 週次 ZIP をスキップ | 同 `:182`（`isMonday`） |

**6.4 新側の既存／E-GW 要件**（確実）:
- e-smart にバックアップ後削除は**なし**。出力2経路あり（①② — コード §7.2/§7.3）。`CsvDownloadHistory` は受信方向。バックアップ = PITR・期限 = TTL（`syp-eminelstandard-backend/template-dynamodb.yaml`）。
- spec [I]: e-smart 踏襲種別（顧客情報・アクセスログ・ポイント履歴… — すべて 🔴T.B.D）＋E-GW 新規3種: GW・連携デバイスデータ／連携デバイスエラー履歴／**連携機器別計測値集計データ（10分/1時間/1日/1ヶ月値）**。**保持期間 24ヶ月（T.B.D）**。SVC-03 は未定義 — 🔍 `eminel_gw_project/docs/eminel/4_spec/admin/I_data_download.md:16-19, 43-52, 200-204`・`eminel_gw_project/docs/eminel/2_management/20_open_issues.md:87`。

**6.5 新方式の提案フロー**:
```
[経路①] 管理者（pages/other/data-management/index.vue ＋ form-download-data-management.vue）→ POST api-download（17 EP — app.ts:23-46）→ 非同期 invoke（'Event' — download-user-info.ts:17-25）
  → batch-download（5120MB/900s — template.yaml:475-493）→ DynamoDB 読出し（例 TABLE_KAIIN — :579）
  → CSV → JSZip（:563-568）→ S3 BUCKET_DOWNLOAD（template.yaml:233）→ presigned URL 600秒（get-presigned-url-for-download.ts:67）
[経路② — §9-B] ScheduleV2（既存例 BatchMigrationIntegratedData — template.yaml:2205-2240）→ CSV → SFTP /EST（雛形 upload-data-backup-to-sftp.ts）
※ どちらにも削除工程なし — 保持は TTL。「退避してから削除」は消滅（§8）
```
**新・1行**: 管理者 → api-download（17 エンドポイント）→ BatchDownloadFunction → ZIP → S3 BUCKET_DOWNLOAD → presigned URL 600秒。`/EST` 分岐: 6 CSV・毎日 8:00。*（完全パス: §11 出典表。）*

実施ステップ（SYP・`gw-syp-dev`）:
1. spec [I]＋SVC-03 の確定を [I] レビュー時に提起（質問表文面 §3）— 理由: 以降の設計値がすべて依存。
2. retention: `syp-eminelstandard-backend/template-dynamodb.yaml` に TTL 定義。高コストなら S3 退避（集計系のデータ量見積りで判断）— 理由: TTL が「バックアップ後削除不要」の前提。
3. ダウンロード拡張4レイヤー: `syp-eminelstandard-backend/src/functions/api-download/app.ts`＋委譲ハンドラ（雛形 `syp-eminelstandard-backend/src/functions/api-download/download-user-info.ts`）／`syp-eminelstandard-backend/src/functions/batch-download/` ハンドラ（雛形 `syp-eminelstandard-backend/src/functions/batch-download/download-user-info.ts`）／`syp-eminelstandard-backend/template.yaml` の `BatchDownloadFunction` へ環境変数 `TABLE_*` 追加（475–493）／web-admin `DOWNLOAD_DATA_MANAGEMENT_TYPE`（`syp-eminelstandard-web-admin/constants/common.ts:614-622`）＋`syp-eminelstandard-web-admin/pages/other/data-management/index.vue`＋`syp-eminelstandard-web-admin/components/data-management/form-download-data-management.vue`＋`syp-eminelstandard-web-admin/components/data-management/list-download-data-management.vue` — 理由: 17 EP／7種別が同一パターン。
4. 顧客が定期ファイル希望と確定した場合のみ: 経路②でエクスポートバッチ1本（雛形 `syp-eminelstandard-backend/src/layers/common/nodejs/services/upload-data-backup-to-sftp.ts`＋`ScheduleV2` 1本）— 理由: [I] で要否未確定・確定前に作らない（§9）。
5. CSV 列: 旧形式互換を推奨（*推定* — 運用慣習）。列一覧は [I] に抽出済み（`DownloadController::getCsvHeadersOnSelection()`）— 再抽出タスクは不要。
6. Notion 分割時:「廃止、retention＋DL／エクスポートで代替」と明記 — 理由: 約46本の母数の誤算入防止。

テスト: 経路① end-to-end（フォーム → 生成 → `BUCKET_DOWNLOAD` → presigned URL 600秒）／列を [I] 現行EMINEL 一覧と突合／TTL 境界（超過は失効・期間内は DL 可）／経路② は既存6種と同形式で `/EST` 送達。
## 7. グループ共通基盤
**7.1 基盤＋前提**:
| | 旧 | e-smart |
|---|---|---|
| 言語 | PHP 8.0 / CakePHP 4.4 | TypeScript / SAM + Lambda（Node.js 24 — `syp-eminelstandard-backend/template.yaml:181`） |
| DB | PostgreSQL（パーティション） | DynamoDB（PITR 有効） |
| バッチ | サーバー cron＋shell flock | Step Functions + EventBridge Scheduler |
| 受信 | SFTP → ディスク | SFTP → S3 → DynamoDB |

静的スケジュール3本（`ScheduleV2`・`Asia/Tokyo` — `syp-eminelstandard-backend/template.yaml:9-11`）: ① `BatchRunSequentially` `cron(5 0-7 * * ? *)`（853–888）② `BatchMigrationIntegratedData` `cron(0 8 * * ?)`（2205–2240）— **経路② `/EST` はこの中**③ `BatchGetErrorDeviceInfoOfRinnai`（2966–2980）。他は one-shot 動的生成（`syp-eminelstandard-backend/src/layers/common/nodejs/services/put-schedule.ts:18-33`）、例外はオートメーション（`syp-eminelstandard-backend/src/functions/api-automation/common.ts:115, 167-175`）、毎分ポーリングなし（grep `rate(`: 0件）。Day3: 現行バッチ「いけてない」— 作り直し・1バッチ=1タスク・バッチボーン先置き・結合9月（🔍 `eminel_gw_project/docs/eminel/2_management/minutes/20260625_egw_camp_day3.md:35, 51, 99-103, 147-149`）。QA 独立デプロイ（swan・回答中）: 独立方向 →「流用」≠ 工数ゼロ。`gw-syp-dev` に E-GW コミットなし。*推定*: e-smart コードベースへの追記方式（QA 管理画面共通ソース — masao takahashi・回答中 — からの推測）。

**7.2 経路①**（確実）— 17 エンドポイント（🔍 `syp-eminelstandard-backend/src/functions/api-download/app.ts:23-46`）＋ web-admin 7種別（🔍 `syp-eminelstandard-web-admin/constants/common.ts:614-622`）:
```ts
const APIs = {
  POST: {
    ...                                    // 先頭エントリ（download_list_device_error_mst）は省略
  [`/${END_POINT}/download_list_dr`]: downloadListDr, ...
  [`/${END_POINT}/download_access_log`]: downloadAccessLog,
  [`/${END_POINT}/download_user_info`]: downloadUserInfo,
  [`/${END_POINT}/download_gas_equipment_data`]: downloadGasEquipmentData, ...
// --- syp-eminelstandard-web-admin/constants/common.ts:614-622 ---
export const DOWNLOAD_DATA_MANAGEMENT_TYPE = {
  USER_INFO: 'user_info',            ACCESS_LOG: 'access_log',
  MUI_SENSOR_HISTORY: 'mui_sensor_history', GAS_DEVICE_HISTORY: 'gas_device_history',
  POINT_AWARD_HISTORY: 'point_award_history', BADGE_EARNED_HISTORY: 'badge_earned_history',
  GAS_DEVICE_RAW_HISTORY: 'gas_device_raw_history',
}
```
- 重量級は `BatchDownloadFunction` を非同期 invoke（`'Event'` — `syp-eminelstandard-backend/src/functions/api-download/download-user-info.ts:17-25`。`syp-eminelstandard-backend/template.yaml:475-493`・5120MB/900s）。DynamoDB 読出し（環境変数 `TABLE_*` — 483–492。顧客情報 = `TABLE_KAIIN` — `syp-eminelstandard-backend/src/functions/batch-download/download-user-info.ts:579, 590`）→ JSZip（563–568）→ S3 `BUCKET_DOWNLOAD`（:233）→ presigned URL 600秒（`syp-eminelstandard-backend/src/functions/api-s3/get-presigned-url-for-download.ts:67`）。
- ⚠️ `CsvDownloadHistory` = 受信方向（`syp-eminelstandard-backend/src/layers/common/nodejs/models/CsvDownloadHistory.ts:1-6`。記録 `syp-eminelstandard-backend/src/functions/batch-forward-csv-from-sftp-server-to-s3/app.ts:80-93`）。

**7.3 経路② `/EST`**（確実。宛先は ※推定（未確認））: 機器 CSV 6種（給湯器系5＋赤外線リモコン）・毎日 8:00・アップロード専用アカウント — 🔍 `syp-eminelstandard-backend/src/layers/common/nodejs/services/upload-data-backup-to-sftp.ts:22-43, 52-57`・`syp-eminelstandard-backend/template.yaml:2215-2226`。§9-B の先例。宛先未確認（§10-B1）。詳細: 外部連携・受信系分冊 **§7.6**（送信方向 `/EST` — コード＋F-ES-10）。受信フロー同 §7.3・8 IF 詳細表 §7.4。
## 8. 新旧データ対照
| 旧テーブル | 旧保持 | 別表①の対応種別 | 新側に既存テーブル？ |
|---|---|---|---|
| `t_202` | 8日 | GW・連携デバイスデータ（🔴T.B.D） | ❌ 新設（§6.5-2/3） |
| `s_102` | 14日 | 集計データ・1時間値（🔴T.B.D） | ❌ 新設・集計系と連携 |
| `s_103` | 2ヶ月 | 集計データ・1日値（🔴T.B.D） | ❌ 新設・集計系と連携 |
| `s_113` | 2ヶ月 | 別表①に直接対応なし | ❌ [I] の種別確定待ち |
| **集計** | — | — | **既存 0/4（❌×4）** —「計測系の流用資産なし。e-smart は事前集計も持たない（`syp-eminelstandard-backend/src/functions/api-dashboard/get-monthly-report-of-user.ts:21`）」と整合 |

| 機構 | 旧 | 新 | 状態 |
|---|---|---|---|
| 置き場所 | PostgreSQL パーティション | DynamoDB（新設） | ❌ |
| 保持期間 | 8〜14日（＋2ヶ月）— `legacy_eminel_docs/sources/conciergesv-develop/src/Command/DeleteDataCommand.php:47-50, 53-54` | [I] 24ヶ月＋TTL | ⚠️ T.B.D |
| 取り出し | 事前作成 → ディスク → 旧画面 | 要求時生成（①）／定期（②） | ✅ 既存・種別追加のみ |
| 削除 | バックアップ後 DROP（`set -eu` 安全弁） | TTL 自動失効 | ✅ DynamoDB 標準 |
| バックアップ | 退避ファイルが兼務 | PITR＋SVC-03 待ち | ⚠️ |
| **集計** | — | — | **✅2 ・ ⚠️2 ・ ❌1** — 作業はテーブル新設＋保持確定に集中。出力機構側にはない |
## 9. 案A/B
| 基準 | **A — 既存 DL の拡張のみ** | **B — A＋定期エクスポート追加（`/EST`）** |
|---|---|---|
| 取り出しニーズ | ✅ 充足 | ✅ 充足＋慣習維持 |
| 追加工数 | パターン追随4レイヤー（§6.5-3） | ＋バッチ1本＋`ScheduleV2`＋配置先決定 |
| 依存する未決 | spec [I] | [I]＋`/EST` 宛先＋顧客希望の確認 |
| 顧客運用 | 慣習変更: 必要時 DL | 現行維持 |

まず **A**（依存最小。「定期ファイル」は未確認の慣習にすぎない）。**B へ**: 顧客が継続希望と回答（§3 文面）または [I] 確定時に定期作成が要件化された場合。
## 10. QA一覧（宛先別。D アプリチーム: 関与なし — 省略）
| # | 宛先 | 質問 | 理由 | 重要度 |
|---|---|---|---|---|
| A1 | 北ガス様/PM | [I] の確定: 24ヶ月＋対象種別。SVC-03 の方針も（文面 §3・質問表へ追加提案） | retention 設計の全前提 | 🔴 |
| A2 | 北ガス様/PM | 週次／月次 ZIP の定期作成・保管の継続希望は？（文面 §3） | 案A/B の分岐（§9）。[I] 未決 | 🟡 |
| A3 | 北ガス様/PM | e-smart 踏襲7種別のうち E-GW 対象はどれか（別表①すべて 🔴T.B.D） | ステップ3の範囲 | 🟡 |
| B1 | mui 様 | `/EST` の宛先は Xzilla/DWH か（短縮形 §3。完全版は Xzilla 分冊 §3 — 両分冊で1回） | 経路②の前提。F-ES-10 送信方向にも関わる | 🟡 |
| B2 | mui 様 *（SYP から回答）* | QA 独立デプロイの設問「使い続けたほうがいい機能」への回答: ① 旧EMINEL なし ・ ② e-smart 4候補 — 本グループは DL／エクスポート機構（§7.2/§7.3） | mui 様が回答待ち。基盤共用方針の確定を助ける（§5-7） | 🟡 |
| C1 | 引継ぎ元 | 現行 CSV 列形式に業務上の制約はあるか（読み込む後続システムの有無） | ステップ5の互換レベル — 現状は*推定* | 🟡 |
```
A1 [I]+SVC-03（🔴）─→ ステップ2 retention → ステップ3 DL 拡張
A2＋B1 ─→ 案A/B 決定（§9）→（B なら）ステップ4 エクスポート     C1 ─→ ステップ5 列互換
```
## 11. 根拠と確度
| 内容 | 出典 |
|---|---|
| 旧: パーティション/default now/出力先/isMonday/不存在時; 削除保持（8/14日・2ヶ月・keepDays+1） | `legacy_eminel_docs/sources/conciergesv-develop/src/Command/CreateCsvAndZip*Command.php:39`（×4）・`legacy_eminel_docs/sources/conciergesv-develop/src/Command/CreateCsvAndZipConSensorDailyValuesCommand.php:28`・`legacy_eminel_docs/sources/conciergesv-develop/src/Command/CreateCsvAndZipConDeviceStatusesCommand.php:58, 182, 42-45`・`legacy_eminel_docs/sources/conciergesv-develop/src/Command/DeleteDataCommand.php:46-50, 53-54, 85, 110-112` |
| ZIP＋SJIS・cron＋shell（`set -eu`・DeleteLogicalDeletedDevices） | `legacy_eminel_docs/sources/conciergesv-develop/src/Command/CreateZipsTrait.php:23-72`・`legacy_eminel_docs/docs/02_詳細設計/10_バッチ処理/mng-webap_cron設定_20241029.txt:39-41`・`legacy_eminel_docs/docs/02_詳細設計/10_バッチ処理/cron設定概要.txt:26-37`・shell: `legacy_eminel_docs/docs/02_詳細設計/10_バッチ処理/cron実行用シェルスクリプト/eminel-mng-webap.20240909.tgz` 内 |
| 経路① | `syp-eminelstandard-backend/src/functions/api-download/app.ts:23-46`・`syp-eminelstandard-backend/src/functions/api-download/download-user-info.ts:17-25`・`syp-eminelstandard-backend/template.yaml:233, 475-493`・`syp-eminelstandard-backend/src/functions/batch-download/download-user-info.ts:563-568, 579, 590`・`syp-eminelstandard-backend/src/functions/api-s3/get-presigned-url-for-download.ts:67`・web-admin `syp-eminelstandard-web-admin/constants/common.ts:614-622`＋`syp-eminelstandard-web-admin/pages/other/data-management/`＋`syp-eminelstandard-web-admin/components/data-management/*` |
| 経路②＋スケジュール基盤 | `syp-eminelstandard-backend/src/layers/common/nodejs/services/upload-data-backup-to-sftp.ts:22-43, 52-57`・`syp-eminelstandard-backend/template.yaml:9-11, 853-888, 2205-2240, 2215-2226, 2966-2980`・`syp-eminelstandard-backend/src/layers/common/nodejs/services/put-schedule.ts:18-33`・`syp-eminelstandard-backend/src/functions/api-automation/common.ts:115, 167-175` |
| E-GW 要件・事前集計なし・Day3 | `eminel_gw_project/docs/eminel/4_spec/admin/I_data_download.md:16-19, 43-52, 200-204`・`eminel_gw_project/docs/eminel/2_management/20_open_issues.md:86-87`・`syp-eminelstandard-backend/src/functions/api-dashboard/get-monthly-report-of-user.ts:21`・`eminel_gw_project/docs/eminel/2_management/minutes/20260625_egw_camp_day3.md:35, 51, 99-103, 147-149` |

- ✅ 確実: 旧システムの挙動全記述（§6.3 — コード＋shell 実物）。「e-smart にバックアップ後削除なし・2出力経路あり」（§7 — `gw-syp-dev` の実コード）。[I]／SVC-03 の内容（メタ欄のコミット時点）。
- ⚠️ *推定*／※推定（未確認）: (a) 列互換推奨 — 運用慣習（§6.5-5）。(b) `/EST` 宛先 = Xzilla/DWH（§7.3）。(c) e-smart コードベースへの追記方式（§7.1）。
- ❓ 未確認: [I] は DRAFT（種別・24ヶ月とも T.B.D）。SVC-03 未定義。データ量（集計系待ち）。定期ファイルの顧客希望。QAデータベース3件（独立デプロイ — swan／調査範囲 — swan／管理画面 — masao takahashi）は回答中・2026-08-04 参照（スクリーンショット経由）— 再引用時は原ページ確認。788b438→fbc0af0（6コミット）は `3_requirements/app/`＋skill 1行のみ — 本書引用資料は不変（2026-08-06 確認）。

| ESTA 調査資料の記載 | 実コード |
|---|---|
| `CsvDownloadHistory` = ダウンロード履歴（`eminel_gw_project/docs/eminel-smart/03_backend_models.md:107`） | 受信方向 — SFTP 取得の二重取込防止（§7.2） |
| 自動化ルール毎分（`eminel_gw_project/docs/eminel-smart/02_product_overview.md:85`） | ルール毎の週次スケジュール動的生成（§7.1。grep `rate(`: 0件） |
| Node.js 20.x（`eminel_gw_project/docs/eminel-smart/02_product_overview.md:49`） | `nodejs24.x`（`syp-eminelstandard-backend/template.yaml:181`。CompatibleRuntimes は 20 のまま — :3163） |
