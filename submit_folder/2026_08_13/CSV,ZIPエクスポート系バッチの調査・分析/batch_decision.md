# batch_decision（Markdown版）

> Bản Markdown convert máy móc 1-1 từ `batch_decision.xlsx` cùng thư mục — nội dung giữ nguyên từng ô, không dịch/không sửa. Ngày convert: 2026-08-16 ・ số sheet: 4.

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
