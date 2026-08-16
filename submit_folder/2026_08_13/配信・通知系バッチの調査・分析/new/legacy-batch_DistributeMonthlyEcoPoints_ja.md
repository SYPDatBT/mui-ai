# 旧バッチ ― DistributeMonthlyEcoPointsCommand（エコ暖房ポイント付与）

## 概要

`DistributeMonthlyEcoPointsCommand` は、旧システム（EMINEL コンシェルジュサーバー）において**月1回**（cron `00 17 1 * *` ― 毎月1日17:00）実行されるバッチであり、**前月の暖房設定温度の平均が22.0°C以下**の顧客に対して**固定250ポイント**を付与する（データは別の月次集計バッチが事前に算出済みであり、ここではそれを読み取る）。cronは**通年**で実行するよう登録されており、コード上も季節による制限はない ― A03の記述「12〜3月」とは食い違っている（`A03_point.md:119`。A03自身も「eGWの値は要確認」と記している）― Kitagasへの確認が必要である。ポイントは会計年度（4月→3月）単位で内部のポイント台帳（`s_141`）の2レコードへ書き込まれ、あわせて外部API **Point Infinity** を呼び出して顧客に実際のポイントを付与する。`con_point_link_logs` ログテーブルによる月単位の重複付与防止の仕組みがある。顧客ごとの処理はすべて個別のトランザクションの中にあり ― 1顧客のエラーがバッチ全体を停止させることはない；詳細は第2部に示す。

## 第1部 ― 概要

| 項目 | 内容 |
|---|---|
| **役割** | 毎月、前月の暖房設定温度の平均が22.0°C以下の顧客を対象とし、エコ暖房ポイント250ポイントを付与する（内部＋Point Infinity）。 |
| **入力** | `ConSensorMonthlyValues`（`s_104` ― 月別の平均値、`device_type=17`＝設定温度）＋ `ConCustomers`（`t_101` ― 顧客番号、削除フラグ）＋ `ConPointLinkLogs`（月単位の重複防止ログ）。 |
| **出力** | `ConEcoPoints`（`s_141`、顧客1件につき2レコード：合計＋温度別）へのポイントの書き込み／加算 ＋ `ConPointLinkLogs` へのinsert ＋ API `PointInfinity::givePoints()` の呼び出し。 |
| **処理概要** | 1. 対象月＝実行日の前月と、対応する会計年度を決定する。<br>2. その月の暖房設定温度の平均が22.0°C以下であり、かつ当月分のポイントがまだ付与されていない顧客を絞り込む。<br>3. 顧客ごとに：ポイント台帳2レコードへ250ポイントを加算し、ログを書き込み、Point Infinityを呼び出す ― すべて顧客1件につき1トランザクションの中で行う。<br>4. 成功／失敗の合計件数をログ出力する。 |

## 第2部 ― 詳細

### 処理の全体図

```
ステップ1  基準の決定         → 実行日の前月、対応する会計年度              §2.1
ステップ2  顧客の絞り込み     → その月の暖房設定温度の平均 ≤ 22.0°C、
                                当月分の付与ログがまだ存在しない            §2.2
ステップ3  台帳の取得／作成   → ConEcoPoints 2レコード（合計、温度別）
                                キー (ems_sp, 会計年度) ごと                §2.3
ステップ4  ポイント加算       → 2レコードとも月カラム＋合計カラムに +250    §2.3
ステップ5  ログ書き込み＆PI付与 → ConPointLinkLogs をinsert、PointInfinity 呼び出し  §2.4
           （ステップ3〜5全体が顧客ごとの個別トランザクション内）
```

| ステップ | 内容 | 詳細箇所 |
|---|---|---|
| 1 | 対象月と会計年度の決定 | §2.1 |
| 2 | 付与対象となる顧客の絞り込み条件 | §2.2 |
| 3–4 | ポイント台帳 `ConEcoPoints` の構造とポイントの加算方法 | §2.3 |
| 5 | 重複防止ログの書き込み、Point Infinityの呼び出し | §2.4 |
| — | Point Infinityへ送信するリクエストの内容 | §2.5 |

---

### 2.1 基準時点と会計年度の決定

| 項目 | 内容 |
|---|---|
| デフォルトの基準時点 | バッチ実行時点の現在日時 |
| 再実行用パラメータ | `--datetime` ― **効果がない**（⚠️①参照） |
| 対象となる月 | `targetDateTime = 現在 − 1か月`（[:79](sources/conciergesv-develop/src/Command/DistributeMonthlyEcoPointsCommand.php#L79)） |
| 会計年度 | `targetDateTime.month >= 4` → その年を採用する；そうでなければ前年を採用する（日本の会計年度：4月 → 3月）（[:109](sources/conciergesv-develop/src/Command/DistributeMonthlyEcoPointsCommand.php#L109)） |
| 重複防止キー | `pointLinkReason = 'monthly_eco_points_' . targetDateTime→'Ym'` ― 対象月に応じて固定され、1回の実行の間は変化しない（[:80](sources/conciergesv-develop/src/Command/DistributeMonthlyEcoPointsCommand.php#L80)） |

### 2.2 ポイント付与対象となる顧客の絞り込み条件

`ConCustomers` に対する単一のクエリであり、`matching`／`notMatching` の2条件をjoinしている（[:83-104](sources/conciergesv-develop/src/Command/DistributeMonthlyEcoPointsCommand.php#L83-L104)）：

| 条件 | 意味 |
|---|---|
| `matching ConSensorMonthlyValues`：`device_type = 17`（`ROOM_TEMP_SETTING`、[const.php:202](sources/conciergesv-develop/config/const.php#L202)）、`room_id = 0`、対象月のカラムが `<= 22.0` | **前月**の暖房設定温度の平均（メインセンサー）が22.0°C以下 |
| `notMatching ConPointLinkLogs`：`reason = pointLinkReason` | 当該月分のポイントがまだ付与されていない（重複防止） |
| `customer_number IS NOT NULL` | 顧客番号がなければPoint Infinityへ送信できない |
| `deleted IS NULL`（`c052`） | 論理削除されていない顧客 |

比較に用いる月カラムは `ConSensorMonthlyValue::getColumnNameOfMonth(targetDateTime.month)` により取得する ― この関数は**暦月にそのまま対応**してマッピングし（`c011`＝1月 … `c022`＝12月）、会計年度によるずれはない（[ConSensorMonthlyValue.php:63-66](sources/eminel_sv_lib-develop/src/Model/Entity/ConSensorMonthlyValue.php#L63-L66)）。

### 2.3 ポイント台帳 `ConEcoPoints`（`s_141` テーブル）とポイントの加算方法

条件を満たす顧客ごとに、キー `(ems_sp, point_kind, 会計年度)` により**2レコード**を取得（または新規作成）する（[:117-141](sources/conciergesv-develop/src/Command/DistributeMonthlyEcoPointsCommand.php#L117-L141)）：

| `point_kind` | 定数 | 意味 |
|---|---|---|
| `0` | `POINT_KIND_TOTAL` | エコ暖房ポイントの合計（ここで併せて加算される） |
| `1` | `POINT_KIND_TEMP` | 温度基準による個別のポイント（本バッチ分） |
| `2` | `POINT_KIND_ACTION` | その他の行動によるポイント ― 本バッチでは**使用しない** |

2レコードとも、月カラムと合計カラムに `+250` が加算される（[:142-147](sources/conciergesv-develop/src/Command/DistributeMonthlyEcoPointsCommand.php#L142-L147)）：

```php
$totalEcoPointRecord->addPointsToMonth($now->month, self::BENEFIT_POINTS);  // dùng $now, KHÔNG dùng $targetDateTime
$totalEcoPointRecord->addPointsToTotal(self::BENEFIT_POINTS);
```

月カラムは `ConEcoPoint::getColumnNameByMonth()` によって算出される ― この関数は**会計年度における月の順序**に従ってマッピングし（4月＝年度の最初の月）、§2.2の `ConSensorMonthlyValue` の暦月によるマッピングとは異なる（[ConEcoPoint.php:81-87](sources/eminel_sv_lib-develop/src/Model/Entity/ConEcoPoint.php#L81-L87)）― カラムずれの不具合の原因であるため、⚠️②を参照。

### 2.4 重複防止ログの書き込みとPoint Infinity連携

すべて**顧客ごとの個別の1トランザクション**の中で行われる（[:158-185](sources/conciergesv-develop/src/Command/DistributeMonthlyEcoPointsCommand.php#L158-L185)）：

1. `ConEcoPoints` の2レコード（合計、温度）を `saveOrFail` する。
2. `ConPointLinkLogs` のレコード（`reason`, `ems_sp`, `links_cus_num`, `status='OK'`, `points=250`）を `saveOrFail` する。
3. `PointInfinity::readHostConfig()` に設定がある場合 → 取引番号 `txNo = 直前に保存したログレコードのid − lastPointLogMaxId` を算出し（[:173](sources/conciergesv-develop/src/Command/DistributeMonthlyEcoPointsCommand.php#L173)）、`sendToPointInfinity()` を呼び出す。
4. いずれかのステップでエラーが発生した場合（Point Infinityがエラーを返した場合を含む）→ **その顧客**のトランザクション全体をrollbackし、`failureCount++` として、バッチは次の顧客へ進む ― バッチ全体は停止しない（[:181-185](sources/conciergesv-develop/src/Command/DistributeMonthlyEcoPointsCommand.php#L181-L185)）。

`$lastPointLogMaxId`（＝**本日より前**に作成された `ConPointLinkLogs` の最大ID）はloopに入る前に**1回だけ**取得され（[:106](sources/conciergesv-develop/src/Command/DistributeMonthlyEcoPointsCommand.php#L106)）、その実行内の全顧客で共用される ― `txNo` を `ConPointLinkLogsTable::calcPointInfinityTransactionNumber()` の設計どおり当日内で一意な連番（1, 2, 3, …）とするためである（[ConPointLinkLogsTable.php:106-120](sources/eminel_sv_lib-develop/src/Model/Table/ConPointLinkLogsTable.php#L106-L120)）― ⚠️③参照。

### 2.5 Point Infinityへ送信するリクエストの内容

`sendToPointInfinity()` は、多数の固定フィールド（通貨コード、`kmt*Id` の各区分コード、`termNo='eminel'`）と取引ごとのフィールドを持つ `GivePointsRequest` リクエストを1つ組み立てる（[:203-228](sources/conciergesv-develop/src/Command/DistributeMonthlyEcoPointsCommand.php#L203-L228)）：

| フィールド | 値 | 意味 |
|---|---|---|
| `kaiinNo` | 顧客番号 | Point Infinity側の顧客識別子 |
| `denpyoNo` | `txNo` を6桁にパディングしたもの | 当日内で一意な取引番号 |
| `fuyoPt` | `250` | 付与ポイント数 |
| `fuyoRiyu` | `"<年>年<月> EMINEL エコ暖房ポイント"`（`targetDateTime`、すなわち対象月に基づく） | 表示される付与理由 |
| `jiyuCd` / `jiyuDetCd` | `'01'` / `'1081'` | Point Infinity側における固定の付与理由コード（「エコ暖房ポイント」の区分） |

レスポンスがOKでない場合 → `EminelLogComponent` によりエラーログを出力し、§2.4のトランザクションをrollbackさせるためexceptionをthrowする（[:224-227](sources/conciergesv-develop/src/Command/DistributeMonthlyEcoPointsCommand.php#L224-L227)）。

---

### ⚠️ 旧システムの異常点

**① `--datetime` オプションが効果を持たない。**（[:73-76](sources/conciergesv-develop/src/Command/DistributeMonthlyEcoPointsCommand.php#L73-L76)）

```php
$now = FrozenTime::now();
if ($args->hasOption('datetime')) {
    $now = FrozenTime::parse($now);   // parse lại chính $now, không lấy giá trị option
}
```

本来は `FrozenTime::parse($args->getOption('datetime'))` であるべきである。現状では `--datetime=...` を渡しても算出日を変更できない ― バッチは常に実システム時刻に従って動作し、指定した1か月分の再実行／backfillはできない。

**② 実際に評価された月とは別の月カラムにポイントが書き込まれる。** 絞り込み条件（§2.2）とレコードの会計年度（§2.3）はいずれも `targetDateTime`（前月）に基づいているが、月カラムへポイントを加算する際には `$now->month`（バッチ実行時点の当月、[:142, :145](sources/conciergesv-develop/src/Command/DistributeMonthlyEcoPointsCommand.php#L142-L145)）を使用している：

```php
$totalEcoPointRecord->addPointsToMonth($now->month, self::BENEFIT_POINTS);
```

`targetDateTime = now − 1か月` はどの実行回においても常に成り立つため、ポイントは実際にしきい値に達した温度の月に対して常に**1つ次の月カラム**へ書き込まれる。ちょうど会計年度の境界（4月に実行した場合）では、この不具合はさらに深刻になる：レコードは3月（`targetDateTime`）の会計年度で取得／作成されるが、ポイントを書き込むカラムは「4月」のカラムであり ― `ConEcoPoint::getColumnNameByMonth()` の月順マッピングに従うと、**その同じ会計年度レコードの先頭**にあたる（「翌年の4月」ではない）。

**③ 既存の関数を使わず、Point Infinityの取引番号を独自に再計算している。** `ConPointLinkLogsTable` にはまさにこの処理を行う `calcPointInfinityTransactionNumber()` が既にあるが、commandは同じロジックを手作業で繰り返している（`$pointLinkLog->id - $lastPointLogMaxId`）― 誤りではないもののコードが重複しており、本来の定義箇所から切り離されている。

---

## 出典

| 内容 | 根拠 |
|---|---|
| バッチのメインロジック | `sources/conciergesv-develop/src/Command/DistributeMonthlyEcoPointsCommand.php` |
| 定数 `ROOM_TEMP_SETTING` | `sources/conciergesv-develop/config/const.php:202` |
| `ConSensorMonthlyValues` のテーブル＋カラム定数 | `sources/eminel_sv_lib-develop/src/Model/Entity/ConSensorMonthlyValue.php` |
| `ConEcoPoints` のテーブル（`s_141`）＋カラム定数 | `sources/eminel_sv_lib-develop/src/Model/Table/ConEcoPointsTable.php`, `src/Model/Entity/ConEcoPoint.php` |
| `ConPointLinkLogs` のテーブル＋Point Infinityの取引番号を算出する関数 | `sources/eminel_sv_lib-develop/src/Model/Table/ConPointLinkLogsTable.php` |
| cronスケジュール（毎月1日17:00）＋季節の対照 | `docs/02_詳細設計/10_バッチ処理/mng-webap_cron設定_20241029.txt:114` ・ `eminel_gw_project/docs/eminel/3_requirements/app/A03_point.md:119` |
