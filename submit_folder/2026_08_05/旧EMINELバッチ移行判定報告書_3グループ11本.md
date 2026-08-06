# 旧EMINELバッチ移行判定報告書 — 配信・通知系／外部連携・受信系（Xzilla取込）／CSV・ZIPエクスポート系（全11本）

## 1. 管理情報

| | |
|---|---|
| 作成日 | 2026-08-05（調査実施日: 2026-08-04） |
| 作成者 | Bui Trong Dat（SYP）＋AI調査支援 |
| 目的 | `legacy_eminel_docs/docs/03_API仕様/04_バッチ一覧.md` のうち **配信・通知系／外部連携・受信系（Xzilla取込）／CSV・ZIPエクスポート系** の3グループ・計11バッチ（いずれも旧システムの `conciergesv` 上で稼働）について、e-smart 既存実装の有無を実コードで確認し、`eminel_gw_project/docs/eminel` の E-GW 要件と照合のうえ **流用・新規・廃止** を判定する |
| 対象リポジトリ | `legacy_eminel_docs` @ `ccd8f56` ・ `eminel_gw_project` @ `788b438` ・ `syp-eminelstandard-backend` @ `dc39aa39`（branch `gw-syp-dev`）・ `syp-eminelstandard-web-admin` @ `e550326`（branch `gw-syp-dev`）・ `syp-eminelstandard-app-syp-dev`（snapshot・git管理外）— いずれも調査時点の origin と一致 |
| 判定区分 | **流用** = e-smart の既存実装・機構をそのまま利用 ・ **新規** = E-GW 向けに新規実装 ・ **廃止** = 移植せず、既存機構または新方針で代替 |
| 凡例 | **確実** = 資料・コード上で直接確認済み ・ ***推定*** = 根拠ある推測（未確定 — 最終判断には使わない）・ 🔍 = 出典（パスは `sources/` 起点、行番号は上記コミット時点のもの）・「grep 0件」= 対象コード全体を検索してヒットなし |

補足（引用時の注意）:

- e-smart（= ESTA = EMINEL-Smart。同一システムの3呼称）に関する「有り／無し」の記述は、すべて `syp-eminelstandard-backend`・`syp-eminelstandard-web-admin`（branch `gw-syp-dev`）の実コードを直接確認した結果である。
- app リポジトリのみ snapshot（git 管理外）のため、アプリ側の行番号は新版で変動しうる。
- QAデータベース（Notion）の引用3件は、いずれも参照日 2026-08-04 時点で**回答中**（スクリーンショット経由で参照）。再引用の際は原ページの最新状態の確認をお願いしたい。
- スコープ・要件の判定は `eminel_gw_project` @ `788b438` 時点の資料に基づく（T.B.D／QA回答中の論点は本文の該当箇所に明記）。

## 2. 総括（結論）

### 2.1 判定結果一覧

#### 配信・通知系（4本）

| # | バッチ | 旧システムでの処理 | e-smart 既存実装 | E-GW 要件 | **判定** | 詳細 |
|---|---|---|---|---|---|---|
| 1 | `DistributeMonthlyEcoPointsCommand` | 月次で「設定温度の月平均 ≤22℃」の世帯に 250 ポイント付与（PointInfinity 連携） | **一部あり** — ポイント／バッジ基盤＋PointInfinity 直接連携は実装済み。計測データからの判定ロジックはなし | 必要（F-ES-04/09。必須 2026 — 劣後との矛盾は質問表（送付前）・質問2に記載済み） | **ポイント基盤＋PI連携は流用、エコ暖房判定ロジックのみ新規** | #1 ・ 確実 |
| 2 | `PublishRegularEcoMissionsCommand` | 19種の省エネアドバイスを判定条件付きで配信（季節固定 cron） | **なし**（grep 0件）— Tip は管理者が手動作成するコンテンツのみで、判定エンジンはなし | 必要・2026スコープ（F-ES-03 必須） | **新規** — 判定エンジン＋管理画面からのスケジュール設定（spec [G]。15種→7種の集約は CLD-06 未決） | #2 ・ 確実 |
| 3 | `DispatchPushMessagesCommand` | 毎分、DB キューから中継サーバー（PushCore）経由で FCM 配信 | **あり（完備）** — FCM 直接送信＋トークン管理＋Push 配信6系統 | 必要（Push 2026） | **旧バッチ廃止、e-smart の Push 基盤を利用**。旧システムは通知種別の棚卸しにのみ参照 | #3 ・ 確実（PushCore→FCM 転送のみ*推定*） |
| 4 | `ControlDrOperationCommand` | 毎分、DR 指令をユーザー操作に見せかけて DB へ書き込み、GW がポーリング取得 | **別方式の DR 基盤あり** — メーカークラウド直結機器をサーバー主導で制御。GW 経由の経路はなし | 必要だが**劣後（2027/4 以降）** | **2026年は実装なし**（「GW が DR 状態を保持するか」のみ要決着 — 質問表・質問5）。2027年に e-smart DR 基盤上で新規 | #4 ・ 確実 |

#### 外部連携・受信系（Xzilla取込 — 3本）

| # | バッチ | 旧システムでの処理 | e-smart 既存実装 | E-GW 要件 | **判定** | 詳細 |
|---|---|---|---|---|---|---|
| 5 | `RcvCntctCancellationCommand`（IF2249） | 5分毎に電力解約 CSV を受信し、買電売電の計算停止フラグを設定 | **同 IF なし**（grep 0件）。ただし SFTP→S3→DynamoDB の受信基盤（8 IF）＋契約失効の後処理はあり | 直接の要件なし。ただし計算停止フラグは #7 の前提（解約後の GW 無効化は管理画面の手動操作） | **廃止（移植しない）。** IF-01 に解約データがあれば既存取込へ統合、なければ要件追加を提起（CLD-07 待ち） | #5 ・ 提案は*推定*、e-smart 側は確実 |
| 6 | `RcvEmsPlsCntrPayerCommand`（IF2264） | 5分毎に支払者マスタを全件削除→対象契約種別のみ再投入し、契約終了判定（3条件）を適用 | **同 IF なし**（grep 0件）。契約／顧客マスタ取込（IF2023/2024/DM1040）はあり — DM1040 は支払者ロールを抽出済み | 個別の要件なし。グルーピング（必須 2026）に間接的に必要 | **廃止（移植しない）。既存の契約取込を IF-01 に沿って拡張。契約終了判定はスペックとして抽出** | #6 ・ 提案は*推定*、e-smart 側は確実 |
| 7 | `RcvHalfHourElectricPowerCommand`（IF1156） | 10分毎に電力30分値（速報／確報）を受信、30分→1時間に集約し買電売電を計算 | **なし**（grep 0件）— e-smart の電力／ガスデータは TagTag API 経由 | **必要・明文・2026スコープ**（「電力30分値はCルート（Xzilla経由）で取得する」） | **新規** — e-smart 取込パターンに準拠、業務ロジックは旧コードから継承。11本中もっとも重量級 | #7 ・ 確実 |

#### CSV・ZIPエクスポート系（4本）

4本とも実態は**削除前バックアップ**であり、運用者向けのデータダウンロード機能ではない。**判定: 4本まとめて廃止**（確実）。新しい保持期間（retention）方針＋e-smart 既存の2出力経路（管理画面ダウンロード 17 エンドポイント／7 データ種別、SFTP への定期エクスポート）で代替する。理由: E-GW 要件は性質が変化しており（spec [I]: 管理画面から集計データをダウンロード、保持期間 **24ヶ月** T.B.D — 「短期保持して削除」方式ではない）、e-smart 側にも「バックアップ後削除」機構は存在しないため。4本の違いは対象データと周期のみ:

| # | バッチ | バックアップ対象（旧テーブル） | 旧周期 |
|---|---|---|---|
| 8 | `CreateCsvAndZipConDeviceStatusesCommand` | 機器状態（`t_202`）・8日経過パーティション | 毎日 05:15、月曜に週次 ZIP |
| 9 | `CreateCsvAndZipConSensorHourlyValuesCommand` | 時間値（`s_102`）・8日経過パーティション | 毎日 05:15、月曜に週次 ZIP |
| 10 | `CreateCsvAndZipConSensorDailyValuesCommand` | 日値（`s_103`）・前月パーティション | 毎月1日 05:15、即 ZIP |
| 11 | `CreateCsvAndZipConSensorDailyAveValuesCommand` | 日平均値（`s_113`）・前月パーティション — 全体1ファイル（世帯分割なし） | 毎月1日 05:15、即 ZIP |

（パーティション = 大テーブルを日／月単位に区切った領域。区切りごと一括削除できるため高速 — 詳細は §4.3）

**一覧の読み方（3点）**:

- **確実／*推定*** のラベルは**事実部分**（旧システムの挙動、e-smart の有無、スコープ）の確度を示す。「判定」列は常にレビュー用の提案である — 特に #5/#6 は推論の比重が大きいため *推定* を明示した。
- 本報告は「何を作る／何を流用する」の判定までであり、**工数は未見積**（方針どおり 1バッチ = 1タスクの Notion 分割時に見積り予定 — §3）。なお #7 が業務的に最重量である。
- 11本の範囲外への示唆: e-smart は**事前集計を一切持たない**（アプリの月次レポートは要求の都度 TagTag API へ転送するだけで保存しない — 🔍 `syp-eminelstandard-backend/src/functions/api-dashboard/get-monthly-report-of-user.ts:21`）。したがって E-GW の**集計・計算系**グループ（バッチ一覧の別グループ、本報告対象外）にも流用できる既存資産はない見込み。

### 2.2 スペック確定を待たず即時対応する3点

1. **「既存システムを使い続けたほうがいい機能」リストの報告** — QA「旧Eminel基盤継承＋EMINEL-smartサーバーは独立デプロイの確認」（swan（mui）・回答中）の「ただし既存システムを使い続けたほうがいい機能があれば教えてほしいです」への回答。回答前に「既存システム」の指す対象の確認が必要。回答案は2部構成: **① 旧EMINEL: 現状のまま使い続ける価値のあるバッチはなし**（本報告の結論）・**② e-smart: 4候補** — Push 基盤（FCM）、ポイント／バッジ基盤＋PI連携、Xzilla SFTP→S3→DynamoDB 受信基盤、管理画面ダウンロード／エクスポート機構。
2. **SFTP エクスポート先 `/EST` の確認**（§4.2 冒頭）: e-smart は毎日6種の機器 CSV を SFTP へ送信しているが、宛先が Xzilla/DWH かはコードから確認できない（接続先は secret 管理）→ mui 様へ確認をお願いしたい（§5-3）。F-ES-10（Xzilla連携）のうち「EMINELデータの共有」に直結する。
3. **未決3件のフォロー**: CLD-07（Xzilla IF-01 の入出力定義）、CLD-06（アドバイス15種→7種の集約）、ポイントの必須／劣後矛盾（質問表・質問2に記載済み）。

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

- 🔍 旧: `legacy_eminel_docs/docs/02_詳細設計/10_バッチ処理/cron設定概要.txt` 1–37 行 ・ e-smart: `syp-eminelstandard-backend/template.yaml`（SAM）、`eminel_gw_project/docs/eminel-smart/02_product_overview.md` 48–53 行

**e-smart バッチ基盤の要点**（E-GW が継承する足回り。以下パスは `syp-eminelstandard-backend/` 起点）:

- **静的スケジュールは3本のみ**（いずれも `ScheduleV2`・timezone `Asia/Tokyo` — `template.yaml:9-11`）: ① `BatchRunSequentiallyStateMachine` — 基幹データ取込、`cron(5 0-7 * * ? *)` = JST 0〜7時の毎時5分（`template.yaml:853-888`、cron は 881–882 行）② `BatchMigrationIntegratedDataStateMachine` — Rinnai／Noritz 機器データ取得＋エクスポート、`cron(0 8 * * ?)`（`template.yaml:2205-2240`、cron は 2233 行）③ `BatchGetErrorDeviceInfoOfRinnaiStateMachine` — 機器エラー取得、同 8:00（`template.yaml:2966-2980`）。
- **それ以外のバッチはすべて EventBridge Scheduler のスケジュールを動的生成**する方式。大半は one-shot（一時点だけ発火し、`ActionAfterCompletion.DELETE` により実行後自動削除される単発スケジュール — 共通関数 🔍 `src/layers/common/nodejs/services/put-schedule.ts:18-33`、発火時刻の式は `src/layers/common/nodejs/utils/date-utils.ts:117` で組立て）。管理者がお知らせを作成 → API 側で配信スケジュールを登録（`src/functions/api-news/common.ts:207-209`）、配信バッチが完了 → 次の Push 送信スケジュールを登録（`src/functions/batch-send-news-complete/app.ts:72-80`）。ユーザーのオートメーション（アプリ内の機器自動化ルール）のみ繰り返し型 — ルール毎の週次 cron を動的生成し、自動削除はしない（`src/functions/api-automation/common.ts:115, 167-175`）。毎分ポーリングは存在しない（grep `rate(`: 0件）。
- **E-GW への含意**: spec [G] G-A-02（管理画面からアドバイスの定期配信スケジュールを設定 — 旧来の cron 固定方式では不可能だった要件）は、このスケジュール動的生成方式により技術的な解が既に基盤側にあると言える（特にオートメーションの繰り返し型は「API から変更できる定期スケジュール」の実例）。

**SYP の担当範囲**: QA「旧EMINEL調査範囲（conciergesv/eminelsv）とhemssv対象外の確認」（swan（mui）・回答中・2026-08-04参照）の要旨 — `conciergesv`/`eminelsv` は SYP の**調査**対象であり、旧システム上で開発を続ける範囲ではない。GW との通信は mui 開発の HEMS-SV（m2-cloud。旧システムの `hemssv` とは別物 — 名称が類似しているのみ）経由となり、スペックは後日共有予定。

**2026-06-10 のスコープ決定**（決定ログ登録済み）: 必須 = 暖房機能／暖房制御／照明アドバイス※／ポイント連携／グルーピング・レポート。劣後（2027/4〜）= 複合制御・DR・ダッシュボード・バッジ等。※「照明アドバイス」は省エネアドバイスの誤記と思われる（*推定*）。

- 🔍 `eminel_gw_project/docs/eminel/2_management/22_decisions.md` 30–31 行
- 機能一覧（`docs/eminel/1_product/10_feature_list.md`）の劣後列の凡例に注意: **✅ = 2027 へ繰越可**（スコープ内の意ではない）、空欄 = 今期必須。

**§4 の実施主体**: 特記のない限り実施者は **SYP**、実装は branch `gw-syp-dev` 上。リポジトリ名のないパスは `syp-eminelstandard-backend`、管理画面側は `syp-eminelstandard-web-admin`。「確認／決着」系のステップは §5 の経路による。本文中の人名（敬称略）: swan・masao takahashi（いずれも mui — QAデータベース回答者）、kihara（mui — GW ハード／ファームウェアリード）。

## 4. バッチ別判定詳細

（旧システムコードのパス表記 `…/src/Command/` は `legacy_eminel_docs/sources/conciergesv-develop/src/Command/` の略。「cron:NN行」は `legacy_eminel_docs/docs/02_詳細設計/10_バッチ処理/mng-webap_cron設定_20241029.txt` の行番号。）

### 4.1 配信・通知系（4本）

#### #1 `DistributeMonthlyEcoPointsCommand` — エコ暖房ポイント月次付与

**旧システムの処理**（確実）: 毎月1日 17:00 に cron 起動（🔍 cron:113-114）。対象抽出クエリは「前月の室温**設定**温度の月平均（`s_104`）≤ 22.0℃」の世帯を抽出し、付与理由キー `monthly_eco_points_YYYYMM`（YYYYMM＝対象月＝前月）により同一対象月に付与済みの顧客を除外（重複防止）— 🔍 `…/src/Command/DistributeMonthlyEcoPointsCommand.php:83-104`。1件あたり **250 ポイント**（定数 `BENEFIT_POINTS = 250` — 同:33）を年度単位（4月起点）で `s_141` に加算し、**同一トランザクション内で PointInfinity API を呼び出す**（同:116-188。PI 失敗時は当該顧客分をロールバックし、後続顧客の処理は継続）。

なお、コードと cron は**通年・毎月実行で季節条件なし** — E-GW の A03 が現行仕様として記す「12〜3月」と食い違いがある。スペック確定時に指摘が必要（対応ステップ1）。

**e-smart 既存実装 — 一部あり**（確実。パスは `syp-eminelstandard-backend/` 起点）:

- ① **PointInfinity 直接連携**: 専用 Lambda `src/functions/give-point-to-point-infinity/app.ts`（宣言 `template.yaml:3282`、secret 同:3289）。接続情報・各種 ID は Secrets Manager から取得（app.ts:15）、付与理由（FUYO_RIYU）は Shift_JIS へ変換して送信（同:35-39）、応答は XML で `<SYORI_STS>` = `000` が成功（同:50, 56）、リクエストは POST フォーム（同:92, 96）。→ 旧システムと**同系統のプロトコル**（旧: CP932 フォーム＋XML、URL `if0200.do`（設計資料上の IF 名は IF0200） — `legacy_eminel_docs/sources/eminel_sv_lib-develop/src/PointInfinity/PointInfinity.php:39, 65-71, 85-98`・同 `Api/InterfaceCode.php:20`。なお文字列 "IF0200" は backend 側には出現しない — 資料上の名称）。残高照会 Lambda `get-point-quantity-from-point-infinity/app.ts`（GET＋`<ZNDK>` タグ — 同:32, 79。secret は `template.yaml:2629`）も併設。
- ② **ポイント／バッジ付与の集中経路**: `src/layers/common/nodejs/business-logic/give-point-badge-for-user.ts:57` の `givePointBadgeForUser()` — すべての付与箇所が経由する共通関数。イベント毎の一意キー `pointBadgeStatsSk`（例 `login#2026-08`、`dr#<id>`）で**重複付与を防止**（同:69）、DynamoDB トランザクションで記帳し、PI 呼び出し失敗時は**ロールバック**（同:296-303 — 旧システムと同じパターン）。伝票番号（DENPYO_NO）はアトミックカウンター採番（同:390-409）。関連モデル: `PointBadgeMaster`／`PointBadgeStats`／`UserBadgeSummary`（`src/layers/common/nodejs/models/`）。現在の呼び出し元: 月初回ログイン、Tip 既読（`api-tip/read-tip.ts:68`）、アンケート回答（`api-survey/answer-survey.ts:346`）、DR 終了（`batch-end-dr/app.ts:86`）、機器連携、会員取込後、アプリ登録完了・お客さま情報入力・オートメーション作成等のチェックリスト達成 など。
- ③ **ないもの**: **計測データからの判定ロジック** — ポイント付与経路にセンサー系データは一切関与しない（ポイント経路内の grep `energy|usage`: 0件）。e-smart には「GW 計測データ」という概念自体がまだない。

**E-GW 要件**: F-ES-04 エコ暖房ポイント＋ F-ES-09 PI連携。ポイント連携は 6/10 決定で**必須 2026** — ただし機能一覧では ✅劣後 が付いており矛盾（質問表・質問2に記載済み。E-GW でのポイント値・条件も未確定 — A03 要確認）。合宿 Day3 の見立て「バッチが実態。ESTAサーバーに既に実装がある可能性が高い → 差分があればやる」は、今回コードで裏付けが取れた。

- 🔍 `eminel_gw_project/docs/eminel/3_requirements/00_integrated_requirements_v1.2.md` 409, 414, 675–691 行 ・ `22_decisions.md:31` ・ `10_feature_list.md:93, 95` ・ 合宿 Day3 議事録 125 行 ・ `A03_point.md:48-102`

**判定**: **①②は現状のまま流用、新規開発は③のみ** — 差分方式の方針どおり。

**対応ステップ**:

1. QA／A03 経由で業務スペックを確定する: ポイント値（250 維持か）、閾値（22℃か）、12〜3月の季節限定の有無（上記のコード vs A03 の食い違いを指摘）、必須／劣後矛盾の決着（質問表・質問2）。
2. HEMS-SV（m2-cloud）スペックの共有を待ち、GW 計測の設定温度データがサーバーへ届く経路を確認する。DynamoDB 上に**世帯別月平均の蓄積テーブル**を設計（旧 `s_104` 相当 — 集計系バッチグループの管轄のため当該グループと連携）。
3. 新規の判定 Lambda を実装する: 月次テーブルを走査 → 閾値以下を抽出 → `givePointBadgeForUser(userId, 'eco_heating#YYYYMM', …)` を呼ぶ — 重複防止／トランザクション／PI連携は既存機構を**そのまま再利用**。追加は新しい付与理由（FUYO_RIYU）の `constants.ts` 登録のみ（雛形: 同:1756-1762）。
4. スケジュール: `template.yaml` に月次の静的 `ScheduleV2` を1本追加（§3 の静的3本の書式に倣う。固定周期のため one-shot は不要）。
5. テスト: 月次ダミーデータ投入 → 2回連続実行で**重複付与なし**を確認、PI エラー模擬で**ロールバック**を確認、同一データでの旧システムクエリ手動実行結果と付与件数を突合（テスト = mui／実装 = SYP の分担前提）。

#### #2 `PublishRegularEcoMissionsCommand` — 省エネアドバイス定期配信

**旧システムの処理**（確実）: コマンドは1本で、`--eco-mission-id` オプション（1〜19）付きで実行。スケジュールは**日時固定の 19 本の cron 行**（うち 15 本は配信月を季節で限定、4 本は通年毎月実行 — 🔍 cron:84-102）。コマンドは **10 クラスの Publisher** へルーティングし、アドバイス種別ごとの判定条件（平均超過、ECO モード未使用、就寝／外出タイマーの設定忘れ、暖房比率、契約記念日…）で対象者を抽出する。（フォルダには 11 ファイルあるが 1 つはオプションクラス。`04_バッチ一覧.md` の「11種Publisher」はこれを含めた数え方。）Publisher はアドバイスレコードの作成**と** Push 登録（対象抽出型は1分後発火）を行い、実際の送信は #3 のバッチが担う。

*3つの数の関係: 19 = 現行アドバイス種別数（mission-id）→ 共用の 10 Publisher クラスで処理。15 = CLD-06 で集約検討時に記された「約15種」。集約先の案 = 7種＋エコ暖房ポイント。*

- 🔍 `…/src/Command/PublishRegularEcoMissionsCommand.php:54-140` ・ `…/src/Command/PublishRegularEcoMission/EcoMissionPublisher.php:60-82, 112-152`

**e-smart 既存実装 — なし**（確実）: `src` 全体で grep `advice|アドバイス|mission|ミッション|判定` → **実ヒット 0件**（ヒットはすべて `permission` の部分一致）。最も近いのは **Tip（エコライフのコツ）** だが、これは管理者が手動作成するコンテンツの配信である（🔍 `src/layers/common/nodejs/models/Tip.ts:4-22`: `body_tip` = 管理画面で編集する本文、`target_type` = ALL／属性／CSV の3種の静的ターゲティングのみ（`batch-send-tip-preprocessing/app.ts:43-50`）、`point_quantity` = 既読時の付与ポイント（`api-tip/read-tip.ts:68`））。**世帯のエネルギーデータを読んで配信可否を判定するフィールド・関数は存在しない**（`api-tip` 内の grep `energy|usage`: 0件）。つまり旧システムの個別判定型「アドバイスエンジン」に相当するものは e-smart にない。

**E-GW 要件**: 2026 スコープ（F-ES-03 は ✅ なし = 今期必須。6/10 決定の「アドバイス」行）。要件は旧システムと**異なる**: spec [G] は管理画面から変更可能な定期配信スケジュールによる自動配信を要求（現行は cron 直書きの固定スケジュールで管理画面から変更不可 — Day3 で「いけてない」とされた典型例と考えられる）。15種→7種の集約は未決（CLD-06 未動）、判定式の踏襲可否も T.B.D（G-C-05 — **種別ごとの判定式は [G] に抽出済み**。旧コードはクロスチェック用）。

- 🔍 `4_spec/admin/G_energy_advice.md:18-19, 28-29, 47` ・ `00_integrated_requirements_v1.2.md:632-647` ・ `20_open_issues.md:176-177`

**判定**: **新規** — 配信の「出口」（ターゲティング＋Push＋ポイントの Tip パターン）は既存を使い、判定層を新規実装する。

**対応ステップ**:

1. CLD-06 の7種確定を待つ／早期確定を依頼する（質問表・予備質問1）。並行して [G] G-C-05 の判定式表を精査し、判定式ごとに「必要な入力データ」と「そのデータの E-GW での取得元（GW 計測か、TagTag か、Xzilla か）」をマッピングする — これが実工数を決める表になる。
2. `Tip` を雛形に新モデル `Advice` を設計（`target_type`／`point_quantity`／Push フラグは踏襲して配信経路を再利用）＋「判定条件」と **管理画面から設定できる定期配信スケジュール**（G-A-02）を追加。
3. **バッチボーン**（§3）を先行構築: state machine `BatchJudgeAdvice`（種別毎）→ `BatchSendAdvice` → `BatchPushNotice` を one-shot スケジューラで連結（既存の news/tip チェーン `api-news/common.ts:207-209` が雛形）。当初は判定が空リストを返す状態にして、他の部分を先にテスト可能にする。
4. web-admin 側 UI: `components/tip/tip-form.vue`（付与ポイント／バッジ・ターゲティング・Push のブロックが既存）を雛形にアドバイス管理フォームを作成＋定期配信スケジュール設定部（新規 — [G] G-A-02）。
5. ステップ1で確定した種別リストに沿って判定式を実装: 種別ごとに判定 Lambda 1本、出力は対象ユーザーリスト → 既存パターンでアドバイス書込み＋Push キュー登録。
6. テスト: 判定式ごとに境界データ一式（閾値の内／外）。結合フェーズ（9月目標 — §3）前に実動確認。

#### #3 `DispatchPushMessagesCommand` — Push 送信（毎分）

**旧システムの処理**（確実）: 毎分起動。`push_message_destinations` から期限到来分をページング取得（500件/ページ）、検証（device_token／FCM トピックの排他確認）後、中継サーバー **PushCore**（`localhost:54650`）へ POST → PushCore が FCM へ転送（*推定* — PushCore 本体のコードはリポジトリに含まれない）。リトライは3分間隔・5回で打切り。

- 🔍 `…/src/Command/DispatchPushMessagesCommand.php:51-177` ・ `legacy_eminel_docs/sources/eminel_sv_lib-develop/src/StaticServices/PushMessageService.php:26, 36-39` ・ `config/push_message.php:4-14` ・ cron:79-80

**e-smart 既存実装 — あり（完備）**（確実）:

- ① **トークン管理**: `src/layers/common/nodejs/models/MobileTokenManagement.ts`（`user_id`＋`mobile_token`。アプリが API `user/save_mobile_token` で登録）。
- ② **firebase-admin による FCM 直接送信＋無効トークン自動削除**: `src/layers/common/nodejs/services/push-notification-firebase.ts:87-97` — `messaging/invalid-registration-token` 等のエラーコード検出時にトークンをテーブルから削除。
- ③ **配信のファンアウト**: `src/functions/batch-push-notice/app.ts:17-34` — 前処理で分割済みのユーザーロット（10,000件/ロット — `batch-push-notice-tip-new-preprocessing/app.ts:53`）を S3 から読み、ロット内は最大 100 並列で送信（`src/layers/common/nodejs/services/push-notice-to-user.ts:21` — ユーザーの受信可否フラグも考慮）。`target_screen`／`target_id` はアプリ側の通知タップ時画面遷移と整合（`syp-eminelstandard-app-syp-dev/lib/presentation/pages/main/bottom_navigation_view.dart:473-528`。トークン登録は同:101-111）。Push 配信の state machine は6系統: survey／news／tip／DR新着／DR開始／DR終了（`template.yaml:510/685/815/1889/1927/1965`）。

**E-GW 要件**: **D03（レビュー中 — 未確定）**に、踏襲元 = **ESTA Push基盤＋現行（通知種別の網羅）**、「全要件がESTA既存のため【新規】なし」と明記。

- 🔍 `3_requirements/app/D03_push.md:7, 32-34, 84-86`

**判定**: **旧バッチ廃止**（PushCore＋DB キュー＋毎分 cron は再構築しない）、**e-smart の Push 基盤を利用** — §3 の前提どおり、独立デプロイ確定時は新環境への同スタック構築となる。

**対応ステップ**（主に「正しく廃止する」ための作業）:

1. 「Push 基盤（FCM）」を独立デプロイ QA のただし書き回答リスト（§2.2-1）に含め、mui 様に共用方針を確認する。
2. **旧システムの通知種別の棚卸し**（D03 の「＋現行」の部分）: 旧システムが発信する全通知種別（アドバイス19種、DR、見守り（CLD-05 で保留中）、レポート…）をリスト化し、種別ごとに「新しいコンテンツ生成元（#1/#2/…）」と「E-GW アプリでの `target_screen`」をマッピングする。成果物は D03 確定時のマッピング表。
3. 独立デプロイの場合: E-GW アプリ用 Firebase プロジェクトの新設、新環境への `MobileTokenManagement` テーブル＋ API `user/save_mobile_token` の構築（パターンは既存。作業は設定＋ Secrets Manager 経由の credential 登録）。
4. `DispatchPushMessagesCommand`／PushCore の移植タスクは**起こさない** — Notion タスク分割時に「廃止、batch-push-notice パターンで代替」と明記し、約46本の母数に誤って算入しないようにする。
5. テスト: 実トークンの dev 端末への送信確認、無効トークンの自動削除確認（②）、メッセージ 4096 バイト上限の確認（`constants.ts:223`）。

#### #4 `ControlDrOperationCommand` — DR 指令制御

**旧システムの処理**（確実）: 毎分起動・2フェーズ構成。DR 参加世帯ごとに指令の衝突を回避（5分）しつつ、`instructions` テーブルへ宅外制御指示（ECHONET 形式 — EPC 80/B0 = 電源／温度変更コード）を書き込む。その際**ユーザーのアプリ操作に見せかける**必要がある。コード内コメント原文: 「暖房制御ユニットとユーザのアプリ端末の情報を取得」「ユーザのアプリ端末からの操作のように見せかけないとゲートウェイが指令を無視する」（🔍 `…/src/Command/ControlDrOperationCommand.php:171-172`）。旧 DR = サーバーが DB へ指令を書き、GW が hemssv 経由で**ポーリング**（定期的に「新しい指令はあるか」を取りに来る方式）で取得する。

**e-smart 既存実装 — 別方式の DR 基盤あり**（確実）:

- ① **DR イベントモデル＋制御前状態の保持**: `src/layers/common/nodejs/models/Dr.ts:5-30` — `implement_start_time`／`implement_end_time`（→ one-shot スケジュール登録）、`target_type`（news/tip と同様のターゲティング）、`control_setting`（どの機器に何をするか）、Push 3点セット（新着／開始／終了）、`point_quantity`／`has_badge` — ＋ `DrUserAction.ts:1-14` — `pre_control_status` = **DR 前の機器状態**（終了時の復元用）。
- ② **開始／終了バッチ**: `batch-start-dr/app.ts:55-65` が参加ユーザーの機器を `control_setting` に従いサーバーから直接制御し、`pre_control_status` を保存（同:212）。`batch-end-dr/app.ts:82-94` が完走ユーザーへポイント付与（#1 の②を再利用）後、機器状態を復元（同:96-190）。制御対象は Rinnai／Noritz／Daikin／MUI 赤外線経由のエアコン・ファンコン（`batch-end-dr/app.ts:139-188`）— いずれも**メーカークラウド直結機器で、GW 経由の制御経路はない**。開始／終了スケジュールは DR 配信完了時に one-shot 登録され（`batch-send-dr-complete/app.ts:127-143`）、配信スケジュール自体は管理者の DR 作成・更新時に登録される（`api-dr/create-dr.ts:111`・`update-dr.ts:149`）。web-admin には DR 管理画面一式（`pages/distribution-management/dr/`＋`components/dr/dr-form.vue` — 1881 行）。

→ e-smart の DR は**サーバー主導で機器を直接制御**する方式であり、旧システムの「DB へ指令書込み → GW ポーリング」方式とは根本的に異なる。

**E-GW 要件**: F-ES-07/08＋ F-AD-08 — **劣後・2027/4 以降**（6/10 決定。B05: 26年スコープ = なし）。将来アーキテクチャ: DR はサーバー主導、指令は HEMS-SV（m2-cloud）経由で GW へ。DR 終了方式（サーバーが時刻どおり指令する A 案 vs GW が自律終了する B 案 — GW が状態を持つか）は**未決** — 質問表・質問5。2026年のファームウェア設計を拘束する。

- 🔍 `22_decisions.md:30-31` ・ `B05_dr.md:8, 33-37` ・ 合宿 Day3 議事録 113–122 行（DR発令の詰め込み → 約17項目へ分割）

**判定**: **2026年は実装なし。** 2027年に e-smart DR 基盤上で新規開発。「アプリ操作への偽装」という旧方式の技巧は**一切継承しない**。

**対応ステップ**:

1. （2026年 — 唯一のアクション）kihara（mui）と社内整理のうえ、北ガス様へ確認: GW が DR 状態を保持してよいか（終了方式 A/B 案 — 質問表・質問5）。結果はファームウェア設計を決めるため、**2027年まで先送りできない**。
2. （2027年）「DR イベント」層は全面流用: `Dr`／`DrUserAction`／`DrStats` モデル、管理画面、ターゲティング、Push 3点セット、終了時ポイント付与。
3. （2027年）`control_setting` に新機器種別「E-GW 経由の暖房」を追加 — `handleControlDevice` に新分岐を実装し、mui 提供予定の HEMS-SV（m2-cloud）API スペックに従って呼び出す（旧方式の `instructions` 書込み＋ GW ポーリングの代替）。
4. （2027年）GW 経由暖房機器の `pre_control_status` マッピング（DR 後の復元）— ステップ1の結果（状態を GW が持つかサーバーが持つか）に依存。
5. （2027年）タスク分割は Day3 の方針どおり（Notion 上の約17項目）— 旧システムのような「1バッチ全部盛り」にはしない。

### 4.2 外部連携・受信系（Xzilla取込 — 3本）

**旧システムの受信方式**: Xzilla からの CSV を、5〜10分毎に SFTP 経由で中間サーバーへ取り込む。

**e-smart の受信方式**（確実）: **SFTP → S3 → DynamoDB** のフローを **JST 0〜7時の毎時**実行（`cron(5 0-7 * * ? *)` — §3）。編成は state machine `src/statemachine/batch_run_sequentially.asl.json`（多重起動防止 5–38 行 → temp 掃除 → ファイル一覧取得 → 8 IF 並列 forward → import → 後処理3本）。SFTP 上の IF フォルダ一覧はコード内に定義 — 🔍 `src/functions/batch-get-list-file-name-from-sftp-server/app.ts:149-169`: IF2241（TagTag会員）／DM1040（契約リスト）／IF2242（会員属性）／IF2016（供給地点）／IF2023（使用契約）／IF2024（顧客）／IF2029（建物）／IF2223（機器）。各 IF は CSV フォルダ＋`END/` 内のメタデータ `.dat`（確定済みファイル一覧 — 同:52-66）で構成。二重取込は `CsvDownloadHistory` テーブルで防止（同:69-87 — このテーブルの実際の役割。§4.3 の注記参照）。ファイルは 50,000 行単位に分割して S3 へ（`batch-forward-csv-from-sftp-server-to-s3/app.ts:56-64`）、`batch-ifXXXX-import-*` ハンドラがトランザクションで DynamoDB へ書き込む。取込順: IF2241 → DM1040 → IF2242 は直列（データ依存）、残り 5 IF は並列（asl 493–794 行）。「fake 会員」（Xzilla データ到着前にアプリ登録した会員）のマージ時は **5分ロック**（`batch-if2241-import-tagtag-kaiin/app.ts:69, 102-111` — TTL（期限到来レコードの自動削除）で自動失効。39 本の API ハンドラが `check-kaiin-updating.ts:10-15` でロックを確認）。取込後処理3本: ① 新規会員への配信中コンテンツ再配信（`batch-send-contents-to-updated-user/app.ts:79-132`）② ガス契約失効時の選択宅変更＋「ゆーぬっく」契約出現時のバッジ付与（「ゆーぬっく」はコード上 YUNUKKU・契約コード `PG003`、backend 定数上の名称は「ゆーぬっく２４ネオ」`constants.ts:1065`。処理箇所: `batch-update-selecting-place-no/app.ts:89-143, 283-296`、`constants.ts:1909`）③ ガス契約終了時の連携・機器削除（`batch-remove-integration-expired/app.ts:44-79`）。

**旧3 IF はいずれも e-smart に存在しない**（確実）: backend 全体で grep `IF1156`・`IF2249`・`IF2264`・`30分`・`HalfHour`・`half_hour`・`速報`・`確報`・`electric_power`・`cntct` = **0件**。（`payer` は DM1040 取込の支払者ロール抽出定数としてのみ出現 — `batch-dm1040-import-user-contract-list-preprocessing/app.ts:54, 63` — 支払者情報が DM1040 フローで処理済みであることの傍証。）

**送信方向（e-smart → 基幹）は実在**（確実）: 🔍 `src/layers/common/nodejs/services/upload-data-backup-to-sftp.ts:22-43, 52-57` — 機器データ CSV 6種（給湯器系5種＋赤外線リモコン）を**同一 SFTP サーバーの `/EST` フォルダ**へ、アップロード専用アカウントで毎日 8:00 に送信（`BatchMigrationIntegratedDataStateMachine` 内 — `template.yaml:2215-2226`）。*推定（未確認）*: `/EST` の宛先は Xzilla/DWH（分析用データ基盤）と思われるが、接続先は secret 管理でコードから確認できない → mui 様へ確認をお願いしたい（§5-3）。該当すれば F-ES-10（Xzilla連携）のうち「EMINELデータの共有」（送信方向）の既存実装となる（`00_integrated_requirements_v1.2.md:696`）。Xzilla 系のタスク一覧作成時は**この送信方向を追加**すること（旧バッチの本数だけで数えない）。なお合宿 Day3 議事録 126 行の見立て（アプリログの基幹への送信インターフェースも ESTA に既にある可能性）は、確認の結果、**該当する実装はなかった** — backend にアプリログの SFTP 送信経路はなく、管理画面ダウンロードのみ。

#### #5 `RcvCntctCancellationCommand` — 電力解約受信（IF2249）

- **旧システム**（確実）: 5分毎に当日 CSV を SFTP 取得。契約種別 PE624/625 を抽出（:242-243）、`ipf_cntct_cancellations` へ upsert（あれば更新・なければ追加）、解約顧客の**買電売電の計算停止フラグ**（`t_101.c065=1`）を設定する。当日分の場所契約支払者情報（IF2264）の取り込みが完了している場合のみ、顧客情報登録完了通知 API を呼び出す。🔍 `…/src/Command/RcvCntctCancellationCommand.php:30, 99-113, 193-217, 242-243, 306-334` ・ cron:107-108
- **E-GW 要件**: 解約の自動連携に個別要件はなし。業務フロー上、解約後の GW 無効化は**管理画面での手動操作**と明記。IF-01 は未決（CLD-07 — 要確認 約10項目）。🔍 `docs/eminel/1_product/11_business_process/readme.md:938-941` ・ `20_open_issues.md:181-182`
- **判定**（*推定*）: **廃止（移植しない）。ただし業務は消えない**: E-GW が 30分値から買電売電を計算する以上（実際に計算する — #7）、電力契約の解約時に「計算停止」フラグを立てる仕組みは必要（手動フローが定めるのは GW 無効化のみで、計算停止には触れていない）。
- **対応ステップ**:
  1. CLD-07／IF-01 が具体化した時点で、解約データフローの有無を確認する。**なければ即座に CLD-07／QA 経由で要件追加を提起**（#7 が停止フラグを必要とするため、要件化しないまま廃止とすることは不可）。
  2. ある場合: 5分毎の専用バッチは作らない — 既存取込フローへの IF 追加として実装する。技術手順はパターンどおり: `DEFAULT_FOLDER_CSV`／`DEFAULT_FILE_NAME_METADATA` へフォルダ追加（§4.2 冒頭参照）、`constants.ts` へ `LIST_COL_*` 列定義追加、`batch_run_sequentially.asl.json` へ Map 分岐追加、`batch-ifXXXX-import-*` ハンドラを IF2016（単純 Put）を雛形に実装。
  3. 「計算停止」の業務ロジック: 取込後処理④として実装（既存の後処理3本のパターンに倣う）— 該当世帯レコードにフラグを設定。e-smart の 0〜7時毎時ウィンドウで解約業務には十分と考える（*推定* — IF-01 確定時に業務側と要確認）。
  4. テスト: PE624/625 有無のダミー CSV。停止フラグが #7 の買電売電計算に反映されることを確認。

#### #6 `RcvEmsPlsCntrPayerCommand` — 支払者マスタ受信（IF2264）

- **旧システム**（確実）: 5分毎。`ipf_ems_pls_cntr_payers` を**全件削除のうえ、対象契約種別（PE624/625/650/651/652・PG077/079）のみ再投入**（除外条件 :319-329、memory_limit 4096M — :63）。**契約終了判定（3条件）** — スペックがコード内コメントに記載（:373-385）— を適用し、`t_101` の連携番号・計算停止フラグを更新。🔍 `…/src/Command/RcvEmsPlsCntrPayerCommand.php:63, 170-177, 245-363, 371-626` ・ cron:105-106
- **E-GW 要件**: `docs/eminel` 全体に「payer」の個別機能なし（grep 済み）。最も近い範疇は F-ES-10（Xzilla連携）のうち「顧客情報・契約情報の取得」。グルーピング（必須 2026）は建物種別（Xzilla より取得と明記 — :619）のほか、料金メニュー・アンペア数等の契約情報を必要とする（これらは F-ES-10 の契約情報取得で賄われる想定 — :692-696）。🔍 `00_integrated_requirements_v1.2.md:415, 619, 692-696`
- **判定**（*推定*）: **廃止（移植しない）**（5分毎の全件入替えは「いけてない」の典型）。既存の契約取込（IF2023/2024/DM1040 — e-smart の DM1040 は支払者ロールを抽出済み）を IF-01 に沿って拡張する。
- **対応ステップ**:
  1. **旧コードのコメントから契約終了判定3条件を1ページのスペックに抽出する**（保存価値のある業務知識 — 出典: `RcvEmsPlsCntrPayerCommand.php:373-385`）— IF-01 を待たず即着手可能。
  2. IF-01 具体化時: 旧システムが使う支払者フィールド（供給地点特定番号、IPF使用契約番号、受電地点特定番号、お客様番号）と e-smart 既存の IF2023/2024/DM1040 データを突合 — 不足フィールドは IF-01 への追加を要請する（不足がなければ支払者専用 IF は要求しない）。
  3. 不足分を既存の契約取込ハンドラの拡張として実装（列追加／処理追加）、ステップ1のスペックを後処理として適用。
  4. テスト: 契約終了3条件 ×（成立／不成立）のダミーデータ。フラグ・連携番号の結果を旧ロジックの手動実行と突合。

#### #7 `RcvHalfHourElectricPowerCommand` — 電力30分値受信（IF1156）

- **旧システム**（確実）: 10分毎。`emn_all`／`emn_fast_electric_powers` を全件入替えして速報値を再登録し、確報値（fixed_div=1）は `emn_confirm_electric_powers` へ追記登録する。その後 **買電売電を計算**: 30分値のペアを1時間値へ集約し `s_102` へ書き込む。分岐条件: 太陽光あり世帯 → 売電は GW 計測値から（日次蓄積バッチが担当）、コージェネかつ受電地点特定番号あり → Xzilla 値から計算。🔍 `…/src/Command/RcvHalfHourElectricPowerCommand.php:107-122, 192-233, 449-583, 591-725, 734-1050`（分岐条件 875–893 行）・ cron:109-110
- **e-smart**: **なし**（確実）— grep 0件（§4.2 冒頭）。e-smart の電力／ガス使用量データは TagTag API 経由（`eminel_gw_project/docs/eminel-smart/02_product_overview.md:119`）。
- **E-GW 要件**: **必要・明文・2026 スコープ**: 「電力30分値はCルート（Xzilla経由）で取得する」（統合要件 3-2 節）。F-ES-10（Xzilla連携）が速報値・確報値の取得を定義。グラフ（F-ES-01）、グルーピング・レポート（必須）のデータ源。連携テスト（Xzilla）は ✅ なし = 今期。🔍 `00_integrated_requirements_v1.2.md:84, 692-696` ・ `10_feature_list.md:148`
- **判定**（確実）: **新規** — 11本中もっとも業務量の重いバッチ。
- **対応ステップ**:
  1. 30分値の IF-01 確定: ファイル形式、提供周期（旧: 10分毎。e-smart 基盤は現状 0〜7時ウィンドウのみのため、準リアルタイム周期は新規要素 — 北ガス様との合意が必要）、認証（CLD-07）。
  2. §4.2 冒頭の取込パターン（SFTP→S3→ハンドラ）で受信経路を構築。周期が 0〜7時ウィンドウより高頻度なら、`BatchRunSequentially` へ相乗りせず専用の `ScheduleV2` を新設する。
  3. 30分値用の DynamoDB テーブル設計: 速報値（上書き）／確報値（確定・追記蓄積）を分離 — 旧 `emn_fast/confirm_electric_powers` 相当。生データの TTL は保持期間（SVC-03）に従い検討。
  4. **業務ロジックの継承**（コードの移植ではない）: 「30分×2 → 1時間値」の集約規則、世帯の設備構成による買電／売電の計算条件表（太陽光／コージェネ／受電地点特定番号 — 出典: 旧コード 875–893 行）を、**E-GW の設置9パターン**（統合要件 v1.2 の 3-5 節定義）に再マッピングする（新構成では分岐追加の可能性あり）。
  5. 出力を集計系バッチグループ（グラフ／グルーピング／レポート — 本報告対象外）へ接続＋ #5 の停止フラグを反映。
  6. テスト: 全分岐（太陽光／コージェネ／通常、速報→確報の上書き、30分ペアの欠損）を網羅するダミー30分値一式 — 1時間値の結果を旧ロジックの手動実行と突合。

### 4.3 CSV・ZIPエクスポート系（4本まとめて判定）

**旧システムでの実態**（確実 — 名前から誤解しやすい）: この4本は**運用者向けのデータダウンロード機能ではなく**、DB の保持期間を短く保つための**削除前バックアップ**である。05:15 に実行: #8/#9 は毎日（月曜に週次 ZIP 圧縮）、#10/#11 は毎月1日のみ（即 ZIP 化）。cron 上は「#12.DBデータ削除」セクションに配置されている（本報告のバッチ番号 1〜11 とは別の番号体系）。shell は `set -eu` — エラー時は即停止のため、CSV 作成に失敗した場合、削除ステップは実行されない（🔍 `cron設定概要.txt` 補足1「CSV作成後に問題なければデータを消去」）。内容: 8日経過パーティション（`t_202` 機器状態、`s_102` 時間値）／前月パーティション（`s_103` 日値、`s_113` 日平均値 — 全体1ファイル・世帯分割なし）を CSV 出力 → ZIP 化 → `DeleteData` がパーティションを削除。ファイルはサーバーディスク上に置かれ、運用者は旧管理画面からダウンロードする。対象・周期の一覧は §2.1 の表を参照。

- 🔍 `CreateCsvAndZip*Command.php` 4ファイル（各ファイル 39 行付近: −8日／−32日のパーティション指定）・ `CreateZipsTrait.php:23-72` ・ cron:39-41

**e-smart 既存実装 — 「バックアップ後削除」機構はなし。データ出力ニーズは既存の2経路で充足**（確実）:

- ① **管理画面オンデマンドダウンロード**: ルーターに 17 エンドポイント — 🔍 `src/functions/api-download/app.ts:23-46`（DR一覧／news一覧／DR統計／アクセスログ／ユーザー情報／ポイント付与履歴／ガス機器データ…）。重量級は `BatchDownloadFunction` へ非同期委譲（`api-download/download-user-info.ts:17-25`、`template.yaml:475-493` — MemorySize 5120／Timeout 900）→ ZIP 化して S3 `BUCKET_DOWNLOAD`（`template.yaml:233`）→ presigned URL（S3 の期限付き署名 URL。有効 600 秒 — `api-s3/get-presigned-url-for-download.ts:67`）で管理者がダウンロード。web-admin 側は `pages/other/data-management/` の 7 データ種別 — 🔍 `syp-eminelstandard-web-admin/constants/common.ts:614-622`（user_info／access_log／mui_sensor_history／gas_device_history／point_award_history／badge_earned_history／gas_device_raw_history）。
- ② **SFTP `/EST` への定期エクスポート**（§4.2 冒頭）— 北ガス様が「定期的にファイルを受領する」運用を希望される場合の直接の先例。
- ⚠️ 調査資料由来の誤解への注記: `CsvDownloadHistory`（「CSVダウンロード履歴」）は**受信方向** — SFTP からのファイル取得履歴（二重取込防止）であり、管理者ダウンロードの履歴ではない（`models/CsvDownloadHistory.ts:1-6`、記録箇所 `batch-forward-csv-from-sftp-server-to-s3/app.ts:80-93`）。また DB に「N日後削除・ZIP保管」のモデルはなく、DynamoDB は PITR（インフラレベルのバックアップ）有効＋必要テーブルごとの TTL である。

**E-GW 要件 — 要件の性質が変化**: spec [I]（DRAFT）が管理画面からのデータダウンロードを定義: e-smart 踏襲種別（顧客情報、アプリアクセスログ、ポイント付与履歴… — いずれも E-GW 向けは T.B.D）＋ E-GW 新規3種: GW・連携デバイスデータ、連携デバイスエラー履歴、**連携機器別計測値集計データ（10分/1時間/1日/1ヶ月値）** — CSV(ZIP) 出力、**保持期間 24ヶ月（T.B.D）**。また SVC-03: 新システムの保持期間／バックアップ要件は未定義。

- 🔍 `4_spec/admin/I_data_download.md:16-19, 43-52, 200-204` ・ `20_open_issues.md:87`（SVC-03）

**判定**（方向性は確実、詳細は T.B.D 待ち）: **現行形態の4本は廃止** — 前提（DB は細粒度データを 8〜14 日程度しか保持しない — `t_202`: 8日、`s_102`: 14日。`DeleteDataCommand.php:47-50`）が「24ヶ月保持・随時ダウンロード」と両立しないため。

**対応ステップ**:

1. spec [I]（E-GW データ種別＋保持期間 24ヶ月）と SVC-03（retention／バックアップの全体方針）の確定 — spec [I] レビュー時に提起する。**質問表に未記載のため質問追加を検討**（§5-6）。
2. 代替 retention 設計: 細粒度データはステップ1で確定する保持期間に従い DynamoDB に保持（TTL 利用）、24ヶ月の DB 保持が高コストなら S3 への退避を検討 — 集計系グループのデータ量見積りに従い判断。
3. E-GW 新データ種別への既存ダウンロード機構の拡張（パターン①どおり）: `api-download/app.ts` へエンドポイント追加 → `batch-download/` へハンドラ実装（雛形: `download-user-info.ts`）→ `DOWNLOAD_DATA_MANAGEMENT_TYPE` へ種別追加＋ web-admin フォーム（`components/data-management/`）。
4. 北ガス様が「週次／月次で ZIP ファイルを定期作成・保管する」従来運用の継続を希望される場合: パターン②で定期エクスポートバッチを1本作成 — [I] の未決事項として確定待ち。
5. CSV 列形式: 運用者の慣れを考慮し、旧形式との互換維持を推奨（*推定* — 運用慣習について）。現行の列一覧は **[I] に抽出済み**（現行 EMINEL セクション、出典 `DownloadController::getCsvHeadersOnSelection()`）— 旧4バッチのヘッダはクロスチェック用のみで、再抽出タスクは不要。
6. Notion タスク分割時: 旧4本は「廃止、retention＋ダウンロード／エクスポートで代替」と明記し、約46本の母数に誤って算入しないようにする。

## 5. ご確認・ご相談事項（一覧）

| # | 事項 | 関連 | 対応・経路 |
|---|---|---|---|
| 1 | **2026年 DR アーキテクチャの決着**: GW が DR 状態を保持してよいか（終了方式 A/B 案）— 2026年ファームウェア設計を拘束 | #4（対応ステップ1） | 北ガス様向け質問表・**質問5**に記載済み。送付前に kihara（mui）との社内整理をお願いしたい |
| 2 | Xzilla IF-01 の入出力＋認証の定義（CLD-07）— **送信方向**（EMINELデータの共有）も含む | #5〜#7（§4.2） | 北ガス様のご回答待ち（mui の PM 様経由）。待機中に SYP が旧コードから必要フィールド一覧を準備（#6 対応ステップ1〜2） |
| 3 | **SFTP `/EST` の宛先確認**: Xzilla/DWH か（接続先は secret 管理のためコードから確認不可） | 送信方向（§4.2）＋ §2.2-2 | mui 様にご確認をお願いしたい（QAデータベース、または HEMS-SV スペック共有時） |
| 4 | ポイントの必須／劣後矛盾＋ E-GW のポイント値 | #1（対応ステップ1） | 質問表・**質問2**に記載済み。コードと A03 の「12〜3月」の食い違い（#1）は A03 スペック確定時に指摘 |
| 5 | アドバイス 15種→7種の集約（CLD-06）＋スケジュール／判定式 spec [G] | #2（対応ステップ1） | 質問表・**予備質問1**に記載済み。スケジュール部分は spec [G] レビュー時に提起 |
| 6 | 保持期間・ダウンロードデータ種別 spec [I]＋ SVC-03 | #8〜#11（§4.3 対応ステップ1） | spec [I] レビュー時に SYP が提起 — **質問表に未記載のため質問追加を検討** |
| 7 | 「既存システムを使い続けたほうがいい機能」リストの報告（2部構成 — §2.2-1） | §2.2-1 ・ #3（対応ステップ1） | SYP が QAデータベースの該当ページへ直接回答予定 |
| 8 | 見守り通知の実施可否（CLD-05） | 新規 Push 種別の棚卸し（#3 対応ステップ2） | 質問表・**質問3**に記載済み |

## 付録A. ご参考: ESTA 調査資料（docs/eminel-smart/）と実コードの差異（6点）

今回のコード照合の過程で、既存の ESTA 調査資料 `eminel_gw_project/docs/eminel-smart/`（6ファイル）と実コードの間に以下の6点の差異を確認した。同資料を引用する際は実コードの再確認を推奨したい（あわせて資料側の更新もご検討をお願いしたい）。

| 調査資料の記載 | 実コード |
|---|---|
| Push「最大500件/バッチ」（`02_product_overview.md:121`） | 500 件という定数はなし。受信者を 10,000 ユーザー/ロットに分割し、ロット内最大 100 並列で送信（#3） |
| 基幹取込「日次・深夜〜早朝」（`02_product_overview.md:30, 63-64`） | `cron(5 0-7 * * ? *)` — JST 0〜7時の**毎時**実行（§3） |
| 会員マージのロック「6分」（`02_product_overview.md:73, 78`） | `UPDATE_LOCK_TTL_MINUTES = 5`（§4.2 冒頭） |
| `CsvDownloadHistory` = 「CSVダウンロード履歴」→ 管理者ダウンロード履歴を示唆（`03_backend_models.md:107`） | **SFTP からの受信履歴**（二重取込防止）。管理者ダウンロードとは無関係（§4.3） |
| 「自動化ルール実行（毎分）」（`02_product_overview.md:85`） | 毎分実行はなし — ルール毎に週次スケジュールを動的生成（§3） |
| Lambda ランタイム「Node.js 20.x, arm64」（`02_product_overview.md:49`） | `Runtime: nodejs24.x`（`template.yaml:181`。なお共通レイヤーの CompatibleRuntimes は nodejs20.x のまま — 同:3163） |

## 付録B. 参照資料一覧

- **`legacy_eminel_docs`**（@ `ccd8f56`）: `docs/03_API仕様/04_バッチ一覧.md`、11 コマンドのコード `sources/conciergesv-develop/src/Command/`＋`sources/eminel_sv_lib-develop`（PointInfinity、Push、共通テーブル）、cron: `docs/02_詳細設計/10_バッチ処理/*.txt`（＋ tgz 内 shell）
- **`eminel_gw_project`**（@ `788b438`）: `docs/eminel/` — 統合要件定義書 v1.2（F-ES-01/03/04/07〜10、F-AD-08、3-2・3-5 節）、`1_product/10_feature_list.md`、`1_product/11_business_process/readme.md`、`2_management/22_decisions.md`（6/10 決定）、`2_management/20_open_issues.md`（CLD-05/06/07、SVC-03）、合宿 Day3 議事録、アプリ要件（A03/B05/D03）、管理画面 spec（[G]/[I]）；`docs/eminel-smart/`（ESTA 調査資料6ファイル — ⚠️ 実コードとの差異6点は付録A参照）
- **`syp-eminelstandard-backend`**（@ `dc39aa39`、branch `gw-syp-dev`）: `template*.yaml`、`src/functions/**`、`src/layers/common/nodejs/**`、`src/statemachine/*.asl.json`
- **`syp-eminelstandard-web-admin`**（@ `e550326`、branch `gw-syp-dev`）: `pages/`、`components/`、`services/`、`stores/`、`constants/`、`locales/`
- **`syp-eminelstandard-app-syp-dev`**（snapshot・git 管理外）: `pubspec.yaml`、`lib/server/rest_client/*`、`lib/presentation/pages/*`、l10n
- **QAデータベース（Notion）** — いずれも参照日 2026-08-04 時点で回答中。再引用時は原ページの最新状態の確認をお願いしたい: 「旧Eminel基盤継承＋EMINEL-smartサーバーは独立デプロイの確認」（回答者: swan（mui））・「旧EMINEL調査範囲（conciergesv/eminelsv）とhemssv対象外の確認」（回答者: swan（mui））・「管理画面は独立か共通か（切替モード追加）の確認」（回答者: masao takahashi（mui））
