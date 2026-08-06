# 調査報告: 配信・通知系（4バッチ #1〜#4）— 新システムへの移植は必要か

| | |
|---|---|
| 対象 | 配信・通知系4バッチ（`legacy_eminel_docs/docs/03_API仕様/04_バッチ一覧.md`・`conciergesv` サーバー）: エコ暖房ポイント（#1）・省エネアドバイス（#2）・Push（#3）・DR（#4） |
| 範囲 | `legacy_eminel_docs`@`ccd8f56` ・ `eminel_gw_project`@`fbc0af0` ・ `syp-eminelstandard-backend`@`dc39aa39` ・ `syp-eminelstandard-web-admin`@`e550326`（branch `gw-syp-dev`）・ `syp-eminelstandard-app-syp-dev`（snapshot）。調査は `788b438` 時点、08-06 に `fbc0af0` で再照合 — 差分は `eminel_gw_project/docs/eminel/3_requirements/app/` のみ、B05/D03 行番号更新済み、結論不変。調査 2026-08-04 ・ 作成 2026-08-06。3分冊の1冊（全11本・番号 #1〜#11 通し・日越共通）— 他分冊: 外部連携・受信系（#5〜#7）、CSV・ZIP（#8〜#11） |
**記号**:

| 記号 | 意味 |
|---|---|
| e-smart = ESTA = EMINEL-Smart | 同一システムの3呼称; hemssv（旧GWサーバー）≠ HEMS-SV（m2-cloud・mui 開発 — 名称類似のみ）; PI = PointInfinity（北ガスのポイントサービス）; TagTag = 北ガスの会員基盤 |
| CLD-05 / CLD-06 ・ [G] ・ 質問表 / QAデータベース ・ 確実 / *推定* / grep 0件 | 未決事項: 見守り / アドバイス15種→7種集約 ・ 管理画面機能仕様「省エネアドバイス」 ・ `qa_kitagas.md`（北ガス様向け・「質問N」）/ mui との内部QA（Notion）・ 直接確認済み / 根拠ある推測 / 全コード検索ヒットなし |
| コード内 `...`・注記コメント | 本書の中略記号・注釈（原文コードではない） |
**目次**: [結論](#ket-luan) ─ I: [§1](#s1) [§2](#s2) [§3](#s3) [§4](#s4) [§5](#s5) ─ II: [§6](#s6)（[#1](#s6-1) [#2](#s6-2) [#3](#s6-3) [#4](#s6-4)）[§7](#s7) [§8](#s8) [§9](#s9) [§10](#s10) [§11](#s11)

## 結論 <a id="ket-luan"></a>
> **#1 エコ暖房ポイント** — ポイント／バッジ基盤＋PI連携を**流用**。**新規は計測データからの判定ロジックのみ**。
> **#2 省エネアドバイス** — 判定エンジン＋管理画面から設定する配信スケジュールを**新規実装**。「出口」は既存 Tip パターンを流用。
> **#3 Push 毎分送信** — **バッチ＋PushCore は廃止・Push 送信業務は存続** — e-smart の FCM 直接送信基盤で代替。
> **#4 DR** — **2026年はコードを書かない**（DR の質問1件の決着のみ）。2027年に e-smart DR 基盤上で新規。「アプリ操作への偽装」は継承しない。
>
> **確定前に確認すべき点は5件**（→ [§3](#s3)）。
# 第I部 — 報告編
## §1. なぜこの結論か <a id="s1"></a>
方針（合宿 Day3・2026-06-25）: 現行バッチは「いけてない」— 作り直し・PHP 移植なし。「流用」= e-smart の機構・基盤の利用（[§7](#s7)）。

| | 旧（`conciergesv`） | e-smart |
|---|---|---|
| 常駐起動 | 固定 cron（毎分〜月次） | 静的3本＋動的 one-shot。毎分ポーリングなし（grep `rate(`: 0件） |
| Push | DB キュー＋PushCore → FCM（*推定*） | firebase-admin で FCM 直接送信、S3 ロット分割 |
| DR | DB へ指令書込み・GW ポーリング —「アプリ操作へ偽装」 | サーバーがメーカークラウドを直接呼出し。DR 前状態の保存・復元つき |
| 基盤 | PHP 8.0 / CakePHP 4.4 / PostgreSQL | TypeScript / Lambda（Node.js 24 — `syp-eminelstandard-backend/template.yaml:181`）/ DynamoDB |

| バッチ | 旧の中核処理 | 要否 | 理由 |
|---|---|---|---|
| #1 | 「設定温度の月平均 ≤22.0℃」世帯の抽出クエリ（`s_104`） | ✅ ロジック継承 | 必須 2026（F-ES-04）— GW 計測データを読む Lambda に書き直す |
| #1 | 付与理由キーによる重複防止 | ✅ 既存あり | `pointBadgeStatsSk` が同役割 |
| #1 | ポイント加算＋PI 呼出し同一トランザクション・ロールバック | ✅ 既存あり | `givePointBadgeForUser`＋PI Lambda が同パターン |
| #1 | 毎月1日の固定 cron | ❌ | 静的 `ScheduleV2` 1本で代替 |
| #2 | 季節固定の 19 本 cron | ❌ | [G] は管理画面から変更可能なスケジュールを要求 |
| #2 | 10 Publisher の種別毎判定 | ✅ 業務は継承 | エンジンは新規; 判定式は [G] に抽出済み |
| #2 | アドバイス書込み＋Push 登録 | ✅ 既存あり | Tip パターンにターゲティング＋Push＋ポイント完備 |
| #3 | DB キュー＋毎分 cron | ❌ | e-smart は S3 ロット・イベント駆動 |
| #3 | 中継サーバー PushCore | ❌ | firebase-admin で直接送信 |
| #3 | トークン管理＋無効トークン処理 | ✅ 既存あり | `TABLE_MOBILE_TOKEN_MANAGEMENT`＋送信時自動削除 |
| #4 | `instructions` へのアプリ操作偽装書込み | ❌ 一切継承しない | 旧 GW 制約への回避策 — 新方式で前提消滅 |
| #4 | GW が `hemssv` 経由ポーリング | ❌ | 2027年は HEMS-SV 経由 |
| #4 | DR イベントの枠組み | ✅ 既存あり | モデル・管理画面・Push・ポイント完備; 「E-GW 経由」分岐追加のみ |
範囲外への示唆: e-smart は事前集計を持たない — 月次レポートは都度 TagTag API へ転送・非保存（🔍 `syp-eminelstandard-backend/src/functions/api-dashboard/get-monthly-report-of-user.ts:21`）→ 集計・計算系グループにも流用資産なし。
## §2. 新システムでの担い先 <a id="s2"></a>

| 仕事 | 担い先 | 種別 |
|---|---|---|
| ポイント付与＋重複防止＋ロールバック | `syp-eminelstandard-backend/src/layers/common/nodejs/business-logic/give-point-badge-for-user.ts:57` | 共通関数 — 既存 |
| PI 呼出し | `syp-eminelstandard-backend/src/functions/give-point-to-point-infinity/`（＋同階層 `get-point-quantity-from-point-infinity/`） | Lambda — 既存 |
| GW 計測データからのエコ暖房判定 | — | 未実装（[§6.1](#s6-1)） |
| コンテンツ配信 → Push | `syp-eminelstandard-backend/src/functions/`（`batch-send-*` → `batch-push-notice/`） | バッチ — 既存 |
| トークン登録 | `syp-eminelstandard-backend/src/functions/api-user/save-mobile-token.ts`（ルートは同フォルダ `syp-eminelstandard-backend/src/functions/api-user/app.ts:58`） | API — 既存 |
| アドバイスエンジン | — | 未実装（[§6.2](#s6-2)） |
| DR イベント | `syp-eminelstandard-backend/src/functions/`（`api-dr/`・`batch-send-dr*`・`batch-start-dr/`・`batch-end-dr/`） | API＋バッチ — 既存 |
| E-GW 経由の機器制御 | — | 未実装 — 2027年に `syp-eminelstandard-backend/src/layers/common/nodejs/business-logic/control-device.ts` へ分岐追加（[§6.4](#s6-4)） |
```
コンテンツ発生（ポイント/アドバイス/DR/news…）──one-shot──▶ 配信バッチ ──▶ 前処理が 10,000件/ロット分割 → S3
    ──▶ batch-push-notice（100 並列）──firebase-admin──▶ FCM ──▶ アプリ（target_screen）
```
思想: 旧 = 固定時刻表＋キュー巡回; 新 = イベントがスケジュールを生み、実行後自動消滅。**命名の罠**（@`dc39aa39` で自ら計数）: `syp-eminelstandard-backend/src/functions/` は **105** フォルダ、うち **81** が `batch-*` 名 — だが静的 `ScheduleV2` は **3本のみ**。「batch- の名前 = 定時実行」と推定してはならない。
## §3. 確定前に確認すべき点 <a id="s3"></a>

| # | 論点 | 旧 | 新／計画 | 重要度 |
|---|---|---|---|---|
| 1 | DR: GW が状態を保持してよいか（A案 サーバー指令 / B案 GW 自律終了）— 2026年ファームウェアを拘束 | GW ポーリング・状態なし | 未決 — 質問5 | 🔴 |
| 2 | ポイント 必須（6/10）vs ✅劣後（機能一覧）＋ E-GW のポイント値 | 250pt・22℃ | 未確定 — 質問2 | 🔴 |
| 3 | 付与の季節: コードは通年、A03 は「12〜3月」 | 通年（確実） | A03 確定時に指摘 | 🟡 |
| 4 | アドバイス 15種→7種（CLD-06）＋スケジュール／判定式 [G] | 19種・固定 cron | 予備質問1; CLD-06 未動 | 🟡 |
| 5 | 見守り（CLD-05） | 旧に存在 | 未決 — 質問3 | 🟡 |
**文面案**（質問 2/3/5・予備質問1 は質問表に記載済み。以下は追加準備分）:
> **（kihara との社内整理 — 質問5送付前）**: 「DR終了方式について、サーバー主導（A案）とGW自律終了（B案）のどちらを前提に質問5を送るか、ファームウェア側の制約を整理させてください。GWがDR状態を保持する場合のメモリ・再起動時の挙動に制約はありますか？」
>
> **（mui 様へ — 独立デプロイ確定時）**: 「独立デプロイとなった場合、Push基盤のFirebaseプロジェクトとPointInfinity接続（credential）は共用できますか、それともE-GW用に新設すべきでしょうか？（QA『旧Eminel基盤継承＋独立デプロイ』のただし書きへの回答と併せて確認したい）」
>
> **（A03 レビュー時 — 論点3）**: 「現行のエコ暖房ポイントは、コード上は通年・毎月実行で季節条件がありません（A03の記載『12〜3月』と食い違い）。E-GWではどちらを正としますか？」
## §4. 誤解されやすい点 <a id="s4"></a>

| 誤解 | 正しくは |
|---|---|
| 「ポイント基盤がある → #1 完了同然」 | 2/3 のみ: PI＋記帳は既存、**計測データからの判定は未実装**（grep `energy|usage`: 0件） |
| 「Tip = アドバイスエンジン」 | Tip は管理者の手動作成＋静的ターゲティング — エンジンは新規作成部分 |
| 「`batch-*` 名 = 定時バッチ」 | 81/105 が `batch-*` 名だが静的スケジュールは 3本（[§2](#s2)） |
| 「#4 = DR をやらない」 | 2026年はコード保留のみ; **質問5だけは保留不可** — 2026年ファームウェアを拘束 |
## §5. 次のアクション <a id="s5"></a>

| # | 内容 | 担当 |
|---|---|---|
| 1 | kihara と終了方式 A/B を整理 → 質問5送付（最優先） | SYP＋PM |
| 2 | QA 独立デプロイのただし書きへ回答: ① 旧EMINEL に使い続ける価値のあるバッチなし; ② e-smart 4候補（本グループ: Push＋ポイント/PI）。⚠️ 回答前に「既存システム」の指す対象を確認 | SYP |
| 3 | 旧通知種別の棚卸し → D03 向けマッピング表（新生成元＋`target_screen`） | SYP（＋アプリ） |
| 4 | [G] G-C-05 判定式の精査: 式ごとの入力データと取得元（GW/TagTag/Xzilla） | SYP |
| 5 | Notion 分割時: #3「廃止、batch-push-notice で代替」、#4「2026年コードなし」と明記 — 約46本に誤算入させない | SYP＋PM |
> **方針**: バッチの廃止 ≠ 業務の廃止 — 業務は e-smart 基盤に載せ替わる。新しく書くのは e-smart が持たない「判定」部分だけ。
# 第II部 — 技術詳細編
*（図表内ではファイル名を短縮表記 — 完全パスは直近の 🔍 行または [§11](#s11) に記載。）*
## §6. バッチ別詳細 <a id="s6"></a>
### 6.1 #1 `DistributeMonthlyEcoPointsCommand` — エコ暖房ポイント月次付与 <a id="s6-1"></a>
**目的**: 設定温度の月平均 ≤22℃ の世帯へ毎月ポイント特典を付与。
**判定**: 廃止 = 旧 PHP コード ・ 流用 = ①PI連携＋②ポイント付与集中経路 ・ 新規 = ③計測データ判定のみ。
**理由**: ①② はコードで確認済み（旧の中核と同型）; ③ は存在しない（grep `energy|usage`: 0件）; 方針は移植なし; Day3 の見立てと一致。
**旧フロー**（確実）— テーブル: `ConCustomers`・`ConSensorMonthlyValues`（`s_104`）・`ConEcoPoints`（`s_141`）・`ConPointLinkLogs`（`fetchTable` :48-51）; PI 同一トランザクション :116-188:
```
cron 毎月1日 17:00（cron :113-114）▼ DistributeMonthlyEcoPointsCommand
    ├─ 読取 s_104 …設定温度の前月平均 ≤22.0℃ の世帯   ├─ 読取 ConPointLinkLogs …付与済み除外（重複防止）
    ├─ 書込 s_141 …年度単位で +250pt（4月起点）＋ 書込 ConPointLinkLogs …履歴
    └─ 呼出 PointInfinity API …同一トランザクション; 失敗 → 当該顧客分ロールバック・後続継続
```
🔍 `legacy_eminel_docs/sources/conciergesv-develop/src/Command/DistributeMonthlyEcoPointsCommand.php:83-104` ・ cron: `legacy_eminel_docs/docs/02_詳細設計/10_バッチ処理/mng-webap_cron設定_20241029.txt:113-114`:
```php
->matching('ConSensorMonthlyValues', fn(Query $q) => $q
    ->where(['...C_DEVICE_TYPE' => ROOM_TEMP_SETTING,                 // 「設定」温度
             '...' . $sensorMonthlyValuesColName . ' <=' => 22.0, ])) // 前月平均 ≤ 22.0℃
->notMatching('ConPointLinkLogs', fn(Query $q) => $q
    ->where(['reason' => $pointLinkReason]))            // 'monthly_eco_points_YYYYMM' — 重複付与防止
```

| 定数／異常系 | 値 |
|---|---|
| ポイント／閾値／重複防止キー | `BENEFIT_POINTS = 250`（:33）; ≤22.0℃ **設定**温度; `monthly_eco_points_YYYYMM`（= 前月） |
| PI エラー | 当該顧客分のみロールバック・後続継続 |
| ⚠️ 季節 | **通年**実行 — A03「12〜3月」と食い違い（[§3](#s3)-3） |
**e-smart**: ① PI連携 既存（確実）— `syp-eminelstandard-backend/src/functions/give-point-to-point-infinity/app.ts`（宣言 `syp-eminelstandard-backend/template.yaml:3282`・secret :3289）; 旧と同系統プロトコル（CP932 フォーム＋XML・`if0200.do`/IF0200 — `legacy_eminel_docs/sources/eminel_sv_lib-develop/src/PointInfinity/PointInfinity.php:39, 65-71, 85-98`・`legacy_eminel_docs/sources/eminel_sv_lib-develop/src/Api/InterfaceCode.php:20`; "IF0200" は backend に出現しない）; 残高照会 `syp-eminelstandard-backend/src/functions/get-point-quantity-from-point-infinity/app.ts`（GET＋`<ZNDK>` :32, 79; secret `syp-eminelstandard-backend/template.yaml:2629`）:
```ts
const fuyoRiyuSjisArray = Encoding.convert(fuyoRiyuUnicodeArray, {  // :35-39 — FUYO_RIYU を Shift_JIS 変換
  to: 'SJIS', from: 'UNICODE', });
const regex = /<SYORI_STS>(.*?)<\/SYORI_STS>/;                      // :50 — XML 解析
if (!syoriStsValue || syoriStsValue !== '000') { ... return false; } // :56 — '000' = 成功
headers: { 'Content-Type': 'application/x-www-form-urlencoded; charset=Shift_JIS' },  // :96（POST — :92）
```
② 付与集中経路 既存（確実）— `syp-eminelstandard-backend/src/layers/common/nodejs/business-logic/give-point-badge-for-user.ts`: 重複防止 :69（`TABLE_POINT_BADGE_STATS`）; トランザクション＋`TABLE_USER_BADGE_SUMMARY`; 伝票 = `TABLE_SYSTEM_STATS` カウンター（:390-409、テーブル名 :392）; 呼び出し元: 月初回ログイン、`syp-eminelstandard-backend/src/functions/api-tip/read-tip.ts:68`、`syp-eminelstandard-backend/src/functions/api-survey/answer-survey.ts:346`、`syp-eminelstandard-backend/src/functions/batch-end-dr/app.ts:86`、機器連携、会員取込後、チェックリスト:
```ts
export const givePointBadgeForUser = async (      // :57 — すべての付与箇所が経由
  userId: string,
  pointBadgeStatsSk: string,                      // 重複防止キー: 'login#2026-08', 'dr#<id>'…
// Rollback transaction items if there is an error // :296-303 — PI 失敗 → DynamoDB 巻き戻し
  await writeOneTransaction(transactionRollbackItems);
```
③ 未実装（確実）: 計測データからの判定 — grep `energy|usage`（ポイント経路）: 0件。
**E-GW**: F-ES-04＋F-ES-09; 必須 2026（6/10）だが機能一覧は ✅劣後（[§3](#s3)-2）。🔍 `eminel_gw_project/docs/eminel/3_requirements/00_integrated_requirements_v1.2.md:409, 414, 675-691`・`eminel_gw_project/docs/eminel/2_management/22_decisions.md:31`・`eminel_gw_project/docs/eminel/1_product/10_feature_list.md:93, 95`・`eminel_gw_project/docs/eminel/2_management/minutes/20260625_egw_camp_day3.md:125`・`eminel_gw_project/docs/eminel/3_requirements/app/A03_point.md:48-102`
```
GW 計測 ──HEMS-SV──▶ 世帯別月平均テーブル（新設・s_104 相当 — 集計系Gと連携）▼ 静的 ScheduleV2 毎月1日（新設）
判定 Lambda（新規 — ③）──▶ givePointBadgeForUser('eco_heating#YYYYMM')（② — TABLE_* 3本）
    ──▶ give-point-to-point-infinity（①）──POST──▶ PI …失敗 → ロールバック
```
データの流れ — 旧: `s_104` → ≤22℃ 抽出 → `s_141` へ +250pt＋`ConPointLinkLogs` 記録 → PI ↔ 新: 月平均テーブル（新設）→ 判定 Lambda → `TABLE_POINT_BADGE_STATS`・`TABLE_USER_BADGE_SUMMARY`・`TABLE_SYSTEM_STATS` → PI。
1. QA／A03 でスペック確定: 250?・22℃?・季節?・必須/劣後（質問2）— *③のパラメータが全てここ*。
2. HEMS-SV スペック待ち; 月平均テーブル設計（集計系Gと連携）— *入力がなければステップ3が動かない*。
3. 判定 Lambda 新規（`syp-eminelstandard-backend/src/functions/`・`batch-*` 慣例）; FUYO_RIYU を `syp-eminelstandard-backend/src/layers/common/nodejs/variables/constants.ts` へ追加（雛形 :1756-1762）— *新規は薄い層のみ*。
4. 静的 `ScheduleV2` 1本追加（`syp-eminelstandard-backend/template.yaml`）— *固定周期、one-shot 不要*。
5. テスト: 2回連続実行で重複なし; PI エラーでロールバック; 旧クエリと突合（テスト=mui/実装=SYP）— *リスクは重複と不整合の2点*。
### 6.2 #2 `PublishRegularEcoMissionsCommand` — 省エネアドバイス定期配信 <a id="s6-2"></a>
**目的**: 条件で世帯を選別し、合った省エネアドバイス（19種）を配信。
**判定**: 廃止 = バッチ＋19 cron＋10 Publisher コード（判定式は [G] の抽出で継承）・ 流用 =「出口」の Tip パターン ・ 新規 = エンジン＋管理画面スケジュール（G-A-02）。
**理由**: e-smart にエンジンなし（grep 0件）; [G] は管理画面から変更可能なスケジュールを要求 — cron 直書きでは不可; 出口は既存; 判定式は抽出済みでコード廃棄の損失なし。
**旧フロー**（確実）— コマンド1本＋`--eco-mission-id`（フォルダ 11 ファイル中 1 はオプションクラス —「11種Publisher」はこれを含む数え方）; テーブル（`legacy_eminel_docs/sources/conciergesv-develop/src/Command/PublishRegularEcoMission/EcoMissionPublisher.php:7-13, 30-34`）: `ConEcoMissions`・`ConEcoMissionDestinations`・`ConRegularEcoMissions`・`PushMessages`・`PushMessageDestinations`; *19種 → 10 Publisher; 15 = CLD-06 の「約15種」→ 案 7種＋エコ暖房*:
```
cron 19行（cron :84-102）…15行 = 季節限定、4行（id 1/2/3/19）= 通年 ▼ --eco-mission-id 1..19 ──▶ 10 Publisher
    ├─ 種別毎の判定（平均超過・タイマー設定忘れ・暖房比率・契約記念日…）
    ├─ 書込 ConEcoMissions＋ConEcoMissionDestinations   └─ 書込 PushMessages＋PushMessageDestinations（1分後発火）
         ▼  実送信は #3（§6.3）が毎分キューを浚う
```
🔍 `legacy_eminel_docs/sources/conciergesv-develop/src/Command/PublishRegularEcoMission/EcoMissionPublisher.php:142-150`（＋同フォルダ `legacy_eminel_docs/sources/conciergesv-develop/src/Command/PublishRegularEcoMissionsCommand.php:54-140`、`legacy_eminel_docs/sources/conciergesv-develop/src/Command/PublishRegularEcoMission/EcoMissionPublisher.php:60-82, 112-152`）・ cron: `legacy_eminel_docs/docs/02_詳細設計/10_バッチ処理/mng-webap_cron設定_20241029.txt:84-102`:
```php
foreach ($this->PushMessageDestinations->createByEmsSp($emsSp) as $pd) {
    $pd->schedule = FrozenTime::now()->addMinutes(1);   // Push は「1分後発火」で登録
    ...
$this->ConEcoMissionDestinations->saveManyOrFail($ecoMissionDestinations);
$this->PushMessageDestinations->saveManyOrFail($pushMessageDestinations);
```
**e-smart**: エンジンなし（確実）— grep `advice|アドバイス|mission|ミッション|判定`: 実ヒット0件（全て `permission`）。最近縁 = Tip（`syp-eminelstandard-backend/src/layers/common/nodejs/models/Tip.ts:4-22`）: 静的ターゲティング3種（`syp-eminelstandard-backend/src/functions/batch-send-tip-preprocessing/app.ts:43-50`）; 既読時付与 `syp-eminelstandard-backend/src/functions/api-tip/read-tip.ts:68`（`TABLE_TIP_STATS`/`TABLE_TIP_USER_ACTION`）; エネルギーデータを読む関数なし（`api-tip` 内 grep `energy|usage`: 0件）:
```ts
export interface Tip {
  target_type?: string;          // ALL／属性／CSV —「エネルギーデータによる」は無い
  body_tip?: IBodyTipItem[];     // 管理者が編集する本文
  send_time?: number;            // 管理者設定の配信時刻（one-shot §7）
  point_quantity?: number;       // 既読時の付与ポイント
  push_notice_flag?: boolean; ...
```
**E-GW**: 2026 スコープ（F-ES-03 必須）; [G] は管理画面変更可のスケジュール要求; 15種→7種未決（CLD-06）; 判定式 T.B.D（G-C-05 — [G] に抽出済み）。🔍 `eminel_gw_project/docs/eminel/4_spec/admin/G_energy_advice.md:18-19, 28-29, 47`・`eminel_gw_project/docs/eminel/3_requirements/00_integrated_requirements_v1.2.md:632-647`・`eminel_gw_project/docs/eminel/2_management/20_open_issues.md:176-177`
```
[web-admin] アドバイス作成＋定期スケジュール（G-A-02・新規 UI）──put-schedule.ts──▶ BatchJudgeAdvice（新規・種別毎）
    ──▶ BatchSendAdvice（新規 — 雛形 batch-send-tip; 新テーブル Advice へ書込み）──one-shot──▶ BatchPushNotice（§6.3）──▶ FCM
```
データの流れ — 旧: 19 cron → 10 Publisher → `ConEcoMissions`＋`ConEcoMissionDestinations` と `PushMessages`＋`push_message_destinations`（1分後発火）→ #3 が送信 ↔ 新: 管理画面スケジュール → `BatchJudgeAdvice` → 新テーブル `Advice` → `BatchPushNotice` → FCM。
1. CLD-06 確定待ち／依頼（予備質問1）; [G] G-C-05 判定式の入力データ・取得元（GW/TagTag/Xzilla）マッピング — *工数を決める表*。
2. `Tip` 雛形に `Advice` モデル設計（`syp-eminelstandard-backend/src/layers/common/nodejs/models/`＋`interfaces/`）、target/point/push 踏襲＋判定条件＋スケジュール追加 — *同型なら配信経路を流用可*。
3. バッチボーン: `BatchJudgeAdvice`→`BatchSendAdvice`→`BatchPushNotice`（雛形 `syp-eminelstandard-backend/src/statemachine/batch-send-tip.asl.json`・`batch-push-notice-tip-new.asl.json`＋`syp-eminelstandard-backend/template.yaml`; 接続は `syp-eminelstandard-backend/src/functions/api-news/common.ts:207-209`）; 判定は空リスト返し — *確定前に配信経路をテスト、9月に間に合わせる*。
4. UI は `syp-eminelstandard-web-admin/components/tip/tip-form.vue` 雛形＋スケジュール設定部（新規）— *UI の大半は既存*。
5. 種別毎に判定 Lambda 1本 → アドバイス書込み＋Push 登録 — *1バッチ=1タスクに一致*。
6. テスト: 判定式毎に境界データ、結合フェーズ前に実動 — *境界誤り = 誤配信*。
### 6.3 #3 `DispatchPushMessagesCommand` — Push 送信（毎分） <a id="s6-3"></a>
**目的**: 共通の「送信口」— 旧の全通知はこの1本を通る。
**判定**: 廃止 = バッチ＋DB キュー＋毎分 cron＋PushCore ・ 存続 = Push 送信業務 ・ 代替 = e-smart の FCM 基盤; 独立デプロイなら同スタックを新環境へ構築。
**理由**: e-smart は完備（FCM＋トークン＋ファンアウト）; D03「全要件がESTA既存のため【新規】なし」; 旧構成は「毎分ポーリングなし」方針と相容れず; PushCore はコード自体がない。
**旧フロー**（確実）— テーブル `PushMessageDestinations`（:14, 40）; リトライ `legacy_eminel_docs/sources/conciergesv-develop/config/push_message.php:4-14`:
```
cron 毎分（cron :79-80）▼ DispatchPushMessagesCommand
    ├─ 読取 push_message_destinations …期限到来分・500件/ページ
    ├─ 検証: device_token／FCM トピックの排他（違反 → STATUS_INVALID）
    └─ POST ──▶ PushCore（localhost:54650 /v2/send-messages）──▶ FCM（*推定*）…リトライ 3分×5回
```
🔍 `legacy_eminel_docs/sources/conciergesv-develop/src/Command/DispatchPushMessagesCommand.php:65-79`（全体 :51-177）・`legacy_eminel_docs/sources/eminel_sv_lib-develop/src/StaticServices/PushMessageService.php:26, 36-39` ・ cron: `mng-webap_cron設定_20241029.txt:79-80`（完全パスは §6.1）:
```php
$limit = 500;                                        // :65 — 500件/ページ
$query = $this->PushMessageDestinations->find()      // :68 — 期限到来分を取得
    ...
    ->where(['status' => PushMessageDestination::STATUS_SCHEDULED, 'schedule >=' => $startAt, 'schedule <=' => $endAt])
$this->apiUrl = $this->getPushCoreHost() . '/v2/send-messages';        // PushMessageService :26
return Configure::read('PushCore.Api.host', 'http://localhost:54650'); // :38
```
**e-smart**: 完備（確実）。① トークン — `syp-eminelstandard-backend/src/layers/common/nodejs/models/MobileTokenManagement.ts`（原文全文; テーブル `TABLE_MOBILE_TOKEN_MANAGEMENT`; API `user/save_mobile_token` — `syp-eminelstandard-backend/src/functions/api-user/save-mobile-token.ts`、ルートは同フォルダ `syp-eminelstandard-backend/src/functions/api-user/app.ts:58`）:
```ts
export interface MobileTokenManagement {
  user_id: string;
  mobile_token: string;   // FCM トークン — アプリが user/save_mobile_token で登録
}
```
② FCM 直接送信＋無効トークン自動削除 — 🔍 `syp-eminelstandard-backend/src/layers/common/nodejs/services/push-notification-firebase.ts:87-97`:
```ts
await firebaseAdmin.messaging().send(notificationMessage);   // トークン毎に送信
if (errorCode === 'messaging/invalid-registration-token' ||
    errorCode === 'messaging/registration-token-not-registered' || ...) {
  await removeMobileTokenInvalid(mobileToken);               // 死んだトークン → 削除
```
③ ファンアウト — 🔍 `syp-eminelstandard-backend/src/functions/batch-push-notice/app.ts:17-34`; 10,000件/ロット（`syp-eminelstandard-backend/src/functions/batch-push-notice-tip-new-preprocessing/app.ts:53`）; 100 並列（定数 `syp-eminelstandard-backend/src/layers/common/nodejs/services/push-notice-to-user.ts:21`）; opt-in `TABLE_USER_SETTING`（同ファイル :35-60、env :19）; `target_screen` はアプリと整合（`syp-eminelstandard-app-syp-dev/lib/presentation/pages/main/bottom_navigation_view.dart:473-528`; トークン :101-111）; state machine 6系統: survey/news/tip/DR新着/DR開始/DR終了（`syp-eminelstandard-backend/template.yaml:510/685/815/1889/1927/1965`）:
```ts
const dataPushNotice: IDataPushNotice = await getDataJSONFromS3(
  BUCKET_TEMPORARY as string, `${targetFileTemp}_${segmentIndex}.json`); // S3 から1ロット読込
  target_screen: dataPushNotice?.data?.target_screen,   // タップ時の画面遷移用
const promisesPushNoticeForUser = listTargetUser.map((targetUser) =>
  pushNoticeToUser(targetUser.user_id, dataPushNoticeForUser));
await Promise.allSettled(promisesPushNoticeForUser);    // 並列・全完了待ち
```
**E-GW**: D03（ファイル: レビュー中; 対顧客スライド: レビュー前 — `eminel_gw_project/docs/eminel/3_requirements/app/README.md:64`）: 踏襲元 = ESTA Push基盤＋現行（通知種別の網羅）、「全要件がESTA既存のため【新規】なし」。🔍 `eminel_gw_project/docs/eminel/3_requirements/app/D03_push.md:5, 7, 29-31, 81-83`
```
配信バッチ完了（6系統）──one-shot──▶ 前処理 10,000件/ロット → S3 ──▶ batch-push-notice（100 並列）
    ── opt-in: TABLE_USER_SETTING ── トークン: TABLE_MOBILE_TOKEN_MANAGEMENT ──▶ FCM ──▶ アプリ …無効トークン自動削除
```
データの流れ — 旧: `push_message_destinations`（毎分 cron・500件/ページ）→ PushCore → FCM ↔ 新: 6系統 state machine → S3（`BUCKET_TEMPORARY`）上の 10,000件/ロット JSON → `batch-push-notice`（100 並列; トークン `TABLE_MOBILE_TOKEN_MANAGEMENT`・opt-in `TABLE_USER_SETTING`）→ FCM。
1. 「Push 基盤（FCM）」を独立デプロイ QA の回答へ（[§5](#s5)-2・[§10](#s10)-B2）— *Firebase 分離要否を決める*。
2. 通知種別の棚卸し（D03「＋現行」）: 19 アドバイス・DR・見守り（CLD-05）・レポート… → 新生成元＋`target_screen` マッピング — *D03 確定に必須*。
3. 独立時: Firebase 新設＋トークンテーブル＋API save_mobile_token — *パターン既存、設定＋credential のみ*。
4. 移植タスクは起こさない — Notion に「廃止、batch-push-notice で代替」— *約46本に誤算入させない*。
5. テスト: 実トークン; 無効トークン自動削除; 4096 バイト上限（`syp-eminelstandard-backend/src/layers/common/nodejs/variables/constants.ts:223`）— *Push 障害の3類型*。
### 6.4 #4 `ControlDrOperationCommand` — DR 指令制御 <a id="s6-4"></a>
**目的**: DR 発動時、参加世帯の暖房をサーバーが自動制御。
**判定**: 2026年コードなし（ステップ1のみ）・ 廃止 = 旧方式全体（毎分 cron・`instructions`・GW ポーリング・偽装）・ 2027年 = e-smart DR 基盤上で新規、GW 経由分岐を追加。
**理由**: DR = 劣後 2027/4〜（6/10; B05: 26年スコープ=なし）; DR 基盤完備 — 分岐1本の追加で済む; 「偽装」は旧 GW 制約の回避策で新方式では前提消滅; 質問5のみ 2026年ファームウェアを拘束。
**旧フロー**（確実）— テーブル（`fetchTable` :56-61）: `ConDrOperations`・`ConDevices`・`ConDeviceControls`・`ConDeviceStatuses`・`HemsGws`・`Instructions`; `instructions` 書込み :210〜（`ems_sp_no`・`node_id`・`eoj`）:
```
cron 毎分（cron :76-77）▼ ControlDrOperationCommand（2フェーズ; 世帯毎に指令衝突を5分回避）
    ├─ 読取 ConDrOperations＋hems_gws＋t_201（ConDevices）   ├─ 書込 ConDeviceControls
    └─ 書込 instructions（宅外制御指示 — ECHONET; EPC 80/B0）※アプリ操作に偽装
         ▼  GW が hemssv 経由でポーリング → 宅内機器を制御
```
🔍 `legacy_eminel_docs/sources/conciergesv-develop/src/Command/ControlDrOperationCommand.php:171-172` ・ cron: `mng-webap_cron設定_20241029.txt:76-77`（完全パスは §6.1）:
```php
// 暖房制御ユニットとユーザのアプリ端末の情報を取得
// ユーザのアプリ端末からの操作のように見せかけないとゲートウェイが指令を無視する
```
**e-smart**: 別方式の DR 基盤あり（確実）。① モデル — `syp-eminelstandard-backend/src/layers/common/nodejs/models/Dr.ts:5-30`・同フォルダ `syp-eminelstandard-backend/src/layers/common/nodejs/models/DrUserAction.ts:1-14`（テーブル: `TABLE_DR` — `syp-eminelstandard-backend/src/functions/api-dr/create-dr.ts`; `TABLE_DR_USER_ACTION` — `batch-start-dr`; `TABLE_DR_STATS` — `batch-send-dr-complete`）:
```ts
export interface Dr {
  implement_start_time?: number;   // 開始/終了 → one-shot
  target_type?: string;  control_setting: IControlSetting[];  // news/tip 同様のターゲティング; どの機器に何をするか
  push_notice_new_dr?: IPushNotice;    // Push 3点 ・ has_badge / point_quantity ...
export interface DrUserAction {
  pre_control_status?: { device_id: string; server_type: string; ... // DR 前の機器状態 — 復元用
```
② 開始／終了 — 🔍 `syp-eminelstandard-backend/src/functions/batch-start-dr/app.ts:55-65`・`syp-eminelstandard-backend/src/functions/batch-end-dr/app.ts:82-94`; `pre_control_status` 保存 :212; 復元 :96-190; 制御対象 Rinnai/Noritz/Daikin/MUI 赤外線（:139-188）— いずれもメーカークラウド直結・GW 経由なし; 実体 `controlDevice`（`syp-eminelstandard-backend/src/layers/common/nodejs/business-logic/control-device.ts`・`SERVER_TYPE` 4分岐）をローカル関数 `handleControlDevice`（`batch-start-dr/app.ts:81`）が呼ぶ; スケジュール2段: 配信 = 作成・更新時（`syp-eminelstandard-backend/src/functions/api-dr/create-dr.ts:111`・`syp-eminelstandard-backend/src/functions/api-dr/update-dr.ts:149`）、start/end = 配信完了時（`syp-eminelstandard-backend/src/functions/batch-send-dr-complete/app.ts:127-143`）; web-admin に DR 管理一式（`syp-eminelstandard-web-admin/pages/distribution-management/dr/`＋`syp-eminelstandard-web-admin/components/dr/dr-form.vue` — 1881 行）:
```ts
handleControlDevice(drUserAction.user_id, drInfo.control_setting, drId)   // start: ユーザー毎に制御
const pointBadgeStatsSK = `dr#${drId}`;                                   // end: 完走ユーザーへ付与
await givePointBadgeForUser(userId, pointBadgeStatsSK, ...);              // その後 pre_control_status で復元
```
**E-GW**: F-ES-07/08＋F-AD-08 — 劣後 2027/4〜; 将来: サーバー主導・指令は HEMS-SV 経由; 終了方式 A/B 未決 — 質問5。🔍 `eminel_gw_project/docs/eminel/2_management/22_decisions.md:30-31`・`eminel_gw_project/docs/eminel/3_requirements/app/B05_dr.md:8, 32-34`・`eminel_gw_project/docs/eminel/2_management/minutes/20260625_egw_camp_day3.md:113-122`（約17項目）
**新フロー（2027年 — 2026年は実装しない）＋ステップ**:
```
[web-admin] dr-form.vue ─ api-dr/create-dr.ts:111・update-dr.ts:149 → TABLE_DR＋one-shot 配信
    ▼ BatchSendDr ─ 配信完了 → batch-send-dr-complete:127-143 が start/end 登録（TABLE_DR_STATS）
batch-start-dr ─ handleControlDevice → controlDevice ─ 既存4分岐＋新分岐 2027「E-GW 経由」（HEMS-SV API）─ pre_control_status 保存（TABLE_DR_USER_ACTION）
batch-end-dr ─ ポイント付与（'dr#<id>'）＋ pre_control_status で復元
```
データの流れ — 旧: `ConDrOperations` →（毎分 cron）`instructions`［アプリ操作に偽装］→ GW が `hemssv` 経由ポーリング → 機器 ↔ 新: `TABLE_DR` → 配信 → one-shot start/end → `controlDevice`（4分岐＋E-GW 分岐 2027）→ 機器; 状態の保存・復元は `TABLE_DR_USER_ACTION.pre_control_status`。
1. （2026年 — 唯一）kihara と整理 → 質問5（文面 [§3](#s3)）— *2026年ファームウェアは待てない*。
2. （2027年）DR イベント層は全面流用（モデル＋管理画面＋ターゲティング＋Push＋ポイント）— *制御方式に依存しない層*。
3. （2027年）`controlDevice` に新 `SERVER_TYPE`「E-GW 経由」を追加、HEMS-SV API を呼ぶ — *既存4分岐と同列 = 最小変更*。
4. （2027年）GW 経由機器の `pre_control_status` マッピング — *ステップ1の帰結に依存*。
5. （2027年）タスク分割は Day3 どおり（約17項目）— *「1バッチ全部盛り」を避ける*。
6. テスト（2027年）: 新旧分岐の混在・途中解除・復元 — *最も壊れやすい箇所*。
## §7. グループ共通基盤と前提 <a id="s7"></a>
**スケジュール基盤**: 静的3本（`ScheduleV2`・`Asia/Tokyo` — `syp-eminelstandard-backend/template.yaml:9-11`）: ① `BatchRunSequentially` `cron(5 0-7 * * ? *)`（:853-888、cron :881-882）② `BatchMigrationIntegratedData` `cron(0 8 * * ?)`（:2205-2240、:2233）③ `BatchGetErrorDeviceInfoOfRinnai` 8:00（:2966-2980）。残りは全て動的 — 🔍 `syp-eminelstandard-backend/src/layers/common/nodejs/services/put-schedule.ts:18-33`（組立て `syp-eminelstandard-backend/src/layers/common/nodejs/utils/date-utils.ts:117`）; 例: `syp-eminelstandard-backend/src/functions/api-news/common.ts:207-209`、`syp-eminelstandard-backend/src/functions/batch-send-news-complete/app.ts:72-80`; オートメーションはルール毎の週次（`syp-eminelstandard-backend/src/functions/api-automation/common.ts:115`）; ポーリングなし（grep `rate(`: 0件）。💡 G-A-02 の技術解 = このパターン:
```ts
return await scheduler.createSchedule({
  ScheduleExpression: scheduleExpression,          // 例 cron(30 14 15 8 ? 2026) — 特定の一時点
  Target: { Arn: resourceArn, ..., Input: JSON.stringify(inputData) },
  ActionAfterCompletion: isDeleteAfterCompletion
    ? ActionAfterCompletion.DELETE : ActionAfterCompletion.NONE, ...  // 実行後に自動削除
```

| チャネル | 発生源 | 格納先 | 役割 |
|---|---|---|---|
| FCM トークン | アプリが `user/save_mobile_token` で登録（`api-user/save-mobile-token.ts`） | `TABLE_MOBILE_TOKEN_MANAGEMENT` | Push 宛先; 無効トークン自動削除 |
| Push 受信可否 | ユーザーがアプリで設定 | `TABLE_USER_SETTING` | 送信時 opt-in フィルタ（`syp-eminelstandard-backend/src/layers/common/nodejs/services/push-notice-to-user.ts:19, 35-60`） |
| ポイント／バッジ | 各イベントが `givePointBadgeForUser` を呼ぶ | `TABLE_POINT_BADGE_STATS`・`TABLE_USER_BADGE_SUMMARY`・`TABLE_SYSTEM_STATS` | 記帳＋重複防止＋伝票; PI 同期 |
| Tip 既読状態 | `api-tip/read-tip.ts:68` | `TABLE_TIP_STATS`・`TABLE_TIP_USER_ACTION` | 既読＋既読時付与 — #2 が再利用する「出口」 |
| DR イベント | 管理者が作成・更新（`api-dr/create-dr.ts`） | `TABLE_DR`・`TABLE_DR_USER_ACTION`（`pre_control_status`）・`TABLE_DR_STATS` | イベント＋参加＋復元＋統計 |
**前提**（3分冊共通）:
- Day3: 作り直し・1バッチ=1タスク・バッチボーン先行・結合フェーズ（9月）前に実動; バッチ/外部連携は SYP。🔍 `eminel_gw_project/docs/eminel/2_management/minutes/20260625_egw_camp_day3.md:35, 51, 99-103, 147-149`
- デプロイ: QA 独立デプロイ（swan・回答中）は暫定*独立の方向* →「流用」≠ 工数ゼロ; `gw-syp-dev` に E-GW コミットゼロ（web-admin: `git log origin/main..gw-syp-dev` 空; backend: 直近15コミットは e-smart のみ）。※推定（未確認）: e-smart コードベースへの追記方式 — QA 管理画面（masao takahashi・回答中）からの推測・文書化なし; 「共通ソース」≠「共通実行環境」。担当範囲: QA 調査範囲（swan・回答中）— `conciergesv`/`eminelsv` は調査対象のみ; GW 通信は HEMS-SV 経由・スペック後日。
- スコープ 6/10（決定ログ）: 必須 = 暖房/暖房制御/照明アドバイス※/ポイント連携/グルーピング・レポート; 劣後 = 複合制御・DR・ダッシュボード・バッジ等; ※省エネアドバイスの誤記と思われる（*推定*）。機能一覧: ✅ = 2027 繰越可、空欄 = 必須。🔍 `eminel_gw_project/docs/eminel/2_management/22_decisions.md:30-31`。§6 の実施主体 = SYP・branch `gw-syp-dev`; 人名: swan・masao takahashi（mui — QA）、kihara（mui — GW ファームウェア）。

| | 旧 | e-smart |
|---|---|---|
| 言語 | PHP 8.0 / CakePHP 4.4 | TypeScript / SAM + Lambda（Node.js 24 — `syp-eminelstandard-backend/template.yaml:181`） |
| DB | PostgreSQL（日/月パーティション） | DynamoDB（PITR 有効） |
| バッチ | サーバー cron＋shell flock | Step Functions + EventBridge Scheduler |
| ファイル受信 | SFTP → ディスク | SFTP → S3 → DynamoDB |
🔍 `legacy_eminel_docs/docs/02_詳細設計/10_バッチ処理/cron設定概要.txt:1-37`・`syp-eminelstandard-backend/template.yaml`・`eminel_gw_project/docs/eminel-smart/02_product_overview.md:48-53`
## §8. 新旧データ対照 <a id="s8"></a>

| データ | 旧（PostgreSQL） | 新（DynamoDB） | 状態 |
|---|---|---|---|
| 月平均センサー値 | `s_104`（`ConSensorMonthlyValues`） | 月平均テーブル — [§6.1](#s6-1) ステップ2 | ❌ 新設要 |
| ポイント台帳 | `s_141`（`ConEcoPoints` — 年度累積） | `TABLE_POINT_BADGE_STATS`（イベント毎）＋`TABLE_USER_BADGE_SUMMARY` | ⚠️ 性質が異なる |
| 付与履歴／重複防止 | `ConPointLinkLogs`（`reason` キー） | `TABLE_POINT_BADGE_STATS` の `pointBadgeStatsSk` | ✅ あり |
| PI 伝票採番 | —（未記録） | `TABLE_SYSTEM_STATS` カウンター（:390-409） | ✅ あり |
| アドバイス＋宛先 | `ConEcoMissions`＋`ConEcoMissionDestinations`（＋`ConRegularEcoMissions`） | `Advice` モデル — [§6.2](#s6-2); 最近縁 Tip | ❌ 新設要 |
| Push キュー | `PushMessages`＋`push_message_destinations` | なし — S3 ロット JSON（`BUCKET_TEMPORARY`・使い捨て） | ⚠️ 性質が異なる |
| トークン | キューのレコードに紐づく | `TABLE_MOBILE_TOKEN_MANAGEMENT` | ✅ あり |
| Push 受信可否 | —（未確認） | `TABLE_USER_SETTING`（:19, 35-60） | ✅ あり |
| DR 指令 | `ConDrOperations`＋`instructions` | `TABLE_DR`＋`TABLE_DR_USER_ACTION`＋`TABLE_DR_STATS`; サーバー直接制御 | ⚠️ 性質が異なる |
| DR 前状態 | —（未記録） | `DrUserAction.pre_control_status` | ✅ あり |
**集計**: ✅ 5 ・ ⚠️ 3 ・ ❌ 2。

| 機構 | 旧 | 新 |
|---|---|---|
| Push 経路 | DB キュー・毎分 cron・500/ページ → PushCore → FCM（*推定*） | 10,000/ロット → S3 → `batch-push-notice`・100 並列・FCM 直接 |
| トークン／受信可否 | キューのレコード紐づき／— | `TABLE_MOBILE_TOKEN_MANAGEMENT`（API save_mobile_token）／`TABLE_USER_SETTING`（:19, 35-60） |
| ポイント記帳 | `s_141`＋`ConPointLinkLogs` | `TABLE_POINT_BADGE_STATS`＋`TABLE_USER_BADGE_SUMMARY`＋`TABLE_SYSTEM_STATS` |
| PI連携 | `PointInfinity.php`（CP932＋XML） | `give-point-to-point-infinity`（Shift_JIS＋XML — 同系統） |
| アドバイス | 19 cron＋10 Publisher → `ConEcoMissions`/`PushMessage*` | 存在しない（#2 新規）; 最近縁 Tip＋one-shot |
| DR | `ConDrOperations` → `instructions` → GW ポーリング（`hemssv`） | `TABLE_DR`/`TABLE_DR_USER_ACTION`/`TABLE_DR_STATS` → `controlDevice` 直接制御 |
| 起動 | 固定 cron `/etc/cron.d/eminel-mng-webap` | 静的 `ScheduleV2` 3本＋動的 one-shot（[§7](#s7)） |
## §9. 設計選択肢 <a id="s9"></a>
報告レベルの A/B/C 選択肢なし; DR 終了方式 A/B は北ガス様が決める質問（[§3](#s3)-1・[§10](#s10)-A1）。
## §10. QA一覧（対象別） <a id="s10"></a>
**A = 北ガス様（PM 経由）**（質問 2/3/5・予備質問1 は質問表に記載済み・未送付）・ **B = mui 様**:

| # | 質問 | 理由 | 重要度 |
|---|---|---|---|
| A1 | 質問5: GW が DR 状態を保持してよいか（A/B 案） | 2026年ファームウェアを拘束（[§6.4](#s6-4) ステップ1） | 🔴 |
| A2 | 質問2: ポイントは必須か劣後か＋ポイント値 | 6/10 と機能一覧の矛盾; #1 のスコープ | 🔴 |
| A3 | 予備質問1: 15種→7種集約（CLD-06） | #2 の Lambda 本数・種別リスト | 🟡 |
| A4 | 質問3: 見守り（CLD-05）? | 通知種別を決める | 🟡 |
| A5 | （A03 レビュー時 — 文面 [§3](#s3)）季節は 12〜3月か通年か | コード通年 vs A03 | 🟡 |
| B1 | （社内・A1 前）kihara: GW が状態保持する場合のファームウェア制約 | 質問5の技術前提 | 🔴 |
| B2 | 独立デプロイ時: Firebase＋PI credential 共用か新設か(ただし書き回答と併せて) | [§6.3](#s6-3) ステップ3 | 🟡 |
| B3 | D03: ファイル「レビュー中」vs スライド「レビュー前」— どちらが正 | 「全要件ESTA既存」の確度 | 🟢 |
**C = 旧システム引継ぎ元**: C1 — 19 アドバイスの業務的意図（[G] で不足時のみ）🟢。**D = アプリチーム**: D1 — 通知種別毎の `target_screen`（D03・[§6.3](#s6-3) ステップ2）🟡。
```
B1（kihara）──▶ A1（質問5・DR）  ★最優先 — 2026年ファームウェア      A2 ──▶ A03 確定 ──▶ A5 同時
A3（CLD-06）──▶ §6.2 ステップ2〜5      B2 ──▶ §6.3 ステップ3（独立確定時）      A4＋D1 ──▶ D03 通知種別表 ──▶（必要なら C1）
```
## §11. 根拠と確度 <a id="s11"></a>

| 内容 | 出典（完全パス） |
|---|---|
| 旧4バッチ | `legacy_eminel_docs/sources/conciergesv-develop/src/Command/`: `DistributeMonthlyEcoPointsCommand.php`（:33, 48-51, 83-104, 116-188）、`PublishRegularEcoMissionsCommand.php`（:54-140）＋`PublishRegularEcoMission/EcoMissionPublisher.php`（:7-13, 30-34, 60-82, 112-152）、`DispatchPushMessagesCommand.php`（:14, 40, 51-177）、`ControlDrOperationCommand.php`（:56-61, 171-172, 210〜）; `legacy_eminel_docs/sources/eminel_sv_lib-develop/src/PointInfinity/PointInfinity.php:39, 65-71, 85-98`・`legacy_eminel_docs/sources/eminel_sv_lib-develop/src/PointInfinity/Api/InterfaceCode.php:20`・`legacy_eminel_docs/sources/eminel_sv_lib-develop/src/StaticServices/PushMessageService.php:26, 36-39`; `legacy_eminel_docs/sources/conciergesv-develop/config/push_message.php:4-14`; cron: `legacy_eminel_docs/docs/02_詳細設計/10_バッチ処理/mng-webap_cron設定_20241029.txt` #1 :113-114, #2 :84-102, #3 :79-80, #4 :76-77 |
| ポイント/PI 新側 | `syp-eminelstandard-backend/src/functions/give-point-to-point-infinity/app.ts`（:15, 35-39, 50, 56, 92, 96; 宣言 `syp-eminelstandard-backend/template.yaml:3282`）、`syp-eminelstandard-backend/src/layers/common/nodejs/business-logic/give-point-badge-for-user.ts`（:57, 69, 296-303, 390-409）、`syp-eminelstandard-backend/src/functions/get-point-quantity-from-point-infinity/app.ts`（:32, 79） |
| Push 新側 | `syp-eminelstandard-backend/src/layers/common/nodejs/models/MobileTokenManagement.ts`、`…/services/push-notification-firebase.ts:87-97`、`…/services/push-notice-to-user.ts:19, 21, 35-60`、`syp-eminelstandard-backend/src/functions/batch-push-notice/app.ts:17-34`、`…/batch-push-notice-tip-new-preprocessing/app.ts:53`、`…/api-user/save-mobile-token.ts`＋`…/api-user/app.ts:58`、`syp-eminelstandard-app-syp-dev/lib/presentation/pages/main/bottom_navigation_view.dart:101-111, 473-528` |
| DR 新側 | `syp-eminelstandard-backend/src/layers/common/nodejs/models/Dr.ts:5-30`、`…/models/DrUserAction.ts:1-14`、`…/business-logic/control-device.ts`、`syp-eminelstandard-backend/src/functions/batch-start-dr/app.ts:55-65, 81, 212`、`…/batch-end-dr/app.ts:82-94, 96-190, 139-188`、`…/batch-send-dr-complete/app.ts:127-143`、`…/api-dr/create-dr.ts:111`、`…/api-dr/update-dr.ts:149`、`syp-eminelstandard-web-admin/pages/distribution-management/dr/`＋`syp-eminelstandard-web-admin/components/dr/dr-form.vue` |
| スケジュール基盤 | `syp-eminelstandard-backend/template.yaml:9-11, 181, 853-888, 2205-2240, 2966-2980`、`syp-eminelstandard-backend/src/layers/common/nodejs/services/put-schedule.ts:18-33`、`…/utils/date-utils.ts:117`、`syp-eminelstandard-backend/src/functions/api-news/common.ts:207-209`、`…/batch-send-news-complete/app.ts:72-80`、`…/api-automation/common.ts:115, 167-175` |
| E-GW 要件 | `eminel_gw_project/docs/eminel/3_requirements/00_integrated_requirements_v1.2.md`（:409, 414, 632-647, 675-691）、`…/1_product/10_feature_list.md:93, 95`、`…/2_management/22_decisions.md:30-31`、`…/2_management/20_open_issues.md:176-177`、`…/2_management/minutes/20260625_egw_camp_day3.md`（:35, 51, 99-103, 113-122, 125, 147-149）、`…/3_requirements/app/A03_point.md:48-102`、`…/app/B05_dr.md:8, 32-34`、`…/app/D03_push.md:5, 7, 29-31, 81-83`、`…/app/README.md:64`、`…/4_spec/admin/G_energy_advice.md:18-19, 28-29, 47`（`…` = `eminel_gw_project/docs/eminel`） |
| §2 の計数 | `syp-eminelstandard-backend`@`dc39aa39` で自ら計数: `syp-eminelstandard-backend/src/functions/` 105 フォルダ、`batch-*` 81、`syp-eminelstandard-backend/template.yaml` の `Type: ScheduleV2` 3（template-api/dynamodb: 0） |

| 段階 | 内容 |
|---|---|
| ✅ 確実 | e-smart の有無に関する全記述（実コード確認）; 旧4バッチの挙動; cron :84-102（季節15行＋通年4行 = id 1/2/3/19）; Node.js 24; DR スケジュール2段; 各 `TABLE_*`; B05/D03 行番号（`fbc0af0`）; 計数 105/81/3 |
| ⚠️ *推定* | (1) PushCore→FCM（コードなし）(2) 「照明アドバイス」= 誤記 (3) e-smart コードベース追記方式（※推定（未確認）— QA 管理画面より） |
| ❓ 未確認 | (1) QA Notion 3件は回答中（08-04・スクリーンショット — 再引用時は原ページ確認）(2) D03/B05 状態 ファイル vs スライド (3) E-GW のポイント値・閾値・季節（A03 要確認）(4) 旧の Push 受信可否設定 (5) CLD-05/06 の帰結 |
コミット: 調査 `788b438`・08-06 に `fbc0af0` 再照合（6コミット・`eminel_gw_project/docs/eminel/3_requirements/app/` 13ファイル＋skill 1行のみ）— B05/D03 更新済み・**結論不変**; app は snapshot のため行番号変動しうる。
**ESTA 調査資料との差異**（ファイル: `eminel_gw_project/docs/eminel-smart/02_product_overview.md`; 本分冊 3/6 点。残り3点: 基幹取込の毎時実行＋ロック5分 → 外部連携・受信系分冊; `CsvDownloadHistory` → 外部連携・受信系＋CSV・ZIP 分冊）:

| 資料の記載 | 実コード |
|---|---|
| Push「最大500件/バッチ」（:121） | 500 の定数なし（旧システム側のページングサイズ）; 10,000/ロット・100 並列（[§6.3](#s6-3)） |
| 「自動化ルール実行（毎分）」（:85） | 毎分なし — ルール毎の週次動的スケジュール（[§7](#s7)） |
| Node.js 20.x（:49） | `nodejs24.x`（`syp-eminelstandard-backend/template.yaml:181`; レイヤーの CompatibleRuntimes は 20.x — :3163） |
