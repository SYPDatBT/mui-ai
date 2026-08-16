# CreateTablePartitionCommand（テーブルパーティション作成）

## Tóm tắt

`CreateTablePartitionCommand` là batch cron chạy hàng ngày (23:20) trên server `conciergesv`: **tạo
trước (pre-create)** các PostgreSQL declarative partition con cho 10 bảng time-series lớn dùng chung
trong toàn hệ thống (sensor theo giờ/ngày/tháng/năm, average theo ngày/tháng/năm, tuần báo cáo tiết
kiệm, ranking, trạng thái thiết bị) — tạo sẵn cho 14 ngày tới (mặc định) hoặc 1 ngày cụ thể (qua tham
số). Đây là workaround bắt buộc của PostgreSQL declarative partitioning: nếu 1 INSERT rơi vào khoảng
ngày/tháng/năm chưa có partition con, PostgreSQL báo lỗi ngay — nên phải có batch này chạy trước để
các Command thực sự ghi vào các bảng đó (phần lớn trong 28 Command khác tham chiếu, đếm thật qua grep)
không bị lỗi insert. Ở repo mới
`syp-eminelstandard-backend`, **không cần và không có chức năng tương đương** — không phải vì thiếu sót
khi port, mà vì đổi hẳn nền tảng lưu trữ sang DynamoDB: đã xác nhận 4 bảng time-series lớn nhất
(`DeviceAccumulatedHistoryTable`, `DeviceDailyUsageHistoryTable`, `DeviceMonthlyUsageHistoryTable`,
`DeviceStatusHistoryTable`) đều là **1 bảng duy nhất, tồn tại vĩnh viễn**, DynamoDB tự phân phối dữ liệu
vào partition vật lý nội bộ theo hash key — hoàn toàn trong suốt với ứng dụng, không có API nào để
"tạo trước" partition theo ngày như PostgreSQL declarative partitioning, nên không tồn tại rủi ro lỗi
kiểu "no partition of relation found for row" mà batch cũ tồn tại để né.

---

# Phần A — Hệ thống cũ

## A.1 Tổng quát

| Mục | Nội dung |
|---|---|
| **Tên batch** | Class: `CreateTablePartitionCommand` (extends `BaseCommand`) · Tên lệnh gọi: `create_table_partition` *(suy đoán theo quy ước CakePHP 4, không có override tường minh trong file)* · Script cron: `13_CreateTablePartition.sh` · Tên tiếng Nhật trong cron: "13.テーブルパーティション作成". |
| **Vai trò** | Bảo trì hạ tầng DB — tạo sẵn partition con cho 10 bảng PostgreSQL partitioned trước khi dữ liệu thật cần ghi vào đó, tránh lỗi insert "no partition of relation found for row". |
| **Input** | Không đọc DB, không đọc file. Chỉ có tham số dòng lệnh `--date` (ngày tạo cụ thể, tùy chọn). |
| **Output** | Chạy `CREATE TABLE IF NOT EXISTS ... PARTITION OF ... FOR VALUES FROM (...) TO (...)` trên 10 bảng cha khác nhau — không ghi dữ liệu, chỉ tạo cấu trúc bảng (partition con rỗng). |
| **Khái quát xử lý** | 1. Xác định danh sách ngày cần tạo partition (xem A.2.1).<br>2. Với mỗi 1 trong 10 bảng cha, lặp qua danh sách ngày đó, tính tên + range partition con tương ứng, chạy `CREATE TABLE IF NOT EXISTS ... PARTITION OF`.<br>3. Với 6/10 bảng có partition granularity thô hơn ngày (tháng/năm), có bước dedup để không tạo lại cùng 1 partition nhiều lần trong 1 lượt chạy.<br>4. Lỗi ở 1 partition (bảng/ngày cụ thể) chỉ log `alert`, KHÔNG dừng batch — vẫn tiếp tục tạo các partition còn lại. |

## A.2 Chi tiết

### A.2.1 Lịch chạy & xác định danh sách ngày cần tạo partition

| Mục | Nội dung | Nguồn |
|---|---|---|
| Lịch chạy (cron) | `20 23 * * *` — hàng ngày 23:20, comment "13.テーブルパーティション作成" | `docs/02_詳細設計/10_バッチ処理/mng-webap_cron設定_20241029.txt:45-46` |
| Tham số `--date` | Không truyền → tạo partition cho **14 ngày tới** (`ngày mai` .. `ngày mai+13`, tức `hôm nay+1`..`hôm nay+14`) — KHÔNG bao gồm hôm nay. Truyền → phải khớp regex `yyyy-MM-dd`, sai format → lỗi validate, chỉ tạo cho ĐÚNG 1 ngày đó. | `CreateTablePartitionCommand.php:463-481`; hằng số `CREATE_PARTITION_RANGE_DAYS=14` (`const.php:720`) |

Với lịch chạy mặc định (23:20 hàng ngày, luôn +14 ngày tới), batch luôn "đi trước" dữ liệu thật ít nhất
13 ngày — đủ dư để không bao giờ thiếu partition cho ngày mai, trừ khi batch bị dừng liên tục >13 ngày.

### A.2.2 Bảng ánh xạ 10 partition — tên bảng, độ hẹp/rộng range, lý do

Tất cả 10 hàm dùng chung 1 khuôn: build tên partition con → build khoảng `FOR VALUES FROM...TO...` →
`CREATE TABLE IF NOT EXISTS ... PARTITION OF {bảng cha}` → try/catch, lỗi thì log `alert` (không dừng
batch). Khác nhau ở: **bảng cha**, **đơn vị lặp** (mỗi ngày trong danh sách, hay dedup theo tháng/năm),
và **độ rộng range**. Độ rộng range phụ thuộc cột partition-key của bảng đó luôn cố định 1 giá trị/kỳ
(range hẹp đúng bằng 1 ngày dù đơn vị là tháng/năm) hay thực sự biến đổi theo ngày trong kỳ (range phải
rộng bằng cả kỳ) — xác nhận qua đọc entity tương ứng, không suy đoán.

| Hàm | Bảng cha (Model/Table) | Ý nghĩa bảng | Đơn vị partition | Dedup theo | Range | Vì sao range hẹp/rộng |
|---|---|---|---|---|---|---|
| `diffSensorInfo` | `s_101` (`ConSensorMemoryValue`) | 差分センサ情報 — giá trị chênh lệch cảm biến | Ngày | Không (mỗi ngày 1 partition) | `[ngày, ngày+1)` | Cột ngày (`c004`) là giá trị THẬT của từng bản ghi, biến đổi theo ngày → cần range đúng 1 ngày |
| `dailySensorInfo` | `s_102` (`ConSensorHourlyValue`) | 日毎センサ情報 — giá trị cảm biến theo giờ, 1 dòng/ngày (24 cột giờ) | Ngày | Không | `[ngày, ngày+1)` | Cột `c004` (`FrozenDate`) biến đổi theo từng ngày thật (`Entity/ConSensorHourlyValue.php:17`) |
| `monthlySensorInfo` | `s_103` (`ConSensorDailyValue`) | 月毎センサ情報 — giá trị cảm biến theo ngày, 1 dòng/tháng (31 cột ngày) | Tháng | Có (bỏ qua nếu cùng tháng với ngày liền trước trong danh sách) | `[đầu tháng, đầu tháng + 1 ngày)` — **hẹp**, chỉ đúng ngày 01 | Cột ngày của dòng luôn CỐ ĐỊNH = ngày 01 đầu tháng (xác nhận cùng pattern ở `s_113`, xem `CreateGroupSummary.md`) — range hẹp vẫn khớp đủ vì giá trị thật không bao giờ khác ngày 01 |
| `yearlySensorInfo` | `s_104` (`ConSensorMonthlyValue`) | 年毎センサ情報 — giá trị cảm biến theo tháng, 1 dòng/năm (12 cột tháng) | Năm | Có (bỏ qua nếu cùng năm) | `[năm, năm+1)` | Cột năm (`c004`, kiểu `int`) chỉ có 1 giá trị/năm (`Entity/ConSensorMonthlyValue.php:16`) → range đúng 1 năm là vừa đủ |
| `dailyAverageSensorInfo` | `s_112` (`ConSensorHourlyAveValue`) | 日毎平均センサ情報 — trung bình theo giờ, 1 dòng/ngày | Ngày | Không | `[ngày, ngày+1)` | Bản average của `s_102`, cùng cấu trúc cột ngày biến đổi theo ngày thật |
| `monthlyAverageSensorInfo` | `s_113` (`ConSensorDailyAveValue`) | 月毎平均センサ情報 — trung bình theo ngày, 1 dòng/tháng (31 cột ngày) | Tháng | Có | `[đầu tháng, đầu tháng + 1 ngày)` — **hẹp** | Cột `c003` luôn = ngày 01 đầu tháng — đã xác nhận trực tiếp ở audit `CreateGroupSummaryCommand` (bảng đích của nhánh daily ghi population) |
| `yearlyAverageSensorInfo` | `s_114` (`ConSensorMonthlyAveValue`) | 年毎平均センサ情報 — trung bình theo tháng, 1 dòng/năm (12 cột tháng) | Năm | Có | `[năm, năm+1)` | Cột `c003` kiểu `int`, chỉ 1 giá trị/năm — đã xác nhận ở audit `CreateGroupSummaryCommand` (bảng đích của nhánh monthly) |
| `weeklyEnergySavingReport` | `s_105` (`ConWeeklyEcoReport`) | 週間省エネレポート情報 | Tháng | Có | `[đầu tháng, đầu THÁNG SAU)` — **rộng, đủ cả tháng** | Cột ngày (`c002`, `FrozenTime`) biến đổi theo từng ngày báo cáo cụ thể trong tháng (`Entity/ConWeeklyEcoReport.php:14`) — range hẹp sẽ làm mất dữ liệu các ngày khác trong tháng |
| `rankingInfo` | `s_121` (`ConRanking`) | ランキング情報 | Năm | Có | `[năm, năm+1)` | Cột `c002` (`C_YEAR`, kiểu `int` — `Entity/ConRanking.php:14,45`) cố định 1 giá trị/năm (`RankingCreationCommand.php:349`) — cùng pattern `s_104`/`s_114`, range 1 năm vừa khớp |
| `deviceStatus` | `t_202` (`ConDeviceStatus`) | 機器状態情報 — trạng thái thiết bị (ghi qua API `InstructionController` của `hemssv-develop` — server tiếp nhận dữ liệu GW, không chỉ batch) | Ngày | Không | `[ngày, ngày+1)` | Dữ liệu trạng thái ghi liên tục theo thời gian thật nhận từ thiết bị |

Nguồn: `CreateTablePartitionCommand.php:83-455` (toàn bộ 10 hàm); PK/tên bảng đối chiếu tại
`sources/eminel_sv_lib-develop/src/Model/Table/{ConSensorMemoryValuesTable,ConSensorHourlyValuesTable,
ConSensorDailyValuesTable,ConSensorMonthlyValuesTable,ConSensorHourlyAveValuesTable,
ConSensorDailyAveValuesTable,ConSensorMonthlyAveValuesTable,ConWeeklyEcoReportsTable,ConRankingsTable,
ConDeviceStatusesTable}.php`.

**Logic dedup** (dùng ở 6/10 hàm: `monthlySensorInfo`, `yearlyAverageSensorInfo`, `weeklyEnergySavingReport`,
`rankingInfo`, `yearlySensorInfo`, `monthlyAverageSensorInfo`): so sánh phần tháng/năm của ngày hiện tại
với ngày NGAY TRƯỚC trong danh sách (`$this->createdate[$index - 1]`), bỏ qua nếu trùng — vì danh sách
ngày luôn được build tăng dần liên tục (14 ngày kế tiếp, hoặc 1 ngày đơn), nên chỉ cần so với phần tử
liền trước là đủ để không tạo trùng partition trong cùng 1 lượt chạy; không so thêm năm khi dedup theo
tháng, nhưng vô hại vì cửa sổ 14 ngày không bao giờ lặp lại cùng số tháng của 2 năm khác nhau.
(`CreateTablePartitionCommand.php:178-182,215-219,252-256,289-293,326-330`)

### A.2.3 Xử lý lỗi — độc lập theo từng partition, không rollback

- Mỗi lần `CREATE TABLE IF NOT EXISTS ...` nằm trong try/catch RIÊNG — lỗi 1 partition (1 bảng, 1
  ngày/tháng/năm cụ thể) chỉ log `alert` kèm tên bảng + range lỗi, KHÔNG throw ra ngoài, KHÔNG dừng các
  partition còn lại (kể cả cùng bảng, ngày khác; hay bảng khác). (`:124-135` và tương tự ở 9 hàm khác)
- Không dùng transaction — `IF NOT EXISTS` khiến việc gọi lại (do cron chạy đè lên ngày đã tạo trong 13
  ngày trước) là vô hại, không lỗi, không ghi đè gì (partition đã tồn tại thì bỏ qua).
- Không có cơ chế retry riêng cho partition bị lỗi — nếu 1 lượt chạy bị lỗi tạo partition cho ngày N,
  chỉ được tạo lại ở lượt chạy NGÀY SAU (khi ngày N vẫn còn nằm trong cửa sổ 14 ngày tới) hoặc phải chạy
  tay bù bằng `--date`.

### A.2.4 Điểm đặc biệt / Rủi ro

- **Đây là batch hạ tầng nền cho rất nhiều batch khác** — grep `EminelSvLib.ConSensor*`/`ConWeeklyEcoReports`/
  `ConRankings`/`ConDeviceStatuses` trong `src/Command/` của `conciergesv` ra **28 file Command khác**
  tham chiếu 1 trong 10 bảng này, trong đó phần lớn (nhóm `Calc*Command`, `RankingCreationCommand`,
  `CreateGroupSummaryCommand`, `DistributeMonthlyEcoPointsCommand`,...) thực sự ghi — chỉ writer mới
  chịu rủi ro lỗi insert khi thiếu partition; riêng `t_202` (trạng thái thiết bị) còn được ghi qua **API**
  `InstructionController` của `hemssv-develop` (server tiếp nhận dữ liệu GW, không phải batch) — nghĩa là
  API nhận dữ liệu thiết bị theo thời gian thực CŨNG phụ thuộc batch này đã tạo sẵn partition ngày hôm
  đó, không chỉ các batch cron.
- **Rủi ro vận hành thật**: nếu batch này ngừng chạy (server down, lỗi triển khai...) liên tục quá 13
  ngày mà không ai chạy tay bù bằng `--date`, các batch/API kể trên sẽ bắt đầu lỗi insert (PostgreSQL
  "no partition of relation found for row") ngay khi chạm ngày chưa có partition — lỗi sẽ xuất hiện ở
  RẤT NHIỀU batch khác nhau cùng lúc, không phải ở chính batch này, gây khó truy nguyên nguyên nhân gốc
  nếu không biết cơ chế này.
- **Cơ chế chống chạy trùng ở tầng ứng dụng** (không riêng batch này, xem thêm `CreateGroupSummary.md`)
  — `BaseCommand` tạo file `.lock` theo PID, dùng chung bởi 18 Command khác trong `conciergesv`
  (19 Command kể cả batch này).
  (`BaseCommand.php:21-38`)
- Range hẹp (chỉ đúng 1 ngày) ở 3/10 bảng tháng/năm (`s_103`, `s_113`, `s_114`) **không phải bug** — đã
  xác nhận trực tiếp cột ngày/năm của các bảng này luôn cố định 1 giá trị/kỳ (xem bảng A.2.2) nên range
  hẹp vẫn khớp đủ 100% dữ liệu thật; chỉ là dễ gây hiểu lầm "bug thiếu dữ liệu" nếu đọc lướt không kiểm
  tra cấu trúc cột thật của bảng đích.

---

# Phần B — Đối chiếu EMINEL-smart (hệ thống mới)

> Không tìm thấy Lambda/cơ chế nào tương đương — không phải vì chưa port, mà vì đổi nền tảng lưu trữ
> khiến bài toán gốc không còn tồn tại. Bảng dưới đây là các khu vực đã tra và bằng chứng cụ thể (thay
> cho B.1/B.2).

## Đã kiểm tra

| Khu vực / candidate | Kết quả |
|---|---|
| Cấu trúc key của 4 bảng time-series lớn nhất trong `template-dynamodb.yaml` | `DeviceAccumulatedHistoryTable` (dòng 1113-1143): PK=`receive_date` (HASH), SK=`history_id` (RANGE), GSI `gsi_tagtag_kaiin_bango`. `DeviceDailyUsageHistoryTable` (:1145-1175), `DeviceMonthlyUsageHistoryTable` (:1177-1207), `DeviceStatusHistoryTable` (:1209-1239) — cùng cấu trúc key. Cả 4 đều `BillingMode: PAY_PER_REQUEST`, có `TimeToLiveSpecification` (attribute `ttl`). `receive_date` chỉ là GIÁ TRỊ của partition key (string thường), không phải "bảng con"/partition object cần pre-provision. |
| Grep `partition`/`CreateTable`/`create-table`/`provision-table`/`provision.?capacity` trên toàn `src/functions/`, `src/statemachine/`, `src/` | 0 kết quả liên quan (chỉ có 1 dòng comment về throughput ở `write-multiple-transaction.ts:34`, không liên quan tạo/provision partition). |
| Toàn bộ `ScheduleV2`/`cron(...)` trong `template.yaml` | Chỉ có 3 lịch cron trong toàn hệ thống (`BatchRunSequentiallyStateMachine`, `BatchMigrationIntegratedDataStateMachine`, `BatchGetErrorDeviceInfoOfRinnaiStateMachine`) — cả 3 đều là batch xử lý dữ liệu nghiệp vụ (import/export/migration), không có function nào mang tính "hạ tầng" (tạo bảng, set capacity, tạo partition). |

---

## Tổng kết

**Bài toán gốc mà batch cũ giải quyết không tồn tại trong kiến trúc mới, chứ không phải bị bỏ sót:**

- Batch cũ tồn tại vì PostgreSQL declarative partitioning yêu cầu partition con phải được tạo trước khi
  có bản ghi rơi vào range đó — 1 giới hạn kỹ thuật CỦA RIÊNG cơ chế partition PostgreSQL, không phải
  yêu cầu nghiệp vụ độc lập với nền tảng lưu trữ.
- DynamoDB (nền tảng lưu trữ của hệ thống mới) không có khái niệm "partition con theo thời gian cần tạo
  trước" — partition trong DynamoDB là cơ chế nội bộ tự động theo hash key, hoàn toàn trong suốt với ứng
  dụng. Xác nhận trực tiếp: 4 bảng time-series lớn nhất đều là 1 bảng duy nhất, tồn tại vĩnh viễn, không
  hề có bảng/resource nào được tạo động lúc runtime trong toàn bộ `template.yaml`/`template-dynamodb.yaml`.
- Vì vậy đây KHÔNG phải trường hợp "1 cơ chế khác về chất thay thế cùng 1 nhiệm vụ" theo nghĩa thông
  thường (như `SendAlertLogMail`) — mà là nhiệm vụ đó **không còn cần làm nữa**, do lựa chọn nền tảng
  lưu trữ khác đã loại bỏ hẳn giới hạn kỹ thuật sinh ra nhiệm vụ này từ đầu.

**Điểm cần lưu ý khi so sánh với cơ chế "cặp đôi" ở hệ cũ (tạo trước ↔ dọn sau):**

- Ở hệ cũ, `CreateTablePartitionCommand` (tạo partition trước) đi cùng với `DeleteDataCommand`
  (`DROP TABLE {partitionName}` — xác nhận trực tiếp `DeleteDataCommand.php:91,116,187`) làm nhiệm vụ
  NGƯỢC LẠI: xóa partition cũ để dọn dữ liệu hết hạn lưu trữ. Cả 2 batch cùng xoay quanh 1 cơ chế
  PostgreSQL partitioning duy nhất — 1 đầu tạo, 1 đầu xóa.
- Ở hệ mới, cả 2 nhiệm vụ này (tạo trước ĐỂ ghi được + xóa sau ĐỂ hết hạn lưu trữ) đều được thay bằng
  **1 cơ chế tự động duy nhất của DynamoDB**: thuộc tính `ttl` (`TimeToLiveSpecification`) tự xóa bản ghi
  hết hạn, không cần batch nào chạy định kỳ để dọn; còn việc "ghi được ngay" thì không cần chuẩn bị gì
  trước cả. Đây LÀ điểm đáng đúc kết: không phải 1 batch biến mất do thiếu tính năng, mà 2 batch cũ
  (tạo + xóa) cùng được thay bằng 1 thuộc tính khai báo tĩnh trong schema — không có Lambda/cron nào
  tương ứng để so sánh trực tiếp được nữa.

---

## Nguồn

| Phần | Nội dung | Căn cứ |
|---|---|---|
| Hệ thống cũ | Logic chính | `sources/conciergesv-develop/src/Command/CreateTablePartitionCommand.php` |
| Hệ thống cũ | Cơ chế lock chống chạy trùng (dùng chung) | `sources/conciergesv-develop/src/Command/BaseCommand.php` |
| Hệ thống cũ | Hằng số phạm vi ngày tạo trước | `sources/conciergesv-develop/config/const.php:720` |
| Hệ thống cũ | Cấu trúc PK/tên bảng của 10 bảng partition | `sources/eminel_sv_lib-develop/src/Model/Table/{ConSensorMemoryValuesTable,ConSensorHourlyValuesTable,ConSensorDailyValuesTable,ConSensorMonthlyValuesTable,ConSensorHourlyAveValuesTable,ConSensorDailyAveValuesTable,ConSensorMonthlyAveValuesTable,ConWeeklyEcoReportsTable,ConRankingsTable,ConDeviceStatusesTable}.php` |
| Hệ thống cũ | Ý nghĩa cột ngày của từng bảng (hẹp vs rộng range) | `sources/eminel_sv_lib-develop/src/Model/Entity/{ConSensorHourlyValue,ConSensorDailyValue,ConSensorMonthlyValue,ConWeeklyEcoReport,ConRanking}.php` |
| Hệ thống cũ | 28 Command khác tham chiếu các bảng này (cross-cutting, đếm thật) | grep `EminelSvLib.ConSensor*`/`ConWeeklyEcoReports`/`ConRankings`/`ConDeviceStatuses` trong `sources/conciergesv-develop/src/Command/` |
| Hệ thống cũ | API cũng ghi `t_202` (ngoài batch) | `sources/hemssv-develop/src/Controller/InstructionController.php:635` |
| Hệ thống cũ | Lịch chạy (cron) | `docs/02_詳細設計/10_バッチ処理/mng-webap_cron設定_20241029.txt:45-46` |
| Hệ thống cũ | Danh sách batch (mô tả tiếng Nhật, nhóm server) | `docs/03_API仕様/04_バッチ一覧.md:75` |
| Hệ thống mới | Cấu trúc key 4 bảng time-series lớn nhất (xác nhận không cần pre-partition) | `template-dynamodb.yaml:1113-1239` (`DeviceAccumulatedHistoryTable`, `DeviceDailyUsageHistoryTable`, `DeviceMonthlyUsageHistoryTable`, `DeviceStatusHistoryTable`) |
| Hệ thống mới | Cơ chế tự xóa hết hạn (thay cho `DeleteDataCommand` phía DROP partition) | `template-dynamodb.yaml` — `TimeToLiveSpecification` (attribute `ttl`) của 4 bảng trên |
| Hệ thống mới | Toàn bộ lịch cron trong hệ thống (xác nhận không có cron nào làm nhiệm vụ hạ tầng tương tự) | `template.yaml` (`BatchRunSequentiallyStateMachine:877-882`, `BatchMigrationIntegratedDataStateMachine:2228-2234`, `BatchGetErrorDeviceInfoOfRinnaiStateMachine:2974-2980`) |
| Hệ thống cũ | Cơ chế xóa partition cũ (đối chứng phía "dọn sau" của cặp đôi tạo/xóa) | `sources/conciergesv-develop/src/Command/DeleteDataCommand.php:91,116,187` |
