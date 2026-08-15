# Batch cũ — CalcDailyRoomTemperatureCommand（日毎室温データ算出）

## Tóm tắt

`CalcDailyRoomTemperatureCommand` là batch chạy mỗi giờ trong hệ thống cũ (EMINEL コンシェルジュサーバー), tính **nhiệt độ phòng trung bình trong 1 giờ vừa qua** cho từng hộ — tách riêng **2 vị trí lắp cảm biến** (E0 / E1) — từ các lần đọc thô mỗi 10 phút (tối đa 6 điểm/giờ). Batch chỉ đọc/ghi DB (không gửi mail, không xuất file): kết quả giờ hiện tại được ghi vào bảng `s_102`, đồng thời chạy thêm một lượt **backfill** để bù các giờ trước đó còn bị thiếu dữ liệu (tối đa 7 ngày). Chi tiết lịch chạy, câu SQL, công thức tính và hằng số nghiệp vụ trình bày ở Phần 2.

## Phần 1 — Tổng quát

| Mục | Nội dung |
|---|---|
| **Vai trò** | Từ các lần đọc nhiệt độ thô mỗi 10 phút, tính **nhiệt độ trung bình của 1 giờ**, tách riêng cho **2 vị trí cảm biến** (E0 / E1), theo từng hộ; đồng thời bù lại các giờ trước đó bị thiếu dữ liệu. |
| **Input** | Chỉ đọc DB, **không gọi API ngoài, không đọc file CSV**: `t_101`（danh sách hộ）＋ `t_202`（bản ghi trạng thái thiết bị thô — 2 cột `c236`/`c237` chứa giá trị nhiệt độ dạng hex）＋ `s_102`（bảng kết quả giờ theo ngày, đọc lại để tìm giờ còn NULL cần bù). |
| **Output** | **Chỉ ghi DB** — mỗi lần chạy ghi 2 bản ghi/hộ (1/vị trí cảm biến) vào `s_102`（entity `ConSensorHourlyValue`, qua thư viện chung `EminelSvLib`), cộng thêm các bản ghi backfill nếu có giờ trống. Không gửi mail, không xuất CSV. |
| **Khái quát xử lý** | 1. Xác định mốc thời gian tính (tham số hoặc giờ hiện tại − 1 giờ), validate format nếu có tham số.<br>2. Lấy toàn bộ bản ghi thô trong khung 1 giờ đó, theo mọi hộ còn hiệu lực, gộp theo hộ.<br>3. Với mỗi hộ × mỗi vị trí cảm biến: parse hex → thập phân/10, loại giá trị lỗi, tính trung bình các bản ghi hợp lệ, null hoá khi ngoài ngưỡng nhiệt độ hợp lệ.<br>4. Ghi kết quả giờ hiện tại vào `s_102`.<br>5. Nếu ghi thành công, quét ngược tối đa 168 giờ cho các hộ có giờ trước đó còn NULL, lấy lại dữ liệu thô để bù (backfill) từng giờ thiếu; toàn bộ nằm trong 1 transaction. |

## Phần 2 — Chi tiết

### 2.1 Lịch chạy & mốc thời gian tính

| Mục | Nội dung | Nguồn |
|---|---|---|
| Lịch chạy (cron) | `26 * * * *` — mỗi giờ 1 lần, phút 26 | `docs/02_詳細設計/10_バッチ処理/mng-webap_cron設定_20241029.txt:15-16` (`#5.日毎室温データ算出` → `5_CalcDailyRoomTemperature.sh`) |
| Command thực thi | `php cake.php CalcDailyRoomTemperature [--datetime="算出日時"]` | `CalcDailyRoomTemperatureCommand.php:46,62` |
| Mốc **calculationTime** (khi không truyền tham số) | `hiện tại − 1 giờ` | `CalcDailyRoomTemperatureCommand.php:65-67` |
| Khi có truyền tham số `--datetime` | Validate format `yyyy-MM-ddTHH:mm:ss+09:00` bằng regex; sai format → log ALERT rồi `abort()` | `CalcDailyRoomTemperatureCommand.php:70-77,713-724` |
| Khung dữ liệu giờ hiện tại | `[calculationTime giờ:00:00, +1 giờ)` — tối đa 6 bản ghi (mỗi 10 phút) | `CalcDailyRoomTemperatureCommand.php:643-645` |
| Ghi kết quả | Trung bình các bản ghi hợp lệ trong giờ, cho **2 vị trí cảm biến (E0/E1)**, ghi vào `s_102` | — |

### 2.2 Câu SQL lấy dữ liệu thô trong giờ (`getDeviceStatusData`)

```sql
SELECT ConCustomers.c001                              -- Mã hộ
     , ConCustomers.c012, ConCustomers.c042
     , ConCustomers.c015, ConCustomers.c016, ConCustomers.c024   -- Thuộc tính nhóm (nhà/thiết bị)
     , ConDeviceStatus.c004                            -- Thời điểm nhận
     , ConDeviceStatus.c236                            -- Nhiệt độ thô, vị trí E0
     , ConDeviceStatus.c237                            -- Nhiệt độ thô, vị trí E1
  FROM t_101 ConCustomers, t_202 ConDeviceStatus
 WHERE ConCustomers.c001 = ConDeviceStatus.c001
   AND ConDeviceStatus.c004 >= :fromDate               -- calculationTime, làm tròn giờ
   AND ConDeviceStatus.c004 <  :toDate                 -- +1 giờ
   AND ConDeviceStatus.c003 IN ('EA', 'EB')
   AND ConDeviceStatus.c006 BETWEEN '0F4500' AND '0F45FF'
   AND ConCustomers.c052 IS NULL                        -- Hộ chưa bị xóa logic
 ORDER BY ConDeviceStatus.c001, ConDeviceStatus.c004
```
Nguồn: `CalcDailyRoomTemperatureCommand.php:647-665`.

**Ý nghĩa các cột dùng trong câu SQL:**

| Bảng | Cột | Ý nghĩa | Ghi chú |
|---|---|---|---|
| `t_101` | `c001` | Mã hộ（EMS-SP） | Khóa nối |
| `t_101` | `c012` | Loại kết cấu nhà (build type) | Thuộc tính nhóm 1 |
| `t_101` | `c042` | Công suất máy sưởi (heater power) | Thuộc tính nhóm 2 |
| `t_101` | `c015` | Diện tích sàn (gross floor space) | Thuộc tính nhóm 3 |
| `t_101` | `c016` | Số người trong hộ (family size) | Thuộc tính nhóm 4 |
| `t_101` | `c024` | Có đồng phát gas hay không (gas cogeneration) | Thuộc tính nhóm 5 |
| `t_101` | `c052` | Thời điểm xóa logic | `IS NULL` = hộ còn hiệu lực |
| `t_202` | `c001` | Mã hộ | Khóa nối |
| `t_202` | `c003` | Loại bản ghi | Lọc `'EA'`/`'EB'` |
| `t_202` | `c004` | Thời điểm nhận | Lọc theo khung giờ + sắp xếp |
| `t_202` | `c006` | Mã thiết bị | Lọc `0F4500`〜`0F45FF` |
| `t_202` | `c236` | Giá trị đo thô, vị trí cảm biến **E0** | ⭐ Giá trị tính toán chính |
| `t_202` | `c237` | Giá trị đo thô, vị trí cảm biến **E1** | ⭐ Giá trị tính toán chính |

### 2.3 Công thức tính trung bình theo giờ (per hộ × per vị trí cảm biến — `getAverage`)

```
Với mỗi bản ghi thô (tối đa 6 bản ghi/giờ) của 1 hộ:
① Lấy 4 ký tự cuối chuỗi hex (c236 hoặc c237)
② Nếu giá trị = 'FFFF'? → không — điều kiện loại là '7FFF' hoặc '8000' (giá trị lỗi/chưa gắn) → BỎ bản ghi này
   Ngược lại → đổi hex → thập phân có dấu (bù 2, `changeHexToDec`), cộng vào tổng, tăng biến đếm

Khi hết bản ghi của 1 hộ (gộp theo ems_sp):
③ Nếu không có bản ghi hợp lệ nào → trung bình = null
   Ngược lại → trung bình = (tổng các giá trị hợp lệ) / (số bản ghi hợp lệ) / 10
④ Nếu trung bình ngoài khoảng [HOURLY_TEMP_LIMIT_BOTTOM, HOURLY_TEMP_LIMIT_TOP] → null
⑤ Lặp lại ③④ độc lập cho E0 và E1
```
Nguồn: `CalcDailyRoomTemperatureCommand.php:556-630` (`getAverage`), `:690-705` (`changeHexToDec`).

**Hằng số nghiệp vụ** (`sources/conciergesv-develop/config/const.php`):

| Hằng số | Giá trị | Dòng |
|---|---|---|
| `HOURLY_TEMP_LIMIT_BOTTOM` | -10.0 (ngưỡng dưới nhiệt độ hợp lệ) | `const.php:413` |
| `HOURLY_TEMP_LIMIT_TOP` | 50.0 (ngưỡng trên nhiệt độ hợp lệ) | `const.php:415` |

### 2.4 Ghi kết quả giờ hiện tại — bảng đích `s_102` (`updateAverageData`)

- Entity: `ConSensorHourlyValue` (thư viện chung `EminelSvLib`), bảng vật lý `s_102` — 1 dòng = 1 hộ × 1 vị trí cảm biến × 1 ngày, có 24 cột giờ (`c011`〜`c034`, tương ứng giờ 0〜23).
- Mỗi lần chạy: với **mỗi hộ có dữ liệu thô trong giờ**, ghi **2 bản ghi mới** — 1 cho vị trí `room_id = 0` (E0), 1 cho `room_id = 1` (E1) — set `device_type = 6`, `date` = ngày của `calculationTime`, cột giờ tương ứng (`c0XX`, XX = giờ + 11) = giá trị trung bình (hoặc null), `need_ele_complete_flag = 2`, `need_agg_complete_flag = 2`, cùng 5 thuộc tính nhóm lấy từ `t_101`.

### 2.5 Bù dữ liệu giờ trước đó còn thiếu — backfill (`checkRecalculation`)

```
1. Lấy danh sách hộ (còn hiệu lực) mà cột giờ liền trước (calculationTime − 1 giờ) trong s_102
   của ngày tương ứng đang là NULL                                          (getEmssp)
2. Với mỗi hộ:
   a. Lấy lại dòng s_102 hiện có của ngày cần backfill                      (getAggregationTarget)
   b. Lùi từng giờ (subHour = 1 → 168, tức tối đa 7 ngày):
      - Nếu cột giờ đó đã có giá trị (không NULL) và không phải giờ 0 → dừng vòng lặp, sang hộ khác
      - Ngược lại → lấy dữ liệu thô t_202 trong khung (giờ cần bù, calculationTime)  (getHourlyData)
        rồi ghi từng bản ghi thô tìm được vào đúng cột giờ của ngày bản ghi đó       (updateRecalculationData)
      - Với mỗi bản ghi thô: lấy 4 ký tự cuối hex → loại '7FFF'/'8000' → đổi hex/10,
        null hoá nếu ngoài [HOURLY_TEMP_LIMIT_BOTTOM, HOURLY_TEMP_LIMIT_TOP]          (getHourColumnNum)
      - need_agg_complete_flag = 1 nếu ngày bản ghi thô cũ hơn ngày đang tính (dữ liệu trễ),
        = 2 nếu cùng ngày
      - Nếu giờ vừa bù = giờ 0 → lấy lại dữ liệu tổng hợp của ngày trước đó, tiếp tục lùi;
        ngược lại → dừng, sang hộ khác
```
Nguồn: `CalcDailyRoomTemperatureCommand.php:115-270` (`checkRecalculation`, `updateRecalculationData`), `:308-346` (`getHourlyData`), `:355-419` (`getAggregationTarget`), `:427-470` (`getEmssp`), `:278-298` (`getHourColumnNum`).

### 2.6 Transaction

- Bước 2.4 (ghi giờ hiện tại) và bước 2.5 (backfill) nằm trong **1 transaction chung cho cả batch**: nếu bước 2.4 ghi lỗi → `rollback()` ngay, không chạy backfill; nếu bước 2.4 thành công nhưng backfill lỗi ở bất kỳ đâu → cũng `rollback()` toàn bộ; chỉ `commit()` khi cả 2 bước đều thành công.
- Batch này **không tự gửi thông báo, không tự tính tiếp giá trị ngày/tháng/năm** — đó là việc của các batch khác đọc `s_102` sau này (nằm ngoài phạm vi command này).
