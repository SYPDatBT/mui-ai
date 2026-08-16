# RankingCreationCommand（ランキング作成）

## 概要

`RankingCreationCommand` は `conciergesv` 上で**月1回**（1日、`CalcCarbonDioxideEmissionsCommand` の直後）実行されるバッチであり、顧客ごとの**CO2排出量のパーセンタイル**（総合／ガス／電気の3種類）を、**世帯属性5項目が同じグループ**（`CreateGroupSummaryCommand` で調査したグループと同一。`CreateGroupSummary.md` 参照）の他の顧客と比較して算出する ― グループが小さすぎる場合（9人以下）は、パーセンタイルが統計的に意味を持つよう、より広いグループ（2属性）へフォールバックする。結果は `ConRankings`（月ごとのパーセンタイル＋前月と比較した改善／悪化／変化なしのトレンドフラグ）に保存され、アプリは `GetRankingInfoController` 経由で読み直して「あなたと似た住宅のグループの中で、排出量が少ない上位X%に入っています」と表示する。新しいリポジトリ `syp-eminelstandard-backend` には、**同等の仕組みは存在せず、本質がまったく異なる**：新システムにも「ranking」という名前の機能が1つある（`get-ranking-by-total-badge.ts`）が、実態は**絶対的なポイント閾値によるtier/levelの仕組み**（ゲームのXPレベルに相当するゲーミフィケーション）であり、そのユーザー自身のポイントのみを読み取って固定の閾値テーブル（regular/bronze/silver/gold/platinum/diamond）と照合するだけで、**他のいかなるユーザーとも一切比較しない**。グループ化もなく、パーセンタイルもなく、CO2／エネルギーとも無関係である。世帯属性5項目によるグループ化の仕組み（旧バッチの基盤）も存在しない ― `CreateGroupSummary.md` で確認済み。「類似住宅グループとのCO2排出量比較」機能は、移植されていないと思われる。

---

# 第A部 ― 旧システム

## A.1 総括

| 項目 | 内容 |
|---|---|
| **バッチ名** | Class: `RankingCreationCommand`（`BaseCommand` を継承）· cronスクリプト内の実際の呼び出し：`RankingCreation`（PascalCase、他のCommandの規約どおり）；docblockのみ `rankingCreation`（lowerCamelCase）と記載 ― このファイル自身のドキュメント記述上の軽微なずれ · cronスクリプト：`20_RankingCreation.sh` · cron内の日本語名称：「20.ランキング作成」。 |
| **役割** | 類似世帯グループ内における顧客ごとのCO2排出量パーセンタイルの算出＋前月比のトレンド追跡。アプリに表示されるランキング機能のためのデータを提供する。 |
| **入力** | `t_101`（顧客）、`s_104`（月ごとのCO2値、`device_type=18/19/20`）、`s_151`（月ごとの顧客グループ）、`s_114`（月ごとのグループのpopulation）、`s_121` 自身（トレンド算出のため前月のrankingを読み直す）を読み取る。パラメータ `--rankingtype`（**必須**、デフォルトなし ― A.2.4参照）、`--yearmonth`（任意、デフォルトは前月）。 |
| **出力** | `ConRankings`（`s_121`）テーブルへの `INSERT`／`UPDATE` ― 顧客×年×ランキング種別ごとに1行、月ごとのカラム（パーセンタイル）＋月ごとのカラム（トレンド状態）。 |
| **処理概要** | 1. パラメータ（ランキング種別、算出対象の年月）のバリデーションとparse。<br>2. ランキング種別ごと（パラメータに応じて1～3種類）に、その月の有効な全顧客のCO2パーセンタイルを算出し（グループ単位、グループが小さい場合は広いグループへフォールバック）、前月と比較してトレンドを算出する。<br>3. 結果の書き込み：その年・その種別の `ConRankings` 行がすでにある顧客 → 該当月のカラムをUPDATE；ない場合 → まとめて一括INSERT。<br>4. 全体を1つのトランザクションで行う（途中でエラーが発生した場合の例外あり。A.2.4参照）。 |

## A.2 詳細

**算出方法のマップ ― 2段階のグループ分け＋パーセンタイルの計算式：**

```
顧客ごと、ランキング種別ごと（1 CO2総合 / 2 CO2ガス / 3 CO2電気）：

  顧客の5属性グループ（s_151 より、ランキング対象月ちょうどのスナップショット）
                    │
                    ▼
       5属性グループのpopulation（s_114、対象月のカラム）> 9人？
                    │
        ┌───────────┴────────────┐
       YES                      NO（9人以下、グループが小さすぎる）
        │                         │
        ▼                         ▼
  CO2順に RANK() ASC        CO2順に RANK() ASC
  5属性グループ内            より広いグループ内（建物種別＋暖房熱源のみ、残り3属性は除外）
  分母 = その5属性           分母 = この2属性が同じ5属性グループのpopulationのSUM
  グループのpopulation            │
        └───────────┬────────────┘
                     ▼
    percentile = GREATEST(trunc((rank − 1) / 分母 × 100), 1)   ← 1-100の整数、決して0にならない
                     │
                     ▼
    今月のpercentileを、同じランキング種別の前月分（s_121 に保存）のpercentileと比較
                     │
      ┌──────────────┼──────────────────┬───────────────────────┐
      ▼              ▼                  ▼                       ▼
  前月のデータが   前月percentile      前月percentile >        前月percentile <
  存在しない       == 今月percentile   今月percentile（低下）   今月percentile（上昇）
  rank_status=2    rank_status=2       rank_status=0（改善）    rank_status=1（悪化）
```

| ステップ | 詳細項目 |
|---|---|
| パラメータのバリデーション＋算出対象月の決定 | §A.2.1 |
| rank＋percentileを算出するSQL（2段階のグループ） | §A.2.2 |
| 月カラムと既知のカラムずれ不具合（`c022`↔`c023`） | §A.2.3 |
| 結果の書き込み ― `ConRankings` へのUPSERT | §A.2.4（書き込み部分） |

### A.2.1 パラメータと算出対象月の決定

| 項目 | 内容 | 出典 |
|---|---|---|
| 実行スケジュール（cron） | `10 7 1 * *` ― 月1回、1日の07:10（同日06:10に実行される `19_CalcCarbonDioxideEmissions.sh` の直後 ― 終了したばかりの月のCO2データが1時間前に算出される） | `docs/02_詳細設計/10_バッチ処理/mng-webap_cron設定_20241029.txt:65,68` |
| `--rankingtype` | **デフォルトなし** ― 必ず渡す必要がある。カンマ区切りで、各値は `1`（総合）／`2`（ガス）／`3`（電気）のいずれかでなければならず、不正な場合は直ちにabortする。`20_RankingCreation.sh`（`eminel-mng-webap.20240909.tgz` 内）から直接確認：cronは3種類すべてを `--rankingtype=1,2,3` として1回だけ呼び出し、`--yearmonth` は渡さない（→デフォルトの前月）。 | `RankingCreationCommand.php:69-82` |
| `--yearmonth` | 未指定→前月（cronが1日に実行されるため「前月」＝終了したばかりの月となり妥当）。指定する場合→形式は `yyyy-MM` で、年は[1900,9000]、月は[1,12]の範囲であること。 | `:85-113` |
| `lastYearMonth` の算出 | ランキング対象月の直前の月（前年同月ではない）― トレンドを算出するために前月の `ConRankings` を参照するのに用いる。 | `:122-128` |

### A.2.2 rank＋percentileを算出するSQL

```sql
WITH current_rank AS (
  SELECT cus.c001 AS ems_sp,
    GREATEST(trunc((
      ( CASE WHEN all_attr.{col} > 9   -- MEMBERS_NUM_OF_SUMMARY_GROUP
             THEN RANK() OVER (PARTITION BY hist.group1..group5 ORDER BY nen.{col} ASC)
             ELSE RANK() OVER (PARTITION BY hist.group1, hist.group2 ORDER BY nen.{col} ASC)
        END - 1
      ) / CASE WHEN all_attr.{col} > 9 THEN all_attr.{col} ELSE parts_attr.{col} END
    ) * 100), 1) AS rank
  FROM t_101 cus
  LEFT JOIN s_104 nen ON cus.c001 = nen.c001                    -- giá trị CO2 theo tháng
  LEFT JOIN (SELECT ... bucket hóa 5 thuộc tính từ s_151 ...) hist ON nen.c001 = hist.c001
  LEFT JOIN s_114 all_attr ON hist.group1..5 = all_attr.c111..115   -- population nhóm 5-thuộc-tính
  LEFT JOIN (SELECT SUM(...) FROM s_114 GROUP BY c111,c112) parts_attr ON hist.group1,2 = parts_attr.c111,c112  -- fallback
  WHERE cus.c001=nen.c001 AND nen.c002=:deviceType AND nen.c003=0 AND nen.c004=:year
    AND nen.{col} IS NOT NULL AND all_attr.c001=16 AND all_attr.c002=0 AND all_attr.c003=:year
    AND cus.c052 IS NULL
)
SELECT ranking.ems_sp, ranking.rank, cur_ranking.*,
  CASE WHEN prv_ranking.{lastCol} IS NULL THEN 2
       WHEN prv_ranking.{lastCol} = ranking.rank THEN 2
       WHEN prv_ranking.{lastCol} > ranking.rank THEN 0
       ELSE 1 END rank_status
FROM current_rank ranking
LEFT JOIN s_121 prv_ranking ON ...ems_sp AND c002=:lastYear AND c003=:rankingType
LEFT JOIN s_121 cur_ranking ON ...ems_sp AND c002=:year AND c003=:rankingType
```
出典：`RankingCreationCommand.php:182-265`（ロジックはそのままに簡略化）。

| テーブル | SQL内での役割 | 対照 |
|---|---|---|
| `t_101`（顧客） | 削除されていない顧客の一覧（`c052 IS NULL`） | `ConCustomer.php` |
| `s_104`（`nen`） | 対象月のCO2値、`device_type=18/19/20` ＝ 総合／ガス／電気 ― **`機器種別一覧.txt` には記載がない**（ドキュメントはコード17までしか列挙しておらず、コード18-20はコード `CalcCarbonDioxideEmissionsCommand.php:185-220` のコメント「機器種別18～20のCO2排出量」からのみ確認できる ― ドキュメントが古く、コードに追随して更新されていない可能性がある） | `CalcCarbonDioxideEmissionsCommand.php:185-220`；`getDeviceTypeFromRankingType()`（`:295-308`） |
| `s_151`（`hist`、サブクエリ経由） | ランキング対象月ちょうどにおける顧客の5属性グループ（現在のグループではなく履歴のスナップショット）― バケット化は `CreateGroupSummaryCommand::populationAggregation()` の**計算式とまったく同一** | `CreateGroupSummary.md` §A.2.2 |
| `s_114`（`all_attr`） | 5属性グループのpopulation、対象月のカラム、`device_type=16`（population ― `CreateGroupSummaryCommand` の月次分岐が書き出すテーブル・カラムと同一） | `CreateGroupSummary.md` §A.2.4 |
| `s_114`（`parts_attr`、フォールバック） | 先頭2属性（建物種別＋暖房熱源）が同じ5属性グループのpopulationの合計。5属性グループが9人以下の場合に使用する | `RankingCreationCommand.php:220-233` |
| `s_121`（`prv_ranking`/`cur_ranking`） | 前月のpercentileの参照（トレンドの算出）、および既存の `ConRankings` 行の確認（INSERTかUPDATEかの判定） | `ConRanking.php` |

**手計算の例** *(数値は仮の例示)* ― 5属性グループに15人の顧客がおり（population=15、>9のためフォールバックしない）、CO2の昇順に並べたときに顧客Xが3番目（rank=3、排出量が3番目に少ない ― 良好）の場合：
- `percentile = GREATEST(trunc(((3−1)/15)×100), 1) = GREATEST(trunc(13.33), 1) = GREATEST(13,1) = 13`
- グループ内で排出量が最も少ない顧客（rank=1）：`GREATEST(trunc((0/15)×100),1) = GREATEST(0,1) = 1` ― 0%と表示されることは決してなく、常に最低1%となる。
- グループ内で排出量が最も多い顧客（rank=15）：`GREATEST(trunc((14/15)×100),1) = 93` ― ちょうど100%に達することもない（計算式 `(N-1)/N` の数学的な限界。Nが大きいほど100に近づくが、決して等しくならない）。

### A.2.3 ⚠️ 旧システムの異常点 ― `ConRankings` テーブルにおける `c022`↔`c023` のカラムずれ

- 他のsensor-value系テーブル（`s_104`,`s_113`,`s_114`,...）における月カラムの標準的な規約は `c0(月+10)` ― 12月は `c022` となる。しかし `ConRankings`（`s_121`）テーブルは**`c022` を空けたまま12月に `c023` を使用している** ― entityの定数宣言から直接確認できる：`C_RANK_11='c021'` の次がいきなり `C_RANK_12='c023'` となっており（`ConRanking.php:57-58`）、entity全体を通して `c022` に対応する `C_RANK` は存在しない。
- コードは `getRankingData()` 内の率直なコメントによって、この不具合を自ら認識している：*「ランキング情報テーブルのランキング12月順位カラムがなぜかc023のため（本来、c022であるべき）、以降のカラム物理名の取得において、便宜的に13とする」*。（`:174-178`）
- このワークアラウンドは `$lastMonthColumn` の算出（トレンド比較のため `s_121` から前月のpercentileを参照する処理）にのみ適用される ― `$currentMonthColumn`（`s_104`／`s_114` の読み取りに使用）には**不要**である（これらsensor-value系テーブルにはこのカラムずれの不具合がなく、12月は通常どおり `c022` のままである）。結果の書き込み（`insertRanking()`）も影響を受けない。明示的なマッピング配列 `$rankColumnName[12] = ConRanking::C_RANK_12 = 'c023'`（すでに正しい）を用いており、`+10` の計算式で求めていないためである。（`:322-336`）
- 結論：これは以前から存在するスキーマ設計上の不具合であり（`ConRankings` テーブルを作成した際に誰かが `c022` を飛ばした／抜かした）、現在誤動作しているバグではない ― コードは手当てすべき箇所を正しく手当てしている。移植時に重要な点：**このカラムずれ不具合をそのまま複製すべきではない**（過去のマイグレーション／設計上の不具合による異常を残す理由はない）。新しいレイアウトが1～12月まで連続して一貫していることを担保すれば足りる。

### A.2.4 結果の書き込みと2つのステップ間のエラー処理の非対称性

- **`ems_sp`＋`year`＋`ranking_category` によるUPSERT**：その年・その種別の `ConRankings` 行がまだない顧客（`cur_rank_ems_sp` が空。SQL内の `cur_ranking` へのLEFT JOINで判定）→ 配列にまとめ、最後に1回で一括 `INSERT` する；行がすでにある場合 → 1行ずつ直ちに `UPDATE` する（まとめない）。（`:342-393`）
- 1回の書き込みでセットするのは処理対象月の2カラム（rank＋status）のみ ― 同じ行の他の月（前月までに行が作成済みの場合）はそのまま維持され、上書きされない。
- **⚠️ 複数の `--rankingtype` を同時に実行した場合（例：`1,2,3`）の、2つのステップ間におけるエラー処理の非対称性**：
  - データ取得ステップ（`getRankingData`）でN番目のランキング種別においてエラーが発生した場合 → `$connection->commit()`（同一実行内でそれ以前に処理を終えたランキング種別1..N-1の変更をすべて保持する）を行ってから `abort()` する。（`:135-140`）
  - データ書き込みステップ（`insertRanking`）でN番目のランキング種別においてエラーが発生した場合 → `$connection->rollback()`（同一実行内ですでに書き込みに成功したランキング種別1..N-1も含め、すべて破棄する）を行ってから `abort()` する。（`:144-149`）
  - 帰結：同じ「複数のランキング種別を処理する途中でのエラー」であっても、エラーがSELECTステップで発生したかINSERT/UPDATEステップで発生したかによって、最終的な結果がまったく異なる（実施済みの分を保持する vs すべて失う）― これが意図的なものかどうかを説明するコメントはない。移植時に留意すべき点：一貫した方針を1つ選ぶべきである（例：常に種別ごとに個別のトランザクションとする、または常に成功した分を保持する）。

---

# 第B部 ― EMINEL-smart（新システム）との対照

> 本質的に同等のLambda／仕組みは見つからなかった。以下の表は、調査した候補と、それが一致しない理由である（B.1/B.2に代えて掲載）― 「ranking」という名称は共通しているものの、両者はまったく別の機能である。

## 確認済み

| 領域／候補 | 一致しない理由 |
|---|---|
| `get-ranking-by-total-badge.ts:3-20` ＋ `RANKING_RANGE`（`variables/constants.ts:1724-1749`） | 誰かと比較したrank/percentileではなく、1人のユーザーの `totalBadge` に対して固定のポイント閾値（regular 0-9、bronze 10-19、…diamond 50+）を当てはめる `switch-case` にすぎない。`ORDER BY` も `PARTITION BY`／`GROUP BY` もなく、ユーザー間の比較も行わない ― 本質的にはゲーム的な「tier/level」（XPレベル）の仕組みであり、比較によるrankingではない。 |
| `api-user/get-ranking-of-user.ts:9-16`, `get-badge-status-for-user.ts:9-17` | 呼び出し元自身の `user_id` に対してDynamoDBの `GetItem` を読み取るだけのフローであることを確認 ― 他のユーザーをquery/scanすることは一切なく、世帯属性によるグループ化はなおさら行わない。 |
| `src/` 全体に対する `CO2`/`carbon`/`emission`/`percentile` のgrep | 結果は1件のみ：`CO2_REDUCTION: 'co2_reduction'`（point-badgeの1種類を示す識別名であり、実際のCO2計算は一切ない）。 |
| リポジトリ全体に対する `CalcCarbonDioxide`/`ConRanking` のgrep | コード内では0件。 |
| `template.yaml` 内の `ScheduleExpression` 全件 | スケジュールは3件のみで、いずれもdaily/hourly ― 月次のスケジュール（`cron(... 1 * ?)`）は存在せず、「毎月1日のみ実行する」というロジック（`dayOfMonth`）も `src/` 内にはない。 |
| `UserBadgeSummaryTable`/`PointBadgeStatsTable` | 累計のポイント／バッジを保存するのみ ― 12か月分のpercentileカラムも、`rank_status` のような増加／減少／変化なしのトレンドフラグもない。 |

---

## まとめ

該当なし ― 旧システムには算出パイプラインが1つしかなく（本質の異なる2つのアルゴリズムが並行しているわけではない。「5属性グループ vs 2属性フォールバック」は同一のパーセンタイル計算式の2つの分岐であって、同じ処理に対する2通りの計算方法ではない）、新システムには対照すべき**本質的に同等のものが見つからなかった** ― 新システムにある同名の「ranking」機能はまったく別の仕組み（絶対的なポイントによるtier判定であり、ユーザー間の比較は行わず、CO2とも無関係）であるため、同じ課題に対する「別の仕組みへの置き換え」とはみなさない ― 各候補が一致しない理由は、第B部の「調査済み」の表にすべて記載している。

---

## 出典

| 区分 | 内容 | 根拠 |
|---|---|---|
| 旧システム | メインロジック | `sources/conciergesv-develop/src/Command/RankingCreationCommand.php` |
| 旧システム | `ConRanking` のカラムの意味＋`c022` の欠番の確認 | `sources/eminel_sv_lib-develop/src/Model/Entity/ConRanking.php:44-71` |
| 旧システム | `device_type=18-20`（CO2）の出所。公式ドキュメントには記載がない | `sources/conciergesv-develop/src/Command/CalcCarbonDioxideEmissionsCommand.php:185-220`；対照 `docs/02_詳細設計/02_データ生成・アプリ通信(旧コンシェルジュ踏襲)/補足資料/機器種別一覧.txt`（コード17までしか列挙されていない） |
| 旧システム | 5属性グループとpopulation（ロジックを共用） | `CreateGroupSummary.md`（同一ディレクトリ） |
| 旧システム | 小規模グループの閾値定数 | `sources/conciergesv-develop/config/const.php:319` |
| 旧システム | `ConRankings` を読み直す箇所（consumer。表示目的であることの確認） | `sources/conciergesv-develop/src/Controller/GetRankingInfoController.php:164,214,317,384` |
| 旧システム | 実行スケジュール（cron） | `docs/02_詳細設計/10_バッチ処理/mng-webap_cron設定_20241029.txt:65,68` |
| 旧システム | バッチ一覧（日本語の説明、サーバのグループ） | `docs/03_API仕様/04_バッチ一覧.md:81` |
| 新システム | 名称は同じだが本質の異なる「ranking」の仕組み（絶対的なポイントによるtier） | `src/layers/common/nodejs/business-logic/get-ranking-by-total-badge.ts:3-20`, `src/layers/common/nodejs/variables/constants.ts:1724-1749`（`RANKING_RANGE`） |
| 新システム | rankingを読み取るAPI（呼び出したユーザー自身のデータのみを読むことの確認） | `src/functions/api-user/get-ranking-of-user.ts:9-16`, `src/layers/common/nodejs/business-logic/get-badge-status-for-user.ts:9-17` |
| 新システム | point/badgeテーブル（percentile／トレンドがないことの確認） | `UserBadgeSummaryTable`, `PointBadgeStatsTable`（`template-dynamodb.yaml`、`DeleteData.md` で調査済み） |
| 新システム | 月次スケジュールが存在しないことの対照 | `template.yaml`（`ScheduleExpression` 全件） |
