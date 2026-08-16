# DeleteDataCommand（データ削除）

## 概要

`DeleteDataCommand` は、サーバ `conciergesv` 上で毎日（05:15、CSV出力と同じラッパーシェルスクリプト経由 ― `12_CreateCsvAndDeleteData_day1.sh`/`_day2to31.sh`）実行されるcronバッチであり、2つの異なる仕組みで古いデータを削除する ― (1) `CreateTablePartitionCommand` が事前に作成したちょうど10個のPostgreSQLパーティションテーブルについて、期限切れの**子パーティションをDROP**する（本バッチはその「後片付け」側のペアである ― `CreateTablePartition.md` 参照）、および (2) パーティション化されていない3テーブルに対する**時間条件による一括DELETE**（機器制御履歴 `t_301` は13か月保持、顧客グループ区分履歴 `s_151` は24か月保持、省エネポイント `s_141` は2会計年度保持）。新リポジトリ `syp-eminelstandard-backend` では、(1) については `CreateTablePartition.md` ですでに結論が出ている（DynamoDB TTLが全面的に代替し、バッチは不要）― (2) については**3テーブルすべてについて同等の仕組みが存在しない**：2つの概念（機器制御履歴、グループ区分履歴）は、削除を必要とする対応データそのものが存在しない；残る1つの概念（省エネポイント）はほぼ同等の保存テーブル（`PointBadgeStatsTable`）を持つが、**TTLも削除バッチも一切存在しない** ― 新システムのポイント/バッジ履歴は無期限に保持されており、旧システムの2会計年度保持というポリシーとは大きく異なる。

---

# 第A部 ― 旧システム

## A.1 全体概要

| 項目 | 内容 |
|---|---|
| **バッチ名** | クラス：`DeleteDataCommand`（`Command` を extends ― `BaseCommand` は**extendsしていない**。ペアとなるバッチ `CreateTablePartitionCommand` とは異なる。A.2.4参照）・ラッパー内での実際の呼び出しコマンド名：`DeleteData`（`cake.php DeleteData` ― `12_CreateCsvAndDeleteData_day1.sh:32`, `_day2to31.sh:26`）・cronスクリプト：`12_CreateCsvAndDeleteData_day1.sh`（月初の1日）/ `12_CreateCsvAndDeleteData_day2to31.sh`（それ以外の日）・cron上の日本語名：「12.DBデータ削除」。 |
| **役割** | DB基盤の保守＋データ保持ポリシー（retention policy）の遵守 ― パーティションテーブル10個＋通常テーブル3個について、許容期限より古いデータを削除する。 |
| **入力** | 計算のためのデータ読み取りは行わない ― コマンドライン引数 `--datetime`（デフォルト `now`）のみを、「どれだけ古いか」を判定するための基準時点として使用する。 |
| **出力** | 子パーティション10個を `DROP TABLE` する（存在し、かつ期限に達している場合）；通常テーブル3個に対して一括 `DELETE` する（期限に達したレコードがある場合）。新規データの書き込みは行わない。 |
| **処理概要** | 1. `--datetime` から3つの基準時点を正規化する：日初、月初、年初（時:分:秒 = 0）。<br>2. 古くなった日次レベルの子パーティション4個を削除する（t_202, s_101, s_102, s_112）。<br>3. 古くなった月次レベルの子パーティション3個（s_103, s_113, s_105）＋月単位で削除する通常テーブル2個（`ConDeviceControls`, `ConUserGroupHistories`）を削除する。<br>4. 古くなった年次レベルの子パーティション3個を削除する（s_104, s_114, s_121）。<br>5. `ConEcoPoints` を会計年度（暦年ではない）に基づいて削除する。<br>6. 完了時に `notice` ログを1行だけ出力する ― 各ステップごとの個別ログは出力せず、いずれのステップにも try/catch はない（A.2.4参照）。 |

## A.2 詳細

### A.2.1 基準時点の正規化とパラメータ

| 項目 | 内容 | 出典 |
|---|---|---|
| 実行スケジュール（cron） | `15 5 * * *`（`_day2to31.sh` ― 1日を含む毎日実行される：cron式にday-of-monthフィールドがなく、スクリプト名は実際のcronを反映していない）と `15 5 1 * *`（`_day1.sh` ― 1日のみ）― どちらも05:15であるため、1日は2つのスクリプトが重なって実行される（`flock` はファイルごとに `$0` でロックするため、相互にはブロックしない）― 旧システムの実際の運用上のquirkであるが、DROPは存在チェックを行い、DELETEも固定条件によるものであるため、結果への影響はない；1日は `CreateCsvAndZip*` を4本実行する（day2to31は2本のみ）― CSV出力のステップが追加されている点は確かである | `docs/02_詳細設計/10_バッチ処理/mng-webap_cron設定_20241029.txt:39-41`；`cron実行用シェルスクリプト/eminel-mng-webap.20240909.tgz` 内の `.sh` の内容 |
| `--datetime` パラメータ | デフォルトは `'now'`。独自のフォーマットバリデーションはなく ― `FrozenTime::parse()` を直接使用する。 | `DeleteDataCommand.php:23-29,35` |
| 3つの正規化された基準時点 | `dateTimeForDay` = 指定された日の00:00:00。`dateTimeForMonth` = 指定された月の1日の00:00:00。`dateTimeForYear` = 指定された年の1月1日の00:00:00。 | `:37-44` |

**cronスクリプト `CreateCsvAndDeleteData` はCSV出力系Commandと共通で呼び出される** *(tgz内の `.sh` の内容から直接確認済み)*：`CreateCsvAndZip*` Command専用のcronエントリは2つのcronファイル（`webap_cron設定_*.txt`, `mng-webap_cron設定_*.txt` ― grep済み、0件）のいずれにも存在しない ― これらのCommandは、まさにこのラッパー `12_CreateCsvAndDeleteData_*.sh` の中から、`CreateCsvAndZip*`（day1は4本／day2to31は2本）→ `DeleteData` → `DeleteLogicalDeletedDevices`（同じグループの4番目のバッチ）の順で呼び出される。`set -eu` により、CSVが失敗した場合は削除コマンドは実行されない ― CSVを削除より先に実行する順序は設計上の意図である（「CSV作成が失敗した場合はDBのデータを消去するコマンドは実施されない。」 ― `cron設定概要.txt:30-32`）。`README.md:159` で確認済みのマッピングとも一致する：docsの項目「08_データ削除と過去データCSV作成」↔ ちょうどこの2つのCommand群（`DeleteDataCommand` + `CreateCsvAndZip*Command`）。

### A.2.2 古い子パーティションのDROP ― 10テーブル、`CreateTablePartitionCommand` との直接対照

`CreateTablePartitionCommand` が事前に作成したものと同じ10テーブル、同じ `CREATE TABLE ... PARTITION OF` の仕組みである（`CreateTablePartition.md` 参照）― 本バッチは方向が逆なだけである：過去のある時点における子パーティション名を（保持すべき日数／月数／年数に基づいて）算出し、`listTables()` にそのテーブルが存在するかを確認し、存在すれば `DROP TABLE` する。

| 関数 | 親テーブル | 保持期間（パラメータ） | 削除対象時点（正規化した基準時点から算出） | 削除後に実際に残る期間数 |
|---|---|---|---|---|
| `dropDailyTable('t_202',...,8)` | 機器状態情報 | `keepDays=8` | `dateTimeForDay − (8+1)` 日 | **9日**（パラメータ名より+1ずれる） |
| `dropDailyTable('s_101',...,8)` | 差分センサ情報 | `keepDays=8` | `− 9` 日 | **9日** |
| `dropDailyTable('s_102',...,14)` | 日毎センサ情報（時間別） | `keepDays=14` | `− 15` 日 | **15日** |
| `dropDailyTable('s_112',...,8)` | 日毎平均センサ情報（時間別） | `keepDays=8` | `− 9` 日 | **9日** |
| `dropMonthlyTable('s_103',...,2)` | 月毎センサ情報（日別） | `keepMonths=2` | `− 2` か月（+1しない） | **2か月**（パラメータ通り） |
| `dropMonthlyTable('s_113',...,2)` | 月毎平均センサ情報（日別） | `keepMonths=2` | `− 2` か月 | **2か月** |
| `dropMonthlyTable('s_105',...,14)` | 週間省エネレポート情報 | `keepMonths=14` | `− 14` か月 | **14か月** |
| `dropAnnuallyTable('s_104',...,3)` | 年毎センサ情報（月別） | `keepYears=3` | `− 3` 年（+1しない） | **3年**（パラメータ通り） |
| `dropAnnuallyTable('s_114',...,3)` | 年毎平均センサ情報（月別） | `keepYears=3` | `− 3` 年 | **3年** |
| `dropAnnuallyTable('s_121',...,3)` | ランキング情報 | `keepYears=3` | `− 3` 年 | **3年** |

出典: `DeleteDataCommand.php:47-62,82-93,107-118,178-189`。

**⚠️ 旧システムの異常点 ― +1のずれが日次レベルにのみ存在し、3つの `drop*Table` 関数の間で一貫していない：**

- `dropDailyTable()` は削除対象時点を `subDays($keepDays + 1)`（`:85`）で算出する ― 減算の前に1を加算している。
- `dropMonthlyTable()` は削除対象時点を `subMonths($keepMonths)`（`:110`）で算出する ― 加算はしない。
- `dropAnnuallyTable()` は削除対象時点を `subYears($keepYears)`（`:181`）で算出する ― 加算はしない。
- 結果として：パラメータ `keepDays=8` は実際には**9日分**のデータを保持するが、`keepMonths=2`／`keepYears=3` は名前の通りちょうど**2か月**／**3年**を保持する ― 同じ「N期間分を保持する」関数群でありながら、日次レベルと月次／年次レベルとで計算式が1単位ずれている。これが意図的なもの（実行時刻が05:15であり、その日がまだ終わっていないための1日分の補正）なのか、3つの関数間のコードのコピーによる誤りなのかは不明である ― コード中に説明のコメントは見つからず、関連する仕様書（`データの保存期間_20240618_朴.xlsx`, `削除処理仕様書_朴_20240819.xlsx`）はバイナリファイルであり内容を読み取れていない。本バッチを移植する担当者は、業務上実際に要求される保持期間数を改めて確認する必要があり、パラメータ名 `keepX` からそのまま推測すべきではない。

### A.2.3 時間条件による一括DELETE ― 通常テーブル3個（パーティション化なし）

| 関数 | テーブル | 意味 | 削除条件 | 出典 |
|---|---|---|---|---|
| `deleteConDeviceControls` | `ConDeviceControls`（テーブル `t_301`） | デバイス制御履歴 ― 機器制御コマンドの履歴 | `created < (当月の月初 − 13か月)` | `:126-141`、カラム `C_CREATED='c004'`（`Entity/ConDeviceControl.php:30`）、`setTable('t_301')`（`Table/ConDeviceControlsTable.php:41`） |
| `deleteConUserGroupHistories` | `ConUserGroupHistories`（テーブル `s_151`） | グループ履歴 ― 月単位の顧客グループ区分履歴（`CreateGroupSummary.md` 参照） | `month < (当月の月初 − 24か月)` | `:149-164`、カラム `C_MONTH='c002'` |
| `deleteConEcoPoints` | `ConEcoPoints`（テーブル `s_141`） | 省エネポイント ― 省エネルギーポイント | `year <= (現在の会計年度 − ECO_POINTS_SAVE_TIME)` | `:201-224`、定数 `ECO_POINTS_SAVE_TIME=2`（`const.php:723`）、`setTable('s_141')`（`Table/ConEcoPointsTable.php:41`） |

- 最初の2つの関数：先に `exists([条件])` を呼び出し、条件に合致するレコードが1件以上ある場合のみ `deleteAll([条件])` を実行する ― 1回の削除につきクエリを2回発行する（チェック＋削除）。最適とは言えないが安全である（対象が無いときは削除せず、不要なロックやログを避けられる）。
- `deleteConEcoPoints` は暦年ではなく**日本の会計年度（4月開始）**を用いる：現在の月が4未満（1〜3月）の場合、会計年度＝暦年 − 1 となる（`:207-211`）。手計算の例：本日が2026-02-15の場合 → 現在の会計年度 = 2025（2月 < 4のため）→ `deleteTargetYear = 2025 − 2 = 2023` → `year <= 2023` の `ConEcoPoints` をすべて削除し、会計年度2024と2025を残す。
- `deleteConEcoPoints` の削除演算子は `<`（前の2つの関数が用いるもの）ではなく `<=` である ― つまり `deleteTargetYear` とちょうど等しい年も削除され、残されない；一方 `ConDeviceControls`／`ConUserGroupHistories` の2つの関数では、しきい値とちょうど等しい時点は保持される（厳密に小さい場合のみ削除する）。

### A.2.4 特記事項／リスク

- **いずれの削除ステップにも try/catch が存在しない**（`CreateTablePartitionCommand` とは大きく異なる ― 作成側バッチでは各 `CREATE TABLE` が個別のtry/catchで隔離されており、1テーブルのエラーが他のテーブルに影響しない）。この削除バッチでは、`execute()`（`:47-65`）内で連続して呼び出される13ステップ全体に一切のエラー処理がない ― 最初のステップでの1つのエラー（例えば依存制約により `DROP TABLE` がブロックされる場合）が例外として外部に投げられ、同じ実行回における残りの削除ステップ全体が停止する（最初のステップでエラーになったテーブルとまったく無関係な通常テーブル3個も含む）。どのステップが失敗したかを具体的に知らせる `alert` ログはなく ― 最後に成功を知らせる `notice` 行が1行あるだけであるため、エラーが発生した場合はその成功ログ行が単に出力されないだけであり、本コマンド内には他の診断情報は一切存在しない。
- **`BaseCommand` を extends していない** ― `CreateTablePartitionCommand`（および他の18個のCommand）とは異なり、本バッチにはCommand層での多重起動防止のPIDロック機構がない；ラッパー `.sh` 層には、それ自身の多重起動を防ぐ `flock -n` がある（各スクリプトの6行目 ― 目的は重複起動排除、`cron設定概要.txt:3-4`）。 *(推測：ここでの削除処理はいずれも重複実行に対して本質的に安全であるため ― `DROP TABLE` は事前に存在チェックを行い、`deleteAll` は同じ日の中では固定の時間条件によるもので、近接した2回の実行の間で変化しない ― Command側で独自のロックを必要としなかった可能性がある；ただしこれは理由についての推測にすぎず、作成者の実際の意図は確認できていない)*。
- `CreateTablePartitionCommand` の出力に直接依存する（作成側バッチが先に、かつ正しいパーティション名で実行されている必要がある。そうでなければ `in_array($partitionName, $tables)` は常に `false` となり、何も削除されない ― エラーではなく、単に動作しないだけである ― そのため2つのバッチでテーブル名がずれた場合、ログから気づくことは非常に難しい）。
- パーティションテーブルを（アーカイブではなく）完全にDROPする処理は、その前段のCSV出力ステップが成功していなければ復旧不可能である ― このリスクはラッパー層で設計上ブロックされている（A.2.1参照）：`.sh` は `set -eu` のもとでCSVを削除より先に実行し、CSVが失敗した場合 `DeleteData` は呼び出されない（`cron設定概要.txt:30-32`）。

---

# 第B部 ― EMINEL-smart（新システム）との対照

> パーティションDROPの部分（10テーブル）については `CreateTablePartition.md` ですでに完全な結論が出ている ― DynamoDB TTLがパーティションの作成／削除のペア全体を代替しており、同等のバッチは一切不要である。以下ではA.2.3の条件付きDELETE対象の3テーブル（`ConDeviceControls`=`t_301`, `ConUserGroupHistories`=`s_151`, `ConEcoPoints`=`s_141`）のみを対照する。
> B.1/B.2を立てられるだけの「同じ本質」を持つ候補（同等のデータを持ち、かつ同等のretention機構を持つもの）は存在しない ― 代わりに「確認済み事項」の表を用いる。

## 確認済み

| 旧システムの概念 | 調査した領域／候補 | 結果 |
|---|---|---|
| `ConDeviceControls`（機器制御履歴、13か月保持） | `template-dynamodb.yaml`（全体）、`src/layers/common/nodejs/models/DeviceControl.ts`、`batch-execute-automation`、`batch-control-device-and-push-notice-sensor`、`batch-end-dr` | 制御の履歴を保存するテーブルは存在しない。`AutomationTable` はオートメーションの設定のみを保存する（履歴用のtimestampを持たない）。`DeviceControl` はコマンド実行時に一時的に用いるpayloadのinterfaceにすぎず、永続化されない。→ 旧システムで削除対象となるデータは新システムには**存在しない**（retentionの問題ではなく、この履歴自体をまだ保存していないということである）。 |
| `ConUserGroupHistories`（グループ区分履歴、24か月保持） | `src/` 全体に対する `UserGroupHistory`/`GroupSummary`/`GroupAve`/`population`/`compare` のgrep | 0件 ― `CreateGroupSummary.md` ですでに出ている結論と一致する（「類似グループとの比較」機能は未移植）。retentionを必要とするこのデータ自体が存在しない。 |
| `ConEcoPoints`（省エネポイント、2会計年度保持） | `PointBadgeStatsTable`（`template-dynamodb.yaml:1012-1047`）、`PointBadgeMasterTable`（`:1049-1061`）、`UserBadgeSummaryTable`（`:1445-1457`）、`src/functions/give-point-to-point-infinity/app.ts` | `PointBadgeStatsTable` が最も近いテーブルである ― `user_id`＋`received_month`/`received_at` によりポイント/バッジの獲得履歴を保存する（GSI `gsi_received_month`）。ただし：**`TimeToLiveSpecification` が存在せず**（`DeviceMonthlyUsageHistoryTable:1202-1204` のようにTTLを持つusage系テーブルとは異なる）、**会計年度という概念も用いておらず**、`src/functions/`, `src/statemachine/` に対する `delete`/`cleanup`/`purge`/`retention` のgrepでも、ポイント/バッジをスケジュールに従って削除するLambdaは見つからない。→ 類似データの保存は行われているが、**retention機構がまったく欠けている** ― 監査対象である部分（retention）とは本質が異なり、storageの部分の話ではない。 |

---

## まとめ

**パーティションDROPの部分（10テーブル）― `CreateTablePartition.md` ですでに結論が出ているため、ここでは繰り返さず、直接関係する点のみを述べる**：`CreateTablePartitionCommand` は各operationのエラーを個別のtry/catchで隔離しているのに対し、`DeleteDataCommand`（監査対象のバッチ）にはtry/catchが一切ない（A.2.4）― 2つのバッチは同一のPostgreSQLパーティショニング機構を運用しているにもかかわらず、耐障害性の水準が大きく異なる；新システムでは、この非対称性もパーティション機構全体とともに消滅する（DynamoDB TTLでは、エラーとなりうる「能動的な削除」ステップが存在しないため、try/catchを必要としない）。

**時間条件によるDELETEの部分（3テーブル）― これは本監査による新しい発見であり、他のファイルではこれまで述べられていない：**

- 3つのうち2つの概念（`ConDeviceControls`=`t_301`, `ConUserGroupHistories`=`s_151`）は、現時点の新システムに対応するデータがまだ存在しない ― 「削除の仕組みが欠けている」のではなく、そのデータを保存する機能自体がまだ存在しないということである（機器制御履歴はリアルタイム処理のみで永続化しない；グループ比較機能は未移植 ― `CreateGroupSummary.md` で確認済み）。ただしグループ履歴（`s_151`）については：グループ比較機能はすでに「実施する」で確定しており（C2 ランキング ― すべての平均/ランキングは月1回のグルーピングバッチに依存する）、このデータは新システムに登場することになる ― 24か月保持という要件は新しいグルーピングの設計の場へ引き継がなければならず、「retentionを気にする必要がない」区分に入れることはできない。
- 3つのうち1つの概念（`ConEcoPoints` → `PointBadgeStatsTable`）はまったく異なるケースであり、最も注目すべきものである：**対応するデータは存在する**（ポイント/バッジ履歴）が、**retention機構は存在しない** ― TTLもなく、削除バッチもない。つまりこの点において、新システムは「質的に別の仕組みへ置き換えた」のではなく、単に**まだ何の仕組みも持っていない**ということである ― 新システムのポイント/バッジ履歴は無期限に保持されている一方で、旧システムは意図的にちょうど2会計年度分を保持していた（`ECO_POINTS_SAVE_TIME=2`, `const.php:723`）。これは、ポイント/バッジの保存期間に制限が必要かどうかを新しい業務側で改めて確認する際に留意すべき実際のギャップであり、「DynamoDBは保存コストが安いのでおそらく不要だろう」と自ら推測することはできない ― これは技術的判断ではなく業務的判断である。

---

## 出典

| 区分 | 内容 | 根拠 |
|---|---|---|
| 旧システム | 主要ロジック | `sources/conciergesv-develop/src/Command/DeleteDataCommand.php` |
| 旧システム | `ConDeviceControl` のカラムの意味 | `sources/eminel_sv_lib-develop/src/Model/Entity/ConDeviceControl.php:30` |
| 旧システム | `ConUserGroupHistory` のカラムの意味（`CreateGroupSummary.md` で監査済み） | `sources/eminel_sv_lib-develop/src/Model/Entity/ConUserGroupHistory.php` |
| 旧システム | `ConEcoPoint` のカラムの意味 | `sources/eminel_sv_lib-develop/src/Model/Entity/ConEcoPoint.php:35` |
| 旧システム | 会計年度のretention定数 | `sources/conciergesv-develop/config/const.php:723` |
| 旧システム | 実行スケジュール（cron）、`CreateCsvAndZip*` 専用のcronが存在しないことの確認 | `docs/02_詳細設計/10_バッチ処理/mng-webap_cron設定_20241029.txt:39-41`（ファイル全体をgrep済み） |
| 旧システム | ラッパー `.sh` の内容（CSV→deleteの順序、`flock`、`set -eu`）＋設計上の意図 | `docs/02_詳細設計/10_バッチ処理/cron実行用シェルスクリプト/eminel-mng-webap.20240909.tgz`（`12_CreateCsvAndDeleteData_day1.sh`, `_day2to31.sh`）、`cron設定概要.txt:3-4,30-32` |
| 旧システム | docs⇔sources のマッピング。`DeleteDataCommand`+`CreateCsvAndZip*Command` のペアを確認 | `README.md:159` |
| 旧システム | バッチ一覧（日本語の説明、サーバのグループ） | `docs/03_API仕様/04_バッチ一覧.md:76` |
| 旧システム | ペアとなる「先に作成する」バッチ（パーティション10テーブルの対照） | `docs/legacy-batch-review/CreateTablePartition.md` |
| 旧システム | retention/CSVの仕様書。内容は未読（バイナリ） | `docs/02_詳細設計/08_データ削除と過去データCSV作成/{データの保存期間_20240618_朴.xlsx,データ削除と過去データCSV作成仕様.xlsx,データ削除仕様書/削除処理仕様書_朴_20240819.xlsx,データ削除仕様書/過去データCSV作成仕様書_20240708.xlsx}` |
| 新システム | `ConEcoPoints` に最も近い候補（storageはあるがretentionが欠けている） | `template-dynamodb.yaml:1012-1047`（`PointBadgeStatsTable`）、`:1049-1061`（`PointBadgeMasterTable`）、`:1445-1457`（`UserBadgeSummaryTable`） |
| 新システム | TTLを持つテーブルとの対照（`PointBadgeStatsTable` に無いことを示すため） | `template-dynamodb.yaml:1202-1204`（`DeviceMonthlyUsageHistoryTable`） |
| 新システム | 機器制御履歴を保存していないことの確認 | `src/layers/common/nodejs/models/DeviceControl.ts` |
| 新システム | 顧客グループ機能が存在しないことの確認（監査済み） | `docs/legacy-batch-review/CreateGroupSummary.md` |
