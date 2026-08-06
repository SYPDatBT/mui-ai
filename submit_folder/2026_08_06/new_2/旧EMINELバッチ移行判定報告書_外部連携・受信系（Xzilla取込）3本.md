# 調査報告: 外部連携・受信系（Xzilla取込）グループ（3バッチ #5〜#7）— 新システムへの移植は必要か
| | |
|---|---|
| 対象 | `legacy_eminel_docs/docs/03_API仕様/04_バッチ一覧.md` の3バッチ（いずれも `conciergesv`）: #5 `RcvCntctCancellationCommand`（IF2249）・#6 `RcvEmsPlsCntrPayerCommand`（IF2264）・#7 `RcvHalfHourElectricPowerCommand`（IF1156） |
| 照合範囲 | `legacy_eminel_docs`@`ccd8f56` ・ `eminel_gw_project`@`fbc0af0`（調査は `788b438` 時点 — 本グループへの影響なし、§11）・ `syp-eminelstandard-backend`@`dc39aa39` ・ `syp-eminelstandard-web-admin`@`e550326`（後2者 branch `gw-syp-dev`）— いずれも 2026-08-06 の origin と一致 |
| 日付 / 作成者 | 調査 2026-08-04 ・ 作成 2026-08-06 ・ Bui Trong Dat（SYP）＋AI支援 |
| 分冊 | 全11本 = Notion 3タスク対応の3分冊; #1〜#11 は通し番号・日越共通; 他分冊: 配信・通知系（#1〜#4）・CSV・ZIPエクスポート系（#8〜#11）; ベトナム語版は同フォルダ `report_batch_nhom_xzilla.md`（1対1一致） |

| 記号 | 意味 |
|---|---|
| 確実 / *推定* / ※推定（未確認） | コード・資料で確認済み / 根拠ある推測（未確定）/ 未検証の仮説 |
| 🔍 + パス | grep 0件 = backend 全体でヒットなし; `...` = 本書のコード省略記号; パスはリポジトリ名から完全表記（起点 `sources/`）; 図中は `ファイル名:行` に省略可 — 完全パスは直近の 🔍 行に記載 |
| e-smart | = ESTA = EMINEL-Smart; `hemssv`（旧）≠ HEMS-SV（m2-cloud・mui 新規開発） |
| IF-01 | E-GW⇔Xzilla の新連携窓口 — 統合要件 v1.2 §4-1 IF一覧の1番、北ガスクラウド経由、未確定（旧4桁 IF とは別物） |
| CLD-07 / SVC-03 ・ F-ES-10 / F-ES-01 | 未決事項: IF-01 の入出力＋認証（約10項目）/ 保持期間・バックアップ方針未定義 ・ 統合要件 v1.2 サーバー機能コード: Xzilla連携 / グラフ |
| 回答中 | QA（Notion）未確定（参照 2026-08-04 — 再引用時は原ページ確認） |

**目次**: 結論 ・ I: §1 理由 ・ §2 実現場所 ・ §3 要確認 ・ §4 誤解されやすい点 ・ §5 ネクストアクション ・ II: §6 バッチ別 ・ §7 共通基盤 ・ §8 データ対照 ・ §9 設計オプション ・ §10 QA ・ §11 根拠と確度
## 結論
> **#5 `RcvCntctCancellationCommand`（電力解約受信、IF2249）: バッチは廃止・業務は存続。** 「買電売電の計算停止フラグ」は #7 の前提のため存続させ、e-smart 既存の Xzilla 取込フローへ統合（専用バッチは作らない）。（*推定*）
>
> **#6 `RcvEmsPlsCntrPayerCommand`（支払者マスタ受信、IF2264）: バッチは廃止・データと業務知識は引き継ぐ。** 支払者データは毎日稼働中の契約系3チャネル（IF2023/IF2024/DM1040）の拡張で受け、契約終了判定3条件はスペックとして抽出・保存。（*推定*）
>
> **#7 `RcvHalfHourElectricPowerCommand`（電力30分値受信、IF1156）: 新規** — e-smart 取込パターンに準拠。明文要件・2026スコープ。全11本中もっとも重量級。（確実）
>
> 確定前に**要確認 4点**（→ §3）: IF-01/CLD-07 ・ IF-01 の解約フロー有無 ・ 30分値の提供周期 ・ SFTP `/EST` の宛先。

*（ラベルは事実部分の確度; 「判定」はレビュー用の提案。工数は未見積 — 1バッチ=1タスクの Notion 分割時に見積り、§5。）*

## 第I部 — 報告編
### §1 なぜこの結論か
| | 旧（`conciergesv`） | 新（e-smart / E-GW） |
|---|---|---|
| Xzilla 受信 | CSV を SFTP で中間サーバーへ、cron 5〜10分毎 | SFTP → S3 → DynamoDB、JST 0〜7時毎時 — 8 IF 稼働中（§7.3） |
| スタック | PHP 8.0 / CakePHP 4.4 + PostgreSQL | TypeScript / Lambda（Node.js 24）+ DynamoDB; Step Functions + EventBridge Scheduler |
| 本グループの3 IF | IF2249・IF2264・IF1156 が安定稼働 | 存在しない（grep 0件 — §7.5）; 受信基盤＋後処理はあり |
| 代替チャネル | — | IF-01 — 未確定（CLD-07） |

| 中核処理（旧） | 必要か |
|---|---|
| 5〜10分毎の SFTP 受信（3本共通） | ❌ アーキテクチャごと廃止 — 「準リアルタイム」は旧 cron の産物; 既存 0〜7時ウィンドウで受ける（30分値のみ §3-3） |
| #5 契約種別 PE624/625 の抽出 | ✅ IF-01 新ファイル種別の抽出条件として存続（§6.1 ステップ2・4） |
| #5 計算停止フラグ（`t_101.c065=1`） | ✅ 存続 — 取込後処理④として実装、#7 が参照（§6.1 ステップ3） |
| #6 5分毎の全件削除→再投入（memory_limit 4096M） | ❌ — 「いけてない」の典型; 既存3チャネルのファイル到着単位更新で代替 |
| #6 対象契約種別のみ投入（PE624/625/650/651/652・PG077/079）＋支払者データ | ✅ — グルーピング（必須 2026）に必要; IF2023/IF2024/DM1040 で受け、不足のみ IF-01 拡張（§6.2 ステップ2） |
| #6 契約終了判定3条件 | ✅ 存続 — コメントから1ページのスペックに抽出（§6.2 ステップ1・即着手可） |
| #7 30分値受信＋速報（上書き）／確報（追記蓄積）の分離 | ✅ — 新テーブル2本をこの分離のまま設計（§6.3 ステップ3） |
| #7 30分×2→1時間集約＋設備構成による買電/売電条件表 | ✅ ロジックとして存続（PHP は移植しない）— 設置9パターンへ再マッピング（§6.3 ステップ4） |
### §2 新システムでの実現場所
| 仕事 | 場所 | 種別 |
|---|---|---|
| Xzilla ファイル受信 | `syp-eminelstandard-backend/src/functions/batch-get-list-file-name-from-sftp-server/` → `syp-eminelstandard-backend/src/functions/batch-forward-csv-from-sftp-server-to-s3/` → 8本の `batch-ifXXXX-import-*` | 既存（`syp-eminelstandard-backend/src/statemachine/batch_run_sequentially.asl.json`、0〜7時 — §7.3） |
| #5 解約＋計算停止フラグ | 上記へファイル種別1種追加＋後処理④を既存3本の隣に新設 | 未実装 — 既存パターンで新規（IF-01 待ち） |
| #6 支払者データ | `syp-eminelstandard-backend/src/functions/batch-if2023-import-contract-info/`・`syp-eminelstandard-backend/src/functions/batch-if2024-import-user-info/`・`syp-eminelstandard-backend/src/functions/batch-dm1040-import-user-contract-list/`（支払者抽出: `syp-eminelstandard-backend/src/functions/batch-dm1040-import-user-contract-list-preprocessing/app.ts:54, 63`） | 既存 — フィールド拡張のみ（IF-01 待ち） |
| #6 契約終了判定 | 新規後処理（抽出スペックを適用） | 未実装 |
| #7 30分値＋買電売電計算 | 新規 handler＋速報/確報新テーブル（`syp-eminelstandard-backend/template-dynamodb.yaml`）＋計算 Lambda | 未実装 — グループ最重量 |
| 送信方向 → 基幹 | `upload-data-backup-to-sftp.ts` → `/EST`（機器 CSV 6種・8:00） | 既存（宛先 ※推定（未確認）— §3-4） |

- フロー全図: §7.3。思想: 旧 = cron 密集; 新 = 静的3本＋動的 one-shot、**毎分ポーリングなし**（grep `rate(`: 0件 — §7.1）。
### §3 確定前に要確認の点
| # | 論点 | 旧 | 新／計画 | 重要度 |
|---|---|---|---|---|
| 1 | IF-01 の入出力＋認証（CLD-07、送信方向「EMINELデータの共有」含む） | 3 IF 安定稼働 | 未確定 — 3バッチすべて依存 | 🔴 |
| 2 | IF-01 に解約フローはあるか | IF2249 が5分毎提供 | 不明 — なければ即要件追加を提起 | 🔴 |
| 3 | 30分値の提供周期 | 10分毎 | e-smart は 0〜7時のみ — 準リアルタイムは新規要素 | 🔴 |
| 4 | SFTP `/EST` の宛先 | （相当なし） | 6種 CSV を毎日 8:00 送信中; ※推定（未確認）: Xzilla/DWH、接続先は secret | 🟡 |

**質問文案**:
> **mui 様へ（QAデータベース）— #4**:
> 「e-smart が毎日 8:00 に機器データ CSV 6種（給湯器系5種＋赤外線リモコン）を SFTP の `/EST` フォルダへアップロードしていますが（`upload-data-backup-to-sftp.ts`）、この宛先は Xzilla もしくは DWH（分析用データ基盤）という理解で合っていますか。接続先が secret 管理のためコードから確認できず、ご確認をお願いしたいです。該当する場合、F-ES-10「EMINELデータの共有」の既存実装として扱いたいと考えています。」

> **北ガス様へ（mui PM 様経由）— #2・#3**（CLD-07 議論と同じタイミングで）:
> 「新アーキテクチャの IF-01（北ガスクラウドAPI — Xzillaデータ連携）について2点ご相談です。①電力契約の解約情報のデータフローは IF-01 に含まれますか（旧 IF2249 相当 — 解約時の買電売電計算停止に必要）。②電力30分値の提供周期はどの程度を想定できますか（旧システムは10分毎。準リアルタイム提供は新規要素のため、可否を確認したいです）。」

### §4 誤解されやすい点
| 誤解 | 正 |
|---|---|
| #5/#6 廃止 = 業務・データが消える | 廃止は PHP コード＋5分毎専用バッチのみ; 計算停止フラグ（#5）・データ＋契約終了判定スペック（#6）は既存フローで存続 |
| IF-01 は旧4桁 IF のどれか | IF-01 = 新アーキテクチャ IF一覧（統合要件 v1.2 §4-1）の1番、未確定（CLD-07） |
| 「e-smart 流用」= 工数ゼロ | 独立デプロイ QA 回答中（*基本的には独立*）→ 新環境構築が別途発生 |
| Xzilla タスク = 受信3本 | 送信方向 `/EST` を追加（既存1フローが毎日稼働 — §7.6） |
### §5 ネクストアクション
| # | 内容 | 担当 |
|---|---|---|
| 1 | CLD-07/IF-01 フォロー; 待機中に即着手: 契約終了判定スペック抽出（§6.2 ステップ1）＋支払者4フィールド突合表（§6.2 ステップ2） | SYP |
| 2 | `/EST` 質問送付（§3） | SYP → QAデータベース |
| 3 | IF-01 質問（解約フロー＋30分値周期 — §3）送付 | SYP → mui PM 様 → 北ガス様 |
| 4 | 「既存システムを使い続けたほうがいい機能」への回答: 本グループ候補 = Xzilla SFTP→S3→DynamoDB 受信基盤（2部構成・3分冊共通: ①旧 — なし ・ ②e-smart — 4候補） | SYP → Notion |

> **方針**（合宿 Day3 — 「バッチ群…作り直す前提」、1バッチ=1タスク）: 新規受信チャネルは既存 SFTP→S3→DynamoDB フローに載せる; 0〜7時より高頻度が必須（30分値のみ）の場合だけ専用スケジュール新設（§9）。

## 第II部 — 技術詳細編
### §6 バッチ別詳細
#### §6.1 #5 `RcvCntctCancellationCommand` — 電力解約受信（IF2249）
**目的**: Xzilla 側の電力解約を同期 — 解約情報の保存＋解約済み顧客の買電売電計算停止＋当日データが揃ったら顧客情報登録完了通知 API 呼出。

**判定**（*推定*）: **バッチは廃止・業務は存続** — 廃止は PHP コード＋5分毎専用バッチ; 計算停止フラグの業務は存続; 実現 = 既存フローへファイル種別1種＋後処理1本追加; 手動フロー（管理画面での GW 無効化）は計算停止をカバーしない。・ *理由*: IF2249 は存在しない（grep 0件 — §7.5）が受信基盤8 IF＋後処理の定位置あり; 作り直し方針（§7.1）; フラグは #7 の前提。

**旧フロー**（確実）— cron `legacy_eminel_docs/docs/02_詳細設計/10_バッチ処理/mng-webap_cron設定_20241029.txt:107-108`・5分毎 ・ 🔍 `legacy_eminel_docs/sources/conciergesv-develop/src/Command/RcvCntctCancellationCommand.php:30, 99-113, 193-217, 242-243, 306-334`:
```
cron */5' ──▶ SFTP で当日解約 CSV → 契約種別 PE624/625 抽出 (:242-243) → upsert ipf_cntct_cancellations
          → 計算停止フラグ t_101.c065=1 (:306-334) → 当日分 IF2264 取込済みなら → 顧客情報登録完了通知API 呼出 (:193-217)
```
キーコード（抽出条件）— 🔍 `legacy_eminel_docs/sources/conciergesv-develop/src/Command/RcvCntctCancellationCommand.php:242-245`:
```php
// 契約種別が'PE624'または'PE625'以外は、登録しない
if ($line[58] != 'PE624' && $line[58] != 'PE625') {
    continue;
}
```
**新システム / E-GW 要件**: e-smart に IF2249 なし（確実）; E-GW に解約自動連携の個別要件なし — 解約後の GW 無効化は管理画面での手動操作と明記; IF-01 未決（CLD-07）。🔍 `eminel_gw_project/docs/eminel/1_product/11_business_process/readme.md:938-941, 945-952` ・ `eminel_gw_project/docs/eminel/2_management/20_open_issues.md:181-182`

**新フロー＋ステップ**:
```
IF-01 (CLD-07 待ち) ──▶ 既存受信フロー (§7.3) +ファイル種別1種 ──▶ 新規 handler ──▶ 解約テーブル新設
                     └▶ 後処理④: 世帯レコードに計算停止フラグ ──▶ #7 が計算時に参照
```
旧: 5分毎の専用バッチ → `ipf_cntct_cancellations` + フラグ `t_101.c065` ↔ 新: 既存8 IF フローへファイル種別+1 → 新設解約テーブル + 世帯レコードのフラグ（後処理4本目 ④）。
1. CLD-07/IF-01 具体化時: 解約フローの有無を確認; **なければ即要件追加を提起**（CLD-07/QAデータベース）。— *理由*: ないとフラグを立てる者がなく #7 が解約済み顧客を計算し続ける。
2. フローあり: 既存フローへ IF 追加（5分毎バッチは作らない）— `syp-eminelstandard-backend/src/functions/batch-get-list-file-name-from-sftp-server/app.ts`（`DEFAULT_FOLDER_CSV`/`DEFAULT_FILE_NAME_METADATA`）＋`syp-eminelstandard-backend/src/layers/common/nodejs/variables/constants.ts`（`LIST_COL_*`）＋`syp-eminelstandard-backend/src/layers/common/nodejs/interfaces/` の interface（雛形 `syp-eminelstandard-backend/src/layers/common/nodejs/interfaces/IDataIF2016.ts`）＋`syp-eminelstandard-backend/src/statemachine/batch_run_sequentially.asl.json`（Map 分岐追加）＋新規 handler（雛形 `syp-eminelstandard-backend/src/functions/batch-if2016-import-service-point-no/`）。— *理由*: 二重取込防止・多重起動防止・50,000行分割を無償継承。
3. 計算停止 = **後処理④** — 既存3本（`syp-eminelstandard-backend/src/functions/batch-send-contents-to-updated-user/`・`syp-eminelstandard-backend/src/functions/batch-update-selecting-place-no/`・`syp-eminelstandard-backend/src/functions/batch-remove-integration-expired/`）の隣に新設。— *理由*: 派生業務の定位置; 0〜7時毎時で十分（*推定* — QA A-4）。
4. テスト: PE624/625 有無のダミー CSV; フラグが #7 の買電売電計算へ反映されること。— *理由*: リスクは「抽出誤り」と「#7 へ伝播しない」の2点。
#### §6.2 #6 `RcvEmsPlsCntrPayerCommand` — 支払者マスタ受信（IF2264）
**目的**: 基幹の支払者マスタを最新に保ち＋契約終了判定で連携番号・計算停止フラグを更新。

**判定**（*推定*）: **バッチは廃止・データと業務知識は引き継ぐ** — 「5分毎全件入替え」を廃止; 支払者データは IF2023/IF2024/DM1040 の拡張で受ける（ステップ2）; 契約終了判定3条件はスペック抽出（ステップ1）; 周期は 0〜7時毎時で足りる見込み（*推定* — QA A-4）。・ *理由*: IF2264 は存在しない（grep 0件 — §7.5）が契約系3チャネルが毎日受信済み（DM1040 は支払者ロール抽出済み）; 4096M の全件入替えは「いけてない」の典型（§7.1）; E-GW に payer 個別要件なし — 実需はグルーピング; スペックは廃止予定コードのコメントにのみ存在。

**旧フロー**（確実）— cron `legacy_eminel_docs/docs/02_詳細設計/10_バッチ処理/mng-webap_cron設定_20241029.txt:105-106`・5分毎・memory_limit 4096M（:63）・ 🔍 `legacy_eminel_docs/sources/conciergesv-develop/src/Command/RcvEmsPlsCntrPayerCommand.php:63, 170-177, 245-363, 371-626`:
```
cron */5' ──▶ ipf_ems_pls_cntr_payers 全件 DELETE (:170-177) → CSV 再投入、契約種別 PE624/625/650/651/652・PG077/079 のみ (:319-329)
          → 契約終了判定 3条件適用 (コメント :373-385) → t_101 更新 (連携番号 + 計算停止フラグ)
```
コメントスペック（ステップ1の「1ページのスペック」原文）— 🔍 `legacy_eminel_docs/sources/conciergesv-develop/src/Command/RcvEmsPlsCntrPayerCommand.php:373-385`:
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
（`99991231` = 「終了日未設定」の慣用値; 380–384 行は `...` で省略。）

**新システム / E-GW 要件**: e-smart に IF2264 なし（確実）、契約／顧客は IF2023/2024/DM1040 で取込済み（§7.4）; E-GW に payer 個別機能なし（docs/eminel grep 済み）— 最近縁は F-ES-10 の顧客情報・契約情報取得; グルーピングは建物種別（Xzilla より取得 — :619）＋料金メニュー・アンペア数を必要とする。🔍 `eminel_gw_project/docs/eminel/3_requirements/00_integrated_requirements_v1.2.md:415, 619, 692-696`

**新フロー＋ステップ**:
```
IF2023/IF2024/DM1040 (毎日稼働) ──▶ TABLE_KAIIN・TABLE_IF2023_USE_CNTR_INFO・TABLE_IF2024_CUSTOMER_INFO
   + IF-01 に沿ってフィールド拡張 (支払者4フィールドに不足があれば) ──▶ 新規後処理: 契約終了判定スペック適用
```
旧: 5分毎全件入替え → `ipf_ems_pls_cntr_payers`（専用1テーブル）↔ 新: 専用テーブル0 — 既存3チャネル → `TABLE_KAIIN`・`TABLE_IF2023_USE_CNTR_INFO`・`TABLE_IF2024_CUSTOMER_INFO` + スペック適用の後処理。
1. **契約終了判定3条件をスペック化**（`legacy_eminel_docs/sources/conciergesv-develop/src/Command/RcvEmsPlsCntrPayerCommand.php:373-385`）— IF-01 を待たず即着手。— *理由*: 抽出しないと業務知識ごと消える; #6 で唯一 IF-01 非依存。
2. IF-01 具体化時: 支払者4フィールド（供給地点特定番号・IPF使用契約番号・受電地点特定番号・お客様番号）を IF2023（`syp-eminelstandard-backend/src/functions/batch-if2023-import-contract-info/`）・IF2024（`syp-eminelstandard-backend/src/functions/batch-if2024-import-user-info/`）・DM1040（`syp-eminelstandard-backend/src/functions/batch-dm1040-import-user-contract-list/`; 抽出は `syp-eminelstandard-backend/src/functions/batch-dm1040-import-user-contract-list-preprocessing/app.ts:54, 63`）と突合; 不足のみ IF-01 へ追加要請（専用 IF は要求しない）。— *理由*: IF-01 の交渉範囲を最小化。
3. 不足分は既存 handler の拡張（`syp-eminelstandard-backend/src/layers/common/nodejs/variables/constants.ts` 列＋interface＋handler）; スペック（ステップ1）を後処理として適用。— *理由*: ファイル到着単位の差分更新にし 4096M の全件入替えを排除。
4. テスト: 3条件 × 成立/不成立; フラグ・連携番号を旧ロジック手動実行と突合。— *理由*: 旧との突合だけがスペック抽出の正しさを立証。
#### §6.3 #7 `RcvHalfHourElectricPowerCommand` — 電力30分値受信（IF1156）
**目的**: Xzilla からの電力30分値を取込み、世帯ごとの買電・売電を1時間値に集約・計算 — グラフ・レポートの供給源; グループ最重量。

**判定**（確実 — 明文要件＋e-smart に確実に存在しない）: **新規** — 全11本中もっとも重量級。・ *理由*: 明文・2026スコープ「電力30分値はCルート（Xzilla経由）で取得する」; e-smart に Xzilla 経由 30分値なし（grep 0件 — §7.5）、電力/ガスは TagTag API 経由; PHP は Lambda/TypeScript で動かない — ロジックのみ継承。

**旧フロー**（確実）— cron `legacy_eminel_docs/docs/02_詳細設計/10_バッチ処理/mng-webap_cron設定_20241029.txt:109-110`・10分毎 ・ 🔍 `legacy_eminel_docs/sources/conciergesv-develop/src/Command/RcvHalfHourElectricPowerCommand.php:107-122, 192-233, 449-583, 591-725, 734-1050`（分岐 875–893）:
```
cron */10' ──▶ 速報値: emn_all/emn_fast_electric_powers 全件入替え (:449-583) ・ 確報値 (fixed_div=1): emn_confirm_electric_powers へ追記 (:591-725)
           → 2×30分→1時間値へ集約、設備構成で分岐 (:875-893) → s_102 へ → グラフ/レポート
```
キーコード（売電分岐）— 🔍 `legacy_eminel_docs/sources/conciergesv-develop/src/Command/RcvHalfHourElectricPowerCommand.php:875-882`:
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
分岐: 太陽光 → 売電は GW 計測値（日次蓄積バッチ担当 — グループ外）; コージェネ＋受電地点特定番号 → Xzilla 値から計算。

**新システム / E-GW 要件**: e-smart になし（確実 — grep 0件）、電力/ガスは TagTag API（`eminel_gw_project/docs/eminel-smart/02_product_overview.md:119`）; E-GW は明文・2026（統合要件 3-2 節）、F-ES-10 が速報値・確報値を定義、グラフ（F-ES-01）/グルーピング・レポートのデータ源、「連携テスト(Xzilla/TagTag)」行 ✅ なし = 今期。🔍 `eminel_gw_project/docs/eminel/3_requirements/00_integrated_requirements_v1.2.md:84, 692-696` ・ `eminel_gw_project/docs/eminel/1_product/10_feature_list.md:148`

**新フロー＋ステップ**:
```
IF-01 30分値 (ステップ1) ──▶ SFTP→S3→新規 handler (ステップ2; 高頻度なら専用 ScheduleV2 — §9) ──▶ 速報/確報新テーブル (ステップ3)
   ──▶ 計算 Lambda: 2×30分→1時間 + 買電/売電条件表を設置9パターンへ (ステップ4) + #5 のフラグ ──▶ 集計系バッチグループ (ステップ5)
```
旧: 10分毎 → 速報2テーブル（`emn_all`/`emn_fast_electric_powers`）+ 確報1テーブル（`emn_confirm_electric_powers`）→ `s_102` ↔ 新: 速報/確報の新2テーブル → 計算 Lambda（設置9パターン）→ 集計系グループ。
1. IF-01 の30分値部分を確定: ファイル形式・提供周期（旧 10分毎）・認証（CLD-07）。— *理由*: ステップ2〜3 が全面依存; 周期が最難点、北ガス様の合意要（§3）。
2. §7.3 パターンで受信経路: `syp-eminelstandard-backend/src/functions/batch-get-list-file-name-from-sftp-server/` → `syp-eminelstandard-backend/src/functions/batch-forward-csv-from-sftp-server-to-s3/` → 新規 handler; 周期 > 0〜7時 → `syp-eminelstandard-backend/template.yaml` に専用 `ScheduleV2`、`BatchRunSequentially` へ相乗りしない（§9）。— *理由*: 直列＋多重起動防止の8 IF 列に高頻度を入れると詰まる; 障害分離。
3. 新テーブル（`syp-eminelstandard-backend/template-dynamodb.yaml`）: 速報（上書き）／確報（追記蓄積）を分離 — 旧 `emn_fast`/`emn_confirm_electric_powers` 相当; TTL は保持期間（SVC-03）に従い検討。— *理由*: 性質が正反対; 旧も同じ理由で分離（:449-583 / :591-725）。
4. ロジック継承（PHP は移植しない）: 2×30分→1時間の集約規則＋買電/売電条件表（:875-893）を**設置9パターン**（統合要件 v1.2 3-5 節）へ再マッピング。— *理由*: 長年商用運用の業務知識; E-GW の機器構成は旧と一致せず分岐追加の可能性。
5. 出力を集計系バッチグループへ接続＋ #5（§6.1）の計算停止フラグ反映。— *理由*: #7 は入口; フラグは計算時点で適用必須。
6. テスト: 全分岐（太陽光/コージェネ/通常、速報→確報上書き、30分ペア欠損）のダミー一式; 1時間値を旧ロジック手動実行と突合。— *理由*: 設備構成分岐が最複雑（:734-1050）。
### §7 グループ共通のフロー・基盤
#### §7.1 バッチ基盤と前提
- 方針（合宿 Day3・2026-06-25）: 現行バッチ「いけてない」→ 作り直し前提、1バッチ=1タスク、バッチボーンを結合フェーズ（9月目標）前に; 「流用」= e-smart の機構・コードベース利用。🔍 `eminel_gw_project/docs/eminel/2_management/minutes/20260625_egw_camp_day3.md:35, 51, 99-103, 147-149`
- QA 独立デプロイ（swan（mui）・回答中）: *基本的には独立システムの方向* → 流用 ≠ 工数ゼロ（§4）。
- `gw-syp-dev` に E-GW コミットゼロ（web-admin: `git log origin/main..gw-syp-dev` 空; backend: 直近15コミットは e-smart 本体のみ）。*推定*: e-smart コードベースへの追記方式 — QA 管理画面（masao takahashi（mui）・回答中 — 暫定回答の要旨: e-smart と共通ソースの方向）からの推測、文書化された決定ではない; 「共通ソース」≠「共通実行環境」。
- 静的スケジュール3本のみ（`ScheduleV2`・`Asia/Tokyo` — `syp-eminelstandard-backend/template.yaml:9-11`）: ① `BatchRunSequentiallyStateMachine`、`cron(5 0-7 * * ? *)` = JST 0〜7時の毎時5分（`syp-eminelstandard-backend/template.yaml:853-888`、cron 881–882）— 本グループの受信フロー; ② `BatchMigrationIntegratedDataStateMachine`、`cron(0 8 * * ?)`（`syp-eminelstandard-backend/template.yaml:2205-2240`、cron 2233）— 送信 `/EST`; ③ `BatchGetErrorDeviceInfoOfRinnaiStateMachine`、8:00（`syp-eminelstandard-backend/template.yaml:2966-2980`）。残りは EventBridge Scheduler の動的生成、大半 one-shot（`syp-eminelstandard-backend/src/layers/common/nodejs/services/put-schedule.ts:18-33`）; 例外はオートメーション — ルール毎の週次・自動削除なし（`syp-eminelstandard-backend/src/functions/api-automation/common.ts:115, 167-175`）; **毎分ポーリングなし**（grep `rate(`: 0件）。
- スコープ決定 6/10（決定ログ）: 必須 = 暖房機能/暖房制御/照明アドバイス※/ポイント連携/グルーピング・レポート; 劣後（→2027/4〜）= 複合制御・DR・ダッシュボード・バッジ（※省エネアドバイスの誤記と思われる — *推定*; 🔍 `eminel_gw_project/docs/eminel/2_management/22_decisions.md:30-31`）・ SYP 範囲（QA 調査範囲・swan（mui）・回答中）: `conciergesv`/`eminelsv` は調査対象であり継続開発範囲ではない; GW 通信は HEMS-SV（m2-cloud）経由、スペック後日共有（B-2、§10）。
#### §7.2 旧システムの受信方式
🔍 `legacy_eminel_docs/docs/02_詳細設計/10_バッチ処理/cron設定概要.txt:1-37`（flock は同フォルダ `eminel-mng-webap.20240909.tgz` 内 `.sh`）:
```
Xzilla ──SFTP (5〜10分毎)──▶ [中間サーバーのディスク] ──▶ 3本の PHP Command (cron + flock) ──▶ [PostgreSQL]
                                                           · RcvCntctCancellation…  ──▶ ipf_cntct_cancellations + フラグ t_101.c065
                                                           · RcvEmsPlsCntrPayer…    ──▶ ipf_ems_pls_cntr_payers + t_101
                                                           · RcvHalfHourElectric…   ──▶ emn_all/emn_fast/emn_confirm + s_102
```
旧: SFTP → 中間サーバーのディスク → 3本の PHP Command（cron 5〜10分 + flock）→ PostgreSQL ↔ 新: SFTP → S3 → 8本の handler Lambda → DynamoDB、0〜7時ウィンドウ、多重防止 asl（5–38）＋`CsvDownloadHistory`（§7.3）。
#### §7.3 e-smart の受信方式（確実）
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
新 ↔ 旧: S3 が中間サーバーのディスクを、8 handler＋後処理3本が単発 PHP Command を、asl ブロック（5–38）＋`CsvDownloadHistory` が flock を、0〜7時ウィンドウが 5〜10分 cron を置き換える。
- 編成 `syp-eminelstandard-backend/src/statemachine/batch_run_sequentially.asl.json`: 多重起動防止（5–38）→ temp 掃除 → 一覧取得 → 8 IF 並列 forward → import → 後処理3本; IF フォルダ8種はコード内定義 — 🔍 `syp-eminelstandard-backend/src/functions/batch-get-list-file-name-from-sftp-server/app.ts:149-169`; `.dat` 読取（52–66）; 二重取込防止 `CsvDownloadHistory`（69–87 — 実際の役割: §11 差異表）; 50,000行単位で S3 へ分割 — 🔍 `syp-eminelstandard-backend/src/functions/batch-forward-csv-from-sftp-server-to-s3/app.ts:56-64`。
- 格納先: IF2241/IF2242/DM1040 → `TABLE_KAIIN`（ゆえに直列）; 残り5チャネルは専用テーブルで並列（asl 493–794）— 各 IF の詳細: §7.4。
- 「fake 会員」マージ時 5分ロック（`UPDATE_LOCK_TTL_MINUTES = 5`・`TABLE_KAIIN_UPDATING` へ書込・TTL 自動失効 — 🔍 `syp-eminelstandard-backend/src/functions/batch-if2241-import-tagtag-kaiin/app.ts:69, 102-111`）; 39 本の API ハンドラが `syp-eminelstandard-backend/src/layers/common/nodejs/business-logic/check-kaiin-updating.ts:10-15` で確認。
- 後処理3本: ① 新規会員へ配信中コンテンツ再配信（`syp-eminelstandard-backend/src/functions/batch-send-contents-to-updated-user/app.ts:79-132`）; ② 選択宅変更＋「ゆーぬっく」バッジ（YUNUKKU・`PG003`・「ゆーぬっく２４ネオ」`syp-eminelstandard-backend/src/layers/common/nodejs/variables/constants.ts:1065`; `syp-eminelstandard-backend/src/functions/batch-update-selecting-place-no/app.ts:89-143, 283-296`＋`syp-eminelstandard-backend/src/layers/common/nodejs/variables/constants.ts:1909`; 対象 `TABLE_KAIIN`＋`TABLE_IF2023_USE_CNTR_INFO`）; ③ ガス契約終了時の連携・機器削除（`syp-eminelstandard-backend/src/functions/batch-remove-integration-expired/app.ts:44-79` — `TABLE_IF2023_USE_CNTR_INFO` を読み `TABLE_KAIIN`/`TABLE_MUI_DEVICE`/`TABLE_MUI_SENSOR` を削除）。
#### §7.4 IF チャネル別詳細表
フィールドは enum `LIST_COL_*`（`syp-eminelstandard-backend/src/layers/common/nodejs/variables/constants.ts:468-565`、interface `syp-eminelstandard-backend/src/layers/common/nodejs/interfaces/IData*.ts` — 一次ソース）; 基幹側は `eminel_gw_project/docs/eminel-smart/02_product_overview.md:68-75`（`eminel_gw_project/docs/eminel-smart/03_backend_models.md:90-97` と突合; 食い違いはコードを正 — §11）; 「x/y列」= コードが使う y 列中 x 列:

| IF | 基幹側 | 主要フィールド（コード） | 格納先 | 役割 |
|---|---|---|---|---|
| IF2241 | `TAG_KAIIN` | 5/11: `kaiinBango`（キー）、`custShikibetsuBango`、`status`、`loginId`、`yubinBango` | `TABLE_KAIIN`（資料: 「KaiinTable + 16関連」:73） | 会員アイデンティティの背骨 — アプリ↔北ガス顧客マージ起点; IF2242/DM1040 は本チャネル完了が前提（直列） |
| DM1040 | `MRT_TAGTAGAPI` | 5/14: `roles`（支払者抽出）、`kaiinbango`、`oc_z_customer_no`、`oc_j_supply_place_no`、`curd_flg` | `TABLE_KAIIN` — `list_contract` | 会員ごとの契約リスト; 支払者ロールが既にある（§6.2） |
| IF2242 | `tag_kaiinzokusei` | 3/3: `kaiinBango`、`zokuseiId`、`kaitouCd` | `TABLE_KAIIN` — `list_zokusei` | 会員属性 — ターゲティング基盤 |
| IF2016 | `ipf_sp_history` | 5/7: `source_sp_num`（PK）、`reg_start_ymd`/`reg_end_ymd`、`cis_use_cntr_num`、`use_type_code` | `TABLE_IF2016_SERVICE_POINT_NO_INFO` | 供給地点マスタ — 地点↔契約の紐づけ |
| IF2023 | `ipf_use_cntr_history` | 6/14: `source_use_cntr_num`（PK）、`reg_start_ymd`、`cntr_clsfy_code`（#5/#6 が抽出する PE/PG）、`cntr_start_ymd`/`cntr_end_ymd`、`cntr_watt` | `TABLE_IF2023_USE_CNTR_INFO` | 使用契約＋種別・期間 — 後処理③が失効判定に読む |
| IF2024 | `ipf_cus_meigi` | 5/8: `source_cus_meigi_num`（PK）、`links_cus_num`、`sex`、`birth_yyyy`、`household_num` | `TABLE_IF2024_CUSTOMER_INFO` | 顧客属性 — ターゲティング・世帯統計 |
| IF2029 | `ipf_bld` | 4/5: `source_bldno`（格納時 `bld_no` — `syp-eminelstandard-backend/src/functions/batch-if2029-import-building-info/app.ts:30`）、`bld_divcod_1`（建物種別）、`bld_use_type`、`newbldno_area` | `TABLE_IF2029_BUILDING_INFO` | 建物情報 — グルーピングが要る建物種別の供給元（§6.2） |
| IF2223 | `lnk_ot_pgedgkk` | CSV 130項目超（`eminel_gw_project/docs/eminel-smart/02_product_overview.md:72`）、コードは13列; 代表: `oc_z_gas_sp_no`（→PK `gas_sp_no`）、`oc_j_gkiki_clsfy_code`＋`oc_h_estkk_mno`（連結 SK `equipment_code` — `syp-eminelstandard-backend/src/functions/batch-if2223-import-equipment/app.ts:49`）、`oc_z_kiki_hinmok_code`、`oc_z_remove_date` | `TABLE_IF2223_EQUIPMENT` | 設置ガス機器 — 機器系機能のデータ基盤 |
#### §7.5 旧3 IF は e-smart に存在しない（確実）
backend 全体 grep `IF1156`・`IF2249`・`IF2264`・`30分`・`HalfHour`・`half_hour`・`速報`・`確報`・`electric_power`・`cntct` = **0件**。（`ElectricPower` は `syp-eminelstandard-backend/src/layers/common/nodejs/services/daikin.ts:73` の1件のみ・無関係; `payer` は DM1040 の支払者ロール抽出定数のみ — `syp-eminelstandard-backend/src/functions/batch-dm1040-import-user-contract-list-preprocessing/app.ts:54, 63`。）
#### §7.6 送信方向 `/EST`（確実）
```
[当日取得済み機器データ] ──▶ BatchMigrationIntegratedDataStateMachine (毎日8:00 — template.yaml:2215-2226)
        ──▶ CSV 6種 (給湯器系5種 + 赤外線リモコン) ──SFTP・アップロード専用アカウント──▶ [/EST]  宛先 = Xzilla/DWH? ※推定（未確認）
```
旧: 相当する送信なし ↔ 新: 1フロー、CSV 6種/日（給湯器系5＋赤外線リモコン1）、8:00。
- 🔍 `syp-eminelstandard-backend/src/layers/common/nodejs/services/upload-data-backup-to-sftp.ts:22-43, 52-57` — `pathExport = '/EST'`、同一 SFTP サーバー、アップロード専用ユーザー（`username_for_upload`/`private_key_for_upload`）。※推定（未確認）: 宛先は Xzilla/DWH と思われる — 接続先は secret 管理、mui 様へ確認（§3）; 該当すれば「EMINELデータの共有」（F-ES-10 — `eminel_gw_project/docs/eminel/3_requirements/00_integrated_requirements_v1.2.md:696`）の既存実装。
- Xzilla タスク一覧にこの送信方向を追加（§4）。合宿 Day3 議事録 126 行の見立て（アプリログ送信も既にある可能性）は確認の結果**なし**（管理画面ダウンロードのみ）。
### §8 新旧データ対照
| 旧データ（PostgreSQL） | 新（DynamoDB）／計画 | 状態 |
|---|---|---|
| `ipf_cntct_cancellations`（#5） | IF-01 に沿った解約テーブル新設、既存フローへ（§6.1 ステップ2） | ❌ |
| `t_101` のフラグ＋連携番号（`c065` 等 — #5/#6） | 世帯レコード上のフラグを後処理④で設定（§6.1 ステップ3）＋契約終了判定後処理（§6.2 ステップ3） | ❌ |
| `ipf_ems_pls_cntr_payers`（#6） | 専用テーブルなし — `TABLE_KAIIN`＋`TABLE_IF2023_USE_CNTR_INFO`/`TABLE_IF2024_CUSTOMER_INFO` に分散、IF-01 で拡張（§6.2 ステップ2） | ⚠️ |
| `emn_all`/`emn_fast_electric_powers`（速報 — #7） | 速報用新テーブル（`syp-eminelstandard-backend/template-dynamodb.yaml` — §6.3 ステップ3） | ❌ |
| `emn_confirm_electric_powers`（確報 — #7） | 確報用新テーブル・分離（§6.3 ステップ3） | ❌ |
| `s_102`（1時間値 — #7） | 新計算 Lambda の出力 → 集計系バッチグループ（§6.3 ステップ5） | ❌ |

**集計**: ✅ 0 ・ ⚠️ 1 ・ ❌ 5 — 3 IF 不在の現状そのまま; 支払者データのみ既存の受け皿あり（3テーブルに分散）。機構: 受信経路 SFTP→ディスク＋cron 5〜10分毎 → SFTP→S3→DynamoDB 0〜7時毎時（`syp-eminelstandard-backend/src/statemachine/batch_run_sequentially.asl.json`）; 多重防止 `flock` → asl 内ブロック（5–38）＋`CsvDownloadHistory`; スケジュール 固定 cron（`/etc/cron.d/eminel-mng-webap`）→ 静的 `ScheduleV2` 3本＋動的 one-shot（§7.1）。
### §9 #7 のスケジュール設計
| 基準 | A. `BatchRunSequentially` 相乗り | B. `syp-eminelstandard-backend/template.yaml` に専用 `ScheduleV2` |
|---|---|---|
| 適用条件 | 周期が 0〜7時毎時ウィンドウに収まる | 周期がそれより高頻度 |
| リスク | 直列＋多重起動防止の8 IF 列が詰まる | 専用フローの多重防止を自前で用意 |
| 障害分離 | 基幹取込全体へ波及 | 分離できる |

選択根拠（§6.3 ステップ2）: 高頻度なら **B**。再検討条件: 北ガス様が実周期を確定した時点（§3-3）— 低頻度なら A で可。
### §10 QA一覧（対象者別）
対象: A = 北ガス様（mui PM 様経由）・ B = mui 様直接 ・ C = 旧システム引き継ぎ元（チャネルがあれば）・ D = アプリチーム: なし（本グループはアプリに触れない）。

| # | 質問 | 理由 | 重要度 |
|---|---|---|---|
| A-1 | IF-01 の入出力＋認証（= CLD-07 決着、送信方向含む） | 3バッチすべての前提 | 🔴 |
| A-2 | IF-01 に解約フローはあるか（§3） | ないと #7 のフラグを立てる者がいない | 🔴 |
| A-3 | 30分値の提供周期（§3） | §9 を左右 | 🔴 |
| A-4 | 0〜7時毎時で解約業務／支払者マスタは足りるか | #5/#6 判定内の *推定* | 🟡 |
| B-1 | `/EST` の宛先 = Xzilla/DWH か（§3） | F-ES-10 既存実装かの確定; タスク一覧に影響 | 🟡 |
| B-2 | HEMS-SV（m2-cloud）スペック共有 | SYP 範囲の境界確定 | 🟢 |
| C-1 | 支払者4フィールドの意味・使い方＋抽出した契約終了判定スペックの実運用一致確認 | スペックの根拠はコメントのみ — 誤読リスク低減 | 🟡 |

処理順序: A-1 → A-2/A-3/A-4（同じ便で質問）→ §6.1 ステップ2〜3・§6.2 ステップ2〜3・§6.3 全体; B-1 は独立・即送付可; C-1 は #6 スペック確定前に（ステップ1 の抽出は即着手）。
### §11 根拠と確度
| 内容 | 出典 |
|---|---|
| 旧3バッチの挙動 | `legacy_eminel_docs/sources/conciergesv-develop/src/Command/`（Rcv* 3ファイル）; `legacy_eminel_docs/docs/03_API仕様/04_バッチ一覧.md`; cron `legacy_eminel_docs/docs/02_詳細設計/10_バッチ処理/*.txt` |
| e-smart 現状＋E-GW コミットゼロ | `syp-eminelstandard-backend`@`dc39aa39`: `template*.yaml`、`syp-eminelstandard-backend/src/functions/**`、`syp-eminelstandard-backend/src/layers/common/nodejs/**`、`syp-eminelstandard-backend/src/statemachine/*.asl.json` ・ `syp-eminelstandard-web-admin`@`e550326`: `git log origin/main..gw-syp-dev` 空; backend 直近15コミットは e-smart 本体のみ |
| 要件・方針・スコープ・未決事項 | `eminel_gw_project/docs/eminel/`: 統合要件 v1.2（3-2、F-ES-01/10）、`10_feature_list.md`、`11_business_process/readme.md`、`22_decisions.md`、`20_open_issues.md`（CLD-07、SVC-03）、合宿 Day3 議事録 |
| ESTA 調査資料（差異あり — 下表） | `eminel_gw_project/docs/eminel-smart/`（6ファイル） |
| QA（Notion）3件（回答中・2026-08-04） | 独立デプロイ（swan）・調査範囲（swan）・管理画面（masao takahashi） |

| 段階 | 内容 |
|---|---|
| ✅ 確実 | 旧3 IF なし（grep 0件）; 8 IF フロー＋`TABLE_*`＋5分ロック＋後処理3本; `/EST` 実在（6種・8:00）; 旧3バッチの挙動; 30分値の明文要件（2026）; E-GW コミットゼロ; アプリログ送信経路なし |
| ⚠️ *推定* | #5/#6 の判定提案; e-smart コードベースへの追記方式; 0〜7時で解約/支払者に足りる（QA A-4）; 「照明アドバイス」は省エネアドバイスの誤記の可能性 |
| ❓ 未確認 | `/EST` 宛先（※推定（未確認）・secret 管理）; IF-01 の内容（CLD-07）; QA 3件はいずれも回答中 |

788b438 → fbc0af0（6コミット）: 差分は `eminel_gw_project/docs/eminel/3_requirements/app/` 13ファイル＋skill 1行のみ — 本書引用ファイルに変更なし、2026-08-06 確認済み（配信・通知系分冊は変更のあった B05/D03 を引用、行番号は当該分冊側で更新済み）。

**ESTA 調査資料と実コードの差異**（本グループ関連5点; 残る1点 — Push 件数 — は配信・通知系分冊）:

| 資料の記載 | 実コード |
|---|---|
| 基幹取込「日次・深夜〜早朝」（`eminel_gw_project/docs/eminel-smart/02_product_overview.md:30, 63-64`） | `cron(5 0-7 * * ? *)` — JST 0〜7時の毎時（§7.1） |
| 会員マージロック「6分」（`eminel_gw_project/docs/eminel-smart/02_product_overview.md:73, 78`） | `UPDATE_LOCK_TTL_MINUTES = 5`（§7.3） |
| `CsvDownloadHistory` = 管理者ダウンロード履歴を示唆（`eminel_gw_project/docs/eminel-smart/03_backend_models.md:107`） | SFTP からの受信履歴（二重取込防止）— 管理者ダウンロードと無関係（§7.3） |
| 「自動化ルール実行（毎分）」（`eminel_gw_project/docs/eminel-smart/02_product_overview.md:85`） | 毎分なし — ルール毎の週次を動的生成（§7.1; grep `rate(`: 0件） |
| ランタイム「Node.js 20.x, arm64」（`eminel_gw_project/docs/eminel-smart/02_product_overview.md:49`） | `Runtime: nodejs24.x`（`syp-eminelstandard-backend/template.yaml:181`; 共通レイヤーの CompatibleRuntimes は nodejs20.x — 同:3163） |
