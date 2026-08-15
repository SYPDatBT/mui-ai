# Batch cũ — CalcDailyEnergyConsumptionCommand（日毎エネルギー使用量算出）

## Tóm tắt

`CalcDailyEnergyConsumptionCommand` là batch chạy **1 lần/giờ** trong hệ thống cũ (EMINEL コンシェルジュサーバー), thực hiện 2 việc: (1) gộp giá trị gas 10 phút (đã có sẵn ở `s_101`) thành giá trị giờ, và (2) **tính giá trị tổng tiêu thụ điện của hộ** (`消費電力量`) cho từng giờ. Hộ không có đồng hồ đo trực tiếp "tổng tiêu thụ điện" — điện dùng trong nhà đến từ điện mua lưới + điện tự phát (mặt trời, gas phát điện) + điện xả từ pin, trừ đi phần bán ngược lưới và phần sạc vào pin — nên giá trị này phải được **suy ra bằng công thức cộng/trừ 6 luồng điện đã đo riêng lẻ**, không đọc thẳng từ 1 cảm biến. 6 luồng đó do **hai batch khác** (`CalcDailyAccumulatedValueCommand`, `RcvHalfHourElectricPowerCommand`) ghi vào `s_102` trước khi batch này chạy. Batch chỉ đọc/ghi DB (không gửi mail, không xuất file), kết quả ghi vào `s_102`. Chi tiết lịch chạy, SQL, công thức và hằng số nghiệp vụ trình bày ở Phần 2.

## Phần 1 — Tổng quát

| Mục | Nội dung |
|---|---|
| **Vai trò** | (1) Gộp giá trị **gas 10 phút → giờ** (tổng/nước nóng/sưởi). (2) **Tính giá trị tổng tiêu thụ điện** (`消費電力量`) của hộ theo từng giờ — vì hộ không có đồng hồ đo trực tiếp đại lượng này, giá trị phải suy ra bằng công thức cộng/trừ 6 luồng điện đã đo riêng lẻ (mua điện, bán điện, mặt trời, gas phát điện, pin xả, pin sạc): `tổng tiêu thụ = mặt trời + gas phát điện + pin xả − pin sạc + mua điện − bán điện`. Hai việc độc lập về mặt dữ liệu, gộp chung trong 1 class. |
| **Input** | Chỉ đọc DB, **không gọi API ngoài, không đọc file CSV**: `t_101`（danh sách khách hàng + 5 thuộc tính nhóm）＋ `s_101`（gas 10 phút, do `CalcTenMinutesEnergyCommand` ghi）＋ `s_102`（giá trị giờ điện, do `CalcDailyAccumulatedValueCommand` và `RcvHalfHourElectricPowerCommand` ghi）. |
| **Output** | **Chỉ ghi DB** — `s_102`（entity `ConSensorHourlyValue`, qua thư viện chung `EminelSvLib`）: giờ gas (`c002 IN (2,3,4)`) và giờ tổng tiêu thụ điện (`c002 = 5`). Không gửi mail, không xuất CSV. |
| **Khái quát xử lý** | 1. Xác định `calculationTime` (mặc định `hiện tại − 1 giờ`, hoặc tham số `--datetime`).<br>2. `gasConsumptionSummary()`: quét lùi **193 giờ** (~8 ngày), mỗi khi đổi ngày chạy 1 câu SQL PIVOT gộp gas 10 phút → giờ bằng `sum()`, ghi đè `s_102`.<br>3. Nếu (2) thành công, `calcPowerConsumption()`: với từng khách hàng, quét lùi **24 giờ**, bỏ qua giờ đã có sẵn giá trị tổng tiêu thụ điện.<br>4. Với mỗi giờ chưa có, gom 6 thành phần hiện có trong `s_102` (mặt trời/gas phát điện/xả pin/sạc pin/mua điện/bán điện), tính công thức nếu đủ cả 6, ghi `null` nếu còn thiếu.<br>5. Ghi kết quả vào `s_102`, mỗi khách hàng nằm trong 1 transaction riêng (lỗi ở khách hàng nào chỉ rollback khách hàng đó). |

## Phần 2 — Chi tiết

### 2.1 Lịch chạy & tham số

| Mục | Nội dung | Nguồn |
|---|---|---|
| Lịch chạy (cron) | `45 * * * *` — 1 lần/giờ, phút 45 | `docs/02_詳細設計/10_バッチ処理/mng-webap_cron設定_20241029.txt:19` (`6_CalcDailyEnergyConsumption.sh`) |
| Command thực thi | `php cake.php CalcDailyEnergyConsumption [--datetime]` | `CalcDailyEnergyConsumptionCommand.php:43-48` |
| Mốc `calculationTime` mặc định | `hiện tại − 1 giờ` | `CalcDailyEnergyConsumptionCommand.php:64-66` |
| Tham số chạy lại | `--datetime` (`yyyy-MM-ddTHH:mm:ss+09:00`), validate bằng regex, sai định dạng → `io->abort()` | `CalcDailyEnergyConsumptionCommand.php:67-74, 704-715` |
| Thứ tự chạy trong 1 lần | `gasConsumptionSummary()` → nếu `true` mới chạy `calcPowerConsumption($calculationTime, 24)` | `CalcDailyEnergyConsumptionCommand.php:81-86` |

### 2.2 Việc 1 — Gộp gas 10 phút → giờ (`gasConsumptionSummary`)

| Mục | Nội dung |
|---|---|
| Nguồn | `s_101`（`ConSensorMemoryValue`, giá trị 10 phút — gas tổng/nước nóng/sưởi, `c002 IN (2,3,4)`, `c003 = 0`） |
| Đích | `s_102`（`ConSensorHourlyValues`）, ghi đè theo cột giờ `c000`~`c023` (`measurement00`~`measurement23`) |
| Phạm vi quét lại | **193 giờ** (~8 ngày) lùi về trước mỗi lần chạy, chỉ gọi lại SQL khi **ngày** thay đổi (~8 lần/lần chạy) | `CalcDailyEnergyConsumptionCommand.php:452-480` |
| Transaction | Toàn bộ Việc 1 nằm trong **1 transaction duy nhất** — lỗi ở bất kỳ ngày nào → rollback toàn bộ `gasConsumptionSummary()` | `CalcDailyEnergyConsumptionCommand.php:448-486` |

**SQL gộp (`dailyDateAggregate`)** — về bản chất là **PIVOT theo giờ bằng `CASE WHEN`**, chạy cho toàn bộ khách hàng trong một ngày:

```sql
SELECT S.c001, S.c002, S.c003, S.c012, S.c042, S.c015, S.c016, S.c024,
       sum(S.c006_00) AS measurement00,   -- giờ 00
       sum(S.c006_01) AS measurement01,   -- giờ 01
       ...
       sum(S.c006_23) AS measurement23    -- giờ 23
  FROM (
        SELECT ConCustomers.c001, ConSensorMemoryValue.c002, ConSensorMemoryValue.c003,
               ConCustomers.c012, ConCustomers.c042, ConCustomers.c015,
               ConCustomers.c016, ConCustomers.c024,
               CASE WHEN date_part('hour', ConSensorMemoryValue.c004) = 0
                    THEN ConSensorMemoryValue.c006 ELSE null END AS c006_00,
               ... (lặp lại cho giờ 1 → 23) ...
          FROM t_101 ConCustomers
          JOIN s_101 ConSensorMemoryValue
            ON ConSensorMemoryValue.c002 IN (2, 3, 4)
           AND ConSensorMemoryValue.c003 = 0
           AND ConSensorMemoryValue.c004 >= :fromDate
           AND ConSensorMemoryValue.c004 <  :toDate
         WHERE ConCustomers.c001 = ConSensorMemoryValue.c001
           AND ConCustomers.c052 IS NULL
       ) AS S
 GROUP BY (S.c001, S.c002, S.c003, S.c012, S.c042, S.c015, S.c016, S.c024)
```
Nguồn: `CalcDailyEnergyConsumptionCommand.php:574-696`.

Vì mỗi giờ có tối đa 6 bản ghi 10 phút (`:00,:10,:20,:30,:40,:50`), `sum(c006_XX)` chính là **tổng 6 giá trị 10 phút trong giờ đó** — không phải trung bình, không phải giá trị cuối kỳ.

**Cờ hồi tố (`aggCompleteFlag`)** — `CalcDailyEnergyConsumptionCommand.php:499-508`:

```
nếu calculationTime và targetDate KHÁC ngày  → flag = 1  (có hồi tố — đang bù ngày cũ)
nếu calculationTime và targetDate CÙNG ngày  → flag = 2  (không hồi tố — hôm nay)
```

Vòng lặp `for ($subHour = 0; $subHour < 193; $subHour++)` (`CalcDailyEnergyConsumptionCommand.php:452`) gọi lại `dailyDateAggregate()` mỗi khi ngày thay đổi. Mỗi lần gọi là một scan `t_101 JOIN s_101` cho toàn bộ khách hàng trong cả ngày đó, không lọc theo khách hàng có dữ liệu mới hay không — nên mỗi lần chạy (mỗi giờ), batch tính lại và ghi đè giá trị gas của 8 ngày gần nhất cho toàn bộ khách hàng. `s_101` có thể nhận dữ liệu trễ, nên việc gộp lại 8 ngày mỗi lần chạy giúp giá trị giờ luôn khớp với dữ liệu 10 phút mới nhất.

### 2.3 Việc 2 — Tính tổng tiêu thụ điện (`calcPowerConsumption`)

Hộ gia đình không có 1 đồng hồ đo trực tiếp "tổng tiêu thụ điện" — mỗi luồng điện (mua từ lưới, bán ngược lưới, tự phát từ mặt trời/gas cogeneration, xả/sạc pin) có đồng hồ/cảm biến riêng và được các batch khác đo, tính hiệu, ghi vào `s_102` theo giờ. `calcPowerConsumption` đọc 6 giá trị giờ đó cho từng khách hàng và cộng/trừ theo công thức cân bằng năng lượng để ra giá trị tổng tiêu thụ điện của giờ đó.

**Công thức** (`calcConsumptionPower`, `CalcDailyEnergyConsumptionCommand.php:323-341`):

```php
powerConsumption = device09        // 太陽光発電電力量 — mặt trời
                  + device08       // ガス発電電力量 — gas phát điện (Collemo/Enefarm)
                  + device12       // 蓄電池(放電量) — pin XẢ
                  - device13       // 蓄電池(充電量) — pin SẠC
                  + device11       // 買電量 — mua điện
                  - device10;      // 売電量 — bán điện
```

Nếu **bất kỳ thành phần nào trong 6 thành phần** là `null` → `powerConsumption = null` (không đoán, không ép `0`) — `CalcDailyEnergyConsumptionCommand.php:326-329`.

**6 thành phần đến từ đâu** (`setRecalculationData`, `CalcDailyEnergyConsumptionCommand.php:351-405`):

| # | Thành phần | `device_type` | Batch ghi vào `s_102` | Điều kiện tính (theo khách hàng) |
|---|---|---|---|---|
| 1 | 太陽光発電 (mặt trời) | 9 | `CalcDailyAccumulatedValueCommand` | Chỉ nếu `c034`(có pin mặt trời) `= 1`, ngược lại giữ mặc định `0` |
| 2 | ガス発電 (gas phát điện) | 8 | `CalcDailyAccumulatedValueCommand` | Chỉ nếu `c024`(gas cogeneration) `∈ {1,2}`, ngược lại giữ mặc định `0` |
| 3 | 蓄電池放電 (xả pin) | 12 | `CalcDailyAccumulatedValueCommand` | Chỉ nếu `c035`(có pin lưu trữ) `= 1`, ngược lại giữ mặc định `0` |
| 4 | 蓄電池充電 (sạc pin) | 13 | `CalcDailyAccumulatedValueCommand` | Chỉ nếu có pin lưu trữ, ngược lại giữ mặc định `0` |
| 5 | 買電 (mua điện) | 11 | `RcvHalfHourElectricPowerCommand` (Xzilla) | **Bắt buộc, luôn từ Xzilla** — không có nhánh ECHONET nào ghi type 11 trong `AGGREGATION_TYPE` |
| 6 | 売電 (bán điện) | 10 | `CalcDailyAccumulatedValueCommand` **hoặc** `RcvHalfHourElectricPowerCommand` | Tùy `c034`(pin mặt trời) — có pin mặt trời thì lấy từ ECHONET (đo chiều ngược), không có thì lấy từ Xzilla |

Thành phần 1–4 mặc định `0` nếu điều kiện không thỏa (`CalcDailyEnergyConsumptionCommand.php:358-363`). Thành phần 5–6 mặc định `null`.

**Vòng quét lại: 24 giờ, "chờ đến khi đủ input"** — `calcPowerConsumption($calculationTime, 24)` quét lùi tối đa 24 giờ (`CalcDailyEnergyConsumptionCommand.php:98, 124-178`). Với mỗi giờ:

1. Nếu `device_type = 5` (tổng tiêu thụ) của giờ đó **đã có giá trị** → bỏ qua, không tính lại (`setRecalculationData` trả `false` ngay — `CalcDailyEnergyConsumptionCommand.php:367-371`).
2. Nếu chưa có → gom 6 thành phần hiện có trong `s_102` cho giờ đó, tính công thức nếu đủ, ghi `null` nếu còn thiếu.

Nếu một thành phần không bao giờ tới (ví dụ Xzilla không gửi CSV), `device_type = 5` của giờ đó giữ `null` — không có cơ chế nào tự chuyển trạng thái sau một khoảng thời gian chờ.

**`roomId` ghi giá trị `DETECT_LIVING`** — khi ghi bản ghi tổng tiêu thụ điện, code gọi `setRoomId(DETECT_LIVING)` (`CalcDailyEnergyConsumptionCommand.php:218`). `DETECT_LIVING` là hằng số phòng khách dùng cho cảm biến người (giá trị `0`); ở bản ghi điện, giá trị này không đại diện phòng khách — bản ghi giờ điện không có khái niệm phòng.

**Group attributes (`c111`~`c115`)** — mọi bản ghi giờ đều được đính kèm 5 thuộc tính nhóm của khách hàng tại **thời điểm ghi**: loại nhà (`c012`→`c111`), công suất sưởi (`c042`→`c112`), diện tích sàn (`c015`→`c113`), số người trong hộ (`c016`→`c114`), loại cogeneration (`c024`→`c115`) — `CalcDailyEnergyConsumptionCommand.php:220-224, 518-522`; mapping cột xác nhận tại `eminel_sv_lib-develop/src/Model/Entity/ConSensorHourlyValue.php:59-63`. Đây là dữ liệu **denormalize** — copy master data vào từng fact row — để báo cáo xếp hạng/so sánh nhóm không cần JOIN ngược lại `t_101` mỗi lần đọc.

### 2.4 Hai batch phụ thuộc (chỉ nêu tóm tắt — không thuộc phạm vi batch này)

`CalcDailyEnergyConsumptionCommand` là **điểm cuối lắp ráp**, không phải nơi phát sinh dữ liệu điện. Nó chỉ đọc 6 cột đã có sẵn ở `s_102` và cộng/trừ theo công thức, miễn là cả 6 đều đã được 2 batch sau điền:

| Batch | Vai trò | Cách tính hiệu |
|---|---|---|
| `CalcDailyAccumulatedValueCommand` | Ghi giờ cho: gas phát điện, mặt trời, xả/sạc pin, (một phần) bán điện — đọc `t_202` (ECHONET thô) | Hiệu giữa **2 điểm chụp** (đầu giờ, cuối giờ), không qua `s_101` |
| `RcvHalfHourElectricPowerCommand` | Ghi giờ cho: mua điện, (một phần) bán điện — nhập CSV Xzilla 30 phút (`IF1156`) | Gộp 2 khung 30 phút thành 1 giờ bằng **cộng trực tiếp**, không qua ECHONET |

### 2.5 Hằng số nghiệp vụ liên quan

| Hằng số | Giá trị | Nguồn |
|---|---|---|
| `device_type` (機器種別) | `5`=消費電力量, `8`=ガス発電, `9`=太陽光発電, `10`=売電, `11`=買電, `12`=蓄電池放電, `13`=蓄電池充電 | `const.php:182,186,188,190,192,194,196` |
| `AGGREGATION_TYPE` | `[GAS_POWER, SOLAR_GENERATION, SALE_ELECTRIC, BATTERY_DISCHARGE, DETECT_CNT]` — không có `BUY_ELECTRIC` | `const.php:655` |
| CO2 điện | `0.499 kg/kWh` (`ELECTRIC_CO2_EMISSION_COEFFICIENT`) | `const.php:649` |
| CO2 gas | `2.09` (`GAS_CO2_EMISSION_COEFFICIENT`, đơn vị nguyên văn const, cần xác nhận khi dùng) | `const.php:651` |
| Vòng quét lại gas | 193 giờ (~8 ngày) | `CalcDailyEnergyConsumptionCommand.php:452` |
| Vòng quét lại điện | 24 giờ | `CalcDailyEnergyConsumptionCommand.php:85` |

---

## Căn cứ của tài liệu

| Nội dung | Căn cứ |
|---|---|
| Logic Việc 1 (gas giờ) | `sources/conciergesv-develop/src/Command/CalcDailyEnergyConsumptionCommand.php::gasConsumptionSummary` (dòng 443-489, 574-696) |
| Logic Việc 2 (ráp điện) | `sources/conciergesv-develop/src/Command/CalcDailyEnergyConsumptionCommand.php::calcPowerConsumption` (dòng 98-341, 351-405) |
| Lịch chạy cron | `docs/02_詳細設計/10_バッチ処理/mng-webap_cron設定_20241029.txt:19` |
| Hằng số nghiệp vụ | `sources/conciergesv-develop/config/const.php` |
| Entity đích | `sources/eminel_sv_lib-develop/src/Model/Entity/ConSensorHourlyValue.php` |
