# Batch cũ — CalcYearlyAccumulatedValueCommand（年毎積算値データ算出機能）

## Tóm tắt

`CalcYearlyAccumulatedValueCommand` là batch chạy **1 lần/tháng** trong hệ thống cũ (EMINEL コンシェルジュサーバー). Mỗi lần chạy, batch cộng dồn 31 cột-ngày của **1 tháng** đã có sẵn trong `s_103` thành 1 số tổng, rồi ghi số đó vào đúng 1 cột-tháng trong dòng-năm tương ứng của `s_104` — cho 10 loại chỉ số (gas, điện, pin lưu trữ...). Tên class ghi "Yearly/年毎" vì bảng đích `s_104` lưu 1 dòng = 1 năm × 12 cột tháng — đó là đơn vị lưu trữ, còn đơn vị tính mỗi lần chạy là tháng.

Sau khi ghi cột-tháng, batch chạy tiếp 1 bước gọi là "tái tính" (`recalculation`) — nhưng khác với batch tháng (`CalcMonthlyAccumulatedValueCommand`), bước này **không dò ngược tìm tháng bị bỏ sót**: nó chỉ truy vấn lại đúng tháng đang xử lý, ghi đè lần thứ 2 vào đúng cột-tháng vừa ghi, rồi đánh dấu cờ "đã tổng hợp" lên đúng dòng-tháng nguồn trong `s_103`. Batch chỉ đọc/ghi DB — không gọi API ngoài, không đọc/xuất CSV, không gửi mail. Chi tiết ở Phần 2.

## Phần 1 — Tổng quát

| Mục | Nội dung |
|---|---|
| **Vai trò** | Cộng dồn 31 cột-ngày/tháng đã có trong `s_103` thành 1 tổng/tháng, ghi vào đúng 1 cột-tháng trong dòng-năm của `s_104`, cho 10 loại chỉ số (gas tổng/gas nước nóng/gas sưởi/điện tiêu thụ/gas phát điện/mặt trời/mua điện/bán điện/pin xả/pin sạc); đồng thời đánh dấu dòng-tháng nguồn trong `s_103` là đã tổng hợp lên năm. |
| **Input** | Chỉ đọc DB, **không gọi API ngoài, không đọc CSV**: `t_101`（danh sách hộ）＋ `s_103`（tổng theo ngày, 31 cột/tháng, do `CalcMonthlyAccumulatedValueCommand` ghi trước）. |
| **Output** | **Chỉ ghi DB** — upsert 1 cột-tháng/loại chỉ số vào `s_104`, ghi đè lại đúng cột đó lần thứ 2 ở bước tái tính; cập nhật cờ `c009` trên dòng-tháng nguồn trong `s_103`. Không gửi mail, không xuất CSV. |
| **Khái quát xử lý** | 1. Đọc `--type`（bắt buộc, phải nằm trong `AGGREGATION_TYPE_YEARLY` — 10 loại）và `--yearmonth`（tùy chọn, mặc định = ngày 1 tháng trước）, validate, tính cột-tháng đích.<br>2. Với mỗi `type`: cộng 31 cột-ngày (coalesce 0) của đúng dòng-tháng ứng với tháng đang tính trong `s_103`, cho mọi hộ chưa xóa logic, ra 1 tổng/hộ kèm 5 thuộc tính nhóm.<br>3. Với mỗi hộ: mở transaction, upsert 1 cột-tháng vào dòng-năm tương ứng trong `s_104`.<br>4. Nếu ghi thành công: truy vấn lại đúng dòng-tháng vừa dùng ở bước 2 (không xét tháng khác), rồi upsert lại đúng cột-tháng đó vào `s_104` lần thứ 2.<br>5. Đánh dấu cờ `c009 = 2`（đã tổng hợp）lên đúng dòng-tháng đó trong `s_103`, rồi commit; lỗi ở bất kỳ bước nào → rollback riêng cho hộ đó. |

## Phần 2 — Chi tiết

### 2.1 Lịch chạy & tham số

| Mục | Nội dung |
|---|---|
| Lịch chạy (cron) | `20 5 1 * *` — 1 lần/tháng, 5h20 sáng ngày 1 |
| Command thực thi | `php cake.php CalcYearlyAccumulatedValue --type=<...> [--yearmonth=<...>]` |
| `--type` | Bắt buộc — nhiều giá trị phân tách bằng dấu phẩy, mỗi giá trị phải nằm trong `AGGREGATION_TYPE_YEARLY` (10 giá trị, xem 2.2) |
| `--yearmonth` mặc định | Ngày 1 của tháng hiện tại − 1 tháng |
| `--yearmonth` khi truyền tay | Format `yyyy-MM` (validate bằng regex, sai format → dừng ngay) |
| Cột đích (`s_104`) | `c%03d` = tháng + 10 → ví dụ tháng 1 → `c011`, tháng 12 → `c022` |

### 2.2 Mười loại chỉ số tổng hợp năm (`AGGREGATION_TYPE_YEARLY`)

| `type` | Tên nghiệp vụ | Mô tả |
|---|---|---|
| `GAS_CO_TYPE_CONSUMPTION` (2) | ガス総合消費量 | Tổng lượng gas tiêu thụ của hộ (gồm sưởi + nước nóng + dùng khác) |
| `GAS_WATER_HEAT_RATE` (3) | ガス給湯消費量 | Lượng gas dùng để đun nước nóng |
| `GAS_HEAT_CONSUMPTION` (4) | ガス暖房消費量 | Lượng gas dùng để sưởi |
| `POWER_CONSUMPTION` (5) | 消費電力量 | Tổng điện năng tiêu thụ của hộ |
| `GAS_POWER` (8) | ガス発電電力量 | Điện năng phát ra từ máy phát điện chạy gas (cogeneration) |
| `SOLAR_GENERATION` (9) | 太陽光発電電力量 | Điện năng phát ra từ pin mặt trời |
| `SALE_ELECTRIC` (10) | 売電量 | Lượng điện bán ra lưới |
| `BUY_ELECTRIC` (11) | 買電量 | Lượng điện mua từ lưới |
| `BATTERY_DISCHARGE` (12) | 蓄電池(放電量) | Lượng điện xả ra từ pin lưu trữ |
| `BATTERY_CHARGE` (13) | 蓄電池(充電量) | Lượng điện sạc vào pin lưu trữ |

So với `AGGREGATION_TYPE_MONTHLY` (11 loại, xem tài liệu `CalcMonthlyAccumulatedValueCommand`), danh sách năm thiếu duy nhất `ROOM_TEMP_ADJUST_CNT` (15, số lần thao tác chỉnh nhiệt độ) — chỉ số này dừng lại ở mức tháng, không tổng hợp lên năm.

### 2.3 Lấy tổng tháng từ `s_103` & ghi cột-tháng vào `s_104`

Với mỗi `type`, hàm `getAggregateValue` chạy 1 câu SQL: nối `t_101`（lọc hộ chưa xóa logic, `c052 IS NULL`）với `s_103`（lọc đúng `type`, `room_id = DETECT_LIVING(0)`, dòng-tháng = tháng đang tính), cộng dồn 31 cột ngày (`c011`~`c041`, coi NULL = 0) thành 1 cột `TOTAL`, kèm 5 thuộc tính nhóm của hộ (`c012, c042, c015, c016, c024` — loại nhà, công suất sưởi, diện tích sàn, số người, loại cogeneration).

`room_id` được lọc cứng bằng `DETECT_LIVING(0)` — cả 10 loại trong danh sách năm đều dùng `room_id = 0`, không có loại nào tách phòng ở mức này.

Với mỗi hộ trả về, hàm `updateYearlySensorInfo` tạo 1 entity `ConSensorMonthlyValue` mới — khóa (mã hộ, loại, room=0, năm) — copy 5 thuộc tính nhóm, set cột-tháng tương ứng (`columnName` tính từ `--yearmonth`) = `TOTAL`, rồi `save()` theo khóa chính (upsert) — luôn tạo entity mới rồi lưu, không đọc dòng cũ lên sửa, cùng cách các batch cùng họ (giờ/ngày/tháng) ghi dữ liệu của chúng. Bước này **không set cờ `c009`** trên `s_104`.

### 2.4 Bước "tái tính" (`recalculation`) — chỉ chạm đúng 1 tháng đang xử lý

Sau khi ghi cột-tháng ở 2.3, batch gọi tiếp `recalculation`, gồm 3 bước:

```text
1. createUpdateData: query lại s_103, lọc CHÍNH XÁC
   (mã hộ, type, room=0, ngày = tháng đang tính) — cùng điều kiện
   tháng như bước 2.3, không mở rộng sang tháng trước/sau.
   → trả về đúng 1 dòng: (c004 = ngày-1 của tháng đang tính, TOTAL = tổng 31 cột-ngày)
2. updateMonthlySensorRecalculation: dùng lại TOTAL vừa lấy, tạo 1 entity
   ConSensorMonthlyValue mới, set cờ c009 = 1, set ĐÚNG cột-tháng đang tính
   (tính lại từ c004 ở bước 1 — trùng với cột đã ghi ở bước 2.3) = TOTAL,
   rồi save() (upsert) — ghi đè lần thứ 2 vào cùng 1 cột-tháng của s_104.
3. updateRetroactiveFlag: UPDATE s_103, set c009 = 2 (đã tổng hợp),
   lọc theo (mã hộ, type, room, ngày = đúng dòng-tháng đã dùng ở bước 1).
```

Khác với cơ chế cùng tên ở `CalcMonthlyAccumulatedValueCommand` (dò ngược tối đa 1 tháng trước để bù các ngày `NULL`), bước "tái tính" của batch năm **không dò ngược tháng nào khác** — toàn bộ 3 bước trên chỉ đọc/ghi lại đúng tháng vừa xử lý ở bước 2.3. Hiệu ứng thực tế là: ghi trùng giá trị vào đúng 1 cột-tháng thêm 1 lần, và đánh dấu dòng-tháng nguồn trong `s_103` đã được tổng hợp lên năm.

Bước 2.3 (`updateYearlySensorInfo`) và bước 2 ở trên (`updateMonthlySensorRecalculation`) nằm trong cùng 1 transaction/hộ — nếu bất kỳ bước nào lỗi, `rollback()` toàn bộ cho hộ đó.

### 2.5 Trường của `s_104` liên quan

| Trường | Ý nghĩa | Khi nào được set |
|---|---|---|
| `c001`~`c004` | Khóa chính (mã hộ, loại thiết bị, vị trí, năm) | Mỗi lần ghi |
| `c009` | Cờ cần tổng hợp | Chỉ được set (`= 1`) ở bước tái tính (2.4); bước ghi chính (2.3) không set cờ này |
| `c111`~`c115` | 5 thuộc tính nhóm: loại nhà, công suất sưởi, diện tích sàn, số người, loại cogeneration | Copy từ danh sách hộ vào mỗi dòng |
| `c011`~`c022` | 12 cột giá trị theo tháng (01月~12月) | 1 cột/lần chạy — ghi 2 lần (bước chính 2.3 + bước tái tính 2.4) vào cùng 1 cột |

### 2.6 Hằng số nghiệp vụ liên quan

| Hằng số | Giá trị |
|---|---|
| `AGGREGATION_TYPE_YEARLY` | `[2, 3, 4, 5, 8, 9, 11, 10, 12, 13]` — tên nghiệp vụ ở 2.2 |
| `DETECT_LIVING` | `0` — room_id cố định dùng để lọc/ghi ở batch này |
| Phạm vi tái tính | Chỉ đúng 1 tháng đang xử lý — không có hằng số giới hạn dò ngược (vì không dò ngược) |

### 2.7 Chuỗi tổng hợp

Batch này là mắt xích thứ ba (cuối) trong chuỗi "1 dòng, N cột theo đơn vị thời gian" đã nêu ở tài liệu `CalcDailyAccumulatedValueCommand`/`CalcMonthlyAccumulatedValueCommand`:

```
s_102  "ConSensorHourlyValues"   1 dòng/ngày   × 24 cột giờ   (CalcDailyAccumulatedValueCommand ghi)
   │  CalcMonthlyAccumulatedValueCommand  (chạy 1 lần/ngày)
   ▼
s_103  "ConSensorDailyValues"    1 dòng/tháng  × 31 cột ngày  (c011~c041)
   │  CalcYearlyAccumulatedValueCommand  (☚ batch đang phân tích — chạy 1 lần/tháng)
   ▼
s_104  "ConSensorMonthlyValues"  1 dòng/năm    × 12 cột tháng (c011~c022)
```

Danh sách 10 loại chỉ số ở batch này là tập con của 11 loại mà `CalcMonthlyAccumulatedValueCommand` ghi vào `s_103` (thiếu `ROOM_TEMP_ADJUST_CNT`, xem 2.2). Batch năm không có bước nào tổng hợp tiếp lên đơn vị thời gian lớn hơn — `s_104` là điểm cuối của chuỗi.

---

## Nguồn tham khảo

| Nội dung | Căn cứ |
|---|---|
| Toàn bộ logic (mục 2.1–2.7) | `sources/conciergesv-develop/src/Command/CalcYearlyAccumulatedValueCommand.php` (đọc toàn văn) |
| Hằng số nghiệp vụ | `sources/conciergesv-develop/config/const.php:687-690` |
| Lịch chạy cron | `docs/02_詳細設計/10_バッチ処理/mng-webap_cron設定_20241029.txt:54-55` |
| Entity đích `s_104` | `sources/eminel_sv_lib-develop/src/Model/Entity/ConSensorMonthlyValue.php` |
| Table đích `s_104` (khóa chính) | `sources/eminel_sv_lib-develop/src/Model/Table/ConSensorMonthlyValuesTable.php:41-43` |
| Batch nguồn dữ liệu (`s_103`) | Xem tài liệu riêng `CalcMonthlyAccumulatedValueCommand/legacy-batch_CalcMonthlyAccumulatedValueCommand.md` |
