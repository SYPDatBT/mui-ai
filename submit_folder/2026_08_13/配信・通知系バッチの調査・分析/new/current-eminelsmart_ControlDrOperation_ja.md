# 現行システム — EMINEL-smart（DR 機器制御）

## 概要

調査済みのXzilla／EcoMission／EcoPointsの各バッチ（同等のものが存在しない）とは異なり、**EMINEL-smartには機器制御DRの業務が完成された形で既に存在し、対応する機器種別は** `ControlDrOperationCommand` より広い：エコジョーズ（Rinnai/Noritz — メーカーのクラウドAPI経由）、エアコン（MUI赤外線 **または** Daikinクラウド経由）、ファンコンベクター（MUI赤外線） — これに対し旧バッチが制御するのはちょうど1種類のみ（ECHONET Lite/GW経由の暖房制御ユニット）である。アーキテクチャ上の重要な差異：**e-smartはメーカー（Rinnai/Noritz/Daikin）のクラウドAPIを直接呼び出して機器を制御する**、またはMUIの赤外線サービスを利用する — **内部のGWを一切経由しない**。e-smartの機器がWi-Fi経由でメーカーのクラウドへ直接接続することに対応しているためである。**E-GW**の機器（マルチセンサー、Wi-SUN HAN/ECHONET Lite経由の暖房制御ユニット）はかならず**GW管理クラウド**（IF-02/07）を経由する必要がある — そのため、e-smartの「機器へ指令を送信する」部分はそのまま適用できないが、**DRの調整全体（制御前の状態を保存 → 制御 → 期限終了後に復元 → ポイント／バッジ付与 → 通知）**は既存の枠組みであり、一から書き直すのではなく新しい機器の分岐を1つ追加して拡張できる。

## 関連するバッチ／関数名とコード上の位置

| 関数／Lambda | 場所（`src/functions/`） | 役割 |
|---|---|---|
| `batch-start-dr`（＋ `-preprocessing`） | `batch-start-dr/app.ts` | DRの開始時点：参加ユーザーごとに、**制御前の機器の状態を保存**したうえで、DRの設定（`control_setting`）に従って制御指令を送信する |
| `batch-end-dr`（＋ `-preprocessing`） | `batch-end-dr/app.ts` | DRの終了時点：設定があればDR参加のポイント／バッジを付与し（`givePointBadgeForUser`、`POINT_BADGE_FOR.DR` に対応）、そのうえで**保存済みの状態へ機器を復元する**（先にOFF、後にON — `offDevices` → `onDevices` の順のとおり） |
| `controlDevice`（DR＋Automationで共用） | `src/layers/common/nodejs/business-logic/control-device.ts` | 実際に機器を制御する関数 — `server_type` によるswitch：`RINNAI`／`NORITZ`／`DAIKIN`（ユーザーごとの個別トークンでメーカーのクラウドAPIを呼び出す）または `MUI_CLOUD`（MUI社内の赤外線サービス経由） |
| `create-dr.ts` ／ `update-dr.ts` | `src/functions/api-dr/` | DRスケジュールの作成／更新 — **配信時刻に対してEventBridge Schedulerのone-shotのみを登録する（`send_time` に従う `SEND_DR`）**；その時刻になると `batch-send-dr` の一連の処理がDRをユーザーへ配信し（`TABLE_DR_USER_ACTION`）、続いて `batch-send-dr-complete` が実行時刻（`implement_start_time`／`implement_end_time`）どおりに `START_DR`／`END_DR` のone-shotを登録し、あわせて `TABLE_DR_STATS` へ書き込む — いずれもone-shotであり、旧システムのような毎分のポーリングは行わない |

**現在DR制御に対応している機器**：エコジョーズ（Rinnai または Noritz 経由の床暖房／パネルヒーター）、エアコン（Daikinクラウド経由またはMUI赤外線経由）、ファンコンベクター（MUI赤外線）。**見当たらないもの**：コレモ、蓄電池、エコキュート、ハイブリッド給湯器（いずれも要件 F-ES-07/08 の一覧にはあるが、上記3グループの範囲外である）。

## 全体像

| 項目 | 内容 |
|---|---|
| **現在の役割** | DRのスケジュールに従って暖房機器／エアコンのON／OFF／設定温度変更を制御し、期限終了後に状態を復元し、ポイント／バッジを付与し、Push通知を行う（`batch-push-notice-dr-*`）。 |
| **Input** | `TABLE_DR`（DRの設定：機器種別ごとの `control_setting`、`point_quantity`、`has_badge`）＋ `TABLE_DEVICE`／`TABLE_MUI_DEVICE`（ユーザーの機器）＋ 各社ごとの個別の連携トークン（Rinnai/Noritz/Daikin、`getIntegrationSettingInfo`）。 |
| **Output** | メーカーのクラウドAPI（Rinnai/Noritz/Daikin）またはMUIの赤外線サービスを呼び出して実際に制御する ＋ `TABLE_DEVICE`／`TABLE_MUI_DEVICE` へ `latest_control_by`／`latest_control_id` を更新する ＋ `TABLE_DR_USER_ACTION.pre_control_status`（制御前の状態。復元に使用する）＋ `givePointBadgeForUser` によるポイント／バッジ（`TABLE_POINT_BADGE_STATS`・`TABLE_USER_BADGE_SUMMARY`・`TABLE_SYSTEM_STATS` へ書き込む）。 |
| **処理概要** | 1. `api-dr` 経由でDRを作成／更新する → `send_time` に従って `SEND_DR` のone-shotを登録する；配信時刻になると、`batch-send-dr` の一連の処理がDRをユーザーへ配信し、続いて `batch-send-dr-complete` が実行時刻どおりに `START_DR`／`END_DR` のone-shotを登録する（ポーリングは行わない）。<br>2. 開始時（`batch-start-dr`）：ユーザーごとに、種別（エコジョーズ／エアコン／ファンコンベクター）に応じた機器を取得し、**現在の状態を保存**したうえで、`control_setting`（ON／OFF／設定温度変更）に従って制御する。<br>3. 終了時（`batch-end-dr`）：設定があればポイント／バッジを付与し（`point_quantity>0` または `has_badge`）、そのうえで保存済みの状態を読み直して機器を**復元する**（先にOFF、後にON）。 |

### `ControlDrOperationCommand`（旧システム）との簡易比較

| | 旧システム | 新システム |
|---|---|---|
| 機器の範囲 | 1種類のみ：暖房制御ユニット（ECHONET Lite、GW経由） | 3グループ：エコジョーズ（Rinnai/Noritz）、エアコン（Daikin／MUI赤外線）、ファンコンベクター（MUI赤外線） — コレモ／蓄電池／エコキュートはまだ無い |
| 指令の伝送経路 | ECHONET Lite → `Instructions` → `hemssv` → GW → 機器 | メーカーのクラウドAPI（Rinnai/Noritz/Daikin）またはMUIの赤外線サービスを直接呼び出す — **GWを一切経由しない** |
| 終了の方式 | 独立したフェーズ2（ON/OFF）、またはECHONETの指令に終了時刻をあらかじめ埋め込む（CHANGE_TEMP） | 制御前の状態を保存 → 終了時にその状態のとおりに復元する（機器への指令に時刻を埋め込まない） |
| トリガーの仕組み | 毎分のポーリングで `start_at`／`end_at` と比較する | EventBridge Schedulerが時刻どおりに発火する（one-shot）、ポーリングは行わない |
| ポイント付与／通知 | `ConMessages`（category=DR、「開始した」ことのみを通知） | `givePointBadgeForUser`（ポイント／バッジ）＋ `batch-push-notice-dr-*`（開始／終了それぞれ別個の通知） |
| **E-GWの機器へ適用できるか？** | — | **直接には不可** — E-GWの機器はGW管理クラウド（IF-02/07、MQTT）を経由するのであり、メーカーのクラウドAPI／MUI赤外線ではない。`controlDevice()` にGW管理クラウド経由で呼び出す新しい `server_type` の分岐を1つ追加し、既存の状態の保存／復元＋ポイント／バッジ＋通知の部分を再利用する必要がある |

---

## 出典

| 内容 | 根拠 |
|---|---|
| DR開始時の制御 | `syp-eminelstandard-backend/src/functions/batch-start-dr/app.ts` |
| DR終了時の復元＋ポイント付与 | `syp-eminelstandard-backend/src/functions/batch-end-dr/app.ts` |
| 共用の機器制御関数（DR＋Automation） | `syp-eminelstandard-backend/src/layers/common/nodejs/business-logic/control-device.ts` |
| DRスケジュールの作成＋EventBridge Schedulerの登録 | `syp-eminelstandard-backend/src/functions/api-dr/create-dr.ts`, `update-dr.ts`, `src/functions/batch-send-dr-complete/app.ts` |
| E-GW側の対応する要件 | `eminel_gw_project/docs/eminel/3_requirements/00_integrated_requirements_v1.2.md` — `[F-ES-07/08] 機器制御DR`, UC-05 01-3 |
