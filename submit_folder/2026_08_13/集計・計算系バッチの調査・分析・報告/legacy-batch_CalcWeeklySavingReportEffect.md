# Batch cũ — CalcWeeklySavingReportEffectCommand（週間暖房効果算出機能）

## Tóm tắt

`CalcWeeklySavingReportEffectCommand` là batch chạy **1 lần/tuần** (Chủ Nhật) trong hệ thống cũ (EMINEL コンシェルジュサーバー), tính **ガス料金削減額（số tiền gas tiết kiệm được trong tuần nhờ hiệu ứng sưởi/eco）** cho từng hộ, dựa trên nhiệt độ phòng trung bình 7 ngày gần nhất, diện tích sàn và loại hợp đồng gas của hộ đó. Batch chỉ đọc/ghi DB (không gửi mail, không xuất file), kết quả được ghi vào bảng `s_105` — cùng bảng với batch song hành `CalcWeeklySavingReportUsingCommand` (tính lượng gas/điện đã dùng trong tuần). Chi tiết công thức, hằng số nghiệp vụ và cơ chế ghi DB trình bày ở Phần 2.

## Phần 1 — Tổng quát

| Mục | Nội dung |
|---|---|
| **Vai trò** | Từ nhiệt độ phòng trung bình 7 ngày, diện tích sàn và loại hợp đồng gas của từng hộ, tính ra **số tiền gas tiết kiệm được trong tuần** (hiệu ứng sưởi/eco) và phân loại kết quả (bình thường / dưới ngưỡng / vượt ngưỡng / không tính được). |
| **Input** | Chỉ đọc DB, **không gọi API ngoài, không đọc file CSV**: `t_101`（danh sách hộ — diện tích sàn `c015`, loại hợp đồng gas `c023`）＋ `s_103`（dữ liệu cảm biến theo tháng, đã được batch/xử lý khác tổng hợp từ trước — lấy nhiệt độ phòng trung bình và lượng gas dùng của 7 ngày trước ngày tính）. |
| **Output** | **Chỉ ghi DB** — mỗi lần chạy, với mỗi hộ đủ điều kiện, **ghi/cập nhật 1 dòng** vào `s_105`（entity `ConWeeklyEcoReport`, qua thư viện chung `EminelSvLib`）, chỉ set các cột liên quan đến "ガス料金削減額" (các cột "lượng gas/điện đã dùng" để `dirty=false` — không đụng tới, do batch song hành `CalcWeeklySavingReportUsingCommand` quản lý). Không gửi mail, không xuất CSV. |
| **Khái quát xử lý** | 1. Xác định "ngày tính" (tham số đầu vào, hoặc ngày hiện tại nếu không truyền).<br>2. Query 1 câu SQL: với mỗi hộ, tổng hợp lượng gas dùng và nhiệt độ phòng trung bình của 7 ngày trước ngày tính, kèm diện tích sàn/loại hợp đồng gas.<br>3. Với mỗi hộ: kiểm tra đủ dữ liệu (diện tích, hợp đồng gas, lượng gas dùng > ngưỡng dưới, có nhiệt độ trung bình) → nếu thiếu, kết quả rỗng (null).<br>4. Nếu đủ dữ liệu: tính số tiền gas tiết kiệm theo công thức vật lý (dùng hằng số Q value, hệ số hiệu chỉnh, đơn giá gas theo loại hợp đồng), làm tròn, rồi phân loại theo 3 ngưỡng (dưới ngưỡng / bình thường / vượt ngưỡng 1 / vượt ngưỡng 2 → không tính được).<br>5. Ghi kết quả (dù null) vào `s_105`, toàn bộ trong 1 transaction cho cả batch. |

## Phần 2 — Chi tiết

### 2.1 Lịch chạy & tham số

| Mục | Nội dung | Nguồn |
|---|---|---|
| Lịch chạy (cron) | `50 4 * * 7` — 1 lần/tuần, Chủ Nhật 04:50 | `docs/02_詳細設計/10_バッチ処理/mng-webap_cron設定_20241029.txt:73-74` (`#22.週間暖房効果算出機能` → `22_CalcWeeklySavingReportEffect.sh`) |
| Command thực thi | `php cake.php CalcWeeklySavingReportEffect [算出日]` (tham số dạng `yyyy-MM-dd`) | `CalcWeeklySavingReportEffectCommand.php:20-21` |
| "Ngày tính" (`calcDate`, khi không truyền tham số) | Ngày hiện tại, format `yyyy/MM/dd` | `CalcWeeklySavingReportEffectCommand.php:56-62` |
| Batch song hành | `CalcWeeklySavingReportUsingCommand` — chạy cùng ngày, sớm hơn 20 phút (`04:30`), tính lượng gas/điện **đã dùng** trong tuần, ghi vào **cùng bảng `s_105`, cùng dòng** (theo `ems_sp` + ngày) | `mng-webap_cron設定_20241029.txt:70-71`, `CalcWeeklySavingReportUsingCommand.php` |

### 2.2 Câu SQL lấy dữ liệu

```sql
SELECT customer_sensor.ems_sp                                        -- Mã hộ
     , customer_sensor.gas_contract                                  -- Loại hợp đồng gas
     , customer_sensor.floor_area                                    -- Diện tích sàn (mã phân loại)
     , SUM(CASE WHEN customer_sensor.device_type = 2                  -- device_type=2: lượng gas dùng
                THEN customer_sensor.month_target_day END) AS gas_using
     , ROUND(AVG(CASE WHEN customer_sensor.device_type = 6             -- device_type=6: nhiệt độ phòng
                     THEN customer_sensor.month_target_day END), 1) AS average_room_temperature
  FROM (
        SELECT customer.c001 AS ems_sp
             , month_sensor_sub.c002 AS device_type
             , customer.c023 AS gas_contract                          -- Loại hợp đồng gas
             , customer.c015 AS floor_area                            -- Diện tích sàn
             , month_sensor_sub.month_target_day                      -- Giá trị của đúng 1 ngày trong tháng (map theo CASE 1~31)
          FROM t_101 AS customer                                      -- Danh sách hộ
          LEFT JOIN (
                    SELECT month_sensor.c001, month_sensor.c002, month_sensor.c003, month_sensor.c004
                         , base_date.target_day
                         , CASE WHEN base_date.target_day = '01' THEN month_sensor.c011
                                WHEN base_date.target_day = '02' THEN month_sensor.c012
                                ...                                    -- lặp cho 31 ngày, cột c011~c041
                                ELSE null END AS month_target_day
                      FROM s_103 AS month_sensor                       -- Dữ liệu cảm biến theo tháng (đã tổng hợp sẵn)
                      INNER JOIN (
                                 SELECT date_trunc('month', :calcDate - serial_number ngày) AS target_ym
                                      , ngày trong tháng của (:calcDate - serial_number ngày) AS target_day
                                   FROM generate_series(1, 7) AS serial_number      -- 7 ngày trước calcDate
                                 ) AS base_date
                        ON base_date.target_ym = month_sensor.c004
                     WHERE (month_sensor.c002 = 6 AND month_sensor.c003 = 0)        -- nhiệt độ phòng, phòng/kênh số 0
                        OR month_sensor.c002 = 2                                   -- hoặc lượng gas dùng
           ) AS month_sensor_sub
            ON customer.c001 = month_sensor_sub.c001
         WHERE customer.c052 IS NULL                                   -- Hộ chưa bị xóa logic
    ) AS customer_sensor
 GROUP BY customer_sensor.ems_sp, customer_sensor.floor_area, customer_sensor.gas_contract
 ORDER BY customer_sensor.ems_sp
```
Nguồn: `CalcWeeklySavingReportEffectCommand.php:69-118` (đã rút gọn phần CASE 31 ngày để dễ đọc).

**Ý nghĩa các cột dùng trong câu SQL:**

| Bảng | Cột | Ý nghĩa | Ghi chú |
|---|---|---|---|
| `t_101` | `c001` | Mã hộ（EMS-SP） | Khóa nối |
| `t_101` | `c015` | Diện tích sàn (mã phân loại 1~6) | Dùng để tra bảng diện tích chuẩn |
| `t_101` | `c023` | Loại hợp đồng gas (1 hoặc 2) | Dùng để tra đơn giá gas |
| `t_101` | `c052` | Thời điểm xóa logic | `IS NULL` = hộ còn hiệu lực |
| `s_103` | `c001` | Mã hộ | Khóa nối |
| `s_103` | `c002` | Loại thiết bị/số liệu | `2` = lượng gas dùng, `6` = nhiệt độ phòng |
| `s_103` | `c003` | Kênh/phòng | Lọc `= 0` khi lấy nhiệt độ phòng |
| `s_103` | `c004` | Năm-tháng của dữ liệu | Join theo tháng chứa 7 ngày cần lấy |
| `s_103` | `c011`〜`c041` | Giá trị từng ngày trong tháng (ngày 1〜31) | Cột tương ứng ngày được chọn qua `CASE` theo `target_day` |

### 2.3 Công thức tính "ガス料金削減額" (per hộ)

```
① Kiểm tra đủ dữ liệu — nếu 1 trong các điều kiện sau đúng → gasReductionAmount = null, dừng:
   - floor_area rỗng/0
   - gas_contract rỗng/0
   - gas_using (lượng gas dùng 7 ngày) rỗng
   - gas_using ≤ WEEKLY_GAS_USAGE_BOTTOM (1.0)
   - average_room_temperature rỗng

② Tra diện tích sàn chuẩn (building_area) theo mã floor_area (1~6):
   1→70㎡, 2→80㎡, 3→100㎡, 4→120㎡, 5→140㎡, 6→151㎡
   (mã khác → building_area = null → bước ③ sẽ không tính được)

③ Tra đơn giá gas (unitCharge) theo gas_contract:
   1 (エコジョーズ) → 93.90 / 2 (マイホーム発電) → 82.35

④ Nếu (①) đủ dữ liệu VÀ building_area VÀ unitCharge đều có giá trị:
     gasReductionAmount =
         (24 − average_room_temperature) × building_area × 1.6 × 24 × 3.6 / 45
         × 7 × unitCharge / 1000 × 0.7
     → làm tròn xuống ở chữ số thập phân thứ 2 (floor × 100 / 100)
   Ngược lại → gasReductionAmount = null

⑤ Làm tròn tới hàng trăm → gasReductionAmountJudgement (dùng round(x, -2))
   Nếu gasReductionAmount rỗng → gasReductionAmountJudgement = null

⑥ Phân loại kết quả (gasReductionAmountResultCode) theo gasReductionAmountJudgement:
   - rỗng                                → 4 (không tính được)
   - < 100 (WEEKLY_GAS_FEE_LIMIT_BOTTOM)  → 2 (dưới ngưỡng)
   - ≤ 900 (WEEKLY_GAS_FEE_LIMIT_THRESHOLD) → 0 (bình thường)
   - ≤ 1900 (WEEKLY_GAS_FEE_LIMIT_TOP)    → 3 (vượt ngưỡng 1)
   - còn lại (> 1900)                     → 4 (không tính được)

⑦ Giá trị hiển thị (gasReductionAmountDisp) = gasReductionAmountJudgement
   CHỈ KHI resultCode = 0 (bình thường), còn lại → null
```
Nguồn: `CalcWeeklySavingReportEffectCommand.php:136-257` (`execute`).

**Hằng số nghiệp vụ** (`sources/conciergesv-develop/config/const.php:614-645`):

| Hằng số | Giá trị | Ý nghĩa |
|---|---|---|
| `UNIT_CHARGE_ECOJOZU` | 93.90 | Đơn giá gas — hợp đồng loại 1 (エコジョーズ) |
| `UNIT_CHARGE_MYHOME` | 82.35 | Đơn giá gas — hợp đồng loại 2 (マイホーム発電) |
| `WEEKLY_GAS_USAGE_BOTTOM` | 1.0 | Ngưỡng dưới lượng gas dùng — dưới mức này coi như không đủ dữ liệu |
| `WEEKLY_GAS_FEE_FLOOR_AREA_1`〜`_6` | 70 / 80 / 100 / 120 / 140 / 151 | Diện tích sàn chuẩn tương ứng mã 1〜6 |
| `WEEKLY_GAS_FEE_TEMPERATURE` | 24 | Nhiệt độ chuẩn (giả định không dùng EMINEL) |
| `WEEKLY_GAS_FEE_Q_VALUE` | 1.6 | Hệ số Q (đặc trưng nhiệt của nhà) |
| `WEEKLY_GAS_FEE_DAYS` | 7 | Số ngày tính trong tuần |
| `WEEKLY_GAS_FEE_COEFFICIENT` | 0.7 | Hệ số hiệu chỉnh |
| `WEEKLY_GAS_FEE_LIMIT_BOTTOM` | 100 | Ngưỡng dưới để phân loại kết quả |
| `WEEKLY_GAS_FEE_LIMIT_THRESHOLD` | 900 | Ngưỡng "bình thường" tối đa |
| `WEEKLY_GAS_FEE_LIMIT_TOP` | 1900 | Ngưỡng trên cùng — vượt mức này coi như không tính được |

### 2.4 Ghi kết quả — bảng đích `s_105`

- Entity: `ConWeeklyEcoReport` (thư viện chung `EminelSvLib`), bảng vật lý `s_105`, khóa chính `(c001, c002)` = (mã hộ, ngày tính).
- Mỗi lần chạy: với **mỗi hộ có trong kết quả query** (không cần đủ điều kiện tính toán — vẫn ghi dòng với giá trị null), **INSERT/UPDATE (upsert) 1 dòng** với các cột: `gas_reduction_amount → c016`, `gas_reduction_amount_result_code → c025`, `gas_reduction_amount_disp → c026`, `weekly_average_room_temperature → c031`, `total_floor_area → c032`, `gas_unit_price → c033`, `correction_factor → c034`; đặt cờ `GasReducedFeeCalculatedFlag (c042) = true`.
- Các cột thuộc phạm vi batch song hành `CalcWeeklySavingReportUsingCommand` (lượng gas/điện đã dùng: `c011`〜`c014`, cờ `c041`) được **set giá trị null khi tạo entity nhưng đánh dấu `setDirty(..., false)`** trước khi save → nếu dòng đã tồn tại (do batch kia chạy trước), các cột này **không bị ghi đè** khi UPDATE.
- Toàn bộ nằm trong **1 transaction cho cả batch**: nếu ghi thất bại ở bất kỳ hộ nào → `rollback()` toàn bộ và `abort()`, không có cơ chế ghi từng phần.
- Batch này **không tự gửi thông báo, không xuất file**. Dữ liệu trong `s_105` được API `GetWeeklyEcoReportController` đọc lại để trả về ứng dụng người dùng — nằm ngoài phạm vi command này.
