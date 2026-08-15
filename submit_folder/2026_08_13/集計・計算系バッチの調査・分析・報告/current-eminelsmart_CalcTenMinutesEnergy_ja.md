# 現行システム — EMINEL-smart（ガス使用量データ）

## 概要

現行のEMINEL-smartバックエンド（`syp-eminelstandard-backend`）は積算読み値からガス使用量を自前で計算していない。**3つの独立したバッチ**が、メーカーアプリ側で**計算済みのガス使用量データ**（Rinnai：日次／月次、Noritz：時間単位）を受け取り、そのまま履歴テーブルに書き込む — 差分計算や暖房／給湯の分離といった処理は行わない。3つのバッチはいずれも1日1回実行され、同じオーケストレーターから呼び出される。

## バッチ名とコード上の位置

| バッチ | 場所（Lambda、`src/functions/` 以下） | State Machine | データソース | 書き込み先DBテーブル |
|---|---|---|---|---|
| Rinnaiから**日次**のガス使用量を取得 | `batch-import-rinnai-daily-usage-preprocessing`（API呼び出し）＋ `batch-import-rinnai-daily-usage`（DB書き込み） | `BatchImportRinnaiDailyUsageStateMachine` | RinnaiのREST APIを呼び出し — `rinnaiService.getDataHistory(API_PATH_RINNAI.DAILY_ENERGY_DATA)`、**前日分**を取得 | `DeviceDailyUsageHistoryTable` |
| Rinnaiから**月次**のガス使用量を取得 | `batch-import-rinnai-monthly-usage-preprocessing` ＋ `batch-import-rinnai-monthly-usage` | `BatchImportRinnaiMonthlyUsageStateMachine` | RinnaiのREST APIを呼び出し — `API_PATH_RINNAI.MONTHLY_ENERGY_DATA`。コード内のガード条件により**毎月2日にのみ実際に実行**され、他の日はスキップされる | `DeviceMonthlyUsageHistoryTable` |
| Noritzから**時間単位**のガス／水使用量を取得 | `batch-import-noritz-hourly-usage-preprocessing` ＋ `batch-import-noritz-hourly-usage` | `BatchImportNoritzHourlyUsageStateMachine` | Noritzが用意した**外部S3**上のJSONファイルを読み取る — `AdapterList_{日付}/ena_h_{日付}.json`（APIは呼ばない） | `DeviceDailyUsageHistoryTable` — 同じ日の時間単位レコードを**1戸1日1レコード**にまとめる（`usage_data` は各時刻のデータを持つ配列） |

| 項目 | 内容 |
|---|---|
| 上記3バッチをまとめて呼び出すオーケストレーター | `BatchMigrationIntegratedDataStateMachine` — `src/statemachine/batch-migration-integrated-data.asl.json` |
| 実行スケジュール | `cron(0 8 * * ?)`、`TimeZone = Asia/Tokyo` — 1日1回、朝8:00 |
| 同じオーケストレーター内の他の処理（ガス以外） | Rinnai/Noritzのproperty／status／sensorデータの取り込み、Kyutokiへのデータexport |

## 全体像

| 項目 | 内容 |
|---|---|
| **役割** | メーカーアプリ側で**計算済み**のガス使用量を、Rinnai（日次・月次）／Noritz（時間単位、日次レコードにまとめる）から受け取り、そのまま保存する — 積算値からの差分計算や、暖房／給湯の分離アルゴリズムは行わない。 |
| **Input** | Rinnai: メーカーのREST APIを呼び出す。Noritz: メーカーが外部S3に置いたJSONファイルを読み取る。いずれもS3の一時ファイルから取得した「アプリ連携済み戸リスト」（`list_intergrated_kaiin`）と対応付ける。 |
| **Output** | DBテーブル `DeviceDailyUsageHistoryTable`（Rinnai日次＋Noritz時間単位）または `DeviceMonthlyUsageHistoryTable`（Rinnai月次）にInsertする。 |
| **処理概要** | 1. オーケストレーターが1日1回（朝8:00、Asia/Tokyo）起動する。<br>2. preprocessingステップがメーカーAPIを呼ぶ（Rinnai）、またはS3のファイルを読む（Noritz）。連携済み戸リストと対応付け、データをセグメントに分割してS3に一時保存する。<br>3. メインステップが各セグメントを読み取り、そのまま履歴テーブルに書き込む — 追加の処理は行わない。<br>4. 積算値からの差分計算や暖房／給湯の分離アルゴリズムは無い。入力自体が既に集計済みの値であるため。 |

---

## 出典

| 内容 | 出典 |
|---|---|
| Rinnaiバッチ — 日次 | `src/functions/batch-import-rinnai-daily-usage-preprocessing/app.ts`, `src/functions/batch-import-rinnai-daily-usage/app.ts` |
| Rinnaiバッチ — 月次 | `src/functions/batch-import-rinnai-monthly-usage-preprocessing/app.ts`, `src/functions/batch-import-rinnai-monthly-usage/app.ts` |
| Noritzバッチ — 時間単位 | `src/functions/batch-import-noritz-hourly-usage-preprocessing/app.ts`, `src/functions/batch-import-noritz-hourly-usage/app.ts` |
| オーケストレーターとスケジュール | `src/statemachine/batch-migration-integrated-data.asl.json`, `template.yaml`（`BatchMigrationIntegratedDataStateMachine`, `ComplexScheduleEvent`） |
| DBテーブル | `template-dynamodb.yaml`（`DeviceDailyUsageHistoryTable`, `DeviceMonthlyUsageHistoryTable`） |
