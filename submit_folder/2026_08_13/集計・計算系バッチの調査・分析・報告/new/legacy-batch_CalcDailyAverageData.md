# Batch cũ — CalcDailyAverageDataCommand（日毎平均データ算出）

## Tóm tắt

`CalcDailyAverageDataCommand` là batch chạy định kỳ mỗi giờ (phút 55) trong hệ thống cũ (EMINEL コンシェルジュサーバー). Với mỗi 1 trong 4 loại chỉ số (ガス総合消費量/ガス給湯消費量/消費電力量/室内温度), batch **gộp giá trị tiêu thụ của giờ vừa kết thúc từ RẤT NHIỀU hộ có cùng thuộc tính nhà ở** (loại nhà, công suất sưởi, diện tích sàn, số người trong hộ, loại cogeneration) **lại thành 1 con số trung bình duy nhất đại diện cho cả nhóm** — đây không phải so sánh hộ với hộ, mà là tạo ra vế "trung bình các hộ giống bạn" để app dùng khi hiển thị mức tiêu thụ của 1 hộ cụ thể cạnh mức trung bình của nhóm tương tự. Batch chỉ đọc/ghi DB (không gửi mail, không xuất file). Ngoài tính trung bình cho giờ hiện tại, batch còn **truy hồi (retroactive)** tối đa 7 ngày trước để tính bù cho các giờ trước đó nếu trước kia chưa đủ dữ liệu. Chi tiết SQL, công thức và hằng số nghiệp vụ trình bày ở Phần 2.

## Phần 1 — Tổng quát

| Mục | Nội dung |
|---|---|
| **Vai trò** | Với 1 trong 4 loại chỉ số tiêu thụ, **gộp NHIỀU hộ có cùng thuộc tính nhà ở lại thành 1 con số trung bình duy nhất theo giờ** (không phải tính riêng cho từng hộ) — con số này là vế "benchmark nhóm" để app so với số tiêu thụ thật của 1 hộ cụ thể; đồng thời truy hồi tính lại các giờ trước đó khi dữ liệu hộ đến muộn. |
| **Input** | Chỉ đọc DB, **không gọi API ngoài, không đọc file CSV**: `s_102`（giá trị theo từng giờ của **từng hộ**, đã được batch khác tính sẵn, có kèm 5 thuộc tính nhóm denormalize từ `t_101`）＋ `s_113`（`ConSensorDailyAveValue` — bảng trung bình NGÀY theo nhóm, được dùng kiêm nơi chứa "mẫu số nhóm": các dòng device_type=16 do batch グループ集計情報登録 (CreateGroupSummaryCommand) ghi sẵn số hộ mỗi nhóm, batch này chỉ đọc các dòng đó để kiểm ngưỡng）＋ tham số dòng lệnh `--type`, `--datetime`. |
| **Output** | Ghi vào `s_112`（entity `ConSensorHourlyAveValue`）, mỗi bản ghi là **1 nhóm hộ tương tự × 1 ngày**, giá trị trung bình ghi vào đúng cột giờ tương ứng. **Đây chính là số liệu "trung bình các hộ giống bạn"** mà app dùng để so sánh với mức tiêu thụ của một hộ cụ thể — batch này chỉ tạo ra số liệu, việc đọc `s_112` để hiển thị lên app là của API/batch khác (ngoài phạm vi command này). Không gửi mail, không xuất CSV. |
| **Khái quát xử lý** | 1. Nhận tham số `type` (loại chỉ số) + `datetime` (mặc định = giờ hệ thống hiện tại − 1h), validate.<br>2. Mở 1 transaction, tính trung bình theo **nhóm chi tiết** (5 thuộc tính, có gộp bucket) từ `s_102` cho đúng cột giờ; chỉ ghi nếu số hộ báo cáo ≥ 70% "mẫu số nhóm" tra từ `s_113`.<br>3. Tính tiếp trung bình theo **nhóm gộp rộng hơn** (bỏ bớt 3/5 thuộc tính, gộp về nhóm "999") — ghi **không kiểm tra ngưỡng**, làm phương án dự phòng.<br>4. Truy hồi tối đa 7 ngày trước: với nhóm nào còn cột giờ = NULL, tính lại trung bình từ `s_102` cho khung giờ đó và cập nhật.<br>5. Commit nếu mọi bước thành công, ngược lại rollback toàn bộ. |

## Phần 2 — Chi tiết

### 2.1 Lịch chạy & tham số

| Mục | Nội dung | Nguồn |
|---|---|---|
| Lịch chạy (cron) | `55 * * * *` — mỗi giờ cron chạy 1 lần, script gọi command 4 lần tuần tự (`--type=2→3→5→6`, mỗi lần 1 loại) | `docs/02_詳細設計/10_バッチ処理/mng-webap_cron設定_20241029.txt:21-22` (`#7.日毎平均データ算出` → `7_CalcDailyAverageData_type2_3_5_6.sh`) |
| Command thực thi | `php cake.php CalcDailyAverageData --type <集計種別> [--datetime <算出日時>]` | `CalcDailyAverageDataCommand.php:39-45` |
| Tham số `type` | 1 ký tự — chỉ nhận 1 trong 4 giá trị: `2`=ガス総合消費量, `3`=ガス給湯消費量, `5`=消費電力量, `6`=室内温度 | `CalcDailyAverageDataCommand.php:96-114`, hằng số tại `config/const.php:176,178,182,184` |
| Tham số `datetime` | Format `yyyy-MM-ddTHH:00:00+09:00`; nếu bỏ trống → `hiện tại − 1 giờ` | `CalcDailyAverageDataCommand.php:62-66,104-113` |
| Validate | Sai `type` hoặc sai format `datetime` → `checkValidate()` trả `false` → `io->abort()`, batch dừng ngay | `CalcDailyAverageDataCommand.php:68-75,92-117` |
| Xử lý chính | Gọi `CalcCommonAverageDataCommand::executeCommon($type, $dateTime, 1)` — tham số `1` = đơn vị tổng hợp "theo giờ trong ngày" (dùng chung code với batch tháng/năm, truyền `2`/`3`) | `CalcDailyAverageDataCommand.php:77-80` |

### 2.2 Tham số tổng hợp ứng với đơn vị "ngày" (`aggregationUnit = 1`)

| Tham số | Giá trị | Ý nghĩa |
|---|---|---|
| `targetDateTime` | Tham số `datetime`, hoặc `hiện tại − 1h` nếu trống | Giờ cần tính trung bình |
| `targetDateCondition` | `yyyy/MM/dd` của `targetDateTime` | Ngày cần cập nhật trong `s_112` |
| `aggregateColumn` | `c0{giờ+11}` (giờ 0 → `c011`, giờ 23 → `c034`) | Cột giờ cần ghi giá trị trung bình |
| `sourceTable` | `s_102`（`ConSensorHourlyValue`, giá trị theo giờ của từng hộ） | Nguồn dữ liệu để tính trung bình |
| `destinationTable` | `s_112`（`ConSensorHourlyAveValue`） | Bảng đích ghi kết quả |
| `retroactiveTable` | `s_112` (chính bảng đích) | Dùng để tìm nhóm còn thiếu dữ liệu giờ trước |
| `previousColum` | Cột giờ liền trước `targetDateTime` | Điều kiện lọc nhóm cần truy hồi |

Nguồn: `CalcCommonAverageDataCommand.php:1235-1265`.

### 2.3 Ý nghĩa 5 thuộc tính nhóm (`c111`~`c115`)

Mỗi bản ghi giờ ở `s_102` được đính kèm sẵn (denormalize từ hồ sơ hộ `t_101` tại thời điểm ghi) 5 thuộc tính dùng để gộp nhóm hộ tương tự: loại nhà, công suất sưởi, diện tích sàn, số người trong hộ, loại cogeneration (map lần lượt vào `c111`~`c115`). Khi tính trung bình, các thuộc tính này được **gộp bucket** thô hơn (xem 2.4) trước khi `GROUP BY`.

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
  FROM {sourceTable}   -- s_102
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
- Với mỗi nhóm, tra "mẫu số nhóm" (tổng số hộ thuộc nhóm, tính sẵn ở batch khác) từ bảng `s_113` — điều kiện `device_type = 16` (mã giả lập "số hộ"), khớp 5 thuộc tính nhóm, cột ngày tương ứng.
- Nếu `count` (số hộ đã báo cáo) / mẫu số nhóm × 100 < `AVERAGE_CALCULATION_THRESHOLD` (**70**) → **bỏ qua, không ghi** nhóm này ở bước 1.
- Nếu mẫu số nhóm = 0 → cũng bỏ qua.

Nguồn: `CalcCommonAverageDataCommand.php:1039-1149`; hằng số `AVERAGE_CALCULATION_THRESHOLD` tại `config/const.php:599`.

Nhóm đạt ngưỡng → ghi/update 1 bản ghi vào `s_112` (khoá: `device_type`, `room_id`, `date`, 5 thuộc tính nhóm đã gộp bucket), set giá trị trung bình vào đúng cột giờ (`aggregateColumn`).

### 2.5 Bước 2 — Trung bình nhóm gộp rộng hơn (`updatePartGroupAverage`)

Chạy tiếp ngay sau bước 1, với cách gộp **thô hơn**: chỉ giữ `c111` nguyên bản, `c112` gộp về `1/2/3` hoặc `201`; **`c113`, `c114`, `c115` cố định = `999`** (bỏ qua, coi mọi hộ cùng loại nhà là 1 nhóm rộng). Bước này **không kiểm tra ngưỡng 70%** — luôn ghi đè nhóm rộng, làm phương án dự phòng khi nhóm chi tiết ở bước 1 chưa đủ dữ liệu.

Nguồn: `CalcCommonAverageDataCommand.php:868-943` (`updatePartGroupAverage`, `getPartGroupAverageCalculation`).

### 2.6 Bước 3 — Truy hồi 7 ngày trước (`retroactiveDaily`)

- Lấy danh sách nhóm trong `s_112` mà cột giờ **liền trước** giờ đang tính vẫn còn `NULL` (`getTargetGroup`, điều kiện `previousColum IS NULL`).
- Với mỗi nhóm, lùi dần từng giờ (vòng lặp chặn tối đa 192 lần; mốc dừng thực tế `retroactiveLimit` = 00:00 của 7 ngày trước — tức tối đa ≈168–191 giờ tuỳ giờ chạy), tìm khung giờ còn thiếu dữ liệu.
- Với khung giờ còn thiếu: tính lại trung bình từ `s_102` cho đúng ngày + nhóm đó (`getRetroactiveData` — cùng logic AVG theo nhóm như bước 1, nhưng theo điều kiện thuộc tính nhóm đã lưu sẵn trong `s_112`, không gộp bucket lại), rồi ghi đè vào `s_112` (`updateRetroactiveData`).
- Dừng lùi tiếp cho 1 nhóm ngay khi gặp giờ đã có dữ liệu (không NULL).

Nguồn: `CalcCommonAverageDataCommand.php:112-132,317-407,591-815`.

### 2.7 Transaction & hằng số nghiệp vụ

- Toàn bộ 3 bước (2.4 → 2.6) nằm trong **1 transaction cho cả lần chạy**: bất kỳ bước nào trả về lỗi → `rollback()`; cả 3 bước thành công mới `commit()`.
- Batch này **không tự gửi thông báo**; dữ liệu `s_112` được các API/batch khác đọc để hiển thị "so với hộ tương tự" trên app (nằm ngoài phạm vi command này).

| Hằng số | Giá trị | Nguồn |
|---|---|---|
| `GAS_CO_TYPE_CONSUMPTION` | 2 — ガス総合消費量 | `const.php:176` |
| `GAS_WATER_HEAT_RATE` | 3 — ガス給湯消費量 | `const.php:178` |
| `POWER_CONSUMPTION` | 5 — 消費電力量 | `const.php:182` |
| `ROOM_TEMPERATURE` | 6 — 室内温度 | `const.php:184` |
| `AVERAGE_CALCULATION_THRESHOLD` | 70 (%) — ngưỡng đủ dữ liệu để ghi nhóm chi tiết | `const.php:599` |
