# Batch cũ — CalcYearlyRoomTemperatureCommand（年毎室温データ算出）

## Tóm tắt

`CalcYearlyRoomTemperatureCommand` là batch chạy **1 lần/tháng** trong hệ thống cũ (EMINEL コンシェルジュサーバー), gộp **31 cột-ngày trong 1 tháng** của bảng nhiệt độ phòng trung bình theo ngày (`s_103`, do batch `CalcMonthlyRoomTemperatureCommand` ghi trước đó) thành **1 giá trị trung bình THÁNG duy nhất**, cho từng hộ × từng vị trí cảm biến (E0/E1), rồi ghi vào bảng theo năm `s_104` (mỗi dòng gồm 12 cột — 1 cột/tháng trong năm). Ngoài tháng đang tính (mặc định là tháng trước), batch còn tính lại (tái tính) đúng **1 tháng liền trước đó nữa** để bù dữ liệu nguồn đến muộn/được sửa sau khi đã tính, rồi đánh dấu lại các dòng nguồn `s_103` đã xử lý là "đã tổng hợp". Batch chỉ đọc/ghi DB (không gửi mail, không xuất file). Tên batch ghi "Yearly" vì bảng đích lưu 1 dòng = 1 hộ × 1 năm × 12 cột tháng — đó là đơn vị **lưu trữ**; đơn vị **tính** của batch này vẫn là 1 tháng (mỗi lần chạy tính và ghi đúng 2 cột tháng: tháng đang tính + tháng liền trước). Chi tiết lịch chạy, câu SQL, công thức tính và các batch dùng lại kết quả này trình bày ở Phần 2.

## Phần 1 — Tổng quát

| Mục | Nội dung |
|---|---|
| **Vai trò** | Gộp (nhiều→một) các giá trị nhiệt độ phòng trung bình theo NGÀY (đã có sẵn ở `s_103`) trong 1 tháng thành 1 giá trị trung bình THÁNG/hộ/vị trí cảm biến, làm dữ liệu nguồn cho màn hình xem lịch sử nhiệt độ phòng theo năm trên app. |
| **Input** | Chỉ đọc DB, **không gọi API ngoài, không đọc file CSV**: `t_101`（danh sách hộ）＋ `s_103`（nhiệt độ phòng trung bình theo ngày của từng hộ, do batch `CalcMonthlyRoomTemperatureCommand` tính sẵn, điều kiện `device_type=6`）＋ tham số dòng lệnh `--yearmonth`. |
| **Output** | **Chỉ ghi DB** — với mỗi hộ × vị trí cảm biến có kết quả, ghi/cập nhật **1 cột tháng** trong **1 dòng-năm** của `s_104`（entity `ConSensorMonthlyValue`, qua thư viện chung `EminelSvLib`）; đồng thời cập nhật cờ `need_agg_complete_flag` trên `s_103` để đánh dấu các dòng-tháng đã tổng hợp. Không gửi mail, không xuất CSV. |
| **Khái quát xử lý** | 1. Xác định "tháng tính" (tham số `--yearmonth`, mặc định = tháng hiện tại trừ 1 tháng); sai format → abort ngay.<br>2. Query lấy tổng 31 cột-ngày + số ngày có dữ liệu của `s_103` cho đúng tháng tính, theo từng hộ × vị trí cảm biến; lỗi query → abort ngay (chưa mở transaction).<br>3. Mở transaction; với mỗi hộ có dữ liệu, tính trung bình tháng = tổng/số ngày có dữ liệu, ghi vào đúng cột-tháng trong dòng-năm ở `s_104`; đánh dấu mọi dòng `s_103` vừa đọc là đã tổng hợp.<br>4. Lặp lại đúng bước 2-3 nhưng cho **đúng 1 tháng liền trước** tháng tính (tái tính).<br>5. Toàn bộ (bước 3+4) nằm trong 1 transaction; lỗi ở bất kỳ bước ghi/query nào bên trong transaction → rollback. |

## Phần 2 — Chi tiết

### 2.1 Lịch chạy & tham số

| Mục | Nội dung | Nguồn |
|---|---|---|
| Lịch chạy (cron) | `20 5 1 * *` (định dạng /etc/cron.d, chạy bởi user `root`) — 1 lần/tháng, ngày 1 lúc 05:20, chạy **quanh năm** (không giới hạn theo mùa) | `docs/02_詳細設計/10_バッチ処理/mng-webap_cron設定_20241029.txt:52` (`#15.年毎室温データ算出` → `15_CalcYearlyRoomTemperature.sh`) |
| Command thực thi | `php cake.php CalcYearlyRoomTemperature [--yearmonth=<yyyy-MM>]` | `CalcYearlyRoomTemperatureCommand.php:46,63` |
| Tham số `yearmonth` (khi không truyền) | `hiện tại − 1 tháng`, format `yyyy/MM/01` | `CalcYearlyRoomTemperatureCommand.php:66-68` |
| Tham số `yearmonth` (khi có truyền) | Validate format `yyyy-MM` bằng regex `^[0-9]{4}-(0[1-9]|1[0-2])$`; sai format → log ALERT rồi `abort('failed validateCalcMonth')` — trước khi đụng DB | `CalcYearlyRoomTemperatureCommand.php:70-81,414-425` |
| Tháng tính chính (`calculationMonth`) | Đúng 1 tháng (ngày 01 của tháng), dùng làm khóa dòng-tháng trong `s_103` | `CalcYearlyRoomTemperatureCommand.php:88` |

### 2.2 Lấy dữ liệu tháng đang tính (`getSensorMonthlyValue`)

```sql
SELECT ConSensorDailyValues.c001, ConSensorDailyValues.c002, ConSensorDailyValues.c003, ConSensorDailyValues.c004
     , ConCustomers.c012 AS c111, ConCustomers.c042 AS c112
     , ConCustomers.c015 AS c113, ConCustomers.c016 AS c114, ConCustomers.c024 AS c115
     , COALESCE(c011,0)+COALESCE(c012,0)+ ... +COALESCE(c041,0) AS total        -- tổng 31 cột-ngày, NULL tính là 0
     , (CASE WHEN c011 IS NULL THEN 0 ELSE 1 END)+ ... +(CASE WHEN c041 IS NULL THEN 0 ELSE 1 END) AS totalNumber  -- số ngày có dữ liệu
  FROM t_101 ConCustomers, s_103 ConSensorDailyValues
 WHERE ConCustomers.c001 = ConSensorDailyValues.c001
   AND ConSensorDailyValues.c002 = 6                    -- device_type = ROOM_TEMPERATURE
   AND ConSensorDailyValues.c004 = :targetDate          -- đúng dòng-tháng đang tính (yyyy/MM/01)
   AND ConCustomers.c052 IS NULL                          -- Hộ chưa bị xóa logic
 ORDER BY ConSensorDailyValues.c001
```
Nguồn: `CalcYearlyRoomTemperatureCommand.php:352-406` (build chuỗi SQL cộng 31 cột ngày tại dòng 359-373, câu SQL tại 375-393).

**Ý nghĩa các cột dùng trong câu SQL:**

| Bảng | Cột | Ý nghĩa |
|---|---|---|
| `t_101` | `c001` | Mã hộ（EMS-SP）— khóa nối |
| `t_101` | `c012`,`c042`,`c015`,`c016`,`c024` | 5 thuộc tính nhóm hộ (kết cấu nhà, công suất sưởi, diện tích sàn, số người, đồng phát gas) — copy nguyên sang `s_104` làm `c111`〜`c115` |
| `t_101` | `c052` | Thời điểm xóa logic — `IS NULL` = hộ còn hiệu lực |
| `s_103` | `c001` | Mã hộ — khóa nối |
| `s_103` | `c002` | Loại thiết bị — lọc cố định `= 6` |
| `s_103` | `c003` | Vị trí cảm biến (0 = E0, 1 = E1) — mỗi hộ có tối đa 2 dòng, 1/vị trí |
| `s_103` | `c004` | Dòng-tháng — lọc đúng tháng đang tính |
| `s_103` | `c011`〜`c041` | 31 giá trị nhiệt độ trung bình theo ngày (ngày 1〜31 trong tháng), có thể NULL |

Nếu câu SQL lỗi → `resultCode = false` → **`io->abort('failed getSensorMonthlyValue')` ngay lập tức, TRƯỚC khi mở transaction** (khác các bước lỗi bên trong transaction, chỉ `rollback()` chứ không gọi `abort()` — xem mục 2.6).

### 2.3 Tính trung bình & ghi kết quả — bảng đích `s_104` (`updateSensorYearlyValue`)

```
Với mỗi dòng kết quả (1 hộ × 1 vị trí cảm biến):
① Nếu total = 0 HOẶC totalnumber = 0 → BỎ, không ghi (code chỉ ghi khi CẢ HAI ≠ 0 — tháng có ngày dữ liệu nhưng tổng đúng bằng 0 cũng bị bỏ, không chỉ riêng trường hợp không có ngày nào có dữ liệu)
② Ngược lại → trung bình tháng = total / totalnumber (KHÔNG có bước kiểm tra ngưỡng số ngày tối thiểu)
③ Ghi vào s_104:
   - Khóa: ems_sp, device_type (= 6, lấy từ dòng s_103), room_id (0/1, lấy từ dòng s_103),
     date = năm chứa calculationMonth (số nguyên yyyy)
   - Cột tháng tương ứng: c0(tháng_của_calculationMonth + 10) = trung bình tháng
     (ví dụ calculationMonth = tháng 3 → cột c013; tháng 12 → cột c022)
   - group_attr1〜5 = 5 thuộc tính nhóm lấy từ t_101 (mục 2.2)
   - modified = thời điểm hiện tại
④ Nếu ghi 1 hộ bị lỗi (exception) → log ALERT, resultCode = false, KHÔNG dừng vòng lặp — tiếp tục ghi các hộ còn lại
```
Nguồn: `CalcYearlyRoomTemperatureCommand.php:292-344`.

Sau khi vòng lặp kết thúc, **nếu `resultCode` vẫn còn `true`** → gọi tiếp `updateSourceData` (mục 2.4) để đánh dấu nguồn; nếu đã `false` thì bỏ qua bước đánh dấu nguồn.

### 2.4 Đánh dấu nguồn `s_103` đã tổng hợp (`updateSourceData`)

```
Chạy với TẤT CẢ các dòng đã lấy được ở bước query (mục 2.2 hoặc mục 2.5.1) —
kể cả những dòng bị BỎ ở bước 2.3/2.5.2 vì total=0 hoặc totalnumber=0:
① Ghi vào s_103 (ConSensorDailyValue, không phải s_104):
   - Khóa: ems_sp, device_type (= hằng số ROOM_TEMPERATURE = 6, gán cứng — không lấy từ dòng dữ liệu),
     room_id (lấy từ dòng dữ liệu), date = đúng dòng-tháng của dòng dữ liệu (yyyy/MM/01)
   - need_agg_complete_flag = 2
   - modified = thời điểm hiện tại
② Nếu ghi 1 hộ bị lỗi (exception) → log ALERT, resultCode = false, KHÔNG dừng vòng lặp — tiếp tục các hộ còn lại
```
Nguồn: `CalcYearlyRoomTemperatureCommand.php:187-217`. Hàm này dùng chung cho cả 2 nhánh — sau `updateSensorYearlyValue` (mục 2.3) và sau `updateRecalculationData` (mục 2.5.2).

### 2.5 Tái tính toán đúng 1 tháng liền trước

#### 2.5.1 Lấy dữ liệu tái tính (`getRecalculationData`)

```sql
-- Cấu trúc SQL giống hệt mục 2.2, khác điều kiện lọc tháng:
...
   AND ConSensorDailyValues.c004 = :targetDate     -- ngày 01 của (tháng calculationMonth − 1 tháng)
...
```
- `targetDate` = ngày 01 của (tháng `calculationMonth` − 1 tháng); nếu `calculationMonth` ở tháng 1, phép trừ tháng tự lùi về tháng 12 năm trước.
- Chỉ lấy đúng **1 dòng-tháng** (bằng, không phải khoảng) — khác `CalcMonthlyRoomTemperatureCommand` (tái tính cả khoảng "tháng này + tháng trước"), batch này chỉ lùi lại đúng 1 tháng.

Nguồn: `CalcYearlyRoomTemperatureCommand.php:225-283` (targetDate tại dòng 230, câu SQL tại 252-270).

#### 2.5.2 Ghi kết quả tái tính vào `s_104` (`updateRecalculationData`)

```
Với mỗi dòng kết quả (1 hộ × 1 vị trí cảm biến, thuộc tháng liền trước calculationMonth):
① Nếu total = 0 HOẶC totalnumber = 0 → BỎ, không ghi (code chỉ ghi khi CẢ HAI ≠ 0 — tháng có ngày dữ liệu nhưng tổng đúng bằng 0 cũng bị bỏ, không chỉ riêng trường hợp không có ngày nào có dữ liệu)
② Ngược lại → trung bình tháng = total / totalnumber
③ Ghi vào s_104 (cùng cấu trúc khóa/cột như mục 2.3), nhưng:
   - date = năm chứa NGÀY của dòng dữ liệu (lấy từ c004 của chính dòng đó, không phải calculationMonth)
   - Cột tháng tương ứng = c0(tháng_của_dòng_dữ_liệu + 10)
④ Nếu ghi 1 hộ bị lỗi (exception) → log CRITICAL, resultCode = false, KHÔNG dừng vòng lặp — tiếp tục ghi các hộ còn lại
```
Nguồn: `CalcYearlyRoomTemperatureCommand.php:126-179`.

Sau khi vòng lặp kết thúc, nếu `resultCode` vẫn `true` → gọi `updateSourceData` (mục 2.4) một lần nữa, lần này đánh dấu các dòng `s_103` của **tháng liền trước**.

### 2.6 Transaction

```
1. getSensorMonthlyValue (mục 2.2) — nếu lỗi SQL → io->abort() ngay, KHÔNG mở transaction, KHÔNG chạy các bước sau
2. Mở transaction
3. updateSensorYearlyValue (mục 2.3, gồm cả updateSourceData mục 2.4) — lỗi → rollback (KHÔNG gọi abort(), hàm execute() vẫn chạy tiếp tới cuối và log "end")
4. getRecalculationData (mục 2.5.1) — lỗi → rollback (không abort)
5. updateRecalculationData (mục 2.5.2, gồm cả updateSourceData mục 2.4) — lỗi → rollback (không abort)
6. Cả 3 bước 3-5 đều thành công → commit
```
Nguồn: `CalcYearlyRoomTemperatureCommand.php:88-115`.

### 2.7 Chuỗi tổng hợp & tính năng dùng kết quả

```
s_103  "ConSensorDailyValue"    1 dòng/hộ/vị trí cảm biến/tháng  × 31 cột ngày   (device_type=6, room_id=0/1)
   │  do CalcMonthlyRoomTemperatureCommand ghi (chạy 1 lần/ngày)
   │
   │  CalcYearlyRoomTemperatureCommand  (☚ batch đang phân tích — chạy 1 lần/tháng)
   │  (gộp CÁC CỘT NGÀY trong 1 tháng của s_103 thành 1 giá trị trung bình tháng,
   │   tính cho tháng đang xét + tái tính 1 tháng liền trước)
   ▼
s_104  "ConSensorMonthlyValue"   1 dòng/hộ/vị trí cảm biến/năm  × 12 cột tháng   (device_type=6, room_id=0/1)
   │
   │  GetUsageController (API màn hình "使用量"／lịch sử sử dụng trên app)
   │  đọc s_104 với device_type=ROOM_TEMPERATURE để trả dữ liệu nhiệt độ phòng theo NĂM
   ▼
Hiển thị biểu đồ nhiệt độ phòng theo năm trên app
```
Nguồn: `GetUsageController.php:1961-2110` (đọc `EminelSvLib.ConSensorMonthlyValues`, lọc `device_type = ROOM_TEMPERATURE`, dùng cho view `YEARLY`).

Batch này **không tự gửi thông báo, không tự tính điểm/thưởng gì** — khác với chuỗi nhiệt độ cài đặt (`CalcYearlyPresetTemperatureCommand` → `DistributeMonthlyEcoPointsCommand`), kết quả của batch này chỉ phục vụ hiển thị.
