# 旧バッチ ― CalcMonthlyRoomTemperatureCommand（月毎室温データ算出）

## 概要

`CalcMonthlyRoomTemperatureCommand`は、旧システム（EMINEL コンシェルジュサーバー）内で1日1回実行されるバッチであり、1日分の**24個の時間別平均室温**（`s_102`テーブルに既に格納済み。別バッチが算出）を、世帯×センサー位置（E0/E1）ごとに**1つの日次平均値**へ集約し、月次テーブル`s_103`（1行につき31カラム＝月内の日ごとに1カラム）へ書き込む。算出対象日に加えて、バッチは当月・前月分の時間データ全体を再スキャンし、範囲内のデータが存在する全ての日を**再計算**する（変更された日のみを絞り込むフィルタは無い。かつて存在したc009=1の条件はコード上コメントアウト済み）。これにより遅延到着・修正されたデータも反映され、そのうえでソースである`s_102`を「集計済み」として再度マークする。バッチはDBの読み書きのみを行う（メール送信・ファイル出力は行わない）。実行スケジュール、SQL文、計算式、業務定数の詳細は第2部に記載する。

## 第1部 ― 全体概要

| 項目 | 内容 |
|---|---|
| **役割** | 温度データは**時間単位**（1日24値、`s_102`に格納）でしか存在しない。**月単位**の温度履歴（月内の日ごとの照会・表示に利用）を持つには、1日分の24時間値を**1つの日次平均値**に集約し、世帯×センサー位置ごとに月次形式（31日カラム）の1行として保存する必要がある。元となる時間データは、その日が算出済みになった後でも遅延到着したり修正されたりする可能性があるため、バッチは過去の日（当月＋前月の範囲）についても**再計算**を行い、月次テーブルが常に最新の時間データと一致するようにしている。 |
| **入力** | DBの読み込みのみ、**外部API呼び出し・CSVファイル読み込みなし**：`t_101`（世帯一覧）＋ `s_102`（時間別結果テーブル、エンティティ`ConSensorHourlyValue`――1行は1世帯×1センサー位置×1日、時間別24カラム`c011`〜`c034`、時間集計バッチが事前に書き込み済み）。 |
| **出力** | **DBへの書き込みのみ**――`s_103`（エンティティ`ConSensorDailyValue`、共通ライブラリ`EminelSvLib`経由）へ書き込み・上書きする――1行は1世帯×1センサー位置×1ヶ月、31日カラム（`c011`〜`c041`）；同時に`s_102`側の`need_agg_complete_flag`フラグを更新し、集計済みの日をマークする。メール送信・CSV出力は行わない。 |
| **処理概要** | 1. 算出対象日を決定する（パラメータ`--date`、または昨日）。パラメータ指定時はフォーマットを検証し、不正な場合はabortする。<br>2. `s_102`から、世帯×センサー位置ごとに、その日の24時間分の温度合計とデータが存在する時間数を取得する。<br>3. 日次平均＝合計÷有効時間数を算出し、`s_103`の月次行の該当日カラムへ書き込む。<br>4. 前月＋当月分（算出対象日そのものを除く）の時間データを再取得し、過去の日を再計算する。<br>5. 再計算した平均値を`s_103`へ上書きし、ソースの`s_102`を集計済みとしてマークする；これら全体は1つのトランザクション内で行われる。 |

## 第2部 ― 詳細

### 2.1 実行スケジュールと算出時点

| 項目 | 内容 | 出典 |
|---|---|---|
| 実行スケジュール（cron） | `10 3 * * *` ― 1日1回、午前3時10分 | `docs/02_詳細設計/10_バッチ処理/mng-webap_cron設定_20241029.txt:24-25` (`#8.月毎室温データ算出` → `8_CalcMonthlyRoomTemperature.sh`) |
| 実行コマンド | `php cake.php CalcMonthlyRoomTemperature [--date="算出日"]` | `CalcMonthlyRoomTemperatureCommand.php:45` |
| **calculationDate**の基準（パラメータ未指定時） | `今日 − 1日` | `CalcMonthlyRoomTemperatureCommand.php:64-66` |
| `--date`パラメータ指定時 | 正規表現`^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])$`で`yyyy-MM-dd`形式を検証する；フォーマット不正の場合はALERTログを出力し`abort()`する | `CalcMonthlyRoomTemperatureCommand.php:68-76,438-449` |
| 主たる算出日 | `calculationDate`（1日単位であり、時間帯ではない） | `CalcMonthlyRoomTemperatureCommand.php:376` |

### 2.2 算出対象日の時間データ取得（`getSensorHourlyValue`）

```sql
SELECT ConSensorHourlyValues.c001, ConSensorHourlyValues.c002, ConSensorHourlyValues.c003
     , ConCustomers.c012 AS c111, ConCustomers.c042 AS c112
     , ConCustomers.c015 AS c113, ConCustomers.c016 AS c114, ConCustomers.c024 AS c115
     , COALESCE(c011,0)+COALESCE(c012,0)+ ... +COALESCE(c034,0) AS total        -- 24時間分の合計、NULLは0として計算
     , (CASE WHEN c011 IS NULL THEN 0 ELSE 1 END)+ ... +(CASE WHEN c034 IS NULL THEN 0 ELSE 1 END) AS totalNumber  -- データが存在する時間数
  FROM t_101 ConCustomers, s_102 ConSensorHourlyValues
 WHERE ConCustomers.c001 = ConSensorHourlyValues.c001
   AND ConSensorHourlyValues.c002 = 6                    -- device_type = ROOM_TEMPERATURE
   AND ConSensorHourlyValues.c004 = :targetDate          -- 算出対象日そのもの（yyyy/MM/dd）
   AND ConCustomers.c052 IS NULL                          -- 論理削除されていない世帯
 ORDER BY ConSensorHourlyValues.c001
```
出典：`CalcMonthlyRoomTemperatureCommand.php:371-430`（24時間カラムを合計するSQL文字列の組み立ては379-395行目、SQL文自体は397-414行目）。

**SQL文で使用しているカラムの意味：**

| テーブル | カラム | 意味 |
|---|---|---|
| `t_101` | `c001` | 世帯コード（EMS-SP）――結合キー |
| `t_101` | `c012`,`c042`,`c015`,`c016`,`c024` | 世帯グループの5属性（住宅構造、暖房能力、床面積、居住人数、ガスコージェネレーション有無）――そのまま`s_103`の`c111`〜`c115`としてコピーされる |
| `t_101` | `c052` | 論理削除日時――`IS NULL`＝世帯が有効 |
| `s_102` | `c001` | 世帯コード――結合キー |
| `s_102` | `c002` | デバイス種別――`= 6`で絞り込み |
| `s_102` | `c003` | センサー位置（0 = E0、1 = E1）――1世帯につき最大2行、1位置につき1行 |
| `s_102` | `c004` | 日付――算出対象日そのもので絞り込み |
| `s_102` | `c011`〜`c034` | 時間別平均温度24値（0時〜23時）、NULLの可能性あり |

**業務定数**：`ROOM_TEMPERATURE = 6`（`sources/conciergesv-develop/config/const.php:184`）――SQL文では定数名を使わず、数値`6`を直接指定している。

### 2.3 日次平均の算出と結果の書き込み ― 書き込み先`s_103`（`updateSensorMonthlyValue`）

```
各結果行（1世帯×1センサー位置）について：
① total = 0 または totalnumber = 0 の場合 → スキップし、書き込まない（コードは両方が0以外の場合のみ書き込む。データが存在しても合計がちょうど0の日はスキップされる点に注意）
② それ以外の場合 → 日次平均 = total / totalnumber
③ s_103へ書き込む：
   - キー：ems_sp、device_type（= 6、s_102の行から取得）、room_id（0/1、s_102の行から取得）、
     date = calculationDateが属する月の1日（yyyy/MM/01）
   - 該当する日カラム：c0(calculationDateの日 + 10) = 日次平均
     （例：calculationDate = 5日 → カラムc015；31日 → カラムc041）
   - group_attr1〜5 = t_101から取得した5つのグループ属性（2.2参照）
   - need_agg_complete_flag = 1
   - modified = 現在時刻
④ ある世帯の書き込みでエラー（例外）が発生した場合 → ALERTログを出力し、resultCode = false とするが、ループは停止せず――残りの世帯の書き込みを継続する
```
出典：`CalcMonthlyRoomTemperatureCommand.php:315-363`。

### 2.4 前月＋当月分の時間データの再計算

#### 2.4.1 再計算対象データの取得（`getRecalculationData`）

```sql
-- SQL構造は2.2と同様だが、SELECT句にConSensorHourlyValues.c004（対象日）が追加され、日付の絞り込み条件が異なる:
...
   AND ConSensorHourlyValues.c004 > :startDate            -- （calculationDateの月 − 1ヶ月）の1日。この日自体は含まない
   AND ConSensorHourlyValues.c004 < :targetDate            -- calculationDateの日。この日自体は含まない
...
```
- `targetDate` ＝ `calculationDate`の日付（yyyy/MM/dd）。
- `startDate` ＝（`calculationDate`の月 − 1ヶ月）の1日（yyyy/MM/dd）；`calculationDate`が1月の場合、月の引き算により自動的に前年12月に戻る。
- データ取得範囲：前月2日から`calculationDate`の前日まで――すなわちちょうど「当月＋前月」であり、コード内の元コメントによれば、月次データは2ヶ月分（当月＋前月）のみ保持されるためである。
- 上記範囲内の（世帯×センサー位置×日）ごとに1行、複数行を返す。構造は2.2と同様の`total`／`totalnumber`を持つ。

出典：`CalcMonthlyRoomTemperatureCommand.php:234-306`（データ保持に関するコメントは241行目、SQL文は264-286行目）。

#### 2.4.2 再計算結果を`s_103`へ書き込み（`updateRecalculationData`）

```
各結果行（1世帯×1センサー位置×再計算対象範囲内の1日）について：
① total = 0 または totalnumber = 0 の場合 → スキップし、書き込まない（コードは両方が0以外の場合のみ書き込む。データが存在しても合計がちょうど0の日はスキップされる点に注意）
② それ以外の場合 → 日次平均 = total / totalnumber
③ s_103へ書き込む（2.3と同じキー／カラム構成だが、以下が異なる）：
   - date = データ行が属する「対象日を含む月」の1日（calculationDateの月ではない）
   - 該当する日カラム = c0(データ行の日 + 10)
   - need_agg_complete_flag = 1 とするのは、対象日の月がcalculationDateの月と一致する場合のみ；
     前月の場合はこのフィールドをセットしない
④ ある世帯の書き込みでエラー（例外）が発生した場合 → CRITICALログを出力し、resultCode = false とし、ループを即座に停止する（break）
```
出典：`CalcMonthlyRoomTemperatureCommand.php:121-183`。

#### 2.4.3 ソース`s_102`を集計済みとしてマーク（`updateSourceData`）

```
2.4.2のステップが成功した場合のみ実行する。2.4.2で書き込まれた各行（total != 0 かつ totalnumber != 0）について：
① s_102（ConSensorHourlyValue。s_103ではない）へ書き込む：
   - キー：ems_sp、device_type、room_id、date = データ行の正確な日付（yyyy/MM/dd）
   - need_agg_complete_flag = 2
   - modified = 現在時刻
② ある世帯の書き込みでエラー（例外）が発生した場合 → ALERTログを出力し、resultCode = false とするが、ループは停止せず――残りの世帯の処理を継続する
```
出典：`CalcMonthlyRoomTemperatureCommand.php:191-226`。

### 2.5 トランザクション

```
1. getSensorHourlyValue（2.2）――SQLエラーの場合 → 直ちにreturnし、トランザクションを開かず、以降のステップも実行しない
2. トランザクションを開始する
3. updateSensorMonthlyValue（2.3）――エラーの場合 → rollbackして停止
4. getRecalculationData（2.4.1）――エラーの場合 → rollbackして停止
5. updateRecalculationData（2.4.2）、続いてupdateSourceData（2.4.3）――いずれかでエラーが発生した場合 → rollbackして停止
6. 上記5ステップすべてが成功した場合 → commit
```
出典：`CalcMonthlyRoomTemperatureCommand.php:57-112`。

本バッチは**自身では通知を送信せず、年間値の算出も行わない**――これらは後続で`s_103`を読み込む別のバッチが担当する処理であり（本コマンドの対象範囲外である）。
