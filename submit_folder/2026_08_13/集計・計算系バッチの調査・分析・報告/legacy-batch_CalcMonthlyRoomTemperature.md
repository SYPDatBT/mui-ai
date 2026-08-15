# Batch cũ — CalcMonthlyRoomTemperatureCommand（月毎室温データ算出）

## Tóm tắt

`CalcMonthlyRoomTemperatureCommand` là batch chạy 1 lần/ngày trong hệ thống cũ (EMINEL コンシェルジュサーバー), gộp **24 giá trị nhiệt độ trung bình theo giờ** (đã có sẵn trong bảng `s_102`, do batch khác tính) của 1 ngày thành **1 giá trị trung bình ngày duy nhất**, cho từng hộ × từng vị trí cảm biến (E0/E1), rồi ghi vào bảng theo tháng `s_103` (mỗi dòng gồm 31 cột — 1 cột/ngày trong tháng). Ngoài ngày đang tính, batch còn quét lại toàn bộ dữ liệu giờ của tháng này và tháng trước để **tái tính** các ngày mà dữ liệu nguồn đã thay đổi/bổ sung sau khi tính lần trước, rồi đánh dấu lại nguồn `s_102` là "đã tổng hợp". Batch chỉ đọc/ghi DB (không gửi mail, không xuất file). Chi tiết lịch chạy, câu SQL, công thức tính và hằng số nghiệp vụ trình bày ở Phần 2.

## Phần 1 — Tổng quát

| Mục | Nội dung |
|---|---|
| **Vai trò** | Dữ liệu nhiệt độ chỉ có sẵn theo **giờ** (24 giá trị/ngày, ở `s_102`); để có lịch sử nhiệt độ theo **tháng** (phục vụ tra cứu/hiển thị theo ngày trong tháng), cần gộp 24 giá trị giờ của 1 ngày thành **1 số trung bình ngày duy nhất** và lưu vào 1 dòng dạng tháng (31 cột ngày), cho mỗi hộ × mỗi vị trí cảm biến. Vì dữ liệu giờ nguồn có thể đến muộn hoặc được sửa lại sau khi ngày đó đã được tính, batch còn phải **tái tính** các ngày cũ (trong phạm vi tháng này + tháng trước) để bảng tháng luôn khớp với dữ liệu giờ mới nhất. |
| **Input** | Chỉ đọc DB, **không gọi API ngoài, không đọc file CSV**: `t_101`（danh sách hộ）＋ `s_102`（bảng kết quả giờ, entity `ConSensorHourlyValue` — mỗi dòng là 1 hộ × 1 vị trí cảm biến × 1 ngày, 24 cột giờ `c011`〜`c034`, do batch tính giờ ghi sẵn). |
| **Output** | **Chỉ ghi DB** — ghi/ghi đè vào `s_103`（entity `ConSensorDailyValue`, qua thư viện chung `EminelSvLib`）— mỗi dòng là 1 hộ × 1 vị trí cảm biến × 1 tháng, 31 cột ngày (`c011`〜`c041`); đồng thời cập nhật cờ `need_agg_complete_flag` trên `s_102` để đánh dấu các ngày đã tổng hợp. Không gửi mail, không xuất CSV. |
| **Khái quát xử lý** | 1. Xác định ngày tính (tham số `--date` hoặc hôm qua), validate format nếu có tham số, sai format thì abort.<br>2. Lấy tổng nhiệt độ 24 giờ + số giờ có dữ liệu trong ngày đó từ `s_102`, theo từng hộ × từng vị trí cảm biến.<br>3. Tính trung bình ngày = tổng ÷ số giờ hợp lệ; ghi vào cột ngày tương ứng của dòng tháng trong `s_103`.<br>4. Lấy lại dữ liệu giờ của tháng trước + tháng này (trừ đúng ngày đang tính) để tái tính các ngày cũ.<br>5. Ghi đè giá trị trung bình tái tính vào `s_103`, đánh dấu nguồn `s_102` là đã tổng hợp; toàn bộ nằm trong 1 transaction. |

## Phần 2 — Chi tiết

### 2.1 Lịch chạy & mốc thời gian tính

| Mục | Nội dung | Nguồn |
|---|---|---|
| Lịch chạy (cron) | `10 3 * * *` — 1 lần/ngày, 3:10 sáng | `docs/02_詳細設計/10_バッチ処理/mng-webap_cron設定_20241029.txt:24-25` (`#8.月毎室温データ算出` → `8_CalcMonthlyRoomTemperature.sh`) |
| Command thực thi | `php cake.php CalcMonthlyRoomTemperature [--date="算出日"]` | `CalcMonthlyRoomTemperatureCommand.php:45` |
| Mốc **calculationDate** (khi không truyền tham số) | `hôm nay − 1 ngày` | `CalcMonthlyRoomTemperatureCommand.php:64-66` |
| Khi có truyền tham số `--date` | Validate format `yyyy-MM-dd` bằng regex `^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])$`; sai format → log ALERT rồi `abort()` | `CalcMonthlyRoomTemperatureCommand.php:68-76,438-449` |
| Ngày tính chính | `calculationDate` (đúng 1 ngày, không phải khung giờ) | `CalcMonthlyRoomTemperatureCommand.php:376` |

### 2.2 Lấy dữ liệu giờ của ngày đang tính (`getSensorHourlyValue`)

```sql
SELECT ConSensorHourlyValues.c001, ConSensorHourlyValues.c002, ConSensorHourlyValues.c003
     , ConCustomers.c012 AS c111, ConCustomers.c042 AS c112
     , ConCustomers.c015 AS c113, ConCustomers.c016 AS c114, ConCustomers.c024 AS c115
     , COALESCE(c011,0)+COALESCE(c012,0)+ ... +COALESCE(c034,0) AS total        -- tổng 24 giờ, NULL tính là 0
     , (CASE WHEN c011 IS NULL THEN 0 ELSE 1 END)+ ... +(CASE WHEN c034 IS NULL THEN 0 ELSE 1 END) AS totalNumber  -- số giờ có dữ liệu
  FROM t_101 ConCustomers, s_102 ConSensorHourlyValues
 WHERE ConCustomers.c001 = ConSensorHourlyValues.c001
   AND ConSensorHourlyValues.c002 = 6                    -- device_type = ROOM_TEMPERATURE
   AND ConSensorHourlyValues.c004 = :targetDate          -- đúng ngày đang tính (yyyy/MM/dd)
   AND ConCustomers.c052 IS NULL                          -- Hộ chưa bị xóa logic
 ORDER BY ConSensorHourlyValues.c001
```
Nguồn: `CalcMonthlyRoomTemperatureCommand.php:371-430` (build chuỗi SQL cộng 24 cột giờ tại dòng 379-395, câu SQL tại 397-414).

**Ý nghĩa các cột dùng trong câu SQL:**

| Bảng | Cột | Ý nghĩa |
|---|---|---|
| `t_101` | `c001` | Mã hộ（EMS-SP）— khóa nối |
| `t_101` | `c012`,`c042`,`c015`,`c016`,`c024` | 5 thuộc tính nhóm hộ (kết cấu nhà, công suất sưởi, diện tích sàn, số người, đồng phát gas) — copy nguyên sang `s_103` làm `c111`〜`c115` |
| `t_101` | `c052` | Thời điểm xóa logic — `IS NULL` = hộ còn hiệu lực |
| `s_102` | `c001` | Mã hộ — khóa nối |
| `s_102` | `c002` | Loại thiết bị — lọc `= 6` |
| `s_102` | `c003` | Vị trí cảm biến (0 = E0, 1 = E1) — mỗi hộ có tối đa 2 dòng, 1/vị trí |
| `s_102` | `c004` | Ngày — lọc đúng ngày đang tính |
| `s_102` | `c011`〜`c034` | 24 giá trị nhiệt độ trung bình theo giờ (giờ 0〜23), có thể NULL |

**Hằng số nghiệp vụ**: `ROOM_TEMPERATURE = 6` (`sources/conciergesv-develop/config/const.php:184`) — câu SQL dùng trực tiếp giá trị số `6`, không gọi tên hằng.

### 2.3 Tính trung bình ngày & ghi kết quả — bảng đích `s_103` (`updateSensorMonthlyValue`)

```
Với mỗi dòng kết quả (1 hộ × 1 vị trí cảm biến):
① Nếu total = 0 VÀ totalnumber = 0 (không có giờ nào có dữ liệu trong ngày) → BỎ, không ghi
② Ngược lại → trung bình ngày = total / totalnumber
③ Ghi vào s_103:
   - Khóa: ems_sp, device_type (= 6, lấy từ dòng s_102), room_id (0/1, lấy từ dòng s_102),
     date = ngày 1 của tháng chứa calculationDate (yyyy/MM/01)
   - Cột ngày tương ứng: c0(ngày_của_calculationDate + 10) = trung bình ngày
     (ví dụ calculationDate = ngày 5 → cột c015; ngày 31 → cột c041)
   - group_attr1〜5 = 5 thuộc tính nhóm lấy từ t_101 (mục 2.2)
   - need_agg_complete_flag = 1
   - modified = thời điểm hiện tại
④ Nếu ghi 1 hộ bị lỗi (exception) → log ALERT, resultCode = false, KHÔNG dừng vòng lặp — tiếp tục ghi các hộ còn lại
```
Nguồn: `CalcMonthlyRoomTemperatureCommand.php:315-363`.

### 2.4 Tái tính toán dữ liệu giờ của tháng trước + tháng này

#### 2.4.1 Lấy dữ liệu tái tính toán (`getRecalculationData`)

```sql
-- Cấu trúc SQL giống mục 2.2, khác điều kiện lọc ngày:
...
   AND ConSensorHourlyValues.c004 > :startDate            -- ngày 1 của (tháng calculationDate − 1 tháng), không lấy đúng ngày này
   AND ConSensorHourlyValues.c004 < :targetDate            -- ngày của calculationDate, không lấy đúng ngày này
...
```
- `targetDate` = ngày của `calculationDate` (yyyy/MM/dd).
- `startDate` = ngày 1 của (tháng của `calculationDate` − 1 tháng) (yyyy/MM/dd); nếu `calculationDate` ở tháng 1, phép trừ tháng tự lùi về tháng 12 năm trước.
- Phạm vi lấy dữ liệu: từ ngày 2 của tháng trước đến hết ngày trước `calculationDate` — tức đúng "tháng này + tháng trước", theo comment gốc trong code là do dữ liệu tháng chỉ giữ lại trong phạm vi 2 tháng (tháng này + tháng trước).
- Trả về nhiều dòng, mỗi dòng ứng với 1 (hộ × vị trí cảm biến × ngày) trong phạm vi trên, cùng cấu trúc `total`/`totalnumber` như mục 2.2.

Nguồn: `CalcMonthlyRoomTemperatureCommand.php:234-306` (comment giữ liệu tại dòng 241, câu SQL tại 264-286).

#### 2.4.2 Ghi kết quả tái tính vào `s_103` (`updateRecalculationData`)

```
Với mỗi dòng kết quả (1 hộ × 1 vị trí cảm biến × 1 ngày trong phạm vi tái tính):
① Nếu total = 0 VÀ totalnumber = 0 → BỎ, không ghi
② Ngược lại → trung bình ngày = total / totalnumber
③ Ghi vào s_103 (cùng cấu trúc khóa/cột như mục 2.3), nhưng:
   - date = ngày 1 của THÁNG CHỨA NGÀY ĐANG XÉT trong dòng dữ liệu (không phải tháng của calculationDate)
   - Cột ngày tương ứng = c0(ngày_của_dòng_dữ_liệu + 10)
   - need_agg_complete_flag = 1 CHỈ KHI tháng của ngày đang xét trùng với tháng của calculationDate;
     nếu là tháng trước thì KHÔNG set trường này
④ Nếu ghi 1 hộ bị lỗi (exception) → log CRITICAL, resultCode = false, DỪNG vòng lặp ngay (break)
```
Nguồn: `CalcMonthlyRoomTemperatureCommand.php:121-183`.

#### 2.4.3 Đánh dấu nguồn `s_102` đã tổng hợp (`updateSourceData`)

```
Chỉ chạy khi bước 2.4.2 thành công. Với mỗi dòng đã ghi ở 2.4.2 (total != 0 và totalnumber != 0):
① Ghi vào s_102 (ConSensorHourlyValue, không phải s_103):
   - Khóa: ems_sp, device_type, room_id, date = đúng ngày của dòng dữ liệu (yyyy/MM/dd)
   - need_agg_complete_flag = 2
   - modified = thời điểm hiện tại
② Nếu ghi 1 hộ bị lỗi (exception) → log ALERT, resultCode = false, KHÔNG dừng vòng lặp — tiếp tục các hộ còn lại
```
Nguồn: `CalcMonthlyRoomTemperatureCommand.php:191-226`.

### 2.5 Transaction

```
1. getSensorHourlyValue (mục 2.2) — nếu lỗi SQL → return ngay, KHÔNG mở transaction, KHÔNG chạy các bước sau
2. Mở transaction
3. updateSensorMonthlyValue (mục 2.3) — lỗi → rollback, dừng
4. getRecalculationData (mục 2.4.1) — lỗi → rollback, dừng
5. updateRecalculationData (mục 2.4.2), rồi updateSourceData (mục 2.4.3) — lỗi ở 1 trong 2 → rollback, dừng
6. Cả 5 bước trên đều thành công → commit
```
Nguồn: `CalcMonthlyRoomTemperatureCommand.php:57-112`.

Batch này **không tự gửi thông báo, không tự tính tiếp giá trị năm** — đó là việc của các batch khác đọc `s_103` sau này (nằm ngoài phạm vi command này).
