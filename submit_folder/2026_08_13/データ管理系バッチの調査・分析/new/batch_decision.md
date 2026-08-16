# batch_decision（Markdown版・修正版）

> **BẢN ĐÃ SỬA THEO REVIEW 16/08** — sheet 要修正 đã thay câu kết luận (đã qua đối kháng); các sheet khác giữ nguyên văn. Sheet đã sửa: CreateTablePartitionCommand、DeleteDataCommand、DeleteLogicalDeletedDevicesCommand. Bản gốc trung thực với xlsx: `../batch_decision.md`.

> Bản Markdown convert máy móc 1-1 từ `batch_decision.xlsx` cùng thư mục — nội dung convert giữ nguyên từng ô (không dịch); riêng câu kết luận các sheet nêu ở ghi chú trên đã thay theo review. Ngày convert: 2026-08-16 ・ số sheet: 8.

## 1. CreateGroupSummaryCommand

| Batch | CreateGroupSummaryCommand |
|---|---|
| 旧Eminelシステムの調査結果については、以下のファイルをご参照ください： | CreateGroupSummary.md |
| 現行のEminel Smartシステムの調査結果： | 再利用可能なバッチ、または同等のロジックは存在しません。 |

## 2. CreateTablePartitionCommand

| Batch | CreateTablePartitionCommand |
|---|---|
| 旧Eminelシステムの調査結果については、以下のファイルをご参照ください： | CreateTablePartition.md |
| 現行のEminel Smartシステムの調査結果： | 再利用可能なバッチ、または同等のロジックは存在しません。旧バッチはPostgreSQL宣言的パーティショニング固有の「パーティション事前作成」という基盤保守処理であり、現行Eminel SmartはDynamoDB採用により課題自体が消滅しています（対象4テーブルは単一テーブル＋TTL自動削除のみで、パーティション作成・削除に相当するLambda/cronは存在しない。TTLが代替するのは旧DeleteDataCommandの削除側のみ）。なお、新システムでRDBを採用する場合に限り、同種のパーティション保守バッチの要否を再検討する必要があります。 |

## 3. DeleteDataCommand

| Batch | DeleteDataCommand |
|---|---|
| 旧Eminelシステムの調査結果については、以下のファイルをご参照ください： | DeleteData.md |
| 現行のEminel Smartシステムの調査結果： | パーティションDROP対象の10テーブル分は、現行Eminel Smartでは対応する履歴系テーブル（DevicePropertyHistory／DeviceAccumulatedHistory／DeviceDailyUsageHistory／DeviceMonthlyUsageHistory／DeviceStatusHistory／InfraredRemoteData等）のDynamoDB TTLにより同等の保持期間管理へ置き換えられています。一方、条件DELETE対象の3テーブルのうち、デバイス制御履歴（t_301）とグループ履歴（s_151）は相当データ自体が存在せず（グループ履歴はC2ランキング「実施する」決定により今後必要となる見込み）、省エネポイント（s_141）に相当するPointBadgeStatsTableはTTLも削除バッチも無く無期限保持となっており、旧システムの保存期間（2年度）に相当する仕組みは未実装です。保持期間の要否は業務確認が必要です。 |

## 4. DeleteLogicalDeletedDevicesCommand

| Batch | DeleteLogicalDeletedDevicesCommand |
|---|---|
| 旧Eminelシステムの調査結果については、以下のファイルをご参照ください： | DeleteLogicalDeletedDevices.md |
| 現行のEminel Smartシステムの調査結果： | 業務側に確認：機器を削除する際、完全に削除する前に「取り消し（復元）」可能な猶予期間（旧システムは論理削除後30日）が必要かどうかを確認する。<br>（参考・現行Eminel Smartの現状）旧版の「論理削除＋30日猶予＋日次物理削除バッチ」に相当する猶予期間は無いが、不要機器の削除自体は複数の経路で即時物理削除として既に行われている：<br>・機器一覧取得API：メーカーサーバ側一覧に存在しなくなった機器（RINNAI/NORITZ/DAIKIN）をDeviceTableから即時削除（get-list-remote-control-device）<br>・会員資格喪失・ガス契約失効時：対象ユーザーの機器・機器エラー情報を一括削除する定期バッチ（batch-remove-integration-expired）、連携解除API、アカウントリセットバッチ<br>・センサー削除API（delete-sensor）・赤外線リモコン削除API（delete-infrared-remote）による即時削除<br>なお計測履歴（DeviceDailyUsageHistoryTable等）は機器レコードとは独立にTTLで自動失効するため、機器削除で即時に失われるのは機器レコード自体である。<br>猶予期間が必要と判断された場合は、soft-deleteフラグ＋TTL属性の追加で対応可能（DeviceTable／MuiDeviceTableは現状TTL未設定のため、TimeToLiveSpecificationの有効化が前提）。旧版のように別途バッチを用意する必要はなく、DynamoDBのTTLを活用できる。 |

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
