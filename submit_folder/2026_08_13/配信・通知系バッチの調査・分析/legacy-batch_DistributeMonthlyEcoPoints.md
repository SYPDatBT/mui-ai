# Batch cũ — DistributeMonthlyEcoPointsCommand（エコ暖房ポイント付与）

## Tóm tắt

`DistributeMonthlyEcoPointsCommand` là batch chạy **1 lần/tháng** trong hệ thống cũ (EMINEL コンシェルジュサーバー), cấp **250 điểm cố định** cho khách hàng có **nhiệt độ cài đặt sưởi trung bình của tháng trước ≤ 22.0°C** (dữ liệu do batch tổng hợp tháng khác tính sẵn, đọc lại ở đây). Điểm được ghi vào 2 bản ghi sổ điểm nội bộ (`s_141`) theo năm tài chính (tháng 4→tháng 3), đồng thời gọi API bên ngoài **Point Infinity** để cấp điểm thật cho khách hàng. Có cơ chế chống cấp trùng theo tháng qua bảng log `con_point_link_logs`. Toàn bộ xử lý theo từng khách hàng nằm trong transaction riêng — 1 khách hàng lỗi không làm dừng cả batch; chi tiết ở Phần 2.

## Phần 1 — Tổng quát

| Mục | Nội dung |
|---|---|
| **Vai trò** | Mỗi tháng, xét khách hàng có nhiệt độ cài đặt sưởi trung bình tháng trước ≤ 22.0°C, cấp 250 điểm sưởi tiết kiệm (nội bộ + Point Infinity). |
| **Input** | `ConSensorMonthlyValues` (`s_1xx` — giá trị trung bình tháng, `device_type=17`=nhiệt độ cài đặt) ＋ `ConCustomers` (`t_101` — số khách hàng, cờ xoá) ＋ `ConPointLinkLogs` (log chống trùng theo tháng). |
| **Output** | Ghi/cộng dồn điểm vào `ConEcoPoints` (`s_141`, 2 bản ghi/khách hàng: tổng + riêng nhiệt độ) ＋ insert `ConPointLinkLogs` ＋ gọi API `PointInfinity::givePoints()`. |
| **Khái quát xử lý** | 1. Xác định tháng cần xét = tháng trước ngày chạy, và năm tài chính tương ứng.<br>2. Lọc khách hàng có nhiệt độ cài đặt sưởi trung bình tháng đó ≤ 22.0°C và chưa được cấp điểm cho tháng này.<br>3. Với mỗi khách hàng: cộng 250 điểm vào 2 bản ghi sổ điểm, ghi log, gọi Point Infinity — tất cả trong 1 transaction/khách hàng.<br>4. Log tổng số thành công/thất bại. |

## Phần 2 — Chi tiết

### Bản đồ xử lý

```
BƯỚC 1  Xác định mốc      → tháng trước ngày chạy, năm tài chính tương ứng     §2.1
BƯỚC 2  Lọc khách hàng    → nhiệt độ cài đặt sưởi TB tháng đó ≤ 22.0°C,
                             chưa có log cấp điểm cho tháng này               §2.2
BƯỚC 3  Tìm/tạo sổ điểm   → 2 bản ghi ConEcoPoints (tổng, riêng nhiệt độ)
                             theo (ems_sp, năm tài chính)                     §2.3
BƯỚC 4  Cộng điểm         → +250 vào cột tháng + cột tổng, cho cả 2 bản ghi   §2.3
BƯỚC 5  Ghi log & cấp qua PI → insert ConPointLinkLogs, gọi PointInfinity     §2.4
        (toàn bộ BƯỚC 3-5 trong 1 transaction riêng cho từng khách hàng)
```

| Bước | Nội dung | Chi tiết ở |
|---|---|---|
| 1 | Xác định tháng xét & năm tài chính | §2.1 |
| 2 | Điều kiện lọc khách hàng đủ điều kiện | §2.2 |
| 3–4 | Cấu trúc sổ điểm `ConEcoPoints`, cách cộng điểm | §2.3 |
| 5 | Ghi log chống trùng, gọi Point Infinity | §2.4 |
| — | Nội dung request gửi Point Infinity | §2.5 |

---

### 2.1 Xác định mốc thời gian & năm tài chính

| Mục | Nội dung |
|---|---|
| Mốc mặc định | Ngày giờ hiện tại lúc chạy batch |
| Tham số chạy lại | `--datetime` — **không có tác dụng** (xem ⚠️①) |
| Tháng được xét | `targetDateTime = hiện tại − 1 tháng` ([:79](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/DistributeMonthlyEcoPointsCommand.php#L79)) |
| Năm tài chính | `targetDateTime.month >= 4` → lấy năm đó; ngược lại lấy năm trước (năm tài chính Nhật: tháng 4 → tháng 3) ([:109](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/DistributeMonthlyEcoPointsCommand.php#L109)) |
| Khoá chống trùng | `pointLinkReason = 'monthly_eco_points_' . targetDateTime→'Ym'` — cố định theo tháng được xét, không đổi trong suốt 1 lần chạy ([:80](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/DistributeMonthlyEcoPointsCommand.php#L80)) |

### 2.2 Điều kiện lọc khách hàng đủ điều kiện cấp điểm

Một truy vấn duy nhất trên `ConCustomers`, join thêm 2 điều kiện `matching`/`notMatching` ([:83-104](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/DistributeMonthlyEcoPointsCommand.php#L83-L104)):

| Điều kiện | Ý nghĩa |
|---|---|
| `matching ConSensorMonthlyValues`: `device_type = 17` (`ROOM_TEMP_SETTING`, [const.php:202](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/config/const.php#L202)), `room_id = 0`, cột tháng được xét `<= 22.0` | Nhiệt độ cài đặt sưởi trung bình (cảm biến chính) của **tháng trước** ≤ 22.0°C |
| `notMatching ConPointLinkLogs`: `reason = pointLinkReason` | Chưa được cấp điểm cho đúng tháng này (chống trùng) |
| `customer_number IS NOT NULL` | Phải có số khách hàng mới gửi được Point Infinity |
| `deleted IS NULL` (`c052`) | Khách hàng chưa bị xoá logic |

Cột tháng dùng để so sánh lấy qua `ConSensorMonthlyValue::getColumnNameOfMonth(targetDateTime.month)` — hàm này map **trực tiếp theo tháng dương lịch** (`c011`=tháng 1 … `c022`=tháng 12), không lệch theo năm tài chính ([ConSensorMonthlyValue.php:63-66](e:/Projects/mui/legacy_eminel_docs-main/sources/eminel_sv_lib-develop/src/Model/Entity/ConSensorMonthlyValue.php#L63-L66)).

### 2.3 Sổ điểm `ConEcoPoints` (bảng `s_141`) & cách cộng điểm

Với mỗi khách hàng thoả điều kiện, tìm (hoặc tạo mới) **2 bản ghi** theo khoá `(ems_sp, point_kind, năm tài chính)` ([:117-141](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/DistributeMonthlyEcoPointsCommand.php#L117-L141)):

| `point_kind` | Hằng số | Ý nghĩa |
|---|---|---|
| `0` | `POINT_KIND_TOTAL` | Tổng điểm sưởi tiết kiệm (đang được cộng chung ở đây) |
| `1` | `POINT_KIND_TEMP` | Điểm riêng theo tiêu chí nhiệt độ (batch này) |
| `2` | `POINT_KIND_ACTION` | Điểm theo hành động khác — batch này **không dùng** |

Cả 2 bản ghi đều được cộng `+250` vào cột tháng và cột tổng ([:142-147](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/DistributeMonthlyEcoPointsCommand.php#L142-L147)):

```php
$totalEcoPointRecord->addPointsToMonth($now->month, self::BENEFIT_POINTS);  // dùng $now, KHÔNG dùng $targetDateTime
$totalEcoPointRecord->addPointsToTotal(self::BENEFIT_POINTS);
```

Cột tháng được tính bởi `ConEcoPoint::getColumnNameByMonth()` — hàm này map theo **thứ tự tháng trong năm tài chính** (tháng 4 = tháng đầu năm), khác cách map lịch dương của `ConSensorMonthlyValue` ở §2.2 ([ConEcoPoint.php:81-87](e:/Projects/mui/legacy_eminel_docs-main/sources/eminel_sv_lib-develop/src/Model/Entity/ConEcoPoint.php#L81-L87)) — xem ⚠️② vì đây là nguồn của lỗi lệch cột.

### 2.4 Ghi log chống trùng & liên kết Point Infinity

Toàn bộ trong **1 transaction riêng cho từng khách hàng** ([:158-185](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/DistributeMonthlyEcoPointsCommand.php#L158-L185)):

1. `saveOrFail` 2 bản ghi `ConEcoPoints` (tổng, nhiệt độ).
2. `saveOrFail` bản ghi `ConPointLinkLogs` (`reason`, `ems_sp`, `links_cus_num`, `status='OK'`, `points=250`).
3. Nếu `PointInfinity::readHostConfig()` có cấu hình → tính số giao dịch `txNo = id bản ghi log vừa lưu − lastPointLogMaxId` ([:173](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/DistributeMonthlyEcoPointsCommand.php#L173)), rồi gọi `sendToPointInfinity()`.
4. Lỗi ở bất kỳ bước nào (kể cả Point Infinity trả lỗi) → toàn bộ transaction của **khách hàng đó** rollback, `failureCount++`, batch tiếp tục sang khách hàng kế tiếp — không dừng cả batch ([:181-185](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/DistributeMonthlyEcoPointsCommand.php#L181-L185)).

`$lastPointLogMaxId` (= ID lớn nhất của `ConPointLinkLogs` được tạo **trước ngày hôm nay**) chỉ lấy **1 lần** trước khi vào loop ([:106](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/DistributeMonthlyEcoPointsCommand.php#L106)), dùng chung cho mọi khách hàng trong lần chạy — mục đích để `txNo` là số thứ tự duy nhất trong ngày (1, 2, 3, …) theo đúng thiết kế của `ConPointLinkLogsTable::calcPointInfinityTransactionNumber()` ([ConPointLinkLogsTable.php:106-120](e:/Projects/mui/legacy_eminel_docs-main/sources/eminel_sv_lib-develop/src/Model/Table/ConPointLinkLogsTable.php#L106-L120)) — xem ⚠️③.

### 2.5 Nội dung request gửi Point Infinity

`sendToPointInfinity()` build 1 request `GivePointsRequest` với nhiều field cố định (mã tiền tệ, các mã phân loại `kmt*Id`, `termNo='eminel'`) và các field theo giao dịch ([:203-228](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/DistributeMonthlyEcoPointsCommand.php#L203-L228)):

| Field | Giá trị | Ý nghĩa |
|---|---|---|
| `kaiinNo` | Số khách hàng | Định danh khách hàng bên Point Infinity |
| `denpyoNo` | `txNo` pad 6 số | Số giao dịch duy nhất trong ngày |
| `fuyoPt` | `250` | Số điểm cấp |
| `fuyoRiyu` | `"<năm>年<tháng> EMINEL エコ暖房ポイント"` (theo `targetDateTime`, tức tháng được xét) | Lý do cấp điểm hiển thị |
| `jiyuCd` / `jiyuDetCd` | `'01'` / `'1081'` | Mã lý do cấp điểm cố định (loại "điểm sưởi tiết kiệm") trong hệ Point Infinity |

Nếu response không OK → ghi log lỗi qua `EminelLogComponent`, throw exception để transaction ở §2.4 rollback ([:224-227](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/DistributeMonthlyEcoPointsCommand.php#L224-L227)).

---

### ⚠️ Điểm bất thường của hệ cũ

**① Tuỳ chọn `--datetime` không có tác dụng.** ([:73-76](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/DistributeMonthlyEcoPointsCommand.php#L73-L76))

```php
$now = FrozenTime::now();
if ($args->hasOption('datetime')) {
    $now = FrozenTime::parse($now);   // parse lại chính $now, không lấy giá trị option
}
```

Lẽ ra phải là `FrozenTime::parse($args->getOption('datetime'))`. Hiện tại truyền `--datetime=...` không đổi được ngày tính — batch luôn chạy theo giờ hệ thống thật, không thể chạy lại/backfill cho 1 tháng chỉ định.

**② Điểm bị ghi lệch cột tháng so với tháng thực sự được đánh giá.** Điều kiện lọc (§2.2) và năm tài chính của bản ghi (§2.3) đều dựa trên `targetDateTime` (tháng trước), nhưng khi cộng điểm vào cột tháng lại dùng `$now->month` (tháng hiện tại lúc chạy batch, [:142, :145](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/DistributeMonthlyEcoPointsCommand.php#L142-L145)):

```php
$totalEcoPointRecord->addPointsToMonth($now->month, self::BENEFIT_POINTS);
```

Vì `targetDateTime = now − 1 tháng` luôn đúng ở mọi lần chạy, điểm luôn bị ghi vào **cột tháng kế tiếp** so với tháng có nhiệt độ thực sự đạt ngưỡng. Ở đúng ranh giới năm tài chính (chạy vào tháng 4), lỗi này còn nặng hơn: bản ghi được tìm/tạo theo năm tài chính của tháng 3 (`targetDateTime`), nhưng cột ghi điểm lại là cột "tháng 4" — thuộc **đầu của cùng bản ghi năm tài chính đó** (theo cách map thứ-tự-tháng của `ConEcoPoint::getColumnNameByMonth()`, không phải "tháng 4 của năm sau").

**③ Tự tính lại số giao dịch Point Infinity thay vì dùng hàm có sẵn.** `ConPointLinkLogsTable` đã có `calcPointInfinityTransactionNumber()` làm đúng việc này, nhưng command tự lặp lại logic bằng tay (`$pointLinkLog->id - $lastPointLogMaxId`) — không sai nhưng trùng lặp code, tách rời khỏi nơi định nghĩa gốc.

---

## Nguồn

| Nội dung | Căn cứ |
|---|---|
| Logic chính của batch | `sources/conciergesv-develop/src/Command/DistributeMonthlyEcoPointsCommand.php` |
| Hằng số `ROOM_TEMP_SETTING` | `sources/conciergesv-develop/config/const.php:202` |
| Bảng + hằng số cột `ConSensorMonthlyValues` | `sources/eminel_sv_lib-develop/src/Model/Entity/ConSensorMonthlyValue.php` |
| Bảng (`s_141`) + hằng số cột `ConEcoPoints` | `sources/eminel_sv_lib-develop/src/Model/Table/ConEcoPointsTable.php`, `src/Model/Entity/ConEcoPoint.php` |
| Bảng `ConPointLinkLogs` + hàm tính số giao dịch Point Infinity | `sources/eminel_sv_lib-develop/src/Model/Table/ConPointLinkLogsTable.php` |
