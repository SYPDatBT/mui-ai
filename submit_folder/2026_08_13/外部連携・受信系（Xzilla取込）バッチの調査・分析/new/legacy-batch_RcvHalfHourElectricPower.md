# Batch cũ — RcvHalfHourElectricPowerCommand（Xzilla 30分電力量データ受信・買電売電時間値算出）

## Tóm tắt

`RcvHalfHourElectricPowerCommand` (lệnh CLI `RcvHalfHourElectricPower`, IF1156) là batch trong hệ thống cũ (EMINEL コンシェルジュサーバー) nhận **dữ liệu điện lượng 30 phút** (48 khung/ngày cho mỗi điểm đo) từ Xzilla, xoá‑nạp lại vào bảng staging, tách theo cờ xác định (`fixed_div`) thành **sơ bộ (fast)** và **đã xác định (confirm)**, rồi từ phần sơ bộ **cộng từng cặp khung 30 phút thành 24 giá trị theo giờ** và tính ra **lượng mua điện／bán điện của từng khách hàng**, ghi vào `ConSensorHourlyValues` (`s_102`) — dữ liệu trực tiếp nuôi biểu đồ điện năng trên app. Khác với 2 batch nhận Xzilla đã điều tra trước (`RcvCntctCancellationCommand`, `RcvEmsPlsCntrPayerCommand` — chỉ cập nhật master/cờ), batch này **sinh ra số liệu hiển thị cho người dùng cuối** và có thể xử lý **nhiều file CSV trong 1 lần chạy**; chi tiết ở Phần 2.

## Phần 1 — Tổng quát

| Mục | Nội dung |
|---|---|
| **Vai trò** | Nhận CSV điện lượng 30 phút (IF1156) từ Xzilla, tách sơ bộ/xác định, tính lượng mua điện／bán điện theo giờ cho từng khách hàng. |
| **Input** | CSV trên server trung gian Xzilla (env `XZILLA_RELATION_SERVER_ELECTRIC_POWER_URL`) ＋ bảng `XzillaRelationLogs`（chống trùng）＋ `emn_all_electric_powers`／`emn_fast_electric_powers`（dữ liệu vừa nạp, đọc lại ngay trong cùng lần chạy）＋ `ConCustomers` (`t_101`) để lấy cờ dừng tính, cờ pin mặt trời/cogeneration, thông tin phân nhóm. |
| **Output** | Xoá‑nạp lại `emn_all_electric_powers` ＋ `emn_fast_electric_powers`; **append** (không xoá) vào `emn_confirm_electric_powers`; insert vào `ConSensorHourlyValues` (`s_102`, `device_type` 10=売電/bán điện, 11=買電/mua điện) ＋ ghi log `XzillaRelationLogs`. |
| **Khái quát xử lý** | 1. Lấy **toàn bộ** file CSV hôm nay (không chỉ file mới nhất); bỏ file đã xử lý qua log.<br>2. Với mỗi file: tải, xoá‑nạp lại bảng tổng, tách sơ bộ/xác định.<br>3. Tính lượng mua điện cho mọi khách hàng có dữ liệu.<br>4. Tính lượng bán điện — chỉ với khách hàng không có pin mặt trời (GW tự tính riêng) và có cấu hình cogeneration liên kết Xzilla. |

## Phần 2 — Chi tiết

### Bản đồ xử lý — 1 transaction, lặp theo từng file CSV của hôm nay

```
BƯỚC 1  Lấy danh sách file    → đọc dir trung gian, lọc .csv                          §2.1
BƯỚC 2  Chọn file hôm nay     → GIỮ TẤT CẢ file có timestamp hôm nay (không chỉ 1)     §2.1
BƯỚC 3  Chống xử lý trùng     → bỏ file nào log (upload_type=1) đang xử lý/đã xong     §2.2
BƯỚC 4  Với mỗi file còn lại:
        4a. Tải & ghi log "đang xử lý"                                                §2.3
        4b. Xoá + nạp lại emn_all_electric_powers (48 khung 30 phút/ngày)              §2.4
        4c. Xoá + nạp lại emn_fast_electric_powers  = dòng fixed_div rỗng             §2.5
        4d. APPEND emn_confirm_electric_powers = dòng fixed_div='1' (KHÔNG xoá)       §2.5
        4e. Cộng cặp khung 30 phút → 24 giá trị giờ, tính mua điện (device_type 11)    §2.6-2.7
        4f. Tính bán điện (device_type 10) — có điều kiện                             §2.6-2.7
        4g. Ghi log "hoàn tất" cho file này                                           §2.3
```

| Bước | Nội dung | Chi tiết ở |
|---|---|---|
| 1–3 | Xác định các file CSV hôm nay, chống xử lý trùng theo từng file | §2.1 · §2.2 |
| 4a | Tải file, ghi log "đang xử lý" | §2.3 |
| 4b–4d | Nạp dữ liệu 30 phút, tách sơ bộ／xác định | §2.4 · §2.5 |
| 4e–4f | Cộng khung giờ, tính mua/bán điện — **2 điều kiện nguồn** | §2.6 · §2.7 |
| — | Cấu trúc bản ghi ghi ra `ConSensorHourlyValues` | §2.8 |

---

### 2.1 Chọn file CSV cần xử lý — khác biệt so với 2 batch Xzilla khác

| Mục | Nội dung |
|---|---|
| Điều kiện lọc file | Chỉ nhận file `.csv`, khoá timestamp 14 ký tự cuối tên file ([:90-100](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvHalfHourElectricPowerCommand.php#L90-L100)) |
| Cách chọn file | **Giữ toàn bộ** file có timestamp trong khung hôm nay (không dừng ở file đầu tiên như `RcvCntctCancellationCommand`/`RcvEmsPlsCntrPayerCommand`) — `$todayFileNames[]` không `break` ([:107-115](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvHalfHourElectricPowerCommand.php#L107-L115)) |
| Không có file | Không có file nào hôm nay → `commit` + `abort` ([:117-122](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvHalfHourElectricPowerCommand.php#L117-L122)) |

Lý do hợp lý: cron cũ poll batch này 10 phút/lượt (`mng-webap_cron設定_20241029.txt:109-110`) nên mỗi ngày có thể có nhiều file; nhịp và format cấp thực tế từ Xzilla là điểm treo QA A-3 của báo cáo di trú, chưa chốt — vì vậy 1 lần chạy batch cần bù hết các file mới chưa xử lý, không chỉ 1 file.

### 2.2 Chống xử lý trùng — theo từng file riêng biệt

Khác 2 batch kia (tra log 1 lần cho 1 file), batch này **tra log cho từng file** trong danh sách hôm nay, giữ lại file nào chưa có log hoặc log không phải "đang xử lý"/"hoàn tất" (`upload_type=1`) ([:124-153](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvHalfHourElectricPowerCommand.php#L124-L153)). Không còn file nào sau khi lọc → `commit` + `abort` ([:155-160](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvHalfHourElectricPowerCommand.php#L155-L160)).

### 2.3 Tải file & ghi log — lặp lại cho mỗi file

Với mỗi file còn lại: tải về `/var/data/xzilla/IF1156/`, ghi log "đang xử lý" (`upload_type=1`), và sau khi xử lý xong file đó thì ghi log "hoàn tất" ngay — **không đợi hết tất cả file mới ghi log** ([:163-260](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvHalfHourElectricPowerCommand.php#L163-L260)). Riêng lỗi **tải file** → `commit` + `abort`, kết quả các file đã xử lý xong trước đó trong cùng lần chạy được giữ lại ([:169-176](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvHalfHourElectricPowerCommand.php#L169-L176)); lỗi từ bước ghi log "đang xử lý"/xoá‑nạp/tính trở đi → `rollback` **toàn bộ transaction**, kể cả các file đã xử lý xong trước đó (vì `$connection->begin()` chỉ gọi 1 lần ở đầu `execute()`).

### 2.4 Nạp dữ liệu 30 phút (`bulkInsert30MinElectricPowerAll`)

Xoá toàn bộ `emn_all_electric_powers` ([:189-199](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvHalfHourElectricPowerCommand.php#L189-L199)), đọc CSV bằng `explode("\n"/",")` (không dùng `fgetcsv`), map 55 cột (index 0-54) ([:273-351](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvHalfHourElectricPowerCommand.php#L273-L351)):

| Cột | Field | Ý nghĩa (theo comment migration) |
|---|---|---|
| `0` | `spl_pw_spt_srno` | EMS‑SP — khoá join thẳng sang `ConCustomers.c001`, không qua bảng ánh xạ |
| `1` | `lct_ctgr` | 供給_受電区分 — comment migration chỉ có tên cột; giá trị `1`=買電 (khách mua điện), `2`=売電 (khách bán điện) theo điều kiện `WHERE` của `calcKaidenBaidenAmount` ([:852-858](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvHalfHourElectricPowerCommand.php#L852-L858)) |
| `2` | `ymd` | Năm‑tháng‑ngày |
| `3` | `splsptidntno` | 供給地点特定番号 |
| `4` | `pw_spt_srno` | 受電地点特定番号 |
| `5`‑`52` | `kwh_0000_0030`…`kwh_2330_2400` | 48 khung 30 phút trong ngày |
| `53` | `fixed_div` | 確定区分 — rỗng/NULL = sơ bộ, `1` = đã xác định |
| `54` | `dwh_updatetime` | Thời điểm cập nhật ở DWH nguồn |

Bulk insert theo lô — **cùng lỗi off‑by‑one đã gặp ở `RcvEmsPlsCntrPayerCommand`**: `$query->values()` chạy trước khi kiểm tra `$splitCount==10`, nên mỗi lô thực chất **11 bản ghi**, không phải 10 như comment ([:412-435](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvHalfHourElectricPowerCommand.php#L412-L435)).

### 2.5 Tách sơ bộ／xác định — 1 bảng KHÔNG bị xoá

| Bảng | Hành vi mỗi lần chạy | Điều kiện lấy dữ liệu |
|---|---|---|
| `emn_fast_electric_powers` | **Xoá toàn bộ rồi nạp lại** ([:210-220](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvHalfHourElectricPowerCommand.php#L210-L220)) | `fixed_div IS NULL OR fixed_div = ''` — dữ liệu sơ bộ ([:452, :570](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvHalfHourElectricPowerCommand.php#L570)) |
| `emn_confirm_electric_powers` | **Không xoá — chỉ APPEND** mỗi lần chạy | `fixed_div = '1'` — dữ liệu đã xác định ([:594, :712](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvHalfHourElectricPowerCommand.php#L594-L712)) |

Cả 2 đều insert bằng `INSERT INTO ... SELECT ... FROM emn_all_electric_powers` (1 câu SQL, không lặp dòng).

### 2.6 Cộng khung 30 phút → giá trị theo giờ

Trong `calcKaidenBaidenAmount`, mỗi cặp khung 30 phút liền kề được cộng thành 1 khung giờ ngay trong câu SELECT, nếu 1 trong 2 khung là NULL thì kết quả là NULL (không tính) ([:776-848](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvHalfHourElectricPowerCommand.php#L776-L848)):

```text
kwh_HHOO_HH+1_OO = kwh_HH00_HH30 + kwh_HH30_HH+1_00
(NULL nếu 1 trong 2 khung NULL)
```

Nguồn luôn lấy từ **`emn_fast_electric_powers`** (sơ bộ) — dữ liệu `emn_confirm_electric_powers` (đã xác định) được lưu ở §2.5 nhưng **không dùng lại** ở bước tính này.

### 2.7 Điều kiện tính mua điện／bán điện

Join `emn_fast_electric_powers` với `ConCustomers` theo `spl_pw_spt_srno = c001`, chỉ lấy khách hàng **chưa xoá** (`c052 IS NULL`) và **chưa bị dừng tính** (`c065 = 0` — cờ mà `RcvEmsPlsCntrPayerCommand`/`RcvCntctCancellationCommand` set khi hợp đồng kết thúc) ([:849-860](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvHalfHourElectricPowerCommand.php#L849-L860)).

2 điều kiện quyết định nguồn tính **bán điện** ([:876-882](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvHalfHourElectricPowerCommand.php#L876-L882)):

| Điều kiện | Giá trị | Ý nghĩa |
|---|---|---|
| `calcFromGw` | `has_solar_cell (c034) == 1` | Khách có pin mặt trời → GW/HEMS đã tự đo, batch **ngày** khác tính bán điện, batch này bỏ qua |
| `calcFromXzilla` | `!has_solar_cell && gas_cogeneration (c024)==1 && juden_point_number (c064)` không rỗng | Khách có cogeneration/fuel‑cell (không pin mặt trời) → chỉ Xzilla mới có số liệu bán điện |

| Đang tính | Trường hợp | Hành vi |
|---|---|---|
| Mua điện (`11`) | Luôn tính, không điều kiện | Cộng khung giờ, ghi `device_type=11` |
| Mua điện (`11`) | **Đồng thời** không `calcFromGw` và không `calcFromXzilla` | Ghi **thêm** 1 bản ghi bán điện = `0` (`device_type=10`) — vì chắc chắn không nguồn nào khác tính ra được ([:891-963](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvHalfHourElectricPowerCommand.php#L891-L963)) |
| Bán điện (`10`) | `calcFromGw` | Bỏ qua hoàn toàn — không tính, không ghi gì (kể cả 0) ([:884-887](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvHalfHourElectricPowerCommand.php#L884-L887)) |
| Bán điện (`10`) | `calcFromXzilla` | Cộng khung giờ, ghi `device_type=10` |
| Bán điện (`10`) | Không `calcFromGw` và không `calcFromXzilla` | Không ghi gì — **khác** trường hợp mua điện, ở đây không có bước ghi `0` bù ([:1036-1039](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvHalfHourElectricPowerCommand.php#L1036-L1039)) |

### 2.8 Bản ghi ghi ra `ConSensorHourlyValues` (`s_102`)

| Cột | Hằng số entity | Nguồn giá trị |
|---|---|---|
| `c001` | `C_EMS_SP` | `spl_pw_spt_srno` |
| `c002` | `C_DEVICE_TYPE` | `11`=買電(mua điện) hoặc `10`=売電(bán điện) |
| `c003` | `C_ROOM_ID` | luôn `0` |
| `c004` | `C_DATE` | `ymd` |
| `c008`/`c009` | `C_NEED_ELE_COMPLETE_FLAG`/`C_NEED_AGG_COMPLETE_FLAG` | luôn `2` |
| `c111`‑`c115` | `C_GROUP_ATTR_1..5` | `c012`(建物種別)/`c042`(暖房熱源)/`c015`(床面積)/`c016`(家族人数)/`c024`(gas_cogeneration) của khách hàng |
| `c011`‑`c034` | `C_VALUE_0..23` | 24 giá trị giờ đã cộng ở §2.6, hoặc `'0'` (trường hợp bù ở §2.7) |
| `c041` | `C_MODIFIED` | thời điểm chạy batch |

Khoá chính của bảng là **`(c001, c002, c003, c004)`** ([ConSensorHourlyValuesTable.php:41-43](e:/Projects/mui/legacy_eminel_docs-main/sources/eminel_sv_lib-develop/src/Model/Table/ConSensorHourlyValuesTable.php#L41-L43)).

### ⚠️ Điểm cần chú ý của hệ cũ

**① Insert bằng entity mới, không upsert — có thể vi phạm khoá chính.** Mỗi bản ghi được tạo bằng `newEmptyEntity()` rồi `save()` ([:896, :969](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvHalfHourElectricPowerCommand.php#L969)) — không tra record cũ theo khoá chính trước. Nếu batch chạy 2 lần trong cùng ngày cho cùng `(ems_sp, device_type, room=0, date)` (hoàn toàn có thể xảy ra vì batch xử lý **nhiều file/ngày** — §2.1), lần ghi thứ 2 sẽ vi phạm khoá chính, bị bắt ở `catch` ([:1041-1044](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/RcvHalfHourElectricPowerCommand.php#L1041-L1044)) và làm `rollback` **toàn bộ transaction của lần chạy đó** — kể cả các file CSV khác đã xử lý xong trước đó trong cùng lần chạy (§2.3).

**② `emn_confirm_electric_powers` tích lũy vô hạn.** Đây là bảng duy nhất trong 3 bảng liên quan tới CSV không bị `deleteAll` mỗi lần chạy — trong khi `emn_all`/`emn_fast` luôn xoá‑nạp lại toàn bộ. Dữ liệu 確報 này được `CalcFixedValueCommand` (固定値計算 — 再集計 chạy tay) đọc lại ([CalcFixedValueCommand.php:203, :252](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/CalcFixedValueCommand.php#L203)) — tích lũy là chủ đích giữ lịch sử 確報 theo `ymd` nhưng không có purge, nên khi port cần kèm chính sách 保持期間/TTL.

**③ Bất đối xứng khi tính bán điện.** Khách hàng không đủ điều kiện tính bán điện: nếu đang ở lượt tính **mua điện** thì được ghi bù `0`; nếu đang ở lượt tính **bán điện** thì không ghi gì cả (§2.7) — cùng một tình huống nghiệp vụ nhưng 2 kết quả khác nhau tuỳ vào lượt gọi hàm nào bắt gặp trước.

---

## Nguồn

| Nội dung | Căn cứ |
|---|---|
| Logic chính của batch | `sources/conciergesv-develop/src/Command/RcvHalfHourElectricPowerCommand.php` |
| Cấu trúc + comment cột `emn_all_electric_powers` | `sources/eminelsv-develop/config/Migrations/20240409095924_CreateElectricPowerAll.php` |
| Cấu trúc bảng `emn_fast_electric_powers` / `emn_confirm_electric_powers` | `sources/eminelsv-develop/config/Migrations/20240410002142_CreateElectricPowerFast.php` / `20240410003631_CreateElectricPowerConfirm.php` |
| Bảng + hằng số cột `ConSensorHourlyValues` (`s_102`) | `sources/eminel_sv_lib-develop/src/Model/Table/ConSensorHourlyValuesTable.php`, `src/Model/Entity/ConSensorHourlyValue.php` |
| Tên cột + hằng số `ConCustomers` (`t_101`) | `sources/eminel_sv_lib-develop/src/Model/Entity/ConCustomer.php` |
| Batch liên quan (cờ `c065` dùng chung) | `investigate/eminel-gw/legacy-batch_RcvCntctCancellation.md`, `investigate/eminel-gw/legacy-batch_RcvEmsPlsCntrPayer.md` |
