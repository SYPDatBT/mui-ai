# batch_decision（Markdown版・修正版）

> **BẢN ĐÃ SỬA THEO REVIEW 16/08** — sheet 要修正 đã thay câu kết luận (đã qua đối kháng); các sheet khác giữ nguyên văn. Sheet đã sửa: RcvCntctCancellationCommand、RcvEmsPlsCntrPayerCommand、RcvHalfHourElectricPowerCommand. Bản gốc trung thực với xlsx: `../batch_decision.md`.

> Bản Markdown convert máy móc 1-1 từ `batch_decision.xlsx` cùng thư mục — nội dung giữ nguyên từng ô, không dịch/không sửa. Ngày convert: 2026-08-16 ・ số sheet: 3.

## 1. RcvCntctCancellationCommand

| Batch | RcvCntctCancellationCommand |
|---|---|
| 旧Eminelシステムの調査結果については、以下のファイルをご参照ください： | legacy-batch_RcvCntctCancellation.md |
| 現行のEminel Smartシステムの調査結果： | 「同等のロジック（接点データ（IF2249）の取込、および買電売電算出停止フラグ設定に相当する処理）は存在しません（IF2249・接点・解約・買電売電の grep は0件）。ただし、Eminel Smart には Xzilla ファイルの SFTP→S3→DynamoDB 受信基盤（batch-get-list-file-name-from-sftp-server／batch-forward-csv-from-sftp-server-to-s3／batch_run_sequentially.asl.json、重複取込防止の CsvDownloadHistory テーブル）が存在し、IF2016・IF2023 等8種のCSV取込で稼働中のため、本バッチのファイル受信部分はこの基盤を再利用可能です。」 |

## 2. RcvEmsPlsCntrPayerCommand

| Batch | RcvEmsPlsCntrPayerCommand |
|---|---|
| 旧Eminelシステムの調査結果については、以下のファイルをご参照ください： | legacy-batch_RcvEmsPlsCntrPayer.md |
| 現行のEminel Smartシステムの調査結果： | IF2264（場所契約支払者マスタ）の取込バッチおよび契約終了判定と同等のロジックは存在しません（backend全体grep 0件）。ただし、Xzilla受信基盤（SFTP→S3→DynamoDB：batch-get-list-file-name-from-sftp-server／batch-forward-csv-from-sftp-server-to-s3＋IF別取込ハンドラ）と契約系取込チャネル（IF2023／IF2024／DM1040 — DM1040は支払者ロール抽出済み）は再利用可能であり、支払者データの受け皿および契約終了判定の後処理は同基盤の拡張として実装できます。 |

## 3. RcvHalfHourElectricPowerCommand

| Batch | RcvHalfHourElectricPowerCommand |
|---|---|
| 旧Eminelシステムの調査結果については、以下のファイルをご参照ください： | legacy-batch_RcvHalfHourElectricPower.md |
| 現行のEminel Smartシステムの調査結果： | IF1156（電力30分値取込・買電売電算出）に相当するバッチや同等のロジックは存在しません（IF1156・30分・速報・確報・HalfHour等で全文検索0件）。ただし、Xzilla向けSFTP→S3→DynamoDBの受信基盤（batch-get-list-file-name-from-sftp-server等の既存バッチ群）は再利用可能なため、本バッチは同基盤上に取込ハンドラー、速報/確報テーブル、および買電・売電算出ロジックを新規実装する必要があります。 |
