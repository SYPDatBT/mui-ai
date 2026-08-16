# 現行システム — EMINEL-smart（Push通知送信）

## 概要

これまでに調査した3つのバッチ（`DistributeMonthlyEcoPointsCommand`、`PublishRegularEcoMissionsCommand`、およびXzilla系のバッチ）とは異なり — 本件については**EMINEL-smartにPush通知を送信する完全な仕組みが既に存在し**、Firebase Admin SDKを直接呼び出す（旧システムの `PushCore` のような中間サービスを経由しない）。アーキテクチャが根本的に異なる：旧システムには**共通の送信スケジュールテーブル**（`PushMessageDestinations`）と、そのテーブルをスキャンする**毎分実行のdispatcher**が1つある；新システムには**共通のスケジュールテーブル／dispatcherが存在しない** — コンテンツ種別ごと（Tip/News/Survey/DR）に独自のstate machineが動作し、配信対象の一覧を組み立てたうえで**即座に**送信を呼び出す。固定スケジュールによるpollingは行わない。

## 関連するバッチ／関数名とコード上の位置

| 関数／Lambda | 場所（`src/functions/`） | 役割 |
|---|---|---|
| `batch-push-notice` | `batch-push-notice/app.ts` | 1つの配信対象セグメント（S3から取得、preprocessingがあらかじめ作成したもの）を受け取り、ユーザーごとに送信を呼び出す |
| `pushNoticeToUser` | `src/layers/common/nodejs/services/push-notice-to-user.ts` | ユーザーの**種別ごとの通知ON/OFFフラグ**（`TARGET_SCREEN_PUSH_NOTICE`）を確認し、モバイルトークンをすべて取得し（1ユーザーにつき複数端末）、最大100リクエストを同時並列で送信する（`p-limit`） |
| `pushNotificationFirebase` / `getFirebaseAdmin` | `src/layers/common/nodejs/services/push-notification-firebase.ts` | `firebaseAdmin.messaging().send()` を直接呼び出す — 1トークンにつき1リクエスト；FCMのバイト数上限を超える場合は内容を自動的に切り詰める；FCMがトークンを無効／期限切れと返した場合はDBからトークンを削除する |
| `batch-push-notice-tip-new-preprocessing` / `-dr-*-preprocessing` / `-news-new-preprocessing` / `-survey-new-preprocessing` | `batch-push-notice-*-preprocessing/app.ts` | コンテンツ種別ごとに配信対象の一覧を組み立て、セグメントに分割してS3へ出力し、`BatchPushNoticeMap` を起動する |

**制御を担うstate machine**（例：`batch-push-notice-tip-new.asl.json`）：セグメントごとに `Preprocessing → Map (MaxConcurrency=5, DISTRIBUTED) → BatchPushNotice` となる。state machine内に「Retry」のステップは宣言されておらず、Lambdaのコードもエラーをログ出力する（`logErrorBatch`）のみでスキップする — 旧システムのように再送信のスケジュールを自ら設定し直すことはない。

## 全体像

| 項目 | 内容 |
|---|---|
| **役割** | コンテンツ種別ごと（Tip/News/Survey/DR…）に、Firebase経由で実際のPush通知を送信する。種別ごとのON/OFFフラグの確認と、無効なトークンの整理を行う。 |
| **Input** | S3上にあらかじめ組み立てられた配信対象の一覧＋コンテンツ（コンテンツ種別ごとのpreprocessingが作成）＋ `TABLE_MOBILE_TOKEN_MANAGEMENT`（ユーザー単位のトークン、複数端末）＋ `TABLE_USER_SETTING`（`target_screen` 単位の通知ON/OFFフラグ：Tip/Survey/News/DR／機器エラー／見守り／熱中症警報 — Tip/Survey/News/DRは1つのフラグ `flag_push_notice_tab_notifications` を共用し、合計4フラグであり、D03の「ESTAは4フラグ」と一致する；細分化の単位は仕様詳細の領分である）。 |
| **Output** | Firebase Admin SDKを呼び出し、トークンごとにメッセージを送信する；トークンが無効な場合は `TABLE_MOBILE_TOKEN_MANAGEMENT` から削除する。`PushMessageDestinations` のような送信状態のテーブル（成功／失敗／試行回数）は**存在しない** — 成否はログにのみ現れる。 |
| **処理概要** | 1. コンテンツ種別ごと（Tip/News/Survey/DR）に独自のstate machineを持つ：preprocessingが配信対象の一覧を組み立てる → セグメントに分割する → `batch-push-notice` を並列で呼び出す。<br>2. セグメント内の各ユーザーについて：コンテンツ種別ごとのON/OFFフラグを確認し、OFFであればスキップする。<br>3. ユーザーの全トークンを取得し、トークンごとにFirebaseへ直接送信する。同時リクエストはLambdaインスタンス（セグメント）ごとに100件までに制限される；Mapの `MaxConcurrency=5` により、1つのstate machineでは最大5×100件の同時リクエストとなり得る。<br>4. トークンごとのエラー：トークンの期限切れ／無効が原因の場合 → トークンを削除する；それ以外のエラー → ログ出力のみで、**リトライは行わない**。 |

### `DispatchPushMessagesCommand`（旧システム）との簡易比較

| | 旧システム | 新システム |
|---|---|---|
| 実際の送信箇所 | 内部サービス `PushCore` を経由する（HTTP） | Firebase Admin SDKを直接呼び出す |
| トリガーの仕組み | 共通のdispatcherが1つあり、スケジュールテーブル（`PushMessageDestinations`）を毎分pollingする — 直接送信する例外（`TerminateOutdatedDeviceControlJobsCommand`、hemssvの `dev_ctrl`）を除く | コンテンツ種別ごとに、preprocessingが完了した時点で即座にトリガーされる（固定スケジュールによるpollingは行わない） |
| 送信失敗時のリトライ | あり — 最大5回、3分間隔、送信先ごとに状態を保存する | **なし** — エラーはログ出力のみで、再送信しない |
| 通知種別ごとのON/OFF | dispatcherには存在しない；発信側では、旧システムはみまもり種別のON/OFFを持つ（`ConMotionSensorNotificationSettings`） — 他の種別は見当たらない | **あり** — `TABLE_USER_SETTING` の `target_screen` 単位 |
| 無効トークンの整理 | 見当たらない | **あり** — Firebaseが無効と返した時点でトークンを自動的に削除する |
| 1ユーザーあたり複数端末 | あり（`ems_sp` 単位の `push_device_token`） | あり（`user_id` 単位の `TABLE_MOBILE_TOKEN_MANAGEMENT`） |

---

## 出典

| 内容 | 根拠 |
|---|---|
| 送信のメインLambda | `syp-eminelstandard-backend-main/src/functions/batch-push-notice/app.ts` |
| ユーザーの選定、ON/OFFフラグの確認、複数端末対応のロジック | `syp-eminelstandard-backend-main/src/layers/common/nodejs/services/push-notice-to-user.ts` |
| Firebase Admin SDKの呼び出し＋無効トークンの整理 | `syp-eminelstandard-backend-main/src/layers/common/nodejs/services/push-notification-firebase.ts` |
| 制御を担うstate machine（例：Tip） | `syp-eminelstandard-backend-main/src/statemachine/batch-push-notice-tip-new.asl.json` |
| E-GW側の対応する要件 | `eminel_gw_project-main/docs/eminel/3_requirements/app/D03_push.md`（受信の制御 — 種別ごとのON/OFF、新システムに既にある仕組みと完全に一致する）、`00_integrated_requirements_v1.2.md` — `[F-AD-07] Push通知管理` |
