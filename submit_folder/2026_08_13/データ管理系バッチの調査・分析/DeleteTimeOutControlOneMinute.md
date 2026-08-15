# DeleteTimeOutControlOneMinuteCommand（1分タイムアウト制御レコード削除）

## Tóm tắt

`DeleteTimeOutControlOneMinuteCommand` là batch cron chạy **mỗi phút** trên `conciergesv`: dọn các lệnh
"điều khiển thiết bị từ xa" (`instruction_type=1`, khi user yêu cầu bật/tắt thiết bị từ xa qua app) đã
nằm trong hàng đợi `Instructions` quá 4 phút mà GW (gateway tại nhà) chưa lấy/xử lý xong — đây là
safety-net cho mô hình **polling-based control**: bình thường lệnh tự bị xóa khi GW báo hoàn tất
(`InstructionController.php:548-563`), batch này chỉ dọn phần "lệnh chết" khi GW mất kết nối/không phản
hồi kịp, tránh hàng đợi phình to vô hạn. Ở repo mới `syp-eminelstandard-backend`, **không cần và không có cơ chế
tương đương** — không phải vì thiếu sót khi port, mà vì kiến trúc điều khiển thiết bị đã đổi hẳn về
chất: thay vì ghi lệnh vào hàng đợi cho GW polling lấy về, hệ thống mới gọi THẲNG API cloud của hãng
thiết bị (Rinnai/Noritz/Daikin) và chờ response ĐỒNG BỘ ngay trong cùng 1 lần chạy Lambda — không còn
khái niệm "lệnh đang chờ xử lý" tồn tại lâu dài trong DB, nên không có gì để timeout/dọn rác.

---

# Phần A — Hệ thống cũ

## A.1 Tổng quát

| Mục | Nội dung |
|---|---|
| **Tên batch** | Class: `DeleteTimeOutControlOneMinuteCommand` (extends `Command` trực tiếp) · Tên lệnh gọi: `delete_time_out_control_one_minute` *(suy đoán theo quy ước CakePHP 4)* · Script cron: `12_DeleteTimeOutControlOneMinute.sh` · Cùng nhóm cron "12.DBデータ削除" với `DeleteDataCommand`/`DeleteTimeOutControlTenMinuteCommand`. |
| **Vai trò** | Safety-net dọn lệnh điều khiển từ xa bị timeout khỏi hàng đợi `Instructions`, tránh tồn đọng lệnh chết do GW không phản hồi. |
| **Input** | Đọc bảng `Instructions` — lọc `instruction_type = 1` AND `instruction_date < (--datetime − 4 phút)`. Tham số `--datetime` (mặc định `now`). |
| **Output** | `DELETE` từng dòng khớp điều kiện, trong 1 transaction. Không ghi dữ liệu mới. |
| **Khái quát xử lý** | 1. Tính mốc timeout = `--datetime − 4 phút`.<br>2. Mở transaction, tìm các `Instructions` loại 1 cũ hơn mốc đó.<br>3. Không có dòng nào khớp → rollback (transaction rỗng) + log `notice` + kết thúc.<br>4. Có dòng khớp → xóa từng dòng; dòng nào xóa lỗi → log `alert`, rollback TOÀN BỘ, dừng ngay.<br>5. Xóa hết thành công → log `notice` + commit. |

## A.2 Chi tiết

### A.2.1 Lịch chạy & điều kiện lọc

| Mục | Nội dung | Nguồn |
|---|---|---|
| Lịch chạy (cron) | `* * * * *` — mỗi phút | `docs/02_詳細設計/10_バッチ処理/mng-webap_cron設定_20241029.txt:42` |
| Điều kiện lọc | `instruction_type = 1` AND `instruction_date < keepTime` (`keepTime = --datetime − 4 phút`, literal `4` trong code, không phải hằng số đặt tên) | `DeleteTimeOutControlOneMinuteCommand.php:39,44-49` |
| Ý nghĩa `instruction_type = 1` | = `INSTRUCTION_TYPE_REMOTE_CONTROL` ("宅外制御指示" — lệnh điều khiển thiết bị từ xa/ngoài nhà) — **xác nhận chéo qua hemssv** (`conciergesv`'s `const.php` không định nghĩa hằng số này, batch dùng thẳng số `1`) | `sources/hemssv-develop/config/const.php:53` |

### A.2.2 Vòng đời bình thường của 1 lệnh điều khiển từ xa (để hiểu batch này là "dọn phần còn sót")

1. Người dùng ra lệnh điều khiển thiết bị từ xa qua app → server ghi 1 dòng vào `Instructions`
   (`instruction_type=1`, khóa `ems_sp_no`+`node_id`+`eoj`, kèm `instruction_content`).
2. GW tại nhà định kỳ **poll** API `InstructionController` (hemssv) để lấy lệnh đang chờ của chính nó
   ("定期ポーリング", `InstructionController.php:77`).
3. GW thực thi lệnh trên thiết bị, gửi kết quả về; server nhận kết quả, **tự xóa** dòng `Instructions`
   tương ứng ngay lúc đó (vòng đời bình thường, không cần batch nào can thiệp).
   (`InstructionController.php:546-563`)
4. **Trường hợp GW không phản hồi kịp** (mất kết nối, offline, lỗi mạng...) — dòng lệnh vẫn nằm trong
   `Instructions` mãi nếu không có gì dọn → đây là lý do batch `DeleteTimeOutControlOneMinuteCommand`
   tồn tại: dọn các dòng loại 1 đã quá 4 phút mà chưa được vòng đời bình thường (bước 3) xóa hộ.

**Batch anh em cùng mục đích, khác loại lệnh/khác timeout** (không audit sâu ở đây, chỉ nêu bối cảnh):
`DeleteTimeOutControlTenMinuteCommand` — dọn `instruction_type IN (3,4,6,7)` (khởi động lại từ xa, cập
nhật property map, cập nhật file cấu hình GW, cập nhật tham số điều khiển sưởi) sau 10 phút, và
`instruction_type = 5` (cập nhật firmware) sau 60 phút (chỉ chạy khi phút hiện tại = 0, tức mỗi giờ 1
lần). `instruction_type = 2` (yêu cầu danh sách thiết bị) **không thấy** được dọn bởi batch timeout nào
trong 2 Command này *(chưa xác minh được có batch khác dọn loại này hay không, ngoài phạm vi audit)*.

### A.2.3 Giao dịch & xử lý lỗi

- Mở transaction NGAY CẢ KHI chưa biết có dòng nào cần xóa hay không — nếu danh sách rỗng thì
  `rollback()` 1 transaction không có thay đổi gì (vô hại, chỉ hơi thừa thao tác). (`:41-54`)
- Xóa TỪNG dòng bằng vòng lặp `foreach` + `delete()` — không dùng `deleteAll()` (khác 1 chút so với
  `DeleteLogicalDeletedDevicesCommand`/`DeleteDataCommand` dùng `deleteAll` cho phần lớn trường hợp);
  do xóa từng dòng nên kiểm tra được kết quả từng bản ghi, lỗi 1 dòng → rollback TOÀN BỘ (kể cả các dòng
  đã xóa thành công trước đó trong cùng lượt) + dừng ngay, không xóa tiếp các dòng còn lại. (`:56-62`)
- Điều kiện lọc chỉ dựa vào `instruction_type` + `instruction_date`, **không kiểm tra `instruction_status`**
  — nếu GW đã bắt đầu xử lý lệnh (có cập nhật `instruction_status` khác trạng thái ban đầu) nhưng chưa
  kịp báo hoàn tất trong vòng 4 phút, dòng lệnh đó vẫn bị xóa như bình thường — *(suy đoán rủi ro: nếu
  GW xử lý xong SAU khi batch đã xóa, GW gọi lại `InstructionController` để báo kết quả sẽ không tìm
  thấy `Instructions` tương ứng nữa — code ở `InstructionController.php:505-510` xử lý trường hợp
  "không tìm thấy lệnh" bằng cách log info rồi trả response bình thường, không coi là lỗi — nên hệ quả
  thực tế là im lặng bỏ qua, không phải crash, nhưng kết quả điều khiển trễ có thể không được xác nhận
  lại đúng lúc)*.

### A.2.4 Điểm đặc biệt / Rủi ro

- Không extends `BaseCommand` → không có lock PID chống chạy trùng — với tần suất mỗi phút, nếu 1 lượt
  chạy trước đó (hiếm khi) mất hơn 60 giây để hoàn tất, có thể có 2 tiến trình cùng xử lý chồng lấn.
  Không xác nhận được trong repo liệu điều này có từng xảy ra hay có cơ chế nào khác (ví dụ lock ở tầng
  cron/hệ điều hành) ngăn việc này.
- Ngưỡng "4 phút" là literal trong code, không có comment giải thích tại sao chọn đúng 4 phút (không
  phải 5 phút tròn, hay khớp chu kỳ polling GW nào) — tài liệu thiết kế liên quan (`01_GW通信` docs) là
  file binary chưa đọc được nội dung để xác nhận con số này có căn cứ kỹ thuật cụ thể (ví dụ chu kỳ
  polling mặc định của GW) hay chỉ là số chọn theo kinh nghiệm vận hành.

---

# Phần B — Đối chiếu EMINEL-smart (hệ thống mới)

> Không tìm thấy Lambda/bảng nào tương đương "hàng đợi lệnh + dọn timeout" — vì bản thân khái niệm hàng
> đợi lệnh chờ-thiết-bị-lấy đã không còn tồn tại trong kiến trúc mới. Bảng dưới đây là các khu vực đã
> tra và bằng chứng cụ thể (thay cho B.1/B.2).

## Đã kiểm tra

| Khu vực / candidate | Kết quả |
|---|---|
| Mô hình điều khiển thiết bị thật | **PUSH đồng bộ, không polling**: `src/functions/api-device/control-device.ts:91-425` (user bấm điều khiển) và `src/functions/batch-execute-automation/app.ts:153-159` (lịch tự động) đều gọi THẲNG API cloud hãng (`rinnaiService`/`noritzService`/`daikinService`) qua `src/layers/common/nodejs/business-logic/control-device.ts:226-793`, `await` kết quả ngay trong cùng lần chạy Lambda — không ghi "lệnh đang chờ" vào bảng nào cả. |
| `AutomationTable` (`template-dynamodb.yaml:568-591`) | Không phải hàng đợi lệnh — chỉ là **cấu hình automation tĩnh** (`user_id`+`automation_id`, chứa `list_device`/`list_control_schedule`/`active_flg`). Không có trường kiểu `instruction_type`, không có TTL, không đại diện "1 lệnh đang chờ gửi". |
| Grep `Instruction`/`PendingCommand`/`DeviceCommand`/`ControlQueue` trên toàn `src/` | 0 kết quả — không có bảng/model nào đóng vai trò hàng đợi lệnh như `Instructions` cũ. |
| Grep `timeout`/`TimeOut`/`stale`/`pending` liên quan device-control trong `src/functions/`, `src/layers/common/nodejs/business-logic/` | 0 kết quả liên quan nghiệp vụ (chỉ có chuỗi lỗi mạng chung "RequestTimeout" ở Lambda giám sát log lỗi, không liên quan hàng đợi lệnh). |
| Vòng lặp chờ kết quả Noritz trong `control-device.ts` (~dòng 214-263, 616-671, 709-764) | Là polling NỘI BỘ trong 1 request (chờ chính lệnh vừa gửi trả kết quả, đồng bộ trong cùng Lambda invocation) — khác bản chất hoàn toàn với hàng đợi persistent nhiều lệnh chờ GW polling định kỳ của bản cũ; không có TTL/dọn rác vì không phải bảng lưu trữ lâu dài. |

---

## Tổng kết

**Đây là 1 trường hợp "thay hẳn cơ chế về chất" rõ ràng — không phải rút gọn hay tối ưu của logic cũ:**

- **Bản cũ — mô hình polling bất đồng bộ, cần hàng đợi + dọn rác:** server ghi lệnh vào `Instructions`
  → GW tự poll định kỳ để lấy → GW thực thi → GW báo kết quả → server xóa lệnh khỏi hàng đợi. Vì GW có
  thể mất kết nối/offline bất kỳ lúc nào, hệ thống BẮT BUỘC phải có cơ chế dọn "lệnh chết" (chính là
  batch đang audit + 2 hàm trong `DeleteTimeOutControlTenMinuteCommand`) — đây là hệ quả tất yếu của
  việc chọn mô hình polling: có hàng đợi thì phải có dọn hàng đợi.
- **Bản mới — mô hình push đồng bộ, không cần hàng đợi:** Lambda gọi thẳng API cloud hãng thiết bị và
  chờ response trong cùng 1 lần thực thi (`control-device.ts:226-793`). Không có bước "ghi lệnh chờ,
  thiết bị tự đến lấy" nào — nên không có gì để "timeout" ở tầng lưu trữ, không cần bảng hàng đợi, không
  cần batch dọn rác đi kèm.
- **Đánh đổi đáng lưu ý** *(suy đoán, ngoài phạm vi trực tiếp của batch này nhưng liên quan kiến trúc)*:
  mô hình mới phụ thuộc thiết bị/cloud hãng phải phản hồi được NGAY trong thời gian chờ của 1 lần gọi
  Lambda (timeout Lambda thường tính bằng giây/phút, không phải "chờ vài phút tới hàng giờ" như mô hình
  polling cũ cho phép) — nếu thiết bị offline, lỗi sẽ trả về ngay cho người dùng thay vì "âm thầm chờ
  rồi timeout dọn sau vài phút" như trước; đây là đánh đổi giữa phản hồi tức thời (mới) và khả năng chịu
  được thiết bị/GW gián đoạn tạm thời mà không báo lỗi ngay cho user (cũ).

---

## Nguồn

| Phần | Nội dung | Căn cứ |
|---|---|---|
| Hệ thống cũ | Logic chính | `sources/conciergesv-develop/src/Command/DeleteTimeOutControlOneMinuteCommand.php` |
| Hệ thống cũ | Batch anh em (bối cảnh, không audit sâu) | `sources/conciergesv-develop/src/Command/DeleteTimeOutControlTenMinuteCommand.php` |
| Hệ thống cũ | Ý nghĩa `instruction_type=1` (xác nhận chéo qua hemssv) | `sources/hemssv-develop/config/const.php:53-65` |
| Hệ thống cũ | Vòng đời bình thường của lệnh điều khiển (tạo → poll → tự xóa khi xong) | `sources/hemssv-develop/src/Controller/InstructionController.php:77,470-563` |
| Hệ thống cũ | Ý nghĩa cột `Instruction` | `sources/eminel_sv_lib-develop/src/Model/Entity/Instruction.php` |
| Hệ thống cũ | Lịch chạy (cron) | `docs/02_詳細設計/10_バッチ処理/mng-webap_cron設定_20241029.txt:42-43` |
| Hệ thống cũ | Danh sách batch (mô tả tiếng Nhật, nhóm server) | `docs/03_API仕様/04_バッチ一覧.md:78` |
| Hệ thống mới | Điều khiển thiết bị qua API (user) | `src/functions/api-device/control-device.ts:91-425` |
| Hệ thống mới | Điều khiển thiết bị theo lịch tự động (batch) | `src/functions/batch-execute-automation/app.ts:153-159` |
| Hệ thống mới | Logic điều khiển dùng chung, gọi thẳng API cloud hãng | `src/layers/common/nodejs/business-logic/control-device.ts:226-793` |
| Hệ thống mới | `AutomationTable` (xác nhận không phải hàng đợi lệnh) | `template-dynamodb.yaml:568-591` |
