# 旧EMINELバッチ移行判定報告書 — 外部連携・受信系（Xzilla取込）3本（#5〜#7）

## 1. 管理情報

| | |
|---|---|
| 作成日 | 2026-08-06（調査実施日: 2026-08-04） |
| 作成者 | Bui Trong Dat（SYP）＋AI調査支援 |
| 位置づけ | 本書は、旧EMINELバッチ移行判定（全11本・3グループ）を分冊化した**3分冊のうちの1冊**であり、**外部連携・受信系（Xzilla取込）3本（#5〜#7）** を対象とする。他分冊: 「配信・通知系4本（#1〜#4）」「CSV・ZIPエクスポート系4本（#8〜#11）」。バッチ番号 #1〜#11 は全11本の通し番号であり、分冊間および日本語版／ベトナム語版の間で共通 |
| 目的 | `legacy_eminel_docs/docs/03_API仕様/04_バッチ一覧.md` のうち **外部連携・受信系（Xzilla取込）** の3バッチ（いずれも旧システムの `conciergesv` 上で稼働）について、e-smart 既存実装の有無を実コードで確認し、`eminel_gw_project/docs/eminel` の E-GW 要件と照合のうえ **流用・新規・廃止** を判定する |
| 対象リポジトリ | `legacy_eminel_docs` @ `ccd8f56` ・ `eminel_gw_project` @ `fbc0af0`（調査実施は `788b438` 時点 — 差分の扱いは補足参照）・ `syp-eminelstandard-backend` @ `dc39aa39`（branch `gw-syp-dev`）・ `syp-eminelstandard-web-admin` @ `e550326`（branch `gw-syp-dev`）— いずれも 2026-08-06 時点の origin と一致 |
| 判定区分 | **流用** = e-smart の既存実装・機構を利用（工数ゼロの意ではない — §3）・ **新規** = E-GW 向けに新規実装 ・ **廃止** = 移植せず、既存機構または新方針で代替 |
| 凡例 | **確実** = 資料・コード上で直接確認済み ・ ***推定*** = 根拠ある推測（未確定 — 最終判断には使わない）・ 🔍 = 出典（パスは `sources/` 起点、行番号は上記コミット時点のもの）・「grep 0件」= 対象コード全体を検索してヒットなし |

補足（引用時の注意）:

- e-smart（= ESTA = EMINEL-Smart。同一システムの3呼称）に関する「有り／無し」の記述は、すべて `syp-eminelstandard-backend`・`syp-eminelstandard-web-admin`（branch `gw-syp-dev`）の実コードを直接確認した結果である。
- **`eminel_gw_project` の更新（788b438 → fbc0af0、6コミット、2026-08-03夜〜08-05夜）について**: 差分は `docs/eminel/3_requirements/app/` 配下13ファイル＋ skill ファイル1行のみであり、本書が引用する統合要件 v1.2・機能一覧・業務プロセス・未決事項・決定ログ・合宿議事録・ESTA調査資料（`docs/eminel-smart/`）には変更がないことを 2026-08-06 に確認済み。**本グループの判定・引用行番号への影響なし**（アプリ要件の変更による行番号のずれは配信・通知系分冊の引用箇所にのみ影響 — 当該分冊で対応）。
- QAデータベース（Notion）の引用3件は、いずれも参照日 2026-08-04 時点で**回答中**（スクリーンショット経由で参照）。再引用の際は原ページの最新状態の確認をお願いしたい。
- スコープ・要件の判定に用いた T.B.D／QA回答中の論点は本文の該当箇所に明記した。

## 2. 総括（結論）

### 2.1 判定結果一覧（外部連携・受信系 — 3本）

| # | バッチ | 旧システムでの処理 | e-smart 既存実装 | E-GW 要件 | **判定** | 詳細 |
|---|---|---|---|---|---|---|
| 5 | `RcvCntctCancellationCommand`（IF2249） | 5分毎に電力解約 CSV を受信し、買電売電の計算停止フラグを設定 | **同 IF なし**（grep 0件）。ただし SFTP→S3→DynamoDB の受信基盤（8 IF）＋契約失効の後処理はあり | 直接の要件なし。ただし計算停止フラグは #7 の前提（解約後の GW 無効化は管理画面の手動操作） | **旧バッチは廃止（コードは移植しない）— ただし「解約時に計算停止フラグを立てる」業務は存続させ、既存の Xzilla 取込フローへ統合。** IF-01（E-GW⇔Xzilla の新連携定義）に解約データがあればファイル種別追加で対応、なければ要件追加を提起（未決事項 CLD-07〔IF-01 の入出力・認証定義〕待ち） | §4.2 ・ 提案は*推定*、e-smart 側は確実 |
| 6 | `RcvEmsPlsCntrPayerCommand`（IF2264） | 5分毎に支払者マスタを全件削除→対象契約種別のみ再投入し、契約終了判定（3条件）を適用 | **同 IF なし**（grep 0件）。契約／顧客マスタ取込（IF2023/2024/DM1040）はあり — DM1040 は支払者ロールを抽出済み | 個別の要件なし。グルーピング（世帯グループ分け機能・必須 2026）に間接的に必要 | **旧バッチは廃止（コードと「5分毎全件入替え」方式は移植しない）— 支払者データは既存の契約取込チャネルの拡張で受け、契約終了判定3条件は業務スペックとして抽出・保存** | §4.3 ・ 提案は*推定*、e-smart 側は確実 |
| 7 | `RcvHalfHourElectricPowerCommand`（IF1156） | 10分毎に電力30分値（速報／確報）を受信、30分→1時間に集約し買電売電を計算 | **なし**（grep 0件）— e-smart の電力／ガスデータは TagTag（北ガスの会員基盤）API 経由 | **必要・明文・2026スコープ**（「電力30分値はCルート（Xzilla経由）で取得する」） | **新規** — e-smart 取込パターンに準拠、業務ロジックは旧コードから継承。11本中もっとも重量級 | §4.4 ・ 確実 |

**一覧の読み方（3点）**:

- **確実／*推定*** のラベルは**事実部分**（旧システムの挙動、e-smart の有無、スコープ）の確度を示す。「判定」列は常にレビュー用の提案である — 特に #5/#6 は推論の比重が大きいため *推定* を明示した。
- 本報告は「何を作る／何を流用する」の判定までであり、**工数は未見積**（方針どおり 1バッチ = 1タスクの Notion 分割時に見積り予定 — §3）。なお #7 は全11本の中でも業務的に最重量である。
- 受信方向のバッチ本数だけでタスクを数えないこと — **送信方向（e-smart → 基幹）の既存実装が1本ある**（§4.1 の `/EST` エクスポート）。Xzilla 系のタスク一覧作成時はこの送信方向を追加する必要がある。

### 2.2 スペック確定を待たず即時対応する3点

1. **SFTP エクスポート先 `/EST` の確認**（§4.1）: e-smart は毎日6種の機器 CSV を SFTP へ送信しているが、宛先が Xzilla/DWH かはコードから確認できない（接続先は secret 管理）→ mui 様へ確認をお願いしたい（§5-2）。F-ES-10（Xzilla連携）のうち「EMINELデータの共有」に直結する。
2. **CLD-07（Xzilla IF-01 の入出力定義）のフォロー**: #5〜#7 のすべてが IF-01 の確定に依存する。確定待ちの間に SYP が旧コードから必要フィールド一覧を準備する（#6 対応ステップ1、およびステップ2で突合する旧システム側フィールドの事前整理 — 即着手可能）。
3. **「既存システムを使い続けたほうがいい機能」リストへの回答（本グループ該当分）**: QA「旧Eminel基盤継承＋EMINEL-smartサーバーは独立デプロイの確認」（swan（mui）・回答中）への回答は「① 旧EMINEL: 現状のまま使い続ける価値のあるバッチはなし ・ ② e-smart: 4候補」の2部構成であり、本グループからは **Xzilla SFTP→S3→DynamoDB 受信基盤** が候補として該当する（回答対応自体は3分冊共通 — §5-3）。

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
| データベース | PostgreSQL（日／月パーティション） | DynamoDB（PITR = ポイントインタイムリカバリ有効） |
| バッチ実行方式 | サーバー cron（`/etc/cron.d/eminel-mng-webap`）＋ shell（flock 排他） | Step Functions + EventBridge Scheduler |
| 外部ファイル受信 | SFTP → サーバーディスク | SFTP → S3 → DynamoDB |

- 🔍 旧: `legacy_eminel_docs/docs/02_詳細設計/10_バッチ処理/cron設定概要.txt` 1–37 行（flock は同フォルダ `cron実行用シェルスクリプト/eminel-mng-webap.20240909.tgz` 内の各 `.sh` に記載）・ e-smart: `syp-eminelstandard-backend/template.yaml`（SAM）、`eminel_gw_project/docs/eminel-smart/02_product_overview.md` 48–53 行

**e-smart バッチ基盤の要点**（E-GW が継承する足回り。以下パスは `syp-eminelstandard-backend/` 起点）:

- **静的スケジュールは3本のみ**（いずれも `ScheduleV2`・timezone `Asia/Tokyo` — `template.yaml:9-11`）:
  - ① `BatchRunSequentiallyStateMachine` — 基幹データ取込、`cron(5 0-7 * * ? *)` = JST 0〜7時の毎時5分（`template.yaml:853-888`、cron は 881–882 行）
  - ② `BatchMigrationIntegratedDataStateMachine` — Rinnai／Noritz 機器データ取得＋エクスポート、`cron(0 8 * * ?)`（= 毎日 8:00 実行 — `template.yaml:2205-2240`、cron は 2233 行）
  - ③ `BatchGetErrorDeviceInfoOfRinnaiStateMachine` — 機器エラー取得、同 8:00（`template.yaml:2966-2980`）
  - 本グループの受信フローは①、送信方向は②に載っている。
- **それ以外のバッチはすべて EventBridge Scheduler のスケジュールを動的生成**する方式。大半は one-shot（一時点だけ発火し、`ActionAfterCompletion.DELETE` により実行後自動削除される単発スケジュール — 共通関数 🔍 `src/layers/common/nodejs/services/put-schedule.ts:18-33`）。例外はユーザーのオートメーション（アプリ内の機器自動化ルール）のみで、ルール毎の週次スケジュールを動的生成する（繰り返し型・自動削除なし — `src/functions/api-automation/common.ts:115, 167-175`）。
- **毎分ポーリングは存在しない**（grep `rate(`: 0件）— 旧システムの「5分毎／10分毎 cron」の移植先を考える際の前提となる。

**SYP の担当範囲**: QA「旧EMINEL調査範囲（conciergesv/eminelsv）とhemssv対象外の確認」（swan（mui）・回答中・2026-08-04参照）の要旨 — `conciergesv`/`eminelsv` は SYP の**調査**対象であり、旧システム上で開発を続ける範囲ではない。GW との通信は mui 開発の HEMS-SV（m2-cloud。旧システムの `hemssv` とは別物 — 名称が類似しているのみ）経由となり、スペックは後日共有予定。

**2026-06-10 のスコープ決定**（決定ログ登録済み）: 必須 = 暖房機能／暖房制御／照明アドバイス※／ポイント連携／グルーピング・レポート。劣後（2027/4〜）= 複合制御・DR・ダッシュボード・バッジ等。※「照明アドバイス」は省エネアドバイスの誤記と思われる（*推定*）。

- 🔍 `eminel_gw_project/docs/eminel/2_management/22_decisions.md` 30–31 行
- 機能一覧（`docs/eminel/1_product/10_feature_list.md`）の劣後列の凡例に注意: **✅ = 2027 へ繰越可**（スコープ内の意ではない）、空欄 = 今期必須。

**§4 の実施主体**: 特記のない限り実施者は **SYP**、実装は branch `gw-syp-dev` 上。リポジトリ名のないパスは `syp-eminelstandard-backend`。「確認／決着」系のステップは §5 の経路による。本文中の人名（敬称略）: swan・masao takahashi（いずれも mui — QAデータベース回答者）。

## 4. バッチ別判定詳細

（旧システムコードのパス表記 `…/src/Command/` は `legacy_eminel_docs/sources/conciergesv-develop/src/Command/` の略。「cron:NN行」は `legacy_eminel_docs/docs/02_詳細設計/10_バッチ処理/mng-webap_cron設定_20241029.txt` の行番号。）

### 4.1 グループ共通: 新旧の受信方式と e-smart 受信基盤

#### 旧システムの受信方式

Xzilla からの CSV を、5〜10分毎に SFTP 経由で中間サーバーへ取り込む:

```
Xzilla ──SFTP (5〜10分毎)──▶ [中間サーバーのディスク] ──▶ PHP Command (cron + flock) ──▶ [PostgreSQL]
                                                           · RcvCntctCancellation…  ──▶ ipf_cntct_cancellations + フラグ t_101.c065
                                                           · RcvEmsPlsCntrPayer…    ──▶ ipf_ems_pls_cntr_payers + t_101
                                                           · RcvHalfHourElectric…   ──▶ emn_all/emn_fast/emn_confirm + s_102
```

#### e-smart の受信方式（確実）

**SFTP → S3 → DynamoDB** のフロー:

```
Xzilla ──SFTP──▶ [SFTPサーバー: IFフォルダ8種 + END/*.dat]     (.dat = 「便」ごとの確定済みファイル一覧)
                   │
                   │ ① batch-get-list-file-name-from-sftp-server/
                   │    · .dat を読んでファイル一覧を取得 (app.ts:52-66)
                   │    · 二重取込防止: CsvDownloadHistory テーブル (app.ts:69-87)
                   ▼
                 [S3] 50,000行単位に分割                       ② batch-forward-csv-from-sftp-server-to-s3/ (app.ts:56-64)
                   ▼
                 ③ batch-ifXXXX-import-* ハンドラ8本 ──トランザクション書込──▶ [DynamoDB]
                   ·  IF2241 → DM1040 → IF2242 (直列)  ──────────▶ TABLE_KAIIN (会員テーブル)
                   ·  IF2016/2023/2024/2029/2223 (並列) ────────▶ チャネル毎の専用テーブル (TABLE_IF2016_SERVICE_POINT_NO_INFO…)
                   ▼
                 ④ 取込後処理3本 ①②③ (import 後の派生業務)
  ⏰ スケジュール: cron(5 0-7 * * ? *) = JST 0〜7時の毎時5分 — state machine batch_run_sequentially.asl.json
```

各段の詳細:

- **編成**: state machine `src/statemachine/batch_run_sequentially.asl.json`（多重起動防止 5–38 行 → temp 掃除 → ファイル一覧取得 → 8 IF 並列 forward → import → 後処理3本）。実行は **JST 0〜7時の毎時**（`cron(5 0-7 * * ? *)` — §3）。
- **SFTP 上の IF フォルダ一覧**はコード内に定義 — 🔍 `src/functions/batch-get-list-file-name-from-sftp-server/app.ts:149-169`: IF2241（TagTag会員）／DM1040（契約リスト）／IF2242（会員属性）／IF2016（供給地点）／IF2023（使用契約）／IF2024（顧客）／IF2029（建物）／IF2223（機器）。
- **各 IF の構成**: CSV フォルダ＋`END/` 内のメタデータ `.dat`（確定済みファイル一覧 — 同:52-66）。二重取込は `CsvDownloadHistory` テーブルで防止（同:69-87 — このテーブルの実際の役割。付録A参照）。
- **分割・書込**: ファイルは 50,000 行単位に分割して S3 へ（`batch-forward-csv-from-sftp-server-to-s3/app.ts:56-64`）、`batch-ifXXXX-import-*` ハンドラがトランザクションで DynamoDB へ書き込む。
- **最終的な格納先テーブル**（各 handler `app.ts` の `TABLE_*` 定数で確認）:
  - IF2241／IF2242／DM1040 → いずれも**会員テーブル `TABLE_KAIIN`** を段階的に構築（これが IF2241 → DM1040 → IF2242 を**直列**で取り込む理由）。
  - 後者5チャネルは各自専用テーブルのため並列取込が可能（asl 493–794 行）: IF2016 → `TABLE_IF2016_SERVICE_POINT_NO_INFO`（供給地点）、IF2023 → `TABLE_IF2023_USE_CNTR_INFO`（使用契約）、IF2024 → `TABLE_IF2024_CUSTOMER_INFO`（顧客）、IF2029 → `TABLE_IF2029_BUILDING_INFO`（建物）、IF2223 → `TABLE_IF2223_EQUIPMENT`（機器）。

**IF チャネル別の詳細**（1 IF = 1行 — 各チャネルの背後の DB を一覧するため）。フィールドは backend 実コードの interface（`src/layers/common/nodejs/interfaces/IData*.ts` — 実列を定義する enum `LIST_COL_*`〔`constants.ts:468-565`〕への mapped type — 一次ソース）に拠る。基幹側ソーステーブル＋ラベルは ESTA 調査資料の IF 表（`eminel_gw_project/docs/eminel-smart/02_product_overview.md:68-75`、`03_backend_models.md:90-97` と突合）に拠る — 両者が食い違う場合はコードを正とする（付録A参照）。括弧内の意味はフィールド名＋調査資料からの推読（明文ソースのない箇所は *推定* 扱い）。「x/y列」= コードが使う全 y 列中 x 列を抜粋の意:

| IF | 基幹側ソース | 主要フィールド（コードの interface より） | 格納先 DynamoDB テーブル | 業務上の役割 |
|---|---|---|---|---|
| IF2241 | `TAG_KAIIN`（TagTag会員） | 5/11列: `kaiinBango`（会員番号 — キー）、`custShikibetsuBango`（顧客識別番号）、`status`（会員ステータス）、`loginId`（ログインID）、`yubinBango`（郵便番号） | `TABLE_KAIIN`（調査資料では「KaiinTable + 16関連」— :73） | 会員アイデンティティの背骨 — アプリ会員↔北ガス顧客のマージの起点。IF2242/DM1040 は本チャネルの取込完了が前提（直列） |
| DM1040 | `MRT_TAGTAGAPI`（TagTag API） | 5/14列: `roles`（契約上のロール — 支払者抽出はここ）、`kaiinbango`（会員番号）、`oc_z_customer_no`（お客様番号）、`oc_j_supply_place_no`（供給地点番号）、`curd_flg`（追加/更新/削除フラグ） | `TABLE_KAIIN` — `list_contract` 配列 | 会員ごとの契約リスト — 会員↔契約・供給地点の紐づけ。支払者ロールが既にある（§4.3） |
| IF2242 | `tag_kaiinzokusei`（会員属性） | 3/3列: `kaiinBango`、`zokuseiId`（属性ID）、`kaitouCd`（回答コード） | `TABLE_KAIIN` — `list_zokusei` 配列 | 会員への属性（アンケート回答）付与 — コンテンツターゲティングの基盤 |
| IF2016 | `ipf_sp_history`（供給地点履歴） | 5/7列: `source_sp_num`（供給地点番号 — PK）、`reg_start_ymd`/`reg_end_ymd`（有効期間）、`cis_use_cntr_num`（CIS使用契約番号）、`use_type_code`（用途コード） | `TABLE_IF2016_SERVICE_POINT_NO_INFO` | 供給地点のマスタ — 地点↔使用契約の紐づけ |
| IF2023 | `ipf_use_cntr_history`（使用契約履歴） | 6/14列: `source_use_cntr_num`（使用契約番号 — PK）、`reg_start_ymd`（レコード有効開始）、`cntr_clsfy_code`（契約種別 — #5/#6 が抽出する PE/PG コード）、`cntr_start_ymd`/`cntr_end_ymd`（契約期間）、`cntr_watt`（契約容量） | `TABLE_IF2023_USE_CNTR_INFO` | 使用契約＋契約種別・契約期間 — 後処理③が契約失効の判定に読む |
| IF2024 | `ipf_cus_meigi`（顧客名義） | 5/8列: `source_cus_meigi_num`（顧客名義番号 — PK）、`links_cus_num`（連携顧客番号）、`sex`（性別）、`birth_yyyy`（生年）、`household_num`（世帯人数） | `TABLE_IF2024_CUSTOMER_INFO` | 顧客の人口統計属性 — ターゲティング・世帯統計向け |
| IF2029 | `ipf_bld`（建物） | 4/5列: `source_bldno`（建物番号 — 格納時に `bld_no` へ改名、`batch-if2029-import-building-info/app.ts:30`）、`bld_divcod_1`（建物種別）、`bld_use_type`（用途）、`newbldno_area`（エリア） | `TABLE_IF2029_BUILDING_INFO` | 建物情報 — グルーピング（必須 2026）が必要とする建物種別の供給元（§4.3） |
| IF2223 | `lnk_ot_pgedgkk`（所有機器） | CSV は 130項目超（`02_product_overview.md:72`）— コードが使うのは 13列。代表: `oc_z_gas_sp_no`（ガス供給地点 — PK `gas_sp_no` に）、`oc_j_gkiki_clsfy_code`＋`oc_h_estkk_mno`（連結して SK `equipment_code` に — `batch-if2223-import-equipment/app.ts:49`）、`oc_z_kiki_hinmok_code`（機器品目コード）、`oc_z_remove_date`（撤去日） | `TABLE_IF2223_EQUIPMENT` | 顧客宅に設置されたガス機器（保証・設置/撤去日付き）— 機器系機能のデータ基盤 |

- **「fake 会員」**（Xzilla データ到着前にアプリ登録した会員）のマージ時は **5分ロック**（`batch-if2241-import-tagtag-kaiin/app.ts:69, 102-111` — TTL（期限到来レコードの自動削除）で自動失効。39 本の API ハンドラが `src/layers/common/nodejs/business-logic/check-kaiin-updating.ts:10-15` でロックを確認）。

取込後処理は3本（図中④）:

- ① 新規会員への配信中コンテンツ再配信（`batch-send-contents-to-updated-user/app.ts:79-132`）
- ② ガス契約失効時の選択宅変更＋「ゆーぬっく」契約出現時のバッジ付与（「ゆーぬっく」はコード上 YUNUKKU・契約コード `PG003`、backend 定数上の名称は「ゆーぬっく２４ネオ」`constants.ts:1065`。処理箇所: `batch-update-selecting-place-no/app.ts:89-143, 283-296`、`constants.ts:1909`）
- ③ ガス契約終了時の連携・機器削除（`batch-remove-integration-expired/app.ts:44-79` — `TABLE_IF2023_USE_CNTR_INFO` から契約失効を読み取り、`TABLE_KAIIN`・`TABLE_MUI_DEVICE`・`TABLE_MUI_SENSOR` 上のデータを削除）

（後処理②の操作対象テーブルは `TABLE_KAIIN`＋`TABLE_IF2023_USE_CNTR_INFO` — いずれも handler 内の `TABLE_*` 定数で確認。）

#### 旧3 IF はいずれも e-smart に存在しない（確実）

backend 全体で grep `IF1156`・`IF2249`・`IF2264`・`30分`・`HalfHour`・`half_hour`・`速報`・`確報`・`electric_power`・`cntct` = **0件**。（camelCase の `ElectricPower` は `src/layers/common/nodejs/services/daikin.ts:73` — エアコンの瞬時消費電力プロパティ — に1件あるのみで、電力30分値とは無関係。`payer` は DM1040 取込の支払者ロール抽出定数としてのみ出現 — `batch-dm1040-import-user-contract-list-preprocessing/app.ts:54, 63` — 支払者情報が DM1040 フローで処理済みであることの傍証。）

#### 送信方向（e-smart → 基幹）`/EST` — 実在（確実）

```
[当日取得済みの機器データ] ──▶ BatchMigrationIntegratedDataStateMachine (毎日8:00 — template.yaml:2215-2226)
        ──▶ CSV 6種 (給湯器系5種 + 赤外線リモコン) ──SFTP・アップロード専用アカウント──▶ [/EST]  宛先 = Xzilla/DWH? ※推定（未確認）— mui様へ確認
```

詳細:

- **実コード** — 🔍 `src/layers/common/nodejs/services/upload-data-backup-to-sftp.ts:22-43, 52-57`: 機器データ CSV 6種（給湯器系5種＋赤外線リモコン）を**同一 SFTP サーバーの `/EST` フォルダ**へ、アップロード専用アカウントで毎日 8:00 に送信（`BatchMigrationIntegratedDataStateMachine` 内 — `template.yaml:2215-2226`）。
- *推定（未確認）*: `/EST` の宛先は Xzilla/DWH（分析用データ基盤）と思われるが、接続先は secret 管理でコードから確認できない → mui 様へ確認をお願いしたい（§5-2）。該当すれば F-ES-10（Xzilla連携）のうち「EMINELデータの共有」（送信方向）の既存実装となる（`00_integrated_requirements_v1.2.md:696`）。
- Xzilla 系のタスク一覧作成時は**この送信方向を追加**すること（旧バッチの本数だけで数えない）。
- なお合宿 Day3 議事録 126 行の見立て（アプリログの基幹への送信インターフェースも ESTA に既にある可能性）については、確認の結果、該当する実装は**なかった** — backend にアプリログの SFTP 送信経路はなく、管理画面ダウンロードのみ。

#### 新旧対応表

（本グループ範囲 — 各要素が新旧どこに位置するかの一覧。）

| 要素 | 旧システム（`conciergesv` — PHP/PostgreSQL） | 新システム（e-smart/E-GW — Lambda/DynamoDB） |
|---|---|---|
| Xzilla ファイル受信経路 | SFTP → 中間サーバーのディスク、5〜10分毎 cron | SFTP → S3 → DynamoDB、JST 0〜7時毎時（state machine `batch_run_sequentially.asl.json`） |
| 多重起動・二重取込の防止 | shell の `flock`（サーバー上のファイルロック） | asl 内の多重起動防止ブロック（5–38 行）＋ `CsvDownloadHistory` テーブルによる二重取込防止 |
| #5 電力解約データ | `ipf_cntct_cancellations` テーブル＋計算停止フラグ `t_101.c065` | *(将来 — IF-01 確定待ち)* 既存取込フローへのファイル種別追加＋取込後処理④で E-GW 側世帯レコードにフラグ設定（§4.2 ステップ2〜3） |
| #6 支払者マスタ | `ipf_ems_pls_cntr_payers` テーブル — 5分毎全件入替え | 専用テーブルなし — `TABLE_KAIIN`＋`TABLE_IF2023_USE_CNTR_INFO`／`TABLE_IF2024_CUSTOMER_INFO`（既存の契約系3チャネル。IF-01 に沿ってフィールド拡張 — §4.3 ステップ2） |
| #7 電力30分値 | `emn_all`／`emn_fast_electric_powers`（速報 — 全件入替え）＋`emn_confirm_electric_powers`（確報 — 追記蓄積）；1時間値は `s_102` へ | 速報／確報を分離した新テーブル（`template-dynamodb.yaml` に定義 — §4.4 ステップ3）；1時間値は集計系バッチグループへ接続 |
| スケジュール | サーバー上の固定 cron（`/etc/cron.d/eminel-mng-webap`） | 静的 `ScheduleV2` 3本＋動的生成の one-shot スケジュール（§3） |

### 4.2 #5 `RcvCntctCancellationCommand` — 電力解約受信（IF2249）

**バッチの目的**（まず位置づけ）: 基幹（Xzilla）側で発生した*電力契約の解約*を EMINEL 側へ同期する。役割は3つ — 解約情報の保存、解約済み顧客の**買電売電計算の停止**（止めないと解約日以降の数値が誤りになる）、当日データが揃った際の顧客情報登録完了通知 API の呼び出し。

**判定**（*推定*）: **バッチは廃止・業務は存続。**

- 廃止するのは旧バッチの PHP コードと「5分毎の専用バッチ」というアーキテクチャ。
- 「解約時に買電売電の計算を止める」という業務そのものは残す — E-GW が 30分値から買電売電を計算する以上（実際に計算する — #7 電力30分値受信）、この仕組みがないと解約済み顧客の計算が続いてしまう。
- 実現は新規バッチではなく、既存の Xzilla 取込フローへのファイル種別追加＋取込後処理として行う（対応ステップ2〜3）。
- （業務フロー上の手動対応が定めるのは GW 無効化のみで、計算停止には触れていない。）

*提案理由*（下記の事実の要約）:

- e-smart に **IF2249 はない**（grep 0件 — §4.1）が、Xzilla SFTP→S3→DynamoDB の受信基盤（8 IF）と取込後処理の定位置は**既にある** — ファイル種別1種の追加で載せられる。
- 合宿 Day3 の方針（§3）: 現行バッチは「いけてない」— 作り直しが前提であり、PHP コードは移植しない。
- 「計算停止フラグ」の業務は #7 の買電売電計算が前提とするため必須であり、手動フロー（管理画面での GW 無効化）ではカバーされない → バッチは廃止し、業務は既存フローへ統合する。

**旧システム**（確実）— フロー:

```
[cron 5分毎] ──▶ RcvCntctCancellationCommand.php
    │ ① SFTP で当日の解約 CSV を取得
    │ ② 契約種別 PE624/625 を抽出 (:242-243)
    ▼
[PostgreSQL] upsert ──▶ ipf_cntct_cancellations
    │ ③ 計算停止フラグ設定: t_101.c065 = 1 (:306-334)
    ▼
    ④ 当日分の IF2264 取込が完了している場合のみ ──▶ 顧客情報登録完了通知API を呼出 (:193-217)
```

キーコード抜粋（②の抽出条件）— 🔍 `…/src/Command/RcvCntctCancellationCommand.php:242-245`:

```php
// 契約種別が'PE624'または'PE625'以外は、登録しない
if ($line[58] != 'PE624' && $line[58] != 'PE625') {
    continue;
}
```

旧システムの詳細:

- 5分毎に当日 CSV を SFTP 取得。契約種別 PE624/625 を抽出（:242-243）。
- `ipf_cntct_cancellations` へ upsert（あれば更新・なければ追加）。
- 解約顧客の**買電売電の計算停止フラグ**（`t_101.c065=1`）を設定する。
- 当日分の場所契約支払者情報（IF2264）の取り込みが完了している場合のみ、顧客情報登録完了通知 API を呼び出す。
- 🔍 `…/src/Command/RcvCntctCancellationCommand.php:30, 99-113, 193-217, 242-243, 306-334` ・ cron:107-108

**E-GW 要件**: 解約の自動連携に個別要件はなし。業務フロー上、解約後の GW 無効化は**管理画面での手動操作**と明記。IF-01 は未決（CLD-07 — 要確認 約10項目）。🔍 `docs/eminel/1_product/11_business_process/readme.md:938-941, 945-952` ・ `20_open_issues.md:181-182`

**新アーキテクチャでの流れ（提案 — 上記判定の実現形）**:

```
IF-01 (CLD-07 確定待ち) ──▶ 既存受信フロー (§4.1) + ファイル種別1種を追加
        ▼
   新規 import handler ──▶ [DynamoDB] 解約テーブル (IF-01 に沿って設計)
        ▼
   取込後処理④ ──▶ E-GW 側世帯レコードに「計算停止」フラグ設定 ──▶ #7 が買電売電計算時に参照
```

**対応ステップ**:
  1. CLD-07（未決事項「E-GW⇔Xzilla 連携 IF-01 の入出力・認証定義」）／IF-01（新アーキテクチャの IF一覧〔統合要件 v1.2 §4-1〕の1番 — 北ガスクラウド経由で Xzilla データを受け取る窓口）が具体化した時点で、解約データフローの有無を確認する。**なければ即座に CLD-07／QAデータベース（mui との内部QA）経由で要件追加を提起**する。
     - 理由: #7（電力30分値受信バッチ）が計算停止フラグを前提とするため、要件化しないまま廃止すると解約済み顧客の買電売電が計算され続ける。手動フロー（管理画面での GW 無効化）は計算停止をカバーしない。
  2. 解約データフローがある場合: 5分毎の専用バッチは作らない — 既存取込フローへの IF（Xzilla とのファイル授受チャネル）追加として実装する。対象コード（§4.1 の既存8 IF パターンどおり）:
     - `src/functions/batch-get-list-file-name-from-sftp-server/app.ts`（SFTP 上のファイル一覧を取得する Lambda）: `DEFAULT_FOLDER_CSV`／`DEFAULT_FILE_NAME_METADATA` へ新 IF のフォルダ定義を追加
     - `src/layers/common/nodejs/variables/constants.ts`（全 Lambda 共通の定数レイヤー）: `LIST_COL_*` 列定義を追加＋`src/layers/common/nodejs/interfaces/` に新 IF のデータ interface を追加（雛形: `IDataIF2016.ts`）
     - `src/statemachine/batch_run_sequentially.asl.json`（Step Functions のフロー定義）: forward の Map 分岐（並列処理ブロック）を追加
     - 新規 Lambda handler `src/functions/batch-ifXXXX-import-*/` — 雛形は `batch-if2016-import-service-point-no/`（IF2016〔供給地点情報チャネル〕の handler。単純 Put のみの最小構成）
     - 理由: 旧の5分周期は旧アーキテクチャ上の擬似リアルタイムであり、解約業務に必須ではない。既存フローに載せることで二重取込防止（`CsvDownloadHistory`）・多重起動防止・50,000行分割を追加実装なしで継承できる。
  3. 「計算停止」の業務ロジック: 取込後処理④として実装 — §4.1 の既存後処理3本（`batch-send-contents-to-updated-user/`・`batch-update-selecting-place-no/`・`batch-remove-integration-expired/`、いずれも `src/functions/` 配下）と並列の新 Lambda とし、該当世帯レコードにフラグを設定する。
     - 理由: 「import 完了後に派生業務を適用する」定位置が既にこの後処理群であり、同じ場所に置くことで構成の一貫性を保てる。e-smart の 0〜7時毎時ウィンドウで解約業務には十分と考える（*推定* — IF-01〔前述の Xzilla 連携窓口〕の内容確定時に業務側と要確認）。
  4. テスト: PE624/625（旧バッチが抽出対象とする電力の契約種別コード）有無のダミー CSV。停止フラグが #7（電力30分値受信）の買電売電計算に反映されることを確認。
     - 理由: 本バッチの実リスクは「契約種別の抽出誤り」と「フラグが #7 へ伝播しない」の2点に集約されるため。

### 4.3 #6 `RcvEmsPlsCntrPayerCommand` — 支払者マスタ受信（IF2264）

**バッチの目的**: 基幹の支払者マスタ（どの契約の料金を誰が支払うかの一覧）を EMINEL 側で常に最新に保ち、契約終了判定を適用して連携番号・計算停止フラグを更新する — 電力データを正しい顧客・契約に紐づけ、終了済み契約を処理対象から外すため。

**判定**（*推定*）: **バッチは廃止・データと業務知識は引き継ぐ。**

- 廃止するのは「5分毎に全件削除→再投入」という旧実装（「いけてない」の典型）。
- 支払者データ自体は E-GW でも必要（グルーピング〔世帯のグループ分け機能・必須 2026〕向け）であり、e-smart が既に毎日受信している契約系3チャネル — IF2023（使用契約）・IF2024（顧客）・DM1040（契約リスト — 支払者ロール抽出済み）— を IF-01（E-GW⇔Xzilla の新連携定義）に沿って拡張して受ける（対応ステップ2）。
- 契約終了判定3条件は業務スペックとして抽出・保存する（対応ステップ1）。

*提案理由*（下記の事実の要約）:

- e-smart に **IF2264 はない**（grep 0件 — §4.1）が、契約・顧客データは IF2023/IF2024/DM1040 で**既に毎日受信済み** — DM1040 は支払者ロールも抽出済み。
- 「5分毎全件入替え」（memory_limit 4096M を要した処理）は、方針（§3）が作り直し対象とする「いけてない」の典型。
- E-GW に「payer」の個別要件はなく、実需はグルーピング（必須 2026）向けの契約情報 — 既存3チャネルの拡張で賄える（不足分のみ IF-01 へ追加要請）。
- 契約終了判定3条件は廃止予定コードのコメントにしか存在しない → 抽出しなければ業務知識ごと消える。

**旧システム**（確実）— フロー:

```
[cron 5分毎] ──▶ RcvEmsPlsCntrPayerCommand.php   (memory_limit 4096M — :63)
    │ ① ipf_ems_pls_cntr_payers を全件 DELETE (:170-177)
    │ ② CSV から再投入 — 契約種別 PE624/625/650/651/652・PG077/079 のみ (:319-329)
    ▼
    ③ 契約終了判定 3条件を適用 (スペックはコメント :373-385)
    ▼
[PostgreSQL] t_101 を更新 (連携番号 + 計算停止フラグ)
```

キーコード抜粋（③のスペック — 対応ステップ1で抽出する「1ページのスペック」の原文コメント）— 🔍 `…/src/Command/RcvEmsPlsCntrPayerCommand.php:373-385`:

```php
/*
 * ＜契約終了判定の仕様について＞
 * 契約終了を判定するポイントは以下の３つ
 * 　① サービスポイント＿適用終了年月日が99991231以外
 * 　② 契約終了年月日が99991231以外
 * 　③ 契約種別が電気（PE624またはPE625）の場合に供給地点特定番号またはIPF使用契約番号がNULL
 * ...
 */
```

（`99991231` = 9999-12-31、「終了日未設定」を表す慣用値。グルーピングの考え方と更新動作の説明部分 — 380–384 行 — は `...` で省略。）

旧システムの詳細:

- 5分毎。`ipf_ems_pls_cntr_payers` を**全件削除のうえ、対象契約種別（PE624/625/650/651/652・PG077/079）のみ再投入**（除外条件 :319-329、memory_limit 4096M — :63）。
- **契約終了判定（3条件）** — スペックがコード内コメントに記載（:373-385 — 上記抜粋）— を適用し、`t_101` の連携番号・計算停止フラグを更新。
- 🔍 `…/src/Command/RcvEmsPlsCntrPayerCommand.php:63, 170-177, 245-363, 371-626` ・ cron:105-106

**E-GW 要件**: `docs/eminel` 全体に「payer」の個別機能なし（grep 済み）。最も近い範疇は F-ES-10（Xzilla連携）のうち「顧客情報・契約情報の取得」。グルーピング（必須 2026）は建物種別（Xzilla より取得と明記 — :619）のほか、料金メニュー・アンペア数等の契約情報を必要とする（これらは F-ES-10 の契約情報取得で賄われる想定 — :692-696）。🔍 `00_integrated_requirements_v1.2.md:415, 619, 692-696`

**新アーキテクチャでの流れ（提案 — 上記判定の実現形）**:

```
IF2023/IF2024/DM1040 (毎日稼働中) ──▶ [DynamoDB] TABLE_KAIIN・TABLE_IF2023_USE_CNTR_INFO・TABLE_IF2024_CUSTOMER_INFO
        │  + IF-01 に沿ってフィールド拡張 (支払者4フィールドに不足があれば)
        ▼
   新規後処理: 契約終了判定スペックを適用 (ステップ1で抽出)
```

**対応ステップ**:
  1. **旧コードのコメントから契約終了判定3条件（契約をいつ終了扱いとするかの業務ルール）を1ページのスペックに抽出する**（出典: `RcvEmsPlsCntrPayerCommand.php:373-385` — `legacy_eminel_docs` リポジトリ、CakePHP の Command 層）— IF-01（E-GW⇔Xzilla の新連携定義。内容は未決事項 CLD-07 で確定待ち）を待たず即着手可能。
     - 理由: このスペックは廃止予定コードのコメントにしか存在せず、抽出しなければ業務知識ごと消える。#6 の作業で唯一 IF-01 に依存しない。
  2. IF-01（前述の新連携定義）の具体化時: 旧システムが使う支払者フィールド（供給地点特定番号、IPF使用契約番号、受電地点特定番号、お客様番号）と、e-smart が既に受信している3チャネル — IF2023（使用契約 — handler `src/functions/batch-if2023-import-contract-info/`）・IF2024（顧客 — `batch-if2024-import-user-info/`）・DM1040（契約リスト — `batch-dm1040-import-user-contract-list/`。支払者ロール抽出は preprocessing の `batch-dm1040-import-user-contract-list-preprocessing/app.ts:54, 63`）— のデータを突合し、不足フィールドのみ IF-01 への追加を要請する（不足がなければ支払者専用 IF は要求しない）。
     - 理由: 既存3チャネルで賄えるなら支払者専用 IF を新規定義する必要がなくなり、北ガス様と交渉すべき IF-01 の範囲を最小化できる。
  3. 不足分を既存の契約取込ハンドラの拡張として実装（`src/layers/common/nodejs/variables/constants.ts` の列定義＋`src/layers/common/nodejs/interfaces/` の対応 interface＋handler 処理の追加）、ステップ1で抽出した契約終了判定スペックを後処理として適用。
     - 理由: 旧方式（5分毎の全件削除→再投入）を持ち込まないため。既存フローの拡張ならファイル到着単位の差分更新となり、全件入替え（メモリ 4096M を要した処理）が不要になる。
  4. テスト: 契約終了判定3条件 ×（成立／不成立）のダミーデータ。フラグ・連携番号の結果を旧ロジックの手動実行と突合。
     - 理由: 契約終了判定は本バッチ最大の派生ロジックであり、旧実装との突合だけがスペック抽出の正しさを立証できる。

### 4.4 #7 `RcvHalfHourElectricPowerCommand` — 電力30分値受信（IF1156）

**バッチの目的**: 基幹（Xzilla）から届く電力30分値（スマートメーター計測）を EMINEL に取り込み、世帯ごとの買電・売電を1時間値に集約・計算する — アプリのグラフ・レポートが表示するエネルギーデータの供給源であり、本グループで業務上もっとも重要かつ重量級のバッチ。

**判定**（確実）: **新規** — 全11本中もっとも業務量の重いバッチ。

*提案理由*（下記の事実の要約）:

- E-GW 要件は**明文・2026 スコープ**: 「電力30分値はCルート（Xzilla経由）で取得する」— 廃止は選択肢にない。
- e-smart に Xzilla 経由の 30分値の実装は**一切ない**（grep 0件 — §4.1）。電力／ガスデータは TagTag API 経由であり、そのまま流用できる実装がない。
- 旧 PHP/CakePHP コードは Lambda/TypeScript スタックでは動かない → e-smart 取込パターン（§4.1）で新規実装し、業務ロジックのみ旧コードから継承する。

**旧システム**（確実）— フロー:

```
[cron 10分毎] ──▶ RcvHalfHourElectricPowerCommand.php
    │ ① 速報値: emn_all / emn_fast_electric_powers を全件入替え (:449-583)
    │ ② 確報値 (fixed_div=1): emn_confirm_electric_powers へ追記 (:591-725)
    ▼
    ③ 2×30分 → 1時間値へ集約; 世帯の設備構成で分岐 (太陽光/コージェネ/受電地点特定番号 — :875-893)
    ▼
[PostgreSQL] 1時間値 ──▶ s_102 ──▶ グラフ / レポート
```

キーコード抜粋（③の分岐条件 — 売電量の算出元の決定）— 🔍 `…/src/Command/RcvHalfHourElectricPowerCommand.php:875-882`:

```php
// 【売電量算出条件①】GWからの計測データによる売電量算出条件
$calcFromGw = $record['has_solar_cell'] == 1;
// 【売電量算出条件②】Xzillaからの30分電力量データによる売電量算出条件
$calcFromXzilla = (
    $record['has_solar_cell'] != 1 &&
    $record['gas_cogeneration'] == 1 &&
    !empty($record['juden_point_number'])
);
```

旧システムの詳細:

- 10分毎。`emn_all`／`emn_fast_electric_powers` を全件入替えして速報値を再登録し、確報値（fixed_div=1）は `emn_confirm_electric_powers` へ追記登録する。
- その後 **買電売電を計算**: 30分値のペアを1時間値へ集約し `s_102` へ書き込む。
- 分岐条件（上記抜粋）: 太陽光あり世帯 → 売電は GW 計測値から（日次蓄積バッチが担当）、コージェネかつ受電地点特定番号あり → Xzilla 値から計算。
- 🔍 `…/src/Command/RcvHalfHourElectricPowerCommand.php:107-122, 192-233, 449-583, 591-725, 734-1050`（分岐条件 875–893 行）・ cron:109-110

**e-smart**: **なし**（確実）— grep 0件（§4.1）。e-smart の電力／ガス使用量データは TagTag API 経由（`eminel_gw_project/docs/eminel-smart/02_product_overview.md:119`）。

**E-GW 要件**: **必要・明文・2026 スコープ**: 「電力30分値はCルート（Xzilla経由）で取得する」（統合要件 3-2 節）。F-ES-10（Xzilla連携）が速報値・確報値の取得を定義。グラフ（F-ES-01）、グルーピング・レポート（必須）のデータ源。機能一覧の「連携テスト(Xzilla/TagTag)」行は ✅ なし = 今期。🔍 `00_integrated_requirements_v1.2.md:84, 692-696` ・ `10_feature_list.md:148`

**新アーキテクチャでの流れ（提案 — ステップ番号は下記「対応ステップ」に対応）**:

```
IF-01 30分値 (形式/周期/認証 — ステップ1) ──▶ SFTP→S3→新規 handler (ステップ2; 高頻度なら専用 ScheduleV2)
        ▼
[DynamoDB] 速報テーブル (上書き) / 確報テーブル (追記蓄積) — template-dynamodb.yaml (ステップ3)
        ▼
   計算 Lambda: 2×30分→1時間の集約 + 買電/売電条件表を設置9パターンへ再マッピング (ステップ4) + #5 の計算停止フラグ反映
        ▼
   集計系バッチグループ (グラフ/グルーピング/レポート)
```

**対応ステップ**:
  1. 30分値に関する IF-01（E-GW⇔Xzilla の新連携窓口 — IF一覧〔統合要件 v1.2 §4-1〕の1番）の確定: ファイル形式、提供周期（旧: 10分毎）、認証方式（未決事項 CLD-07 — IF-01 の入出力・認証定義そのもの）。
     - 理由: ステップ2〜3の設計はこの3点に全面依存する。特に周期は、e-smart 基盤が現状 0〜7時ウィンドウのみのため準リアルタイム提供が新規要素となり、北ガス様との合意が必要。
  2. §4.1 の取込パターンで受信経路を構築: `src/functions/batch-get-list-file-name-from-sftp-server/`（ファイル一覧取得）→ `batch-forward-csv-from-sftp-server-to-s3/`（S3 転送）→ 新規 import handler（`src/functions/` 配下に新設）。周期が 0〜7時ウィンドウより高頻度なら、`BatchRunSequentially`（毎時実行の基幹取込 state machine — §3）へ相乗りせず、`template.yaml`（SAM のインフラ定義）に専用の `ScheduleV2`（EventBridge 静的スケジュール）を新設する。
     - 理由: `BatchRunSequentially` は多重起動防止付きの直列実行であり、高頻度フローを同居させると既存8 IF の取込全体を詰まらせる。専用スケジュールにすれば障害影響も分離できる。
  3. 30分値用の DynamoDB テーブル設計（`template-dynamodb.yaml` に定義追加）: 速報値（上書き）／確報値（確定・追記蓄積）を分離 — 旧 `emn_fast/confirm_electric_powers` 相当。生データの TTL（期限到来レコードの自動削除）は保持期間（SVC-03 — 新システムの保持期間・バックアップ方針が未定義という未決事項）に従い検討。
     - 理由: 速報は常時上書き、確報は課金・レポートの確定根拠として不変保持 — 性質が正反対であり、混在させると確報の履歴喪失か速報の無限肥大を招く。旧システムも同じ理由で分離している（速報 :449-583・確報 :591-725）。
  4. **業務ロジックの継承**（コードの移植ではない）: 「30分×2 → 1時間値」の集約規則、世帯の設備構成による買電／売電の計算条件表（太陽光／コージェネ／受電地点特定番号 — 出典: 旧コード 875–893 行）を、**E-GW の設置9パターン**（宅内の機器組み合わせ9類型 — 統合要件 v1.2 の 3-5 節定義）に再マッピングする。
     - 理由: PHP/CakePHP 実装は Lambda/TypeScript スタックで動かないが、分岐条件そのものは長年商用運用された業務知識であり保存価値が高い。E-GW の設置9パターンは旧の機器構成と一致しないため、分岐追加の可能性あり。
  5. 出力を集計系バッチグループ（グラフ／グルーピング／レポートを算出する別グループ — 本報告対象外）へ接続＋ #5（電力解約受信）の計算停止フラグを反映。
     - 理由: #7 は「原データの入口」であり、集計系が消費して初めて価値になる。停止フラグをここで適用しないと解約済み顧客の計算が続いてしまう（#5 の判定の前提）。
  6. テスト: 全分岐（太陽光／コージェネ／通常、速報→確報の上書き、30分ペアの欠損）を網羅するダミー30分値一式 — 1時間値の結果を旧ロジックの手動実行と突合。
     - 理由: 設備構成の分岐は旧実装で最も複雑な箇所（:734-1050）であり、漏れた分岐はそのままその構成の顧客の数値誤りになる。

## 5. ご確認・ご相談事項（一覧）

| # | 事項 | 関連 | 対応・経路 |
|---|---|---|---|
| 1 | IF-01（E-GW⇔Xzilla の新連携窓口）の入出力＋認証の定義 — 未決事項 CLD-07 の決着。**送信方向**（「EMINELデータの共有」= E-GW から基幹へのデータ提供）も含む | 本分冊の3バッチすべての前提 — #5 解約受信・#6 支払者マスタ・#7 電力30分値（詳細 §4） | 北ガス様のご回答待ち（mui の PM 様経由）。待機中に SYP が旧コードから必要フィールド一覧を準備（#6 対応ステップ1の契約終了判定スペック抽出＋ステップ2で突合する支払者4フィールドの事前整理） |
| 2 | **SFTP `/EST` の宛先確認**: e-smart が毎日 8:00 に機器 CSV 6種を送信している先が Xzilla/DWH（分析用データ基盤）か（接続先は secret 管理のためコードから確認不可） | §4.1 末尾の送信方向（e-smart → 基幹）の既存実装＋即時対応1点目（§2.2-1） | mui 様にご確認をお願いしたい（QAデータベース、または HEMS-SV スペック共有時） |
| 3 | 「既存システムを使い続けたほうがいい機能」リスト（QA 独立デプロイ内の設問）への報告 — 回答は「① 旧EMINEL: 現状のまま使い続ける価値のあるバッチはなし ・ ② e-smart: 4候補」の2部構成・3分冊共通。本グループからの候補は **Xzilla SFTP→S3→DynamoDB 受信基盤** | 即時対応3点目（§2.2-3） | SYP が QAデータベースの該当ページへ直接回答予定 |

## 付録A. ご参考: ESTA 調査資料（docs/eminel-smart/）と実コードの差異（本書関連5点）

コード照合の過程で、既存の ESTA 調査資料 `eminel_gw_project/docs/eminel-smart/`（6ファイル）と実コードの間に計6点の差異を確認した。うち本書に関連する5点を以下に示す（残る1点 — Push 配信の件数 — は配信・通知系分冊に記載）。同資料を引用する際は実コードの再確認を推奨したい（あわせて資料側の更新もご検討をお願いしたい）。

| 調査資料の記載 | 実コード |
|---|---|
| 基幹取込「日次・深夜〜早朝」（`02_product_overview.md:30, 63-64`） | `cron(5 0-7 * * ? *)` — JST 0〜7時の**毎時**実行（§3） |
| 会員マージのロック「6分」（`02_product_overview.md:73, 78`） | `UPDATE_LOCK_TTL_MINUTES = 5`（§4.1） |
| `CsvDownloadHistory` = 「CSVダウンロード履歴」→ 管理者ダウンロード履歴を示唆（`03_backend_models.md:107`） | **SFTP からの受信履歴**（二重取込防止）。管理者ダウンロードとは無関係（§4.1） |
| 「自動化ルール実行（毎分）」（`02_product_overview.md:85`） | 毎分実行はなし — ルール毎に週次スケジュールを動的生成（§3。grep `rate(`: 0件） |
| Lambda ランタイム「Node.js 20.x, arm64」（`02_product_overview.md:49`） | `Runtime: nodejs24.x`（`template.yaml:181`。なお共通レイヤーの CompatibleRuntimes は nodejs20.x のまま — 同:3163） |

## 付録B. 参照資料一覧

- **`legacy_eminel_docs`**（@ `ccd8f56`）: `docs/03_API仕様/04_バッチ一覧.md`、3 コマンドのコード `sources/conciergesv-develop/src/Command/`（`RcvCntctCancellationCommand.php`・`RcvEmsPlsCntrPayerCommand.php`・`RcvHalfHourElectricPowerCommand.php`）、cron: `docs/02_詳細設計/10_バッチ処理/*.txt`
- **`eminel_gw_project`**（@ `fbc0af0`。調査実施は `788b438` — 本グループの引用ファイルは両コミットで同一）: `docs/eminel/` — 統合要件定義書 v1.2（3-2 節、F-ES-01/10）、`1_product/10_feature_list.md`、`1_product/11_business_process/readme.md`、`2_management/22_decisions.md`（6/10 決定）、`2_management/20_open_issues.md`（CLD-07、SVC-03）、合宿 Day3 議事録；`docs/eminel-smart/`（ESTA 調査資料6ファイル — ⚠️ 実コードとの差異は付録A参照）
- **`syp-eminelstandard-backend`**（@ `dc39aa39`、branch `gw-syp-dev`）: `template*.yaml`、`src/functions/**`、`src/layers/common/nodejs/**`、`src/statemachine/*.asl.json`
- **`syp-eminelstandard-web-admin`**（@ `e550326`、branch `gw-syp-dev`）: E-GW コミット有無の確認（`git log`）のみ
- **QAデータベース（Notion）** — いずれも参照日 2026-08-04 時点で回答中。再引用時は原ページの最新状態の確認をお願いしたい: 「旧Eminel基盤継承＋EMINEL-smartサーバーは独立デプロイの確認」（回答者: swan（mui））・「旧EMINEL調査範囲（conciergesv/eminelsv）とhemssv対象外の確認」（回答者: swan（mui））・「管理画面は独立か共通か（切替モード追加）の確認」（回答者: masao takahashi（mui））
