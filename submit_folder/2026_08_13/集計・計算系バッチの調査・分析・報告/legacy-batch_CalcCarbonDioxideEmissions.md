# Batch cũ — CalcCarbonDioxideEmissionsCommand（CO2排出量算出）

## Tóm tắt

`CalcCarbonDioxideEmissionsCommand` là batch chạy **1 lần/tháng** trong hệ thống cũ (EMINEL コンシェルジュサーバー), tính **lượng CO2 phát ra trong 1 tháng** của từng hộ — tách riêng theo gas, theo điện, và tổng hợp — từ dữ liệu tiêu thụ gas/điện theo tháng đã có sẵn trong bảng `s_104`. Kết quả được ghi ngược lại vào chính bảng `s_104` (dùng 3 mã loại thiết bị riêng cho CO2), để 2 chỗ khác trong hệ cũ dùng tiếp: API `GetCo2ReductionReportController` (báo cáo lượng CO2 giảm được so với cùng kỳ năm trước, hiển thị trên app) và `Co2ReducedPublisher` (gửi lời khuyên tiết kiệm năng lượng định kỳ dựa trên CO2 tăng/giảm). Batch chỉ đọc/ghi DB, không gửi mail, không xuất CSV. Chi tiết ở Phần 2.

## Phần 1 — Tổng quát

| Mục | Nội dung |
|---|---|
| **Vai trò** | Từ lượng gas/điện tiêu thụ theo tháng đã có sẵn trong `s_104`, tính ra lượng CO2 phát ra trong tháng đó (gas / điện / tổng) cho từng hộ, ghi ngược lại vào `s_104`, để phục vụ báo cáo CO2 và lời khuyên tiết kiệm năng lượng trên app. |
| **Input** | Chỉ đọc DB, **không gọi API ngoài, không đọc CSV**: `t_101`（danh sách hộ）＋ `s_104`（chính nó — 3 dòng nguồn/hộ/năm: 売電-bán điện, 買電-mua điện, gas tiêu thụ, cùng ở cột-tháng đang tính; cả 3 do `CalcYearlyAccumulatedValueCommand` ghi vào — xem [2.5](#25-nguồn-gốc-dữ-liệu-trong-s_104-3-loại-dùng-làm-input)). |
| **Output** | **Chỉ ghi DB** — ghi/đè 3 dòng（gas CO2, điện CO2, tổng CO2）× 1 cột-tháng vào chính bảng `s_104`（entity `ConSensorMonthlyValue`, qua thư viện chung `EminelSvLib`）. Không gửi mail, không xuất CSV. |
| **Khái quát xử lý** | 1. Lấy tham số `--yearmonth`（mặc định = ngày 1 của tháng trước tháng hiện tại）, validate format `yyyy-MM` nếu có truyền tay.<br>2. Chạy 1 câu SQL: với mỗi hộ chưa xóa logic, lấy lượng điện mua trừ điện bán và lượng gas tiêu thụ của đúng cột-tháng đang tính (đọc từ `s_104`), nhân hệ số CO2 tương ứng; loại các hộ mới đăng ký trong đúng tháng đang tính.<br>3. Với mỗi hộ trả về: ghi 3 dòng vào `s_104`（`device_type` = tổng/gas/điện CO2), set đúng 1 cột-tháng = giá trị tính được.<br>4. Toàn bộ nằm trong 1 transaction cho cả batch — 1 hộ ghi lỗi → dừng ngay, rollback toàn bộ. |

## Phần 2 — Chi tiết

### 2.1 Lịch chạy & tham số

| Mục | Nội dung | Nguồn |
|---|---|---|
| Lịch chạy (cron) | `10 6 1 * *` — 1 lần/tháng, 6h10 sáng ngày 1 | `docs/02_詳細設計/10_バッチ処理/mng-webap_cron設定_20241029.txt:64-65` (`#19.CO2排出量算出バッチ` → `19_CalcCarbonDioxideEmissions.sh`) |
| Command thực thi | `php cake.php CalcCarbonDioxideEmissions [--yearmonth=yyyy-MM]` | `CalcCarbonDioxideEmissionsCommand.php:22,36` |
| `--yearmonth` mặc định (không truyền) | Ngày 1 của (tháng hiện tại − 1 tháng) | `CalcCarbonDioxideEmissionsCommand.php:57-60` |
| `--yearmonth` khi truyền tay | Format `yyyy-MM`（regex `/^[0-9]{4}-(0[1-9]|1[0-2])$/`); sai format → log ALERT, `commit()`（transaction rỗng）rồi `abort()` dừng batch | `CalcCarbonDioxideEmissionsCommand.php:62-70, 245-256` |
| Cột đích/nguồn trên `s_104` | `c0<số>` = tháng + 10 → tháng 1 → `c011`, tháng 12 → `c022` | `CalcCarbonDioxideEmissionsCommand.php:85, 212` |

### 2.2 Câu SQL lấy dữ liệu

```sql
WITH gas_elec_co2 AS (
    SELECT customer.c001 AS ems_sp                                       -- Mã hộ
         , customer.c012 AS build_type                                  -- Loại nhà
         , customer.c042 AS heater_power                                -- Công suất sưởi
         , customer.c015 AS floor_space                                 -- Diện tích sàn
         , customer.c016 AS family_size                                 -- Số người
         , customer.c024 AS gas_cogeneration                            -- Loại cogeneration
         , customer.c051 AS regist_date                                 -- Ngày đăng ký hộ
         , baiden.c003   AS room_id                                     -- = 0 (cố định qua điều kiện lọc)
         , baiden.c004   AS target_year                                 -- Năm tính
         , TRUNC(SUM((kaiden.<cột tháng> - baiden.<cột tháng>) * :electricCoefficient), 0) AS elec_co2
         , TRUNC(SUM(gas.<cột tháng> * :gasCoefficient), 0)             AS gas_co2
      FROM t_101 AS customer
      LEFT JOIN s_104 AS baiden                                         -- 売電(bán điện), room=0
             ON customer.c001 = baiden.c001
      LEFT JOIN s_104 AS kaiden                                         -- 買電(mua điện), room=0, đúng năm
             ON customer.c001 = kaiden.c001 AND kaiden.c002 = 11 AND kaiden.c003 = 0 AND kaiden.c004 = :year
      LEFT JOIN s_104 AS gas                                            -- Gas tiêu thụ, room=0, đúng năm
             ON customer.c001 = gas.c001 AND gas.c002 = 2 AND gas.c003 = 0 AND gas.c004 = :year
     WHERE baiden.c002 = 10 AND baiden.c003 = 0 AND baiden.c004 = :year -- Hộ phải có dòng 売電 của đúng năm
       AND customer.c052 IS NULL                                       -- Hộ chưa bị xóa logic
     GROUP BY customer.c001, customer.c012, customer.c042, customer.c015
            , customer.c016, customer.c024, baiden.c003, baiden.c004
)
SELECT co2.ems_sp, co2.build_type, co2.heater_power, co2.floor_space, co2.family_size, co2.gas_cogeneration
     , co2.room_id, co2.target_year, co2.elec_co2, co2.gas_co2, (co2.elec_co2 + co2.gas_co2) AS total_co2
  FROM gas_elec_co2 AS co2
 WHERE regist_date NOT BETWEEN :fistOfMonth AND :endOfMonth            -- Loại hộ đăng ký trong đúng tháng đang tính
```
Nguồn: `CalcCarbonDioxideEmissionsCommand.php:87-152` (cột tháng thật là `c0<tháng+10>`, viết gọn thành `<cột tháng>` ở trên — xem 2.1).

**Ý nghĩa các mã dùng để lọc/join** (theo `AGGREGATION_TYPE_YEARLY`, cùng danh sách với tài liệu `CalcYearlyAccumulatedValueCommand`):

| Bảng/alias | `c002`（loại）| `c003`（phòng）| Ý nghĩa |
|---|---|---|---|
| `baiden` | `10`（SALE_ELECTRIC）| `0` | 売電量 — lượng điện bán ra lưới trong năm; hộ phải có dòng này mới được tính |
| `kaiden` | `11`（BUY_ELECTRIC）| `0` | 買電量 — lượng điện mua từ lưới trong năm |
| `gas` | `2`（GAS_CO_TYPE_CONSUMPTION）| `0` | ガス総合消費量 — tổng lượng gas tiêu thụ trong năm |

`t_101.c051` = ngày đăng ký hộ, `t_101.c052` = ngày xóa logic (`IS NULL` = hộ còn hiệu lực).

### 2.3 Công thức tính (per hộ, theo đúng 1 cột-tháng đang xử lý)

```
elec_co2  = (điện mua tháng đó − điện bán tháng đó) × ELECTRIC_CO2_EMISSION_COEFFICIENT, cắt phần thập phân (TRUNC)
gas_co2   = (gas tiêu thụ tháng đó) × GAS_CO2_EMISSION_COEFFICIENT, cắt phần thập phân (TRUNC)
total_co2 = elec_co2 + gas_co2
```
Nguồn: `CalcCarbonDioxideEmissionsCommand.php:97-98, 135`.

**Hằng số nghiệp vụ** (`sources/conciergesv-develop/config/const.php`):

| Hằng số | Giá trị | Dòng |
|---|---|---|
| `ELECTRIC_CO2_EMISSION_COEFFICIENT` | 0.499（kg/kWh）| `const.php:649` |
| `GAS_CO2_EMISSION_COEFFICIENT` | 2.09（MJ/m3）| `const.php:651` |
| `TOTAL_CO2_EMISSIONS` | 18 — `device_type` ghi tổng CO2 | `const.php:204` |
| `GAS_CO2_EMISSIONS` | 19 — `device_type` ghi CO2 từ gas | `const.php:206` |
| `ELE_CO2_EMISSIONS` | 20 — `device_type` ghi CO2 từ điện | `const.php:208` |

### 2.4 Ghi kết quả — bảng đích `s_104` (chính bảng vừa dùng làm input)

- Entity: `ConSensorMonthlyValue` (thư viện chung `EminelSvLib`), bảng vật lý `s_104` — cùng 1 bảng đã đọc ở 2.2.
- Với **mỗi hộ** trong kết quả SQL, lặp `device_type` = 18, 19, 20 (tổng / gas / điện): tạo 1 entity mới — khóa (mã hộ, `device_type`, `room_id = 0`, `target_year`) — copy 5 thuộc tính nhóm (`c111`~`c115` = loại nhà, công suất sưởi, diện tích sàn, số người, loại cogeneration) từ hộ, set đúng cột-tháng đang tính (`c0<tháng+10>`) = giá trị CO2 tương ứng (ép kiểu string), set `c031 = thời điểm hiện tại`, rồi `save()`（upsert theo khóa chính).
- Toàn bộ nằm trong **1 transaction cho cả batch**: nếu `save()` lỗi ở bất kỳ hộ/`device_type` nào → dừng ngay, `rollback()` toàn bộ, `abort()` — không tiếp tục ghi các hộ còn lại.
- Nếu câu SQL ở 2.2 trả về 0 hộ: chỉ log info, không rollback, batch vẫn `commit()`（transaction rỗng).
- Batch này **không tự gửi thông báo, không tự tính tiếp giá trị nào khác** — dữ liệu `device_type` 18/19/20 được 2 chỗ khác trong hệ cũ đọc lại sau: API `GetCo2ReductionReportController`（so sánh với cùng kỳ năm trước）và `Co2ReducedPublisher`（phát lời khuyên tiết kiệm năng lượng định kỳ）— cả 2 nằm ngoài phạm vi command này.

### 2.5 Nguồn gốc dữ liệu trong `s_104` (3 loại dùng làm input)

3 dòng `s_104` mà batch này đọc (bán điện=10, mua điện=11, gas tổng=2) đều do **`CalcYearlyAccumulatedValueCommand`** ghi vào (batch tổng hợp năm, chạy 1 lần/tháng, cộng dồn 31 cột-ngày của `s_103` thành 1 cột-tháng của `s_104`). Trước `s_103`, mỗi loại đi qua một chuỗi batch khác nhau:

```text
Gas tổng (type 2):
  t_202 (raw ECHONET, gas meter)
     │  CalcTenMinutesEnergyCommand              (mỗi 10 phút)
     ▼
  s_101  (10 phút, type 2/3/4)
     │  CalcDailyEnergyConsumptionCommand         (mỗi giờ — "Việc 1: gasConsumptionSummary")
     ▼
  s_102  (giờ, type 2/3/4)
     │  CalcMonthlyAccumulatedValueCommand        (mỗi ngày)
     ▼
  s_103  (ngày, type 2/3/4)
     │  CalcYearlyAccumulatedValueCommand         (mỗi tháng)
     ▼
  s_104  (tháng, type 2)  ← batch CO2 đọc tại đây (alias "gas")

Bán điện (type 10) / Mua điện (type 11):
  t_202 (raw ECHONET, chiều bán — chỉ hộ có pin mặt trời)
     │  CalcDailyAccumulatedValueCommand          (mỗi giờ; ghi type 10 khi hộ có pin mặt trời)
     ▼
  CSV Xzilla IF1156, 30 phút
     │  RcvHalfHourElectricPowerCommand           (mỗi giờ; ghi type 11 luôn, ghi type 10 khi hộ KHÔNG có pin mặt trời)
     ▼
  s_102  (giờ, type 10/11)
     │  CalcMonthlyAccumulatedValueCommand        (mỗi ngày)
     ▼
  s_103  (ngày, type 10/11)
     │  CalcYearlyAccumulatedValueCommand         (mỗi tháng)
     ▼
  s_104  (tháng, type 10/11)  ← batch CO2 đọc tại đây (alias "baiden"/"kaiden")
```

Nguồn: `legacy-batch_CalcTenMinutesEnergy.md` (mục 2.1), `legacy-batch_CalcDailyEnergyConsumption.md` (mục 2.2–2.3), `legacy-batch_CalcDailyAccumulatedValueCommand.md` (mục 2.3.1), `legacy-batch_CalcMonthlyAccumulatedValueCommand.md` (mục 2.2, 2.8), `legacy-batch_CalcYearlyAccumulatedValueCommand.md` (mục 2.2–2.3, 2.7) — cùng bộ tài liệu này.
