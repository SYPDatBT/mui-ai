# Batch cũ — ControlDrOperationCommand（DR 指令制御）

## Tóm tắt

`ControlDrOperationCommand` chạy **mỗi phút** (cron `* * * * *`), là nơi thực thi thật các lệnh **DR (Demand Response)** đã được đặt lịch trước — gửi chỉ thị ECHONET Lite tới **đơn vị điều khiển sưởi (Eco Jozu, `device_id=1001`)** qua bảng `Instructions` (bảng dùng chung với `hemssv`, nơi thực sự đẩy lệnh xuống GW), rồi cập nhật trạng thái và thông báo cho app. Mỗi lệnh DR có **2 "phase" độc lập** (mỗi phase tự có loại lệnh, thời gian, nhiệt độ, trạng thái riêng) — dùng để mô hình hoá cả 2 kiểu chỉ thị nêu trong yêu cầu E-GW: *"server gửi lệnh cả lúc bắt đầu và lúc kết thúc"* (ON/OFF) và *"server gửi lệnh lúc bắt đầu kèm sẵn thời điểm kết thúc"* (đổi nhiệt độ — thiết bị tự khôi phục, không cần lệnh thứ 2). **Batch này chỉ điều khiển đúng 1 loại thiết bị (sưởi Eco Jozu)** — không phải toàn bộ phạm vi DR nêu trong yêu cầu (điều hòa, Koremo, pin lưu điện, Eco‑Cute); chi tiết ở Phần 2.

## Phần 1 — Tổng quát

| Mục | Nội dung |
|---|---|
| **Vai trò** | Gửi lệnh ECHONET Lite điều khiển thiết bị sưởi (ON/OFF hoặc đổi nhiệt độ) tới đúng thời điểm đã lên lịch trong `ConDrOperations`, theo dõi trạng thái, đóng lệnh quá hạn, thông báo app. |
| **Input** | `ConDrOperations` + `ConDrOperationDestinations` (lịch DR, theo từng EMS-SP, 2 phase) ＋ `HemsGws` (GW của hộ) ＋ `ConDevices` (thiết bị sưởi + thiết bị app của hộ) ＋ `ConDeviceStatuses` (nhiệt độ hiện tại, khi cần offset) ＋ `ConDeviceControls` (chống gửi trùng trong 5 phút). |
| **Output** | Insert `Instructions` (lệnh gửi tới GW qua `hemssv`) ＋ `ConDeviceControls` (lịch sử lệnh) ＋ cập nhật `status_1`/`status_2` của `ConDrOperationDestinations` ＋ `ConMessages`/`ConMessageDestinations` (thông báo "DR đã bắt đầu" cho app). |
| **Khái quát xử lý** | 1. Với mỗi phase (1 và 2): tìm destination đến hạn bắt đầu (`start_at_N <= now <= end_at_N`, `status_N=SCHEDULED`), gửi lệnh, cập nhật trạng thái, gom danh sách EMS-SP đã gửi thành công để thông báo app.<br>2. Với mỗi phase: tìm destination đã quá hạn kết thúc (`end_at_N < now`) mà vẫn `SCHEDULED`/`RUNNING`, đóng lại thành `FAILED`/`COMPLETE`. |

## Phần 2 — Chi tiết

### Bản đồ xử lý — chạy mỗi phút

```
execute():
  startOperations(now, phase=1)    → gửi lệnh phase 1 đến hạn                 §2.3
  startOperations(now, phase=2)    → gửi lệnh phase 2 đến hạn                 §2.3
  finishOperations(now, phase=1)   → đóng lệnh phase 1 quá hạn kết thúc       §2.7
  finishOperations(now, phase=2)   → đóng lệnh phase 2 quá hạn kết thúc       §2.7
```

| Bước | Nội dung | Chi tiết ở |
|---|---|---|
| — | Lịch chạy & tham số | §2.1 |
| — | Cấu trúc 1 lệnh DR — 2 phase độc lập | §2.2 |
| 1 | Tìm + gửi lệnh đến hạn (`startOperations`) | §2.3 |
| 1a | Chống gửi trùng trong 5 phút | §2.4 |
| 1b | Build & gửi chỉ thị ECHONET thật (`dispatchOperation`) | §2.5 |
| 1c | Thông báo app "DR đã bắt đầu" | §2.6 |
| 2 | Đóng lệnh quá hạn (`finishOperations`) | §2.7 |

---

### 2.1 Lịch chạy & tham số

| Mục | Nội dung |
|---|---|
| Lịch chạy | Cron `* * * * *` — mỗi phút ([mng-webap_cron設定_20241029.txt:77](e:/Projects/mui/legacy_eminel_docs-main/docs/02_詳細設計/10_バッチ処理/mng-webap_cron設定_20241029.txt#L77)) |
| Tham số `--send_time` | Cho phép ghi đè mốc thời gian xử lý — **đọc đúng cách** bằng `getOption('send_time')`, khớp với khai báo `addOption('send_time')` ([:66-75](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/ControlDrOperationCommand.php#L66-L75)) — khác 2 batch đã gặp trước (`DispatchPushMessagesCommand`, `DistributeMonthlyEcoPointsCommand`) nơi tham số tương tự bị khai sai kiểu và không hoạt động |
| `$allowDuplicateExec = true` | Override lock-file mặc định của `BaseCommand` ([:38](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/ControlDrOperationCommand.php#L38)) — hợp lý vì batch chạy mỗi phút, nếu 1 lượt chạy vượt quá 1 phút (DB chậm) thì lock-file sẽ làm **bỏ hẳn 1 phút xử lý** thay vì cho chạy chồng lấp |

### 2.2 Cấu trúc 1 lệnh DR — 2 phase độc lập

Mỗi `ConDrOperation` có 2 bộ field giống nhau, đánh số `_1`/`_2`, theo dõi trạng thái riêng trong `ConDrOperationDestination` (`status_1`, `status_2`):

| Field (theo phase) | Ý nghĩa |
|---|---|
| `operation_N` | `ON` / `OFF` / `CHANGE_TEMP` |
| `start_at_N` / `end_at_N` | Khung thời gian hiệu lực của phase này |
| `temp_N` | Nhiệt độ (chỉ dùng khi `operation_N=CHANGE_TEMP`) — có thể là giá trị tuyệt đối hoặc **offset** |
| `temp_origin_N` | `ZERO` (temp_N là giá trị tuyệt đối) hoặc `CURRENT` (temp_N là **độ lệch** so với nhiệt độ đang cài đặt tại thời điểm gửi lệnh) ([ConDrOperation.php:38-39](e:/Projects/mui/legacy_eminel_docs-main/sources/eminel_sv_lib-develop/src/Model/Entity/ConDrOperation.php#L38-L39)) |
| `status_N` | `SCHEDULED` → `RUNNING`/`COMPLETE` → hoặc `FAILED`/`CANCELED` ([ConDrOperationDestination.php:25-29](e:/Projects/mui/legacy_eminel_docs-main/sources/eminel_sv_lib-develop/src/Model/Entity/ConDrOperationDestination.php#L25-L29)) |

`operation_2`/`start_at_2`/... đều **nullable** — 1 lệnh DR có thể chỉ dùng phase 1. Cách dùng 2 phase khớp với 2 kiểu chỉ thị DR nêu trong yêu cầu E-GW (UC-05 01-3): **ON/OFF** cần phase 2 riêng làm lệnh "kết thúc" (gửi tường minh lúc hết hạn), còn **CHANGE_TEMP** nhúng sẵn thời điểm kết thúc ngay trong lệnh phase 1 (xem §2.5) nên thiết bị tự khôi phục, không cần phase 2.

### 2.3 Tìm & gửi lệnh đến hạn (`startOperations`)

Với mỗi phase, lấy các `ConDrOperationDestination` có `status_N=SCHEDULED` và đang trong khung `start_at_N <= now <= end_at_N` ([:84-97](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/ControlDrOperationCommand.php#L84-L97)). Với mỗi destination, gọi `dispatchOperation()` (§2.5); nếu gửi thành công ([:105-121](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/ControlDrOperationCommand.php#L105-L121)):

| Loại lệnh | Trạng thái mới |
|---|---|
| `ON` / `OFF` | `COMPLETE` ngay — coi như xong khi đã gửi |
| `CHANGE_TEMP` | `RUNNING` — chưa xong, chờ tới `finishOperations` khi `end_at_N` qua mới đóng thành `COMPLETE` |

Nếu `dispatchOperation()` trả `false` (bị chặn do trùng, thiếu GW/thiết bị, lỗi khác) → **giữ nguyên `SCHEDULED`**, không đánh dấu gì — lượt chạy phút sau sẽ tự thử lại vì destination vẫn khớp điều kiện, cho tới khi thành công hoặc `end_at_N` trôi qua (sẽ bị `finishOperations` đóng thành `FAILED`). Toàn bộ EMS-SP gửi thành công trong lượt này được gom lại để báo app (§2.6).

### 2.4 Chống gửi trùng — `checkConflicting`

Trước khi build lệnh mới, kiểm tra có `ConDeviceControl` nào của cùng EMS-SP + thiết bị sưởi (`device_id=1001`) được tạo **trong 5 phút gần nhất**, mà **chưa có kết quả trả về** (`result_received IS NULL`) và **chưa bị đánh dấu lỗi HEMS** (`send_result_kind IS NULL`) ([:130-139](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/ControlDrOperationCommand.php#L130-L139)) — nếu có, bỏ qua lượt này (destination giữ `SCHEDULED`, thử lại phút sau).

### 2.5 Build & gửi chỉ thị thật (`dispatchOperation`)

1. Lấy `gw_id` của hộ từ `HemsGws`; không có → bỏ qua ([:160-169](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/ControlDrOperationCommand.php#L160-L169)).
2. Lấy **2 thiết bị**: thiết bị sưởi (`device_id=1001`) và **1 thiết bị "app"** bất kỳ (`device_id` thuộc `0000-0009`) của hộ — thiếu 1 trong 2 → bỏ qua ([:171-198](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/ControlDrOperationCommand.php#L171-L198)).
3. Build nội dung lệnh ECHONET theo `operation_N` ([:223-271](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/ControlDrOperationCommand.php#L223-L271)):

| `operation` | EPC | Nội dung `edt` |
|---|---|---|
| `ON` | `80` | `30` |
| `OFF` | `80` | `31` |
| `CHANGE_TEMP` | `B0` | `31` + nhiệt độ (hex có dấu) + **thời điểm kết thúc** (`end_at_N`, định dạng nhúng trực tiếp vào `edt`) |

   Với `CHANGE_TEMP`, nếu `temp_origin_N=CURRENT`: đọc nhiệt độ cài đặt hiện tại từ `ConDeviceStatuses` (EPC `A1`, giải mã hex có dấu), rồi **cộng thêm** `temp_N` làm giá trị cuối — không có dữ liệu → bỏ qua ([:242-261](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/ControlDrOperationCommand.php#L242-L261)).
4. Lưu `ConDeviceControls` (lịch sử, dùng cho chống trùng §2.4) + `Instructions` (hàng đợi lệnh thật, `instruction_type=1`="宅外制御指示", dùng chung với `hemssv` để đẩy xuống GW) trong 1 transaction ([:283-294](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/ControlDrOperationCommand.php#L283-L294)).

> ⚠️ **Chỉ thị phải "giả làm app"**: comment gốc trong code ghi rõ *"ユーザのアプリ端末からの操作のように見せかけないとゲートウェイが指令を無視する"* (không giả làm thao tác từ thiết bị app của user thì GW sẽ bỏ qua lệnh) — vì vậy lệnh ECHONET dùng `nid` = node ID của **thiết bị app**, không phải node ID của server/DR ([:172-190, :226](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/ControlDrOperationCommand.php#L172-L226)) — 1 workaround phần cứng GW, không phải thiết kế chủ ý ở tầng nghiệp vụ.

### 2.6 Thông báo app — "DR đã bắt đầu"

Sau khi gửi xong cho ≥1 EMS-SP trong phase, tạo 1 `ConMessage` từ `ConRegularMessages` **id cố định = 8** (`category=DR`, nội dung *"DR を開始しました。"* — "DR đã bắt đầu", [ConRegularMessagesSeed.php:115-128](e:/Projects/mui/legacy_eminel_docs-main/sources/eminelsv-develop/config/Seeds/ConRegularMessagesSeed.php#L115-L128)), gửi tới toàn bộ EMS-SP vừa gửi lệnh thành công trong lượt này ([:303-325](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/ControlDrOperationCommand.php#L303-L325)) — dùng hệ thống `ConMessages`/`ConMessageDestinations`, khác với `ConEcoMissions` (dùng cho lời khuyên tiết kiệm năng lượng) nhưng cùng mô hình "1 bản ghi nội dung + n đích".

### 2.7 Đóng lệnh quá hạn (`finishOperations`)

Với mỗi phase, tìm destination có `end_at_N < now` mà vẫn `SCHEDULED` hoặc `RUNNING` ([:332-347](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/ControlDrOperationCommand.php#L332-L347)):

| Trạng thái trước | Trạng thái sau | Ý nghĩa |
|---|---|---|
| `SCHEDULED` | `FAILED` | Hết hạn mà **chưa từng gửi được** lệnh (do conflict/thiếu thiết bị/lỗi liên tục) |
| `RUNNING` | `COMPLETE` | Đã gửi lệnh `CHANGE_TEMP` thành công, giờ tới hạn kết thúc → coi như hoàn tất (thiết bị tự khôi phục nhiệt độ theo thời điểm đã nhúng ở §2.5, batch không cần gửi thêm lệnh nào) |

---

## Nguồn

| Nội dung | Căn cứ |
|---|---|
| Logic chính của batch | `sources/conciergesv-develop/src/Command/ControlDrOperationCommand.php` |
| Lịch cron (mỗi phút) | `docs/02_詳細設計/10_バッチ処理/mng-webap_cron設定_20241029.txt:77` |
| Cấu trúc lệnh DR 2-phase | `sources/eminel_sv_lib-develop/src/Model/Entity/ConDrOperation.php`, `src/Model/Entity/ConDrOperationDestination.php`, `src/Model/Table/ConDrOperationsTable.php` |
| Lịch sử điều khiển thiết bị (chống trùng) | `sources/eminel_sv_lib-develop/src/Model/Entity/ConDeviceControl.php` |
| Nội dung thông báo "DR đã bắt đầu" | `sources/eminelsv-develop/config/Seeds/ConRegularMessagesSeed.php` |
| Bảng hàng đợi lệnh dùng chung với GW | `sources/eminel_sv_lib-develop/src/Model/Table/InstructionsTable.php`, `sources/hemssv-develop/src/Model/Table/InstructionsTable.php` |
| Yêu cầu tương ứng ở E-GW | `eminel_gw_project-main/docs/eminel/3_requirements/00_integrated_requirements_v1.2.md` — `[F-ES-07/08] 機器制御DR`, UC-05 01-3 |
