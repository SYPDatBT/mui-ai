# DeleteTimeOutControlOneMinuteCommand（1分タイムアウト制御レコード削除）

## 概要

`DeleteTimeOutControlOneMinuteCommand` は `conciergesv` 上で**毎分**実行される cron バッチであり、「遠隔機器制御」の指令（`instruction_type=1` — ユーザーがアプリから機器を遠隔でON/OFFしたもの、またはDRバッチ `ControlDrOperationCommand` が書き込んだもの）のうち、GW（宅内のゲートウェイ）が取得・処理を完了しないまま `Instructions` キューに4分以上滞留したものを削除する。これは**ポーリング型制御モデル**のsafety-netである：通常はGWが完了を通知した時点で指令が自動的に削除される（`InstructionController.php:548-563`）ため、本バッチはGWが接続を失った／期限内に応答しなかった場合の「死んだ指令」（タイムアウトしたDR指令も含む）だけを掃除し、キューの無限な肥大化を防ぐ。新リポジトリ `syp-eminelstandard-backend` には**同等の仕組みが不要であり、存在もしない** — 移植時の漏れではなく、機器制御のアーキテクチャが質的に全く変わったためである：GWがポーリングで取りに来るためにキューへ指令を書き込む方式ではなく、新システムは機器メーカー（Rinnai/Noritz/Daikin）のクラウドAPIを直接呼び出し、同一のLambda実行内で**同期的に**レスポンスを待つ — DB内に長期間存在する「処理待ちの指令」という概念がもはや無く、タイムアウト／クリーンアップすべき対象が存在しない。

---

# 第A部 ― 旧システム

## A.1 全体概要

| 項目 | 内容 |
|---|---|
| **バッチ名** | クラス：`DeleteTimeOutControlOneMinuteCommand`（`Command` を直接継承）・コマンド名：`DeleteTimeOutControlOneMinute`（`12_DeleteTimeOutControlOneMinute.sh:20` — `bin/cake.php DeleteTimeOutControlOneMinute`）・cronスクリプト：`12_DeleteTimeOutControlOneMinute.sh`・`DeleteDataCommand`／`DeleteTimeOutControlTenMinuteCommand` と同じcronグループ「12.DBデータ削除」に属する。 |
| **役割** | タイムアウトした遠隔制御指令を `Instructions` キューから削除するsafety-net。GWが応答しないことによる死んだ指令の滞留を防ぐ。 |
| **入力** | `Instructions` テーブルを読み取る — `instruction_type = 1` AND `instruction_date < (--datetime − 4分)` で絞り込む。パラメータ `--datetime`（デフォルト `now`）。 |
| **出力** | 条件に一致した各行を1つのトランザクション内で `DELETE` する。新規データの書き込みは行わない。 |
| **処理概要** | 1. タイムアウト基準時刻＝`--datetime − 4分` を算出する。<br>2. トランザクションを開始し、その基準より古い種別1の `Instructions` を検索する。<br>3. 一致する行が無い場合→ロールバック（変更の無いトランザクション）＋`notice` ログ＋終了。<br>4. 一致する行がある場合→1行ずつ削除する。削除に失敗した行があれば `alert` ログを出力し、**全体**をロールバックして直ちに停止する。<br>5. すべて削除に成功→`notice` ログ＋コミット。 |

## A.2 詳細

### A.2.1 実行スケジュールと絞り込み条件

| 項目 | 内容 | 出典 |
|---|---|---|
| 実行スケジュール（cron） | `* * * * *` — 毎分 | `docs/02_詳細設計/10_バッチ処理/mng-webap_cron設定_20241029.txt:42` |
| 絞り込み条件 | `instruction_type = 1` AND `instruction_date < keepTime`（`keepTime = --datetime − 4分`。コード内では `4` のリテラルであり、名前付き定数ではない） | `DeleteTimeOutControlOneMinuteCommand.php:39,44-49` |
| `instruction_type = 1` の意味 | ＝`INSTRUCTION_TYPE_REMOTE_CONTROL`（「宅外制御指示」— 宅外からの遠隔機器制御指令）— **hemssv 側でクロス確認**（`conciergesv` の `const.php` にはこの定数の定義が無く、バッチは数値 `1` を直接使用している） | `sources/hemssv-develop/config/const.php:53` |

### A.2.2 遠隔制御指令1件の通常のライフサイクル（本バッチが「取りこぼしの掃除」であることを理解するため）

1. `instruction_type=1` の指令は2つの経路で `Instructions` に書き込まれる：(a) ユーザーがアプリから機器の遠隔制御を指示 → サーバーが1行を書き込む（`SetDataController.php:384,413`）；(b) 旧システムのDRバッチも種別1の指令を書き込む（`ControlDrOperationCommand.php:215`、コメント「宅外制御指示」）— したがって本バッチはタイムアウトしたDR指令も削除する。（キーは `ems_sp_no`＋`node_id`＋`eoj`、`instruction_content` を伴う）
2. 宅内のGWは定期的に `InstructionController`（hemssv）のAPIを**ポーリング**し、自分宛ての待機中の指令を取得する（「定期ポーリング」、`InstructionController.php:77`）。
3. GWは機器上で指令を実行し、結果をサーバーへ送信する。サーバーは結果を受け取ると、その時点で該当する `Instructions` の行を**自動的に削除**する（通常のライフサイクルであり、バッチによる介入は不要）。
   （`InstructionController.php:546-563`）
4. **GWが期限内に応答しない場合**（接続喪失、オフライン、ネットワーク障害など）— 何も掃除しなければ指令の行は `Instructions` に残り続ける → これが `DeleteTimeOutControlOneMinuteCommand` の存在理由である：通常のライフサイクル（手順3）で削除されないまま4分を超えた種別1の行を掃除する。

**目的は同じで指令種別／タイムアウトが異なる兄弟バッチ**（ここでは詳細な監査は行わず、文脈の提示のみ）：`DeleteTimeOutControlTenMinuteCommand` — `instruction_type IN (3,4,6,7)`（遠隔再起動、プロパティマップ更新、GW設定ファイル更新、暖房制御パラメータ更新）を10分後に削除し、`instruction_type = 5`（ファームウェア更新）を60分後に削除する（現在の分＝0のときのみ実行、つまり毎時1回）。`instruction_type = 2`（機器一覧要求）は、この2つのCommandのいずれのタイムアウトバッチによっても削除されて**いない** *（他のバッチがこの種別を削除しているかどうかは確認できておらず、監査の範囲外）*。

### A.2.3 トランザクションとエラー処理

- 削除すべき行があるかどうかが判明する前にトランザクションを開始する — リストが空の場合は変更の無いトランザクションを `rollback()` することになる（無害だが、やや無駄な操作である）。（`:41-54`）
- `foreach` ループ＋`delete()` で1行ずつ削除し、`deleteAll()` は使用しない（大半のケースで `deleteAll` を使う `DeleteLogicalDeletedDevicesCommand`／`DeleteDataCommand` とは少し異なる）。1行ずつ削除するためレコードごとに結果を確認でき、1行でも失敗すれば**全体**（同じ実行内で既に削除に成功した行も含む）をロールバックして直ちに停止し、残りの行の削除は続行しない。（`:56-62`）
- 絞り込み条件は `instruction_type` ＋ `instruction_date` のみに基づいており、**`instruction_status` は確認しない** — GWが既に指令の処理を開始していた（`instruction_status` が初期状態から更新されている）としても、4分以内に完了を通知できなければ、その指令の行は通常どおり削除される — *（リスクの推測：バッチが削除した後にGWが処理を完了した場合、GWが結果を通知するために `InstructionController` を再度呼び出しても対応する `Instructions` は見つからない — `InstructionController.php:505-510` のコードは「指令が見つからない」場合を info ログを出力して通常のレスポンスを返す形で処理しており、エラーとは扱わない — したがって実際の影響はクラッシュではなく暗黙のスキップであるが、遅延した制御の結果が適切なタイミングで確認できない可能性がある）*。

### A.2.4 特記事項／リスク

- `BaseCommand` を継承していない → PHP Command 自体には二重起動を防ぐPIDロックが無い — ただしcronスクリプト `12_DeleteTimeOutControlOneMinute.sh:5-9` がシェル層で `flock -n` により事前に防いでいる（「多重起動チェック」：実行中のプロセスがあれば `Already running.` を出力して終了する）ため、標準のcronスクリプト経由で実行する限り、1回の実行に60秒以上かかった場合でも2つのプロセスの処理が重複することはない。
  （スクリプトは `docs/02_詳細設計/10_バッチ処理/cron実行用シェルスクリプト/eminel-mng-webap.20240909.tgz` に含まれる）
- 「4分」というしきい値はコード内のリテラルであり、なぜちょうど4分なのか（5分ちょうどではなく、またGWの何らかのポーリング周期に合わせたものでもない）を説明するコメントは無い — 関連する設計ドキュメント（`01_GW通信` docs）はバイナリファイルであり内容を読み取れていないため、この数値に具体的な技術的根拠（例：GWのデフォルトのポーリング周期）があるのか、運用経験に基づいて選ばれた数値に過ぎないのかは確認できていない。

---

# 第B部 ― EMINEL-smart（新システム）との対照

> 「指令キュー＋タイムアウト削除」に相当するLambda／テーブルは見つからなかった — 機器が取りに来るのを待つ指令キューという概念自体が、新アーキテクチャにはもはや存在しないためである。以下の表は調査した領域と具体的な根拠である（B.1/B.2の代わり）。

## 確認済み

| 調査領域／候補 | 結果 |
|---|---|
| 実際の機器制御モデル | **同期プッシュ方式であり、ポーリングではない**：`src/functions/api-device/control-device.ts:91-425`（ユーザーが制御を実行）、`src/functions/batch-execute-automation/app.ts:153-159`（自動スケジュール）— および次行の残りの制御経路 — はいずれも `src/layers/common/nodejs/business-logic/control-device.ts:226-793` を通じてメーカーのクラウドAPI（`rinnaiService`／`noritzService`／`daikinService`）を直接呼び出し、同一のLambda実行内で結果を `await` する — 「処理待ちの指令」をどのテーブルにも書き込まない。 |
| 残りの制御経路（追加確認） | 同じ同期モデルである：DRは `controlDevice` を直接呼び出す（`batch-start-dr/app.ts:110,163,191`、`DEVICE_LASTEST_CONTROL_BY.DR`）か、メーカーのサービスを直接呼び出す（`batch-end-dr/app.ts:206-330`）。センサーによる制御（`batch-control-device-and-push-notice-sensor/app.ts:153-225`）も `rinnaiService`／`noritzService` を直接呼び出す。mui M300 機器は `control-device.ts` 自体を経由し（`SERVER_TYPE.MUI_CLOUD` `:199` → `controlMuiDevice` `:363,452,470`、定義は `:867`）、`infraredRemoteService`（axios、`services/infrared-remote.ts`）を呼び出す — いずれの経路もキューへの書き込みを行わない。ステートマシン `batch-control-device-by-temperature.asl.json` はASLの定義のみが残っており、対応するLambdaは `src/functions/` に存在しない — この結論をさらに裏付けている。 |
| `AutomationTable`（`template-dynamodb.yaml:568-591`） | 指令キューではない — **静的なオートメーション設定**にすぎない（`user_id`＋`automation_id`、`list_device`／`list_control_schedule`／`active_flg` を保持）。`instruction_type` のようなフィールドは無く、TTLも無く、「送信待ちの指令1件」を表すものでもない。 |
| `src/` 全体に対する `Instruction`／`PendingCommand`／`DeviceCommand`／`ControlQueue` のgrep | 0件 — 旧 `Instructions` のような指令キューの役割を担うテーブル／モデルは存在しない。 |
| `src/functions/`、`src/layers/common/nodejs/business-logic/` 内の機器制御に関連する `timeout`／`TimeOut`／`stale`／`pending` のgrep | 業務に関連する結果は0件（エラーログ監視Lambdaに一般的なネットワークエラー文字列 "RequestTimeout" があるのみで、指令キューとは無関係）。 |
| `control-device.ts` 内のNoritzの結果待ちループ（約 214-263, 616-671, 709-764 行） | 1リクエスト内の**内部**ポーリングである（送信したばかりの指令自体の結果を、同一のLambda invocation内で同期的に待つ）— GWが定期的にポーリングして取りに来る複数の待機指令を保持する旧システムの永続キューとは、本質的に全く異なる。長期保存のテーブルではないためTTL／クリーンアップも無い。 |

---

## まとめ

**これは明確に「仕組みが質的に置き換わった」ケースであり、旧ロジックの簡略化や最適化ではない：**

- **旧システム — 非同期ポーリングモデル。キューとクリーンアップが必要：** サーバーが `Instructions` に指令を書き込む → GWが定期的にポーリングして取得する → GWが実行する → GWが結果を通知する → サーバーがキューから指令を削除する。GWはいつでも接続喪失／オフラインになりうるため、システムには「死んだ指令」を掃除する仕組み（まさに監査対象の本バッチ＋`DeleteTimeOutControlTenMinuteCommand` 内の2つの関数）が**必須**である — これはポーリングモデルを選択したことの必然的な帰結である：キューがあれば、キューを掃除する仕組みも必要になる。
- **新システム — 同期プッシュモデル。キューは不要：** Lambdaが機器メーカーのクラウドAPIを直接呼び出し、同一の実行内でレスポンスを待つ（`control-device.ts:226-793`）。「待機指令を書き込み、機器が自分で取りに来る」という手順が無いため、ストレージ層で「タイムアウト」する対象が存在せず、キューテーブルも、それに付随するクリーンアップバッチも不要である。
- **留意すべきトレードオフ** *（推測。本バッチの直接の範囲外だがアーキテクチャに関連する）*：新モデルは、機器／メーカークラウドが1回のLambda呼び出しの待ち時間内に**直ちに**応答できることに依存している（Lambdaのタイムアウトは通常は秒／分単位であり、旧ポーリングモデルが許容していた「数分から数時間待つ」ことはできない）— 機器がオフラインの場合、以前のように「静かに待って数分後にタイムアウトで掃除する」のではなく、エラーが直ちにユーザーへ返される。これは即時の応答性（新）と、機器／GWの一時的な中断をユーザーに直ちにエラーとして通知することなく許容できること（旧）とのトレードオフである。

---

## 出典

| 区分 | 内容 | 出典 |
|---|---|---|
| 旧システム | メインロジック | `sources/conciergesv-develop/src/Command/DeleteTimeOutControlOneMinuteCommand.php` |
| 旧システム | 兄弟バッチ（文脈の提示。詳細な監査は行わない） | `sources/conciergesv-develop/src/Command/DeleteTimeOutControlTenMinuteCommand.php` |
| 旧システム | `instruction_type=1` の意味（hemssv 側でクロス確認） | `sources/hemssv-develop/config/const.php:53-65` |
| 旧システム | `instruction_type=1` の指令の書き込み元（アプリ／DR） | `sources/conciergesv-develop/src/Controller/SetDataController.php:384,413` ・ `src/Command/ControlDrOperationCommand.php:210-215,288` |
| 旧システム | 制御指令の通常のライフサイクル（作成→ポーリング→完了時に自動削除） | `sources/hemssv-develop/src/Controller/InstructionController.php:77,470-563` |
| 旧システム | `Instruction` のカラムの意味 | `sources/eminel_sv_lib-develop/src/Model/Entity/Instruction.php` |
| 旧システム | 実行スケジュール（cron） | `docs/02_詳細設計/10_バッチ処理/mng-webap_cron設定_20241029.txt:42-43` |
| 旧システム | cronスクリプト（flock 多重起動チェック＋コマンド名） | `docs/02_詳細設計/10_バッチ処理/cron実行用シェルスクリプト/eminel-mng-webap.20240909.tgz` → `eminel-mng-webap/12_DeleteTimeOutControlOneMinute.sh:5-9,20` |
| 旧システム | バッチ一覧（日本語の説明、サーバーグループ） | `docs/03_API仕様/04_バッチ一覧.md:78` |
| 新システム | API経由の機器制御（ユーザー） | `src/functions/api-device/control-device.ts:91-425` |
| 新システム | 自動スケジュールによる機器制御（バッチ） | `src/functions/batch-execute-automation/app.ts:153-159` |
| 新システム | 残りの制御経路（DR／sensor／mui M300） | `src/functions/batch-start-dr/app.ts:110,163,191` ・ `src/functions/batch-end-dr/app.ts:206-330` ・ `src/functions/batch-control-device-and-push-notice-sensor/app.ts:153-225` ・ `src/layers/common/nodejs/business-logic/control-device.ts:199,363,452,470,867` |
| 新システム | 共通の制御ロジック。メーカーのクラウドAPIを直接呼び出す | `src/layers/common/nodejs/business-logic/control-device.ts:226-793` |
| 新システム | `AutomationTable`（指令キューではないことの確認） | `template-dynamodb.yaml:568-591` |
