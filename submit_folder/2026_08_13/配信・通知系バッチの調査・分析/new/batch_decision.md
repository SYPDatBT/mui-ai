# batch_decision（Markdown版・修正版）

> **【メンバーの作業】xlsx の修正は不要です。current-eminelsmart_DistributeMonthlyEcoPoints.md（＋ _ja 版）の内容を new/ 版に差し替えてください。**

> **BẢN ĐÃ SỬA THEO REVIEW 16–17/08** — nhóm này KHÁC 6 nhóm còn lại: mọi ô của xlsx chỉ trỏ **TÊN FILE** điều tra, không chứa câu phán định; phán định thật nằm trong `current-eminelsmart_*.md`. Vì vậy toàn bộ ô bên dưới **giữ nguyên văn 100%** (tên file vẫn đúng sau khi sửa), câu đã sửa được bổ sung dưới dạng dòng 「レビュー結果」 — **dòng này KHÔNG có trong xlsx**, chỉ để tra cứu/copy. **Hành động của member: thay NỘI DUNG `current-eminelsmart_DistributeMonthlyEcoPoints.md`（＋ bản `_ja`）bằng bản trong `new/` — ô xlsx KHÔNG cần sửa.** Bản gốc trung thực với xlsx: `../batch_decision.md`.

> **Verdict 4/4 sheet**: `DistributeMonthlyEcoPointsCommand` **要修正** (câu sửa ở dòng 「レビュー結果」 của sheet 1; batch này đồng thời có câu hỏi nghiệp vụ **QA-04①**) ・ `PublishRegularEcoMissionsCommand` **妥当だが根拠不足** (không có câu thay thế soạn sẵn — lý do ở `../../review_summary.md` §3.G3) ・ `DispatchPushMessagesCommand` **妥当** (nguyên văn, không đổi) ・ `ControlDrOperationCommand` **要業務確認** (**QA-04②**). Câu hỏi QA: `../../../qa/qa_review_20260813_20260817.md` — **CHƯA GỬI**, chờ user chuyển PM mui.

> Bản Markdown convert máy móc 1-1 từ `../batch_decision.xlsx` (thư mục nhóm) — nội dung convert giữ nguyên từng ô (không dịch); riêng sheet 1 có thêm dòng 「レビュー結果」 theo review, dòng này không tồn tại trong xlsx. Ngày convert: 2026-08-16 ・ số sheet: 4.

## 1. DistributeMonthlyEcoPointsCommand

| Batch | DistributeMonthlyEcoPointsCommand |
|---|---|
| 旧Eminelシステムの調査結果については、以下のファイルをご参照ください： | legacy-batch_DistributeMonthlyEcoPoints_ja.md |
| 現行のEminel Smartシステムの調査結果： | current-eminelsmart_DistributeMonthlyEcoPoints_ja.md |
| 【レビュー結果】修正後の総括<br>※xlsxには存在しない参考行 — xlsxへの貼り付けは不要。修正の反映は current-eminelsmart_DistributeMonthlyEcoPoints_ja.md の差し替えで行う。 | E-GWで本業務を改めて実装する場合（要件 F-ES-04）、新規に構築が必要なのは、月ごとの平均暖房設定温度を集計するバッチとしきい値判定のロジックのみである。月単位の重複付与防止（checkUserHasReceivedPoint 経由の pointBadgeStatsSk キー）、内部のポイント台帳（PointBadgeStats／UserBadgeSummary）、およびPIエラー時のロールバックは、共用フロー givePointBadgeForUser に既に存在する — 最終的なPoint Infinity呼び出しのステップとして GivePointToPointInfinityFunction とあわせて再利用でき、書き直す必要はない。なお 10_feature_list によると、ポイント管理・PI連携（F-ES-09）のブロックとアプリ側のポイント・省エネアドバイスは劣後（✅）となっている — 実装時期についてはmui／Kitagasと優先度を確認する必要がある。 |

*(Nguồn dòng 「レビュー結果」: `./current-eminelsmart_DistributeMonthlyEcoPoints_ja.md:24` — ô 「総括」, cùng thư mục `new/` này; đã bỏ ký hiệu định dạng Markdown (`**`, backtick) để tiện trích dùng dạng văn bản thuần khi cần, nội dung chữ không đổi — **hành động chính thức vẫn là thay nội dung file md trong `new/`, KHÔNG dán dòng này vào xlsx**. Bản VN tương ứng: `./current-eminelsmart_DistributeMonthlyEcoPoints.md:24` ô 「Khái quát」.)*

## 2. PublishRegularEcoMissionsCommand

| Batch | PublishRegularEcoMissionsCommand |
|---|---|
| 旧Eminelシステムの調査結果については、以下のファイルをご参照ください： | legacy-batch_PublishRegularEcoMissions_ja.md |
| 現行のEminel Smartシステムの調査結果： | current-eminelsmart_PublishRegularEcoMissions_ja.md |

## 3. DispatchPushMessagesCommand

| Batch | DispatchPushMessagesCommand |
|---|---|
| 旧Eminelシステムの調査結果については、以下のファイルをご参照ください： | legacy-batch_DispatchPushMessages_ja.md |
| 現行のEminel Smartシステムの調査結果： | current-eminelsmart_DispatchPushMessages_ja.md |

## 4. ControlDrOperationCommand

| Batch | ControlDrOperationCommand |
|---|---|
| 旧Eminelシステムの調査結果については、以下のファイルをご参照ください： | legacy-batch_ControlDrOperation_ja.md |
| 現行のEminel Smartシステムの調査結果： | current-eminelsmart_ControlDrOperation_ja.md |
