# 旧EMINELバッチ移行判定報告書 — CSV・ZIPエクスポート系4本（#8〜#11）

## 1. 管理情報

| | |
|---|---|
| 作成日 | 2026-08-06（調査実施日: 2026-08-04） |
| 作成者 | Bui Trong Dat（SYP）＋AI調査支援 |
| 位置づけ | 本書は、旧EMINELバッチ移行判定（全11本・3グループ）を分冊化した**3分冊のうちの1冊**であり、**CSV・ZIPエクスポート系4本（#8〜#11）** を対象とする。他分冊: 「配信・通知系4本（#1〜#4）」「外部連携・受信系（Xzilla取込）3本（#5〜#7）」。バッチ番号 #1〜#11 は全11本の通し番号であり、分冊間および日本語版／ベトナム語版の間で共通 |
| 目的 | `legacy_eminel_docs/docs/03_API仕様/04_バッチ一覧.md` のうち **CSV・ZIPエクスポート系** の4バッチ（いずれも旧システムの `conciergesv` 上で稼働）について、e-smart 既存実装の有無を実コードで確認し、`eminel_gw_project/docs/eminel` の E-GW 要件と照合のうえ **流用・新規・廃止** を判定する |
| 対象リポジトリ | `legacy_eminel_docs` @ `ccd8f56` ・ `eminel_gw_project` @ `fbc0af0`（調査実施は `788b438` 時点 — 差分の扱いは補足参照）・ `syp-eminelstandard-backend` @ `dc39aa39`（branch `gw-syp-dev`）・ `syp-eminelstandard-web-admin` @ `e550326`（branch `gw-syp-dev`）— いずれも 2026-08-06 時点の origin と一致 |
| 判定区分 | **流用** = e-smart の既存実装・機構を利用（工数ゼロの意ではない — §3）・ **新規** = E-GW 向けに新規実装 ・ **廃止** = 移植せず、既存機構または新方針で代替 |
| 凡例 | **確実** = 資料・コード上で直接確認済み ・ ***推定*** = 根拠ある推測（未確定 — 最終判断には使わない）・ 🔍 = 出典（パスは `sources/` 起点、行番号は上記コミット時点のもの）・「grep 0件」= 対象コード全体を検索してヒットなし |

補足（引用時の注意）:

- e-smart（= ESTA = EMINEL-Smart。同一システムの3呼称）に関する「有り／無し」の記述は、すべて `syp-eminelstandard-backend`・`syp-eminelstandard-web-admin`（branch `gw-syp-dev`）の実コードを直接確認した結果である。
- **`eminel_gw_project` の更新（788b438 → fbc0af0、6コミット、2026-08-03夜〜08-05夜）について**: 差分は `docs/eminel/3_requirements/app/` 配下13ファイル＋ skill ファイル1行のみであり、本書が引用する管理画面データダウンロード仕様 `4_spec/admin/I_data_download.md`・未決事項一覧 `20_open_issues.md`・統合要件 v1.2・決定ログ・合宿議事録・ESTA調査資料（`docs/eminel-smart/`）には変更がないことを 2026-08-06 に確認済み。**本グループの判定・引用行番号への影響なし**。
- QAデータベース（Notion — mui との内部QAチャネル）の引用3件は、いずれも参照日 2026-08-04 時点で**回答中**（スクリーンショット経由で参照）。再引用の際は原ページの最新状態の確認をお願いしたい。
- スコープ・要件の判定に用いた T.B.D（未定）／QA回答中の論点は本文の該当箇所に明記した。

## 2. 総括（結論）

4本とも実態は**削除前バックアップ**（詳細 §4）であり、運用者向けのデータダウンロード機能ではない。**判定（確実）: 4本まとめて廃止** — ただし「廃止」の中身は次の3行に分解される:

- **廃止するもの**: 「CSV/ZIP へ退避してからパーティション（大テーブルを日／月単位に区切った領域。区切りごと一括削除できるため高速）を削除する」機構そのもの — 旧 DB の短期保持（機器状態 `t_202`: 8日、時間値 `s_102`: 14日 — §4.1）と一体の設計であり、E-GW には持ち込まない。
- **残すもの**: 「運用者がデータをファイル（CSV/ZIP）で取り出せる」というニーズ — E-GW 側では spec [I]（管理画面データダウンロード仕様 `4_spec/admin/I_data_download.md`・DRAFT）が管理画面ダウンロード機能として再定義している。
- **代替**: 新しい保持期間（retention）方針 — DynamoDB TTL（期限到来レコードの自動削除）＋高コストなら S3（ファイルストレージ）退避。spec [I]＋SVC-03（未決事項: 性能・可用性・運用・移行要件が未記載 — `20_open_issues.md:86`。保持期間・バックアップはその一項目・同:87）の確定待ち — に、e-smart 既存の2出力経路を組み合わせる: **経路①** 管理画面オンデマンドダウンロード（17 エンドポイント／7 データ種別）・**経路②** SFTP `/EST` への定期エクスポート（いずれも §4.3）。

判定理由: E-GW 要件は性質が変化しており（spec [I]: 管理画面から集計データをダウンロード、保持期間 **24ヶ月** T.B.D — 「短期保持して削除」方式ではない）、e-smart 側にも「バックアップ後削除」機構は存在しないため。4本の違いは対象データと周期のみ:

| # | バッチ | バックアップ対象（旧テーブル） | 旧周期 |
|---|---|---|---|
| 8 | `CreateCsvAndZipConDeviceStatusesCommand` | 機器状態（`t_202`）・8日経過パーティション | 毎日 05:15、月曜に週次 ZIP |
| 9 | `CreateCsvAndZipConSensorHourlyValuesCommand` | 時間値（`s_102`）・8日経過パーティション | 毎日 05:15、月曜に週次 ZIP |
| 10 | `CreateCsvAndZipConSensorDailyValuesCommand` | 日値（`s_103`）・**前々月**パーティション（約2ヶ月経過 — `DeleteData` の保持2ヶ月と一致。§4.2） | 毎月1日 05:15、即 ZIP |
| 11 | `CreateCsvAndZipConSensorDailyAveValuesCommand` | 日平均値（`s_113`）・**前々月**パーティション（同上）— 全体1ファイル（世帯分割なし） | 毎月1日 05:15、即 ZIP |

**一覧の読み方（3点）**:

- **確実／*推定*** のラベルは**事実部分**（旧システムの挙動、e-smart の有無、スコープ）の確度を示す。「判定」は常にレビュー用の提案である — 本分冊の4本は「廃止」の方向性まで確実、詳細（保持期間の値・定期エクスポートの要否）は spec [I]・SVC-03 の T.B.D 待ち（§4.7 ステップ1）。
- 本報告は「何を作る／何を流用する」の判定までであり、**工数は未見積**（方針どおり 1バッチ = 1タスクの Notion 分割時に見積り予定 — §3）。
- 4本の範囲外への示唆: e-smart は**事前集計を一切持たない**（アプリの月次レポートは要求の都度 TagTag API（北ガスの会員基盤 API — e-smart の電力／ガスデータ源）へ転送するだけで保存しない — 🔍 `syp-eminelstandard-backend/src/functions/api-dashboard/get-monthly-report-of-user.ts:21`）。
  - したがって E-GW の**集計・計算系**グループ（バッチ一覧の別グループ、本書対象外）にも流用できる既存資産はない見込み。
  - 本分冊の対象に含まれる「連携機器別計測値集計データ」（10分/1時間/1日/1ヶ月値 — §4.4）のダウンロードは、同グループが新規に構築する集計出力を前提とする。

## 3. 判定の前提

**方針（mui 合宿 Day3・2026-06-25 決定済み）**: 現行バッチは「いけてない」— **作り直しが前提**（「バッチ群（約46本…）をNotionに機能単位でタスク化…作り直す前提」）。1バッチ = 1タスク、バッチボーン（空実装の骨組み）を先に置き、結合フェーズ（9月目標）前に実動確認する。バッチ／外部連携領域は SYP 担当想定。→ 本報告の「**流用**」は **e-smart の機構・基盤・コードベースの利用**を指し、旧システムの PHP コード移植（port）ではない。

- 🔍 `eminel_gw_project/docs/eminel/2_management/minutes/20260625_egw_camp_day3.md` 35, 51, 99–103, 147–149 行

**実行環境に関する前提（3点）**:

- QA「旧Eminel基盤継承＋EMINEL-smartサーバーは独立デプロイの確認」（swan（mui）・回答中・2026-08-04参照）の暫定回答の要旨: **基本的には独立したシステムとして開発する方向**。したがって本報告の「e-smart 流用」= コード・機構・パターンの流用であり、独立デプロイが確定した場合は**新環境への構築作業が別途発生**する（「流用」≠ 工数ゼロ）。
- 現状コード: backend・web-admin とも branch `gw-syp-dev` は存在するが **E-GW 向けコミットはまだゼロ**（web-admin: `git log origin/main..gw-syp-dev` が空。backend: 直近15コミットは e-smart 本体のみ）。E-GW 開発はこのブランチ上でゼロから開始となる。*推定*: 実装は e-smart コードベースへの追記方式となる見込み — QA「管理画面は独立か共通か（切替モード追加）の確認」（masao takahashi（mui）・回答中・2026-08-04参照）の暫定回答（要旨: e-smart と共通ソースの方向）からの推測であり、文書化された決定ではない。
- 「共通ソース」と「共通実行環境」は別問題 — 上記2件の QA はいずれも暫定回答の段階である。

**新旧の技術ギャップ**:

| | 旧システム（`conciergesv` 等） | e-smart（`syp-eminelstandard-backend`） |
|---|---|---|
| 言語／フレームワーク | PHP 8.0 / CakePHP 4.4 | TypeScript / AWS SAM + Lambda（Node.js 24 — `template.yaml:181`） |
| データベース | PostgreSQL（日／月パーティション） | DynamoDB（PITR = ポイントインタイムリカバリ〔任意時点への復旧バックアップ〕有効） |
| バッチ実行方式 | サーバー cron（`/etc/cron.d/eminel-mng-webap`）＋ shell（flock 排他） | Step Functions + EventBridge Scheduler |
| 外部ファイル受信 | SFTP → サーバーディスク | SFTP → S3 → DynamoDB |

- 🔍 旧: `legacy_eminel_docs/docs/02_詳細設計/10_バッチ処理/cron設定概要.txt` 1–37 行 ・ e-smart: `syp-eminelstandard-backend/template.yaml`（SAM）、`eminel_gw_project/docs/eminel-smart/02_product_overview.md` 48–53 行

**e-smart バッチ基盤の要点**（E-GW が継承する足回り。以下パスは `syp-eminelstandard-backend/` 起点）:

- **静的スケジュールは3本のみ**（いずれも `ScheduleV2`・timezone `Asia/Tokyo` — `template.yaml:9-11`）: ① `BatchRunSequentiallyStateMachine` — 基幹データ取込、`cron(5 0-7 * * ? *)` = JST 0〜7時の毎時5分（`template.yaml:853-888`、cron は 881–882 行）② `BatchMigrationIntegratedDataStateMachine` — Rinnai／Noritz 機器データ取得＋エクスポート、`cron(0 8 * * ?)`（`template.yaml:2205-2240`、cron は 2233 行）— **本分冊の経路②（`/EST` エクスポート — §4.3）はこの②に載っている** ③ `BatchGetErrorDeviceInfoOfRinnaiStateMachine` — 機器エラー取得、同 8:00（`template.yaml:2966-2980`）。
- **それ以外のバッチはすべて EventBridge Scheduler のスケジュールを動的生成**する方式。大半は one-shot（一時点だけ発火し、`ActionAfterCompletion.DELETE` により実行後自動削除される単発スケジュール — 共通関数 🔍 `src/layers/common/nodejs/services/put-schedule.ts:18-33`）。例外はユーザーのオートメーション（アプリ内の機器自動化ルール）のみで、ルール毎の週次スケジュールを動的生成する（繰り返し型・自動削除なし — `src/functions/api-automation/common.ts:115, 167-175`）。毎分ポーリングは存在しない（grep `rate(`: 0件）。

**SYP の担当範囲**: QA「旧EMINEL調査範囲（conciergesv/eminelsv）とhemssv対象外の確認」（swan（mui）・回答中・2026-08-04参照）の要旨 — `conciergesv`/`eminelsv` は SYP の**調査**対象であり、旧システム上で開発を続ける範囲ではない。GW との通信は mui 開発の HEMS-SV（m2-cloud。旧システムの `hemssv` とは別物 — 名称が類似しているのみ）経由となり、スペックは後日共有予定。

**2026-06-10 のスコープ決定**（決定ログ登録済み）: 必須 = 暖房機能／暖房制御／照明アドバイス※／ポイント連携／グルーピング・レポート。劣後（2027/4〜）= 複合制御・DR・ダッシュボード・バッジ等。※「照明アドバイス」は省エネアドバイスの誤記と思われる（*推定*）。

- 🔍 `eminel_gw_project/docs/eminel/2_management/22_decisions.md` 30–31 行
- 機能一覧（`docs/eminel/1_product/10_feature_list.md`）の劣後列の凡例に注意: **✅ = 2027 へ繰越可**（スコープ内の意ではない）、空欄 = 今期必須。

**§4 の実施主体**: 特記のない限り実施者は **SYP**、実装は branch `gw-syp-dev` 上。リポジトリ名のないパスは `syp-eminelstandard-backend`、管理画面側は `syp-eminelstandard-web-admin`。「確認／決着」系のステップは §5 の経路による。本文中の人名（敬称略）: swan・masao takahashi（いずれも mui — QAデータベース回答者）。

## 4. 判定詳細（4本まとめて判定）

（旧システムコードのパス表記 `…/src/Command/` は `legacy_eminel_docs/sources/conciergesv-develop/src/Command/` の略。「cron:NN行」は `legacy_eminel_docs/docs/02_詳細設計/10_バッチ処理/mng-webap_cron設定_20241029.txt` の行番号。）

**4本の目的**: この4本は「細粒度データ（機器状態・時間値・日値・日平均値）を CSV/ZIP に退避してから、DB のパーティションを削除する」ために存在する。これにより旧 DB は細粒度データを 8〜14 日程度しか保持せずに済み、それでも運用者は必要時に退避済み ZIP から過去データを参照できた。**運用者向けのデータダウンロード機能ではない** — ファイルの取り出しは結果として可能だが、主目的は削除前の退避である（バッチ名だけを見ると誤解しやすい）。

### 4.1 判定（方向性は確実、詳細は T.B.D 待ち）

**現行形態の4本は廃止 — ただし「ファイルで取り出せること」は残す。** 整理すると:

- **廃止**: 「削除前バックアップ」機構（4バッチ＋shell＋`DeleteData` の組合せ）。前提である旧 DB の短期保持 — 細粒度データを 8〜14 日程度しか保持しない（`t_202`: 8日、`s_102`: 14日 — 🔍 `…/src/Command/DeleteDataCommand.php:47-50`、§4.2 のキーコード参照）— が、spec [I] の「24ヶ月保持・随時ダウンロード」と両立しないため。
- **維持**: 運用者がデータを CSV/ZIP で取り出せるニーズ — spec [I] の管理画面ダウンロードとして実現（旧形式の列互換は §4.7 ステップ5）。
- **代替**: 保持期間は DynamoDB TTL（＋必要なら S3 退避）で管理（§4.7 ステップ2）、取り出しは経路①（オンデマンド）を基本とし、定期ファイル受領の運用希望があれば経路②（定期エクスポート）を追加（§4.7 ステップ3〜4）。

**この判定の理由（3点）**:

- ① 4本の実態は上記「目的」のとおり**削除前バックアップ**であり、旧 DB の保持期間 8〜14 日（§4.2 のキーコード）と一体の設計である — 保持期間の前提が変われば機構ごと存在理由を失う。
- ② E-GW 要件は性質が変化した: spec [I]（管理画面データダウンロード仕様）は**保持期間 24ヶ月（T.B.D）＋随時ダウンロード**を定義しており（§4.4）、「短期保持して削除」方式とは両立しない。
- ③ e-smart に「バックアップ後削除」機構は存在しない一方、**データ出力の2経路（管理画面オンデマンド／SFTP 定期エクスポート）は既に完備**している（§4.3）— したがって4本を移植せず、新 retention 方針＋既存2経路で代替するのが最小構成となる。

### 4.2 旧システムでの実態（確実）— 流れ・キーコード・要点

```
【旧システム】4本の実際の流れ（毎日または毎月1日の 05:15）

  cron 05:15（「#12.DBデータ削除」セクション — cron:39-41）
    │  毎日: day2to31.sh（#8/#9 の2本）
    │  毎月1日: day1.sh（#8〜#11 の全4本 — #10/#11 はここにしか登場しない）
    ▼
  CreateCsvAndZip*Command（4本 — 対象テーブルと周期だけが違う）
    │  PostgreSQL の日付付きパーティションから読み出し
    │  （t_202_YYYYMMDD 機器状態・s_102 時間値: 8日前
    │    s_103 日値・s_113 日平均値: 前々月 = 約2ヶ月経過 — 下記キーコード注参照）
    ▼
  CSV 生成（世帯 = EMS-SP-NO 単位に分割。#11 のみ全体1ファイル）
    │  出力先: サーバーディスク（環境変数 CON_DEVICE_CSV_FILES_PATH 等）
    ▼
  ZIP 圧縮（ZipArchive・ZIP 内ファイル名は SJIS — CreateZipsTrait.php:23-72）
    │  （#8/#9 の週次 ZIP は月曜のみ — isMonday 判定
    │    CreateCsvAndZipConDeviceStatusesCommand.php:182 ／ #10/#11 は即 ZIP）
    ▼
  DeleteDataCommand が保持期間超過のパーティションを DROP（区切りごと一括削除 = 高速）
    │  #8/#9: 9日／15日経過分を削除 — dropDailyTable は keepDays+1 日前を対象
    │    （DeleteDataCommand.php:85）→ いずれも前回以前の実行で export 済みの分
    │  #10/#11: 当回 export したパーティションと同一（保持2ヶ月 — 同:110-112）
    ※ shell は set -eu（エラー時即停止）
      → CSV 作成に失敗したら削除まで到達しない = データは消えない（安全弁）
    ▼
  運用者: 旧管理画面（eminelsv）からディスク上の CSV/ZIP をダウンロード
```

**キーコード（2箇所）** — 4本の「対象と周期」および保持期間の根拠:

対象パーティションの指定 — 4ファイルとも**同じ 39 行目**（🔍 各 `CreateCsvAndZip*Command.php:39`）:

```php
$partitionTableName = 't_202_' . $dateTime->subDays(8)->format('Ymd');   // #8 機器状態: 8日前の日パーティション
$partitionTableName = 's_102_' . $dateTime->subDays(8)->format('Ymd');   // #9 時間値: 8日前の日パーティション
$partitionTableName = 's_103_' . $dateTime->subDays(32)->format('Ym');   // #10 日値: 前々月の月パーティション
$partitionTableName = 's_113_' . $dateTime->subDays(32)->format('Ym');   // #11 日平均値: 前々月の月パーティション
```

（注 — なぜ −32日 が「前々月」になるか: shell は `--datetime` を渡さないため常に default `'now'` = 実行時刻で動く（各コマンドの `buildOptionParser` — 例 `CreateCsvAndZipConSensorDailyValuesCommand.php:28`）。毎月1日 05:15 の −32日 は必ず2ヶ月前の月に落ちる — 例: 8/1 − 32日 = 6/30 → `s_103_202606`。削除側 `dropMonthlyTable(…, 2)` = `subMonths(2)`（`DeleteDataCommand.php:110-112`）とも整合する。）

削除側の保持期間 — 🔍 `…/src/Command/DeleteDataCommand.php:46-50`（日単位分。月単位の `s_103`/`s_113` は同:53-54 で 2ヶ月）:

```php
// 日単位削除処理
$this->dropDailyTable('t_202', $dateTimeForDay, 8);    // 機器状態: 8日で削除
$this->dropDailyTable('s_101', $dateTimeForDay, 8);
$this->dropDailyTable('s_102', $dateTimeForDay, 14);   // 時間値: 14日で削除
$this->dropDailyTable('s_112', $dateTimeForDay, 8);
```

**要点（5行）**:

- **起動**: cron 05:15・「#12.DBデータ削除」セクション（本報告のバッチ番号 #1〜#11 とは別の番号体系）。shell 2本（いずれも末尾で `DeleteData` を実行 — tgz 内の実物で確認）: `12_CreateCsvAndDeleteData_day2to31.sh`（cron `15 5 * * *` = 毎日）は **#8/#9 の2本**を、`12_CreateCsvAndDeleteData_day1.sh`（cron `15 5 1 * *` = 毎月1日）は **#8〜#11 の全4本**を実行する（#10/#11 はこの shell にしか登場しない）— 🔍 cron:39-41。
- **CSV 出力**: 世帯（EMS-SP-NO）単位に分割（#11 の日平均値 `s_113` のみ全体1ファイル）。出力先はサーバーディスク（環境変数 `CON_DEVICE_CSV_FILES_PATH` 等 — `CreateCsvAndZipConDeviceStatusesCommand.php:58`）。
- **ZIP 化**: PHP の `ZipArchive`、ZIP 内ファイル名は SJIS へ変換（🔍 `CreateZipsTrait.php:23-72`）。#8/#9 の週次 ZIP は月曜のみ実行（`isMonday` 判定 — `CreateCsvAndZipConDeviceStatusesCommand.php:182`）。
- **削除**: CSV/ZIP 成功後に `DeleteDataCommand` が同パーティションを DROP。shell は `set -eu`（エラー時即停止）— **CSV 作成に失敗した場合、削除は実行されない**（🔍 `cron設定概要.txt` 26–37 行・補足1「CSV作成後に問題なければデータを消去」）。
- **取り出し**: ファイルはディスク上に残り、運用者は旧管理画面（`eminelsv`）からダウンロード。

### 4.3 e-smart 既存実装 — 「バックアップ後削除」機構はなし。データ出力は既存の2経路（確実）

**経路①: 管理画面オンデマンドダウンロード** — 管理者が要求した時点で生成する方式:

- 入口はルーターの 17 エンドポイント — 🔍 `src/functions/api-download/app.ts:23-46`（DR一覧／news一覧／DR統計／アクセスログ／ユーザー情報／ポイント付与履歴／ガス機器データ…）。
- 重量級のデータ種別は専用 Lambda `BatchDownloadFunction` へ**非同期委譲**（`InvocationType: 'Event'` — `src/functions/api-download/download-user-info.ts:17-25`。関数定義は `template.yaml:475-493` — MemorySize 5120／Timeout 900 の重量設定）。
- `BatchDownloadFunction`（コード実体 `src/functions/batch-download/`）は **DynamoDB のソーステーブルから読み出す**（環境変数に `TABLE_APP_ACCESS_LOG`・`TABLE_DR` 等を注入 — `template.yaml:483-492`。例: 顧客情報は会員テーブル `TABLE_KAIIN` から — `batch-download/download-user-info.ts:579, 590`）→ CSV 生成 → JSZip で ZIP 化（同:563-568）。
- 成果物は S3 バケット `BUCKET_DOWNLOAD`（ダウンロード成果物専用バケット — 定義 `template.yaml:233`）へ格納、管理者は **presigned URL**（S3 の期限付き署名 URL。有効 600 秒 — `src/functions/api-s3/get-presigned-url-for-download.ts:67`）でダウンロードする。
- 管理画面（web-admin）側の対応ページは `pages/other/data-management/index.vue`＋フォーム `components/data-management/form-download-data-management.vue`・一覧 `list-download-data-management.vue`。扱う 7 データ種別は定数 `DOWNLOAD_DATA_MANAGEMENT_TYPE` — 🔍 `syp-eminelstandard-web-admin/constants/common.ts:614-622`（user_info／access_log／mui_sensor_history／gas_device_history／point_award_history／badge_earned_history／gas_device_raw_history）。
- 経路①の end-to-end の流れは §4.6 の図を参照。

**経路②: SFTP `/EST` への定期エクスポート** — 定期的にファイルを送り出す方式:

- e-smart は毎日 8:00 に機器データ CSV 6種（給湯器系5種＋赤外線リモコン）を SFTP サーバーの `/EST` フォルダへアップロード専用アカウントで送信している（`BatchMigrationIntegratedDataStateMachine`〔§3 の静的スケジュール②〕内 — 🔍 `src/layers/common/nodejs/services/upload-data-backup-to-sftp.ts:22-43, 52-57`・`template.yaml:2215-2226`）。
- 北ガス様が「定期的にファイルを受領する」運用を希望される場合の直接の先例。
- *推定（未確認）*: `/EST` の宛先は Xzilla/DWH（分析用データ基盤）と思われるが、接続先は secret 管理でコードから確認できない（§5-2）。
- この送信経路自体の詳細（コード引用・F-ES-10〔Xzilla連携〕の「EMINELデータの共有」との関係）は**外部連携・受信系（Xzilla取込）分冊の §4.1**（e-smart 受信基盤と送信方向 `/EST` を扱う節）に記載した。

⚠️ 調査資料由来の誤解への注記（2点）:

- `CsvDownloadHistory`（「CSVダウンロード履歴」）は**受信方向** — SFTP からのファイル取得履歴（二重取込防止）であり、管理者ダウンロードの履歴ではない（`src/layers/common/nodejs/models/CsvDownloadHistory.ts:1-6`、記録箇所 `src/functions/batch-forward-csv-from-sftp-server-to-s3/app.ts:80-93`）。
- DynamoDB に「N日後削除・ZIP保管」のモデルはない — バックアップは PITR（任意時点への復旧 — インフラレベル）、期限管理は必要テーブルごとの TTL（期限到来レコードの自動削除。`template-dynamodb.yaml` に定義）。

### 4.4 E-GW 要件 — 要件の性質が変化

spec [I]（管理画面データダウンロード仕様 `4_spec/admin/I_data_download.md`・DRAFT）が管理画面からのデータダウンロードを定義している:

- **e-smart 踏襲種別**: 顧客情報、アプリアクセスログ、ポイント付与履歴… — いずれも E-GW 向けは T.B.D（未定）。
- **E-GW 新規3種**: GW・連携デバイスデータ、連携デバイスエラー履歴、**連携機器別計測値集計データ（10分/1時間/1日/1ヶ月値）** — CSV(ZIP) 出力。
- **保持期間**: **24ヶ月（T.B.D）** — 旧方式の「8〜14日で削除」とは前提が根本的に異なる。
- あわせて SVC-03（未決事項一覧 `20_open_issues.md:86` の1項目 — **性能・可用性・運用・移行要件が未記載**）: その列挙の中に**データ保持期間・監視／バックアップ**が含まれる（同:87）— つまり新システムの保持期間／バックアップ要件は未定義。

- 🔍 `4_spec/admin/I_data_download.md:16-19, 43-52, 200-204` ・ `20_open_issues.md:87`（SVC-03）

### 4.5 新旧対応表（本グループ範囲 — 各観点が新旧どこにあるかの一覧）

| 観点 | 旧システム（4バッチ — PHP/PostgreSQL） | e-smart／E-GW（代替 — Lambda/DynamoDB） |
|---|---|---|
| データの置き場所 | PostgreSQL の日／月パーティション（`t_202` 機器状態・`s_102` 時間値・`s_103` 日値・`s_113` 日平均値） | DynamoDB 各テーブル（E-GW 計測系テーブルは新設 — 集計・計算系グループ〔別グループ・本書対象外〕と連携して設計） |
| 保持期間 | `t_202`: 8日・`s_102`: 14日（`DeleteDataCommand.php:47-50`）、`s_103`/`s_113`: 2ヶ月（同:53-54） | spec [I] は **24ヶ月（T.B.D）**。DynamoDB TTL で管理、高コストなら S3 退避（§4.7 ステップ2） |
| ファイルの取り出し方 | バッチが**事前に** CSV/ZIP を作成 → サーバーディスク → 旧管理画面（`eminelsv`）からダウンロード | **要求時に**オンデマンド生成（経路① — S3 `BUCKET_DOWNLOAD`＋presigned URL）／SFTP `/EST` へ定期送信（経路②） |
| 削除の仕組み | CSV 作成成功後に `DeleteDataCommand` がパーティション DROP（`set -eu` が安全弁） | DynamoDB TTL による自動失効（削除前の退避は不要 — 保持期間内は常に取り出せるため） |
| バックアップ | 退避 CSV/ZIP 自体がバックアップを兼ねる | PITR（インフラレベルの時点復旧）＋ SVC-03 の全体方針確定待ち |

### 4.6 新方式の流れ（図 — 経路①＋経路②）

```
【e-smart／E-GW】経路①: 管理画面オンデマンドダウンロード（旧4本の代替の主経路）

  管理者が web-admin「データ管理」画面でデータ種別・期間を指定
  （pages/other/data-management/index.vue ＋ components/data-management/form-download-data-management.vue）
    │  POST /download_user_info 等（17 エンドポイント — api-download/app.ts:23-46）
    ▼
  api-download の該当ハンドラ（例: download-user-info.ts）
    │  重量級は BatchDownloadFunction を非同期 invoke（InvocationType: 'Event' — 同:17-25）
    ▼
  batch-download（MemorySize 5120／Timeout 900 — template.yaml:475-493）
    │  DynamoDB ソーステーブルから読み出し
    │  （例: 顧客情報 = TABLE_KAIIN — batch-download/download-user-info.ts:579。
    │    E-GW 新種別のソーステーブルは §4.7 ステップ2〜3 で新設・追加）
    ▼
  CSV 生成 → JSZip で ZIP 化（同:563-568）
    ▼
  S3 バケット BUCKET_DOWNLOAD へアップロード（バケット定義 template.yaml:233）
    ▼
  管理者: presigned URL（期限付き署名 URL・有効 600 秒 —
  api-s3/get-presigned-url-for-download.ts:67）でブラウザからダウンロード

【経路②（分岐）: 定期ファイル受領の運用を継続する場合 — §4.7 ステップ4】

  静的スケジュール（毎日 8:00 の既存例: BatchMigrationIntegratedDataStateMachine — template.yaml:2205-2240）
    │  雛形: upload-data-backup-to-sftp.ts（機器 CSV 6種の既存送信）
    ▼
  CSV 生成 → SFTP サーバーの /EST フォルダへアップロード（宛先確認は §5-2）

  ※ データの削除は上記どちらの経路にも無い — 保持期間の管理は DynamoDB TTL が担い、
    「削除前の退避」という工程そのものが不要になる（§4.5 の対応表参照）
```

### 4.7 対応ステップ

1. spec [I]（E-GW データ種別＋保持期間 24ヶ月の確定）と SVC-03（retention／バックアップの全体方針）の確定 — spec [I] レビュー時に提起する。**質問表（北ガス様向け質問一覧 — 送付前）に未記載のため質問追加を検討**（§5-1）。
   - 理由: ステップ2以降の設計値（TTL 値・S3 退避の要否・対象データ種別）がすべてこの2点に依存する。確定前に着手すると手戻りになる。
2. 代替 retention 設計: 細粒度データはステップ1で確定する保持期間に従い DynamoDB に保持（`template-dynamodb.yaml` の対象テーブルに TTL を定義）、24ヶ月の DB 保持が高コストなら S3 への退避を検討 — 集計・計算系グループ（本書対象外）のデータ量見積りに従い判断。
   - 理由: 旧方式の「削除前バックアップ」が不要になるのは、保持期間内のデータが常に DB から取り出せる場合のみ。TTL 設計がこの前提そのものであり、コスト判断にはデータ量（集計系グループの管轄）が要る。
3. E-GW 新データ種別への既存ダウンロード機構の拡張（経路①のパターンどおり。変更ファイルはレイヤー毎に次のとおり）:
   - backend 入口: `src/functions/api-download/app.ts` へエンドポイント追加＋同フォルダに委譲ハンドラ追加（雛形: `api-download/download-user-info.ts` — 非同期 invoke の定型）
   - backend 生成処理: `src/functions/batch-download/` へハンドラ実装（雛形: `batch-download/download-user-info.ts` — DynamoDB 読出し→CSV→JSZip→S3 の定型）
   - インフラ: `template.yaml` の `BatchDownloadFunction`（475-493 行）へ新テーブルの環境変数 `TABLE_*` を追加
   - web-admin: `constants/common.ts` の `DOWNLOAD_DATA_MANAGEMENT_TYPE`（614-622 行）へ種別追加＋`pages/other/data-management/index.vue`・`components/data-management/form-download-data-management.vue`（期間指定フォーム）・`list-download-data-management.vue`（結果一覧）の対応
   - 理由: 17 エンドポイント／7 種別が同一パターンで並んでおり、パターン追随なら生成・ZIP・presigned URL・画面の各層を再実装せずに済む。
4. 北ガス様が「週次／月次で ZIP ファイルを定期作成・保管する」従来運用の継続を希望される場合: 経路②のパターン（`src/layers/common/nodejs/services/upload-data-backup-to-sftp.ts` が雛形。スケジュールは §3 の静的 `ScheduleV2` を1本追加）で定期エクスポートバッチを1本作成 — spec [I] の未決事項として確定待ち。
   - 理由: 経路①は「必要時に取りに来る」方式であり、「定期的にファイルが置かれている」ことを前提とする運用習慣とは別物。希望の有無自体が spec [I] で未確定のため、確定前に作らない。
5. CSV 列形式: 運用者の慣れを考慮し、旧形式との互換維持を推奨（*推定* — 運用慣習について）。現行の列一覧は **spec [I] に抽出済み**（現行 EMINEL セクション、出典 `DownloadController::getCsvHeadersOnSelection()`）— 旧4バッチのヘッダはクロスチェック用のみで、再抽出タスクは不要。
   - 理由: 列定義の一次情報は既に spec [I] 側にあり、二重管理を作らないため。互換維持は移行時の運用側の検証コストを下げる。
6. Notion タスク分割時: 旧4本は「廃止、retention＋ダウンロード／エクスポートで代替」と明記し、約46本の母数に誤って算入しないようにする。
   - 理由: 方針（§3 — 1バッチ=1タスク）どおり分割すると、廃止バッチも「移植タスク」に見えてしまう。母数の誤りは見積り全体を歪める。

### 4.8 テスト観点と確定待ち事項

**テスト観点**（§4.7 ステップ3〜4 の実装時の受入れ確認 — 提案）:

- 経路① end-to-end: 新データ種別を web-admin フォームで指定 → `batch-download` が生成 → `BUCKET_DOWNLOAD` へ格納 → presigned URL（600秒）でダウンロードできること（§4.6 の図の全区間）。
- 列互換: 生成 CSV の列を spec [I] の現行 EMINEL 列一覧（§4.7 ステップ5 の出典）と突合。
- TTL 境界: 保持期間を過ぎたレコードの自動失効と、保持期間内データがダウンロード可能であることの境界確認（ステップ2 の設計値どおり）。
- 経路②（ステップ4 を作る場合）: 既存6種の送信（`upload-data-backup-to-sftp.ts`）と同形式で `/EST` へ送達されること。

**確定待ち**（着手をブロックする外部要因）: spec [I] のデータ種別＋保持期間 24ヶ月・SVC-03 の全体方針（§5-1）、SFTP `/EST` の宛先（§5-2）。

## 5. ご確認・ご相談事項（一覧）

| # | 事項 | 関連 | 対応・経路 |
|---|---|---|---|
| 1 | spec [I]（管理画面データダウンロード仕様・DRAFT）の確定 — E-GW ダウンロード対象データ種別＋保持期間 24ヶ月（T.B.D）— と、SVC-03（未決事項: 性能・可用性・運用・移行要件が未記載 — `20_open_issues.md:86`。保持期間・バックアップを含む・同:87）の全体方針 | #8〜#11 の代替設計の前提（§4.7 ステップ1〜2）— 確定しないと TTL 値も S3 退避の要否も定期エクスポートの要否も決められない | spec [I] レビュー時に SYP が提起 — **質問表（北ガス様向け質問一覧）に未記載のため質問追加を検討** |
| 2 | **SFTP `/EST` の宛先確認**: e-smart が毎日 8:00 に機器 CSV 6種を送信している先が Xzilla/DWH（分析用データ基盤）か（接続先は secret 管理のためコードから確認不可） | §4.3 経路②（定期エクスポート — §4.7 ステップ4 の実現手段）の前提。送信経路自体の詳細は外部連携・受信系（Xzilla取込）分冊 §4.1 に記載 | mui 様にご確認をお願いしたい（QAデータベース、または HEMS-SV スペック共有時） |
| 3 | 「既存システムを使い続けたほうがいい機能」リスト（QA「旧Eminel基盤継承＋EMINEL-smartサーバーは独立デプロイの確認」内の設問「ただし既存システムを使い続けたほうがいい機能があれば教えてほしいです」）への報告 — 回答前に「既存システム」の指す対象の確認が必要。回答は「① 旧EMINEL: 現状のまま使い続ける価値のあるバッチはなし ・ ② e-smart: 4候補」の2部構成・3分冊共通。本グループからの候補は **管理画面ダウンロード／エクスポート機構**（§4.3 の経路①②） | §2 の「代替」に挙げた経路①②そのもの | SYP が QAデータベースの該当ページへ直接回答予定 |

## 付録A. ご参考: ESTA 調査資料（docs/eminel-smart/）と実コードの差異（本書関連3点）

コード照合の過程で、既存の ESTA 調査資料 `eminel_gw_project/docs/eminel-smart/`（6ファイル）と実コードの間に**計6点**の差異を確認した（全11本の調査全体での件数）。うち本書の記載内容に関わる3点を下表に示す — 残る3点（Push 配信の件数・基幹取込の周期・会員マージのロック分数）は配信・通知系／外部連携・受信系の各分冊に記載。同資料を引用する際は実コードの再確認を推奨したい（あわせて資料側の更新もご検討をお願いしたい）。

| 調査資料の記載 | 実コード |
|---|---|
| `CsvDownloadHistory` = 「CSVダウンロード履歴」→ 管理者ダウンロード履歴を示唆（`03_backend_models.md:107`） | **SFTP からの受信履歴**（二重取込防止）。管理者ダウンロードとは無関係（§4.3 の⚠️注記） |
| 「自動化ルール実行（毎分）」（`02_product_overview.md:85`） | 毎分実行はなし — ルール毎に週次スケジュールを動的生成（§3。grep `rate(`: 0件） |
| Lambda ランタイム「Node.js 20.x, arm64」（`02_product_overview.md:49`） | `Runtime: nodejs24.x`（`template.yaml:181`。なお共通レイヤーの CompatibleRuntimes は nodejs20.x のまま — 同:3163） |

## 付録B. 参照資料一覧

- **`legacy_eminel_docs`**（@ `ccd8f56`）: `docs/03_API仕様/04_バッチ一覧.md`、対象4コマンドのコード `sources/conciergesv-develop/src/Command/CreateCsvAndZip*Command.php`（4ファイル）＋ `CreateZipsTrait.php`＋`DeleteDataCommand.php`、cron: `docs/02_詳細設計/10_バッチ処理/*.txt`（`cron設定概要.txt`〔shell 構成と `set -eu` の説明〕・`mng-webap_cron設定_20241029.txt`〔cron 行〕。shell 本体は同フォルダ `cron実行用シェルスクリプト/eminel-mng-webap.20240909.tgz` 内）
- **`eminel_gw_project`**（@ `fbc0af0`。調査実施は `788b438` — 本グループの引用ファイルは両コミットで同一・§1 補足）: `docs/eminel/4_spec/admin/I_data_download.md`（spec [I]）、`2_management/20_open_issues.md`（SVC-03）、`3_requirements/00_integrated_requirements_v1.2.md`；判定前提: `2_management/22_decisions.md`（6/10 決定）、`2_management/minutes/20260625_egw_camp_day3.md`、`1_product/10_feature_list.md`；`docs/eminel-smart/`（ESTA 調査資料6ファイル — ⚠️ 実コードとの差異は付録A参照）
- **`syp-eminelstandard-backend`**（@ `dc39aa39`、branch `gw-syp-dev`）: `template.yaml`・`template-dynamodb.yaml`、`src/functions/api-download/**`・`batch-download/**`・`api-s3/**`、`src/layers/common/nodejs/**`（`upload-data-backup-to-sftp.ts`、`put-schedule.ts`、`models/CsvDownloadHistory.ts` 等）
- **`syp-eminelstandard-web-admin`**（@ `e550326`、branch `gw-syp-dev`）: `constants/common.ts`、`pages/other/data-management/index.vue`、`components/data-management/form-download-data-management.vue`・`list-download-data-management.vue`
- **QAデータベース（Notion）** — いずれも参照日 2026-08-04 時点で回答中。再引用時は原ページの最新状態の確認をお願いしたい: 「旧Eminel基盤継承＋EMINEL-smartサーバーは独立デプロイの確認」（回答者: swan（mui））・「旧EMINEL調査範囲（conciergesv/eminelsv）とhemssv対象外の確認」（回答者: swan（mui））・「管理画面は独立か共通か（切替モード追加）の確認」（回答者: masao takahashi（mui））
