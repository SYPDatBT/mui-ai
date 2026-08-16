# 現行システム — EMINEL-smart（エコ暖房ポイント）

## 概要

現行のEMINEL-smartバックエンド（`syp-eminelstandard-backend`）には、**月間の平均暖房設定温度を評価してポイントを付与するバッチは存在しない** — テーブルも無く、月ごとに温度を集計するロジックも無く、暖房設定温度のしきい値に基づくポイント付与理由（`POINT_BADGE_FOR`）も無い（「暖房機器の操作」のような、暖房機器の操作／接続に関するチェックリスト項目があるのみである）。ただし、**実際にポイントを付与するためのPoint Infinity呼び出しのインフラ**（旧バッチの `PointInfinity::givePoints()` に相当）は、共用の1つのLambda（`give-point-to-point-infinity`）として**既に存在する**。現在は共用のポイント／バッジ付与フロー `givePointBadgeForUser` および各バッチ（DR完了など）から呼び出されている — 温度に基づいて計算するフローは1つも存在しない。

## 関連する関数名とコード上の位置

| 関数／Lambda | 場所（`src/functions/`） | 現行の役割 | エコ暖房の業務に該当するか |
|---|---|---|---|
| `GivePointToPointInfinityFunction` | `give-point-to-point-infinity/app.ts` | 共用のLambda。上書き用のフィールド（`JIYU_CD`, `JIYU_DET_CD`, `FUYO_PT`, `FUYO_RIYU`…）を含む `event` を受け取り、Point InfinityのAPIを呼び出す — 旧バッチの `sendToPointInfinity()` に相当する | 該当しない — API呼び出しのインフラにすぎず、ポイント付与条件を自ら判断することはない |
| `GetPointQuantityFromPointInfinityFunction` | `get-point-quantity-from-point-infinity/app.ts` | Point Infinityから現在の保有ポイント数を取得する | 無関係 |
| `give-point-badge.ts`（`api-user`）＋ `givePointBadgeForUser` | `api-user/give-point-badge.ts` | `POINT_BADGE_FOR` に応じてポイント／バッジを付与する（ログイン、DR参加、tip閲覧、アンケート回答、ガス／電気／保守の契約締結、チェックリスト完了など） — 内部テーブル（`PointBadgeStats`／`UserBadgeSummary`）へ書き込み、**かつ**共用Lambda経由でPoint Infinityを呼び出して実際にポイントを付与する。PIエラー時のロールバックがある | 該当しない — 暖房設定温度のしきい値に応じてポイントを付与する理由は1つも存在しない |

**現在の `GivePointToPointInfinityFunction` の呼び出し箇所**：本Lambdaは、共用のポイント／バッジ付与フロー `givePointBadgeForUser`（layer `give-point-badge-for-user.ts:364-367`）からinvokeされる — API stack全体で使用される（give-point-badge, read-tip, answer-survey, first-login-in-month, action-tip…；`template.yaml:3123` がnested stackへARNを渡し、`template-api.yaml:202` が変数 `LAMBDA_GIVE_POINT_TO_POINT_INFINITY` を設定する） — さらに2つのバッチ `BatchEndDrFunction`（DR完了時のポイント付与）、`BatchUpdateSelectingPlaceNoFunction` も、まさにこのlayerを経由して**間接的に**呼び出している。暖房設定温度に関係するフローは1つも存在しない。

## 全体像

| 項目 | 内容 |
|---|---|
| **現行の役割** | 「月間の平均暖房設定温度に応じてポイントを付与する」業務は存在しない。他の理由のために共用されるPoint Infinityへのポイント付与インフラのみが存在する。 |
| **Input** | 無し — 現行のEMINEL-smartには、月ごとの平均暖房設定温度を保持するテーブルが存在しない。 |
| **Output** | 旧システムの `ConEcoPoints`（`s_141`）に相当する内部のポイント台帳テーブルは存在しない。現在のポイント／バッジは `POINT_BADGE_FOR` 単位で保存される（温度のしきい値による項目は無い）。 |
| **総括** | E-GWで本業務を改めて実装する場合（要件 `F-ES-04`）、**新規に**構築が必要なのは、月ごとの平均暖房設定温度を集計するバッチとしきい値判定のロジックのみである。月単位の重複付与防止（`checkUserHasReceivedPoint` 経由の `pointBadgeStatsSk` キー）、内部のポイント台帳（`PointBadgeStats`／`UserBadgeSummary`）、およびPIエラー時のロールバックは、共用フロー `givePointBadgeForUser` に**既に存在する** — 最終的なPoint Infinity呼び出しのステップとして `GivePointToPointInfinityFunction` とあわせて**再利用**でき、書き直す必要はない。なお `10_feature_list` によると、ポイント管理・PI連携（`F-ES-09`）のブロックとアプリ側のポイント・省エネアドバイスは劣後（✅）となっている — 実装時期についてはmui／Kitagasと優先度を確認する必要がある。 |

---

## 出典

| 内容 | 根拠 |
|---|---|
| Point Infinityへポイントを付与する共用Lambda | `syp-eminelstandard-backend/src/functions/give-point-to-point-infinity/app.ts` |
| 本Lambdaの現在の呼び出し箇所 | `syp-eminelstandard-backend/template.yaml:3123`, `template-api.yaml:202`, `src/layers/common/nodejs/business-logic/give-point-badge-for-user.ts:364-367`（変数 `LAMBDA_GIVE_POINT_TO_POINT_INFINITY`） |
| 現在存在する内部のポイント／バッジ付与理由の一覧（`POINT_BADGE_FOR`） | `syp-eminelstandard-backend/src/layers/common/nodejs/variables/constants.ts:1340-1358` |
| 契約に応じたポイント／バッジ付与ロジック（温度とは無関係） | `syp-eminelstandard-backend/src/functions/api-user/give-point-badge.ts` |
| E-GW側の対応する要件 | `eminel_gw_project/docs/eminel/3_requirements/00_integrated_requirements_v1.2.md` — `[F-ES-04] エコ暖房ポイント`、`[F-ES-09]`（ポイント付与対象となる行動の例「目標値の達成（暖房設定温度が推奨温度以下等）」） |
| ポイント関連ブロックの優先度の状態（劣後 ✅） | `eminel_gw_project/docs/eminel/1_product/10_feature_list.md:93,95,130` |
