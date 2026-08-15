# 旧バッチ ― CalcDailyRoomTemperatureCommand（日毎室温データ算出）

## 要約

`CalcDailyRoomTemperatureCommand` は、旧システム（EMINEL コンシェルジュサーバー）において毎時実行されるバッチであり、10分毎の生データ（1時間あたり最大6件）をもとに、各世帯について**直近1時間の平均室温**を、**センサー設置位置2箇所**（E0／E1）ごとに分けて算出する。本バッチはDBの読み書きのみを行い（メール送信・ファイル出力は行わない）、現在時刻分の結果を`s_102`テーブルへ書き込むとともに、過去の時間帯でデータが欠落している箇所を補う**backfill（遡及補完）**（最大7日分）も併せて実行する。実行スケジュール、SQL文、計算式、業務定数の詳細は「2. 詳細」に記載する。

## 1. 概要

| 項目 | 内容 |
|---|---|
| **役割** | 10分毎の生の温度データから、**1時間分の平均室温**を、世帯ごとに**2つのセンサー位置**（E0／E1）に分けて算出する。あわせて、過去の時間帯でデータが欠落している箇所を遡って補完する。 |
| **入力** | DBの読み取りのみ。**外部API呼び出し・CSVファイル読み込みは行わない**：`t_101`（世帯一覧）＋`t_202`（機器ステータスの生データ ― 温度の16進値を格納する`c236`／`c237`の2カラム）＋`s_102`（日別・時間別の結果テーブル。NULLのまま残っている時間帯を探すために再読込する）。 |
| **出力** | **DBへの書き込みのみ** ― 実行ごとに世帯あたり2件（センサー位置ごとに1件）を`s_102`（エンティティ`ConSensorHourlyValue`、共通ライブラリ`EminelSvLib`経由）へ書き込み、欠落時間帯があればbackfillの書き込みも追加する。メール送信・CSV出力は行わない。 |
| **処理概要** | 1. 算出対象の時刻を決定する（パラメータ指定またはシステム現在時刻－1時間）。パラメータがある場合はフォーマットをvalidateする。<br>2. その1時間の枠内にある生データを、有効な全世帯について取得し、世帯ごとにまとめる。<br>3. 世帯×センサー位置ごとに、16進値をパース→10進値/10に変換し、エラー値を除外したうえで有効な値の平均を算出、有効な温度範囲を外れる場合はnull化する。<br>4. 現在時刻分の結果を`s_102`へ書き込む。<br>5. 書き込みが成功した場合、過去の時間帯がNULLのままの世帯について最大168時間分遡ってスキャンし、欠落している時間帯ごとに生データを再取得して補完（backfill）する。これらは全体で1つのtransactionにまとめる。 |

## 2. 詳細

### 2.1 実行スケジュールと算出時刻

| 項目 | 内容 | 出典 |
|---|---|---|
| 実行スケジュール（cron） | `26 * * * *` ― 毎時1回、26分に実行 | `docs/02_詳細設計/10_バッチ処理/mng-webap_cron設定_20241029.txt:15-16` (`#5.日毎室温データ算出` → `5_CalcDailyRoomTemperature.sh`) |
| 実行コマンド | `php cake.php CalcDailyRoomTemperature [--datetime="算出日時"]` | `CalcDailyRoomTemperatureCommand.php:46,62` |
| **calculationTime**（パラメータ未指定の場合） | `現在時刻－1時間` | `CalcDailyRoomTemperatureCommand.php:65-67` |
| パラメータ`--datetime`を指定した場合 | 正規表現でフォーマット`yyyy-MM-ddTHH:mm:ss+09:00`をvalidateする。フォーマット不正の場合はALERTログを出力したうえで`abort()`する | `CalcDailyRoomTemperatureCommand.php:70-77,713-724` |
| 現在時刻分のデータ範囲 | `[calculationTime の 時:00:00, +1時間)` ― 最大6件（10分毎） | `CalcDailyRoomTemperatureCommand.php:643-645` |
| 結果の書き込み | その時間帯内の有効な記録の平均値を、**2つのセンサー位置（E0/E1）**それぞれについて算出し、`s_102`へ書き込む | ― |

### 2.2 時間内の生データ取得SQL（`getDeviceStatusData`）

```sql
SELECT ConCustomers.c001                              -- 世帯コード
     , ConCustomers.c012, ConCustomers.c042
     , ConCustomers.c015, ConCustomers.c016, ConCustomers.c024   -- 属性グループ（住宅／機器）
     , ConDeviceStatus.c004                            -- 受信日時
     , ConDeviceStatus.c236                            -- 生の温度値、位置E0
     , ConDeviceStatus.c237                            -- 生の温度値、位置E1
  FROM t_101 ConCustomers, t_202 ConDeviceStatus
 WHERE ConCustomers.c001 = ConDeviceStatus.c001
   AND ConDeviceStatus.c004 >= :fromDate               -- calculationTime、時単位に丸めた値
   AND ConDeviceStatus.c004 <  :toDate                 -- +1時間
   AND ConDeviceStatus.c003 IN ('EA', 'EB')
   AND ConDeviceStatus.c006 BETWEEN '0F4500' AND '0F45FF'
   AND ConCustomers.c052 IS NULL                        -- 論理削除されていない世帯
 ORDER BY ConDeviceStatus.c001, ConDeviceStatus.c004
```
出典：`CalcDailyRoomTemperatureCommand.php:647-665`。

**SQL文で使用しているカラムの意味：**

| テーブル | カラム | 意味 | 備考 |
|---|---|---|---|
| `t_101` | `c001` | 世帯コード（EMS-SP） | 結合キー |
| `t_101` | `c012` | 住宅構造タイプ（build type） | 属性グループ1 |
| `t_101` | `c042` | 暖房機出力（heater power） | 属性グループ2 |
| `t_101` | `c015` | 延床面積（gross floor space） | 属性グループ3 |
| `t_101` | `c016` | 世帯人数（family size） | 属性グループ4 |
| `t_101` | `c024` | ガスコージェネレーションの有無（gas cogeneration） | 属性グループ5 |
| `t_101` | `c052` | 論理削除日時 | `IS NULL` ＝有効な世帯 |
| `t_202` | `c001` | 世帯コード | 結合キー |
| `t_202` | `c003` | レコード種別 | `'EA'`／`'EB'`で絞り込み |
| `t_202` | `c004` | 受信日時 | 時間帯で絞り込み＋ソート |
| `t_202` | `c006` | 機器コード | `0F4500`〜`0F45FF`で絞り込み |
| `t_202` | `c236` | 生の計測値、センサー位置**E0** | ⭐ 算出対象の主要値 |
| `t_202` | `c237` | 生の計測値、センサー位置**E1** | ⭐ 算出対象の主要値 |

### 2.3 時間平均の計算式（世帯×センサー位置ごと ― `getAverage`）

```
1世帯につき、生データ（1時間あたり最大6件）ごとに以下を行う：
① hex文字列（c236またはc237）の末尾4文字を取得する
② 値が'FFFF'か？ → いいえ ― 除外条件は'7FFF'または'8000'（エラー値／未接続）であり、該当する場合はこのレコードを除外する
   該当しない場合 → hexを符号付き10進数へ変換し（2の補数、`changeHexToDec`）、合計に加算し、件数カウンタを増やす

1世帯分のレコードを処理し終えたら（ems_spでグルーピング）：
③ 有効なレコードが1件もない場合 → 平均値 = null
   それ以外の場合 → 平均値 = （有効な値の合計） / （有効なレコード件数） / 10
④ 平均値が[HOURLY_TEMP_LIMIT_BOTTOM, HOURLY_TEMP_LIMIT_TOP]の範囲外の場合 → null
⑤ ③④をE0とE1それぞれについて独立に繰り返す
```
出典：`CalcDailyRoomTemperatureCommand.php:556-630`（`getAverage`）、`:690-705`（`changeHexToDec`）。

**業務定数**（`sources/conciergesv-develop/config/const.php`）：

| 定数 | 値 | 行 |
|---|---|---|
| `HOURLY_TEMP_LIMIT_BOTTOM` | -10.0（有効な温度の下限） | `const.php:413` |
| `HOURLY_TEMP_LIMIT_TOP` | 50.0（有効な温度の上限） | `const.php:415` |

### 2.4 現在時刻分の結果の書き込み ― 書き込み先テーブル`s_102`（`updateAverageData`）

- エンティティ：`ConSensorHourlyValue`（共通ライブラリ`EminelSvLib`）、物理テーブル`s_102` ― 1行＝1世帯×1センサー位置×1日で、24個の時間カラム（`c011`〜`c034`、それぞれ0時〜23時に対応）を持つ。
- 実行ごとに、**その時間帯に生データがある世帯ごと**に**新規レコードを2件**書き込む ― `room_id = 0`（E0）用に1件、`room_id = 1`（E1）用に1件。`device_type = 6`を設定し、`date`は`calculationTime`の日付、該当する時間カラム（`c0XX`、XX＝時＋11）には平均値（またはnull）を設定、`need_ele_complete_flag = 2`、`need_agg_complete_flag = 2`とし、`t_101`から取得した5つの属性グループも併せて設定する。

### 2.5 過去の時間帯で欠落しているデータの補完 ― backfill（`checkRecalculation`）

```
1. s_102において、直前の時間カラム（calculationTime－1時間）に該当する日付の値がNULLのままになっている
   世帯（有効なもの）の一覧を取得する                                          (getEmssp)
2. 各世帯について：
   a. backfill対象の日付について、既存のs_102の行を取得する                    (getAggregationTarget)
   b. 1時間ずつ遡る（subHour = 1 → 168、つまり最大7日分）：
      - その時間カラムに既に値がある（NULLでない）かつ0時でない場合 → ループを終了し、次の世帯へ
      - そうでない場合 → 補完対象の時間帯（補完すべき時刻からcalculationTimeまで）のt_202の生データを取得し (getHourlyData)
        取得した各生データを、そのレコードの日付の該当する時間カラムへ書き込む             (updateRecalculationData)
      - 各生データについて：hexの末尾4文字を取得→'7FFF'/'8000'を除外→hex/10に変換し、
        [HOURLY_TEMP_LIMIT_BOTTOM, HOURLY_TEMP_LIMIT_TOP]の範囲外であればnull化する          (getHourColumnNum)
      - 生データの日付が算出対象日より古い場合（データ遅延）はneed_agg_complete_flag = 1、
        同日の場合は= 2とする
      - 補完した時刻が0時の場合 → 前日分の集計データを再取得し、さらに遡り続ける。
        そうでない場合 → 終了し、次の世帯へ
```
出典：`CalcDailyRoomTemperatureCommand.php:115-270`（`checkRecalculation`、`updateRecalculationData`）、`:308-346`（`getHourlyData`）、`:355-419`（`getAggregationTarget`）、`:427-470`（`getEmssp`）、`:278-298`（`getHourColumnNum`）。

### 2.6 トランザクション

- 手順2.4（現在時刻分の書き込み）と手順2.5（backfill）は、**バッチ全体で1つの共通トランザクション**にまとめられている：手順2.4の書き込みが失敗した場合 → 直ちに`rollback()`し、backfillは実行しない。手順2.4が成功してもbackfillのどこかで失敗した場合 → 同様に全体を`rollback()`する。両方の手順が成功した場合のみ`commit()`する。
- 本バッチは**通知の送信や、日次／月次／年次の値の算出は行わない** ― それらは後続で`s_102`を読み取る別のバッチの役割であり（本commandの対象範囲外である）。
