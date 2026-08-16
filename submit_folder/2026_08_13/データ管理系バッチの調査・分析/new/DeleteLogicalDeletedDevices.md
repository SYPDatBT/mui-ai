# DeleteLogicalDeletedDevicesCommand（論理削除済みデバイス削除）

## Tóm tắt

`DeleteLogicalDeletedDevicesCommand` là **batch chạy cron hằng ngày 05:15** (chung wrapper shell với
`DeleteData`) trong `conciergesv` của hệ thống cũ, nhưng thao tác lên các bảng gốc thuộc domain HEMS
dùng chung cả 3 server (`Devices`/`DeviceDatas`/`ErrorDeviceDatas`/`Instructions`): tìm các thiết bị đã
bị **soft-delete** (`delete_flg=true` — do API `NotifyDeviceListController` ở `hemssv` đặt khi GW báo
thiết bị không còn tồn tại) và đã soft-delete quá 30 ngày, rồi **hard-delete** (xóa vật lý) toàn bộ dữ
liệu đo/lỗi/lệnh điều khiển liên quan + chính record thiết bị đó, trong 1 transaction. Đây là bước "dọn
dẹp thật" sau grace period 30 ngày của vòng đời gỡ thiết bị IoT. Ở repo mới `syp-eminelstandard-backend`,
đây là trường hợp **"thay bằng cơ chế khác về chất"** — cả 2 vế: (1) không có cờ soft-delete nào trên
bảng thiết bị (`DeviceTable`, `MuiDeviceTable`) tương đương `delete_flg`; khái niệm "gỡ thiết bị không
còn ở nguồn" tồn tại dưới dạng đồng bộ-xóa-NGAY — API danh sách thiết bị đối chiếu DB với server maker
(RINNAI/NORITZ/DAIKIN) và Delete ngay record không còn trong danh sách
(`get-list-remote-control-device.ts:199-222`); (2) xóa thiết bị ở hệ mới là hard-delete NGAY qua nhiều
luồng (user gọi API, sync danh sách, gỡ liên kết maker, batch định kỳ `batch-remove-integration-expired`
khi mất tư cách hội viên/hết hợp đồng gas), không qua soft-delete + grace period 30 ngày nào. Cái chưa
tồn tại ở kiến trúc mới chỉ là riêng khái niệm nghiệp vụ "soft-delete thiết bị khi GW báo mất, chờ 30
ngày rồi mới xóa hẳn" (grace period + batch dọn định kỳ theo từng thiết bị).

---

# Phần A — Hệ thống cũ

## A.1 Tổng quát

| Mục | Nội dung |
|---|---|
| **Tên batch** | Class: `DeleteLogicalDeletedDevicesCommand` (extends `Command` trực tiếp, không `BaseCommand`) · Tên lệnh gọi thực tế: `DeleteLogicalDeletedDevices` *(theo wrapper script production, `12_CreateCsvAndDeleteData_day1.sh:35`)* · **Cron hằng ngày 05:15** (`mng-webap_cron設定_20241029.txt:39-41` — cron gọi wrapper `12_CreateCsvAndDeleteData_day1.sh`/`day2to31.sh` trong `eminel-mng-webap.20240909.tgz`, bên trong wrapper gọi batch này ngay sau `DeleteData`; tên batch chỉ xuất hiện BÊN TRONG script nên grep trực tiếp 2 file cron `.txt` không thấy). |
| **Vai trò** | Dọn dẹp vật lý dữ liệu của thiết bị đã bị gỡ khỏi hộ gia đình (soft-delete từ lâu) — tránh tồn đọng vô hạn record "thiết bị ma" trong các bảng dùng chung giữa 3 server. |
| **Input** | Đọc bảng `Devices` — lọc `delete_flg=true` AND `update_datetime < (--datetime − 30 ngày)`. Tham số dòng lệnh `--datetime` (mặc định `now`). |
| **Output** | `DELETE` vật lý trên 4 bảng: `DeviceDatas`, `ErrorDeviceDatas`, `Instructions` (theo từng thiết bị), rồi `Devices` (record chính). Không ghi dữ liệu mới. |
| **Khái quát xử lý** | 1. Tính mốc `keepDays` = `--datetime` trừ 30 ngày.<br>2. Tìm toàn bộ thiết bị đã soft-delete trước mốc đó.<br>3. Mở 1 transaction DUY NHẤT cho toàn bộ danh sách.<br>4. Với mỗi thiết bị: xóa `DeviceDatas`, `ErrorDeviceDatas`, `Instructions` liên quan (theo `ems_sp_no`+`node_id`+`eoj`), rồi xóa chính record `Devices`.<br>5. Nếu xóa `Devices` cho 1 thiết bị thất bại → rollback TOÀN BỘ transaction (kể cả thiết bị đã xóa thành công trước đó trong cùng lượt) và dừng ngay; nếu không → commit sau khi xử lý hết danh sách. |

## A.2 Chi tiết

### A.2.1 Điều kiện lọc & nguồn phát sinh `delete_flg`

| Mục | Nội dung | Nguồn |
|---|---|---|
| Điều kiện lọc thiết bị cần xóa | `delete_flg = true` AND `update_datetime < (--datetime − 30 ngày)` | `DeleteLogicalDeletedDevicesCommand.php:64-71` |
| Định danh 1 thiết bị | Tổ hợp `ems_sp_no` (mã hộ/EMS-SP) + `node_id` + `eoj` (ECHONET Lite Object — mã loại thiết bị) | `Entity/Device.php:11-13` |
| Nguồn phát sinh `delete_flg=true` | API `NotifyDeviceListController` ở **hemssv** (không phải conciergesv) — khi GW báo cáo danh sách thiết bị hiện có, nếu 1 thiết bị đã lưu trong DB không còn xuất hiện trong danh sách GW báo → `Devices->updateAll(['delete_flg'=>true,'update_datetime'=>now], ...)`. `DeviceDatas` cũng được soft-delete tương tự (nhưng độc lập, có `delete_flg` riêng — batch này KHÔNG kiểm tra lại cờ này trên `DeviceDatas`, chỉ hard-delete thẳng theo khóa thiết bị). | `sources/hemssv-develop/src/Controller/NotifyDeviceListController.php:661-666,676-679` |
| Phạm vi dùng chung | Cả 4 bảng (`Devices`,`DeviceDatas`,`ErrorDeviceDatas`,`Instructions`) được đọc/ghi bởi 24 file code khác (25 file .php kể cả batch này, + 1 README) trên CẢ 3 server (`hemssv`,`eminelsv`,`conciergesv` + lib — đếm thật qua grep) — xác nhận đây là dữ liệu lõi domain HEMS dùng chung toàn hệ thống, không riêng gì `conciergesv`. | grep `EminelSvLib.(Devices\|DeviceDatas\|ErrorDeviceDatas\|Instructions)` trên `sources/` |

### A.2.2 Xóa liên đới theo từng thiết bị

Với mỗi thiết bị khớp điều kiện A.2.1 (lặp tuần tự, không batch/bulk):

1. `DeviceDatas->deleteAll(['ems_sp_no'=>..., 'node_id'=>..., 'eoj'=>...])` — xóa dữ liệu đo/trạng thái
   mới nhất của thiết bị (`latest_node_operating_state`, `latest_device_fault_content`,...).
   (`Entity/DeviceData.php:14-24`)
2. `ErrorDeviceDatas->deleteAll([cùng điều kiện])` — xóa lịch sử lỗi thiết bị.
3. `Instructions->deleteAll([cùng điều kiện])` — xóa lệnh điều khiển/polling đang chờ GW lấy về (nếu
   thiết bị đã gỡ, các lệnh cũ với nó không còn ý nghĩa). (`Entity/Instruction.php:11-19`)
4. `Devices->delete($device)` — xóa chính record thiết bị. Chỉ bước NÀY được kiểm tra kết quả
   (`if`/`else`); 3 bước xóa trước KHÔNG kiểm tra số dòng bị ảnh hưởng hay lỗi riêng.

Nguồn: `DeleteLogicalDeletedDevicesCommand.php:73-103`.

### A.2.3 Giao dịch & xử lý lỗi

- Toàn bộ danh sách thiết bị (có thể nhiều thiết bị/nhiều hộ khác nhau) chạy trong **1 transaction DUY
  NHẤT**, mở ở đầu hàm `deleteInstructions()`, commit ở cuối SAU KHI vòng lặp hoàn tất hết. (`:60-62,104`)
- Nếu `Devices->delete($device)` trả về `false` (xóa thất bại) ở BẤT KỲ thiết bị nào trong danh sách:
  log `alert`, `rollback()`, và `return` ngay — hủy TOÀN BỘ thay đổi trong transaction, **kể cả các
  thiết bị đã xóa thành công ở những vòng lặp TRƯỚC ĐÓ trong cùng lượt chạy này**. (`:96-102`)
- Không có try/catch bọc quanh các lệnh `deleteAll`/`delete` — nếu 1 trong 3 bước `deleteAll` (bước 1-3
  ở A.2.2) ném exception (ví dụ lỗi kết nối, ràng buộc khóa ngoại), exception đó KHÔNG bị bắt ở đây,
  sẽ ném ra ngoài `execute()` luôn — transaction không được `rollback()` một cách rõ ràng trong code
  (dù CakePHP/PostgreSQL có thể tự hủy transaction khi connection đóng đột ngột do exception, đây là
  hành vi framework/DB, không xác nhận trực tiếp được trong repo này).

### A.2.4 Điểm đặc biệt / Rủi ro

- **Batch chạy cron hằng ngày 05:15** — cùng nhóm `#12.DBデータ削除` với `DeleteDataCommand` (cùng
  wrapper). Cron không gọi thẳng batch mà gọi wrapper shell `12_CreateCsvAndDeleteData_day1.sh` (ngày
  mùng 1) / `day2to31.sh` (hằng ngày) — bên trong wrapper chạy lần lượt các batch CSV/xóa rồi tới batch
  này ngay sau `DeleteData` (`day1.sh:35`, `day2to31.sh:29`).
- **Rollback-toàn-bộ khi lỗi 1 thiết bị** (xem A.2.3) — nếu danh sách có N thiết bị và thiết bị thứ K bị
  lỗi xóa, N-1 thiết bị xóa thành công trước đó cũng bị hủy theo, phải chạy lại từ đầu cho toàn bộ danh
  sách ở lần chạy sau (không có cơ chế "xử lý xong bao nhiêu thì giữ bấy nhiêu", không phải theo từng
  thiết bị 1 transaction riêng).
- Không extends `BaseCommand` → không có cơ chế lock PID chống chạy trùng (giống nhận xét ở
  `DeleteData.md`) — wrapper có `flock -n` chống chạy trùng (`day1.sh:4-9`) nhưng chỉ theo TỪNG file
  script; ngày mùng 1 cả `day1` lẫn `day2to31` cùng đặt lịch 05:15 (cron `:40-41`) mà flock KHÔNG chống
  chéo giữa 2 file script khác nhau — 2 tiến trình có thể cùng chạy batch này trùng thời điểm.
- Xóa 3 bảng con TRƯỚC khi xóa `Devices` (không phải xóa `Devices` trước rồi cascade) — thứ tự này hợp
  lý về mặt tránh vi phạm ràng buộc khóa ngoại nếu có FK constraint từ 3 bảng con tới `Devices`, dù
  không thấy khai báo FK rõ ràng trong các Table class đã đọc.

---

# Phần B — Đối chiếu EMINEL-smart (hệ thống mới)

> Không có Lambda/cơ chế nào tương đương nguyên trạng (soft-delete + grace period 30 ngày); chức năng
> "gỡ thiết bị không còn ở nguồn" được thay bằng cơ chế khác về chất. Bảng dưới đây là các khu
> vực/candidate/luồng xóa đã tra và mức độ khớp (thay cho B.1/B.2).

## Đã kiểm tra

| Khu vực / candidate | Vì sao không khớp |
|---|---|
| `DeviceTable` (`template-dynamodb.yaml:525-548`, model `src/layers/common/nodejs/models/Device.ts`) | Không có field nào kiểu `is_deleted`/`delete_flag`/`deleted_at`. Field gần nhất về nghĩa là `error_flag` — cờ báo LỖI thiết bị, không phải cờ "đã gỡ khỏi nhà". |
| `MuiDeviceTable` (`template-dynamodb.yaml:1495-1511`, model `src/layers/common/nodejs/models/MuiDevice.ts`) | Cũng không có `delete_flg`/`deleted_at`. Có `availability` (khả dụng tức thời cho remote control hồng ngoại) — khác bản chất "đã bị GW báo gỡ vĩnh viễn". |
| Grep `NotifyDeviceList`/`delete_flg` trên toàn `src/` | 0 kết quả — không có API nào chỉ ĐÁNH DẤU soft-delete tương đương `NotifyDeviceListController`; việc phát hiện "thiết bị không còn ở nguồn" nằm ở luồng sync ngay dòng dưới (xóa ngay, không đánh dấu). |
| `src/functions/api-device/get-list-remote-control-device.ts:199-222` | Candidate gần nhất về BẢN CHẤT nghiệp vụ (trigger: sync): khi gọi API danh sách thiết bị, đối chiếu DB với danh sách server maker (RINNAI/NORITZ/DAIKIN), thiết bị không còn trong danh sách → `Delete` ngay record `DeviceTable`. Khác: xóa ngay không soft-delete, không grace period 30 ngày, chạy theo lượt gọi API chứ không phải batch định kỳ. |
| `src/functions/api-device/delete-sensor.ts:54-121` | 1 trong các luồng xóa do NGƯỜI DÙNG chủ động (trigger: user): xóa `MuiSensor` + `MuiDevice` con trong 1 transaction, hard-delete NGAY, không qua soft-delete + grace period; không xóa dữ liệu đo/lỗi/lệnh chờ tương đương `DeviceDatas`/`ErrorDeviceDatas`/`Instructions` (dữ liệu đo ở hệ mới dùng bảng khác đã có TTL sẵn — `DeviceMonthlyUsageHistoryTable`,... — không cần dọn thủ công theo thiết bị). |
| `src/functions/api-device/delete-infrared-remote.ts:40-56` | Luồng xóa remote hồng ngoại do user (trigger: user): hard-delete `MuiDevice` ngay rồi gọi `infraredRemoteService.removeConnectedDevice`, có rollback (Put lại) khi service ngoài lỗi. |
| Gỡ liên kết maker / reset account / import hội viên (`api-integration/get-access-token-integration.ts:292,317`, `batch-reset-account/app.ts:275-284`, `batch-if2241-import-tagtag-kaiin/app.ts:902-909`) | Các luồng xóa record `DeviceTable` theo sự kiện tài khoản/liên kết (trigger: hết liên kết / reset account / đổi hội viên) — hard-delete ngay, không theo vòng đời từng thiết bị. |
| `src/functions/batch-remove-integration-expired` (`app.ts:44-53,92` → `get-transaction-reset-integration.ts:145-176`) | Batch ĐỊNH KỲ có hard-delete record thiết bị + dữ liệu lỗi thiết bị (`TABLE_DEVICE`+`TABLE_DEVICE_ERROR` — tương ứng cặp `Devices`+`ErrorDeviceDatas` hệ cũ) khi user mất tư cách hội viên hoặc hết hợp đồng gas — tức xóa theo vòng đời hợp đồng/liên kết, không phải theo vòng đời từng thiết bị như batch cũ. |
| `TimeToLiveSpecification` trên `DeviceTable`/`MuiDeviceTable` | Không có — 2 bảng này không nằm trong khối TTL nào của `template-dynamodb.yaml` (khác các bảng lịch sử usage đã có TTL, xem `DeleteData.md`). |
| 81 thư mục `batch-*` trong `src/functions/` | Không có TÊN nào liên quan "delete-device"/"hard-delete"/"device-cleanup"/"purge-device"/"delete-logical" — nhưng soi theo NỘI DUNG thì `batch-remove-integration-expired` (dòng trên) có hard-delete record thiết bị. |

---

## Tổng kết

Không có ánh xạ 1-1 — bản cũ chỉ có 1 luồng xử lý đơn giản (không nhánh/thuật toán song song), và ở hệ
thống mới đây là trường hợp **"thay bằng cơ chế khác về chất"**: khái niệm "gỡ thiết bị không còn ở
nguồn" tồn tại dưới dạng đồng bộ-xóa-ngay khi gọi API danh sách (`get-list-remote-control-device`),
cộng các luồng xóa theo vòng đời hợp đồng/liên kết (`batch-remove-integration-expired`,...) — bảng "Đã
kiểm tra" ở Phần B đã nêu từng luồng và mức độ khớp. Đáng chú ý: cái chưa tồn tại ở kiến trúc mới không
phải việc xóa thiết bị, mà là chính sách vòng đời "soft-delete khi GW báo mất kết nối, giữ 30 ngày grace
period rồi mới xóa hẳn" — tương tự dạng gap đã ghi nhận ở `DeleteData.md` cho `ConEcoPoints` (có dữ liệu
nhưng thiếu chính sách vòng đời; ở đây việc xóa đều có nhưng là xóa NGAY, thiếu grace period).

---

## Nguồn

| Phần | Nội dung | Căn cứ |
|---|---|---|
| Hệ thống cũ | Logic chính | `sources/conciergesv-develop/src/Command/DeleteLogicalDeletedDevicesCommand.php` |
| Hệ thống cũ | Ý nghĩa cột `Device` | `sources/eminel_sv_lib-develop/src/Model/Entity/Device.php:11-24` |
| Hệ thống cũ | Ý nghĩa cột `DeviceData` | `sources/eminel_sv_lib-develop/src/Model/Entity/DeviceData.php:11-24` |
| Hệ thống cũ | Ý nghĩa cột `Instruction` | `sources/eminel_sv_lib-develop/src/Model/Entity/Instruction.php:11-19` |
| Hệ thống cũ | Nguồn phát sinh `delete_flg=true` (API khác server) | `sources/hemssv-develop/src/Controller/NotifyDeviceListController.php:661-666,676-679` |
| Hệ thống cũ | Phạm vi dùng chung 3 server (đếm thật) | grep `EminelSvLib.(Devices\|DeviceDatas\|ErrorDeviceDatas\|Instructions)` trên `sources/` — 25 file .php (kể cả batch này) + 1 README |
| Hệ thống cũ | Cron hằng ngày 05:15 (qua wrapper script) | `docs/02_詳細設計/10_バッチ処理/mng-webap_cron設定_20241029.txt:39-41` + `cron実行用シェルスクリプト/eminel-mng-webap.20240909.tgz` → `12_CreateCsvAndDeleteData_day1.sh:35`, `day2to31.sh:29` |
| Hệ thống cũ | Danh sách batch (mô tả tiếng Nhật, nhóm server) | `docs/03_API仕様/04_バッチ一覧.md:77` |
| Hệ thống mới | Bảng thiết bị (xác nhận không có cờ soft-delete) | `template-dynamodb.yaml:525-548` (`DeviceTable`), `src/layers/common/nodejs/models/Device.ts` |
| Hệ thống mới | Bảng thiết bị MUI (xác nhận không có cờ soft-delete) | `template-dynamodb.yaml:1495-1511` (`MuiDeviceTable`), `src/layers/common/nodejs/models/MuiDevice.ts` |
| Hệ thống mới | Các luồng xóa thiết bị (hard-delete ngay, không qua soft-delete) | `src/functions/api-device/get-list-remote-control-device.ts:199-222`, `delete-sensor.ts:54-121`, `delete-infrared-remote.ts:40-56`, `api-integration/get-access-token-integration.ts:292,317`, `batch-reset-account/app.ts:275-284`, `batch-remove-integration-expired/app.ts:44-53` |
| Hệ thống mới | Đối chứng bảng có TTL (để thấy `DeviceTable`/`MuiDeviceTable` không có) | `docs/legacy-batch-review/DeleteData.md` |
