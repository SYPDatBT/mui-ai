# Batch cũ — CalcYearlyPresetTemperatureCommand（年毎平均設定温度算出）

## Tóm tắt

`CalcYearlyPresetTemperatureCommand` là batch chạy **1 lần/tháng, chỉ trong mùa sưởi ấm** (ngày 1 của các tháng 1, 2, 3, 4 lúc 16:10) trong hệ thống cũ (EMINEL コンシェルジュサーバー). Mỗi lần chạy, batch gộp **toàn bộ 31 cột-ngày trong 1 tháng** của bảng nhiệt độ cài đặt trung bình theo ngày (`s_103`, do batch `CalcMonthlyAverageSetTemperatureCommand` ghi trước đó) thành **1 giá trị trung bình THÁNG duy nhất cho mỗi hộ** — chỉ tính khi số ngày thiếu dữ liệu trong tháng đủ ít (dưới 10 ngày). Batch chỉ đọc/ghi DB (không gửi mail, không xuất file), kết quả ghi vào bảng `s_104`. Tên batch ghi "Yearly" vì bảng đích lưu 1 dòng = 1 hộ × 1 năm × 12 cột tháng — đó là đơn vị **lưu trữ**; đơn vị **tính** của batch này vẫn là 1 tháng (mỗi lần chạy chỉ tính và ghi đúng 1 cột tháng). Chi tiết lịch chạy, câu SQL, công thức tính và các batch dùng lại kết quả này trình bày ở Phần 2.

## Phần 1 — Tổng quát

| Mục | Nội dung |
|---|---|
| **Vai trò** | Gộp (nhiều→một) các giá trị nhiệt độ cài đặt trung bình theo NGÀY (đã có sẵn ở `s_103`) trong 1 tháng thành 1 giá trị trung bình THÁNG/hộ, làm dữ liệu nguồn cho tính năng thưởng điểm "エコ暖房" (eco sưởi ấm) hàng tháng. |
| **Input** | Chỉ đọc DB, **không gọi API ngoài, không đọc file CSV**: `t_101`（danh sách hộ）＋ `s_103`（nhiệt độ cài đặt trung bình theo ngày của từng hộ, do batch `CalcMonthlyAverageSetTemperatureCommand` tính sẵn, điều kiện `device_type=17`）＋ tham số dòng lệnh `--yearmonth`. |
| **Output** | **Chỉ ghi DB** — mỗi lần chạy, với mỗi hộ có kết quả, ghi/cập nhật **1 cột tháng** trong **1 dòng-năm** của `s_104`（entity `ConSensorMonthlyValue`, qua thư viện chung `EminelSvLib`）. Không gửi mail, không xuất CSV. |
| **Khái quát xử lý** | 1. Xác định "tháng tính" (tham số `--yearmonth`, mặc định = tháng hiện tại trừ 1 tháng).<br>2. Query 1 câu SQL: với mỗi hộ còn hiệu lực, cộng dồn 31 cột-ngày của đúng dòng-tháng trong `s_103`, đếm số ngày có dữ liệu.<br>3. Nếu số ngày thiếu dữ liệu < ngưỡng (10 ngày) → tính trung bình tháng = tổng/số ngày có dữ liệu, làm tròn 1 chữ số thập phân; ngược lại → NULL.<br>4. Với mỗi hộ trong kết quả, ghi/update 1 bản ghi vào `s_104` — set đúng cột-tháng tương ứng của dòng-năm.<br>5. Toàn bộ nằm trong 1 transaction; lỗi ở bước ghi → rollback + dừng; lỗi ở bước query → commit (không rollback) + dừng. |

## Phần 2 — Chi tiết

### 2.1 Lịch chạy & tham số

| Mục | Nội dung | Nguồn |
|---|---|---|
| Lịch chạy (cron) | 2 dòng, cùng chạy `17_CalcYearlyPresetTemperature.sh` lúc **16:10**: `10 16 1 1,2,3 *`（ngày 1 các tháng 1/2/3）, `10 16 1 4 *`（riêng ngày 1 tháng 4） | `docs/02_詳細設計/10_バッチ処理/mng-webap_cron設定_20241029.txt:57-59` (`#17.年毎平均設定温度算出` → `17_CalcYearlyPresetTemperature.sh`) |
| Command thực thi | `php cake.php CalcYearlyPresetTemperature [--yearmonth=<yyyy-MM>]` | `CalcYearlyPresetTemperatureCommand.php:35,58-61` |
| Tham số `yearmonth` (khi không truyền) | `hiện tại − 1 tháng`, format `yyyy-MM` | `CalcYearlyPresetTemperatureCommand.php:58-61` |
| Vì sao cron chạy vào 4 tháng liên tiếp (1,2,3,4) | Tham số mặc định luôn lùi 1 tháng so với ngày chạy; để tính đủ trọn mùa sưởi ấm (12~3) thì ngày chạy phải là 1/1, 1/2, 1/3, 1/4 (tính lần lượt cho tháng 12, 1, 2, 3) — cùng lý do phải chia dòng cron như batch `CalcMonthlyAverageSetTemperatureCommand` | — |

### 2.2 Câu SQL tổng hợp

```sql
WITH calc_monthly AS (
  SELECT monthly.c001 AS ems_sp                        -- Mã hộ
       , monthly.c002 AS device_type
       , monthly.c003 AS location
       , :calcYear AS target_year
       , (CASE WHEN monthly.c011 IS NULL THEN 0 ELSE monthly.c011 END
          + CASE WHEN monthly.c012 IS NULL THEN 0 ELSE monthly.c012 END
          + ... -- cộng dồn hết c012~c041 (31 cột-ngày tổng cộng)
         ) AS temp_sum                                  -- Tổng nhiệt độ cài đặt trung bình các ngày có dữ liệu
       , (CASE WHEN monthly.c011 IS NULL THEN 0 ELSE 1 END
          + CASE WHEN monthly.c012 IS NULL THEN 0 ELSE 1 END
          + ... -- đếm hết c012~c041
         ) AS total_days                                -- Số ngày có dữ liệu trong tháng
       , EXTRACT(DAY FROM DATE_TRUNC('MONTH', :calcDate::DATE) + INTERVAL '1 MONTH' - INTERVAL '1 day') AS days  -- Tổng số ngày của tháng
    FROM t_101 AS customer
    INNER JOIN s_103 AS monthly
       ON customer.c001 = monthly.c001
      AND monthly.c002 = 17                             -- device_type = ROOM_TEMP_SETTING
      AND monthly.c004 = :calcDate                       -- Dòng-tháng cần tính (ngày 01 của tháng)
   WHERE customer.c052 IS NULL                           -- Hộ chưa bị xóa logic
)
SELECT calc_monthly.ems_sp
     , calc_monthly.device_type
     , calc_monthly.location
     , calc_monthly.target_year
     , CASE WHEN (calc_monthly.days - calc_monthly.total_days) < :summaryThreshould
         THEN trunc((calc_monthly.temp_sum / calc_monthly.total_days), 1)
         ELSE NULL
       END AS sensor
  FROM calc_monthly
```
Nguồn: `CalcYearlyPresetTemperatureCommand.php:64-112` (chuỗi SQL được dựng bằng vòng lặp `for ($i = 12; $i <= 41; $i++)`, rút gọn trong khối trên để dễ đọc).

Ý nghĩa các tham số truyền vào:

| Tham số | Giá trị | Ý nghĩa |
|---|---|---|
| `:calcDate` | `<yearmonth>-01 00:00:00` | Khóa dòng-tháng cần đọc trong `s_103` (khớp cách `CalcMonthlyAverageSetTemperatureCommand` ghi: `datetime` = ngày-01 của tháng chứa ngày tính) |
| `:calcYear` | 4 ký tự đầu của `yearmonth` | Năm — dùng làm khóa dòng-năm khi ghi vào `s_104` |
| `:summaryThreshould` | Hằng số `NOT_SUMMARY_DATE_COUNT` = 10 | Số ngày thiếu dữ liệu tối đa cho phép trong tháng |

Nguồn: `CalcYearlyPresetTemperatureCommand.php:103-110`; hằng số tại `const.php:595`.

**Ý nghĩa các cột dùng trong câu SQL:**

| Bảng | Cột | Ý nghĩa | Ghi chú |
|---|---|---|---|
| `t_101` | `c001` | Mã hộ（EMS-SP） | Khóa nối |
| `t_101` | `c052` | Thời điểm xóa logic | `IS NULL` = hộ còn hiệu lực |
| `s_103` | `c001` | Mã hộ | Khóa nối |
| `s_103` | `c002` | Loại thiết bị (device_type) | Lọc cố định `= 17` (`ROOM_TEMP_SETTING`) |
| `s_103` | `c003` | Room id / vị trí | Lấy nguyên trạng (`location`), không lọc |
| `s_103` | `c004` | Datetime dòng-tháng | Lọc đúng 1 tháng đang tính (`= :calcDate`) |
| `s_103` | `c011`~`c041` | 31 cột-ngày — nhiệt độ cài đặt trung bình/ngày (do `CalcMonthlyAverageSetTemperatureCommand` ghi trước) | ⭐ Giá trị dùng để tính trung bình tháng |

### 2.3 Công thức tính (per hộ, gộp cả tháng)

```
① temp_sum   = tổng các cột c011~c041 khác NULL (coi NULL = 0)
② total_days = số cột c011~c041 khác NULL
③ days       = tổng số ngày thực tế của tháng đang tính (28/29/30/31)
④ Nếu (days − total_days) < NOT_SUMMARY_DATE_COUNT (10)
       → trung bình tháng = trunc(temp_sum / total_days, 1)
   Ngược lại (thiếu quá nhiều ngày dữ liệu trong tháng)
       → kết quả = NULL
```
Nguồn: `CalcYearlyPresetTemperatureCommand.php:96-101`.

Không có bước loại giá trị bất thường/ngoài dải hợp lệ — công thức chỉ dựa vào số lượng ngày có dữ liệu, không xét giá trị nhiệt độ cụ thể có hợp lý hay không.

### 2.4 Ghi kết quả — bảng đích `s_104`

- Entity: `ConSensorMonthlyValue` (thư viện chung `EminelSvLib`), bảng vật lý `s_104` — 1 dòng = 1 hộ × 1 năm, 12 cột tháng (`c011`~`c022`, cột tháng = `c0` + (số tháng + 10)).
- Chỉ chạy bước ghi khi câu SQL ở 2.2 trả về ít nhất 1 dòng kết quả. Batch **không** kiểm tra riêng giá trị `sensor` có NULL hay không trước khi ghi — nếu `sensor` là NULL thì cột tháng tương ứng vẫn được set NULL (ghi đè giá trị cũ nếu có).
- Với mỗi hộ trong kết quả: set `ems_sp`, `device_type = 17`, `room_id = 0`, `datetime = target_year` (năm dạng số nguyên, dùng làm khóa dòng-năm), set giá trị vào đúng cột tháng (`c0` + (tháng đang tính + 10)), cập nhật `modified`.
- Toàn bộ nằm trong **1 transaction cho cả batch**: nếu ghi thất bại ở bất kỳ hộ nào → `rollback()` toàn bộ và `abort()`, không có cơ chế ghi từng phần.
- Nếu câu SQL tổng hợp ở 2.2 lỗi → batch gọi `commit()` (**không** `rollback()`) rồi `abort()` ngay — khác với nhánh lỗi khi ghi kết quả (dùng `rollback()`); cùng kiểu không nhất quán như batch `CalcMonthlyAverageSetTemperatureCommand`.

Nguồn: `CalcYearlyPresetTemperatureCommand.php:113-152`.

### 2.5 Chuỗi tổng hợp & tính năng dùng kết quả

Batch này là mắt xích thứ 2 trong chuỗi tổng hợp nhiệt độ cài đặt (sau `CalcMonthlyAverageSetTemperatureCommand`):

```
s_103  "ConSensorDailyValue"    1 dòng/hộ/tháng  × 31 cột ngày   (device_type=17, room_id=0)
   │  do CalcMonthlyAverageSetTemperatureCommand ghi (chạy 1 lần/ngày, mùa sưởi ấm)
   │
   │  CalcYearlyPresetTemperatureCommand  (☚ batch đang phân tích — chạy 1 lần/tháng)
   │  (gộp CÁC CỘT NGÀY trong 1 tháng của s_103 thành 1 giá trị trung bình tháng,
   │   CHỈ tính khi số ngày có dữ liệu ≥ (số ngày trong tháng − NOT_SUMMARY_DATE_COUNT=10))
   ▼
s_104  "ConSensorMonthlyValue"   1 dòng/hộ/năm  × 12 cột tháng   (device_type=17, room_id=0)
   │
   │  DistributeMonthlyEcoPointsCommand
   │  (chạy 1 lần/tháng, đọc đúng cột-tháng liền trước của s_104;
   │   nếu giá trị ≤ 22.0°C → cộng 250 điểm "エコ暖房" cho hộ,
   │   chặn cộng trùng bằng log lý do "monthly_eco_points_YYYYMM")
   ▼
Hộ được cộng điểm eco qua ConEcoPoints / PointInfinity
```

Nguồn: `DistributeMonthlyEcoPointsCommand.php:33,79-114` (`BENEFIT_POINTS=250`).

Lưu ý: `GetEcoPointsController` (API hiển thị điểm eco cho app) **không** đọc `s_104` — nó đọc thẳng dòng-tháng của `s_103` (`ConSensorDailyValues`) để tự tính lại trung bình tháng khi hiển thị, độc lập với kết quả batch này ghi ra.

Nguồn: `GetEcoPointsController.php:106-118`.
