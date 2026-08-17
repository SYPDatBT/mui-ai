# batch_decision（Markdown版・レビュー確認版）

> **【メンバーの作業】なし — 要修正シートは0件です。本ファイルはレビュー完了の確認用であり、本グループに問題があったという意味ではありません。**

> **REVIEW 16–17/08: NHÓM NÀY KHÔNG CÓ SHEET 要修正** — mọi ô bên dưới **trùng khít bản gốc** `../batch_decision.md` (chỉ khác tiêu đề và 3 ghi chú meta này). **Member KHÔNG bắt buộc dán gì vào `batch_decision.xlsx` của nhóm.** ⚠️ 4 file `legacy-batch_CreateCsvAndZip*_ja.md` trong `new/` là **bản sao nguyên văn (0 byte khác)** của bản ở thư mục nhóm — chúng trùng khít bản đã review và nộp ở `../../../2026_08_12/` nên đợt này không review lại nội dung (`../../review_plan_20260813.md` mục 8 điểm 3 — user duyệt bỏ qua); chúng có mặt ở đây vì **`new/` là bộ tài liệu nộp, phải đủ file dù có sửa hay không** — **KHÔNG có nghĩa nhóm bị lỗi phải vá.**

> **Verdict 4/4 sheet**: `CreateCsvAndZipConDeviceStatusesCommand` **妥当だが根拠不足** — **không có câu bổ sung soạn sẵn** (別表① chưa có loại 機器状態履歴 theo kỳ, 未決#1 要FIX; xem `../../review_summary.md` §3.G6) ・ `CreateCsvAndZipConSensorDailyValuesCommand` **妥当** ・ `CreateCsvAndZipConSensorDailyAveValuesCommand` **要業務確認** (**QA-01①** — `s_113` là trung bình LIÊN HỘ, 別表① không có loại 平均) ・ `CreateCsvAndZipConSensorHourlyValuesCommand` **妥当**. Câu hỏi QA: `../../../qa/qa_review_20260813_20260817.md` — **CHƯA GỬI**, chờ user chuyển PM mui.

> Bản Markdown convert máy móc 1-1 từ `../batch_decision.xlsx` (thư mục nhóm) — nội dung giữ nguyên từng ô, không dịch/không sửa. Ngày convert: 2026-08-16 ・ số sheet: 4.

## 1. CreateCsvAndZipConDeviceStatusesCommand

| batch | CreateCsvAndZipConDeviceStatusesCommand |
|---|---|
| 旧Eminelシステムの調査結果については、以下のファイルをご参照ください： | legacy-batch_CreateCsvAndZipConDeviceStatuses_ja.md |
| 現行のEminel Smartシステムの調査結果： | バッチとしては不要（新システムでは F-AD-09 データダウンロードで代替）。 |
| 理由： | 新システムは「定期的にファイルを作り置き」しない。管理者が期間を指定した時点で api-download が batch-download Lambda を非同期起動してZIPを生成し、S3経由の署名付きURLで配布する方式。DB側の保持は DynamoDB TTL、バックアップは PITR が担うため、「退避してからDROP」という仕組み自体が不要。<br>※根拠は e-smart backend（api-download / batch-download）の調査分。本判定は旧システム調査書の範囲外。 |

## 2. CreateCsvAndZipConSensorDailyValuesCommand

| batch | CreateCsvAndZipConSensorDailyValuesCommand |
|---|---|
| 旧Eminelシステムの調査結果については、以下のファイルをご参照ください： | legacy-batch_CreateCsvAndZipConSensorDailyValues_ja.md |
| 現行のEminel Smartシステムの調査結果： | バッチとしては不要（新システムでは F-AD-09 データダウンロードで代替）。 |
| 理由： | 新システムは「定期的にファイルを作り置き」しない。管理者が期間を指定した時点で api-download が batch-download Lambda を非同期起動してZIPを生成し、S3経由の署名付きURLで配布する方式。DB側の保持は DynamoDB TTL、バックアップは PITR が担うため、「退避してからDROP」という仕組み自体が不要。 |

## 3. CreateCsvAndZipConSensorDailyAveValuesCommand

| batch | CreateCsvAndZipConSensorDailyAveValuesCommand |
|---|---|
| 旧Eminelシステムの調査結果については、以下のファイルをご参照ください： | legacy-batch_CreateCsvAndZipConSensorDailyAveValues_ja.md |
| 現行のEminel Smartシステムの調査結果： | バッチとしては不要（新システムでは F-AD-09 データダウンロードで代替）。 |
| 理由： | 新システムは「定期的にファイルを作り置き」しない。管理者が期間を指定した時点で api-download が batch-download Lambda を非同期起動してZIPを生成し、S3経由の署名付きURLで配布する方式。DB側の保持は DynamoDB TTL、バックアップは PITR が担うため、「退避してからDROP」という仕組み自体が不要。 |

## 4. CreateCsvAndZipConSensorHourlyValuesCommand

| batch | CreateCsvAndZipConSensorHourlyValuesCommand |
|---|---|
| 旧Eminelシステムの調査結果については、以下のファイルをご参照ください： | legacy-batch_CreateCsvAndZipConSensorHourlyValues_ja.md |
| 現行のEminel Smartシステムの調査結果： | バッチとしては不要（新システムでは F-AD-09 データダウンロードで代替）。 |
| 理由： | 新システムは「定期的にファイルを作り置き」しない。管理者が期間を指定した時点で api-download が batch-download Lambda を非同期起動してZIPを生成し、S3経由の署名付きURLで配布する方式。DB側の保持は DynamoDB TTL、バックアップは PITR が担うため、「退避してからDROP」という仕組み自体が不要。 |
