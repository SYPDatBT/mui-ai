# batch_decision（Markdown版）

> Bản Markdown convert máy móc 1-1 từ `batch_decision.xlsx` cùng thư mục — nội dung giữ nguyên từng ô, không dịch/không sửa. Ngày convert: 2026-08-16 ・ số sheet: 3.

## 1. SendAlertLogMailCommand

| Batch | SendAlertLogMailCommand |
|---|---|
| 旧Eminelシステムの調査結果については、以下のファイルをご参照ください： | SendAlertLogMail.md |
| 調査結果： | 追加で対応する必要はありません。これは、今回のセッションでKita Gas向けに拡張された仕組みそのものです。 |

## 2. WatchNotificationCommand

| Batch | WatchNotificationCommand |
|---|---|
| 旧Eminelシステムの調査結果については、以下のファイルをご参照ください： | WatchNotification.md |
| 調査結果： | 旧システムの2つのアルゴリズムは、同じ処理に対する2つの計算方法ではなく、参照する時間範囲が異なります。<br><br>新システムは、旧システムのどちらか一方を簡略化したものではなく、よりシンプルな別の仕組みに完全に置き換えています。 |

## 3. PutLogFileCommand

| Batch | PutLogFileCommand |
|---|---|
| 旧Eminelシステムの調査結果については、以下のファイルをご参照ください： | PutLogFile.md |
| 調査結果： | Xzilla側でも引き続きアプリログを受け取る必要がある場合は、まずXzillaのパートナー／業務側に確認する必要があります。必要であれば、両方の側で対応する必要があります（ZIPを受け取るAPI ＋ ZIPを解凍・バリデーションし、SFTPで送信するバッチ）。 |
