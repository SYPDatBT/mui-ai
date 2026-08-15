# Batch cũ — CalcMonthlyAverageSetTemperatureCommand（月毎平均設定温度算出）

## Tóm tắt

`CalcMonthlyAverageSetTemperatureCommand` là batch chạy **1 lần/ngày, chỉ trong mùa sưởi ấm (khoảng 1/12 ~ 31/3)** trong hệ thống cũ (EMINEL コンシェルジュサーバー). Mỗi lần chạy, batch gộp **toàn bộ bản ghi trạng thái thiết bị cảm biến môi trường trong đúng 1 ngày** (nhiều lần đọc, không phân biệt phòng/thiết bị) thành **1 giá trị trung bình duy nhất** cho mỗi hộ — đại diện cho nhiệt độ cài đặt (設定温度) trung bình trong ngày đó. Batch chỉ đọc/ghi DB (không gửi mail, không xuất file), kết quả ghi vào bảng `s_103`. Tên batch ghi "月毎/Monthly" vì bảng đích lưu 1 dòng = 1 hộ × 1 tháng × 31 cột ngày — đó là đơn vị **lưu trữ**; đơn vị **tính** của batch này là 1 ngày (mỗi lần chạy chỉ tính và ghi đúng 1 cột ngày). Chi tiết lịch chạy, câu query, công thức tính và các batch dùng lại kết quả này trình bày ở Phần 2.

## Phần 1 — Tổng quát

| Mục | Nội dung |
|---|---|
| **Vai trò** | Gộp (nhiều→một) toàn bộ bản ghi trạng thái thiết bị cảm biến môi trường (lớp 0F45) phát sinh trong 1 ngày thành 1 giá trị nhiệt độ cài đặt trung bình/hộ/ngày, để làm dữ liệu nguồn cho batch tổng hợp tháng và tính năng thưởng điểm "エコ暖房" (eco sưởi ấm) dựa trên hành vi cài nhiệt độ. |
| **Input** | Chỉ đọc DB, **không gọi API ngoài, không đọc file CSV**: `t_101`（danh sách hộ）＋ `t_202`（bản ghi trạng thái thiết bị thô, đã được hệ thống khác ingest từ trước — cột `c219` chứa giá trị cài đặt thô）. |
| **Output** | **Chỉ ghi DB** — mỗi lần chạy, với mỗi hộ có dữ liệu, ghi/cập nhật **1 cột ngày** trong **1 dòng** của `s_103`（entity `ConSensorDailyValue`, qua thư viện chung `EminelSvLib`）. Không gửi mail, không xuất CSV. |
| **Khái quát xử lý** | 1. Xác định "ngày tính" (mặc định = hôm nay trừ 1 ngày), suy ra khung `[ngày 00:00, ngày+1 00:00)`.<br>2. Lấy toàn bộ hộ chưa xóa logic (`t_101`).<br>3. Với mỗi hộ: query `t_202` lấy MỌI bản ghi trạng thái thiết bị lớp 0F45 (loại bản ghi EA/EB) rơi trong khung ngày đó, sắp theo thời gian.<br>4. Với từng bản ghi: cắt 2 ký tự từ cột `c219`, đổi hex→thập phân; gộp toàn bộ giá trị trong ngày bằng trung bình cộng, rồi chia 10.<br>5. Ghi giá trị trung bình (nếu có ít nhất 1 bản ghi) vào đúng cột-ngày tương ứng trong dòng-tháng của `s_103`, toàn bộ trong 1 transaction. Hộ không có bản ghi nào trong ngày thì không ghi gì (không có bản ghi null cho ngày đó). |

## Phần 2 — Chi tiết

### 2.1 Lịch chạy & mốc thời gian tính

| Mục | Nội dung | Nguồn |
|---|---|---|
| Lịch chạy (cron) | 3 dòng cấu hình, cùng chạy `10_CalcMonthlyAverageSetTemperature.sh` lúc **15:10**: `10 15 2-31 12 * *`（mỗi ngày tháng 12, trừ ngày 1）, `10 15 * 1,2,3 *`（mọi ngày tháng 1/2/3）, `10 15 1 4 *`（riêng ngày 1/4） | `docs/02_詳細設計/10_バッチ処理/mng-webap_cron設定_20241029.txt:30-33` |
| Command thực thi | `php cake.php CalcMonthlyAverageSetTemperature [算出年月日]`（tham số `--date`, tùy chọn） | `CalcMonthlyAverageSetTemperatureCommand.php:24,38-42` |
| Ngày tính (khi không truyền `--date`) | `hôm nay − THIS_MONTH_CORRECTION_DATE(1 ngày)` = **hôm qua** | `CalcMonthlyAverageSetTemperatureCommand.php:62-66`, `const.php:593` |
| Khung dữ liệu | `[ngày tính 00:00:00, ngày tính+1 00:00:00)` | `CalcMonthlyAverageSetTemperatureCommand.php:69-72` |
| Ghi kết quả | 1 giá trị trung bình/hộ/ngày, ghi vào `s_103` | — |

**Vì sao lịch cron chia 3 dòng thay vì 1 dòng đơn giản:** do "ngày tính" luôn lùi lại 1 ngày so với ngày chạy, để phủ đúng trọn mùa sưởi ấm (1/12 ~ 31/3) thì lịch chạy phải là 2/12 ~ 1/4 — không thể biểu diễn bằng 1 biểu thức cron chuẩn khi khoảng ngày vắt qua nhiều tháng có số ngày khác nhau, nên phải tách thành 3 dòng (tháng 12 từ ngày 2, trọn tháng 1–3, và riêng ngày 1/4).

### 2.2 Câu query lấy dữ liệu

Với mỗi hộ (lặp tuần tự, không phải 1 câu SQL gộp tất cả hộ):

```php
$deviceStatus = $deviceStatuses->find()
    ->select(['ems_sp' => c001, 'record_type' => c003, 'record_time' => c004, 'dev_epccf' => c219])
    ->where([
        c001 => $emsSp,
        c004 . ' >=' => $periodFrom,      // 00:00:00 ngày tính
        c004 . ' <' => $periodTo,         // 00:00:00 ngày kế tiếp
        c003 . ' IN' => ['EA', 'EB'],
    ])
    ->andWhere(fn($exp) => $exp->between(c006, '0F4500', '0F45FF'))
    ->order(c004)
    ->all();
```
Nguồn: `CalcMonthlyAverageSetTemperatureCommand.php:102-121`.

**Ý nghĩa các cột dùng trong query:**

| Bảng | Cột | Ý nghĩa | Ghi chú |
|---|---|---|---|
| `t_101` | `c001` | Mã hộ（EMS-SP） | Duyệt tuần tự từng hộ |
| `t_101` | `c052` | Thời điểm xóa logic | `IS NULL` = hộ còn hiệu lực |
| `t_202` | `c001` | Mã hộ | Điều kiện lọc |
| `t_202` | `c003` | Loại bản ghi | Lọc `'EA'`/`'EB'` |
| `t_202` | `c004` | Thời điểm nhận | Lọc theo khung ngày, `ORDER BY` |
| `t_202` | `c006` | Mã lớp thiết bị (EOJ) | Lọc `0F4500`〜`0F45FF`（lớp cảm biến môi trường — cùng lớp thiết bị với batch `CalcTenMinutesSensorCommand`） |
| `t_202` | `c219` | Giá trị thuộc tính thô (EPC `CF`) | ⭐ Giá trị dùng để tính nhiệt độ cài đặt |

Không giới hạn số bản ghi/ngày — nếu thiết bị gửi dữ liệu nhiều lần trong ngày (nhiều thời điểm, có thể cả nhiều thiết bị cùng hộ vì không lọc theo mã thiết bị con), **tất cả** đều được đưa vào tính trung bình chung 1 con số.

### 2.3 Công thức tính (per hộ, gộp cả ngày)

```
Với mỗi bản ghi trong ngày:
    ① Lấy 2 ký tự tại vị trí offset 2 của chuỗi dev_epccf (c219): substr(dev_epccf, 2, 2)
    ② Đổi hex → thập phân, đưa vào mảng giá trị của hộ

Sau khi duyệt hết bản ghi trong ngày (mảng có ít nhất 1 phần tử):
    trung bình = tổng(mảng) / số phần tử(mảng)
    trung bình = trung bình / 10
```
Nguồn: `CalcMonthlyAverageSetTemperatureCommand.php:136-143` (`array_sum`, `hexdec`, `substr`).

Không có bước loại giá trị đặc biệt/ngoài dải hợp lệ (khác với công thức của `CalcTenMinutesSensorCommand`) — mọi bản ghi khớp điều kiện query đều được đưa vào tính trung bình nguyên trạng. Nếu hộ không có bản ghi nào khớp điều kiện trong ngày, khối tính toán và ghi kết quả không chạy (bỏ qua hộ đó cho ngày này).

### 2.4 Ghi kết quả — bảng đích `s_103`

- Entity: `ConSensorDailyValue` (thư viện chung `EminelSvLib`), bảng vật lý `s_103` — 1 dòng = 1 hộ × 1 tháng, 31 cột ngày (`c011`~`c041`).
- Mỗi lần chạy, với mỗi hộ có dữ liệu: set `device_type = ROOM_TEMP_SETTING (17)`, `room_id = 0`, `datetime` = ngày-01 của tháng chứa "ngày tính" (dùng làm khóa dòng-tháng), rồi set giá trị trung bình vào đúng cột ngày tương ứng (`c0` + (số ngày trong tháng + 10)) và cập nhật `c051` (thời điểm sửa).
- Toàn bộ nằm trong **1 transaction cho cả batch**: nếu ghi thất bại ở bất kỳ hộ nào → `rollback()` toàn bộ và `abort()`.
- Nếu lấy danh sách hộ hoặc lấy dữ liệu thiết bị của 1 hộ bị lỗi → batch gọi `commit()` (không rollback) rồi `abort()` ngay, dừng xử lý các hộ còn lại — khác với nhánh lỗi khi ghi kết quả (dùng `rollback()`).

Nguồn: `CalcMonthlyAverageSetTemperatureCommand.php:165-193`, `ConSensorDailyValue.php:59-100`, `ConSensorDailyValuesTable.php:41`.

### 2.5 Chuỗi tổng hợp & tính năng dùng kết quả

Batch này là mắt xích đầu tiên trong chuỗi tổng hợp nhiệt độ cài đặt, đồng thời kết quả cũng được đọc trực tiếp bởi 1 API:

```
t_202 (raw, lớp 0F45, thuộc tính CF)
   │  CalcMonthlyAverageSetTemperatureCommand  (☚ batch đang phân tích — chạy 1 lần/ngày, mùa sưởi ấm)
   ▼
s_103  "ConSensorDailyValue"   1 dòng/hộ/tháng   × 31 cột ngày   (device_type=17, room_id=0)
   │                                                    │
   │ CalcYearlyPresetTemperatureCommand                 │ GetEcoPointsController
   │ (chạy 1 lần/tháng, gộp CÁC CỘT NGÀY trong           │ (đọc thẳng dòng-tháng s_103
   │  1 tháng của s_103 thành 1 giá trị trung bình        │  của 1 hộ để hiển thị)
   │  tháng, CHỈ tính khi số ngày có dữ liệu ≥            │
   │  (số ngày trong tháng − NOT_SUMMARY_DATE_COUNT=10))  │
   ▼
s_104  "ConSensorMonthlyValue"  1 dòng/hộ/năm   × 12 cột tháng   (device_type=17, room_id=0)
   │
   │ DistributeMonthlyEcoPointsCommand
   │ (chạy 1 lần/tháng, đọc đúng cột-tháng liền trước của s_104;
   │  nếu giá trị ≤ 22.0°C → cộng 250 điểm "エコ暖房" cho hộ,
   │  chặn cộng trùng bằng log lý do "monthly_eco_points_YYYYMM")
   ▼
Hộ được cộng điểm eco qua ConEcoPoints / PointInfinity
```

Nguồn: `CalcYearlyPresetTemperatureCommand.php:64-137`, `const.php:595` (`NOT_SUMMARY_DATE_COUNT=10`), `DistributeMonthlyEcoPointsCommand.php:33,79-114` (`BENEFIT_POINTS=250`), `GetEcoPointsController.php:109-118`.

Cùng lý do đặt tên như batch chính: `CalcYearlyPresetTemperatureCommand` ghi tên "Yearly" nhưng mỗi lần chạy chỉ gộp dữ liệu của **1 tháng** (nhiều cột-ngày → một cột-tháng) rồi ghi vào đúng 1 cột-tháng của dòng-năm — đơn vị lưu trữ là năm, đơn vị tính vẫn là tháng.

---
