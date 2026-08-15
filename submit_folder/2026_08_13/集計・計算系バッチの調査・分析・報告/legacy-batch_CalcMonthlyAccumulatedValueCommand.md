# Batch cũ — CalcMonthlyAccumulatedValueCommand（月毎積算値データ算出機能）

## Tóm tắt

`CalcMonthlyAccumulatedValueCommand` là batch chạy **1 lần/ngày** (dù tên gọi "Monthly") trong hệ thống cũ (EMINEL コンシェルジュサーバー). Mỗi lần chạy, batch cộng dồn 24 cột-giờ của **1 ngày** đã có sẵn trong `s_102` thành 1 số tổng, rồi ghi số đó vào đúng 1 cột-ngày trong dòng-tháng tương ứng của `s_103` — cho 11 loại chỉ số (gas, điện, pin lưu trữ, thao tác nhiệt độ...). Tên class ghi "Monthly/月毎" vì bảng đích `s_103` lưu 1 dòng = 1 tháng × 31 cột ngày — đó là đơn vị lưu trữ, còn đơn vị tính mỗi lần chạy là ngày.

Ngoài việc ghi ngày hiện tại, batch còn tự dò các ngày bị bỏ trống (NULL) trong `s_103` của tối đa 1 tháng trước, tính lại từ `s_102` và ghi bù. Batch chỉ đọc/ghi DB — không gọi API ngoài, không đọc/xuất CSV, không gửi mail. Riêng loại `POWER_CONSUMPTION`, trước khi tổng hợp tháng, batch gọi lại 1 hàm của batch khác (`CalcDailyEnergyConsumptionCommand`) để tái tính giờ cho 7 ngày gần nhất. Chi tiết ở Phần 2.

## Phần 1 — Tổng quát

| Mục | Nội dung |
|---|---|
| **Vai trò** | Cộng dồn 24 cột-giờ/ngày đã có trong `s_102` thành 1 tổng/ngày, ghi vào đúng 1 cột-ngày trong dòng-tháng của `s_103`, cho 11 loại chỉ số (gas tổng/gas nước nóng/gas sưởi/điện tiêu thụ/gas phát điện/mặt trời/mua điện/bán điện/pin xả/pin sạc/thao tác nhiệt độ); đồng thời dò và bù các ngày bị bỏ sót trong vòng 1 tháng gần nhất. |
| **Input** | Chỉ đọc DB, **không gọi API ngoài, không đọc CSV**: `t_101`（danh sách hộ）＋ `s_102`（tổng theo giờ, 24 cột/ngày, do các batch giờ/ngày khác ghi trước）＋ `s_103`（dòng-tháng đã có, dùng để dò cột-ngày còn NULL）. |
| **Output** | **Chỉ ghi DB** — upsert 1 cột-ngày/loại chỉ số mỗi lần chạy vào `s_103`; có thể ghi đè thêm nhiều cột-ngày (kể cả ở dòng-tháng trước) khi cơ chế tái tính kích hoạt; cập nhật cờ `c009` trên các dòng-giờ `s_102` đã dùng để tái tính. Không gửi mail, không xuất CSV. |
| **Khái quát xử lý** | 1. Đọc `--type`（bắt buộc）và `--date`（tùy chọn, mặc định = hôm qua）, validate.<br>2. Nếu `type = POWER_CONSUMPTION`: gọi hàm tái tính giờ của `CalcDailyEnergyConsumptionCommand` cho 168 giờ (7 ngày) gần nhất.<br>3. Với mỗi hộ còn hiệu lực: cộng 24 cột-giờ của "ngày tính" trong `s_102`, upsert thành 1 cột-ngày trong dòng-tháng `s_103`.<br>4. Với mỗi hộ đã có dòng-tháng hiện tại: dò ngược từng ngày (tối đa 1 tháng trước) tìm ngày gần nhất còn NULL trong `s_103`.<br>5. Tính lại tổng ngày từ `s_102` cho khoảng thiếu tìm được, ghi đè vào các cột-ngày tương ứng (có thể trải sang dòng-tháng trước), rồi đánh dấu cờ đã tổng hợp trên các dòng-giờ `s_102` liên quan. |

## Phần 2 — Chi tiết

### 2.1 Lịch chạy & tham số

| Mục | Nội dung |
|---|---|
| Lịch chạy (cron) | `20 3 * * *` — 1 lần/ngày, 3h20 sáng |
| Command thực thi | `php cake.php CalcMonthlyAccumulatedValue --type=<...> [--date=<...>]` |
| `--type` | Bắt buộc — nhiều giá trị phân tách bằng dấu phẩy, mỗi giá trị phải nằm trong `AGGREGATION_TYPE_MONTHLY` (11 giá trị, xem 2.2) |
| `--date` mặc định | Ngày hiện tại − 1 ngày |
| `--date` khi truyền tay | Format `yyyy-MM-dd` |
| Cột đích | `c%03d` = ngày + 10 → ví dụ ngày 1 → `c011`, ngày 31 → `c041` |

Docblock của command liệt kê thêm `7:灯油消費量`（灯油/dầu hỏa）như 1 giá trị `--type` hợp lệ, nhưng hằng số `7` không tồn tại trong `AGGREGATION_TYPE_MONTHLY` — nếu truyền `--type=7`, batch sẽ báo lỗi validate ở bước 1.

### 2.2 11 loại chỉ số tổng hợp tháng (`AGGREGATION_TYPE_MONTHLY`)

| `type` | Tên nghiệp vụ | Mô tả |
|---|---|---|
| `GAS_CO_TYPE_CONSUMPTION` (2) | ガス総合消費量 | Tổng lượng gas tiêu thụ của hộ (gồm sưởi + nước nóng + dùng khác) |
| `GAS_WATER_HEAT_RATE` (3) | ガス給湯消費量 | Lượng gas dùng để đun nước nóng |
| `GAS_HEAT_CONSUMPTION` (4) | ガス暖房消費量 | Lượng gas dùng để sưởi |
| `POWER_CONSUMPTION` (5) | 消費電力量 | Tổng điện năng tiêu thụ của hộ — có bước tái tính giờ riêng trước khi tổng hợp (xem 2.4) |
| `GAS_POWER` (8) | ガス発電電力量 | Điện năng phát ra từ máy phát điện chạy gas (cogeneration) |
| `SOLAR_GENERATION` (9) | 太陽光発電電力量 | Điện năng phát ra từ pin mặt trời |
| `SALE_ELECTRIC` (10) | 売電量 | Lượng điện bán ra lưới |
| `BUY_ELECTRIC` (11) | 買電量 | Lượng điện mua từ lưới |
| `BATTERY_DISCHARGE` (12) | 蓄電池(放電量) | Lượng điện xả ra từ pin lưu trữ |
| `BATTERY_CHARGE` (13) | 蓄電池(充電量) | Lượng điện sạc vào pin lưu trữ |
| `ROOM_TEMP_ADJUST_CNT` (15) | 室温設定の操作回数 | Số lần người dùng thao tác chỉnh nhiệt độ phòng |

`DETECT_CNT`（人感, 14）không nằm trong danh sách này — 人感 dừng lại ở mức ngày (`s_102`), không tổng hợp lên tháng, khớp với ghi chú ở tài liệu `legacy-batch_CalcDailyAccumulatedValueCommand.md`.

### 2.3 Lấy tổng ngày từ `s_102` & ghi cột-ngày vào `s_103`

Với mỗi `type`, hàm `getAggregateValue` chạy 1 câu SQL: nối `t_101`（lọc hộ chưa xóa logic）với `s_102`（lọc đúng `type`, `room_id = DETECT_LIVING(0)`, ngày = `--date`), cộng dồn 24 cột giờ (`c011`~`c034`, coi NULL = 0) thành 1 cột `TOTAL`, kèm 5 thuộc tính nhóm của hộ (`c012, c042, c015, c016, c024`).

`room_id` được lọc cứng bằng `DETECT_LIVING(0)` bất kể `type` — vì chỉ `DETECT_CNT` (không nằm trong danh sách tháng) mới dùng `room_id` khác 0, nên với 11 loại còn lại điều kiện này luôn đúng.

Với mỗi dòng kết quả, hàm `updateMonthlySensorInfo` tạo 1 entity `ConSensorDailyValue` mới — khóa (mã hộ, loại, room=0, ngày 1 của tháng) — set cờ `c009 = 1`（cần tổng hợp）, copy 5 thuộc tính nhóm, set cột-ngày tương ứng (`columnName` tính từ `--date`) = `TOTAL`, rồi `save()` theo khóa chính (upsert) — luôn tạo entity mới rồi lưu, không đọc dòng cũ lên sửa, cùng cách `CalcDailyAccumulatedValueCommand` ghi `s_102`.

### 2.4 Bước riêng cho `POWER_CONSUMPTION`

Trước khi tổng hợp tháng cho loại `POWER_CONSUMPTION` (5), batch khởi tạo 1 instance `CalcDailyEnergyConsumptionCommand` và gọi trực tiếp hàm `calcPowerConsumption(ngày tính 23:00, 168)` của batch đó — tái tính lại giá trị giờ (`s_102`) cho tối đa 168 giờ (7 ngày) gần nhất trước khi cộng dồn thành tổng ngày ở bước 2.3. Chi tiết công thức `calcPowerConsumption` nằm ở tài liệu riêng `legacy-batch_CalcDailyEnergyConsumption.md`.

### 2.5 Tái tính khi phát hiện ngày trước bị NULL (`recalculation`)

Sau bước 2.3, với mỗi `type`, batch chạy tiếp cơ chế tái tính:

```text
1. getRecountEmssp: lấy danh sách (hộ, type, room=0) đã có dòng-tháng
   hiện tại trong s_103, nối t_101 lọc hộ chưa xóa logic.
2. Với mỗi hộ: getRecountDateTime dò ngược từng ngày, bắt đầu từ
   (ngày tính − 2 ngày), tối đa lùi 1 tháng:
   - nếu gặp 1 ngày đã có giá trị (khác NULL) trong s_103
     → điểm bắt đầu tái tính = ngày liền sau ngày đó, dừng dò
   - nếu lùi hết 1 tháng mà không gặp ngày nào có giá trị
     → điểm bắt đầu tái tính = mốc 1 tháng trước, dừng dò
3. createUpdateData: cộng lại tổng theo ngày từ s_102, trong khoảng
   [điểm bắt đầu, ngày tính − 1 ngày].
4. updateDailySensorRecalculation: ghi từng tổng-ngày vào đúng cột-ngày
   của dòng-tháng tương ứng trong s_103 (UPDATE, không tạo dòng mới) —
   nếu khoảng tái tính vắt qua 2 tháng, tách ghi riêng cho từng dòng-tháng;
   dòng-tháng nào khác tháng hiện tại thì set thêm cờ c009 = 1 (cần tổng
   hợp lại) trên chính dòng-tháng đó.
5. updateRetroactiveFlag: cập nhật cờ c009 = 2 (đã tổng hợp) trên các
   dòng-giờ s_102 trong khoảng vừa tái tính, chỉ những dòng đang có
   c009 = 1 (đang chờ tổng hợp). Bước 4-5 nằm trong 1 transaction/hộ.
```

Không có bước nào trong cơ chế này kiểm tra giá trị tổng hợp có hợp lệ hay không (âm/dương, ngưỡng...) — chỉ kiểm tra NULL hay không.

### 2.6 Trường của `s_103` liên quan

| Trường | Ý nghĩa | Khi nào được set |
|---|---|---|
| `c001`~`c004` | Khóa chính (mã hộ, loại thiết bị, vị trí, tháng) | Mỗi lần ghi |
| `c009` | Cờ cần tổng hợp (lên năm / tái tính) | `= 1` khi ghi cột-ngày mới (2.3), hoặc khi tái tính chạm dòng-tháng khác tháng hiện tại (2.5) |
| `c111`~`c115` | 5 thuộc tính nhóm: loại nhà, công suất sưởi, diện tích sàn, số người, loại cogeneration | Copy từ danh sách hộ vào mỗi dòng |
| `c011`~`c041` | 31 cột giá trị theo ngày (01日~31日) | 1 cột/lần chạy, hoặc nhiều cột khi tái tính |

### 2.7 Hằng số nghiệp vụ liên quan

| Hằng số | Giá trị |
|---|---|
| `AGGREGATION_TYPE_MONTHLY` | `[2, 3, 4, 5, 8, 9, 10, 11, 12, 13, 15]` — tên nghiệp vụ ở 2.2 |
| `DETECT_LIVING` | `0` — room_id cố định dùng để lọc/ghi ở batch này |
| Giới hạn dò ngược khi tái tính | Tối đa 1 tháng trước `--date` |
| Giới hạn tái tính giờ riêng cho `POWER_CONSUMPTION` | 168 giờ (7 ngày) |

### 2.8 Chuỗi tổng hợp

Batch này là mắt xích thứ hai trong chuỗi "1 dòng, N cột theo đơn vị thời gian" đã nêu ở tài liệu `CalcDailyAccumulatedValueCommand`:

```
s_102  "ConSensorHourlyValues"   1 dòng/ngày   × 24 cột giờ   (do batch giờ/ngày khác ghi)
   │  CalcMonthlyAccumulatedValueCommand  (☚ batch đang phân tích — chạy 1 lần/ngày)
   ▼
s_103  "ConSensorDailyValues"    1 dòng/tháng  × 31 cột ngày  (c011~c041)
   │  batch tổng hợp năm (chạy 1 lần/tháng)
   ▼
s_104  "ConSensorMonthlyValues"  1 dòng/năm    × 12 cột tháng
```

Batch nguồn ghi `s_102` cho `GAS_POWER/SOLAR_GENERATION/SALE_ELECTRIC/BUY_ELECTRIC/BATTERY_DISCHARGE/BATTERY_CHARGE` là `CalcDailyAccumulatedValueCommand`; cho `POWER_CONSUMPTION` là `CalcDailyEnergyConsumptionCommand` (được gọi lại trực tiếp trong batch này, xem 2.4); cho `GAS_CO_TYPE_CONSUMPTION/GAS_WATER_HEAT_RATE/GAS_HEAT_CONSUMPTION/ROOM_TEMP_ADJUST_CNT` nằm ngoài phạm vi tài liệu này.

---

