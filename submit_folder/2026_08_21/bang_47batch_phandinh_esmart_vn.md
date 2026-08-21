# Bảng 47 batch hệ cũ — e-smart có sẵn không, và có dùng lại được không

> ⚠️ **FILE NỘI BỘ, TIẾNG VIỆT.** Không nộp cho mui / 北ガス.
> Cấu trúc bảng giữ nguyên theo `legacy_eminel_docs/docs/03_API仕様/04_バッチ一覧.md` (chia theo server và nhóm chức năng, giữ nguyên tên class và 概要), **thêm ba cột**: e-smart có sẵn không · phán định · lý do.

| | |
|---|---|
| Ngày lập | 2026-08-21 |
| Cập nhật | 2026-08-22 — đính chính dòng `ControlDrOperationCommand`: DR cơ bản = FY26 (3 inline comment masao 08-20, phiếu No. 12) |
| Nguồn danh mục batch | `legacy_eminel_docs/docs/03_API仕様/04_バッチ一覧.md` — repo tại `ccd8f56` |
| Nguồn cột phán định | `submit_folder/2026_08_13/summary_batch_migration/summary_batch_migration_ja.md` — cột `新システムでの対応機能` · `結論` · `補足` |
| Kiểm trực tiếp trên code | `syp-eminelstandard-backend` @ `dc39aa39` (branch `gw-syp-dev`) · `legacy_eminel_docs` @ `ccd8f56` |

**Ký hiệu cột 「e-smart」:**

| | Nghĩa |
|---|---|
| ✅ | e-smart **đã có** và **dùng lại được** gần như nguyên trạng |
| 🔶 | e-smart **đã có** nhưng **phải sửa / thêm** mới dùng được |
| ⚠️ | e-smart **có cái gì đó** nhưng **KHÔNG dùng lại được** — bản chất khác |
| ⭕ | Không cần dùng lại vì **vấn đề tự tiêu biến** do kiến trúc mới |
| ❌ | e-smart **không có gì** — phải làm mới |
| — | **Không thuộc phạm vi SYP** (担当 = mui) |

**Tổng hợp trước khi vào chi tiết:**

| Ký hiệu | Số batch |
|---|---|
| ✅ dùng lại được nguyên trạng | **3** |
| 🔶 có nhưng phải sửa | **2** |
| ⚠️ có nhưng khác bản chất | **4** |
| ⭕ vấn đề tự tiêu biến | **3** |
| ❌ phải làm mới | **25** |
| 🔻 bỏ vì hệ mới đổi cách làm | **4** |
| 🚫 bỏ / không xác định | **2** |
| — không thuộc SYP | **4** |
| | **= 47** |

---

## hemssv（HEMSサーバ / GW通信）

**担当 = mui Lab.** Cả bốn batch đều nằm ngoài phạm vi SYP, khớp với bảng 担当 đã chốt 2026-08-13 (`7-1 ファームウェア` và `7-2 GW管理クラウド` là của mui Lab).

| クラス名 | 概要 | e-smart | Phán định | Lý do |
|---|---|---|---|---|
| `DlLimitManagerCommand` | FW更新指示の同時DL上限数管理 | — | Ngoài phạm vi SYP | 担当 = mui |
| `DlUlControllerCommand` | ファイル転送（DL/UL）制御 | — | Ngoài phạm vi SYP | 担当 = mui |
| `ErrorDeviceMailSendCommand` | 計測エラー通知メール送信 | — | Ngoài phạm vi SYP | 担当 = mui |
| `LogDeleteCommand` | ログファイルの退避・圧縮・削除 | — | Ngoài phạm vi SYP | 担当 = mui |

---

## conciergesv（コンシェルジュサーバ / アプリ通信・バッチ集計）

### 集計・計算系 — **19 batch, e-smart không có batch nào**

Toàn bộ nhóm này phán định 「**新規追加が必要**」. Đây là nhóm nặng nhất trong 47 batch, và là nền của toàn bộ tầng hiển thị trên app.

⚠️ **Đọc kỹ chỗ này**: 「新規追加が必要」 nói về **bản thân các batch**, **không** có nghĩa e-smart trắng tay ở mảng này. Kiểm trực tiếp 2026-08-21: e-smart **đã có ba bảng tích luỹ đang chạy** — `DeviceAccumulatedHistoryTable` · `DeviceDailyUsageHistoryTable` · `DeviceMonthlyUsageHistoryTable` (`template-dynamodb.yaml` dòng **1113 · 1145 · 1177**), cùng các batch nhập dữ liệu ghi vào chúng. Tức **cấu trúc lưu số liệu tích luỹ đã có**; phần phải làm mới là **logic tính toán** đặt lên trên. Giả định cũ *"nhóm 集計・計算系 không có gì dùng lại"* **đã bị bác từ 2026-08-12** — đừng dùng lại giả định đó khi ước lượng công.

| クラス名 | 概要 | e-smart | Chức năng E-GW tương ứng | Phán định |
|---|---|---|---|---|
| `CalcTenMinutesSensorCommand` | 10分単位センサー集計 | ❌ | `F-ES-01` biểu đồ cảm biến người · `F-ES-05` ただいま／見守り通知 | 新規追加が必要 |
| `CalcTenMinutesEnergyCommand` | 10分単位エネルギー集計 | ❌ | `F-ES-01` biểu đồ gas · `F-ES-02` report · `F-ES-13` dữ liệu thiếu · `F-ES-15` realtime | 新規追加が必要 |
| `CalcDailyAccumulatedValueCommand` | 日別累積値計算 | ❌ | `F-ES-01` biểu đồ phát điện/mua-bán điện/pin · `F-ES-15` | 新規追加が必要 |
| `CalcDailyAverageDataCommand` | 日別平均データ計算 | ❌ | `F-ES-01` trung bình cạnh biểu đồ · `F-ES-02` · `F-ES-12` gom nhóm | 新規追加が必要 |
| `CalcDailyEnergyConsumptionCommand` | 日別エネルギー消費量計算 | ❌ | `F-ES-01` biểu đồ gas/điện · `F-ES-15` | 新規追加が必要 |
| `CalcDailyRoomTemperatureCommand` | 日別室温計算 | ❌ | `F-ES-01` biểu đồ nhiệt độ phòng · `F-ES-13` | 新規追加が必要 |
| `CalcMonthlyAccumulatedValueCommand` | 月別累積値計算 | ❌ | `F-ES-01` biểu đồ tháng · `F-ES-02` report tháng · `F-ES-13` | 新規追加が必要 |
| `CalcMonthlyAverageDataCommand` | 月別平均データ計算 | ❌ | `F-ES-01` trung bình biểu đồ tháng · `F-ES-02` · `F-ES-12` | 新規追加が必要 |
| `CalcMonthlyAverageSetTemperatureCommand` | 月別平均設定温度計算 | ❌ | `F-ES-04` エコ暖房ポイント | 新規追加が必要 |
| `CalcMonthlyRoomTemperatureCommand` | 月別室温計算 | ❌ | `F-ES-01` biểu đồ nhiệt độ phòng theo tháng | 新規追加が必要 |
| `CalcYearlyAccumulatedValueCommand` | 年別累積値計算 | ❌ | `F-ES-02` tổng năm cho report năm | 新規追加が必要 |
| `CalcYearlyAverageDataCommand` | 年別平均データ計算 | ❌ | `F-ES-02` so sánh với hộ khác trong report năm · `F-ES-12` | 新規追加が必要 |
| `CalcYearlyPresetTemperatureCommand` | 年別プリセット温度計算 | ❌ | `F-ES-04` エコ暖房ポイント | 新規追加が必要 |
| `CalcYearlyRoomTemperatureCommand` | 年別室温計算 | ❌ | ⚠️ **không có chức năng tương ứng rõ ràng** — `F-ES-01` chỉ định nghĩa tới mức tháng, mức năm chưa xác nhận được | 新規追加が必要 |
| `CalcCommonAverageDataCommand` | 共通平均データ計算 | ❌ | Giống batch gọi nó: `F-ES-01` · `F-ES-02` · `F-ES-12` | 新規追加が必要 |
| `CalcFixedValueCommand` | 固定値計算 | ❌ | `F-ES-01` biểu đồ lượng điện mua | 新規追加が必要 |
| `CalcCarbonDioxideEmissionsCommand` | CO2排出量計算 | ❌ | `F-ES-02` hiệu quả giảm CO2 · `F-ES-03` tư vấn tiết kiệm | 新規追加が必要 |
| `CalcWeeklySavingReportEffectCommand` | 週間省エネレポート効果計算 | ❌ | `F-ES-02` hiệu quả tiết kiệm trong report tuần | 新規追加が必要 |
| `CalcWeeklySavingReportUsingCommand` | 週間省エネレポート使用量計算 | ❌ | `F-ES-02` report tuần | 新規追加が必要 |

### 配信・通知系 — **4 batch, chia làm ba tình huống khác nhau**

| クラス名 | 概要 | e-smart | Phán định | Lý do |
|---|---|---|---|---|
| `DistributeMonthlyEcoPointsCommand` | 月別エコポイント配布（PI連携） | ❌ | 新規追加が必要 | Nghiệp vụ của chính batch = `F-ES-04` エコ暖房ポイント; gián tiếp liên quan `F-ES-09` PI連携. Hệ cũ cấp **250 điểm/tháng** cho hộ có nhiệt độ cài đặt TB tháng **≤22℃** |
| `PublishRegularEcoMissionsCommand` | 定期省エネアドバイス配信（11種Publisher） | ❌ | 新規追加が必要 | Nghiệp vụ của chính batch = `F-ES-03` tư vấn tiết kiệm; gián tiếp `F-ES-12` gom nhóm. ⚠️ **Chặn**: gom 19 loại còn 7 mà **chưa ai định nghĩa 7 loại là gì** |
| `DispatchPushMessagesCommand` | Pushメッセージ配信 | ✅ | **新規追加不要 — 同等機能が既に存在** | Hệ cũ dùng server trung gian + hàng đợi DB + cron **mỗi phút**. e-smart làm thẳng bằng FCM và **chia mịn hơn hệ cũ**: kiểm 08-20 thấy `batch-push-notice` cùng 5 batch tiền xử lý theo loại (`-dr-start-`, `-dr-end-`, `-dr-new-`, `-news-new-`, `-survey-new-`) |
| `ControlDrOperationCommand` | DR指令操作制御 | 🔶 | **同等機能が既に存在（対象範囲はより広い）— cần thêm nhánh cho thiết bị E-GW** | e-smart có chùm `api-dr` · `batch-end-dr` · `batch-end-dr-preprocessing` (kiểm 08-20). ⚠️ **Đây LÀ việc FY26** (đính chính 22/08 — bản trước ghi nhầm "lùi 2027" theo body phiếu No. 12 khi chưa có trả lời): 3 inline comment của masao (mui, 08-20) trên bảng phiếu No. 12 chốt server DR管理 (`F-ES-07,08`) 「基本機能はFY26スコープで、一部DR実施判定ロジックが劣後の予定」, admin (`F-AD-08`) và app (B5) đều 「FY26スコープです」; tiền đề kế hoạch nội bộ (user chốt 21/08): coi **toàn bộ** `F-ES-07,08` là FY26. Phương án kết thúc DR: phiếu No. 25 vẫn là 「**後回し**」 (chưa chọn A/B) |

### 外部連携・受信系（Xzilla取込）— **3 batch, đường ống có sẵn nhưng handler phải viết**

Cả ba đều 「新規追加が必要」 và đều ứng với `F-ES-10` (liên kết Xzilla). Điểm cần nhớ: e-smart **có sẵn đường ống nhận** SFTP → S3 → DynamoDB — đây là một trong bốn ứng viên "nên dùng tiếp" đã báo mui. Cái phải làm mới là **handler cho từng loại dữ liệu**, không phải cả đường ống.

| クラス名 | 概要 | e-smart | Phán định | Lý do |
|---|---|---|---|---|
| `RcvCntctCancellationCommand` (IF2249) | 契約キャンセル受信 | ❌ | 新規追加が必要 | `F-ES-10` lấy thông tin hợp đồng; gián tiếp `F-ES-01`/`F-ES-15` vì cờ dừng tính ảnh hưởng biểu đồ và realtime |
| `RcvEmsPlsCntrPayerCommand` (IF2264) | EMSプラス契約支払者受信 | ❌ | 新規追加が必要 | `F-ES-10` lấy thông tin khách + hợp đồng; gián tiếp `F-ES-01`/`F-ES-15` (số liên kết cấp điện, cờ dừng tính mua-bán điện) |
| `RcvHalfHourElectricPowerCommand` (IF1156) | 30分電力データ受信 | ❌ | 新規追加が必要 | `F-ES-10` lấy điện 30 phút — nghiệp vụ của chính batch; kéo theo `F-ES-01` biểu đồ điện và `F-ES-02` report |

### CSV / ZIPエクスポート系 — **4 batch, bỏ vì hệ mới đổi cách làm**

Cả bốn 「**バッチとしては不要**」. Nghiệp vụ **vẫn còn** nhưng chuyển thành `F-AD-09`: người quản trị chọn khoảng thời gian rồi hệ **sinh file ngay lúc đó**, thay vì làm sẵn định kỳ. ⚠️ Hệ quả kéo theo: bỏ cách làm sẵn ZIP thì **thời hạn lưu của database thành trần cứng** của việc truy ngược — phiếu QA No. 14 trả lời **24 tháng** nhưng còn `回答中` và 2/3 câu chưa đáp.

| クラス名 | 概要 | e-smart | Phán định | Lý do |
|---|---|---|---|---|
| `CreateCsvAndZipConDeviceStatusesCommand` | 機器状態 CSV/ZIP 生成 | 🔻 | バッチとしては不要 | Thay bằng `F-AD-09` sinh file lúc bấm |
| `CreateCsvAndZipConSensorDailyValuesCommand` | センサー日別値 CSV/ZIP 生成 | 🔻 | バッチとしては不要 | Thay bằng `F-AD-09` |
| `CreateCsvAndZipConSensorDailyAveValuesCommand` | センサー日別平均値 CSV/ZIP 生成 | 🔻 | バッチとしては不要 | ⚠️ **Còn một chỗ mờ**: loại dữ liệu **trung bình** 「別表①未掲載」 — chưa có trong bảng loại dữ liệu tải về của spec mới, nên **chưa chắc `F-AD-09` thay được**; đang chờ xác nhận nghiệp vụ |
| `CreateCsvAndZipConSensorHourlyValuesCommand` | センサー時間別値 CSV/ZIP 生成 | 🔻 | バッチとしては不要 | Thay bằng `F-AD-09` |

### データ管理系 — **8 batch, nhóm hỗn hợp nhất**

Đây là nhóm phải đọc kỹ nhất, vì cột "chức năng tương ứng ở hệ mới" của nhiều dòng **không trống** nên trông như đã có sẵn — nhưng phán định lại là không dùng được.

| クラス名 | 概要 | e-smart | Phán định | Lý do |
|---|---|---|---|---|
| `CreateGroupSummaryCommand` | グループサマリー作成 | ❌ | 新規追加が必要 | 「該当機能なし」 — e-smart không có gì tương ứng |
| `CreateTablePartitionCommand` | テーブルパーティション作成 | ⭕ | バッチとしては不要 | Hệ cũ dùng MySQL nên phải tạo sẵn partition. e-smart dùng DynamoDB — 「テーブル設計そのものにパーティション事前作成という概念がない」 |
| `DeleteDataCommand` | データ削除 | ⚠️ | (1) không cần · (2) 3 mục: **2 mục không có dữ liệu đối tượng** nên ngoài phạm vi, **1 mục là khoảng trống mới** | Chỉ `PointBadgeStatsTable` có dữ liệu tương tự (lịch sử điểm/huy hiệu), nhưng 「データはあるが**保持期限の仕組みがない**」 — có dữ liệu mà không có cơ chế hạn lưu. Nối trực tiếp với phiếu QA No. 14 (24 tháng) |
| `DeleteLogicalDeletedDevicesCommand` | 論理削除済みデバイス削除 | ⚠️ | **完全に異なる仕組み** | e-smart có `api-device/delete-sensor.ts` nhưng **xoá thẳng** — không có khái niệm *xoá mềm + thời gian ân hạn* như hệ cũ |
| `DeleteTimeOutControlOneMinuteCommand` | 1分タイムアウト制御レコード削除 | ⭕ | **不要 — vấn đề kỹ thuật đó không tồn tại** | Hệ cũ ghi lệnh vào DB rồi gateway lấy về → mới có "lệnh treo" cần dọn. e-smart gọi thẳng API đám mây thiết bị **theo lối đồng bộ** (`api-device/control-device.ts`) → không có bản ghi treo |
| `DeleteTimeOutControlTenMinuteCommand` | 10分タイムアウト制御レコード削除 | ⭕ | 不要 — cùng lý do với batch sinh đôi | Như trên |
| `TerminateOutdatedDeviceControlJobsCommand` | 期限切れデバイス制御ジョブ終了 | ⚠️ | **未移行** | e-smart trả lỗi ngay qua API response. Phán định ghi rõ: 「単なるアーキテクチャ変更ではなく、**UX上の保証が1つ消失している**」 — không chỉ là đổi kiến trúc mà **mất một bảo đảm về trải nghiệm** |
| `RankingCreationCommand` | ランキング作成 | ⚠️ | **未移行 — chỉ có cái cùng tên** | e-smart có `get-ranking-by-total-badge.ts`, **trùng tên "ranking" nhưng bản chất khác**: xếp theo **ngưỡng tuyệt đối** trên điểm huy hiệu tích luỹ, không phải **so sánh giữa các hộ** như hệ cũ |

### 監視・ログ系 — **3 batch**

| クラス名 | 概要 | e-smart | Phán định | Lý do |
|---|---|---|---|---|
| `SendAlertLogMailCommand` | アラートログメール送信 | ✅ | **移行済み・カバー範囲も拡大 — 対応不要** | Không phải dùng lại code mà **dùng lại một cách làm khác thay thế hoàn toàn**: `push-notification-error-log/app.ts` + **CloudWatch Logs Subscription Filter** + **SNS** — hạ tầng giám sát của chính AWS |
| `WatchNotificationCommand` | 通知監視 | 🔶 | **部分的に移行済み・大幅に簡略化** | e-smart có `batch-receive-data-infrared-remote` + `batch-control-device-and-push-notice-sensor`; chỉ còn giữ đúng phần *"có chuyển động thì thông báo ngay"*. ⚠️ **Đừng lẫn** `通知監視` (*giám sát thông báo*) với `見守り` (*trông nom người thân*) — hai chức năng khác nhau; `見守り` vừa được chốt **PHẢI LÀM** (phiếu QA No. 24) |
| `PutLogFileCommand` | ログファイル出力 | 🚫 | **未移行 → đã chốt BỎ** | 「該当なし」. Phiếu QA No. 24 chốt: **không tiếp tục** gửi log app lên Xzilla ⇒ **không port**, không dựng đường SFTP xuất log, **trừ hạng mục này khi đếm số batch phải làm** |

---

## eminelsv（新EMINELサーバ / 運用管理画面）

| クラス名 | 概要 | e-smart | Phán định | Lý do |
|---|---|---|---|---|
| `MakeCodeMapDataCommand` | コードマップデータをCSVから生成・ファイル出力 | 🚫 | **未移行 — không xác định được mục đích nghiệp vụ** | 「そもそもの業務目的が特定できず」 |
| `HashPasswordCommand` | パスワードハッシュ生成（ユーティリティ） | ✅ | **不要 — Cognito thay hoàn toàn** | AWS Cognito, thấy ở `api-admin/create-admin.ts` |

---

## Phụ chú — ba con số khác nhau về số loại tư vấn tiết kiệm

Trong lúc dựng bảng này phát hiện **ba nguồn ghi ba con số khác nhau** cho cùng một thứ. Không phải chúng mâu thuẫn — chúng **đếm ba thứ khác nhau**:

| Con số | Nguồn | Thật ra đang đếm gì |
|---|---|---|
| **19** | `PublishRegularEcoMissionsCommand.php` dòng 74–135 (`case 1`→`case 19`) và `ConRegularEcoMissionsSeed.php` dòng 24–301 (19 bản ghi) | **Số mã mission** — đây là con số đúng để nói "hệ cũ có bao nhiêu loại tư vấn" |
| **11** | `04_バッチ一覧.md` ghi 「11種Publisher」 | **Số FILE** Publisher trong `sources/conciergesv-develop` — nhưng trong 11 file có **2 file nền** (`EcoMissionPublisher.php` là lớp cơ sở, `EcoMissionPublisherOption.php` là tuỳ chọn), nên chỉ **9 lớp thật sự phát tư vấn** |
| **約15** | `20_open_issues.md` dòng 176 (CLD-06) | **Ước lượng** của tài liệu quản lý — chữ 「約」 (*khoảng*) nói rõ là không đếm chính xác |

⇒ **Khi trích, dùng con số 19** và dẫn nguồn code. Guide đã sửa theo hướng này và ghi thành mục mâu thuẫn **Phụ lục B.6** *(mục đầu tiên thuộc loại "tài liệu ↔ code", 5 mục cũ đều là "tài liệu ↔ tài liệu")*.

*(Chín lớp phát tư vấn: `Co2Reduced` · `EcoModeNotSet` · `OverGasElectricUsageOverAvg` · `OverGasElectricUsageOverAvgWinter` · `SetHighTempInAbsence` · `SetHighTempInSleep` · `SetHighTemp` · `StartContractAnniversary` · `StillRunningHeaterMission`. Chín lớp xử lý 19 mã mission — tức **một lớp phục vụ nhiều mã**; quan hệ 1-nhiều cụ thể thì chưa kiểm.)*

---

## Giới hạn của bảng này

Cột phán định **không phải do tôi tự điều tra** mà lấy lại từ bảng tổng hợp 47 batch của đợt review 2026-08-13, do **thành viên khác điều tra**. SYP mới tự điều tra **11/47 batch** (nhóm 配信・通知系 4 · Xzilla 3 · CSV/ZIP 4).

Nghĩa là: **nhóm 集計・計算系 19 batch — nhóm nặng nhất — SYP chưa tự điều tra**, nên các phán định 「新規追加が必要」 ở nhóm đó là trích lại, **chưa kiểm chứng độc lập trên code**.

Riêng ba nhóm khẳng định về code e-smart trong bảng này thì **tôi kiểm trực tiếp ngày 2026-08-21** trên `syp-eminelstandard-backend` @ `dc39aa39`: ba bảng tích luỹ (`template-dynamodb.yaml` 1113/1145/1177) · họ batch push (`batch-push-notice*`, 6 batch) · chùm DR (`api-dr` · `batch-end-dr` · `batch-end-dr-preprocessing`). Và số lớp Publisher trên `legacy_eminel_docs` @ `ccd8f56`.
