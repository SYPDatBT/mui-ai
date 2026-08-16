# TerminateOutdatedDeviceControlJobsCommand（期限切れデバイス制御ジョブ終了）

## 概要

`TerminateOutdatedDeviceControlJobsCommand` は `conciergesv` 上で**毎分**実行されるcronバッチであり、アプリ側の
「機器制御ジョブ」（`ConDeviceControls` テーブル）のうち、作成から5分以上経過してもGWから結果を受け取れて
いないものを処理する ― 一括で失敗としてマークし（`send_result_kind=HEMS_FAILED`）、「[機器名]の設定が
タイムアウトしました」とユーザーへPush通知を送信する。直接のPush送信が失敗した場合は `PushMessages` キューへ
投入し、`DispatchPushMessagesCommand` が再送するフォールバック機構を備える。本バッチは、
`DeleteTimeOutControlOneMinuteCommand`（調査済み）がHEMS側のキューを片付けているのと同じ遠隔制御フローに
おける「ユーザーへのエラー通知」を担う環である ― 2つのバッチは同じ1つのジョブを見張っており、対象テーブルと
タイムアウト時間が異なる（GW側キューは4分、アプリ側ジョブは5分）。新リポジトリ `syp-eminelstandard-backend`
には**同等の仕組みが存在しない** ― テーブル／バッチが無いだけでなく、「制御がタイムアウトした際にPushで
ユーザーへ能動的にエラーを通知する」という業務上の振る舞いそのものも**完全に消失**しており、いかなる形でも
移植されていない：新システムの機器制御は機器メーカーのクラウドへの同期API呼び出し1回であり、エラー／
タイムアウトはそのAPI自身のHTTPレスポンスとしてその場で返るのみである ― アプリを閉じている、あるいは
エラーを表示しない場合、ユーザーは自分の要求が失敗したことを知ることができない（GWのポーリング＋独立した
cronバッチにより、アプリを閉じていても必ずPushが届くことを保証していた旧システムとは大きく異なる）。

---

# 第A部 ― 旧システム

## A.1 全体概要

| 項目 | 内容 |
|---|---|
| **バッチ名** | Class: `TerminateOutdatedDeviceControlJobsCommand`（`Command` を継承。コンストラクタ経由で `PushMessageServiceInterface` をdependency injectionしている ― 調査済みの他のCommandと比べて異例）・cronスクリプト: `30_TerminateOutdatedDeviceControlJobs.sh`・cron内の日本語名称:「30.機器制御タイムアウト機能」。 |
| **役割** | （GWが期限内に応答しなかったことで）タイムアウトしたアプリ側の機器制御ジョブを検出し、失敗としてマークしたうえで、Push通知によりユーザーへ能動的に通知する。 |
| **Input** | `ConDeviceControls` テーブル（物理テーブル `t_301`）を読み取り、`ConDevices`（物理テーブル `t_201`。有効かつ未削除の機器のみ）および `PushDeviceTokens`（Push送信用のトークンを取得）とJOINする ― 絞り込みは `created <= now−5分` AND `result_received IS NULL` AND `send_result_kind IS NULL`。パラメータ `--datetime`（デフォルト `now`）。 |
| **Output** | `ConDeviceControls` の `send_result_kind`／`modified` を一括 `UPDATE` する；`PushMessageServiceInterface` 経由でPush通知を送信する；送信に失敗した場合 → `PushMessages`＋`PushMessageDestinations` に1行を追加で書き込む（再送キュー）。 |
| **処理概要** | 1. タイムアウトしたジョブを絞り込むクエリを組み立てる（機器＋Pushトークンのjoinを含む）。<br>2. データが尽きるまでページング（1ページあたりlimit 500）で繰り返す。<br>3. 各ページ：`updateAll` によりページ内の全ジョブを `HEMS_FAILED` としてマークする。<br>4. ジョブごとに：Pushトークンがあれば「タイムアウト」のPushを送信する；送信に失敗した場合は他バッチが再送できるよう `PushMessages` キューへ保存する；Pushトークンが無い場合はスキップする（再送用の保存も行わない）。 |

## A.2 詳細

**機器制御ジョブ1件のライフサイクル図**（本バッチが全体のどこに位置するかを示すため ― `DeleteTimeOutControlOneMinute.md`
に既出の詳細は繰り返さず、参照にとどめる）：

```
アプリが制御コマンドを送信 ─▶ SetDataController (conciergesv):
                             ConDeviceControls に1行書き込む (created=now, result_received=NULL,
                             send_result_kind=NULL) + Instructions に1行 (type=1)、照合用に "seqno"
                             = control_id を格納
                                     │
                                     ▼
                    GW が Instructions をポーリング (hemssv) ── コマンドを取得し機器を実行
                                     │
                     ┌───────────────┴───────────────┐
                     ▼ (GWが4分以内に応答)          ▼ (GWが応答しない)
     InstructionController が ConDeviceControls を更新  Instructions は
     (result_properties, result_received=now) ＋        DeleteTimeOutControlOneMinuteCommand
     Instructions の行を削除；結果が異常な場合は       により削除される (4分、ConDeviceControls には触れない)
     失敗をPush通知 (sendPushNotification は常に succeeded=false で呼ばれる)
                                                                    │
                                                                    ▼
                                                   ConDeviceControls は result_received=NULL
                                                   send_result_kind=NULL のまま残る (「孤児ジョブ」)
                                                                    │
                                                                    ▼
                                      TerminateOutdatedDeviceControlJobsCommand (5分、本バッチ):
                                      HEMS_FAILED としてマーク + 「タイムアウト」をユーザーへPush通知
```

本バッチの**5分**という基準は、`Instructions` を削除する**4分**より長い ― アプリ側が正式にユーザーへエラーを
通知する前に、HEMS側のキューが自力で決着（成功、または削除）するだけの時間を確保するためであり、GWにまだ
応答の余地がある段階で早すぎるエラー通知を出すことを避けている。

### A.2.1 タイムアウトジョブの絞り込み条件

| 項目 | 内容 | 出典 |
|---|---|---|
| 実行スケジュール（cron） | `* * * * *` ― 毎分 | `docs/02_詳細設計/10_バッチ処理/mng-webap_cron設定_20241029.txt:116-117` |
| 絞り込み条件 | `ConDeviceControls.created <= (--datetime − 5分)` AND `result_received IS NULL` AND `send_result_kind IS NULL` | `TerminateOutdatedDeviceControlJobsCommand.php:96-100` |
| 有効な機器の条件（JOIN） | `ConDevices.dev_reg_status = REG_STATUS_ACTIVE(1)` AND `ConDevices.deleted IS NULL` ― 削除済み／稼働停止となった機器のジョブもタイムアウト処理の対象となる（通知に表示するための正式な機器名が取得できないだけで、その場合は「機器」という文字列で代替する） | `:82-94,131-134` |
| `ConDeviceControls` のカラムの意味 | `c001`=control_id（hemssv側の `Instructions.instruction_content` 内の `seqno` と一致）、`c002`=ems_sp、`c004`=created、`c008`=result_received、`c010`=send_result_kind（`HEMS_FAILED=1`。定義されている値は1つのみ ― 成功時はこのカラムをセットする必要がない） | `Entity/ConDeviceControl.php:27-39` |
| ライフサイクルの確認（GWが期限内に応答した場合に `result_received` を書き込み／`Instructions` を削除する箇所） | `sources/hemssv-develop/src/Controller/InstructionController.php:572-582`（`result_received` の書き込み）・`:545-556`（`Instructions` の削除） |

### A.2.2 ページング処理と一括マーキング

1. 元のクエリは固定の絞り込み条件（A.2.1）を共通で用いており、明示的な `->order()` は無い。
2. `while(true)` ループ：`limit(500)->offset($offset)` により最大500行を1ページとして取得する。
3. データが尽きたら（`isEmpty()`）→ ループを終了する。
4. `updateAll()` によりページ内の全ジョブをマークする：`send_result_kind = HEMS_FAILED`、`modified = now`。
5. ジョブごとにPush送信処理を行う（A.2.3参照）。
6. ページの返却件数が `limit`（500）未満 → 終了する（最終ページとみなす）；そうでなければ `offset += 500` として繰り返す。

出典：`TerminateOutdatedDeviceControlJobsCommand.php:82-119,166-170`。

**⚠️ 旧システムの異常点 ― 縮小し続ける結果セットに対してOFFSETを加算していくページング：**

- 再現条件：1回の実行におけるタイムアウトジョブ数が500を超える（1ページより多い）場合。
- 不具合の仕組み：上記の手順4は、現在のページで取得したばかりのジョブに `send_result_kind` をセットする ―
  これにより、それらのジョブは `send_result_kind IS NULL` の条件に合致しなくなる。次のページは `offset += 500`
  を用いるが、（前ページ分のジョブが除かれて）縮小した集合に対して改めて先頭から検索する ― 従来のoffsetは
  位置がずれてしまい、途中の**一定範囲のジョブが取りこぼされる**（この実行では、どのページでも取得されない）。
  さらに、実際より早くループが終了する可能性もある（offsetがそれらを「飛び越えて」しまうため、未処理のジョブが
  残っていても次のページの返却件数が `limit` 未満になる）。
- 実際の影響：この実行で取りこぼされたジョブが**永久に失われることはない** ― それらの `send_result_kind` は
  `NULL` のままであるため、次回の実行（cronは毎分のため1分後）が `offset=0` から改めて検索し、通常どおり
  拾い上げる。したがって実質的な影響は、500件を超えるタイムアウトジョブが同時に発生するという稀なケースにおいて
  **ユーザーへのエラー通知が最大で数分遅れる**ことである ― データの消失ではないが、新システムへ移植する場合には
  修正すべきページングのロジック不具合であることに変わりはない（単純なoffsetではなく、cursor/keyset paginationを
  用いるか、処理済みIDを除外する条件を追加する）。
- 明示的な `->order()` が無いことが、この問題をさらに悪化させている（SQLの理論上、呼び出しごとの返却順序が
  安定する保証はない。実際にはPostgreSQLでは、間に挿入／削除が入らなければ安定することが多いが ― ここでは
  まさに、このループ自身の `updateAll` による書き込みが間に入っている）。

### A.2.3 通知の送信と再送フォールバック機構

1. ジョブごとに：対応する `PushDeviceToken` が見つからない場合（`ems_sp` に登録済みトークンが無い場合）→
   `continue` により完全にスキップする ― 送信も、再送用の保存も、ログ出力も行わない。（`:126-129`）
2. トークンがある場合 → タイトルは固定で `"機器設定変更"`、本文は機器名（`HemsDeviceNameService::getDeviceNameForApp`
   経由。機器を取得できない場合のフォールバックは `"機器"`）＋
   `"... の設定変更がタイムアウトしました。"`（機器の設定変更がタイムアウトした旨）を組み立てる。（`:131-135`）
3. `pushMessageService->sendToDeviceTokens()` を呼び出す（interfaceはコンストラクタでinjectされている ― テストや
   実装の差し替えを容易にする設計）。**exception** が発生した場合、または `successCount !== 1` の場合をエラーと
   みなす（`:137-146`）― 2種類のエラー（ネットワークのexceptionと「送信したが受信者がいない」）を同一の
   エラー処理分岐に正規化している。
4. 送信に成功した場合 → `continue` で次のジョブへ進み、手順5には一切入らない。（`:148-149`）
5. 送信エラー（try/catchで捕捉）→ エラーログを出力したうえで、**`PushMessage` 1件 ＋ `PushMessageDestination` 1件を
   新規作成**しDBへ保存する ― これはシステム全体で共通利用される標準のキューであり、`DispatchPushMessagesCommand`
   （バッチ#24。同じく毎分実行）が自動的に走査して後から再送する。この再送レコードの保存に失敗した場合もログ
   出力のみで、追加の処理は無い（直接送信と再送用保存の両方が失敗しても、ジョブは「処理済み」として扱われる）。
   （`:154-163`）

### A.2.4 特記事項／リスク

- `BaseCommand` を継承していない → PHP層でのPIDロックによる多重起動防止は無い（調査済みの他のクリーンアップ系
  バッチと同様）。ただし外側のcronスクリプト `30_TerminateOutdatedDeviceControlJobs.sh` が `flock -n` を用いている
  （「flockで多重起動チェック」）ため、実際にはシェル層で多重起動が防止されている。
- 有効でない／削除済みの機器のジョブも通常どおりタイムアウトとしてマークされる（違いは通知に表示される名称のみ）
  ― つまり、ジョブ作成後にその機器がシステムから取り外された場合でも、ユーザーは「[機器]の設定がタイムアウト
  しました」という通知を受け取る。これは意図的な挙動（ユーザーへ要求の失敗を知らせる必要は残る）である可能性も
  あれば、このエッジケースが考慮されていないだけの可能性もある ― 意図を裏づけるコメントは無い。*(推測)*
- `PushMessages` 層には「再送を何回行ったか」の記録や再送回数の上限が無い（本書の範囲外 ―
  `DispatchPushMessagesCommand` に属し、未調査）。
- コンストラクタでdependency injectionにより `PushMessageServiceInterface` を受け取る ― 調査済みの他のCommand全体
  （いずれも `initialize()` 内でservice/tableを直接呼び出している）と比べた唯一の相違点であり、本Commandには実際に
  unit testが存在する可能性を示す（テストファイルは、調査済みの他の `src/Command` 群には含まれていない）。

---

# 第B部 ― EMINEL-smart（新システム）との対照

> 同等のLambda／テーブルは見つからなかった。以下の表は、調査した箇所と具体的な根拠である
> （B.1／B.2に代えて記載する）。

## 確認済み

| 領域／候補 | 結果 |
|---|---|
| 機器制御時のエラー経路（`src/functions/api-device/control-device.ts`、関数 `controlDevice:63-467`） | `rinnaiService`／`noritzService`／`daikinService` の呼び出しの周囲に内部的なtry/catchは一切無い ― エラー／exceptionはそのまま `apiHandler`（`src/layers/common/nodejs/utils/api-handler.ts:19-37`）まで上がり、`fail(STATUS_CODE.INTERNAL_SERVER_ERROR, {message: ERR_SYS_ERROR})` を**HTTPレスポンスとしてその場で**返す。Noritzのいくつかの分岐は能動的に `fail(BAD_REQUEST, ERR_CANNOT_CONTROL_REMOTE_DEVICE)` を返す（233-236行、259-262行、291-294行、316-319行）― いずれもAPIのエラーレスポンスにとどまり、Pushが併せて送られることは無い。 |
| Noritzの結果待ちループ（`control-device.ts` 214-223行、243-252行、…） | 同一Lambda内での同期的なポーリングであり、ループ内に明示的なタイムアウトは無い ― ハングした場合はAWS Lambda自身のタイムアウトで打ち切られ、汎用の500エラーを返すのみでPushは無い。5分後に独立したcronバッチが確認する旧システムとは大きく異なる。 |
| `src/layers/common/nodejs/business-logic/control-device.ts:776-789` | try/catchはあるが、扱うのはトークンがrevokeされたケースのみ（`isUnauthorizedRemoved` → その機器をスキップする）。それ以外のエラーはそのまま `throw` され、Push関連のロジックは無い（ファイル内でPush系serviceを一切importしていない）。 |
| `src/layers/common/nodejs/services/push-notification-firebase.ts`、関数 `pushNotificationFirebase:35-105` | Firebase経由で**1回のみ**送信する（89行）。トークンが不正な場合はトークンを削除し（138-149行）、それ以外のエラーは `throw` する ― 旧システムの `PushMessages`／`PushMessageDestinations`／`DispatchPushMessagesCommand` のような**再送キューは存在しない**。 |
| `src/` 全体に対する `HEMS_FAILED`／`send_result_kind`／`ConDeviceControls`／`result_received`／`PushMessage`／`DispatchPushMessages` のgrep | 0件 ― 新システムには、テーブルもバッチも、「制御ジョブのタイムアウト」という概念自体も存在しない。 |

---

## まとめ

**本件は「仕組みそのものが質的に置き換わった」ケースである ― ただし兄弟バッチ `DeleteTimeOutControlOneMinuteCommand`
とは異なり、単に方式が変わっただけでなく、業務上の振る舞いが1つ完全に抜け落ちている：**

- **「タイムアウトしたキューの掃除」の部分**：`DeleteTimeOutControlOneMinute.md` でまとめた理由とまったく同じである ―
  機器制御のアーキテクチャが、非同期ポーリング型（キュー＋タイムアウトの掃除が必要）から同期プッシュ型
  （メーカークラウドのAPIを直接呼び出し、Lambda内でそのまま `await` する）へ変わった ― タイムアウト検出のための
  専用バッチが必要になるほど長く残る「待機中のジョブ」自体が存在しない。
- **「Pushによるユーザーへのエラー通知」の部分 ― ここが兄弟バッチとの相違点であり、本調査で最も注目すべき点である**：
  旧システムは2つの役割を分離していた ― (1) 制御を開始するためのAPI呼び出し、(2) 制御が失敗またはタイムアウト
  した場合に、ユーザーへ必ずPushで通知することの保証（成功時にPushは無い ― アプリ自身が新しい状態を確認する）。
  後者は、バックエンド層でのGWポーリング＋専用のcronバッチによる監視により、アプリが開いているかどうかに関係なく
  成立していた。新システムはこの2つを1つに統合している：結果は、その時に呼び出したAPI自身のレスポンスとしてのみ
  返る ― アプリを閉じている、通信が切れている、あるいはエラーを正しく表示しない場合、**ユーザーは自分の制御要求が
  失敗したことを永久に知ることができない**。これは「アーキテクチャの最適化」ではなく、旧システムと比べて
  **UX／信頼性上の保証が1つ完全に失われている**ということである ― アプリを閉じていても制御失敗をユーザーへ通知する
  保証が新しい業務でも必要であるならば（例：タイマー制御や、バックグラウンドで動作するautomation）、同等の非同期
  通知の仕組みを改めて追加する必要があり、「APIレスポンスでエラーを返す」ことをもって十分な代替とみなすことは
  できない。
- 全体としてのトレードオフ：アプリが開いていて直接応答を待っている場合はより速く結果が返る一方、アプリが
  フォアグラウンドに無い場合や、automation／バックグラウンドから制御が起動された場合（エラーを見るために
  「レスポンスを待っている」者が誰もいない場合）には、通知を保証できなくなる。

---

## 出典

| 区分 | 内容 | 根拠 |
|---|---|---|
| 旧システム | メインロジック | `sources/conciergesv-develop/src/Command/TerminateOutdatedDeviceControlJobsCommand.php` |
| 旧システム | `ConDeviceControl` のカラムの意味（物理テーブル `t_301`） | `sources/eminel_sv_lib-develop/src/Model/Entity/ConDeviceControl.php` · `Table/ConDeviceControlsTable.php:41` |
| 旧システム | 関連する `ConDevice` のカラムの意味（物理テーブル `t_201`） | `sources/eminel_sv_lib-develop/src/Model/Entity/ConDevice.php:52-88` · `Table/ConDevicesTable.php:41` |
| 旧システム | GWが期限内に応答した場合に `result_received` を書き込み／`Instructions` を削除する箇所（ライフサイクルの確認） | `sources/hemssv-develop/src/Controller/InstructionController.php:572-582`（`result_received` の書き込み）· `:545-556`（`Instructions` の削除） |
| 旧システム | 同じライフサイクルに関わる関連バッチ（調査済み） | `docs/legacy-batch-review/DeleteTimeOutControlOneMinute.md` |
| 旧システム | Push再送キューの仕組み（consumer側） | `sources/conciergesv-develop/src/Command/DispatchPushMessagesCommand.php:68-172` |
| 旧システム | 実行スケジュール（cron） | `docs/02_詳細設計/10_バッチ処理/mng-webap_cron設定_20241029.txt:116-117` |
| 旧システム | バッチ一覧（日本語の説明、サーバー区分） | `docs/03_API仕様/04_バッチ一覧.md:80` |
| 新システム | 機器制御API（エラー経路、Pushの併送は無い） | `src/functions/api-device/control-device.ts`（関数 `controlDevice:63-467`） |
| 新システム | エラーのHTTPレスポンスへの正規化 | `src/layers/common/nodejs/utils/api-handler.ts:19-37` |
| 新システム | 共通の制御ロジック（automation）、エラーPushが無いことの確認 | `src/layers/common/nodejs/business-logic/control-device.ts:1-22,776-789` |
| 新システム | 共通のPush機構（1回のみ送信、再送キュー無しの確認） | `src/layers/common/nodejs/services/push-notification-firebase.ts:35-149` |
