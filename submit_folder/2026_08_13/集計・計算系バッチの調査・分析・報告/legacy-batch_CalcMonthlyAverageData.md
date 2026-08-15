# Batch cũ — CalcMonthlyAverageDataCommand（月毎平均データ算出）

## Tóm tắt

`CalcMonthlyAverageDataCommand` là batch chạy **1 lần/ngày** (cron 15:10) trong hệ thống cũ (EMINEL コンシェルジュサーバー). Với mỗi 1 trong 4 loại chỉ số (ガス総合消費量/ガス給湯消費量/消費電力量/室内温度), batch **gộp giá trị tiêu thụ của NGÀY vừa kết thúc từ RẤT NHIỀU hộ có cùng thuộc tính nhà ở** (loại nhà, công suất sưởi, diện tích sàn, số người trong hộ, loại cogeneration) **lại thành 1 con số trung bình duy nhất đại diện cho cả nhóm** — cùng cơ chế với batch cùng họ `CalcDailyAverageDataCommand` (chạy theo giờ, xem tài liệu riêng), chỉ khác đơn vị tính là NGÀY thay vì GIỜ. Batch chỉ đọc/ghi DB (không gửi mail, không xuất file). Ngoài tính trung bình cho ngày hiện tại, batch còn **truy hồi (retroactive)** tối đa khoảng 1 tháng trước để tính bù cho các ngày trước đó nếu trước kia chưa đủ dữ liệu. Chi tiết SQL, công thức và hằng số nghiệp vụ trình bày ở Phần 2.

## Phần 1 — Tổng quát

| Mục | Nội dung |
|---|---|
| **Vai trò** | Với 1 trong 4 loại chỉ số tiêu thụ, **gộp NHIỀU hộ có cùng thuộc tính nhà ở lại thành 1 con số trung bình duy nhất theo NGÀY** (không phải tính riêng cho từng hộ) — con số này là vế "benchmark nhóm" để app so với số tiêu thụ thật của 1 hộ cụ thể; đồng thời truy hồi tính lại các ngày trước đó khi dữ liệu hộ đến muộn. |
| **Input** | Chỉ đọc DB, **không gọi API ngoài, không đọc file CSV**: `s_103`（giá trị theo từng ngày của **từng hộ**, đã được batch khác tính sẵn, có kèm 5 thuộc tính nhóm denormalize từ `t_101`）＋ CHÍNH bảng `s_113`（dùng lại để tra "mẫu số nhóm" — số hộ thuộc mỗi nhóm tại ngày tương ứng, điều kiện `device_type=16`）＋ tham số dòng lệnh `--type`, `--datetime`. |
| **Output** | Ghi vào `s_113`（entity `ConSensorDailyAveValue`), mỗi bản ghi là **1 nhóm hộ tương tự × 1 tháng**, giá trị trung bình ghi vào đúng cột ngày tương ứng. **Đây chính là số liệu "trung bình các hộ giống bạn" theo ngày** mà app dùng để so sánh với mức tiêu thụ của một hộ cụ thể — batch này chỉ tạo ra số liệu, việc đọc `s_113` để hiển thị lên app là của API/batch khác (ngoài phạm vi command này). Không gửi mail, không xuất CSV. |
| **Khái quát xử lý** | 1. Nhận tham số `type` (loại chỉ số) + `datetime` (mặc định = ngày hệ thống hiện tại − 1 ngày), validate.<br>2. Mở 1 transaction, tính trung bình theo **nhóm chi tiết** (5 thuộc tính, có gộp bucket) từ `s_103` cho đúng cột ngày; chỉ ghi nếu số hộ báo cáo ≥ 70% "mẫu số nhóm" tra từ `s_113`.<br>3. Tính tiếp trung bình theo **nhóm gộp rộng hơn** (bỏ bớt 3/5 thuộc tính, gộp về nhóm "999") — ghi **không kiểm tra ngưỡng**, làm phương án dự phòng.<br>4. Truy hồi tối đa khoảng 1 tháng trước: với nhóm nào còn cột ngày = NULL, tính lại trung bình từ `s_103` cho khung ngày đó và cập nhật.<br>5. Commit nếu mọi bước thành công, ngược lại rollback toàn bộ. |

## Phần 2 — Chi tiết

### 2.1 Lịch chạy & tham số

| Mục | Nội dung | Nguồn |
|---|---|---|
| Lịch chạy (cron) | `10 15 * * *` — 1 lần/ngày, 15:10 (cho cả 4 loại, `type2_3_5_6`) | `docs/02_詳細設計/10_バッチ処理/mng-webap_cron設定_20241029.txt:36-37` (`#11.月毎平均データ算出` → `11_CalcMonthlyAverageData_type2_3_5_6.sh`) |
| Command thực thi | `php cake.php CalcMonthlyAverageData --type=<集計種別> [--datetime=<算出日時>]` | `CalcMonthlyAverageDataCommand.php:39-45` |
| Tham số `type` | 1 ký tự — chỉ nhận 1 trong 4 giá trị: `2`=ガス総合消費量, `3`=ガス給湯消費量, `5`=消費電力量, `6`=室内温度 | `CalcMonthlyAverageDataCommand.php:89-109`, hằng số tại `config/const.php:176,178,182,184` |
| Tham số `datetime` | Format `yyyy-MM-dd`; nếu bỏ trống → `hiện tại − 1 ngày` (`yyyy-MM-dd`) | `CalcMonthlyAverageDataCommand.php:62-65,101-107` |
| Validate | Sai `type` hoặc sai format `datetime` → `checkValidate()` trả `false` → `io->abort()`, batch dừng ngay | `CalcMonthlyAverageDataCommand.php:68-72,89-112` |
| Xử lý chính | Gọi `CalcCommonAverageDataCommand::executeCommon($type, $dateTime, 2)` — tham số `2` = đơn vị tổng hợp "theo ngày trong tháng" (dùng chung code với batch giờ/năm, truyền `1`/`3`) | `CalcMonthlyAverageDataCommand.php:74-77` |

### 2.2 Tham số tổng hợp ứng với đơn vị "tháng" (`aggregationUnit = 2`)

| Tham số | Giá trị | Ý nghĩa |
|---|---|---|
| `targetDateTime` | Nối trực tiếp tham số `datetime` với chuỗi `'00:00:00'` (không có khoảng trắng ở giữa) rồi parse; hoặc `hiện tại − 1 ngày` nếu `datetime` trống | Ngày cần tính trung bình |
| `targetDateCondition` | `yyyy/MM/01` của `targetDateTime` | Dòng-tháng cần cập nhật trong `s_113` |
| `aggregateColumn` | `c0{ngày+10}` (ngày 1 → `c011`, ngày 31 → `c041`) | Cột ngày cần ghi giá trị trung bình |
| `sourceTable` | `s_103`（`ConSensorDailyValue`, giá trị theo ngày của từng hộ） | Nguồn dữ liệu để tính trung bình |
| `destinationTable` | `s_113`（`ConSensorDailyAveValue`） | Bảng đích ghi kết quả |
| `retroactiveTable` | `s_113` (chính bảng đích) | Dùng để tìm nhóm còn thiếu dữ liệu ngày trước |
| `previousColum` | Cột ngày liền trước `targetDateTime` | Điều kiện lọc nhóm cần truy hồi |

Nguồn: `CalcCommonAverageDataCommand.php:1267-1291`.

### 2.3 Ý nghĩa 5 thuộc tính nhóm (`c111`~`c115`)

Mỗi bản ghi ngày ở `s_103` được đính kèm sẵn (denormalize từ hồ sơ hộ `t_101`) 5 thuộc tính dùng để gộp nhóm hộ tương tự: loại nhà, công suất sưởi, diện tích sàn, số người trong hộ, loại cogeneration (map lần lượt vào `c111`~`c115`). Khi tính trung bình, các thuộc tính này được **gộp bucket** thô hơn (xem 2.4) trước khi `GROUP BY`.

Nguồn: `sources/eminel_sv_lib-develop/src/Model/Entity/ConSensorDailyValue.php` (khai báo `c111`~`c115`).

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
  FROM {sourceTable}   -- s_103
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
- Với mỗi nhóm, tra "mẫu số nhóm" (tổng số hộ thuộc nhóm, tính sẵn ở batch khác) từ **chính bảng** `s_113` — điều kiện `device_type = 16` (mã giả lập "số hộ"), khớp 5 thuộc tính nhóm, dòng-tháng (`yyyy/MM/01`) + cột ngày tương ứng.
- Nếu `count` (số hộ đã báo cáo) / mẫu số nhóm × 100 < `AVERAGE_CALCULATION_THRESHOLD` (**70**) → **bỏ qua, không ghi** nhóm này ở bước 1.
- Nếu mẫu số nhóm = 0 → cũng bỏ qua.

Nguồn: `CalcCommonAverageDataCommand.php:1066-1149`; hằng số `AVERAGE_CALCULATION_THRESHOLD` tại `config/const.php:599`.

Nhóm đạt ngưỡng → ghi/update 1 bản ghi vào `s_113` (khoá: `device_type`, `room_id`, dòng-tháng (`c003`), 5 thuộc tính nhóm đã gộp bucket), set giá trị trung bình vào đúng cột ngày (`aggregateColumn`).

### 2.5 Bước 2 — Trung bình nhóm gộp rộng hơn (`updatePartGroupAverage`)

Chạy tiếp ngay sau bước 1, với cách gộp **thô hơn**: chỉ giữ `c111` nguyên bản, `c112` gộp về `1/2/3` hoặc `201`; **`c113`, `c114`, `c115` cố định = `999`** (bỏ qua, coi mọi hộ cùng loại nhà là 1 nhóm rộng). Bước này **không kiểm tra ngưỡng 70%** — luôn ghi đè nhóm rộng, làm phương án dự phòng khi nhóm chi tiết ở bước 1 chưa đủ dữ liệu.

Nguồn: `CalcCommonAverageDataCommand.php:868-943` (`updatePartGroupAverage`, `getPartGroupAverageCalculation`).

### 2.6 Bước 3 — Truy hồi tối đa khoảng 1 tháng trước (`retroactiveMonthly`)

- Lấy danh sách nhóm trong `s_113` mà cột ngày **liền trước** ngày đang tính vẫn còn `NULL` (`getTargetGroup`, điều kiện `previousColum IS NULL`).
- Với mỗi nhóm, lùi dần từng ngày (giới hạn kỹ thuật của vòng lặp là 62 ngày, nhưng chặn thực tế ở `retroactiveLimit` = ngày 01 của [tháng đang tính trừ 1 tháng]), tìm ngày còn thiếu dữ liệu.
- Khi lùi sang một tháng khác, đọc lại dòng-tháng tương ứng trong `s_113` (`getAggregationTarget`) để biết cột ngày nào của tháng đó còn `NULL`.
- Với ngày còn thiếu: tính lại trung bình từ `s_103` cho đúng tháng + nhóm đó (`getRetroactiveData` — cùng logic AVG theo nhóm như bước 1, nhưng theo điều kiện thuộc tính nhóm đã lưu sẵn trong `s_113`, không gộp bucket lại), rồi ghi đè vào `s_113` (`updateRetroactiveData`).
- Dừng lùi tiếp cho 1 nhóm ngay khi gặp ngày đã có dữ liệu (không `NULL`).

Nguồn: `CalcCommonAverageDataCommand.php:112-132,226-310,591-815`.

### 2.7 Transaction & hằng số nghiệp vụ

- Toàn bộ 3 bước (2.4 → 2.6) nằm trong **1 transaction cho cả lần chạy**: bất kỳ bước nào trả về lỗi → `rollback()`; cả 3 bước thành công mới `commit()`.
- Batch này **không tự gửi thông báo**; dữ liệu `s_113` được các API/batch khác đọc để hiển thị "so với hộ tương tự" trên app (nằm ngoài phạm vi command này).
- Bảng `s_113` (entity `ConSensorDailyAveValue`, comment trong code "月毎平均センサ情報 Entity") lưu trữ theo đơn vị **THÁNG** (1 dòng = 1 tháng × 31 cột ngày) — cùng cách đặt tên theo đơn vị lưu trữ (không phải đơn vị tính) như `CalcDailyAccumulatedValueCommand` (xem tài liệu `legacy-batch_CalcDailyAccumulatedValueCommand.md`, mục Tóm tắt); batch này tính và ghi giá trị ở granularity **NGÀY**, đúng 1 cột/lần chạy.

| Hằng số | Giá trị | Nguồn |
|---|---|---|
| `GAS_CO_TYPE_CONSUMPTION` | 2 — ガス総合消費量 | `const.php:176` |
| `GAS_WATER_HEAT_RATE` | 3 — ガス給湯消費量 | `const.php:178` |
| `POWER_CONSUMPTION` | 5 — 消費電力量 | `const.php:182` |
| `ROOM_TEMPERATURE` | 6 — 室内温度 | `const.php:184` |
| `AVERAGE_CALCULATION_THRESHOLD` | 70 (%) — ngưỡng đủ dữ liệu để ghi nhóm chi tiết | `const.php:599` |
