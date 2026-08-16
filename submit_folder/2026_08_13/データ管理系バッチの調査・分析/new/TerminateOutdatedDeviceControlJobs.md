# TerminateOutdatedDeviceControlJobsCommand（期限切れデバイス制御ジョブ終了）

## Tóm tắt

`TerminateOutdatedDeviceControlJobsCommand` là batch cron chạy **mỗi phút** trên `conciergesv`: xử lý
"job điều khiển thiết bị" phía app (bảng `ConDeviceControls`) đã tồn tại quá 5 phút mà chưa nhận được
kết quả từ GW — đánh dấu hàng loạt là thất bại (`send_result_kind=HEMS_FAILED`) rồi gửi push notification
báo user "thiết lập [tên thiết bị] đã timeout", có cơ chế fallback đưa vào hàng đợi `PushMessages` để
`DispatchPushMessagesCommand` gửi lại nếu push trực tiếp thất bại. Đây là mắt xích "báo lỗi cho user"
của cùng luồng điều khiển từ xa mà `DeleteTimeOutControlOneMinuteCommand` (đã audit) dọn phía hàng đợi
HEMS — 2 batch cùng canh 1 job, khác bảng/khác timeout (4 phút cho hàng đợi GW, 5 phút cho job phía app).
Ở repo mới `syp-eminelstandard-backend`, **không có cơ chế tương đương** — không chỉ thiếu bảng/batch,
mà cả HÀNH VI NGHIỆP VỤ "chủ động báo lỗi cho user qua push khi điều khiển timeout" cũng **biến mất
hoàn toàn**, không được port lại dưới hình thức nào: điều khiển thiết bị mới là 1 lệnh gọi API đồng bộ
tới cloud hãng thiết bị, lỗi/timeout chỉ trả về ngay trong response HTTP của chính API đó — nếu app đã
đóng hoặc không hiển thị lỗi, user sẽ không biết yêu cầu của mình thất bại (khác hẳn bản cũ luôn đảm bảo
có push dù app đã đóng, nhờ polling GW + batch cron độc lập).

---

# Phần A — Hệ thống cũ

## A.1 Tổng quát

| Mục | Nội dung |
|---|---|
| **Tên batch** | Class: `TerminateOutdatedDeviceControlJobsCommand` (extends `Command`, có dependency injection `PushMessageServiceInterface` qua constructor — khác thường so với các Command khác đã audit) · Script cron: `30_TerminateOutdatedDeviceControlJobs.sh` · Tên tiếng Nhật trong cron: "30.機器制御タイムアウト機能". |
| **Vai trò** | Phát hiện job điều khiển thiết bị (app-side) bị timeout (GW không phản hồi kịp), đánh dấu thất bại + chủ động báo cho user qua push notification. |
| **Input** | Đọc bảng `ConDeviceControls` (bảng vật lý `t_301`) JOIN `ConDevices` (bảng vật lý `t_201`; chỉ thiết bị đang active, chưa xóa) JOIN `PushDeviceTokens` (lấy token để gửi push) — lọc `created <= now−5 phút` AND `result_received IS NULL` AND `send_result_kind IS NULL`. Tham số `--datetime` (mặc định `now`). |
| **Output** | `UPDATE` hàng loạt `send_result_kind`/`modified` trên `ConDeviceControls`; gửi push notification qua `PushMessageServiceInterface`; nếu gửi lỗi → ghi thêm 1 dòng vào `PushMessages`+`PushMessageDestinations` (hàng đợi retry). |
| **Khái quát xử lý** | 1. Xây câu query lọc job timeout (kèm join device + push token).<br>2. Lặp phân trang (limit 500/trang) cho tới khi hết dữ liệu.<br>3. Mỗi trang: `updateAll` đánh dấu `HEMS_FAILED` cho toàn bộ job trong trang.<br>4. Với từng job: có push token thì gửi push "timeout"; gửi lỗi thì lưu vào hàng đợi `PushMessages` để batch khác gửi lại; không có push token thì bỏ qua (không lưu retry). |

## A.2 Chi tiết

**Bản đồ vòng đời 1 job điều khiển thiết bị** (để thấy batch này nằm ở đâu trong tổng thể — không lặp
lại chi tiết đã có ở `DeleteTimeOutControlOneMinute.md`, chỉ tham chiếu):

```
App gửi lệnh điều khiển ─▶ SetDataController (conciergesv):
                             ghi 1 dòng ConDeviceControls (created=now, result_received=NULL,
                             send_result_kind=NULL) + 1 dòng Instructions (type=1) chứa "seqno"
                             = control_id để đối chiếu ngược lại
                                     │
                                     ▼
                    GW poll Instructions (hemssv) ── lấy lệnh, thực thi thiết bị
                                     │
                     ┌───────────────┴───────────────┐
                     ▼ (GW phản hồi trong 4 phút)      ▼ (GW KHÔNG phản hồi)
     InstructionController cập nhật ConDeviceControls    Instructions bị dọn bởi
     (result_properties, result_received=now) + xóa       DeleteTimeOutControlOneMinuteCommand
     dòng Instructions; push báo THẤT BẠI khi kết quả     (4 phút, không đụng ConDeviceControls)
     bất thường (sendPushNotification luôn gọi với succeeded=false)
                                                                    │
                                                                    ▼
                                                   ConDeviceControls VẪN còn result_received=NULL
                                                   send_result_kind=NULL ("job mồ côi")
                                                                    │
                                                                    ▼
                                      TerminateOutdatedDeviceControlJobsCommand (5 phút, batch NÀY):
                                      đánh dấu HEMS_FAILED + push báo "timeout" cho user
```

Mốc **5 phút** ở batch này dài hơn mốc **4 phút** dọn `Instructions` — cho hàng đợi HEMS đủ thời gian tự
giải quyết (thành công hoặc bị dọn) trước khi phía app chính thức báo lỗi cho user, tránh báo lỗi quá
sớm trong khi GW vẫn còn cơ hội phản hồi kịp.

### A.2.1 Điều kiện lọc job timeout

| Mục | Nội dung | Nguồn |
|---|---|---|
| Lịch chạy (cron) | `* * * * *` — mỗi phút | `docs/02_詳細設計/10_バッチ処理/mng-webap_cron設定_20241029.txt:116-117` |
| Điều kiện lọc | `ConDeviceControls.created <= (--datetime − 5 phút)` AND `result_received IS NULL` AND `send_result_kind IS NULL` | `TerminateOutdatedDeviceControlJobsCommand.php:96-100` |
| Điều kiện thiết bị hợp lệ (JOIN) | `ConDevices.dev_reg_status = REG_STATUS_ACTIVE(1)` AND `ConDevices.deleted IS NULL` — job của thiết bị đã bị xóa/ngừng hoạt động vẫn bị xử lý timeout (chỉ KHÔNG lấy được tên thiết bị đẹp để hiện trong thông báo, dùng chữ "機器" thay thế) | `:82-94,131-134` |
| Ý nghĩa cột `ConDeviceControls` | `c001`=control_id (khớp `seqno` trong `Instructions.instruction_content` phía hemssv), `c002`=ems_sp, `c004`=created, `c008`=result_received, `c010`=send_result_kind (`HEMS_FAILED=1`, chỉ 1 giá trị được định nghĩa — thành công thì cột này không cần set) | `Entity/ConDeviceControl.php:27-39` |
| Xác nhận vòng đời (nơi ghi `result_received`/xóa `Instructions` khi GW phản hồi kịp) | `sources/hemssv-develop/src/Controller/InstructionController.php:572-582` (ghi `result_received`) · `:545-556` (xóa `Instructions`) |

### A.2.2 Xử lý phân trang & đánh dấu hàng loạt

1. Query gốc dùng chung điều kiện lọc cố định (A.2.1), KHÔNG có `->order()` tường minh.
2. Vòng lặp `while(true)`: lấy 1 trang tối đa 500 dòng bằng `limit(500)->offset($offset)`.
3. Hết dữ liệu (`isEmpty()`) → dừng vòng lặp.
4. `updateAll()` đánh dấu TOÀN BỘ job trong trang: `send_result_kind = HEMS_FAILED`, `modified = now`.
5. Xử lý gửi push cho từng job (xem A.2.3).
6. Trang trả về ít hơn `limit` (500) → dừng (coi là trang cuối); ngược lại `offset += 500` rồi lặp tiếp.

Nguồn: `TerminateOutdatedDeviceControlJobsCommand.php:82-119,166-170`.

**⚠️ Điểm bất thường của hệ cũ — phân trang bằng OFFSET tăng dần trên 1 tập kết quả đang CO LẠI:**

- Điều kiện tái hiện: số job timeout trong 1 lượt chạy VƯỢT QUÁ 500 (nhiều hơn 1 trang).
- Cơ chế lỗi: bước 4 ở trên đánh dấu `send_result_kind` cho các job VỪA lấy ở trang hiện tại — khiến
  chúng KHÔNG CÒN khớp điều kiện `send_result_kind IS NULL` nữa. Trang tiếp theo dùng `offset += 500`
  nhưng truy vấn LẠI TỪ ĐẦU trên tập đã bị thu hẹp (đã trừ đi các job trang trước) — offset cũ giờ trỏ
  lệch vị trí, dẫn tới **bỏ sót 1 khoảng job** ở giữa (không được lấy ra ở bất kỳ trang nào trong lượt
  chạy này) và có thể dừng vòng lặp SỚM hơn thực tế (vì trang tiếp theo trả về ít hơn `limit` dù vẫn còn
  job chưa xử lý, do offset đã "nhảy qua" chúng).
- Hệ quả thực tế: các job bị bỏ sót trong lượt chạy này **không mất vĩnh viễn** — vì `send_result_kind`
  của chúng vẫn còn `NULL`, lượt chạy KẾ TIẾP (1 phút sau, do cron mỗi phút) sẽ query lại từ `offset=0`
  và bắt được chúng bình thường. Vậy hệ quả thực chất là **báo lỗi cho user bị trễ thêm tối đa vài phút**
  trong trường hợp hiếm khi có >500 job timeout cùng lúc — không phải mất dữ liệu, nhưng vẫn là lỗi
  logic phân trang cần sửa nếu port sang hệ mới (dùng cursor/keyset pagination hoặc lọc thêm điều kiện
  loại trừ ID đã xử lý thay vì offset thuần).
- Thiếu `->order()` tường minh làm trầm trọng thêm vấn đề (thứ tự trả về giữa các lần gọi không được
  đảm bảo ổn định về mặt lý thuyết SQL, dù PostgreSQL trong thực tế thường ổn định nếu không có ghi
  chèn/xóa xen giữa — ở đây LẠI CÓ ghi xen giữa qua chính `updateAll` của vòng lặp này).

### A.2.3 Gửi thông báo & cơ chế fallback retry

1. Với mỗi job: nếu không tìm được `PushDeviceToken` tương ứng (`ems_sp` không có token đăng ký) →
   `continue`, bỏ qua hoàn toàn — không gửi, không lưu retry, không log. (`:126-129`)
2. Có token → dựng tiêu đề cố định `"機器設定変更"`, nội dung theo tên thiết bị (qua
   `HemsDeviceNameService::getDeviceNameForApp`, fallback `"機器"` nếu không lấy được thiết bị) +
   `"... の設定変更がタイムアウトしました。"` (cấu hình thiết bị đã timeout). (`:131-135`)
3. Gọi `pushMessageService->sendToDeviceTokens()` (interface được inject qua constructor — thiết kế để
   dễ test/thay thế implementation). Coi là lỗi nếu **exception** HOẶC `successCount !== 1`
   (`:137-146`) — chuẩn hóa cả 2 loại lỗi (network exception và "gửi nhưng không có ai nhận") thành
   cùng 1 nhánh xử lý lỗi.
4. Gửi thành công → `continue` sang job tiếp theo, KHÔNG chạm vào bước 5. (`:148-149`)
5. Gửi lỗi (bắt bởi try/catch) → log lỗi, rồi **tạo 1 `PushMessage` + 1 `PushMessageDestination` mới**,
   lưu vào DB — đây là hàng đợi chuẩn dùng chung toàn hệ thống, được `DispatchPushMessagesCommand`
   (batch #24, cũng chạy mỗi phút) tự động quét và gửi lại sau. Lỗi khi LƯU record retry này cũng chỉ
   log, không có xử lý gì thêm (job coi như đã "xử lý xong" dù cả gửi trực tiếp lẫn lưu retry đều lỗi).
   (`:154-163`)

### A.2.4 Điểm đặc biệt / Rủi ro

- Không extends `BaseCommand` → không lock PID chống chạy trùng ở tầng PHP (nhất quán với các batch dọn
  dẹp khác đã audit); tuy nhiên script cron bọc ngoài `30_TerminateOutdatedDeviceControlJobs.sh` dùng
  `flock -n` (「flockで多重起動チェック」) nên thực tế vẫn được chống chạy trùng ở tầng shell.
- Job của thiết bị KHÔNG active/đã xóa vẫn bị đánh dấu timeout bình thường (chỉ khác ở tên hiển thị
  trong thông báo) — nghĩa là user vẫn nhận được thông báo "thiết lập [thiết bị] timeout" ngay cả khi
  thiết bị đó đã bị gỡ khỏi hệ thống sau khi job được tạo; đây có thể là hành vi cố ý (vẫn cần báo cho
  user biết yêu cầu của họ thất bại) hoặc chưa tính tới trường hợp edge case này — không có comment xác
  nhận chủ đích. *(suy đoán)*
- Không có track "đã gửi bao nhiêu lần retry" hay giới hạn số lần retry ở tầng `PushMessages` (nằm ngoài
  phạm vi file này — thuộc về `DispatchPushMessagesCommand`, chưa audit).
- Constructor nhận `PushMessageServiceInterface` qua dependency injection — điểm khác biệt duy nhất so
  với toàn bộ các Command khác đã audit (đều gọi trực tiếp service/table trong `initialize()`), cho thấy
  đây có thể là Command có unit test thật (test file không có trong nhóm `src/Command` đã audit khác).

---

# Phần B — Đối chiếu EMINEL-smart (hệ thống mới)

> Không tìm thấy Lambda/bảng nào tương đương. Bảng dưới đây là các khu vực đã tra và bằng chứng cụ thể
> (thay cho B.1/B.2).

## Đã kiểm tra

| Khu vực / candidate | Kết quả |
|---|---|
| Đường lỗi khi điều khiển thiết bị (`src/functions/api-device/control-device.ts`, hàm `controlDevice:63-467`) | Không có try/catch nội bộ nào quanh lời gọi `rinnaiService`/`noritzService`/`daikinService` — lỗi/exception bay thẳng lên `apiHandler` (`src/layers/common/nodejs/utils/api-handler.ts:19-37`), trả `fail(STATUS_CODE.INTERNAL_SERVER_ERROR, {message: ERR_SYS_ERROR})` **ngay trong response HTTP**. Vài nhánh Noritz chủ động trả `fail(BAD_REQUEST, ERR_CANNOT_CONTROL_REMOTE_DEVICE)` (dòng 233-236, 259-262, 291-294, 316-319) — vẫn chỉ là response lỗi API, không có push nào kèm theo. |
| Vòng lặp chờ kết quả Noritz (`control-device.ts` dòng 214-223, 243-252,...) | Polling ĐỒNG BỘ trong cùng Lambda, không có timeout tường minh trong vòng lặp — nếu treo, bị chính AWS Lambda timeout cắt ngang, trả lỗi 500 chung, không có push nào. Khác hẳn bản cũ dùng batch cron độc lập kiểm tra sau 5 phút. |
| `src/layers/common/nodejs/business-logic/control-device.ts:776-789` | Có try/catch nhưng chỉ xử lý case token bị revoke (`isUnauthorizedRemoved` → bỏ qua thiết bị đó); các lỗi khác `throw` tiếp, không có logic push nào (không import bất kỳ service push nào trong file). |
| `src/layers/common/nodejs/services/push-notification-firebase.ts`, hàm `pushNotificationFirebase:35-105` | Gửi **1 lần duy nhất** qua Firebase (dòng 89); lỗi token không hợp lệ thì xóa token (dòng 138-149), lỗi khác thì `throw` — **không có hàng đợi retry nào** như `PushMessages`/`PushMessageDestinations`/`DispatchPushMessagesCommand` cũ. |
| Grep `HEMS_FAILED`/`send_result_kind`/`ConDeviceControls`/`result_received`/`PushMessage`/`DispatchPushMessages` trên toàn `src/` | 0 kết quả — không có bảng, batch, hay khái niệm "job điều khiển timeout" nào tồn tại ở hệ mới. |

---

## Tổng kết

**Đây là 1 trường hợp "thay hẳn cơ chế về chất" — nhưng khác với batch anh em `DeleteTimeOutControlOneMinuteCommand`
ở chỗ có 1 hành vi nghiệp vụ bị RỤNG HẲN theo, không chỉ đổi cách làm:**

- **Phần "dọn hàng đợi timeout"**: giống hệt lý do đã đúc kết ở `DeleteTimeOutControlOneMinute.md` —
  kiến trúc điều khiển thiết bị đổi từ polling-bất-đồng-bộ (cần hàng đợi + dọn timeout) sang push-đồng-bộ
  (gọi thẳng API cloud hãng, `await` ngay trong Lambda) — không còn "job đang chờ" nào tồn tại đủ lâu để
  cần 1 batch riêng phát hiện timeout.
- **Phần "báo lỗi cho user qua push" — đây là điểm KHÁC batch anh em, đáng lưu ý nhất của audit này**:
  bản cũ tách biệt 2 việc — (1) gọi API để bắt đầu điều khiển, (2) đảm bảo user LUÔN được báo qua push
  khi điều khiển THẤT BẠI hoặc timeout (thành công KHÔNG có push — app tự thấy trạng thái mới), độc lập
  với việc app có đang mở hay không, nhờ polling GW ở tầng backend + batch cron riêng theo dõi. Bản mới
  GỘP 2 việc làm 1: kết quả CHỈ trả về trong response của chính lệnh API gọi lúc đó — nếu app đã đóng,
  mất mạng, hoặc không hiển thị lỗi đúng cách, **user sẽ không bao giờ biết** yêu cầu điều khiển của họ
  đã thất bại. Đây không phải "tối ưu kiến trúc" mà là **mất hẳn 1 đảm bảo UX/reliability** so với bản
  cũ — nếu nghiệp vụ mới vẫn cần đảm bảo user được báo khi điều khiển thất bại dù app đã đóng (ví dụ
  điều khiển hẹn giờ/automation chạy nền), cần bổ sung lại cơ chế thông báo bất đồng bộ tương đương,
  không thể coi "trả lỗi qua response API" là đủ thay thế.
- Đánh đổi tổng thể: được phản hồi nhanh hơn khi app đang mở và chờ trực tiếp; mất khả năng đảm bảo
  thông báo khi app không ở foreground hoặc lệnh được kích hoạt từ automation/background (không có ai
  "đang chờ response" để thấy lỗi).

---

## Nguồn

| Phần | Nội dung | Căn cứ |
|---|---|---|
| Hệ thống cũ | Logic chính | `sources/conciergesv-develop/src/Command/TerminateOutdatedDeviceControlJobsCommand.php` |
| Hệ thống cũ | Ý nghĩa cột `ConDeviceControl` (bảng vật lý `t_301`) | `sources/eminel_sv_lib-develop/src/Model/Entity/ConDeviceControl.php` · `Table/ConDeviceControlsTable.php:41` |
| Hệ thống cũ | Ý nghĩa cột `ConDevice` liên quan (bảng vật lý `t_201`) | `sources/eminel_sv_lib-develop/src/Model/Entity/ConDevice.php:52-88` · `Table/ConDevicesTable.php:41` |
| Hệ thống cũ | Nơi ghi `result_received`/xóa `Instructions` khi GW phản hồi kịp (xác nhận vòng đời) | `sources/hemssv-develop/src/Controller/InstructionController.php:572-582` (ghi `result_received`) · `:545-556` (xóa `Instructions`) |
| Hệ thống cũ | Batch liên quan cùng vòng đời (đã audit) | `docs/legacy-batch-review/DeleteTimeOutControlOneMinute.md` |
| Hệ thống cũ | Cơ chế hàng đợi retry push (consumer) | `sources/conciergesv-develop/src/Command/DispatchPushMessagesCommand.php:68-172` |
| Hệ thống cũ | Lịch chạy (cron) | `docs/02_詳細設計/10_バッチ処理/mng-webap_cron設定_20241029.txt:116-117` |
| Hệ thống cũ | Danh sách batch (mô tả tiếng Nhật, nhóm server) | `docs/03_API仕様/04_バッチ一覧.md:80` |
| Hệ thống mới | API điều khiển thiết bị (đường lỗi, không có push đi kèm) | `src/functions/api-device/control-device.ts` (hàm `controlDevice:63-467`) |
| Hệ thống mới | Chuẩn hóa lỗi thành response HTTP | `src/layers/common/nodejs/utils/api-handler.ts:19-37` |
| Hệ thống mới | Logic điều khiển dùng chung (automation), xác nhận không có push lỗi | `src/layers/common/nodejs/business-logic/control-device.ts:1-22,776-789` |
| Hệ thống mới | Cơ chế push chung (xác nhận gửi 1 lần, không hàng đợi retry) | `src/layers/common/nodejs/services/push-notification-firebase.ts:35-149` |
