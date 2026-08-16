# 旧バッチ ― DispatchPushMessagesCommand（プッシュ通知メッセージ送信）

## 概要

`DispatchPushMessagesCommand` は、旧システムにおいて**実際にPush通知を送信する「最終工程」**であり、**毎分**（cron `* * * * *`）実行され、`PushMessageDestinations` テーブルを走査して現在の分にちょうど該当する予約済みの行（`status=SCHEDULED`）を取得し、妥当性を検査したうえで、`PushCore` という名前の内部サービス1つを経由して一括送信する（Firebaseを直接呼び出すことはない）。**通知を発行するバッチの大半**（例：`PublishRegularEcoMissionsCommand`、`WatchNotificationCommand` など）はここへ集約される ― それらのバッチは `PushMessageDestinations` へ**送信予約を書き込む**のみであり、実際の送信は本バッチが担う；例外として、`TerminateOutdatedDeviceControlJobsCommand` は `PushCore` へ直接送信し、送信に失敗した場合にのみ送信予約を書き込む。hemssv（`dev_ctrl` の通知）も本バッチを経由せず直接送信する。最大5回・3分間隔のリトライの仕組みがあるが、ページング（offset）の方式には、1分間に送信すべき通知が500件を超える場合に一部の通知を**恒久的に取りこぼす**おそれがある；詳細は第2部に示す。

## 第1部 ― 概要

| 項目 | 内容 |
|---|---|
| **役割** | 現在の分に予約されているレコードに対して実際にPush通知を送信する；送信に失敗した場合のリトライを処理する。 |
| **入力** | `PushMessageDestinations`（送信予約、ステータス、失敗回数）に `PushMessages`（内容、有効期間の枠）をjoinし、さらに `PushDeviceTokens`/`PushFcmTopics`（送信先 ― 特定の1端末、または共通のFCMトピック1つ）をjoinしたもの。 |
| **出力** | 内部API `PushCore`（`POST {PushCore.Api.host}/v2/send-messages`）を呼び出す ― 送信結果に応じて、各 `PushMessageDestinations` の `status`／`schedule`／`failure_count` を更新する。 |
| **処理概要** | 1. 現在の1分間の枠を確定する（`[now:分, now:分+1]` ― `schedule <= endAt`、両端を含む）。<br>2. `schedule` がその枠に入る `SCHEDULED` のdestinationであり、**かつ**親の `PushMessage` が有効期間内であるものを、500件のロット単位で取得する。<br>3. 妥当でないdestination（内容の欠落、送信先の欠落／過剰）を除外する。<br>4. 残りのロットを `PushCore` 経由で送信し、各行の結果（成功／再試行／再試行の上限到達）を更新する。 |

## 第2部 ― 詳細

### 処理の全体図

```
ステップ1  1分間の枠の確定        → [now:分, now:分+1]（schedule <= endAt）            §2.1
ステップ2  500件のdestination取得 → SCHEDULED + 枠に一致 + PushMessage が有効期間内    §2.2
ステップ3  不正なdestinationの除外 → 内容の欠落／送信先の欠落・過剰                    §2.3
ステップ4  payloadの組み立てと送信 → 最大500メッセージ/リクエストにまとめPushCoreを呼ぶ §2.4
ステップ5  結果の更新             → 成功／リトライ（最大5回、3分間隔）／上限到達        §2.5
           データが尽きるまでoffsetを増やしながらステップ2-5を繰り返す                 §2.6 ⚠️
```

| ステップ | 内容 | 詳細箇所 |
|---|---|---|
| 1 | 処理対象の時間枠の確定 | §2.1 |
| 2 | 送信すべきdestinationのクエリ | §2.2 |
| 3 | 妥当でないdestinationの除外 | §2.3 |
| 4 | `PushCore` 経由での送信 | §2.4 |
| 5 | 結果の処理、リトライ | §2.5 |
| ― | ページングのループ ― 異常点 | §2.6 |

---

### 2.1 処理対象の時間枠と再実行用パラメータ

| 項目 | 内容 |
|---|---|
| 実行スケジュール | cron `* * * * *` ― **毎分**（[mng-webap_cron設定_20241029.txt:80](e:/Projects/mui/legacy_eminel_docs-main/docs/02_詳細設計/10_バッチ処理/mng-webap_cron設定_20241029.txt#L80)） |
| 処理対象の枠 | `startAt = now（時:分をそのまま保持）`、`endAt = startAt + 1分`（[:59-60](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/DispatchPushMessagesCommand.php#L59-L60)）― WHEREは `schedule >= startAt` **かつ** `schedule <= endAt` であり、両端を含む（[:77-78](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/DispatchPushMessagesCommand.php#L77-L78)） |
| 再実行用パラメータ | `send_time` ― **効果がない**（⚠️①参照） |

### 2.2 送信すべきdestinationのクエリ

単一のクエリであり、500行のページ単位で繰り返す（[:67-85](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/DispatchPushMessagesCommand.php#L67-L85)）：

| 条件 | 意味 |
|---|---|
| `PushMessageDestinations.status = SCHEDULED`（`0`） | 未送信／再送信待ち |
| `PushMessageDestinations.schedule` が現在の1分間の枠に入る | 送信すべき時点にちょうど該当する（この時点は、送信予約を作成するバッチ ― 例えば `PublishRegularEcoMissionsCommand` ― があらかじめ設定している） |
| `matching PushMessages`：`start_at < endAt` **かつ** `end_at >= startAt` | 親の `PushMessage`（内容）が、それ自身の有効期間の枠内にまだあること（例：ミッションは発行時点から30日間有効 ― `PublishRegularEcoMissionsCommand` の資料を参照）― これはdestinationの送信予約とは**独立した第2の条件**である |

### 2.3 妥当でないdestinationの除外

取得した各destinationについて、送信前に2種類のエラーを検査する（[:90-120](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/DispatchPushMessagesCommand.php#L90-L120)）：

| エラー | 条件 |
|---|---|
| 内容がない | `PushMessage` の `title`、`body`、`data` がいずれも空 |
| 送信先の欠落 | `push_device_token` も `push_fcm_topic` も存在しない |
| 送信先の過剰 | `push_device_token` と `push_fcm_topic` が**両方とも**同時に存在する（本来は排他であるべき ― `PushMessageDestinationsTable` のvalidateを参照） |

エラーとなったdestination → `status = INVALID`（`-2`）をセットし、直ちに保存し、`failureCount` に計上して、後続のステップでは**送信しない**。

### 2.4 payloadの組み立てと `PushCore` 経由での送信

- 妥当な各destination → メッセージ1件 `{title, body, data?, registrationToken または topic}`（[:127-147](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/DispatchPushMessagesCommand.php#L127-L147)）。
- ロット全体（最大500）を1回の `PushMessage->sendMessages()` の呼び出しで送信する（[:152](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/DispatchPushMessagesCommand.php#L152)）― 実際の実装（`PushMessageService`）は `POST {PushCore.Api.host}/v2/send-messages`（デフォルトは `http://localhost:54650`、[push_message.php:4-8](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/config/push_message.php#L4-L8)）を呼び出す ― **Firebaseを直接呼び出すのではなく**、中間の内部サービス1つを経由し、500件を超える場合はさらに500件ずつのロットへ自ら分割する（[PushMessageService.php:81](e:/Projects/mui/legacy_eminel_docs-main/sources/eminel_sv_lib-develop/src/StaticServices/PushMessageService.php#L81)）。
- `data`（存在する場合）は、アプリが通知の種別を判別するための `kind` を持つ：`message`, `survey`, `dev_ctrl`, `motion_alarm`, `eco_mission`, `plus_point`（[PushMessage.php:25-38](e:/Projects/mui/legacy_eminel_docs-main/sources/eminel_sv_lib-develop/src/Model/Entity/PushMessage.php#L25-L38)）。

### 2.5 結果の処理とリトライ

| 結果 | 挙動 |
|---|---|
| 送信成功（`responseItem['success']`） | `status = COMPLETED`（`1`）（[PushMessageDestination.php:44-47](e:/Projects/mui/legacy_eminel_docs-main/sources/eminel_sv_lib-develop/src/Model/Entity/PushMessageDestination.php#L44-L47)） |
| 送信失敗（行ごと、またはリクエスト全体のエラー／exception） | `failure_count += 1`；`< maxFailureCount`（**5**）であれば → 再試行のため `schedule = now + retryIntervalMinutes`（**3分**）に再設定する；そうでなければ → `status = OVER_RETRIED`（`-1`）とし、完全に停止する（[PushMessageDestination.php:58-66](e:/Projects/mui/legacy_eminel_docs-main/sources/eminel_sv_lib-develop/src/Model/Entity/PushMessageDestination.php#L58-L66)、パラメータは [push_message.php:9-14](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/config/push_message.php#L9-L14)） |
| リクエスト全体のエラー（exception、例えば `PushCore` が応答しない場合） | そのロット内の**すべての**destinationが失敗とみなされる ― 上記と同じリトライを適用する（[:164-169](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/DispatchPushMessagesCommand.php#L164-L169)） |

### 2.6 ページングのループ ― ⚠️②の発生源

```php
$limit = 500; $offset = 0;
while (true) {
    $query = ...->limit($limit)->offset($offset);   // điều kiện WHERE giữ nguyên suốt vòng lặp
    $destinations = $query->all()->toList();
    if (empty($destinations)) break;
    // ... xử lý, đổi status/schedule của TOÀN BỘ destination vừa lấy ...
    $offset += $limit;                                // luôn cộng thêm, không reset về 0
}
```

問題：1ページの処理が終わると、そのページ内の**すべての**destinationはステータスが（`SCHEDULED` から）変わるか、`schedule` が**現在の1分間の枠の外**へ変わる ― つまり、それらは**もはやWHEREの条件に一致しなくなる**。条件に一致する結果集合は処理し終えた行数のぶんだけ縮むが、`$offset` は次のループのために `500` 加算されたままである ― 詳細は⚠️②を参照。

---

### ⚠️ 旧システムの異常点

**① パラメータ `send_time` が効果を持たない ― パラメータの種別を誤って宣言しているため。** `buildOptionParser` は `send_time` を**option**としてのみ宣言している（`->addOption('send_time')`、[:45-47](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/DispatchPushMessagesCommand.php#L45-L47)）が、`execute()` は `$args->getArgument('send_time')` によって読み取っている ― これは**argument**（位置パラメータ）を読み取る関数であり、optionではない（[:55](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/DispatchPushMessagesCommand.php#L55)）。`addArgument('send_time')` はどこにも宣言されていないため、`getArgument('send_time')` は常に `null` を返す ― `$now` を上書きする分岐は**決して実行されず**、`--send_time=...` を渡したかどうかにかかわらず、バッチは常に実システム時刻に従って処理する。`DistributeMonthlyEcoPointsCommand`（`--datetime`）で見られたものと同じ型の「テスト用パラメータが機能しない」不具合である。

**② 1分間に500件を超えるdestinationがある場合、offsetによるページングが通知を恒久的に取りこぼしうる。** 1ページの処理が終わるたびに、そのページ内の**すべての**destinationが条件に一致する結果集合から消える（statusが変わるか、`schedule` が1分間の枠の外へ移る）一方で、`offset` はループごとに500ずつ加算されるため ― 次のクエリは、縮んだ集合における「本当の次のページ」にあたる行をちょうどその分だけ**スキップ**してしまう。条件に一致するdestinationが1200件、limitが500の場合の具体例：
  - 1回目（`offset=0`）：先頭の500行を処理する → その500行すべてが条件に一致する集合から外れる。未処理の行は700行残る。
  - 2回目（`offset=500`）：700行に減った集合に対して、offset 500は先頭の500行（まさに処理すべき500行）をスキップし、末尾の200行のみを取得する → 処理を終えた時点で、**一度もクエリされていない500行**が残る。
  - 3回目（`offset=1000`）：集合には500行しか残っておらず、offset 1000はそれを超える → 空が返る → ループが停止する。
  - **結果：500件のdestinationは `SCHEDULED` のまま、`schedule` は既に過去（処理済みの分）となって残る ― 以降の実行（新しい分の枠）では、この `schedule` に二度と一致しない**（条件は `schedule` が*現在*の分の枠に入ることであり、古い `schedule` は既に過去へ流れているため）。したがってそれらの通知は**決して送信されず**、どこにもエラーとして現れない。
  - 1分間に同時に送信すべきdestinationが500件を超える場合にのみ発生する（例：多数のミッション／broadcastの発行時刻が重なる場合）。

---

## 出典

| 内容 | 根拠 |
|---|---|
| バッチのメインロジック | `sources/conciergesv-develop/src/Command/DispatchPushMessagesCommand.php` |
| cronスケジュール（毎分） | `docs/02_詳細設計/10_バッチ処理/mng-webap_cron設定_20241029.txt:80` |
| リトライのパラメータ（`maxFailureCount`, `retryIntervalMinutes`） | `sources/conciergesv-develop/config/push_message.php` |
| `PushMessageDestination` のEntity＋ステータス／リトライ | `sources/eminel_sv_lib-develop/src/Model/Entity/PushMessageDestination.php` |
| `PushMessage` のEntity＋構造（`data.kind`） | `sources/eminel_sv_lib-develop/src/Model/Entity/PushMessage.php`, `src/Model/Table/PushMessagesTable.php` |
| `PushCore` 経由で実際に送信するService | `sources/eminel_sv_lib-develop/src/StaticServices/PushMessageService.php` |
