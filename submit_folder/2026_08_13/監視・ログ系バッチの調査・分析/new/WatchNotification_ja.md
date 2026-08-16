# WatchNotificationCommand（見守り通知機能）

## 概要

`WatchNotificationCommand` は、旧システム（`conciergesv`、`mng-webap` グループ）において1時間に6回（10分ごと、7分ずらし）実行されるバッチである：「見守り通知」を登録している各世帯について、`s_101` にあらかじめ算出済みの10分単位の人感センサーデータ（`CalcTenMinutesSensorCommand` が10分ごとに生成する）を読み取り、その世帯の設定に応じて**2種類の異なる判定アルゴリズムのうち1つ**（見守り①「ただいま通知/お留守番代行」または継続的に監視する見守り②「見守り通知」）を適用して5つの状態のうち1つ（対象外／在室／不在／データなし／継続的データ欠損）を決定し、対応するPush notification＋「お知らせ」（message）をアプリが読み取れるように書き込む。`syp-eminelstandard-backend`（EMINEL-smart）には、**同等の部分が1つ存在するが大幅に簡略化されている**：「お部屋みまもり」（room monitor）機能は、MUIのIoTセンサーが `motion=1` を報告した際にリアルタイムでpushする ― 10分の枠でpollingすることはなく、設定に応じた2種類の個別のアルゴリズムもなく、旧システムの「不在」／「データなし」／「継続的データ欠損」の部分に**相当するものは見つからなかった**。

---

# 第A部 ― 旧システム

## A.1 全体概要

| 項目 | 内容 |
|---|---|
| **バッチ名** | クラス：`WatchNotificationCommand`・cronスクリプト：`3_WatchNotification.sh`・cron上の日本語名：`3.見守り通知機能`。 |
| **役割** | 「見守り通知」を登録している各世帯の10分単位に集計済みの人感センサー（PIR）データを監視し、その世帯に設定された2種類のアルゴリズムのうち1つに従って「在室／不在／データなし／継続的データ欠損」を判定し、通知を発信する。 |
| **入力** | 4つの業務テーブルから読み取る：`t_901`（設定＋前回の通知履歴）＋ `t_101`（世帯リスト）＋ `t_201`（登録済み機器、人感センサーで絞り込み）＋ `s_101`（10分単位のPIRデータ、`CalcTenMinutesSensorCommand` が事前に生成）、加えてテンプレートテーブル `con_regular_messages`（6件の通知テンプレート、id `1`～`6`、結果を書き込むステップで読み取る）。CSV／ファイルの読み込みはなく、外部APIの呼び出しもない。 |
| **出力** | 4つのテーブルへInsertする：`push_messages`/`push_message_destinations`（エンティティ `PushMessage`、Push notification）＋ `con_messages`/`con_message_destinations`（エンティティ `ConMessage`、アプリ内の「お知らせ」）― ただし `saveOrFail` が `foreach` の外に置かれているため、状態パターン（101/102/103/104）ごとにリストの最後の世帯の1組しか保存されない（旧システムのバグの疑い ― §A.2.7 の観察を参照）。`t_901`（前回の通知時刻）のUpdateは、判定対象となったすべての世帯について実行される。 |
| **処理概要** | 1. 2種類の「見守り通知」設定のうち少なくとも1つが有効な世帯の一覧を取得する。<br>2. 各世帯について、有効な設定から監視時間帯（start/end）を取得する。<br>3. 登録済みの人感センサー機器の台数を取得する（1台または2台以上）。<br>4. 「継続的データ欠損」を判定する ― 該当する場合はこの状態の処理を優先し、他の判定ステップを行わない。<br>5. 該当しない場合、有効になっている設定に応じて2種類のアルゴリズム（見守り①または②）のうち1つを実行し、5つの状態のうち1つを得る。<br>6. 「対象外」以外の各状態について、対応するPush＋「お知らせ」（固定の6テンプレートのうち1つ）を書き込む。<br>7. ステップ6で判定対象となったすべての世帯について `t_901.c006`（前回の通知時刻）をUpdateする。 |

## A.2 詳細

### 算出方法のマップ ― 7ステップ

```
ステップ1  監視対象世帯の取得    → 2種類の設定のうち1つ以上が有効、論理削除されていない世帯  §A.2.3
ステップ2  監視時間帯            → 両方が有効な場合は start_time が早い方の設定を選ぶ        §A.2.3
ステップ3  センサー機器数        → 登録済みのPIR機器を数える（t_201）                        §A.2.3
ステップ4  継続的データ欠損      → 2種類のアルゴリズムより優先、該当すれば処理を終了         §A.2.4
ステップ5  見守り①アルゴリズム  → 「ただいま通知/お留守番代行」（c003_01 が有効な場合）     §A.2.5
ステップ5' 見守り②アルゴリズム  → 「見守り通知」継続的な監視（c003_02 が有効な場合）        §A.2.6
ステップ6  通知の書き込み        → 固定の6テンプレートのうち1つで Push＋お知らせ             §A.2.7
ステップ7  t_901 のUpdate        → 通知時刻（c006）＋ modified を記録                        §A.2.7
```

### A.2.1 実行スケジュールとパラメータ

| 項目 | 内容 | 出典 |
|---|---|---|
| 実行スケジュール（cron） | `7,17,27,37,47,57 * * * *` ― 1時間に6回、10分ごと、7分ずらし（`2,12,...` 分に実行される `CalcTenMinutesSensorCommand` の**5分後**に実行され、`s_101` に新しいデータが揃うだけの時間を確保している） | `docs/02_詳細設計/10_バッチ処理/mng-webap_cron設定_20241029.txt:8-10` |
| 実行コマンド | `php cake.php WatchNotification [--datetime=<判定日>]` | `WatchNotificationCommand.php:57-62` |
| **判定日** の基準（パラメータ未指定時） | `現在時刻 − 20分`、その後10分単位に切り下げる | `WatchNotificationCommand.php:917-936` |
| 渡されたパラメータのバリデーション | 正規表現により `yyyy-MM-ddTHH:mm:00+09:00` の形式へ厳密に一致することを必須とする；形式が不正な場合→`abort`（`alert` ログ付き） | `WatchNotificationCommand.php:79-83,917-930` |

### A.2.2 データソース ― 関連する4テーブル

| テーブル | カラム | 意味 | 確度 |
|---|---|---|---|
| `t_901`（`ConMotionSensorNotificationSettings`） | `c001` | EMS-SP | **確実** ― エンティティ内の定数 `C_EMS_SP` |
| `t_901` | `c002` | 設定の種別：`1`=`NOTIFICATION_TYPE_WHEN_DETECTED`（見守り①）, `2`=`NOTIFICATION_TYPE_WHEN_UNDETECTED`（見守り②） | **確実** ― エンティティの定数であり、コードでの `MOTION_DETECTION_NOTIFICATION_1/_2` の使い方と一致する |
| `t_901` | `c003` | 設定の有効／無効フラグ（0/1） | **確実** ― `C_ENABLE_FLAG` |
| `t_901` | `c004` / `c005` | 監視の開始時刻／終了時刻 | **確実** ― `C_START_TIME`/`C_END_TIME` |
| `t_901` | `c006` | 前回の通知時刻 | **確実** ― `C_BEFORE_NOTICED`、送信後にバッチ自身がUpdateする |
| `t_901` | `c007` | 設定の変更時刻 | **確実** ― `C_MODIFIED` |
| `t_201`（`ConDevices`、登録機器） | `c007` | ECHONETクラスコード（`class_eoj`）、`'001101'` = 人感センサーで絞り込み | **確実** ― エンティティ `ConDevice` 内の定数 `C_CLASS_EOJ` |
| `t_201` | `c017` | メーカーコード（`dev_maker_code`）、`'0000E3'` で絞り込み | **確実** ― `C_DEV_MAKER_CODE` |
| `t_201` | `c035` | 論理削除の時刻、`IS NULL` = 有効 | **確実** ― `C_DELETED` |
| `s_101`（`ConSensorMemoryValue`、バッチ `CalcTenMinutesSensorCommand` も参照） | `c001`/`c002`/`c003`/`c004`/`c006` | EMS-SP / device_type（`DETECT_CNT`=14）/ room_id（`DETECT_LIVING`=0, `DETECT_OTHER`=1）/ 10分の基準時刻 / 検知回数 | **確実** ― 同じテーブルであり、バッチ `CalcTenMinutesSensorCommand` で確認済みの同じ定数 |

### A.2.3 判定対象世帯と監視時間帯の特定

1. `getWatchTargetEmsp()` ― 複雑なSQL（`WatchNotificationCommand.php:835-909`）により、`t_901` の2種類の設定のうち少なくとも1つが**判定時点で監視時間帯の中にあり**（`unixTime` を `c004`/`c005` と比較し、日をまたぐケースにも対応する）、かつ**現在の時間帯でまだ通知されていない**（`c006 IS NULL` または `c006` が比較基準より古い）すべての世帯（`t_101`、論理削除されていないもの）を取得する ― 通知の重複を防ぐ仕組みである。留意点：返却される `c005` はSQLによりあらかじめ**10分引かれている**（`notification.c005 - cast('10 minutes' as INTERVAL)`、`:851`、コメント「監視終了時間（10分前）」`:501`）― 判定に用いる終了の基準時刻＝`c005 − 10分` であり、`getMonitoringTime()` を通じて後続のステップへそのまま引き継がれる。
2. `getMonitoringTime()` ― 世帯が2種類の設定をいずれも有効にしている場合は、**開始時刻（`c004`）が早い方の設定**を正式な監視時間帯として選ぶ；1つのみ有効な場合はその設定を用いる。（`WatchNotificationCommand.php:765-795`）
3. `getRegisteredDeviceData()` ― その世帯の有効な登録済み人感センサー機器の台数を数える（機器1台／2台以上の分岐で使用する）。（`WatchNotificationCommand.php:803-828`）

### A.2.4 「継続的データ欠損」の判定（`getContinuousMissingData`）― 最も優先度が高い

- **直近3つの10分枠**（`generate_series(0, CONSECUTIVE_MISSING_VALUES−1=2)` ＝ 判定時刻、−10分、−20分の3つの基準時刻。監視時間帯で切り取る）における**欠損**レコード数（`c006 IS NULL` → 1として数える）の合計を、部屋ごと（`c006Living`、`c006Other`）に取得する。（`WatchNotificationCommand.php:643-677`、定数 `const.php:694`）
- 世帯の機器が2台以上の場合：**2部屋のうち1部屋**がしきい値 `CONSECUTIVE_MISSING_VALUES = 3` に達した時点で継続的データ欠損とする。機器が1台の場合：リビング（`c006living`）のみを対象とする。（`WatchNotificationCommand.php:612-635`）
- **該当する場合→直ちに処理を終了し、この世帯について見守り①／②のアルゴリズムを実行しない** ― 判定フロー全体の中で最も優先度が高いステップである。（`WatchNotificationCommand.php:150-157`）

### A.2.5 見守り①アルゴリズム ― 「ただいま通知／お留守番代行」（`checkMonitoring1`、`c003_01` が有効な場合）

考え方：**10分枠を1つだけ**（判定時刻を含む枠、10分単位に切り下げ）対象とする ― 「直前に人を検知したか？」に答えるものである。

```
判定時刻を含む10分枠における SUM(検知回数)  (SQL s_101、WHERE c004 = 当該枠)

├─ count > 0（レコードあり）かつ sum >= MOTION_DETECTION_COUNT_THRESHOLD(=1)
│     → MOTION_SENSOR (101)「在室」
│
├─ count > 0 かつ 判定時刻（10分単位に丸め）== 判定の終了基準時刻（= c005 − 10分、分単位ちょうど）
│     ├─ sum が NULL でない（レコードはあるが = 0）→ NO_MOTION_SENSOR (102)「不在」
│     └─ sum = NULL（レコードが1件もない）        → NO_DATA (103)「データなし」（INFOログ付き）
│
└─ それ以外の場合 → NOT_APPLICABLE (100)「対象外」、通知しない
```
出典：`WatchNotificationCommand.php:373-427,491-528`、定数 `const.php:702,708-716`。

**注意点**：「不在」／「データなし」の分岐は、**判定の終了基準時刻 = `c005 − 10分` ちょうどにおいてのみ判定される**（設定の終了時刻の10分前の枠。§A.2.3 参照）― 途中の枠では「在室」または「対象外」しか出ず、時間帯の途中で「不在」を通知することはない。

### A.2.6 見守り②アルゴリズム ― 「見守り通知」継続的な監視（`checkMonitoring2`、`c003_02` が有効な場合）

考え方：**判定時刻に近い最大3つの10分枠**（直近30分、監視時間帯で切り取る ― §A.2.4 と同じ `generate_series` の仕組みであり、モードのみが異なる；`SENSOR_NOTIFY_JUDGMENT_FRAME_NUMBER = 3`）を対象とし、単発の測定による誤報を避ける。

```
monitorFrameNum = (判定の終了基準時刻（c005 − 10分） − 監視の開始時刻) / 10分
frameNum        = MIN(SENSOR_NOTIFY_JUDGMENT_FRAME_NUMBER=3, monitorFrameNum)
count           = 判定時刻/−10分/−20分 の3つの基準時刻で取得できたレコード数（≤3、監視時間帯で切り取る）

├─ count < frameNum  → NOT_APPLICABLE (100)「判定するにはデータが足りない」
│
└─ count >= frameNum（かつ count > 0）
      │
      ├─ 測定の合計（c006、2部屋分の和） >= SENSOR_NOTIFY_NUMBER_2(=1) のレコードが1件以上ある
      │     ├─ 判定の終了基準時刻（c005 − 10分）ちょうど → MOTION_SENSOR (101)「在室」
      │     └─ それ以外の枠                            → NOT_APPLICABLE (100)（時間帯の途中での通知を抑止）
      │
      ├─ （上の分岐に該当しない）c006 < 0 のレコードが1件以上ある（レコードのない枠に対しSQLが自動で −1 を割り当てる ― データが空の枠）
      │     → MISSING_DATA (104)「継続的データ欠損」
      │
      └─ 上のいずれの分岐にも一致しない → NO_MOTION_SENSOR (102)「不在」
```
出典：`WatchNotificationCommand.php:373-427`、定数 `const.php:704,706`。

**備考**：`checkMonitoring2` 内の変数 `$resultCode` には「未確定」の値として `0` が代入され、`if ($resultCode != 0)` で比較される ― しかし `0` は5つの有効な状態定数（100-104）の**いずれでもなく**、内部的なsentinelにすぎない。`foreach` ループの結果はSQLが返す順序に依存しない：判定の終了基準時刻ちょうどでしきい値に達したレコードが1件以上あれば → 101（guardなしで代入される）；しきい値に達したレコードが時間帯の途中にしかない場合 → 100（`if ($resultCode === 0)` の分岐は、既に代入された101を上書きできない）。（`WatchNotificationCommand.php:397-415`）

### A.2.7 結果の書き込み ― `PushMessage` ＋ `ConMessage`（「お知らせ」）＋ `t_901` のUpdate

- 6件の固定の通知テンプレート（`ConRegularMessages`、id `'1'`～`'6'`）― **実際のタイトル／messageの内容は読み取れない**（データはDB内にあり、ソースコード内のseedではない）― `updateEcoMission()` 内の `switch` により、どのidがどの状態に対応するかのみが分かる：

  | id | 条件 | コードから推し量られる意味 |
  |---|---|---|
  | `1` | `MOTION_SENSOR`（見守り①、1部屋の設定が有効） | *(推測)*「在室」― 見守り①の文脈 |
  | `2` | `NO_MOTION_SENSOR`、見守り① | *(推測)*「不在」― 見守り① |
  | `3` | `MOTION_SENSOR`、見守り②（または1以外の設定） | *(推測)*「在室」― 見守り② |
  | `4` | `NO_MOTION_SENSOR`、見守り② | *(推測)*「不在」― 見守り② |
  | `5` | `NO_DATA`（見守り①からのみ） | *(推測)*「データなし」 |
  | `6` | `MISSING_DATA` ― §A.2.4 から（すべての世帯、設定①・②のいずれも）、または②のデータが空の枠の分岐（§A.2.6） | *(推測)*「継続的データ欠損」 |

  （`WatchNotificationCommand.php:223-252`）
- 2種類のレコードを並行して書き込む：`PushMessage`（kind `DATA_KIND_MOTION_ALARM = 'motion_alarm'`、`eminel_sv_lib/.../PushMessage.php:36`）と `ConMessage`（配信範囲 `DISTRIBUTE_SCOPE_EMS_SP = 'EMS_SP'` ― 1世帯を名指しで送るものであり、broadcastではない、`.../ConMessage.php:33`）。（`WatchNotificationCommand.php:257-280`）
- **観察（旧システムのバグの疑い）**：2つの `saveOrFail` はいずれも `foreach` の**外**にある（`:281` の閉じ括弧の後）― 状態パターンごとに**リストの最後の世帯**のPush＋messageの1組しか保存されず、それ以前の世帯のエンティティは変数の上書きにより失われる；保存時のエラーは例外を捕捉し、通常のログ（`alert` ではない）を出力して `$resultCode = false` をセットする。（`WatchNotificationCommand.php:228-291`）
- 保存に成功した後 → パターンのリストにある**すべての**世帯について `t_901.c006`（`setBeforeNoticed`）＋ `c007`（`setModified`）をUpdateする ― 上記でPush/messageが保存されなかった世帯も「通知済み」として記録される ― Updateのエラーは `alert` ログを出力する（上記のPush/Messageの書き込みエラーとは異なり、深刻度が高い）。（`WatchNotificationCommand.php:294-296,307-333`）

### A.2.8 特記事項／リスク

- 本バッチは、深刻なエラー（`checkValidate` の失敗、SQLのエラー、`t_901` のUpdateのエラー）が発生した際に `alert` レベルのログを出力する `conciergesv` 内の多数のCommandの1つである（PSR-3の定数 `LogLevel::ALERT` を使用しており、`SendAlertLogMailCommand` が走査する文字列 `'alert'` に相当する ― 詳細はそちらを参照）。本バッチも当該バッチにとっての**アラート発生源のリストに含まれる**が、これまで `WatchNotification` に列挙されていたリストは十分に検証されたことがなかった ― 改めてgrepしたところ、`alert` ログの仕組みの実際の範囲は、以前に列挙されていた8ファイルよりもはるかに広いことが分かった（更新内容は `SendAlertLogMail.md` を参照）。
- 先に（5分ずらして）実行される `CalcTenMinutesSensorCommand` に直接依存する ― 当該バッチがエラー／遅延した場合、`s_101` に新しいデータがなく、`WatchNotificationCommand` は古いデータまたは不足したデータに基づいて判定することになり、「データなし」／「継続的データ欠損」の分岐へ誤って（false positive）陥りやすい。
  - 見守り②はさらに、先に実行され優先度がより高い `getContinuousMissingData`（§A.2.4）へ間接的に依存する ― 観察：「データ欠損」を通知する2つの仕組みが、しきい値を異にしたまま同じ1つのバッチの中で設計上重複している（§A.2.4 は3枠中3枠の欠損を必要とする；②のデータが空の枠の分岐 §A.2.6 は1枠の欠損のみで足りる）。
- バッチ全体のトランザクションはない ― ある世帯の書き込みのエラーが他の世帯に影響することはないが、1回の実行で合計何世帯がエラーになったのかを知る手段もない（世帯ごとの断片的なログしかない）。

---

# 第B部 ― EMINEL-smart（新システム）との対照

## B.1 バッチ名とコード上の位置

| バッチ／仕組み | 位置（Lambda） | State Machine／trigger | データソース | 出力先 |
|---|---|---|---|---|
| IoTセンサーのイベントの受信＋push対象世帯の特定 | `src/functions/batch-receive-data-infrared-remote/app.ts` | `BatchReceiveDataInfraredRemoteStateMachine`（`src/statemachine/batch-receive-data-infrared-remote.asl.json`）― **IoTセンサーのイベントによるリアルタイムのtrigger**（payload `event: SENSOR_AUTO_REPORT`/`EXECUTE_AUTOMATION`）であり、cronではない | MUIのIoTセンサーからの直接のイベント（`payload.motion`, `payload.wbgt`, `payload.temperature`）＋ `TABLE_KAIIN`（GSI `gsi_house_id` ― イベントの `houseID` を `kaiin_bango` の一覧へ変換する、`app.ts:280-293`） | 履歴を `TABLE_INFRARED_REMOTE_DATA` へ書き込む；push対象世帯の一覧を一時的なS3経由で渡す（`createDataSegment`） |
| 「room monitor」pushの送信（＋スケジュールがある場合は機器の制御） | `src/functions/batch-control-device-and-push-notice-sensor/app.ts` | 同じstate machineの中で、上のステップの直後にある `Map`（DISTRIBUTED）ステップ | S3からsegmentを読み直す；`TABLE_USER_SETTING`（フラグ `flag_push_notice_room_monitor`）＋ `TABLE_MOBILE_TOKEN_MANAGEMENT`（モバイル端末のトークン、`app.ts:261-274`）を読み取る | `pushNotificationFirebase()` ― Firebase経由でモバイル端末へ直接pushする。`ConMessage` に相当する「message」／アプリ内inboxのテーブルへは書き込まない |

| 項目 | 内容 |
|---|---|
| triggerの方式 | MUIのIoTセンサーが `motion` をリアルタイムに報告するイベント駆動 ― **旧システムのようなcron pollingのバッチではない**（`s_101` に相当するものがなく、10分の枠もない）。 |
| ユーザーのopt-inフラグ | `UserSetting` 内の `flag_push_notice_room_monitor` ― アカウントの作成／リセット時のデフォルトは `true`（`batch-if2241-import-tagtag-kaiin/app.ts:218`, `authorizer/app.ts:112`, `batch-reset-account/app.ts:189`）であり、API `api-user/update-user-setting.ts` から変更する。役割としては `t_901` の有効／無効フラグ `c003` に相当するが、**共通のフラグが1つ**あるのみで、旧システムのような2つの時間帯設定は持たない。 |

## B.2 全体概要

| 項目 | 内容 |
|---|---|
| **役割** | MUIのIoTセンサーがauto-reportのイベントで動きの検知（`motion === 1`）を報告した際に、その世帯へ「部屋で活動あり」のpush notificationを直ちに送る（フラグが有効な場合）。 |
| **入力** | IoTセンサーから直接送られるイベント `SENSOR_AUTO_REPORT`/`EXECUTE_AUTOMATION`（`s_101` のような中間のDBテーブルを経由しない）。起動の条件：`payload.motion === 1`（`batch-receive-data-infrared-remote/app.ts:222`）。 |
| **出力** | Firebase push、固定のタイトル `"お部屋みまもり"`、固定の本文 `"お部屋での活動を検知しました。"`（`batch-control-device-and-push-notice-sensor/app.ts:110-113`）― **`ConMessage` に相当する「お知らせ」／アプリ内inboxのレコードはなく**、重複を防ぐための「前回の通知」を保存するフィールドも見当たらない（**同一ファイル内**の熱中症／heat-strokeの分岐には throttle `HEAT_STROKE_NOTICE_INTERVAL_MS = 29分` がある（`:35,71-73`）のとは異なり ― room-monitorの分岐には同様のthrottleがない）。 |
| **処理概要** | 1. IoTセンサーが `motion`／`wbgt`／`temperature` のイベントをリアルタイムに送る。<br>2. Lambdaがイベントを受け取り、`motion === 1` であれば → push対象の世帯として `has_push_notice_room_monitor` を立てる。<br>3. 世帯の一覧をsegmentに分割し、Step FunctionsのMap（distributed）へ渡す。<br>4. Lambdaが各segmentを処理する：ユーザーのフラグ `flag_push_notice_room_monitor` を確認し、有効であれば → モバイル端末のトークンを取得し、直ちにFirebase pushを送信する。 |

**旧システムとの本質的な相違**（単に「アーキテクチャが異なる」と一般論を述べるのではなく、双方のfile:lineの根拠が揃っている）：

| 観点 | 旧（`WatchNotificationCommand`） | 新（`batch-receive-data-infrared-remote` ＋ `batch-control-device-and-push-notice-sensor`） |
|---|---|---|
| triggerの仕組み | 10分ごとのcronで、事前に集計済みの `s_101` をpollingする | イベント駆動のリアルタイムであり、センサーのpayloadから直接、中間の集計テーブルを経由しない |
| センサーのハードウェア | HEMS-GW経由のECHONET標準のPIR（`t_201.c007='001101'`） | MUI独自のセンサー（同一の機器に温度／湿度／WBGTを含む） |
| アルゴリズムの種類数 | 2種類（見守り①／②、時間帯＋枠ごとのしきい値、世帯単位の設定） | 1種類（`motion === 1` という単純なboolean、時間帯なし、枠数のしきい値なし） |
| 「不在」の状態 | あり（`NO_MOTION_SENSOR`、message id 2/4） | **見つからない** |
| 「データなし」の状態 | あり（`NO_DATA`、message id 5） | **見つからない** |
| 「継続的データ欠損」の状態 | あり、2つの発生源（§A.2.4 ＋ データが空の枠の分岐 §A.2.6、message id 6） | **見つからない** |
| 通知の重複防止 | あり ― `t_901.c006` をUpdateし、次回の実行で再度用いる | room-monitor向けのthrottleの仕組みが**見つからない**（同一ファイル内で `HEAT_STROKE_NOTICE_INTERVAL_MS` を持つheat-strokeの分岐とは異なる）― *(推測：`motion=1` のたびに再び通知される可能性がある。他の層 ― 例えばFirebaseのclient側、あるいはセンサーの本来の報告頻度の低さ ― に制限があるかどうかは未検証であり、読んだソースの範囲外である)* |
| アプリ内の「お知らせ」レコード | あり（`ConMessage`） | 見つからない ― pushのみであり、アプリのinboxに相当する項目はない |

---

## まとめ

**旧システムの2種類のアルゴリズムは、判定する時間の範囲が異なるのであり、同じ1つの用途に対する2通りの計算方法ではない：**

- **見守り①** ― 判定時刻における**10分枠を1つ**のみを対象とし、「不在」／「データなし」は**監視時間帯の終了時点ちょうど**にのみ通知する。「約束の時刻になったので1回確認する」という状況に適する（例：ただいま通知、あるいはお留守番代行）。
- **見守り②** ― 結論を出す前に、**判定時刻に近い最大3つの10分枠**（直近30分、監視時間帯で切り取る；frameNum = MIN(3, ウィンドウの枠数)）を対象とし、1回の測定の取りこぼしによる誤報を避ける。長時間にわたる継続的な見守りの状況に適する（例：高齢者を半日にわたり見守る）。
- 世帯が「より適した方」を自ら選ぶわけではない ― コードは固定の優先順位を持つ：**スイッチ①（`c003_01`）が有効であれば、スイッチ②に関わらず常に①を実行する**；②は①が無効な場合にのみ実行される。（`dataAssignment()`、if/elseif ― `WatchNotificationCommand.php:343-364`）

**新システムは2種類のアルゴリズムのいずれかを簡略化したものではなく、はるかに単純な別の仕組みへ完全に置き換えたものである：**

- 「動きがあれば直ちに通知する」部分だけを残している（センサーが `motion=1` を報告 → リアルタイムでpush）。
- 完全に廃止された部分：監視時間帯（start/end）、②の3枠のしきい値、そして「不在」／「データなし」／「継続的データ欠損」の3状態 ― 新システムでこれらを再現する必要があるか否かは、依然として未決の保留事項である（CLD-05）。
- 何度も繰り返し通知することを防ぐ仕組みがない（通知後に必ず `t_901.c006` をUpdateする旧システムとは異なる）。
- トレードオフ：複雑な判定ロジックが失われる一方で、10分のcron周期を待つのではなくリアルタイムの応答が得られる。

---

## 出典

| 区分 | 内容 | 根拠 |
|---|---|---|
| 旧システム | メインロジック | `sources/conciergesv-develop/src/Command/WatchNotificationCommand.php` |
| 旧システム | 業務定数 | `sources/conciergesv-develop/config/const.php:198,228,230,694,696,698,700,702,704,706,708,710,712,714,716` |
| 旧システム | `t_901` のカラムの意味 | `sources/eminel_sv_lib-develop/src/Model/Entity/ConMotionSensorNotificationSetting.php` |
| 旧システム | `t_201` のカラムの意味 | `sources/eminel_sv_lib-develop/src/Model/Entity/ConDevice.php` |
| 旧システム | `PushMessage`/`ConMessage` の定数 | `sources/eminel_sv_lib-develop/src/Model/Entity/PushMessage.php:36`, `.../ConMessage.php:33` |
| 旧システム | 実行スケジュール（cron） | `docs/02_詳細設計/10_バッチ処理/mng-webap_cron設定_20241029.txt:8-10` |
| 新システム | センサーのイベントの受信＋segmentの分割 | `src/functions/batch-receive-data-infrared-remote/app.ts` |
| 新システム | room-monitor＋heat-strokeのpush | `src/functions/batch-control-device-and-push-notice-sensor/app.ts` |
| 新システム | Orchestrator | `src/statemachine/batch-receive-data-infrared-remote.asl.json` |
| 新システム | opt-inフラグと更新のフロー | `src/functions/api-user/update-user-setting.ts`, `src/layers/common/nodejs/models/UserSetting.ts` |
