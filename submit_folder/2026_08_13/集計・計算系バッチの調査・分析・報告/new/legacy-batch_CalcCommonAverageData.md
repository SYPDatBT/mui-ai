# Batch cũ — CalcCommonAverageDataCommand（平均データ算出 — Common, dùng chung cho Daily/Monthly/Yearly）

## Tóm tắt

`CalcCommonAverageDataCommand` không phải là 1 batch có lịch chạy (cron) riêng — phương thức `execute()` của class này để RỖNG, và trong toàn bộ cấu hình cron (`mng-webap_cron設定_20241029.txt`) không có dòng nào gọi batch này qua CLI. Đây là 1 **class chứa thuật toán dùng chung**, được 3 batch khác khởi tạo và gọi qua phương thức `executeCommon($type, $dateTime, $aggregationUnit)`: `CalcDailyAverageDataCommand` (truyền `aggregationUnit=1`, tính theo GIỜ — xem tài liệu riêng), `CalcMonthlyAverageDataCommand` (truyền `aggregationUnit=2`, tính theo NGÀY — xem tài liệu riêng), `CalcYearlyAverageDataCommand` (truyền `aggregationUnit=3`, tính theo THÁNG — xem tài liệu riêng). Cả 3 batch chạy ĐÚNG CÙNG 1 thuật toán 3 bước (tính trung bình nhóm chi tiết → tính trung bình nhóm gộp rộng hơn → truy hồi các kỳ trước còn thiếu dữ liệu) nằm trong class này; điểm khác nhau chỉ là bộ tham số bảng nguồn/bảng đích/tên cột do `aggregationUnit` quyết định. Batch chỉ đọc/ghi DB (không gửi mail, không xuất file). Tài liệu này mô tả chi tiết thuật toán chung đó; lịch cron, tham số dòng lệnh và hằng số loại chỉ số tiêu thụ riêng của từng đơn vị nằm ở 3 tài liệu của batch gọi nó.

## Phần 1 — Tổng quát

| Mục | Nội dung |
|---|---|
| **Vai trò** | Cung cấp thuật toán CHUNG (3 bước: trung bình nhóm chi tiết → trung bình nhóm gộp rộng → truy hồi kỳ trước còn thiếu) để gộp nhiều hộ cùng thuộc tính nhà ở thành 1 số trung bình nhóm, dùng lại cho cả 3 đơn vị tính GIỜ/NGÀY/THÁNG. |
| **Input** | Không tự nhận tham số dòng lệnh — chỉ nhận qua lời gọi hàm `executeCommon($type, $dateTime, $aggregationUnit)` từ 1 trong 3 batch gọi nó. Chỉ đọc DB: bảng giá trị theo từng hộ tương ứng đơn vị (`s_102`/`s_103`/`s_104`) + bảng đích tổng hợp nhóm (`s_112`/`s_113`/`s_114`, dùng lại để tìm kỳ còn thiếu dữ liệu) + bảng tra "mẫu số nhóm": unit=1 và unit=2 tra `s_113`, unit=3 tra `s_114` (riêng unit=1 là đọc CHÉO sang bảng của đơn vị ngày — xem 2.4). |
| **Output** | Ghi vào 1 trong 3 bảng tổng hợp nhóm `s_112`/`s_113`/`s_114` tuỳ `aggregationUnit` — không gửi mail, không xuất CSV. |
| **Khái quát xử lý** | 1. Nhận `type`+`dateTime`+`aggregationUnit` từ batch gọi, suy ra bộ tham số bảng nguồn/đích/cột tương ứng.<br>2. Mở 1 transaction cho toàn bộ.<br>3. Tính trung bình theo nhóm chi tiết (5 thuộc tính nhà ở, chỉ ghi nếu đủ ≥70% mẫu số nhóm).<br>4. Tính tiếp trung bình theo nhóm gộp rộng hơn (bỏ 3/5 thuộc tính, không kiểm tra ngưỡng) làm phương án dự phòng.<br>5. Truy hồi các kỳ trước còn thiếu dữ liệu (tối đa ~7 ngày/1 tháng/1 năm tuỳ đơn vị); commit nếu mọi bước thành công, ngược lại rollback toàn bộ. |

## Phần 2 — Chi tiết

### 2.1 Không có lịch chạy riêng — chỉ được gọi từ 3 batch khác

| Batch gọi | `aggregationUnit` truyền vào | Đơn vị tính trung bình | Tài liệu chi tiết (lịch cron, tham số CLI, hằng số loại chỉ số) |
|---|---|---|---|
| `CalcDailyAverageDataCommand` | `1` | Theo GIỜ | `docs/CalcDailyAverageDataCommand/legacy-batch_CalcDailyAverageData.md` |
| `CalcMonthlyAverageDataCommand` | `2` | Theo NGÀY | `docs/CalcMonthlyAverageDataCommand/legacy-batch_CalcMonthlyAverageData.md` |
| `CalcYearlyAverageDataCommand` | `3` | Theo THÁNG | `docs/CalcYearlyAverageDataCommand/legacy-batch_CalcYearlyAverageData.md` |

Cả 3 batch đều khởi tạo `new CalcCommonAverageDataCommand()` rồi gọi `executeCommon($type, $dateTime, $aggregationUnit)` — không có route CLI (`cake.php CalcCommonAverageData ...`) nào cho class này; tham số `type`/`datetime` khai báo ở `buildOptionParser()`/`execute()` của class này không được dùng thực tế.

Nguồn: `CalcCommonAverageDataCommand.php:62-105`; `CalcDailyAverageDataCommand.php:77-80`; `CalcMonthlyAverageDataCommand.php:74-77`; `CalcYearlyAverageDataCommand.php:74-77`.

### 2.2 Bảng tham số hoá theo `aggregationUnit` (`getAggregationUnitParameters`)

| Tham số | `aggregationUnit=1` (Giờ) | `aggregationUnit=2` (Ngày) | `aggregationUnit=3` (Tháng) |
|---|---|---|---|
| `targetDateTime` mặc định (khi không truyền `dateTime`) | hiện tại − 1 giờ | hiện tại − 1 ngày | hiện tại − 1 tháng |
| `targetDateCondition` | `yyyy/MM/dd` của `targetDateTime` | `yyyy/MM/01` của `targetDateTime` | `yyyy` của `targetDateTime` |
| `aggregateColumn` | `c0{giờ+11}` (giờ 0→`c011`, 23→`c034`) | `c0{ngày+10}` (ngày 1→`c011`, 31→`c041`) | `c0{tháng+10}` (tháng 1→`c011`, 12→`c022`) |
| `sourceTable` | `s_102`（`ConSensorHourlyValue`） | `s_103`（`ConSensorDailyValue`） | `s_104`（`ConSensorMonthlyValue`） |
| `destinationTable` | `s_112`（`ConSensorHourlyAveValue`） | `s_113`（`ConSensorDailyAveValue`） | `s_114`（`ConSensorMonthlyAveValue`） |
| `periodColumn` | `c004` | `c004` | `c004` |
| `retroactiveTable` | `s_112` (chính bảng đích) | `s_113` (chính bảng đích) | `s_114` (chính bảng đích) |
| `previousColum` | Cột giờ liền trước | Cột ngày liền trước | Cột tháng liền trước |

Nguồn: `CalcCommonAverageDataCommand.php:1235-1334`.

### 2.3 Ví dụ minh hoạ cụ thể theo từng batch gọi

Cùng 1 thuật toán, nhưng cột đọc/ghi thực tế khác nhau theo `aggregationUnit`. Giả sử cả 3 ví dụ dưới đây đều tính cho `type=5` (`POWER_CONSUMPTION` — 消費電力量/điện tiêu thụ):

**`CalcDailyAverageDataCommand` gọi với `aggregationUnit=1`** — ví dụ `--datetime=2024-06-15T08:00:00+09:00`:
- `targetDateTime` = `2024-06-15 08:00:00` → `targetDateCondition` = `2024/06/15`; giờ cần tính = **08** → `aggregateColumn` = `c0(8+11)` = **`c019`**.
- Bước 1 đọc từ `s_102` (đã được batch khác tính sẵn theo từng hộ): các cột `c002` (device_type=5), `c003` (room_id), `c004` (=`2024/06/15`), `c111`~`c115` (5 thuộc tính nhà ở), và **`c019`** (giá trị điện tiêu thụ giờ 08 của từng hộ) — lọc `c004 = '2024/06/15'` và `c019 IS NOT NULL`.
- Ghi ra `s_112`: mỗi nhóm 1 dòng (khoá `c001=5, c002=room_id, c003='2024/06/15', c111~c115`), set trung bình vào cột **`c019`** (đúng cột giờ 08).
- Bước 3 kiểm tra cột giờ liền trước (07h → `c018`) của `s_112` còn `NULL` không, nếu còn thì lùi tối đa 192 giờ (~8 ngày) để backfill.

**`CalcMonthlyAverageDataCommand` gọi với `aggregationUnit=2`** — ví dụ `--datetime=2024-06-15`:
- `targetDateTime` = `2024-06-15 00:00:00` → `targetDateCondition` = `2024/06/01` (vì `s_103` lưu 1 dòng/tháng); ngày cần tính = **15** → `aggregateColumn` = `c0(15+10)` = **`c025`**.
- Bước 1 đọc từ `s_103`: các cột `c002` (device_type=5), `c003` (room_id), `c004` (=`2024/06/01`), `c111`~`c115`, và **`c025`** (giá trị điện tiêu thụ NGÀY 15 của từng hộ) — lọc `c004 = '2024/06/01'` và `c025 IS NOT NULL`.
- Ghi ra `s_113`: mỗi nhóm 1 dòng/tháng (khoá `c001=5, c002=room_id, c003='2024/06/01', c111~c115`), set trung bình vào cột **`c025`** (đúng cột ngày 15).
- Bước 3 kiểm tra cột ngày liền trước (14 → `c024`) của `s_113` còn `NULL` không, nếu còn thì lùi tối đa 62 ngày, chặn thực tế ở ngày 01/05/2024 (1 tháng trước).

**`CalcYearlyAverageDataCommand` gọi với `aggregationUnit=3`** — ví dụ `--datetime=2024-06`:
- `targetDateTime` = `2024-06-01 00:00:00` → `targetDateCondition` = `2024` (vì `s_104` lưu 1 dòng/năm); tháng cần tính = **06** → `aggregateColumn` = `c0(6+10)` = **`c016`**.
- Bước 1 đọc từ `s_104`: các cột `c002` (device_type=5), `c003` (room_id), `c004` (=`2024`), `c111`~`c115`, và **`c016`** (giá trị điện tiêu thụ THÁNG 6 của từng hộ) — lọc `c004 = '2024'` và `c016 IS NOT NULL`.
- Ghi ra `s_114`: mỗi nhóm 1 dòng/năm (khoá `c001=5, c002=room_id, c003=2024, c111~c115`), set trung bình vào cột **`c016`** (đúng cột tháng 6).
- Bước 3 kiểm tra cột tháng liền trước (05 → `c015`) của `s_114` còn `NULL` không, nếu còn thì lùi tối đa 24 tháng, chặn thực tế ở năm 2023 (1 năm trước).

Nhận xét chung: dù đọc/ghi bảng khác nhau, **công thức đổi từ "đơn vị thời gian" sang tên cột luôn theo dạng `c0{giá trị đơn vị + hằng số lệch}`, sao cho giá trị nhỏ nhất của đơn vị luôn rơi vào cột `c011`** — giờ đánh số từ 0 (0~23) nên lệch `+11` (`0+11=11`); ngày (1~31) và tháng (1~12) đánh số từ 1 nên lệch `+10` (`1+10=11`).

### 2.4 Bước 1 — Trung bình nhóm chi tiết (`updateGroupAverage` → `getGroupAverageCalculation`)

Dùng chung 1 đoạn SQL cho cả 3 đơn vị, chỉ thay `{sourceTable}`/`{periodColumn}`/`{aggregateColumn}` theo bảng 2.2:

```sql
-- Truy vấn con: chuẩn hoá/gộp bucket cho từng thuộc tính nhóm (c111~c115)
SELECT c002, c003, {periodColumn},
       c111,
       CASE WHEN c112 IN (1,2,3) THEN c112 ELSE 201 END AS c112,
       CASE WHEN c113 IN (1,2,3) THEN 301
            WHEN c113 IN (5,6)   THEN 302
            ELSE c113 END AS c113,
       CASE WHEN c114 IN (1,2) THEN 401
            WHEN c114 IN (3,4) THEN 402
            ELSE 403 END AS c114,
       CASE WHEN c115 IN (1,2) THEN c115 ELSE 501 END AS c115,
       {aggregateColumn}
  FROM {sourceTable}
 WHERE c002 = :type
   AND {periodColumn} = :targetDateCondition
   AND c111 IN (1,2) AND c112 IN (1,2,3,4,9) AND c113 IN (1,2,3,4,5,6)
   AND c114 IN (1,2,3,4,5,6) AND c115 IN (1,2,9,10)
   AND {aggregateColumn} IS NOT NULL

-- Truy vấn ngoài: AVG + COUNT theo nhóm đã gộp bucket
SELECT c002, c003, {periodColumn}, c111, c112, c113, c114, c115,
       AVG({aggregateColumn}) AS {aggregateColumn},
       COUNT({aggregateColumn}) AS count
  FROM (<truy vấn con trên>) AS sensorInfo
 GROUP BY c002, c003, {periodColumn}, c111, c112, c113, c114, c115
```
Nguồn: `CalcCommonAverageDataCommand.php:1156-1228`.

5 thuộc tính nhóm `c111`~`c115` (denormalize sẵn từ hồ sơ hộ `t_101` vào bảng nguồn): loại nhà, công suất sưởi, diện tích sàn, số người trong hộ, loại cogeneration.

**Kiểm tra đủ dữ liệu trước khi ghi** (`checkGroupDataNum`, chỉ áp dụng ở bước này):

| | `aggregationUnit=1` | `aggregationUnit=2` | `aggregationUnit=3` |
|---|---|---|---|
| Bảng tra "mẫu số nhóm" | `s_113` | `s_113` | `s_114` |
| Điều kiện `device_type` | `16` (mã giả lập "số hộ", hardcode — không lấy từ `type` truyền vào) | `16` | `16` |
| Cột đối chiếu | `c0{ngày của dateTime + 10}` | `c0{ngày của dateTime + 10}` | `c0{tháng của dateTime + 10}` |

Nếu `count` (số hộ đã báo cáo) / mẫu số nhóm × 100 < `AVERAGE_CALCULATION_THRESHOLD` (**70**), hoặc mẫu số nhóm = 0 → bỏ qua, không ghi nhóm đó ở bước này.

Nhóm đạt ngưỡng → ghi/update 1 bản ghi vào `destinationTable` (khoá: `device_type`, `room_id`, kỳ (`c003`), 5 thuộc tính nhóm đã gộp bucket), set giá trị trung bình vào đúng `aggregateColumn`.

Nguồn: `CalcCommonAverageDataCommand.php:1039-1149`; hằng số `AVERAGE_CALCULATION_THRESHOLD` tại `config/const.php:599`.

### 2.5 Bước 2 — Trung bình nhóm gộp rộng hơn (`updatePartGroupAverage` → `getPartGroupAverageCalculation`)

Chạy ngay sau bước 1, cùng bảng nguồn/đích, nhưng gộp bucket **thô hơn**: chỉ giữ `c111` nguyên bản, `c112` gộp về `1/2/3` hoặc `201`; **`c113`, `c114`, `c115` cố định = `999`** (coi mọi hộ cùng loại nhà là 1 nhóm rộng, bỏ qua công suất sưởi/diện tích sàn/số người/cogeneration). Bước này **không gọi `checkGroupDataNum`** — luôn ghi đè, làm phương án dự phòng khi nhóm chi tiết ở bước 1 chưa đủ ngưỡng 70%.

Nguồn: `CalcCommonAverageDataCommand.php:868-943`.

### 2.6 Bước 3 — Truy hồi kỳ trước còn thiếu dữ liệu (`retroactiveAdjustment`)

Sau khi bước 1–2 hoàn tất cho kỳ hiện tại, `retroactiveAdjustment()` chọn 1 trong 3 hàm theo `aggregationUnit` — cùng khung xử lý, khác đơn vị lùi thời gian:

| | `retroactiveDaily()` (unit=1) | `retroactiveMonthly()` (unit=2) | `retroactiveYearly()` (unit=3) |
|---|---|---|---|
| Bước lùi mỗi lần | 1 giờ (`subHours`) | 1 ngày (`subDays`) | 1 tháng (`subMonths`) |
| Số lần lùi tối đa (giới hạn vòng lặp) | 192 | 62 | 24 |
| Giới hạn thực tế (`retroactiveLimit`) | `targetDateTime − 7 ngày` | Ngày 01 của [tháng tính − 1 tháng] | Năm [năm tính − 1] |
| Cột lệch khi ghi (`columnAdjusted`) | `+11` (giờ) | `+10` (ngày) | `+10` (tháng) |
| Entity ghi kết quả | `ConSensorHourlyAveValue` | `ConSensorDailyAveValue` | `ConSensorMonthlyAveValue` |

Cơ chế chung (`getTargetGroup` → lùi dần → `getAggregationTarget` → `getRetroactiveData` → `updateRetroactiveData`):
1. `getTargetGroup()`: lấy danh sách nhóm trong `retroactiveTable` mà cột kỳ liền trước (`previousColum`) vẫn còn `NULL` — điều kiện `c111 IN (1,2)`, `c112 IN (1,2,3,201)`, `c113 IN (301,4,302,999)`, `c114 IN (401,402,403,999)`, `c115 IN (1,2,501,999)` (khớp cả nhóm chi tiết ở bước 1 và nhóm rộng ở bước 2).
2. Với mỗi nhóm, lùi dần theo bước ở bảng trên, không vượt quá `retroactiveLimit`.
3. Khi lùi sang 1 dòng kỳ lưu trữ khác (ngày/tháng/năm khác dòng hiện tại), gọi `getAggregationTarget()` đọc lại dòng kỳ đó trong `retroactiveTable` để biết cột nào còn `NULL`.
4. Với đoạn còn thiếu: `getRetroactiveData()` tính lại `AVG` từ `sourceTable` theo đúng nhóm (dùng lại 5 thuộc tính đã lưu sẵn trong `retroactiveTable`, KHÔNG gộp bucket lại) cho khung thời gian còn thiếu; `updateRetroactiveData()` ghi đè kết quả vào `retroactiveTable` — tự tính lại khoảng cột cần ghi khi khung thời gian truy hồi vắt qua 2 dòng kỳ liền kề (`getRetroactiveUpdatePeriod`).
5. Dừng lùi tiếp cho 1 nhóm ngay khi gặp kỳ đã có dữ liệu (không `NULL`).

Nguồn: `CalcCommonAverageDataCommand.php:112-407` (3 hàm `retroactiveDaily/Monthly/Yearly`), `418-861` (`updateRetroactiveData`, `getRetroactiveUpdatePeriod`, `getRetroactiveData`, `getAggregationTarget`, `getTargetGroup`).

### 2.7 Transaction & hằng số nghiệp vụ

- Bước 1 → Bước 2 → Bước 3 nằm trong **1 transaction duy nhất cho cả lần gọi `executeCommon`**: bất kỳ bước nào trả về lỗi → `rollback()` toàn bộ; cả 3 bước thành công mới `commit()`.
- Class này **không tự gửi thông báo, không tự đọc dữ liệu để hiển thị** — dữ liệu ghi ra (`s_112`/`s_113`/`s_114`) được API/batch khác đọc để hiển thị "so với hộ tương tự" trên app (nằm ngoài phạm vi command này).

| Hằng số | Giá trị | Nguồn |
|---|---|---|
| `AVERAGE_CALCULATION_THRESHOLD` | 70 (%) — ngưỡng đủ dữ liệu để ghi nhóm chi tiết ở Bước 1 | `const.php:599` |

Danh sách giá trị hợp lệ của tham số `type` (loại chỉ số tiêu thụ) khác nhau theo từng batch gọi (`GAS_CO_TYPE_CONSUMPTION`, `GAS_WATER_HEAT_RATE`, `POWER_CONSUMPTION`, `ROOM_TEMPERATURE`; riêng `CalcYearlyAverageDataCommand` còn nhận thêm `ENERGY_CONSUMPTION`) — do `checkValidate()` nằm ở 3 command gọi, không nằm trong `CalcCommonAverageDataCommand`; xem chi tiết ở 3 tài liệu liệt kê tại mục 2.1.
