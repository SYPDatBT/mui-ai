# batch_decision（Markdown版・レビュー確認版）

> **【メンバーの作業】なし — 要修正シートは0件です。本ファイルはレビュー完了の確認用であり、本グループに問題があったという意味ではありません。**

> **REVIEW 16–17/08: NHÓM NÀY KHÔNG CÓ SHEET 要修正** — mọi ô bên dưới **trùng khít bản gốc** `../batch_decision.md` (chỉ khác tiêu đề, 3 ghi chú meta này và phần 付録 cuối file). **Member KHÔNG bắt buộc dán gì vào `batch_decision.xlsx` của nhóm.** File tồn tại để phân biệt rõ "đã review xong, không phải sửa câu" với "chưa review", và để tra verdict tại chỗ khỏi mở `../../review_summary.md` (~1.130 dòng).

> **Verdict 3/3 sheet**: `SendAlertLogMailCommand` **妥当だが根拠不足** — có câu bổ sung đề xuất, **chưa áp** (xem 付録 cuối file) ・ `WatchNotificationCommand` **要業務確認** (**QA-03①**) ・ `PutLogFileCommand` **要業務確認** (**QA-03②**). Câu hỏi QA: `../../../qa/qa_review_20260813_20260817.md` — **CHƯA GỬI**, chờ user chuyển PM mui. Lý do từng verdict + bảng findings: `../../review_summary.md` §3.G5.

> Bản Markdown convert máy móc 1-1 từ `../batch_decision.xlsx` (thư mục nhóm) — nội dung giữ nguyên từng ô, không dịch/không sửa. Ngày convert: 2026-08-16 ・ số sheet: 3.

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

---

## 付録：妥当だが根拠不足のシートに対する補足文【提案・未適用】

> ⚠️ **Đây KHÔNG phải câu đã chốt.** Verdict 妥当だが根拠不足 nghĩa là **kết luận của member đúng nhưng chưa dẫn đủ căn cứ** — theo quy ước đợt review, chỉ sheet 要修正 mới thay câu, nên câu dưới đây **cố ý chưa được áp** vào bảng phía trên. Member tự cân nhắc dùng hay không khi cập nhật xlsx; nếu dùng thì đây là phát ngôn của member trước khách, hãy đọc lại lý do ở `../../review_summary.md` §3.G5 trước khi quyết.

**1. SendAlertLogMailCommand** — câu bổ sung đề xuất (JP, thay cho ô 調査結果：):

> 追加で対応する必要はありません。旧SendAlertLogMailに相当する機能は、新システムでは CloudWatch Logs サブスクリプションフィルタ（78件）＋ push-notification-error-log Lambda ＋ SNS 通知として既に存在しています。さらに、この仕組みは今回のセッションで feat/kitagas-batch-import-error-notification ブランチ（b087399c〜68d7a5fc、2026-08-11〜14）により、日次取込バッチのエラーを Kita Gas 向け SNSトピック（SnsTopicKitaGas）へも通知するよう拡張されています（※本調査時点で gw-syp-dev へは未マージ）。
