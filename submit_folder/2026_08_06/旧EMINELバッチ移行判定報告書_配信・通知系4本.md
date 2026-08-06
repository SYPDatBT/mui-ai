# 旧EMINELバッチ移行判定報告書 — 配信・通知系（4本）

## 1. 管理情報

| | |
|---|---|
| 作成日 | 2026-08-06（調査実施日: 2026-08-04） |
| 作成者 | Bui Trong Dat（SYP）＋AI調査支援 |
| 位置づけ | 本書は、旧EMINELバッチ移行判定（全11本・3グループ）を分冊化した**3分冊のうちの1冊**であり、**配信・通知系4本（#1〜#4）** を対象とする。他分冊: 「外部連携・受信系（Xzilla取込）3本（#5〜#7）」「CSV・ZIPエクスポート系4本（#8〜#11）」。バッチ番号 #1〜#11 は全11本の通し番号であり、分冊間および日本語版／ベトナム語版の間で共通 |
| 目的 | `legacy_eminel_docs/docs/03_API仕様/04_バッチ一覧.md` のうち **配信・通知系** の4バッチ（いずれも旧システムの `conciergesv` 上で稼働）について、e-smart 既存実装の有無を実コードで確認し、`eminel_gw_project/docs/eminel` の E-GW 要件と照合のうえ **流用・新規・廃止** を判定する |
| 対象リポジトリ | `legacy_eminel_docs` @ `ccd8f56` ・ `eminel_gw_project` @ `fbc0af0`（調査実施は `788b438` 時点 — 差分の扱いは補足参照）・ `syp-eminelstandard-backend` @ `dc39aa39`（branch `gw-syp-dev`）・ `syp-eminelstandard-web-admin` @ `e550326`（branch `gw-syp-dev`）・ `syp-eminelstandard-app-syp-dev`（snapshot・git管理外） |
| 判定区分 | **流用** = e-smart の既存実装・機構を利用（工数ゼロの意ではない — §3）・ **新規** = E-GW 向けに新規実装 ・ **廃止** = 移植せず、既存機構または新方針で代替 |
| 凡例 | **確実** = 資料・コード上で直接確認済み ・ ***推定*** = 根拠ある推測（未確定 — 最終判断には使わない）・ 🔍 = 出典（パスは `sources/` 起点、行番号は上記コミット時点のもの）・「grep 0件」= 対象コード全体を検索してヒットなし |

補足（引用時の注意）:

- e-smart（= ESTA = EMINEL-Smart。同一システムの3呼称）に関する「有り／無し」の記述は、すべて `syp-eminelstandard-backend`・`syp-eminelstandard-web-admin`（branch `gw-syp-dev`）の実コードを直接確認した結果である。
- **`eminel_gw_project` の更新（788b438 → fbc0af0、6コミット）について**: 差分は `docs/eminel/3_requirements/app/`（アプリ要件）配下13ファイル＋ skill ファイル1行のみ。2026-08-06 に全引用を `fbc0af0` で再照合し、本書では **B05（アプリ要件「DR」）・D03（アプリ要件「PUSH通知」）の引用行番号を `fbc0af0` 基準に更新**した。要件内容の変更はなく（B05 は出典表記の整理のみ）、**判定結論への影響はない**。
- app リポジトリのみ snapshot（git 管理外）のため、アプリ側の行番号は新版で変動しうる。
- QAデータベース（Notion — mui との内部QAページ群）の引用3件は、いずれも参照日 2026-08-04 時点で**回答中**（スクリーンショット経由で参照）。再引用の際は原ページの最新状態の確認をお願いしたい。
- スコープ・要件の判定は `eminel_gw_project` @ `fbc0af0` 時点の資料に基づく（T.B.D／QA回答中の論点は本文の該当箇所に明記）。

## 2. 総括（結論）

### 2.1 判定結果一覧（配信・通知系 4本）

| # | バッチ | 旧システムでの処理 | e-smart 既存実装 | E-GW 要件 | **判定** | 詳細 |
|---|---|---|---|---|---|---|
| 1 | `DistributeMonthlyEcoPointsCommand` | 月次で「設定温度の月平均 ≤22℃」の世帯に 250 ポイント付与（PointInfinity = 北ガスのポイントサービス — 連携） | **一部あり** — ポイント／バッジ基盤＋PointInfinity 直接連携は実装済み。計測データからの判定ロジックはなし | 必要（F-ES-04 エコ暖房ポイント／F-ES-09 PI連携。必須 2026 — 劣後との矛盾は質問表〔北ガス様向け質問一覧・送付前〕・質問2に記載済み） | **廃止するもの: 旧バッチの PHP コード。流用: ポイント／バッジ基盤＋PI連携（そのまま利用）。新規: エコ暖房判定ロジックのみ** | §4.2 ・ 確実 |
| 2 | `PublishRegularEcoMissionsCommand` | 19種の省エネアドバイスを判定条件付きで配信（季節固定 cron） | **なし**（grep 0件）— Tip（エコライフのコツ — 管理者手動作成コンテンツ）のみで、判定エンジンはなし | 必要・2026スコープ（F-ES-03 省エネアドバイス — 必須） | **旧バッチ＋19本の固定 cron＋10 Publisher のコードは廃止。新規 = 判定エンジン＋管理画面からのスケジュール設定**（spec [G] = 管理画面機能仕様「省エネアドバイス」。15種→7種の集約は未決事項 CLD-06 待ち）。配信の「出口」（ターゲティング＋Push＋ポイント）は既存 Tip パターンを流用 | §4.3 ・ 確実 |
| 3 | `DispatchPushMessagesCommand` | 毎分、DB キューから中継サーバー（PushCore）経由で FCM（スマホへの Push 通知サービス）配信 | **あり（完備）** — FCM 直接送信＋トークン管理＋Push 配信6系統 | 必要（Push 2026） | **廃止するもの: 旧バッチ＋DB キュー＋毎分 cron＋中継サーバー PushCore（再構築しない）。存続するもの: Push 送信業務そのもの。代替: e-smart の FCM 直接送信基盤**。旧システムは通知種別の棚卸しにのみ参照 | §4.4 ・ 確実（PushCore→FCM 転送のみ*推定*） |
| 4 | `ControlDrOperationCommand` | 毎分、DR（デマンドレスポンス — 需要抑制要請）指令をユーザー操作に見せかけて DB へ書き込み、GW がポーリング取得 | **別方式の DR 基盤あり** — メーカークラウド直結機器をサーバー主導で制御。GW 経由の経路はなし | 必要だが**劣後（2027/4 以降）** | **2026年は実装なし**（唯一のアクション = 「GW が DR 状態を保持するか」の決着 — 質問表・質問5）。**2027年に e-smart DR 基盤上で新規**（DR イベント層は全面流用・機器制御分岐のみ追加）。「アプリ操作への偽装」は一切継承しない | §4.5 ・ 確実 |

**一覧の読み方（3点）**:

- **確実／*推定*** のラベルは**事実部分**（旧システムの挙動、e-smart の有無、スコープ）の確度を示す。「判定」列は常にレビュー用の提案である。本書の4本は事実部分がいずれも確実（#3 の PushCore→FCM 転送のみ、PushCore 本体のコードがリポジトリにないため*推定*）。
- 本報告は「何を作る／何を流用する」の判定までであり、**工数は未見積**（方針どおり 1バッチ = 1タスクの Notion 分割時に見積り予定 — §3）。
- 対象4本の範囲外への示唆: e-smart は**事前集計を一切持たない**（アプリの月次レポートは要求の都度 TagTag API〔北ガスの会員基盤 API〕へ転送するだけで保存しない — 🔍 `syp-eminelstandard-backend/src/functions/api-dashboard/get-monthly-report-of-user.ts:21`）。したがって E-GW の**集計・計算系**グループ（バッチ一覧の別グループ、本書対象外）にも流用できる既存資産はない見込み。

### 2.2 スペック確定を待たず即時対応する2点

1. **「既存システムを使い続けたほうがいい機能」リストの報告**（全分冊共通のアクション） — これはページ名ではなく、QA「旧Eminel基盤継承＋EMINEL-smartサーバーは独立デプロイの確認」（swan（mui）・回答中）**内の設問**「ただし既存システムを使い続けたほうがいい機能があれば教えてほしいです」を指す。回答前に「既存システム」の指す対象の確認が必要。回答案は2部構成:
   - ① 旧EMINEL: **現状のまま使い続ける価値のあるバッチはなし**（全11本を通した結論 — 本書の4本を含む）。
   - ② e-smart: **4候補** — Push 基盤（FCM）、ポイント／バッジ基盤＋PI連携、Xzilla SFTP→S3→DynamoDB 受信基盤、管理画面ダウンロード／エクスポート機構（前2者は本書 #3/#1 の判定根拠。後2者は他分冊の対象）。
2. **未決2件のフォロー**: CLD-06（アドバイス15種→7種集約の未決事項 — #2 の種別数を決める）、ポイントの必須／劣後矛盾（質問表・質問2に記載済み — #1 のスコープを決める）。

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
- **それ以外のバッチはすべて EventBridge Scheduler のスケジュールを動的生成**する方式。大半は one-shot（一時点だけ発火し、`ActionAfterCompletion.DELETE` により実行後自動削除される単発スケジュール — 共通関数 🔍 `src/layers/common/nodejs/services/put-schedule.ts:18-33`、発火時刻の式は `src/layers/common/nodejs/utils/date-utils.ts:117` で組立て）。
  - (a) 管理者がお知らせを作成 → API 側で配信スケジュールを登録（`src/functions/api-news/common.ts:207-209`）。
  - (b) 配信バッチが完了 → 次の Push 送信スケジュールを登録（`src/functions/batch-send-news-complete/app.ts:72-80`）。
  - (c) ユーザーのオートメーション（アプリ内の機器自動化ルール）のみ繰り返し型 — ルール毎の週次 cron を動的生成し、自動削除はしない（`src/functions/api-automation/common.ts:115, 167-175`）。
  - (d) 毎分ポーリングは存在しない（grep `rate(`: 0件）。
- **E-GW への含意**: spec [G]（管理画面機能仕様「省エネアドバイス」`4_spec/admin/G_energy_advice.md`）の G-A-02（管理画面からアドバイスの定期配信スケジュールを設定 — 旧来の cron 固定方式では不可能だった要件）は、このスケジュール動的生成方式により技術的な解が既に基盤側にあると言える（特にオートメーションの繰り返し型は「API から変更できる定期スケジュール」の実例）。

**SYP の担当範囲**: QA「旧EMINEL調査範囲（conciergesv/eminelsv）とhemssv対象外の確認」（swan（mui）・回答中・2026-08-04参照）の要旨 — `conciergesv`/`eminelsv` は SYP の**調査**対象であり、旧システム上で開発を続ける範囲ではない。GW との通信は mui 開発の HEMS-SV（m2-cloud。旧システムの `hemssv` とは別物 — 名称が類似しているのみ）経由となり、スペックは後日共有予定。

**2026-06-10 のスコープ決定**（決定ログ登録済み）: 必須 = 暖房機能／暖房制御／照明アドバイス※／ポイント連携／グルーピング・レポート。劣後（2027/4〜）= 複合制御・DR・ダッシュボード・バッジ等。※「照明アドバイス」は省エネアドバイスの誤記と思われる（*推定*）。

- 🔍 `eminel_gw_project/docs/eminel/2_management/22_decisions.md` 30–31 行
- 機能一覧（`docs/eminel/1_product/10_feature_list.md`）の劣後列の凡例に注意: **✅ = 2027 へ繰越可**（スコープ内の意ではない）、空欄 = 今期必須。

**§4 の実施主体**: 特記のない限り実施者は **SYP**、実装は branch `gw-syp-dev` 上。リポジトリ名のないパスは `syp-eminelstandard-backend`、管理画面側は `syp-eminelstandard-web-admin`。「確認／決着」系のステップは §5 の経路による。本文中の人名（敬称略）: swan・masao takahashi（いずれも mui — QAデータベース回答者）、kihara（mui — GW ハード／ファームウェアリード）。

## 4. バッチ別判定詳細

（表記の約束: 旧システムコードのパス `…/src/Command/` は `legacy_eminel_docs/sources/conciergesv-develop/src/Command/` の略。「cron:NN行」は `legacy_eminel_docs/docs/02_詳細設計/10_バッチ処理/mng-webap_cron設定_20241029.txt` の行番号。**コード引用内の日本語注記コメントと `...` は本書が付した注釈・中略記号**であり、原文コードの一部ではない。）

### 4.1 グループ共通: 新旧対応表

本グループの各要素が新旧システムのどこに位置するかの一覧。e-smart 側のテーブル名は各 handler 内の環境変数定数 `TABLE_*` で確認済み。

| 要素 | 旧システム（`conciergesv` — PHP/PostgreSQL） | 新システム（e-smart/E-GW — Lambda/DynamoDB） |
|---|---|---|
| Push 送信経路 | DB キュー `push_message_destinations` を毎分 cron でページング取得（500件/ページ）→ 中継サーバー PushCore（`localhost:54650`）→ FCM（*推定*） | 前処理 Lambda が対象者を 10,000件/ロットに分割して S3 へ → `batch-push-notice` が最大100並列で **firebase-admin から FCM へ直接送信**（DB キュー・中継サーバーなし） |
| Push トークン管理 | `push_message_destinations` レコードに紐づく device_token／FCM トピック | `TABLE_MOBILE_TOKEN_MANAGEMENT`（アプリが API `user/save_mobile_token` で登録・無効トークンは送信時に自動削除） |
| Push 受信可否設定 | —（本調査範囲では未確認） | `TABLE_USER_SETTING`（送信時に opt-in フラグを確認 — `push-notice-to-user.ts:19, 35-60`） |
| ポイント記帳 | `s_141`（`ConEcoPoints` — 年度単位で加算）＋`ConPointLinkLogs`（付与履歴 — 重複防止の根拠） | `TABLE_POINT_BADGE_STATS`（イベント毎キーで重複防止）＋`TABLE_USER_BADGE_SUMMARY`（累計）＋`TABLE_SYSTEM_STATS`（伝票番号のアトミックカウンター） |
| PointInfinity 連携 | `eminel_sv_lib-develop/src/PointInfinity/PointInfinity.php`（CP932 フォーム＋XML 応答） | Lambda `give-point-to-point-infinity`（Shift_JIS フォーム＋XML 応答 — 同系統プロトコル）＋残高照会 `get-point-quantity-from-point-infinity` |
| 省エネアドバイス | 19本の固定 cron ＋10 Publisher クラス → `ConEcoMissions`／`ConEcoMissionDestinations`（アドバイス本体＋宛先）＋`PushMessages`／`PushMessageDestinations`（Push 登録） | **存在しない（#2 で新規実装）**。最も近い既存 = Tip（`TABLE_TIP_STATS`／`TABLE_TIP_USER_ACTION`＋one-shot 配信チェーン） |
| DR 指令 | `ConDrOperations`（DR 指令設定）→ 毎分 cron が `instructions`（宅外制御指示）へ書込み → GW が `hemssv` 経由でポーリング取得 | `TABLE_DR`（イベント）＋`TABLE_DR_USER_ACTION`（参加者・制御前状態）＋`TABLE_DR_STATS`（統計）→ サーバーが `controlDevice` でメーカークラウドを直接制御（GW 経由なし） |
| バッチの起動 | `/etc/cron.d/eminel-mng-webap` の固定 cron（毎分〜月次） | 静的 `ScheduleV2` 3本＋one-shot／繰り返しスケジュールの動的生成（§3） |

### 4.2 #1 `DistributeMonthlyEcoPointsCommand` — エコ暖房ポイント月次付与

**バッチの目的**: 暖房の設定温度を控えめ（月平均 22℃ 以下）にして省エネを実践した世帯へ、毎月自動でポイント特典を付与する — ユーザーの省エネ行動に報酬を返す機能。

**判定 — 廃止・流用・新規の内訳**: **廃止 = 旧バッチの PHP コード**（移植しない）。**流用 = ①PI 直接連携＋②ポイント／バッジ共通経路**（現状のまま利用 — 重複防止・トランザクション・ロールバック込み）。**新規 = ③計測データからの判定ロジックのみ** — 差分方式の方針どおり。（①②③の番号は後述「e-smart 既存実装」の項目に対応。）

**この判定の理由**:

- e-smart には PI 直接連携（Lambda `give-point-to-point-infinity`）とポイント付与の集中経路（`givePointBadgeForUser` — 重複防止・トランザクション・ロールバック込み）が実装済みで、旧バッチの中核機能と同型であることをコードで確認した。
- 一方、計測データから対象世帯を判定するロジックは e-smart のどこにも存在しない（ポイント経路内の grep `energy|usage`: 0件）— 実装の空白はここだけ。
- 方針（合宿 Day3 — §3）はコード移植ではなく作り直しであり、旧 PHP コードを残す理由がない。
- 合宿 Day3 の見立て「ESTAサーバーに既に実装がある可能性が高い → 差分があればやる」とも一致する。

**旧システムの流れ**（確実）:

```
cron 毎月1日 17:00（cron:113-114）
    ▼
DistributeMonthlyEcoPointsCommand
    ├─ 読取: s_104（ConSensorMonthlyValues — 月平均センサー値）……設定温度の前月平均 ≤22.0℃ の世帯を抽出
    ├─ 読取: ConPointLinkLogs（付与履歴）……付与理由キーで当月付与済みを除外（重複防止）
    ├─ 書込: s_141（ConEcoPoints — エコポイント）……1件 250pt を年度単位（4月起点）で加算
    ├─ 書込: ConPointLinkLogs ……付与履歴を記録
    └─ 外部呼出: PointInfinity API ……同一トランザクション内。失敗時は当該顧客分をロールバックし後続は継続
```

対象抽出クエリの核心部 — 🔍 `…/src/Command/DistributeMonthlyEcoPointsCommand.php:89-100`:

```php
->matching('ConSensorMonthlyValues', fn(Query $q) => $q
    ->where([
        'ConSensorMonthlyValues.' . ConSensorMonthlyValue::C_DEVICE_TYPE => ROOM_TEMP_SETTING,  // 「設定」温度
        'ConSensorMonthlyValues.' . ConSensorMonthlyValue::C_ROOM_ID => 0,
        'ConSensorMonthlyValues.' . $sensorMonthlyValuesColName . ' <=' => 22.0,  // 前月平均 ≤ 22.0℃
    ]))
->notMatching('ConPointLinkLogs', fn(Query $q) => $q
    ->where(['reason' => $pointLinkReason]))  // 'monthly_eco_points_YYYYMM' — 重複付与を防止
```

**旧システムの詳細**（確実）:

- ポイント値は定数 `BENEFIT_POINTS = 250`（同:33）。付与は同:116-188 — **同一トランザクション内で PointInfinity API を呼び出し**、PI 失敗時は当該顧客分をロールバックして後続顧客の処理は継続。
- 操作テーブル（`fetchTable` 宣言 同:48-51）: `ConCustomers`・`ConSensorMonthlyValues`（`s_104`）・`ConEcoPoints`（`s_141`）・`ConPointLinkLogs`。
- **コードと cron は通年・毎月実行で季節条件なし** — E-GW の A03（アプリ要件書「ポイント」セクション）が現行仕様として記す「12〜3月」と食い違いがある。スペック確定時に指摘が必要（対応ステップ1）。

**e-smart 既存実装 — 一部あり**（確実。パスは `syp-eminelstandard-backend/` 起点）:

- ① **PointInfinity 直接連携**: 専用 Lambda `src/functions/give-point-to-point-infinity/app.ts`（宣言 `template.yaml:3282`、secret 同:3289）。
  - 接続情報・各種 ID は Secrets Manager から取得（app.ts:15）、付与理由（FUYO_RIYU — PI へ送る「付与の理由」項目）は Shift_JIS へ変換して送信（同:35-39）、応答は XML で `<SYORI_STS>` = `000` が成功（同:50, 56）、リクエストは POST フォーム（同:92, 96）。
  - → 旧システムと**同系統のプロトコル**（旧: CP932 フォーム＋XML、URL `if0200.do`〔設計資料上の IF 名は IF0200〕 — `legacy_eminel_docs/sources/eminel_sv_lib-develop/src/PointInfinity/PointInfinity.php:39, 65-71, 85-98`・同 `Api/InterfaceCode.php:20`。なお文字列 "IF0200" は backend 側には出現しない — 資料上の名称）。
  - 残高照会 Lambda `src/functions/get-point-quantity-from-point-infinity/app.ts`（GET＋`<ZNDK>` タグ — 同:32, 79。secret は `template.yaml:2629`）も併設。
- ② **ポイント／バッジ付与の集中経路**: `src/layers/common/nodejs/business-logic/give-point-badge-for-user.ts:57` の `givePointBadgeForUser()` — すべての付与箇所が経由する共通関数。
  - イベント毎の一意キー `pointBadgeStatsSk`（例 `login#2026-08`、`dr#<id>`）で**重複付与を防止**（同:69 — 記録先は `TABLE_POINT_BADGE_STATS`）。
  - DynamoDB トランザクションで記帳（`TABLE_POINT_BADGE_STATS`＋`TABLE_USER_BADGE_SUMMARY`）し、PI 呼び出し失敗時は**ロールバック**（同:296-303 — 旧システムと同じパターン）。伝票番号（DENPYO_NO）は `TABLE_SYSTEM_STATS` 上のアトミックカウンターで採番（同:390-409、テーブル名は同:392）。
  - 関連モデル: `PointBadgeMaster`／`PointBadgeStats`／`UserBadgeSummary`（`src/layers/common/nodejs/models/`）。現在の呼び出し元: 月初回ログイン、Tip 既読（`api-tip/read-tip.ts:68`）、アンケート回答（`api-survey/answer-survey.ts:346`）、DR 終了（`batch-end-dr/app.ts:86`）、機器連携、会員取込後、アプリ登録完了・お客さま情報入力・オートメーション作成等のチェックリスト達成 など。
- ③ **ないもの**: **計測データからの判定ロジック** — ポイント付与経路にセンサー系データは一切関与しない（ポイント経路内の grep `energy|usage`: 0件）。e-smart には「GW 計測データ」という概念自体がまだない。

**E-GW 要件**: F-ES-04（エコ暖房ポイント）＋ F-ES-09（PointInfinity 連携）。ポイント連携は 6/10 決定で**必須 2026** — ただし機能一覧では ✅劣後 が付いており矛盾（質問表〔北ガス様向け質問一覧〕・質問2に記載済み。E-GW でのポイント値・条件も未確定 — A03 要確認）。合宿 Day3 の見立て「バッチが実態。ESTAサーバーに既に実装がある可能性が高い → 差分があればやる」は、今回コードで裏付けが取れた。

- 🔍 `eminel_gw_project/docs/eminel/3_requirements/00_integrated_requirements_v1.2.md` 409, 414, 675–691 行 ・ `22_decisions.md:31` ・ `10_feature_list.md:93, 95` ・ 合宿 Day3 議事録 125 行 ・ `A03_point.md:48-102`

**新方式の流れ（提案）**:

```
GW 計測（設定温度）──HEMS-SV（m2-cloud — mui 開発の GW 通信サーバー）経由──▶ 世帯別月平均テーブル（新設・旧 s_104 相当 — 集計系グループと連携）
    ▼ 毎月1日発火（template.yaml に静的 ScheduleV2 を新設）
判定 Lambda（新規 — 上記③）……月次テーブルを走査し閾値以下の世帯を抽出
    ▼ givePointBadgeForUser(userId, 'eco_heating#YYYYMM', …)
give-point-badge-for-user.ts（流用 — 上記②）
    ├─ 重複防止: TABLE_POINT_BADGE_STATS   ├─ 記帳: TABLE_USER_BADGE_SUMMARY   └─ 伝票採番: TABLE_SYSTEM_STATS
    ▼
give-point-to-point-infinity Lambda（流用 — 上記①）──POST──▶ PointInfinity ……失敗時はトランザクションをロールバック
```

**対応ステップ**:

1. QA／A03（アプリ要件書「ポイント」）経由で業務スペックを確定する: ポイント値（250 維持か）、閾値（22℃か）、12〜3月の季節限定の有無（上記のコード vs A03 の食い違いを指摘）、必須／劣後矛盾の決着（質問表・質問2）。
   - 理由: 差分方式で新規実装するのは③のみであり、その③の仕様パラメータがすべてここで決まる。食い違いを放置すると判定 Lambda の仕様が確定できない。
2. HEMS-SV（m2-cloud）スペックの共有を待ち、GW 計測の設定温度データがサーバーへ届く経路を確認する。DynamoDB 上に**世帯別月平均の蓄積テーブル**を設計（旧 `s_104` 相当 — 集計系バッチグループの管轄のため当該グループと連携）。
   - 理由: e-smart には GW 計測データの受け皿が存在しない（③）。判定の入力となる月平均テーブルがなければステップ3が動かない。集計系グループとの連携は二重設計の防止のため。
3. 新規の判定 Lambda を実装する（`src/functions/` 配下に新設 — 命名は既存 `batch-*` 慣例に従う）: 月次テーブルを走査 → 閾値以下を抽出 → `givePointBadgeForUser(userId, 'eco_heating#YYYYMM', …)` を呼ぶ。追加は新しい付与理由（FUYO_RIYU）の登録のみ — `src/layers/common/nodejs/variables/constants.ts`（雛形: 同:1756-1762）。
   - 理由: 重複防止／トランザクション／PI連携／ロールバックは `givePointBadgeForUser` が既に備えるため、新規は「判定して呼ぶ」薄い層だけで済む。
4. スケジュール: `template.yaml` に月次の静的 `ScheduleV2` を1本追加（§3 の静的3本の書式に倣う）。
   - 理由: 毎月1日の固定周期であり、one-shot（管理者操作を起点とする動的登録）に載せる契機がない。静的スケジュールが最も単純で保守しやすい。
5. テスト: 月次ダミーデータ投入 → 2回連続実行で**重複付与なし**を確認、PI エラー模擬で**ロールバック**を確認、同一データでの旧システムクエリ手動実行結果と付与件数を突合（テスト = mui／実装 = SYP の分担前提）。
   - 理由: 本バッチの実リスクは「重複付与」「PI 失敗時の不整合」の2点に集約される。旧クエリとの突合で判定条件の解釈誤り（設定温度 vs 実測温度など）も検出できる。

### 4.3 #2 `PublishRegularEcoMissionsCommand` — 省エネアドバイス定期配信

**バッチの目的**: 各世帯の使い方（暖房の使いすぎ、タイマー設定忘れなど）を判定条件で選別し、その世帯に合った省エネアドバイス（現行19種）を自動配信する — ユーザーが省エネ行動に気づくきっかけを作る機能。

**判定 — 廃止・流用・新規の内訳**: **廃止 = 旧バッチ・19本の固定 cron・10 Publisher の PHP コード**（判定式という業務知識のみ [G] 経由で継承）。**流用 = 配信の「出口」**（ターゲティング＋Push＋ポイントの Tip パターンと one-shot 配信チェーン）。**新規 = 判定層（アドバイスエンジン）＋管理画面からの定期配信スケジュール設定**。

**この判定の理由**:

- e-smart にアドバイス判定エンジンが存在しないことを grep で確認（実ヒット0件）— 流用元がない以上、判定層は新規にならざるを得ない。
- E-GW 要件（spec [G] = 管理画面機能仕様「省エネアドバイス」）は「管理画面から変更できる定期配信スケジュール」を要求しており、cron 直書き19本の旧構造ではこの要件を満たせない — 構造ごと廃止が必要。
- 配信・Push・ポイントの「出口」は Tip パターンとして e-smart に完備しており、新規範囲を判定層に限定できる。
- 判定式という業務知識は [G] に抽出済みのため、旧コードを残さなくても失われない（旧コードはクロスチェック用）。

**旧システムの流れ**（確実）:

```
cron 19行（cron:84-102）……日時固定。15行 = 配信月を季節で限定、4行（id 1/2/3/19）= 通年毎月実行
    ▼ 25_PublishRegularEcoMissions_idN.sh（--eco-mission-id 1〜19）
PublishRegularEcoMissionsCommand ──▶ 10 クラスの Publisher へルーティング
    ├─ 判定: 種別毎の条件で対象世帯を抽出（平均超過・ECO モード未使用・タイマー設定忘れ・暖房比率・契約記念日…）
    ├─ 書込: ConEcoMissions＋ConEcoMissionDestinations（アドバイス本体＋世帯毎の宛先）
    └─ 書込: PushMessages＋PushMessageDestinations（Push 登録 — 対象抽出型は schedule = 1分後）
         ▼
       実送信は #3 DispatchPushMessagesCommand（§4.4）が毎分キューを浚って実施
```

アドバイス書込みと Push 登録が同一トランザクションで行われる核心部 — 🔍 `…/src/Command/PublishRegularEcoMission/EcoMissionPublisher.php:142-150`:

```php
foreach ($this->PushMessageDestinations->createByEmsSp($emsSp) as $pd) {
    $pd->push_message_id = $pushMessage->id;
    $pd->schedule = FrozenTime::now()->addMinutes(1);   // Push は「1分後発火」で登録（実送信は #3）
    $pushMessageDestinations[] = $pd;
}
...
$this->ConEcoMissionDestinations->saveManyOrFail($ecoMissionDestinations);
$this->PushMessageDestinations->saveManyOrFail($pushMessageDestinations);
```

**旧システムの詳細**（確実）:

- コマンドは1本で `--eco-mission-id` オプション（1〜19）付きで実行。（フォルダには 11 ファイルあるが 1 つはオプションクラス。`04_バッチ一覧.md` の「11種Publisher」はこれを含めた数え方。）
- 操作テーブル（`EcoMissionPublisher.php:7-13, 30-34` の宣言）: `ConEcoMissions`・`ConEcoMissionDestinations`・`ConRegularEcoMissions`（アドバイス定義マスタ）・`PushMessages`・`PushMessageDestinations`。
- *3つの数の関係: 19 = 現行アドバイス種別数（mission-id）→ 共用の 10 Publisher クラスで処理。15 = CLD-06（アドバイス集約の未決事項）で集約検討時に記された「約15種」。集約先の案 = 7種＋エコ暖房ポイント。*
- 🔍 `…/src/Command/PublishRegularEcoMissionsCommand.php:54-140` ・ `…/src/Command/PublishRegularEcoMission/EcoMissionPublisher.php:60-82, 112-152`

**e-smart 既存実装 — なし**（確実）: `src` 全体で grep `advice|アドバイス|mission|ミッション|判定` → **実ヒット 0件**（ヒットはすべて `permission` の部分一致）。

- 最も近いのは **Tip（エコライフのコツ）** だが、これは管理者が手動作成するコンテンツの配信である（🔍 `src/layers/common/nodejs/models/Tip.ts:4-22`: `body_tip` = 管理画面で編集する本文、`target_type` = ALL／属性／CSV の3種の静的ターゲティングのみ（`batch-send-tip-preprocessing/app.ts:43-50`）、`point_quantity` = 既読時の付与ポイント（`api-tip/read-tip.ts:68` — 記帳先は `TABLE_TIP_STATS`／`TABLE_TIP_USER_ACTION`））。
- **世帯のエネルギーデータを読んで配信可否を判定するフィールド・関数は存在しない**（`api-tip` 内の grep `energy|usage`: 0件）。つまり旧システムの個別判定型「アドバイスエンジン」に相当するものは e-smart にない。

**E-GW 要件**: 2026 スコープ（F-ES-03 省エネアドバイス — 機能一覧で ✅ なし = 今期必須。6/10 決定の「アドバイス」行）。要件は旧システムと**異なる**: spec [G]（管理画面機能仕様「省エネアドバイス」）は管理画面から変更可能な定期配信スケジュールによる自動配信を要求（現行は cron 直書きの固定スケジュールで管理画面から変更不可 — Day3 で「いけてない」とされた典型例と考えられる）。15種→7種の集約は未決（CLD-06 未動）、判定式の踏襲可否も T.B.D（G-C-05 — **種別ごとの判定式は [G] に抽出済み**。旧コードはクロスチェック用）。

- 🔍 `4_spec/admin/G_energy_advice.md:18-19, 28-29, 47` ・ `00_integrated_requirements_v1.2.md:632-647` ・ `20_open_issues.md:176-177`

**新方式の流れ（提案）**:

```
[管理画面（web-admin）] アドバイス作成＋定期配信スケジュール設定（G-A-02 — 新規 UI）
    ▼ スケジュール登録（put-schedule.ts — 既存の動的スケジュール機構）
BatchJudgeAdvice（種別毎の判定 Lambda — 新規）……入力: GW 計測／TagTag／Xzilla（ステップ1でマッピング）
    ▼ 対象ユーザーリスト
BatchSendAdvice（新規 — 雛形: batch-send-tip 系）……Advice 受信レコードを新テーブルへ書込み
    ▼ 完了時に Push を one-shot 登録（雛形: batch-send-tip-complete）
BatchPushNotice（既存の Push 基盤 — §4.4）──▶ FCM ──▶ アプリ
```

**対応ステップ**:

1. CLD-06（アドバイス15種→7種集約の未決事項）の7種確定を待つ／早期確定を依頼する（質問表・予備質問1）。並行して [G] G-C-05 の判定式表を精査し、判定式ごとに「必要な入力データ」と「そのデータの E-GW での取得元（GW 計測か、TagTag か、Xzilla か）」をマッピングする。
   - 理由: 種別数（Lambda 本数）と入力データ経路が決まらないと工数も設計も確定しない — このマッピング表が実工数を決める表になる。
2. `Tip` を雛形に新モデル `Advice` を設計（`src/layers/common/nodejs/models/` に追加、対応 interface は `src/layers/common/nodejs/interfaces/`）: `target_type`／`point_quantity`／Push フラグは踏襲して配信経路を再利用＋「判定条件」と**管理画面から設定できる定期配信スケジュール**（G-A-02）を追加。
   - 理由: Tip と同型にすれば配信・Push・ポイントの既存経路（batch-send-tip 系）がそのまま流用でき、新規実装が判定層に集中する。
3. **バッチボーン**（§3 の方針 — 空実装の骨組み）を先行構築: state machine `BatchJudgeAdvice`（種別毎）→ `BatchSendAdvice` → `BatchPushNotice` を one-shot スケジューラで連結。定義追加は `src/statemachine/`（雛形: `batch-send-tip.asl.json`・`batch-push-notice-tip-new.asl.json`）＋`template.yaml` への宣言。既存の news/tip チェーン（`api-news/common.ts:207-209`）が接続の雛形。当初は判定が空リストを返す状態にする。
   - 理由: 方針（1バッチ=1タスク・バッチボーン先行）どおり、判定式が未確定でも配信経路側を先にテスト可能にするため — 結合フェーズ（9月目標）に判定確定を待たず間に合わせる。
4. web-admin 側 UI: `components/tip/tip-form.vue`（付与ポイント／バッジ・ターゲティング・Push のブロックが既存）を雛形にアドバイス管理フォームを作成＋定期配信スケジュール設定部（新規 — [G] G-A-02）。
   - 理由: UI の大半（付与ポイント・ターゲティング・Push 設定）は tip-form に既存であり、純粋な新規は定期スケジュール設定部のみ。
5. ステップ1で確定した種別リストに沿って判定式を実装: 種別ごとに判定 Lambda 1本（`src/functions/` 配下）、出力は対象ユーザーリスト → 既存パターンでアドバイス書込み＋Push キュー登録。
   - 理由: 種別単位の Lambda 分割は「1バッチ=1タスク」の Notion 分割と一致し、CLD-06 の帰結（種別の追加・廃止）に強い構造になる。
6. テスト: 判定式ごとに境界データ一式（閾値の内／外）。結合フェーズ（9月目標 — §3）前に実動確認。
   - 理由: 判定式の境界値誤りはそのまま誤配信（出すべき世帯に出ない／出すべきでない世帯に出る）になるため、境界の両側を必ず踏む。

### 4.4 #3 `DispatchPushMessagesCommand` — Push 送信（毎分）

**バッチの目的**: サーバーで発生したあらゆる通知（アドバイス・DR・レポート等）を、ユーザーのスマホへ Push 通知として届ける共通の「送信口」。旧システムの全 Push はこの1本を通る。

**判定 — 廃止・存続・代替の内訳**: **廃止 = 旧バッチ＋DB キュー（`push_message_destinations`）＋毎分 cron＋中継サーバー PushCore**（いずれも再構築しない）。**存続 = Push 送信という業務そのもの**（E-GW の全通知が必要とする）。**代替 = e-smart の FCM 直接送信基盤**（後述の新方式の流れ） — §3 の前提どおり、独立デプロイ確定時は新環境への同スタック構築となる。

**この判定の理由**:

- e-smart は FCM 直接送信＋トークン管理＋配信ファンアウトを完備しており（コードで確認）、旧バッチが担う機能の全てを既にカバーしている。
- 要件側も同方向 — D03（アプリ要件書「PUSH通知」）が「全要件がESTA既存のため【新規】なし」と明記している。
- 旧構成（DB キュー＋毎分 cron＋中継 PushCore）は e-smart 基盤の「毎分ポーリングなし」方針（§3）と相容れず、PushCore は本体コードすらリポジトリにない。
- ただし D03 の踏襲元「＋現行（通知種別の網羅）」のため、旧システムの通知種別の棚卸しだけは必要（対応ステップ2）。

**旧システムの流れ**（確実）:

```
cron 毎分（cron:79-80）
    ▼
DispatchPushMessagesCommand
    ├─ 読取: push_message_destinations（DB キュー）……期限到来分を 500件/ページでページング取得
    ├─ 検証: device_token／FCM トピックの排他確認（両方あり・両方なしは STATUS_INVALID へ）
    └─ POST: PushCore（中継サーバー localhost:54650 /v2/send-messages）──▶ FCM（*推定* — PushCore 本体のコードはリポジトリにない）
         リトライ 3分間隔・5回で打切り
```

キュー取得とページングの核心部 — 🔍 `…/src/Command/DispatchPushMessagesCommand.php:65-79`、PushCore の接続先 — 🔍 `legacy_eminel_docs/sources/eminel_sv_lib-develop/src/StaticServices/PushMessageService.php:26, 36-39`:

```php
$limit = 500;                                        // :65 — 500件/ページ
$query = $this->PushMessageDestinations->find()      // :68 — DB キューから期限到来分を取得
    ...
    ->contain('PushDeviceTokens')
    ->contain('PushFcmTopics')
    ->where(['status' => PushMessageDestination::STATUS_SCHEDULED,
             'schedule >=' => $startAt, 'schedule <=' => $endAt])
// PushMessageService.php
$this->apiUrl = $this->getPushCoreHost() . '/v2/send-messages';        // :26
return Configure::read('PushCore.Api.host', 'http://localhost:54650'); // :38
```

**旧システムの詳細**（確実）: リトライ設定は `config/push_message.php:4-14`（3分間隔・5回で打切り）。操作テーブルは `PushMessageDestinations`（宣言 :14, 40）。

- 🔍 `…/src/Command/DispatchPushMessagesCommand.php:51-177` ・ cron:79-80

**e-smart 既存実装 — あり（完備）**（確実）:

- ① **トークン管理**: `src/layers/common/nodejs/models/MobileTokenManagement.ts`（`user_id`＋`mobile_token`）。格納先は `TABLE_MOBILE_TOKEN_MANAGEMENT` — アプリが API `user/save_mobile_token` で登録（handler `src/functions/api-user/save-mobile-token.ts`、ルート登録 `api-user/app.ts:58`）。
- ② **firebase-admin による FCM 直接送信＋無効トークン自動削除**: `src/layers/common/nodejs/services/push-notification-firebase.ts:87-97` — `messaging/invalid-registration-token` 等のエラーコード検出時にトークンを `TABLE_MOBILE_TOKEN_MANAGEMENT` から削除。
- ③ **配信のファンアウト**: `src/functions/batch-push-notice/app.ts:17-34`。
  - (a) 前処理で分割済みのユーザーロット（10,000件/ロット — `batch-push-notice-tip-new-preprocessing/app.ts:53`）を S3 から読み、ロット内は最大 100 並列で送信（並列数の定数は `src/layers/common/nodejs/services/push-notice-to-user.ts:21`）。
  - (b) 送信時にユーザーの受信可否フラグを確認（同:35-60 — テーブルは `TABLE_USER_SETTING`、環境変数の宣言は同:19）。
  - (c) `target_screen`／`target_id` はアプリ側の通知タップ時画面遷移と整合（`syp-eminelstandard-app-syp-dev/lib/presentation/pages/main/bottom_navigation_view.dart:473-528`。トークン登録は同:101-111）。
  - (d) Push 配信の state machine は6系統: survey／news／tip／DR新着／DR開始／DR終了（`template.yaml:510/685/815/1889/1927/1965`）。

**E-GW 要件**: **D03（アプリ要件書「PUSH通知」— 状態「レビュー中」・未確定。なお対顧客スライド「要件一覧」上の D3 ステータスは「レビュー前」 — `3_requirements/app/README.md:64`）**に、踏襲元 = **ESTA Push基盤＋現行（通知種別の網羅）**、「全要件がESTA既存のため【新規】なし」と明記。

- 🔍 `3_requirements/app/D03_push.md:5, 7, 29-31, 81-83`

**新方式の流れ（e-smart 既存 — E-GW はこれを利用）**:

```
配信バッチ完了（news／tip／survey／DR の各 state machine — 6系統）
    ▼ one-shot スケジュール登録（batch-send-*-complete）
batch-push-notice-*-preprocessing ……対象者を抽出し 10,000件/ロットに分割 → S3（BUCKET_TEMPORARY）へ JSON 保存
    ▼ ロット毎に起動
batch-push-notice ……S3 のロットを読み、最大 100 並列で送信
    ├─ 受信可否確認: TABLE_USER_SETTING（ユーザーの opt-in フラグ）
    └─ トークン取得: TABLE_MOBILE_TOKEN_MANAGEMENT（API user/save_mobile_token で登録）
    ▼ firebase-admin
FCM ──▶ アプリ（target_screen に従い通知タップで画面遷移）……無効トークンは検出時に自動削除
```

**対応ステップ**（主に「正しく廃止する」ための作業）:

1. 「Push 基盤（FCM）」を独立デプロイ QA のただし書き回答リスト（§2.2-1 — 既存システム継続利用の設問への回答）に含め、mui 様に共用方針を確認する。
   - 理由: Push 基盤は独立デプロイの帰結（Firebase プロジェクトの分離要否）が最も大きく出る機能であり、方針確認を他作業に先行させる必要がある。
2. **旧システムの通知種別の棚卸し**（D03 の踏襲元「＋現行」の部分）: 旧システムが発信する全通知種別（アドバイス19種、DR、見守り〔CLD-05 = 見守り通知実施可否の未決事項 — 保留中〕、レポート…）をリスト化し、種別ごとに「新しいコンテンツ生成元（#1/#2/…）」と「E-GW アプリでの `target_screen`」をマッピングする。成果物は D03 確定時のマッピング表。
   - 理由: D03 は「通知種別の網羅」を現行から踏襲すると明記しており、棚卸しなしには D03 を確定できない。この表は #2（アドバイス）・CLD-05（見守り）の検討にも共用できる。
3. 独立デプロイの場合: E-GW アプリ用 Firebase プロジェクトの新設、新環境への `TABLE_MOBILE_TOKEN_MANAGEMENT` テーブル＋ API `user/save_mobile_token`（`api-user/save-mobile-token.ts` パターン）の構築。
   - 理由: パターンが既存のため、作業は環境設定と Secrets Manager 経由の credential 登録が主で、コードの新規開発はほぼない。
4. `DispatchPushMessagesCommand`／PushCore の移植タスクは**起こさない** — Notion タスク分割時に「廃止、batch-push-notice パターンで代替」と明記し、約46本の母数に誤って算入しないようにする。
   - 理由: 母数に紛れ込むと見積り・進捗率の分母が狂う。廃止判定は Notion 上に明記して初めて効力を持つ。
5. テスト: 実トークンの dev 端末への送信確認、無効トークンの自動削除確認（②）、メッセージ 4096 バイト上限の確認（`constants.ts:223`）。
   - 理由: Push の障害は「届かない」「無効トークンへ送り続ける」「本文超過で切れる」の3類型に集約され、この3項目でそれぞれ検出できる。

### 4.5 #4 `ControlDrOperationCommand` — DR 指令制御

**バッチの目的**: 電力需給の逼迫時などに、DR（デマンドレスポンス — エネルギー事業者からの需要抑制要請）指令として、参加世帯の暖房をサーバー側から自動制御する — 北ガスからの要請をユーザー宅の機器操作に変換する機能。

**判定 — 廃止・実施時期・代替の内訳**: **2026年は実装なし**（唯一のアクションは対応ステップ1の確認のみ）。**廃止 = 旧方式の全体**（毎分 cron・`instructions` 書込み・GW ポーリング・「アプリ操作への偽装」— 偽装は一切継承しない）。**2027年に e-smart DR 基盤上で新規** — DR イベント層（モデル・管理画面・配信・ポイント）は全面流用し、機器制御の新分岐だけを追加する。

**この判定の理由**:

- E-GW 要件上 DR は**劣後（2027/4 以降）**であり（6/10 決定・B05〔アプリ要件書「DR」〕: 26年スコープ = なし）、2026年に実装する根拠がない。
- e-smart に別方式（サーバー主導・メーカークラウド直接制御）の DR 基盤が完備しており、2027年はその機器制御分岐に「E-GW 経由」を1本足すのが最小コスト。
- 旧方式の「アプリ操作への偽装」は旧 GW の仕様制約（アプリ端末以外の指令を無視する）への回避策であり、新アーキテクチャ（HEMS-SV 経由のサーバー主導）では前提ごと消える — 継承する理由がない。
- 唯一 2026 年に動くべきは「GW が DR 状態を保持するか」の決着（質問表・質問5）— GW ファームウェア設計を拘束するため先送りできない。

**旧システムの流れ**（確実）:

```
cron 毎分（cron:76-77）
    ▼
ControlDrOperationCommand（2フェーズ構成。世帯毎に指令衝突を5分回避）
    ├─ 読取: ConDrOperations（DR 指令設定）＋hems_gws（GW 情報）＋t_201（ConDevices — 機器・アプリ端末）
    ├─ 書込: ConDeviceControls（制御履歴）
    └─ 書込: instructions（宅外制御指示 — ECHONET 形式。EPC 80/B0 = 電源／温度変更コード）
         ※ユーザーのアプリ端末からの操作に「偽装」して書き込む
         ▼
       GW が hemssv（旧システムの GW 通信サーバー）経由でポーリング（定期的に取りに来る）→ 宅内機器を制御
```

「偽装」が必要である根拠 — コード内コメント原文 🔍 `…/src/Command/ControlDrOperationCommand.php:171-172`:

```php
// 暖房制御ユニットとユーザのアプリ端末の情報を取得
// ユーザのアプリ端末からの操作のように見せかけないとゲートウェイが指令を無視する
```

**旧システムの詳細**（確実）: 操作テーブル（`fetchTable` 宣言 同:56-61）: `ConDrOperations`・`ConDevices`・`ConDeviceControls`・`ConDeviceStatuses`・`HemsGws`・`Instructions`。`instructions` への書込みは同:210 以降（`ems_sp_no`・`node_id`・`eoj` 等 — ECHONET の機器アドレス指定）。

**e-smart 既存実装 — 別方式の DR 基盤あり**（確実）:

- ① **DR イベントモデル＋制御前状態の保持**: `src/layers/common/nodejs/models/Dr.ts:5-30` — `implement_start_time`／`implement_end_time`（→ one-shot スケジュール登録）、`target_type`（news/tip と同様のターゲティング）、`control_setting`（どの機器に何をするか）、Push 3点セット（新着／開始／終了）、`point_quantity`／`has_badge` — ＋ `DrUserAction.ts:1-14` — `pre_control_status` = **DR 前の機器状態**（終了時の復元用）。格納先: `TABLE_DR`（イベント — `api-dr/create-dr.ts` で確認）・`TABLE_DR_USER_ACTION`（参加者 — `batch-start-dr/app.ts` で確認）・`TABLE_DR_STATS`（統計 — `batch-send-dr-complete/app.ts` で確認）。
- ② **開始／終了バッチ**:
  - (a) `batch-start-dr/app.ts:55-65` が参加ユーザーの機器を `control_setting` に従いサーバーから直接制御し、`pre_control_status` を保存（同:212）。
  - (b) `batch-end-dr/app.ts:82-94` が完走ユーザーへポイント付与（#1 で確認したポイント共通経路 `givePointBadgeForUser` を `dr#<id>` キーで再利用）後、機器状態を復元（同:96-190）。
  - (c) 制御対象は Rinnai／Noritz／Daikin／MUI 赤外線経由のエアコン・ファンコン（`batch-end-dr/app.ts:139-188`）— いずれも**メーカークラウド直結機器で、GW 経由の制御経路はない**。
  - (d) 機器制御の実体は共通関数 `controlDevice`（`src/layers/common/nodejs/business-logic/control-device.ts` — `SERVER_TYPE` = RINNAI／NORITZ／DAIKIN／MUI_CLOUD の4分岐）で、`batch-start-dr/app.ts:81` のローカル関数 `handleControlDevice` が呼び出す。
- ③ **スケジュールの2段構え**: 開始／終了スケジュールは DR 配信完了時に one-shot 登録され（`batch-send-dr-complete/app.ts:127-143`）、配信スケジュール自体は管理者の DR 作成・更新時に登録される（`api-dr/create-dr.ts:111`・`update-dr.ts:149`）。web-admin には DR 管理画面一式（`pages/distribution-management/dr/`＋`components/dr/dr-form.vue` — 1881 行）。

→ e-smart の DR は**サーバー主導で機器を直接制御**する方式であり、旧システムの「DB へ指令書込み → GW ポーリング」方式とは根本的に異なる。

**E-GW 要件**: F-ES-07（暖房DR）/F-ES-08（電力DR）＋ F-AD-08（管理画面の DR 管理） — **劣後・2027/4 以降**（6/10 決定。B05〔アプリ要件書「DR」〕: 26年スコープ = なし）。将来アーキテクチャ: DR はサーバー主導、指令は HEMS-SV（m2-cloud）経由で GW へ。DR 終了方式（サーバーが時刻どおり指令する A 案 vs GW が自律終了する B 案 — GW が状態を持つか）は**未決** — 質問表・質問5。2026年のファームウェア設計を拘束する。

- 🔍 `22_decisions.md:30-31` ・ `B05_dr.md:8, 32-34` ・ 合宿 Day3 議事録 113–122 行（DR発令の詰め込み → 約17項目へ分割）

**新方式の流れ（2027年の姿 — 2026年は実装しない）**:

```
[管理画面（web-admin）] DR 作成・更新（dr-form.vue — 既存）
    ▼ api-dr/create-dr.ts:111・update-dr.ts:149 — TABLE_DR へ保存＋「配信」スケジュールを one-shot 登録
BatchSendDr（配信バッチ — 既存）……対象者へ DR 受信レコード＋Push（DR新着）
    ▼ 配信完了 → batch-send-dr-complete/app.ts:127-143 が start／end の one-shot を登録（TABLE_DR_STATS 更新）
batch-start-dr ……開始時刻に発火
    ├─ handleControlDevice（app.ts:81）→ controlDevice（business-logic/control-device.ts）
    │    ├─ 既存分岐: RINNAI／NORITZ／DAIKIN／MUI_CLOUD（メーカークラウド直接制御）
    │    └─ 新分岐（2027 実装）: E-GW 経由の暖房 — HEMS-SV（m2-cloud）API を呼ぶ
    └─ 制御前状態を TABLE_DR_USER_ACTION の pre_control_status へ保存
batch-end-dr ……終了時刻に発火
    ├─ 完走ユーザーへポイント付与（givePointBadgeForUser — 'dr#<id>' キー）
    └─ pre_control_status に従い機器状態を復元
```

**対応ステップ**:

1. （2026年 — 唯一のアクション）kihara（mui — GW ハード／ファームウェアリード）と社内整理のうえ、北ガス様へ確認: GW が DR 状態を保持してよいか（終了方式 A/B 案 — 質問表・質問5）。
   - 理由: GW ファームウェアは 2026 年に設計・製造されるため、この1点だけは 2027 年の DR 開発まで先送りできない。結果がファームウェア設計を決める。
2. （2027年）「DR イベント」層は全面流用: `Dr`／`DrUserAction`／`DrStats` モデル（`src/layers/common/nodejs/models/`）、管理画面（`pages/distribution-management/dr/`）、ターゲティング、Push 3点セット、終了時ポイント付与。
   - 理由: この層は「どの機器をどう動かすか」に依存しない部分であり、機器が GW 経由になっても変更が不要。
3. （2027年）`control_setting` に新機器種別「E-GW 経由の暖房」を追加 — `controlDevice`（`src/layers/common/nodejs/business-logic/control-device.ts`）に新 `SERVER_TYPE` 分岐を実装し、mui 提供予定の HEMS-SV（m2-cloud）API スペックに従って呼び出す（旧方式の `instructions` 書込み＋ GW ポーリングの代替）。
   - 理由: 既存の4分岐（RINNAI／NORITZ／DAIKIN／MUI_CLOUD）と同列に追加する構造が最小変更で済む。旧方式の毎分ポーリングは e-smart 基盤の「毎分ポーリングなし」（§3 — grep `rate(`: 0件）と相容れない。
4. （2027年）GW 経由暖房機器の `pre_control_status` マッピング（DR 後の復元）— ステップ1の結果（状態を GW が持つかサーバーが持つか）に依存。
   - 理由: 「DR 終了後に元の設定へ戻る」ことは DR 体験の核心であり、復元用状態の置き場所が A/B 案の帰結そのものだから。
5. （2027年）タスク分割は Day3 の方針どおり（Notion 上の約17項目）— 旧システムのような「1バッチ全部盛り」にはしない。
   - 理由: 合宿 Day3 で「DR発令に詰め込みすぎ」と指摘された旧構造の再現を防ぐ。
6. テスト: （2027年）制御分岐の新旧混在（メーカークラウド機器＋GW 経由機器の同時参加）、途中解除、`pre_control_status` 復元の3点を重点確認。
   - 理由: 新分岐追加で最も壊れやすいのは既存4分岐との併走と復元処理であり、DR はユーザーの宅内環境を直接変えるため復元漏れの影響が大きい。

## 5. ご確認・ご相談事項（一覧）

| # | 事項 | 関連 | 対応・経路 |
|---|---|---|---|
| 1 | **2026年 DR アーキテクチャの決着**: GW が DR 状態を保持してよいか（終了方式 A/B 案）— 2026年ファームウェア設計を拘束 | #4 対応ステップ1（2026年唯一の DR アクション — §4.5） | 北ガス様向け質問表・**質問5**に記載済み。送付前に kihara（mui）との社内整理をお願いしたい |
| 2 | ポイントの必須／劣後矛盾＋ E-GW のポイント値 | #1 対応ステップ1（エコ暖房ポイントの業務スペック確定 — §4.2） | 質問表・**質問2**に記載済み。コードと A03（アプリ要件書「ポイント」）の「12〜3月」の食い違い（#1）は A03 スペック確定時に指摘 |
| 3 | アドバイス 15種→7種の集約（CLD-06）＋スケジュール／判定式 spec [G]（管理画面機能仕様「省エネアドバイス」） | #2 対応ステップ1（種別確定と判定式マッピング — §4.3） | 質問表・**予備質問1**に記載済み。スケジュール部分は spec [G] レビュー時に提起 |
| 4 | 「既存システムを使い続けたほうがいい機能」リストの報告（QA 独立デプロイ内の設問への回答。2部構成 — §2.2-1。**全分冊共通のアクション**） | §2.2-1 ・ #3 対応ステップ1（Push 基盤の共用方針確認 — §4.4） | SYP が QAデータベースの該当ページへ直接回答予定 |
| 5 | 見守り通知の実施可否（CLD-05） | #3 対応ステップ2（旧システム通知種別の棚卸し — 見守りが種別リストに残るかを左右 — §4.4） | 質問表・**質問3**に記載済み |

## 付録A. ご参考: ESTA 調査資料（docs/eminel-smart/）と実コードの差異（本分冊関連 3点）

今回のコード照合の過程で、既存の ESTA 調査資料 `eminel_gw_project/docs/eminel-smart/`（6ファイル）と実コードの間に**計6点**の差異を確認した（3グループ全体での合計）。うち本分冊（配信・通知系）に関わるのは以下の3点である。残り3点（基幹取込の実行頻度・会員マージのロック時間・`CsvDownloadHistory` の役割）は外部連携・受信系分冊／CSV・ZIPエクスポート系分冊に記載。同資料を引用する際は実コードの再確認を推奨したい（あわせて資料側の更新もご検討をお願いしたい）。

| 調査資料の記載 | 実コード |
|---|---|
| Push「最大500件/バッチ」（`02_product_overview.md:121`） | 500 件という定数はなし（500件/ページは旧システム側のページングサイズ）。受信者を 10,000 ユーザー/ロットに分割し、ロット内最大 100 並列で送信（§4.4） |
| 「自動化ルール実行（毎分）」（`02_product_overview.md:85`） | 毎分実行はなし — ルール毎に週次スケジュールを動的生成（§3。grep `rate(`: 0件） |
| Lambda ランタイム「Node.js 20.x, arm64」（`02_product_overview.md:49`） | `Runtime: nodejs24.x`（`template.yaml:181`。なお共通レイヤーの CompatibleRuntimes は nodejs20.x のまま — 同:3163） |

## 付録B. 参照資料一覧

- **`legacy_eminel_docs`**（@ `ccd8f56`）: `docs/03_API仕様/04_バッチ一覧.md`、対象4コマンドのコード `sources/conciergesv-develop/src/Command/`（`DistributeMonthlyEcoPointsCommand.php`・`PublishRegularEcoMissionsCommand.php`＋`PublishRegularEcoMission/`・`DispatchPushMessagesCommand.php`・`ControlDrOperationCommand.php`）＋`sources/eminel_sv_lib-develop`（PointInfinity、Push、共通テーブル定義）、cron: `docs/02_詳細設計/10_バッチ処理/*.txt`
- **`eminel_gw_project`**（@ `fbc0af0`。調査実施は `788b438` — B05／D03 の引用行番号は `fbc0af0` 基準に更新済み）: `docs/eminel/` — 統合要件定義書 v1.2（F-ES-03/04/07〜09、F-AD-08）、`1_product/10_feature_list.md`、`2_management/22_decisions.md`（6/10 決定）、`2_management/20_open_issues.md`（CLD-05/06）、合宿 Day3 議事録、アプリ要件（A03/B05/D03＋`app/README.md`）、管理画面 spec（[G]）；`docs/eminel-smart/`（ESTA 調査資料6ファイル — ⚠️ 実コードとの差異のうち本分冊関連の3点は付録A参照）
- **`syp-eminelstandard-backend`**（@ `dc39aa39`、branch `gw-syp-dev`）: `template*.yaml`、`src/functions/**`、`src/layers/common/nodejs/**`、`src/statemachine/*.asl.json`
- **`syp-eminelstandard-web-admin`**（@ `e550326`、branch `gw-syp-dev`）: `pages/`、`components/`、`constants/`
- **`syp-eminelstandard-app-syp-dev`**（snapshot・git 管理外）: `lib/presentation/pages/*`
- **QAデータベース（Notion）** — いずれも参照日 2026-08-04 時点で回答中。再引用時は原ページの最新状態の確認をお願いしたい: 「旧Eminel基盤継承＋EMINEL-smartサーバーは独立デプロイの確認」（回答者: swan（mui））・「旧EMINEL調査範囲（conciergesv/eminelsv）とhemssv対象外の確認」（回答者: swan（mui））・「管理画面は独立か共通か（切替モード追加）の確認」（回答者: masao takahashi（mui））
