# Batch cũ — CalcWeeklySavingReportUsingCommand（ガス・電気週間使用量算出機能）

## Tóm tắt

`CalcWeeklySavingReportUsingCommand` là batch chạy **1 lần/tuần** (Chủ Nhật) trong hệ thống cũ (EMINEL コンシェルジュサーバー), tính **tổng lượng gas và tổng lượng điện mà hộ đã dùng trong 7 ngày gần nhất**, cộng dồn từ dữ liệu cảm biến theo tháng (vì không có đồng hồ đo trực tiếp theo tuần). Cùng lúc, batch "dịch chuyển" giá trị "tuần trước" đã tính ở lần chạy trước thành "tuần trước nữa" của lần chạy này, để dòng báo cáo mới có đủ 2 mốc so sánh. Batch chỉ đọc/ghi DB (không gửi mail, không xuất file), kết quả được ghi vào bảng `s_105` — cùng bảng với batch song hành `CalcWeeklySavingReportEffectCommand` (tính số tiền gas tiết kiệm được, chạy 20 phút sau). Chi tiết công thức, câu SQL và cơ chế ghi DB trình bày ở Phần 2.

## Phần 1 — Tổng quát

| Mục | Nội dung |
|---|---|
| **Vai trò** | Hộ không có đồng hồ đo gas/điện theo tuần, nên phải **cộng dồn từ dữ liệu cảm biến hàng ngày (đã tổng hợp theo tháng)** để ra tổng lượng gas và tổng lượng điện đã dùng trong 7 ngày gần nhất; đồng thời kế thừa giá trị "tuần trước" của dòng report gần nhất (lần chạy trước) thành "tuần trước nữa" của dòng report mới, vì mỗi lần chạy chỉ tính lại đúng 1 tuần gần nhất, không tính lại lịch sử. |
| **Input** | Chỉ đọc DB, **không gọi API ngoài, không đọc file CSV**: `t_101`（danh sách hộ, dùng để lọc hộ chưa xóa logic）＋ `s_103`（dữ liệu cảm biến theo tháng, đã tổng hợp sẵn — lấy tổng lượng gas/điện dùng của 7 ngày trước ngày tính）＋ `s_105`（chính bảng đích — đọc dòng report gần nhất trước ngày tính để lấy "tuần trước" chuyển thành "tuần trước nữa"）＋ bảng cảm biến theo giờ (entity `ConSensorHourlyValue`, dùng để kiểm tra dữ liệu gas có bị thiếu không). |
| **Output** | **Chỉ ghi DB** — mỗi lần chạy, với mỗi hộ có trong kết quả tính, ghi/cập nhật (upsert) 1 dòng vào `s_105`（entity `ConWeeklyEcoReport`, qua thư viện chung `EminelSvLib`）, chỉ set các cột liên quan đến "lượng gas/điện đã dùng" (các cột thuộc batch song hành `CalcWeeklySavingReportEffectCommand` được đặt `dirty=false` — không đụng tới). Không gửi mail, không xuất CSV. |
| **Khái quát xử lý** | 1. Xác định "ngày tính" (`calcDate` — tham số đầu vào, hoặc ngày hiện tại nếu không truyền).<br>2. Query `s_103` lấy tổng lượng gas dùng (device_type=2) và tổng lượng điện dùng (device_type=5) của 7 ngày trước `calcDate`, theo từng hộ, kèm số ngày thực có dữ liệu.<br>3. Query `s_105` lấy dòng report gần nhất (tuần trước) của từng hộ, chuyển "lượng gas/điện tuần trước" của dòng đó thành "lượng gas/điện tuần trước nữa" của dòng sắp ghi.<br>4. Với mỗi hộ: nếu đủ 7 ngày dữ liệu gas và không thiếu dữ liệu giờ (check thêm ở bảng cảm biến theo giờ, 23h ngày trước `calcDate`) → tính lượng gas tuần trước (làm tròn) + giá trị hiển thị; tương tự cho điện (không có bước check giờ); thiếu điều kiện → null.<br>5. Ghi/cập nhật 1 dòng/hộ vào `s_105` (giữ nguyên các cột thuộc batch song hành), toàn bộ trong 1 transaction cho cả batch. |

## Phần 2 — Chi tiết

### 2.1 Lịch chạy & tham số

| Mục | Nội dung | Nguồn |
|---|---|---|
| Lịch chạy (cron) | `30 4 * * 7` — 1 lần/tuần, Chủ Nhật 04:30 | `docs/02_詳細設計/10_バッチ処理/mng-webap_cron設定_20241029.txt:70-71` (`#21.ガス・電気週間使用量算出機能` → `21_CalcWeeklySavingReportUsing.sh`) |
| Command thực thi | `php cake.php CalcWeeklySavingReportUsing [算出日]` (tham số dạng `yyyy-MM-dd`) | `CalcWeeklySavingReportUsingCommand.php:21-23` |
| "Ngày tính" (`calcDate`, khi không truyền tham số) | Ngày hiện tại, format `yyyy/MM/dd` | `CalcWeeklySavingReportUsingCommand.php:58-64` |
| Batch song hành | `CalcWeeklySavingReportEffectCommand` — chạy cùng ngày, 20 phút sau (`04:50`), tính số tiền gas tiết kiệm được, ghi vào **cùng bảng `s_105`, cùng dòng** (theo `ems_sp` + ngày) | `mng-webap_cron設定_20241029.txt:73-74`, `CalcWeeklySavingReportEffectCommand.php` |

### 2.2 Câu SQL lấy dữ liệu

**SQL 1 — tổng lượng gas dùng 7 ngày trước `calcDate` (device_type = 2):**

```sql
SELECT sensor.ems_sp
     , SUM(sensor.month_target_day) AS gas_using
     , COUNT(sensor.month_target_day) AS gas_using_day
  FROM (
        SELECT month_sensor.c001 AS ems_sp
             , base_date.target_ym
             , base_date.target_day
             , CASE
                 WHEN base_date.target_day = '01' THEN month_sensor.c011
                 WHEN base_date.target_day = '02' THEN month_sensor.c012
                 ...                                              -- lặp cho 31 ngày, cột c011~c041
                 ELSE null END AS month_target_day
          FROM s_103 AS month_sensor                              -- Dữ liệu cảm biến theo tháng (đã tổng hợp sẵn)
            INNER JOIN (
                SELECT date_trunc('month', :calcDate - serial_number ngày) AS target_ym
                     , ngày trong tháng của (:calcDate - serial_number ngày) AS target_day
                  FROM generate_series(1, 7) AS serial_number       -- 7 ngày trước calcDate
            ) AS base_date
              ON base_date.target_ym = month_sensor.c004
            LEFT JOIN t_101 AS customer
              ON customer.c001 = month_sensor.c001
         WHERE customer.c052 IS NULL                                -- Hộ chưa bị xóa logic
           AND month_sensor.c002 = 2                                -- device_type = 2 (gas)
  ) AS sensor
 GROUP BY sensor.ems_sp
```
Nguồn: `CalcWeeklySavingReportUsingCommand.php:71-105` (đã rút gọn phần CASE 31 ngày để dễ đọc).

**SQL 2 — tổng lượng điện dùng 7 ngày trước `calcDate` (device_type = 5):** cấu trúc hoàn toàn giống SQL 1, chỉ khác điều kiện `month_sensor.c002 = 5` (electric). Nguồn: `CalcWeeklySavingReportUsingCommand.php:129-163`.

**SQL 3 — lấy dòng report gần nhất (tuần trước) từ `s_105`:**

```sql
SELECT weekly_energy.c001 AS ems_sp
     , weekly_energy.c011 AS last_week_gas
     , weekly_energy.c012 AS last_week_elec
     , weekly_energy.c021 AS last_week_gas_disp
     , weekly_energy.c022 AS last_week_elec_disp
  FROM s_105 AS weekly_energy
      LEFT JOIN t_101 AS customer
        ON customer.c001 = weekly_energy.c001
 WHERE customer.c052 IS NULL
   AND weekly_energy.c002 = (
           SELECT MAX(weekly_energy_sub.c002)
             FROM s_105 AS weekly_energy_sub
                 LEFT JOIN t_101 AS customer_sub
                   ON customer_sub.c001 = weekly_energy_sub.c001
            WHERE customer_sub.c052 IS NULL
              AND weekly_energy_sub.c002 < :calcDate               -- dòng gần nhất TRƯỚC ngày tính
       )
```
Nguồn: `CalcWeeklySavingReportUsingCommand.php:187-210`.

**Ý nghĩa các cột dùng trong 3 câu SQL:**

| Bảng | Cột | Ý nghĩa | Ghi chú |
|---|---|---|---|
| `t_101` | `c001` | Mã hộ（EMS-SP） | Khóa nối |
| `t_101` | `c052` | Thời điểm xóa logic | `IS NULL` = hộ còn hiệu lực |
| `s_103` | `c001` | Mã hộ | Khóa nối |
| `s_103` | `c002` | Loại thiết bị/số liệu | `2` = lượng gas dùng, `5` = lượng điện dùng |
| `s_103` | `c004` | Năm-tháng của dữ liệu | Join theo tháng chứa 7 ngày cần lấy |
| `s_103` | `c011`〜`c041` | Giá trị từng ngày trong tháng (ngày 1〜31) | Cột tương ứng ngày được chọn qua `CASE` theo `target_day` |
| `s_105` | `c001` | Mã hộ | Khóa nối |
| `s_105` | `c002` | Ngày tính (khóa chính cùng `c001`) | Dùng để tìm dòng gần nhất trước `calcDate` |
| `s_105` | `c011` / `c012` | Lượng gas / điện đã dùng tuần trước (của dòng đó) | Trở thành "tuần trước nữa" ở dòng mới |
| `s_105` | `c021` / `c022` | Lượng gas / điện đã dùng tuần trước — giá trị hiển thị (của dòng đó) | Trở thành "tuần trước nữa" (giá trị hiển thị) ở dòng mới |

### 2.3 Công thức tính (per hộ)

**① Dịch chuyển "tuần trước" → "tuần trước nữa"** (áp dụng cho mọi hộ có ở SQL 3):
```
gas_using_week_before_last          = last_week_gas       (nếu không rỗng, ngược lại null)
electric_using_week_before_last     = last_week_elec       (nếu không rỗng, ngược lại null)
gas_using_week_before_last_disp     = last_week_gas_disp   (nếu không rỗng, ngược lại null)
electric_using_week_before_last_disp= last_week_elec_disp  (nếu không rỗng, ngược lại null)
```

**② Tính "lượng gas dùng tuần trước"** (per hộ, dựa trên kết quả SQL 1):
```
① Lấy bản ghi bảng cảm biến theo giờ (ConSensorHourlyValue), device_type=2, room_id=0,
   tại khung giờ 23h của ngày liền trước calcDate (dùng để phát hiện dữ liệu bị thiếu —
   dữ liệu ở khung giữa ngày có thể đã được nội suy/lấp đầy nên không dùng để check)
② Nếu gas_using_day ≠ 7  HOẶC  bản ghi giờ ở bước ① rỗng
      → gas_using_last_week = null, gas_using_last_week_disp = null
   Ngược lại:
      gas_using_last_week = floor(gas_using × 100) / 100   nếu gas_using > 0, ngược lại null
      Nếu gas_using rỗng, hoặc < 0, hoặc > 999
          → gas_using_last_week_disp = null
      Ngược lại
          → gas_using_last_week_disp = intval(gas_using)
```

**③ Tính "lượng điện dùng tuần trước"** (per hộ, dựa trên kết quả SQL 2) — cùng công thức với ②, nhưng **không có bước check dữ liệu giờ**:
```
Nếu electric_using_day ≠ 7
      → electric_using_last_week = null, electric_using_last_week_disp = null
   Ngược lại:
      electric_using_last_week = floor(electric_using × 100) / 100   nếu electric_using > 0, ngược lại null
      Nếu electric_using rỗng, hoặc < 0, hoặc > 999
          → electric_using_last_week_disp = null
      Ngược lại
          → electric_using_last_week_disp = intval(electric_using)
```
Nguồn: `CalcWeeklySavingReportUsingCommand.php:220-313` (`execute`).

### 2.4 Ghi kết quả — bảng đích `s_105`

- Entity: `ConWeeklyEcoReport` (thư viện chung `EminelSvLib`), bảng vật lý `s_105`, khóa chính `(c001, c002)` = (mã hộ, ngày tính).
- Mỗi lần chạy: với **mỗi hộ có trong kết quả tính gas hoặc điện**, **INSERT/UPDATE (upsert) 1 dòng** với các cột: `used_last_week_gas → c011`, `used_last_week_ele → c012`, `used_week_before_last_gas → c013`, `used_week_before_last_ele → c014`, `report_used_last_week_gas → c021`, `report_used_last_week_ele → c022`, `report_used_week_before_last_gas → c023`, `report_used_week_before_last_ele → c024`; đặt cờ `GasEleCalculatedFlag (c041) = true`.
- Các cột thuộc phạm vi batch song hành `CalcWeeklySavingReportEffectCommand` (`reduced_gas_fee`, `gas_fee_reduce_code`, `report_reduced_gas_fee`, `weekly_ave_temp`, `gross_floor_space`, `gas_fee_unit`, `correcting_factor`, cờ `GasReducedFeeCalculatedFlag`) được **set giá trị null/false khi tạo entity nhưng đánh dấu `setDirty(..., false)`** trước khi save → nếu dòng đã tồn tại (do batch kia chạy trước), các cột này **không bị ghi đè** khi UPDATE.
- Toàn bộ nằm trong **1 transaction cho cả batch**: nếu ghi thất bại ở bất kỳ hộ nào → `rollback()` toàn bộ và `abort()`, không có cơ chế ghi từng phần.
- Batch này **không tự gửi thông báo, không xuất file**. Dữ liệu trong `s_105` được API `GetWeeklyEcoReportController` đọc lại để trả về ứng dụng người dùng — nằm ngoài phạm vi command này.
