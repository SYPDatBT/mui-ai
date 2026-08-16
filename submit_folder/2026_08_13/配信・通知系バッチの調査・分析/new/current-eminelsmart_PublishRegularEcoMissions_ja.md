# 現行システム — EMINEL-smart（省エネアドバイス配信）

## 概要

現行のEMINEL-smartバックエンド（`syp-eminelstandard-backend`）には、**計測／使用量データから条件を自動的に判定して省エネアドバイスを配信するバッチは一切存在しない** ― 「設定温度が高い」「暖房をつけたままである」「ガス／電気の使用量がグループ平均より多い」「前年比でCO2が削減された／されていない」に相当するロジックはいずれも存在しない。あるのは**管理者が自ら作成するコンテンツの配信基盤**（`Tip`/`News`/`Survey`）であり ― 配信対象は静的な属性またはCSVの一覧で絞り込まれ、動的に計算した条件によるターゲティングは行われない。「CO2削減」機能が過去に想定されていたが未実装であることを示す痕跡が1つある：定数 `POINT_ACTION.CO2_REDUCTION` は定義されているが、コード内の他のどこでも使用されていない。

## 関連するバッチ／関数名とコード上の位置

| 関数／Lambda | 場所（`src/functions/` 以下） | 現在の役割 | 「計測データから条件を判定する」業務に該当するか |
|---|---|---|---|
| `batch-send-tip-preprocessing` / `batch-send-tip` / `batch-send-tip-complete` | `batch-send-tip*/app.ts` | 管理者があらかじめ作成した「Tip」（エコライフのコツ）を配信対象ユーザーの一覧へ送信する | 該当しない ― `Tip` は静的なコンテンツであり、計測データから条件を判定するステップは存在しない |
| `batch-send-news*`, `batch-send-survey*` | 同様、News/Survey向け | 同じ3段階の枠組み（preprocessing → send → complete） | 該当しない |
| `checkUserMatchesConditionAttribute` | `business-logic/check-user-matches-condition-attribute.ts` | Tip/Newsの配信対象を**静的な属性**で絞り込む：世帯人数、エアコンの有無、太陽光発電の有無、住宅の所有形態、契約種別（ガス／電気／保守）、建物種別、保有機器 | 該当しない ― すべて申告／1回の参照で得られる属性であり、時系列の計測値から算出するしきい値は存在しない |
| `givePointBadgeForUser` + `POINT_BADGE_FOR.TIP` | `api-user/give-point-badge.ts`, `constants.ts:1340-1358` | ユーザーがTipを1件閲覧した際にポイント／バッジを付与する | 該当しない |
| `POINT_ACTION.CO2_REDUCTION` | `constants.ts:1306-1311` | 定数として定義されている（`'co2_reduction'`）が、**他に参照している箇所が一切ない** ― 機能として想定されていたが未実装であることを示す痕跡 | ― |

## 全体像

| 項目 | 内容 |
|---|---|
| **現在の役割** | **管理者が自ら作成した**コンテンツ（Tip/News/Survey）を、静的な属性またはCSVの一覧に基づいてユーザーへ配信する ― このコンテンツ配信の枠組みの中に、動的に計算した条件でターゲティングする業務は存在しない；熱中症／見守りの警報についてのみ、センサー値に基づくPushのパイプライン（`batch-receive-data-infrared-remote` → `batch-control-device-and-push-notice-sensor`）があるが、省エネアドバイスではない。 |
| **Input** | `TABLE_TIP`/`TABLE_NEWS`/`TABLE_SURVEY`（管理画面から管理者が手入力したコンテンツ）＋ 配信対象の一覧（全件／静的な属性による／CSVで指定）。センサーデータは読み取らず、ガス／電気の使用履歴も読み取らず、`ConSensorMonthlyAveValues` に相当するグループ別平均テーブルも存在しない。 |
| **Output** | 共通のパイプラインを通じてPush通知を送信し、ユーザーがコンテンツを閲覧した際にポイント／バッジを付与する（`POINT_BADGE_FOR.TIP` など）。「顧客ごとのミッション」テーブル（`ConEcoMissionDestinations`）は存在しない ― 閲覧状態は `TipUserAction` で保持される。 |
| **総括** | 旧バッチの19個のミッションをE-GW（`F-ES-03`）で再実装するには、種別ごとの**条件判定部分を完全に新規で構築する**必要がある（計測データの読み取り／グループ化、しきい値／平均との比較）― ただし、最終的な通知送信層としては**既存のコンテンツ配信＋ポイント／バッジ付与の枠組みを再利用できる**（`Tip`／pushパイプライン／`givePointBadgeForUser`）ため、一から書き直す必要はない。 |

---

## 出典

| 内容 | 根拠 |
|---|---|
| Tip配信のパイプライン（3段階） | `syp-eminelstandard-backend-main/src/functions/batch-send-tip-preprocessing/app.ts`, `batch-send-tip/app.ts`, `batch-send-tip-complete/app.ts` |
| 静的な属性による配信対象の絞り込み | `syp-eminelstandard-backend-main/src/layers/common/nodejs/business-logic/check-user-matches-condition-attribute.ts` |
| Tip閲覧時のポイント／バッジ付与 | `syp-eminelstandard-backend-main/src/functions/api-user/give-point-badge.ts`, `src/layers/common/nodejs/variables/constants.ts:1340-1358`（`POINT_BADGE_FOR`） |
| 未使用の「CO2削減」定数 | `syp-eminelstandard-backend-main/src/layers/common/nodejs/variables/constants.ts:1306-1311`（`POINT_ACTION.CO2_REDUCTION`）― リポジトリ全体をgrepしても他に参照している箇所は見つからない |
| センサー値に基づく熱中症／見守り警報のパイプライン | `syp-eminelstandard-backend-main/src/functions/batch-receive-data-infrared-remote/app.ts:200-225`, `src/functions/batch-control-device-and-push-notice-sensor/app.ts:64-97` |
| E-GW側の対応する要件 | `eminel_gw_project-main/docs/eminel/3_requirements/00_integrated_requirements_v1.2.md` ― `[F-ES-03] 省エネアドバイス` |
