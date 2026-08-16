# Batch cũ — CalcFixedValueCommand（確定値再集計機能）

## Tóm tắt

`CalcFixedValueCommand` là batch **chạy thủ công** (không có lịch cron) trong hệ thống cũ (EMINEL コンシェルジュサーバー), dùng để (ghi lại/ghi đè) **tổng LƯỢNG điện mua theo NGÀY (買電量, kWh)** vào bảng tổng hợp theo tháng `s_103`, cho 1 hoặc nhiều hộ được chỉ định qua tham số dòng lệnh. Nguồn dữ liệu không phải từ cảm biến ECHONET (`t_202`) như các batch tính theo giờ khác, mà từ bảng `emn_confirm_electric_powers` — dữ liệu điện mua đã được **xác nhận/chốt (確定)** theo từng 30 phút, do batch khác (`RcvHalfHourElectricPowerCommand`) nạp trước đó từ nguồn ngoài "Xzilla" (情報共通基盤連携) qua CSV. Batch chỉ đọc/ghi DB, không gọi API ngoài, không gửi mail, không xuất CSV. Chi tiết tham số, câu SQL, công thức tính và cơ chế ghi/transaction trình bày ở Phần 2.

## Phần 1 — Tổng quát

| Mục | Nội dung |
|---|---|
| **Vai trò** | Ghi/ghi đè tổng 買電量 (điện mua từ lưới) theo NGÀY vào bảng tổng hợp tháng, lấy từ dữ liệu điện đã xác nhận (確定) từ Xzilla — chuỗi tổng hợp tự động từ cảm biến ECHONET hiện chỉ tính 売電 (bán điện), không tính 買電; tuy nhiên 買電 bình thường vẫn được ghi tự động vào `s_103` qua ngả 速報値: `RcvHalfHourElectricPowerCommand` (cron 10 phút/lần) tính 1時間値 từ 速報値 Xzilla (`emn_fast_electric_powers`) ghi vào `s_102`, rồi `CalcMonthlyAccumulatedValueCommand` (cron hằng ngày 3:20, `--type` có chứa 11=買電) tổng hợp vào `s_103`. Batch này là đường THỦ CÔNG tái tổng hợp/ghi đè các giá trị gốc 速報値 đó bằng 確定値 (`emn_confirm_electric_powers`); chạy thủ công theo hộ + tháng (tuỳ chọn thêm theo ngày) do người vận hành chỉ định. |
| **Input** | Chỉ đọc DB, **không gọi API ngoài, không tự đọc CSV** (CSV Xzilla đã được `RcvHalfHourElectricPowerCommand` nạp vào DB từ trước): `t_101`（danh sách hộ, dùng 5 thuộc tính nhóm）＋ `emn_confirm_electric_powers`（dữ liệu điện mua đã xác nhận, theo từng 30 phút／ngày）. Tham số dòng lệnh: `--emssp`（bắt buộc, nhiều hộ cách nhau bằng dấu phẩy）, `--yearmonth`（bắt buộc）, `--day`（tuỳ chọn）. |
| **Output** | **Chỉ ghi DB** — với mỗi hộ, mỗi ngày có dữ liệu trả về, ghi 1 bản ghi (UPSERT: theo khóa chính, đã có thì UPDATE, chưa có thì INSERT) vào `s_103`（entity `ConSensorDailyValue`, qua thư viện chung `EminelSvLib`）: set `device_type = BUY_ELECTRIC(11)`, 1 cột-ngày tương ứng (`c011`〜`c041`) + 5 cột thuộc tính nhóm. Không gửi mail, không xuất CSV. |
| **Khái quát xử lý** | 1. Đọc tham số `--emssp` / `--yearmonth` / `--day`, validate định dạng, tách danh sách hộ.<br>2. Với mỗi hộ: query `emn_confirm_electric_powers` nối `t_101`, lấy dữ liệu điện mua đã xác nhận — theo cả tháng (nếu không truyền `--day`) hoặc đúng 1 ngày (nếu có `--day`).<br>3. Với mỗi dòng-ngày trả về: cộng dồn 48 giá trị nửa-giờ trong ngày thành 1 tổng ngày.<br>4. Với mỗi ngày: tạo bản ghi mới, set cột-ngày = tổng vừa tính + 5 thuộc tính nhóm lấy từ `t_101`, lưu vào `s_103`.<br>5. Toàn bộ xử lý của 1 hộ nằm trong 1 transaction riêng; lỗi ở bất kỳ bước nào của hộ đó → rollback transaction của hộ đó và dừng hẳn command (`abort()`), không xử lý tiếp các hộ còn lại trong danh sách. |

## Phần 2 — Chi tiết

### 2.1 Tham số khởi động & kiểm tra hợp lệ

| Tham số | Bắt buộc | Định dạng | Ghi chú |
|---|---|---|---|
| `--emssp` | Có | Danh sách mã hộ, cách nhau bằng dấu phẩy, mỗi mã phải là số | Nếu rỗng hoặc có phần tử không phải số → `checkValidate` trả `false` |
| `--yearmonth` | Có | `YYYY-MM` | Nếu rỗng hoặc sai định dạng → `false` |
| `--day` | Không | `DD` (kết hợp với `--yearmonth` thành `YYYY-MM-DD` hợp lệ theo lịch) | Nếu có truyền mà ngày không tồn tại trong tháng (`checkdate`) → `false` |

Nguồn: `CalcFixedValueCommand.php:48-55` (`buildOptionParser`), `:289-345` (`checkValidate`).

Nếu `checkValidate` trả `false`, `execute()` gọi `$io->abort('failed checkValidate')` ngay từ đầu, không xử lý hộ nào (`CalcFixedValueCommand.php:74-78`).

Khi hợp lệ: `$this->emssps` = mảng mã hộ tách từ `--emssp`; `$this->yearmonth` = `YYYY` + `MM` nối liền (bỏ dấu `-`); nếu có `--day`, `$this->day` = giá trị ngày truyền vào (`CalcFixedValueCommand.php:296-341`).

### 2.2 Vòng lặp theo hộ & transaction

```
foreach (emssps as emssp):
    lấy dữ liệu điện mua xác nhận cho emssp (2.3)
    nếu lấy dữ liệu lỗi → resultCode=false, KHÔNG mở transaction
    nếu lấy dữ liệu OK:
        begin transaction
        ghi từng ngày vào s_103 (2.4/2.5)
        nếu ghi OK toàn bộ → commit
        nếu ghi lỗi ở bất kỳ ngày nào → rollback
    nếu resultCode=false → abort() toàn bộ command ngay tại hộ này
```
Nguồn: `CalcFixedValueCommand.php:81-87` (`execute`), `:98-122` (`recalculation`).

Mỗi hộ có transaction riêng (không phải 1 transaction chung cho cả danh sách `--emssp`). Khi 1 hộ thất bại, `abort()` dừng ngay command — các hộ đứng sau trong danh sách chưa được xử lý sẽ bị bỏ qua, nhưng các hộ đã xử lý và commit thành công trước đó vẫn giữ nguyên kết quả đã ghi.

### 2.3 Câu SQL lấy dữ liệu điện mua đã xác nhận

Có 2 nhánh, chọn theo việc có truyền `--day` hay không — cùng cấu trúc, chỉ khác điều kiện lọc ngày:

```sql
SELECT
    customer.c001 as "c001", customer.c012 as "c012", customer.c015 as "c015",
    customer.c016 as "c016", customer.c024 as "c024", customer.c042 as "c042",
    confirm.ymd as "ymd",
    COALESCE(confirm.kwh_0000_0030, 0) + COALESCE(confirm.kwh_0030_0100, 0) + ... (48 cột nửa-giờ, 00:00〜24:00)
        AS total
FROM emn_confirm_electric_powers AS confirm
    INNER JOIN t_101 AS customer
        ON confirm.spl_pw_spt_srno = customer.c001 AND customer.c052 IS NULL
WHERE (
    confirm.spl_pw_spt_srno = :emssp AND
    confirm.lct_ctgr = '1' AND
    -- nhánh không có --day:
    confirm.ymd >= :fromdate AND confirm.ymd < :todate    -- fromdate = yearmonth+"01", todate = fromdate + 1 tháng
    -- nhánh có --day:
    -- confirm.ymd = :date                                -- date = yearmonth + day
);
```
Nguồn: `CalcFixedValueCommand.php:182-212`（nhánh tháng）, `:231-260`（nhánh ngày）.

**Ý nghĩa các cột dùng trong câu SQL:**

| Bảng | Cột | Ý nghĩa | Ghi chú |
|---|---|---|---|
| `t_101` | `c001` | Mã hộ（EMS-SP） | Khóa nối |
| `t_101` | `c052` | Thời điểm xóa logic | `IS NULL` = hộ còn hiệu lực |
| `t_101` | `c012` | 建物区分（loại nhà: chung cư(1)/nhà riêng(2)） | → `GroupAttr1` |
| `t_101` | `c042` | 暖房熱源（nguồn nhiệt sưởi: 13A(1)/LPG(2)/điện(3)/dầu hỏa(4)/khác(9)） | → `GroupAttr2` |
| `t_101` | `c015` | 延床面積（diện tích sàn, 6 mức） | → `GroupAttr3` |
| `t_101` | `c016` | 家族人数（số người trong hộ, 1〜6） | → `GroupAttr4` |
| `t_101` | `c024` | ガスコージェネレーション（loại cogeneration: コレモ(1)/エネファーム(2)/khác(9)/không có(10)） | → `GroupAttr5` |
| `emn_confirm_electric_powers` | `spl_pw_spt_srno` | Mã hộ（EMS-SP） | Khóa nối, comment: "EMS-SP" |
| `emn_confirm_electric_powers` | `lct_ctgr` | 供給_受電区分 | Lọc `= '1'` |
| `emn_confirm_electric_powers` | `ymd` | Năm-tháng-ngày（chuỗi 8 ký tự） | Lọc theo khoảng tháng hoặc đúng 1 ngày |
| `emn_confirm_electric_powers` | `kwh_0000_0030`〜`kwh_2330_2400` | 48 cột kWh theo từng khung 30 phút trong ngày | ⭐ Giá trị tính toán chính |

Nguồn comment cột: `sources/eminelsv-develop/config/Migrations/20240410003631_CreateElectricPowerConfirm.php` (comment bảng: "EMN_30分電力量確定値出力情報取り込みデータ"), `20230807080522_InitialMigration.php` (comment cột `t_101`).

Nếu không có dòng dữ liệu nào trả về (hộ không có dữ liệu điện xác nhận cho tháng/ngày đó), bước ghi (2.4) không chạy lần nào cho hộ đó — không ghi gì vào `s_103`, hàm vẫn coi là xử lý thành công (không tính là lỗi).

### 2.4 Công thức tính tổng ngày

Với mỗi dòng-ngày trả về từ câu SQL trên:

```
total(ngày) = Σ (48 cột kwh_HHMM_HHMM trong ngày đó), COALESCE null → 0
```
Việc cộng dồn thực hiện ngay trong câu SQL (`COALESCE(..., 0) + COALESCE(..., 0) + ...`), không tính ở tầng code PHP. Nguồn: `CalcFixedValueCommand.php:186-202` (nhánh tháng), `:236-251` (nhánh ngày).

### 2.5 Ghi kết quả — bảng đích `s_103`

- Entity: `ConSensorDailyValue` (thư viện chung `EminelSvLib`, tên bảng vật lý `s_103`, tên gọi trong code "月毎センサ情報" = thông tin cảm biến theo tháng). Khóa chính: `(c001, c002, c003, c004)` = (mã hộ, loại thiết bị, vị trí, năm-tháng — luôn là ngày 01 của tháng).
- Với mỗi dòng-ngày trong kết quả SQL: tạo **entity mới**, set:

| Trường entity | Giá trị set | Nguồn |
|---|---|---|
| `c001`（EmsSp） | `rowData['c001']` | `:139` |
| `c002`（DeviceType） | `BUY_ELECTRIC`（hằng số = `11`） | `:140` |
| `c003`（RoomId） | `0` | `:141` |
| `c004`（Datetime） | Ngày 01 của tháng chứa `rowData['ymd']` | `:133-134,142` |
| `c009`（NeedAggCompleteFlag） | `2` | `:143` |
| `c111`〜`c115`（GroupAttr1〜5） | `c012, c042, c015, c016, c024` của hộ (thứ tự tương ứng: 建物区分, 暖房熱源, 延床面積, 家族人数, ガスコージェネレーション) | `:144-148` |
| Cột ngày tương ứng（`c011`〜`c041`, = `c0` + (ngày+10)） | `rowData['total']`（tổng đã tính ở 2.4） | `:135,149` |
| `c051`（Modified） | Thời điểm hiện tại | `:150` |
- Gọi `save()` — CakePHP (4.4) với entity mới có đủ 4 cột khóa chính sẽ tự kiểm tra tồn tại theo PK (`checkExisting` mặc định) rồi UPDATE cột-ngày tương ứng nếu bản ghi (hộ, 11, 0, tháng) đã tồn tại, ngược lại INSERT — tức **UPSERT**, cùng pattern được docblock hệ cũ gọi là 「INSERT(UPSERT)」 (`CalcMonthlyAccumulatedValueCommand.php:638`). Code Command không tự đọc bản ghi cũ; việc kiểm tồn tại do ORM thực hiện.
- Nếu `save()` ném exception ở bất kỳ dòng-ngày nào: log lỗi kèm EMS-SP + ngày, trả `false` ngay tại đó — các dòng-ngày còn lại trong cùng lần gọi (nếu xử lý cả tháng) không được ghi tiếp.

Nguồn: `CalcFixedValueCommand.php:130-165` (`updatePurchasedElectricityData`), entity `sources/eminel_sv_lib-develop/src/Model/Entity/ConSensorDailyValue.php`, table `sources/eminel_sv_lib-develop/src/Model/Table/ConSensorDailyValuesTable.php`.

### 2.6 Hằng số & nguồn dữ liệu liên quan

| Hằng số / bảng | Giá trị / vai trò | Nguồn |
|---|---|---|
| `BUY_ELECTRIC` | `11` — mã loại thiết bị ghi vào `s_103.c002` | `const.php:192` |
| `emn_confirm_electric_powers` | "EMN_30分電力量確定値出力情報取り込みデータ" — dữ liệu điện 30 phút đã **xác nhận/chốt (確定)**, nạp từ Xzilla | `20240410003631_CreateElectricPowerConfirm.php:75` |
| `emn_fast_electric_powers` | "EMN_30分電力量速報値出力情報取り込みデータ" — dữ liệu điện 30 phút **sơ bộ/nhanh (速報)**, cùng nguồn Xzilla, bảng riêng, batch này không đọc bảng này | `20240410002142_CreateElectricPowerFast.php:75` |
| Batch nạp dữ liệu Xzilla vào 2 bảng trên | `RcvHalfHourElectricPowerCommand` — tải CSV từ máy chủ trung gian Xzilla rồi insert vào `emn_confirm_electric_powers`/`emn_fast_electric_powers`/`emn_all_electric_powers` | `sources/conciergesv-develop/src/Command/RcvHalfHourElectricPowerCommand.php` |
| Lịch chạy (cron) | Không có — không tìm thấy `CalcFixedValueCommand` trong danh sách cron (`mng-webap_cron設定_20241029.txt`, `webap_cron設定_20240905.txt`, `cron設定一覧.xlsx`) | — |
