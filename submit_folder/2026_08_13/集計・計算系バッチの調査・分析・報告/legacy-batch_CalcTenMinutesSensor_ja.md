# 旧バッチ — CalcTenMinutesSensorCommand（10分毎人感検知差分データ算出）

## 概要

`CalcTenMinutesSensorCommand` は旧システム（EMINEL コンシェルジュサーバー）で10分ごとに実行されるバッチで、ECHONETセンサーのPIR積算カウンタを2回連続で読み取った差分から、各戸ごとに**直近10分間の人感検知回数**を**2部屋分**（リビング／ベッドルーム他）に分けて算出する。結果は `s_101` テーブルに書き込まれ、後続の処理で使用される。詳細はPart 2を参照。

## Part 1 — 概要

| 項目 | 内容 |
|---|---|
| **役割** | センサーから送られる**積算**読み値（PIRカウンタ）から、各戸の**10分間の人感検知回数**を、**2部屋**（リビング／ベッドルーム他）に分けて算出する。 |
| **Input** | 2つのDBテーブルから読み取る: `t_101`（戸別リスト）＋ `t_202`（生の機器状態レコード、別システムが事前にingest済み — `c248`/`c249` の2カラムにPIR積算読み値を保持）。 |
| **Output** | DBテーブル `s_101`（エンティティ `ConSensorMemoryValue`、共通ライブラリ `EminelSvLib` 経由）にInsertする — 実行毎に1戸あたり2レコード（部屋ごと1件）。 |
| **処理概要** | 1. 算出対象の時刻Tを決定する。<br>2. SQL1本で、有効な全戸について2部屋分・連続する2つの10分枠（前枠T〜T+10、後枠T+10〜T+20）の積算読み値を取得する。<br>3. 戸×部屋ごとに、16進文字列→10進数に変換し、異常値／空値を除外する。<br>4. 2つの読み値の差分を計算し、負の場合はカウンタ一周分を補正、閾値超過の場合はnullにする。<br>5. 結果（nullの場合も含む）を `s_101` に書き込む — 全体を1トランザクションで実行。 |

## Part 2 — 詳細

### 2.1 実行スケジュールと算出時刻

| 項目 | 内容 | 出典 |
|---|---|---|
| 実行スケジュール（cron） | `2,12,22,32,42,52 * * * *` — 1時間に6回、10分おき、2分ずらし | `docs/02_詳細設計/10_バッチ処理/mng-webap_cron設定_20241029.txt:6-7` (`#2.10分毎人感検知差分データ算出` → `2_CalcTenMinutesSensor.sh`) |
| 実行コマンド | `php cake.php CalcTenMinutesSensor ["処理対象時刻"]` | `CalcTenMinutesSensorCommand.php:21` |
| **T**（パラメータ未指定時） | `現在時刻 − 20分`、その後10分単位に切り下げ（分の末尾の文字を `'0'` に置換） | `CalcTenMinutesSensorCommand.php:59-66` |
| 2つのデータ枠 | 枠A = `[T, T+10)`（20分前）・枠B = `[T+10, T+20)`（10分前） | `CalcTenMinutesSensorCommand.php:82-97` |
| 結果 | 差分 = （枠Bの読み値） − （枠Aの読み値）、**2部屋**分、`s_101` に書き込み | — |

### 2.2 データ取得SQL

```sql
SELECT customer.c001 AS ems_sp                       -- 戸コード
     , dst_20.living_20                              -- 枠A: リビング
     , dst_20.bed_20                                 -- 枠A: ベッドルーム他
     , dst_10.living_10                              -- 枠B: リビング
     , dst_10.bed_10                                 -- 枠B: ベッドルーム他
  FROM t_101 AS customer                             -- 戸別リストテーブル

  LEFT OUTER JOIN (                                  -- 枠A = [T, T+10)
        SELECT c001 AS ems_sp
             , c248 AS living_20
             , c249 AS bed_20
             , row_number() OVER (PARTITION BY c001
                                  ORDER BY c004 DESC) AS line   -- 1 = 最新レコード
          FROM t_202
         WHERE :targetDate <= c004
           AND c004 < cast(:targetDate as timestamp with time zone) + interval '10 minutes'
           AND c003 IN ('EA', 'EB')
           AND c006 BETWEEN '0F4500' AND '0F45FF'
       ) AS dst_20
    ON dst_20.ems_sp = customer.c001

  LEFT OUTER JOIN (                                  -- 枠B = [T+10, T+20)
        SELECT c001 AS ems_sp
             , c248 AS living_10
             , c249 AS bed_10
             , row_number() OVER (PARTITION BY c001 ORDER BY c004 DESC) AS line
          FROM t_202
         WHERE cast(:targetDate as timestamp with time zone) + interval '10 minutes' <= c004
           AND c004 < cast(:targetDate as timestamp with time zone) + interval '20 minutes'
           AND c003 IN ('EA', 'EB')
           AND c006 BETWEEN '0F4500' AND '0F45FF'
       ) AS dst_10
    ON dst_10.ems_sp = customer.c001

 WHERE customer.c052 IS NULL                         -- 論理削除されていない戸
   AND (dst_20.line = 1 OR dst_20.line IS NULL)      -- 最新レコード、またはデータなしの戸
   AND (dst_10.line = 1 OR dst_10.line IS NULL)
 ORDER BY customer.c001
```
出典: `CalcTenMinutesSensorCommand.php:71-107`。

**SQLで使用するカラムの意味**（コード内コメントをそのまま引用、122〜136行目）：

| テーブル | カラム | 意味 | 備考 |
|---|---|---|---|
| `t_101` | `c001` | 戸コード（EMS-SP） | 結合キー |
| `t_101` | `c052` | 論理削除日時 | `IS NULL` = 有効な戸 |
| `t_202` | `c001` | 戸コード | 結合キー |
| `t_202` | `c003` | レコード種別 | `'EA'`/`'EB'` でフィルタ |
| `t_202` | `c004` | 受信日時 | 時間枠でフィルタ＋最新順に並べ替え |
| `t_202` | `c006` | 機器コード | `0F4500`〜`0F45FF` でフィルタ |
| `t_202` | `c248` | **住環境マルチセンサ0 人感積算** — PIR積算読み値、センサー0（リビング） | ⭐ 主要な計算対象値 |
| `t_202` | `c249` | **住環境マルチセンサ1 人感積算** — PIR積算読み値、センサー1（ベッドルーム他） | ⭐ 主要な計算対象値 |

### 2.3 計算式（戸×部屋ごと）

```
① 文字列切り出し: nullでなく かつ 長さが16文字 → 先頭8文字を取得、そうでなければ → null
② 2つの読み値（枠A／枠B）のいずれかが空          → 結果はnull、処理終了
③ 16進数 → 10進数に変換
④ 値が（0未満 かつ 999,999,999超 — つまり有効範囲外）
   または 元の文字列 = 'FFFFFFFF'（センサー未接続）
   または 元の文字列 = 'FFFFFFFE'（センサー無応答）      → 結果はnull
   それ以外:
       差分 = （枠Bの読み値） − （枠Aの読み値）
       差分 < 0 の場合    → 差分 = 999,999,999 + 差分             ← カウンタ一周分を補正
       差分 > 300 の場合  → 結果はnull                          ← 異常閾値超過
⑤ s_101 に1レコードを書き込む — 結果がnullの場合も含む
```
出典: `CalcTenMinutesSensorCommand.php:177-253`（`updateSensorMemoryValue`, `calcDiffValue`）。

**業務定数**（`sources/conciergesv-develop/config/const.php`）：

| 定数 | 値 | 行 |
|---|---|---|
| `TEN_MINUTES_CALC_SENSOR_START_TIME` | 20分（Tを算出する際のデフォルト遅延） | `const.php:601` |
| `MAX_SENSOR_VALUE` | 999,999,999（カウンタの上限、一周補正に使用） | `const.php:603` |
| `TEN_MINUTES_SENSOR_LIMIT_TOP` | 300回／10分（上限閾値） | `const.php:605` |
| `DETECT_CNT` | 14 — `s_101` に書き込む機器種別コード | `const.php:198` |
| `DETECT_LIVING` | 0 — リビングのコード | `const.php:228` |
| `DETECT_OTHER` | 1 — ベッドルーム他のコード | `const.php:230` |

### 2.4 結果の書き込み — 対象テーブル `s_101`

- エンティティ: `ConSensorMemoryValue`（共通ライブラリ `EminelSvLib`）、物理テーブル `s_101`。
- 実行毎に、**有効な各戸**について**2レコード**を書き込む — `DETECT_LIVING` 用に1件、`DETECT_OTHER` 用に1件 — `device_type = DETECT_CNT(14)`、`room_id`、`date_time = T`、`measured_value = 差分（またはnull）` を設定。
- 全体を**バッチ全体で1トランザクション**として実行: いずれかの戸で書き込みに失敗 → 全体を `rollback()` して `abort()`、部分的な書き込みは行わない。
- このバッチは**自ら通知を送信せず、日次／時間別の値も自ら算出しない** — それらは後で `s_101` を読み取る他のバッチ／コマンドが行う。
