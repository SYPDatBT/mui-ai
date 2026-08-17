# Batch cũ — CalcYearlyAverageDataCommand（年毎平均データ算出）

## Tóm tắt

`CalcYearlyAverageDataCommand` là batch chạy **1 lần/tháng** (cron ngày 1, 16:10) trong hệ thống cũ (EMINEL コンシェルジュサーバー). Với 1 trong các loại chỉ số tiêu thụ (ガス総合消費量/ガス給湯消費量/消費電力量/室内温度, và theo code còn cho phép cả エネルギー消費量), batch **gộp giá trị tiêu thụ của THÁNG vừa kết thúc từ RẤT NHIỀU hộ có cùng thuộc tính nhà ở** (loại nhà, công suất sưởi, diện tích sàn, số người trong hộ, loại cogeneration) **lại thành 1 con số trung bình duy nhất đại diện cho cả nhóm** — cùng cơ chế với 2 batch cùng họ `CalcDailyAverageDataCommand` (tính theo giờ, chạy mỗi giờ) và `CalcMonthlyAverageDataCommand` (tính theo ngày, chạy mỗi ngày), chỉ khác đơn vị lưu trữ là NĂM (12 cột tháng) thay vì NGÀY/THÁNG. Batch chỉ đọc/ghi DB (không gửi mail, không xuất file). Ngoài tính trung bình cho tháng hiện tại, batch còn **truy hồi (retroactive)** tối đa khoảng 1 năm trước để tính bù cho các tháng trước đó nếu trước kia chưa đủ dữ liệu. Chi tiết SQL, công thức và hằng số nghiệp vụ trình bày ở Phần 2.

## Phần 1 — Tổng quát

| Mục | Nội dung |
|---|---|
| **Vai trò** | Với 1 trong các loại chỉ số tiêu thụ, **gộp NHIỀU hộ có cùng thuộc tính nhà ở lại thành 1 con số trung bình duy nhất theo THÁNG** (không phải tính riêng cho từng hộ) — con số này là vế "benchmark nhóm" để app so với số tiêu thụ thật của 1 hộ cụ thể; đồng thời truy hồi tính lại các tháng trước đó khi dữ liệu hộ đến muộn. |
| **Input** | Chỉ đọc DB, **không gọi API ngoài, không đọc file CSV**: `s_104`（giá trị theo từng tháng của **từng hộ**, đã được batch khác tính sẵn, có kèm 5 thuộc tính nhóm denormalize từ `t_101`）＋ CHÍNH bảng `s_114`（dùng lại để tra "mẫu số nhóm" — số hộ thuộc mỗi nhóm tại tháng tương ứng, điều kiện `device_type=16`）＋ tham số dòng lệnh `--type`, `--datetime`. |
| **Output** | Ghi vào `s_114`（entity `ConSensorMonthlyAveValue`), mỗi bản ghi là **1 nhóm hộ tương tự × 1 năm**, giá trị trung bình ghi vào đúng cột tháng tương ứng. **Đây chính là số liệu "trung bình các hộ giống bạn" theo tháng** mà app dùng để so sánh với mức tiêu thụ của một hộ cụ thể — batch này chỉ tạo ra số liệu, việc đọc `s_114` để hiển thị lên app là của API/batch khác (ngoài phạm vi command này). Không gửi mail, không xuất CSV. |
| **Khái quát xử lý** | 1. Nhận tham số `type` (loại chỉ số) + `datetime` (mặc định = tháng hệ thống hiện tại trừ 1 tháng), validate.<br>2. Mở 1 transaction, tính trung bình theo **nhóm chi tiết** (5 thuộc tính, có gộp bucket) từ `s_104` cho đúng cột tháng; chỉ ghi nếu số hộ báo cáo ≥ 70% "mẫu số nhóm" tra từ `s_114`.<br>3. Tính tiếp trung bình theo **nhóm gộp rộng hơn** (bỏ bớt 3/5 thuộc tính, gộp về nhóm "999") — ghi **không kiểm tra ngưỡng**, làm phương án dự phòng.<br>4. Truy hồi tối đa khoảng 1 năm trước: với nhóm nào còn cột tháng = NULL, tính lại trung bình từ `s_104` cho khung tháng đó và cập nhật.<br>5. Commit nếu mọi bước thành công, ngược lại rollback toàn bộ. |

## Phần 2 — Chi tiết

### 2.1 Lịch chạy & tham số

| Mục | Nội dung | Nguồn |
|---|---|---|
| Lịch chạy (cron) | `10 16 1 * *` — 1 lần/tháng, ngày 1 lúc 16:10 (cho các loại `type2_3_5_6`) | `docs/02_詳細設計/10_バッチ処理/mng-webap_cron設定_20241029.txt:61-62` (`#18.年毎平均データ算出` → `18_CalcYearlyAverageData_type2_3_5_6.sh`) |
| Command thực thi | `php cake.php CalcYearlyAverageData --type=<集計種別> [--datetime=<算出日時>]` | `CalcYearlyAverageDataCommand.php:39-45` |
| Tham số `type` | 1 ký tự — theo code (`checkValidate`) nhận **5** giá trị: `1`=エネルギー消費量, `2`=ガス総合消費量, `3`=ガス給湯消費量, `5`=消費電力量, `6`=室内温度; riêng tên file shell script chạy cron (`type2_3_5_6`) chỉ nêu **4** giá trị `2,3,5,6`, không có `1` | `CalcYearlyAverageDataCommand.php:89-113`; hằng số tại `config/const.php:174,176,178,182,184` |
| Tham số `datetime` | Format `yyyy-MM`; nếu bỏ trống → `hiện tại − 1 tháng` (`yyyy-MM`) | `CalcYearlyAverageDataCommand.php:62-65,102-108` |
| Validate | Sai `type` (không thuộc 5 giá trị trên hoặc không đúng 1 ký tự) hoặc sai format `datetime` → `checkValidate()` trả `false` → `io->abort()`, batch dừng ngay | `CalcYearlyAverageDataCommand.php:67-72,89-113` |
| Xử lý chính | Gọi `CalcCommonAverageDataCommand::executeCommon($type, $dateTime, 3)` — tham số `3` = đơn vị tổng hợp "theo tháng trong năm" (dùng chung code với batch giờ/ngày, truyền `1`/`2`) | `CalcYearlyAverageDataCommand.php:74-77` |

### 2.2 Tham số tổng hợp ứng với đơn vị "năm" (`aggregationUnit = 3`)

| Tham số | Giá trị | Ý nghĩa |
|---|---|---|
| `targetDateTime` | Nối tham số `datetime` với chuỗi `'-01 00:00:00'` rồi parse; hoặc `hiện tại − 1 tháng` nếu `datetime` trống | Tháng cần tính trung bình |
| `targetDateCondition` | `yyyy` của `targetDateTime` | Dòng-năm cần cập nhật trong `s_114` |
| `aggregateColumn` | `c0{tháng+10}` (tháng 1 → `c011`, tháng 12 → `c022`) | Cột tháng cần ghi giá trị trung bình |
| `sourceTable` | `s_104`（`ConSensorMonthlyValue`, giá trị theo tháng của từng hộ） | Nguồn dữ liệu để tính trung bình |
| `destinationTable` | `s_114`（`ConSensorMonthlyAveValue`） | Bảng đích ghi kết quả |
| `retroactiveTable` | `s_114` (chính bảng đích) | Dùng để tìm nhóm còn thiếu dữ liệu tháng trước |
| `previousColum` | Cột tháng liền trước `targetDateTime` | Điều kiện lọc nhóm cần truy hồi |

Nguồn: `CalcCommonAverageDataCommand.php:1292-1317`.

### 2.3 Ý nghĩa 5 thuộc tính nhóm (`c111`~`c115`)

Mỗi bản ghi tháng ở `s_104` được đính kèm sẵn (denormalize từ hồ sơ hộ `t_101`) 5 thuộc tính dùng để gộp nhóm hộ tương tự: loại nhà, công suất sưởi, diện tích sàn, số người trong hộ, loại cogeneration (map lần lượt vào `c111`~`c115`). Khi tính trung bình, các thuộc tính này được **gộp bucket** thô hơn (xem 2.4) trước khi `GROUP BY` — logic gộp bucket giống hệt 2 batch cùng họ (Daily/Monthly).

### 2.4 Bước 1 — Trung bình nhóm chi tiết (`updateGroupAverage`)

```sql
-- Truy vấn con: chuẩn hoá/gộp bucket cho từng thuộc tính nhóm
SELECT c002, c003, {periodColumn},
       c111,
       CASE WHEN c112 IN (1,2,3) THEN c112 ELSE 201 END AS c112,
       CASE WHEN c113 IN (1,2,3) THEN 301
            WHEN c113 IN (5,6)   THEN 302
            ELSE c113 END AS c113,
       CASE WHEN c114 IN (1,2) THEN 401
            WHEN c114 IN (3,4) THEN 402
            ELSE 403 END AS c114,
       CASE WHEN c115 IN (1,2) THEN c115 ELSE 501 END AS c115,
       {aggregateColumn}
  FROM {sourceTable}   -- s_104
 WHERE c002 = :type
   AND {periodColumn} = :targetDateCondition
   AND c111 IN (1,2) AND c112 IN (1,2,3,4,9) AND c113 IN (1,2,3,4,5,6)
   AND c114 IN (1,2,3,4,5,6) AND c115 IN (1,2,9,10)
   AND {aggregateColumn} IS NOT NULL

-- Truy vấn ngoài: AVG + COUNT theo nhóm đã gộp bucket
SELECT c002, c003, {periodColumn}, c111, c112, c113, c114, c115,
       AVG({aggregateColumn}) AS {aggregateColumn},
       COUNT({aggregateColumn}) AS count
  FROM (<truy vấn con trên>) AS sensorInfo
 GROUP BY c002, c003, {periodColumn}, c111, c112, c113, c114, c115
```
Nguồn: `CalcCommonAverageDataCommand.php:1156-1228` (`getGroupAverageCalculation`).

**Kiểm tra đủ dữ liệu trước khi ghi** (`checkGroupDataNum`, chỉ áp dụng ở bước này):
- Với mỗi nhóm, tra "mẫu số nhóm" (tổng số hộ thuộc nhóm, tính sẵn ở batch khác) từ **chính bảng** `s_114` — điều kiện `device_type = 16` (mã giả lập "số hộ"), khớp 5 thuộc tính nhóm, dòng-năm (giá trị năm dạng số nguyên) + cột tháng tương ứng.
- Nếu `count` (số hộ đã báo cáo) / mẫu số nhóm × 100 < `AVERAGE_CALCULATION_THRESHOLD` (**70**) → **bỏ qua, không ghi** nhóm này ở bước 1.
- Nếu mẫu số nhóm = 0 → cũng bỏ qua.

Nguồn: `CalcCommonAverageDataCommand.php:1039-1149`, riêng nhánh năm (`case 3`) tại `1086-1092`; hằng số `AVERAGE_CALCULATION_THRESHOLD` tại `config/const.php:599`.

Nhóm đạt ngưỡng → ghi/update 1 bản ghi vào `s_114` (khoá: `device_type`, `room_id`, dòng-năm (`c003`, ép kiểu số nguyên — khác với Daily/Monthly ghi dòng-ngày/dòng-tháng dạng ngày tháng), 5 thuộc tính nhóm đã gộp bucket), set giá trị trung bình vào đúng cột tháng (`aggregateColumn`).

### 2.5 Bước 2 — Trung bình nhóm gộp rộng hơn (`updatePartGroupAverage`)

Chạy tiếp ngay sau bước 1, với cách gộp **thô hơn**: chỉ giữ `c111` nguyên bản, `c112` gộp về `1/2/3` hoặc `201`; **`c113`, `c114`, `c115` cố định = `999`** (bỏ qua, coi mọi hộ cùng loại nhà là 1 nhóm rộng). Bước này **không kiểm tra ngưỡng 70%** — luôn ghi đè nhóm rộng, làm phương án dự phòng khi nhóm chi tiết ở bước 1 chưa đủ dữ liệu.

Nguồn: `CalcCommonAverageDataCommand.php:868-943` (`updatePartGroupAverage`, `getPartGroupAverageCalculation`).

### 2.6 Bước 3 — Truy hồi tối đa khoảng 1 năm trước (`retroactiveYearly`)

- Lấy danh sách nhóm trong `s_114` mà cột tháng **liền trước** tháng đang tính vẫn còn `NULL` (`getTargetGroup`, điều kiện `previousColum IS NULL`).
- Với mỗi nhóm, lùi dần từng tháng (giới hạn kỹ thuật của vòng lặp là 24 tháng, nhưng chặn thực tế ở `retroactiveLimit` = năm [năm đang tính trừ 1]), tìm tháng còn thiếu dữ liệu.
- Khi lùi sang một năm khác, đọc lại dòng-năm tương ứng trong `s_114` (`getAggregationTarget`) để biết cột tháng nào của năm đó còn `NULL`.
- Với tháng còn thiếu: tính lại trung bình từ `s_104` cho đúng năm + nhóm đó (`getRetroactiveData` — cùng logic AVG theo nhóm như bước 1, nhưng theo điều kiện thuộc tính nhóm đã lưu sẵn trong `s_114`, không gộp bucket lại; điều kiện thời gian chỉ so khớp theo **năm**, không tách theo tháng), rồi ghi đè vào `s_114` (`updateRetroactiveData`, cập nhật đúng dải cột tháng còn thiếu).
- Dừng lùi tiếp cho 1 nhóm ngay khi gặp tháng đã có dữ liệu (không `NULL`).

Nguồn: `CalcCommonAverageDataCommand.php:139-219` (`retroactiveYearly`), `550-573` (`getRetroactiveUpdatePeriod`, nhánh năm), `645-658` (`getRetroactiveData`, nhánh năm), `758-815` (`getAggregationTarget`).

### 2.7 Transaction & hằng số nghiệp vụ

- Toàn bộ 3 bước (2.4 → 2.6) nằm trong **1 transaction cho cả lần chạy**: bất kỳ bước nào trả về lỗi → `rollback()`; cả 3 bước thành công mới `commit()`.
- Batch này **không tự gửi thông báo**; dữ liệu `s_114` được các API/batch khác đọc để hiển thị "so với hộ tương tự" trên app (nằm ngoài phạm vi command này).
- Bảng `s_114` (entity `ConSensorMonthlyAveValue`) lưu trữ theo đơn vị **NĂM** (1 dòng = 1 năm × 12 cột tháng) — cùng cách đặt tên theo đơn vị lưu trữ (không phải đơn vị tính) như 2 batch cùng họ; batch này tính và ghi giá trị ở granularity **THÁNG**, đúng 1 cột/lần chạy.
- Khác với Daily/Monthly (2 batch đó dùng chung **1 bảng `s_113`** làm nguồn tra "mẫu số nhóm" cho cả 2), batch Yearly tra "mẫu số nhóm" từ **chính bảng `s_114`**, không dùng `s_113`.

| Hằng số | Giá trị | Nguồn |
|---|---|---|
| `ENERGY_CONSUMPTION` | 1 — エネルギー消費量 (được `checkValidate` chấp nhận, nhưng không có trong tên shell script chạy cron) | `const.php:174` |
| `GAS_CO_TYPE_CONSUMPTION` | 2 — ガス総合消費量 | `const.php:176` |
| `GAS_WATER_HEAT_RATE` | 3 — ガス給湯消費量 | `const.php:178` |
| `POWER_CONSUMPTION` | 5 — 消費電力量 | `const.php:182` |
| `ROOM_TEMPERATURE` | 6 — 室内温度 | `const.php:184` |
| `AVERAGE_CALCULATION_THRESHOLD` | 70 (%) — ngưỡng đủ dữ liệu để ghi nhóm chi tiết | `const.php:599` |
