# batch_decision（Markdown版）

> Bản Markdown convert máy móc 1-1 từ `batch_decision.xlsx` cùng thư mục — nội dung giữ nguyên từng ô, không dịch/không sửa. Ngày convert: 2026-08-16 ・ số sheet: 8.

## 1. CreateGroupSummaryCommand

| Batch | CreateGroupSummaryCommand |
|---|---|
| 旧Eminelシステムの調査結果については、以下のファイルをご参照ください： | CreateGroupSummary.md |
| 現行のEminel Smartシステムの調査結果： | 再利用可能なバッチ、または同等のロジックは存在しません。 |

## 2. CreateTablePartitionCommand

| Batch | CreateTablePartitionCommand |
|---|---|
| 旧Eminelシステムの調査結果については、以下のファイルをご参照ください： | CreateTablePartition.md |
| 現行のEminel Smartシステムの調査結果： | 旧ロジックは使用せず、同等のロジックに変更されています。 |

## 3. DeleteDataCommand

| Batch | DeleteDataCommand |
|---|---|
| 旧Eminelシステムの調査結果については、以下のファイルをご参照ください： | DeleteData.md |
| 現行のEminel Smartシステムの調査結果： | 旧ロジックは使用せず、同等のロジックに変更されています。 |

## 4. DeleteLogicalDeletedDevicesCommand

| Batch | DeleteLogicalDeletedDevicesCommand |
|---|---|
| 旧Eminelシステムの調査結果については、以下のファイルをご参照ください： | DeleteLogicalDeletedDevices.md |
| 現行のEminel Smartシステムの調査結果： | 業務側に確認：デバイスデータが完全に失われる前に、「取り消し（復元）」可能な猶予期間が必要かどうかを確認する。<br>必要であれば、これは対応する価値のある改善です（soft-delete フラグを追加し、N日後に自動削除するTTLを設定する。旧版のように別途バッチを用意する必要はなく、DynamoDBのTTLを活用する）。 |

## 5. DeleteTimeOutControlOneMinuteCommand

| Batch | DeleteTimeOutControlOneMinuteCommand |
|---|---|
| 旧Eminelシステムの調査結果については、以下のファイルをご参照ください： | DeleteTimeOutControlOneMinute.md |
| 現行のEminel Smartシステムの調査結果： | ・再利用可能なバッチ、または同等のロジックは存在しません。<br><br>・新システムはポーリング方式を廃止したため、本バッチの置き換えは不要。 |

## 6. DeleteTimeOutControlTenMinuteCommand

| Batch | DeleteTimeOutControlTenMinuteCommand |
|---|---|
| 旧Eminelシステムの調査結果については、以下のファイルをご参照ください： | DeleteTimeOutControlTenMinute.md |
| 現行のEminel Smartシステムの調査結果： | 新システムはポーリング方式を廃止したため、本バッチの置き換えは不要。 |

## 7. TerminateOutdatedDeviceControlJobsCommand

| Batch | TerminateOutdatedDeviceControlJobsCommand |
|---|---|
| 旧Eminelシステムの調査結果については、以下のファイルをご参照ください： | TerminateOutdatedDeviceControlJobs.md |
| 現行のEminel Smartシステムの調査結果： | 再利用可能なバッチ、または同等のロジックは存在しません。 |

## 8. RankingCreationCommand

| Batch | RankingCreationCommand |
|---|---|
| 旧Eminelシステムの調査結果については、以下のファイルをご参照ください： | RankingCreation.md |
| 現行のEminel Smartシステムの調査結果： | 再利用可能なバッチ、または同等のロジックは存在しません。 |
