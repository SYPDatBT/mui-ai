# WatchNotificationCommand（見守り通知機能）

## Tóm tắt

`WatchNotificationCommand` là batch chạy 6 lần/giờ (mỗi 10 phút, lệch 7 phút) trong hệ thống cũ
(`conciergesv`, nhóm `mng-webap`): với mỗi hộ đã đăng ký "見守り通知" (thông báo trông nom người thân),
đọc dữ liệu cảm biến người 10-phút đã tính sẵn trong `s_101` (do `CalcTenMinutesSensorCommand` tạo ra
mỗi 10 phút), áp dụng **1 trong 2 thuật toán phán đoán khác nhau** tùy cấu hình của hộ đó (見守り①
"ただいま通知/お留守番代行" hoặc 見守り② "見守り通知" theo dõi liên tục) để quyết định 1 trong 5 trạng
thái (không áp dụng / có người / không có người / không có dữ liệu / mất dữ liệu liên tục), rồi ghi Push
notification + "お知らせ" (message) tương ứng cho app đọc. Trong `syp-eminelstandard-backend`
(EMINEL-smart), **có 1 phần tương đương nhưng đơn giản hóa mạnh**: tính năng "お部屋みまもり" (room
monitor) push khi cảm biến IoT của MUI báo `motion=1` theo thời gian thực — không polling theo cửa sổ
10 phút, không có 2 thuật toán riêng theo cấu hình, và **không tìm thấy tương đương** cho phần "không có
người" / "không có dữ liệu" / "mất dữ liệu liên tục" của bản cũ.

---

# Phần A — Hệ thống cũ

## A.1 Tổng quát

| Mục | Nội dung |
|---|---|
| **Tên batch** | Class: `WatchNotificationCommand` · Script cron: `3_WatchNotification.sh` · Tên tiếng Nhật trong cron: `3.見守り通知機能`. |
| **Vai trò** | Theo dõi dữ liệu cảm biến người (PIR) đã tổng hợp 10 phút của từng hộ đăng ký "見守り通知", phán đoán và phát thông báo "có người / không có người / không có dữ liệu / mất dữ liệu liên tục" theo 1 trong 2 thuật toán cấu hình cho hộ đó. |
| **Input** | Đọc từ 4 bảng nghiệp vụ: `t_901`（cấu hình + lịch sử thông báo trước）＋ `t_101`（danh sách hộ）＋ `t_201`（thiết bị đã đăng ký, lọc cảm biến người）＋ `s_101`（dữ liệu PIR 10 phút, do `CalcTenMinutesSensorCommand` tạo ra trước đó）, cộng bảng mẫu `con_regular_messages`（6 mẫu thông báo id `1`–`6`, đọc ở bước ghi kết quả）. Không đọc CSV/file, không gọi API ngoài. |
| **Output** | Insert 4 bảng: `push_messages`/`push_message_destinations`（Entity `PushMessage`, Push notification）+ `con_messages`/`con_message_destinations`（Entity `ConMessage`, "お知らせ" trong app）— nhưng mỗi pattern trạng thái (101/102/103/104) chỉ lưu được 1 cặp cho hộ cuối danh sách do `saveOrFail` đặt ngoài `foreach` (nghi bug hệ cũ — xem QUAN SÁT §A.2.7). Update `t_901` (thời điểm thông báo trước) vẫn chạy cho mọi hộ đã xét. |
| **Khái quát xử lý** | 1. Lấy danh sách hộ có bật ít nhất 1 trong 2 cấu hình "見守り通知".<br>2. Với mỗi hộ: lấy khung giờ theo dõi (start/end) từ cấu hình đang hiệu lực.<br>3. Lấy số thiết bị cảm biến người đã đăng ký (1 hoặc ≥2 phòng).<br>4. Kiểm tra "mất dữ liệu liên tục" — nếu đúng, ưu tiên xử lý trạng thái này, bỏ qua bước phán đoán khác.<br>5. Nếu không, chạy 1 trong 2 thuật toán (見守り① hoặc ②) tùy cấu hình nào đang bật, ra 1 trong 5 trạng thái.<br>6. Với mỗi trạng thái ≠ "không áp dụng": ghi Push + "お知らše" tương ứng (1 trong 6 mẫu cố định).<br>7. Update `t_901.c006`（thời điểm thông báo trước）cho mọi hộ đã xét ở bước 6. |

## A.2 Chi tiết

### Bản đồ cách tính — 7 bước

```
BƯỚC 1  Lấy hộ theo dõi     → hộ có ≥1 trong 2 cấu hình bật, chưa xóa logic      §A.2.3
BƯỚC 2  Khung giờ theo dõi  → chọn cấu hình có start_time sớm hơn nếu cả 2 bật   §A.2.3
BƯỚC 3  Số thiết bị cảm biến → đếm thiết bị PIR đã đăng ký (t_201)               §A.2.3
BƯỚC 4  Mất dữ liệu liên tục → ưu tiên trên cả 2 thuật toán, nếu đúng thì dừng   §A.2.4
BƯỚC 5  Thuật toán 見守り①  → "ただいま通知/お留守番代行" (nếu c003_01 bật)      §A.2.5
BƯỚC 5' Thuật toán 見守り②  → "見守り通知" theo dõi liên tục (nếu c003_02 bật)   §A.2.6
BƯỚC 6  Ghi thông báo       → Push + お知らせ theo 1 trong 6 mẫu cố định         §A.2.7
BƯỚC 7  Update t_901        → ghi lại thời điểm thông báo (c006) + modified     §A.2.7
```

### A.2.1 Lịch chạy & tham số

| Mục | Nội dung | Nguồn |
|---|---|---|
| Lịch chạy (cron) | `7,17,27,37,47,57 * * * *` — 6 lần/giờ, mỗi 10 phút, lệch 7 phút (chạy **5 phút sau** `CalcTenMinutesSensorCommand` ở phút `2,12,...`, đủ thời gian để `s_101` có dữ liệu mới) | `docs/02_詳細設計/10_バッチ処理/mng-webap_cron設定_20241029.txt:8-10` |
| Command thực thi | `php cake.php WatchNotification [--datetime=<判定日>]` | `WatchNotificationCommand.php:57-62` |
| Mốc **判定日** (khi không truyền tham số) | `hiện tại − 20 phút`, sau đó làm tròn xuống mốc 10 phút | `WatchNotificationCommand.php:917-936` |
| Validate tham số truyền vào | Regex bắt buộc đúng format `yyyy-MM-ddTHH:mm:00+09:00`; sai format → `abort` (kèm log `alert`) | `WatchNotificationCommand.php:79-83,917-930` |

### A.2.2 Nguồn dữ liệu — 4 bảng liên quan

| Bảng | Cột | Ý nghĩa | Độ tin cậy |
|---|---|---|---|
| `t_901` (`ConMotionSensorNotificationSettings`) | `c001` | EMS-SP | **Chắc chắn** — hằng số `C_EMS_SP` trong Entity |
| `t_901` | `c002` | Loại cấu hình: `1`=`NOTIFICATION_TYPE_WHEN_DETECTED`（見守り①）, `2`=`NOTIFICATION_TYPE_WHEN_UNDETECTED`（見守り②） | **Chắc chắn** — hằng số Entity, khớp cách code dùng `MOTION_DETECTION_NOTIFICATION_1/_2` |
| `t_901` | `c003` | Cờ bật/tắt cấu hình (0/1) | **Chắc chắn** — `C_ENABLE_FLAG` |
| `t_901` | `c004` / `c005` | Giờ bắt đầu / kết thúc theo dõi | **Chắc chắn** — `C_START_TIME`/`C_END_TIME` |
| `t_901` | `c006` | Thời điểm thông báo lần trước | **Chắc chắn** — `C_BEFORE_NOTICED`, batch tự update sau khi gửi |
| `t_901` | `c007` | Thời điểm sửa đổi cấu hình | **Chắc chắn** — `C_MODIFIED` |
| `t_201` (`ConDevices`, thiết bị đăng ký) | `c007` | Mã lớp ECHONET (`class_eoj`), lọc `'001101'` = cảm biến người | **Chắc chắn** — hằng số `C_CLASS_EOJ` trong Entity `ConDevice` |
| `t_201` | `c017` | Mã hãng sản xuất (`dev_maker_code`), lọc `'0000E3'` | **Chắc chắn** — `C_DEV_MAKER_CODE` |
| `t_201` | `c035` | Thời điểm xóa logic, `IS NULL` = còn hiệu lực | **Chắc chắn** — `C_DELETED` |
| `s_101` (`ConSensorMemoryValue`, xem thêm batch `CalcTenMinutesSensorCommand`) | `c001`/`c002`/`c003`/`c004`/`c006` | EMS-SP / device_type (`DETECT_CNT`=14) / room_id (`DETECT_LIVING`=0, `DETECT_OTHER`=1) / mốc 10 phút / số lần phát hiện | **Chắc chắn** — cùng bảng, cùng hằng số đã xác nhận ở batch `CalcTenMinutesSensorCommand` |

### A.2.3 Xác định hộ cần xét & khung giờ theo dõi

1. `getWatchTargetEmsp()` — SQL phức tạp (`WatchNotificationCommand.php:835-909`) lấy mọi hộ (`t_101`,
   chưa xóa logic) có ít nhất 1 trong 2 cấu hình `t_901` đang **trong khung giờ theo dõi tại thời điểm
   phán đoán** (so `unixTime` với `c004`/`c005`, có xử lý case qua nửa đêm) VÀ **chưa được thông báo
   trong khung hiện tại** (`c006 IS NULL` hoặc `c006` cũ hơn mốc so sánh) — cơ chế chống thông báo trùng.
   Lưu ý: `c005` trả về đã bị SQL **trừ sẵn 10 phút** (`notification.c005 - cast('10 minutes' as
   INTERVAL)`, `:851`, comment 「監視終了時間（10分前）」`:501`) — mốc kết thúc dùng để phán đoán =
   `c005 − 10分`, truyền xuyên suốt xuống các bước sau qua `getMonitoringTime()`.
2. `getMonitoringTime()` — nếu hộ có cả 2 cấu hình bật, **chọn cấu hình có giờ bắt đầu (`c004`) sớm
   hơn** làm khung giờ theo dõi chính thức; nếu chỉ 1 cấu hình bật, dùng cấu hình đó.
   (`WatchNotificationCommand.php:765-795`)
3. `getRegisteredDeviceData()` — đếm số thiết bị cảm biến người đã đăng ký hợp lệ của hộ (dùng ở bước
   phân nhánh 1 thiết bị / ≥2 thiết bị). (`WatchNotificationCommand.php:803-828`)

### A.2.4 Kiểm tra "mất dữ liệu liên tục" (`getContinuousMissingData`) — có ưu tiên cao nhất

- Lấy tổng số bản ghi **thiếu** (`c006 IS NULL` → tính là 1) trong **3 khung 10 phút gần nhất**
  (`generate_series(0, CONSECUTIVE_MISSING_VALUES−1=2)` = 3 mốc: 判定時刻, −10分, −20分, cắt theo khung
  theo dõi), riêng cho từng phòng (`c006Living`, `c006Other`).
  (`WatchNotificationCommand.php:643-677`, hằng số `const.php:694`)
- Nếu hộ có ≥2 thiết bị: mất dữ liệu liên tục khi **1 trong 2 phòng** đạt ngưỡng `CONSECUTIVE_MISSING_VALUES = 3`.
  Nếu hộ có 1 thiết bị: chỉ xét phòng khách (`c006living`). (`WatchNotificationCommand.php:612-635`)
- **Nếu đúng → dừng ngay, không chạy tiếp thuật toán 見守り①/② cho hộ này** — đây là bước có độ ưu tiên
  cao nhất trong toàn luồng phán đoán. (`WatchNotificationCommand.php:150-157`)

### A.2.5 Thuật toán 見守り① — "ただいま通知／お留守番代行" (`checkMonitoring1`, khi `c003_01` bật)

Ý tưởng: chỉ xét **1 khung 10 phút duy nhất** (khung chứa thời điểm phán đoán, làm tròn xuống chục
phút) — trả lời "vừa rồi có phát hiện người không?".

```
SUM(số lần phát hiện) trong khung 10 phút chứa thời điểm phán đoán  (SQL s_101, WHERE c004 = khung đó)

├─ count > 0 (có bản ghi) VÀ sum >= MOTION_DETECTION_COUNT_THRESHOLD(=1)
│     → MOTION_SENSOR (101) "có người"
│
├─ count > 0 VÀ thời điểm phán đoán (làm tròn 10p) == mốc kết thúc phán đoán (= c005 − 10分, phút nguyên)
│     ├─ sum khác NULL (có bản ghi nhưng = 0)  → NO_MOTION_SENSOR (102) "không có người"
│     └─ sum = NULL (không có bản ghi nào)     → NO_DATA (103) "không có dữ liệu" (kèm log INFO)
│
└─ Các trường hợp còn lại → NOT_APPLICABLE (100) "không áp dụng", không thông báo
```
Nguồn: `WatchNotificationCommand.php:373-427,491-528`, hằng số `const.php:702,708-716`.

**Đọc kỹ**: nhánh "không có người"/"không có dữ liệu" **chỉ được xét đúng vào mốc kết thúc phán đoán
= `c005 − 10分`** (khung 10 phút trước giờ kết thúc cấu hình, xem §A.2.3) — các khung giữa chừng chỉ
có thể ra "có người" hoặc "không áp dụng", không báo "không có người" giữa giờ.

### A.2.6 Thuật toán 見守り② — "見守り通知" theo dõi liên tục (`checkMonitoring2`, khi `c003_02` bật)

Ý tưởng: xét **cụm tối đa 3 khung 10 phút sát thời điểm phán đoán** (30 phút gần nhất, cắt theo khung
theo dõi — cùng cơ chế `generate_series` như §A.2.4, chỉ khác mode; `SENSOR_NOTIFY_JUDGMENT_FRAME_NUMBER
= 3`) để tránh báo động giả từ 1 lần đo lẻ.

```
monitorFrameNum = (mốc kết thúc phán đoán (c005 − 10分) − giờ bắt đầu theo dõi) / 10 phút
frameNum        = MIN(SENSOR_NOTIFY_JUDGMENT_FRAME_NUMBER=3, monitorFrameNum)
count           = số bản ghi lấy được trong cụm 3 mốc 判定時刻/−10分/−20分 (≤3, cắt theo khung theo dõi)

├─ count < frameNum  → NOT_APPLICABLE (100)  "chưa đủ dữ liệu để phán đoán"
│
└─ count >= frameNum (và count > 0)
      │
      ├─ có ≥1 bản ghi với tổng đo (c006, 2 phòng cộng) >= SENSOR_NOTIFY_NUMBER_2(=1)
      │     ├─ đúng vào mốc kết thúc phán đoán (c005 − 10分) → MOTION_SENSOR (101) "có người"
      │     └─ khung khác                            → NOT_APPLICABLE (100) (chặn báo giữa giờ)
      │
      ├─ (không rơi vào nhánh trên) có ≥1 bản ghi c006 < 0 (−1 do SQL tự gán cho khung không có bản ghi — khung trống dữ liệu)
      │     → MISSING_DATA (104) "mất dữ liệu liên tục"
      │
      └─ Không khớp nhánh nào ở trên → NO_MOTION_SENSOR (102) "không có người"
```
Nguồn: `WatchNotificationCommand.php:373-427`, hằng số `const.php:704,706`.

**Ghi chú**: biến `$resultCode` trong `checkMonitoring2` được gán `0` làm giá trị "chưa xác định" rồi
so sánh `if ($resultCode != 0)` — nhưng `0` **không phải** 1 trong 5 hằng số trạng thái hợp lệ
(100-104), chỉ là sentinel nội bộ. Kết quả vòng `foreach` độc lập với thứ tự SQL trả về: có ≥1 bản ghi
đạt ngưỡng đúng mốc kết thúc phán đoán → 101 (gán không có guard); chỉ có bản ghi đạt ngưỡng giữa giờ
→ 100 (nhánh `if ($resultCode === 0)` không ghi đè được 101 đã gán).
(`WatchNotificationCommand.php:397-415`)

### A.2.7 Ghi kết quả — `PushMessage` + `ConMessage` ("お知らせ") + update `t_901`

- 6 mẫu thông báo cố định (`ConRegularMessages`, id `'1'`–`'6'`) — **nội dung tiêu đề/message thật
  không đọc được** (dữ liệu nằm trong DB, không phải seed trong source code) — chỉ biết id nào ứng với
  trạng thái nào qua `switch` trong `updateEcoMission()`:

  | id | Điều kiện | Ý nghĩa suy ra từ code |
  |---|---|---|
  | `1` | `MOTION_SENSOR` (見守り①, cấu hình 1 phòng bật) | *(suy đoán)* "có người" — bối cảnh 見守り① |
  | `2` | `NO_MOTION_SENSOR`, 見守り① | *(suy đoán)* "không có người" — 見守り① |
  | `3` | `MOTION_SENSOR`, 見守り② (hoặc cấu hình khác 1) | *(suy đoán)* "có người" — 見守り② |
  | `4` | `NO_MOTION_SENSOR`, 見守り② | *(suy đoán)* "không có người" — 見守り② |
  | `5` | `NO_DATA` (chỉ từ 見守り①) | *(suy đoán)* "không có dữ liệu" |
  | `6` | `MISSING_DATA` — từ §A.2.4 (mọi hộ, cả cấu hình ① lẫn ②) hoặc nhánh khung trống dữ liệu của ② (§A.2.6) | *(suy đoán)* "mất dữ liệu liên tục" |

  (`WatchNotificationCommand.php:223-252`)
- Ghi song song 2 loại bản ghi: `PushMessage` (kind `DATA_KIND_MOTION_ALARM = 'motion_alarm'`,
  `eminel_sv_lib/.../PushMessage.php:36`) và `ConMessage` (phạm vi phân phối `DISTRIBUTE_SCOPE_EMS_SP =
  'EMS_SP'` — gửi đích danh 1 hộ, không broadcast, `.../ConMessage.php:33`).
  (`WatchNotificationCommand.php:257-280`)
- **QUAN SÁT (nghi bug hệ cũ)**: cả 2 lệnh `saveOrFail` nằm **ngoài** vòng `foreach` (sau dấu đóng ở
  `:281`) — mỗi pattern trạng thái chỉ lưu được 1 cặp Push+message của hộ **cuối danh sách**, entity các
  hộ trước bị biến ghi đè; lỗi khi lưu → bắt exception, ghi log thường (không phải `alert`), set
  `$resultCode = false`. (`WatchNotificationCommand.php:228-291`)
- Sau khi lưu thành công → update `t_901.c006` (`setBeforeNoticed`) + `c007` (`setModified`) cho **mọi**
  hộ trong danh sách pattern — kể cả hộ không được lưu Push/message ở trên vẫn bị đánh dấu "đã thông
  báo" — lỗi update thì ghi log `alert` (khác lỗi ghi Push/Message ở trên, mức nghiêm trọng cao hơn).
  (`WatchNotificationCommand.php:294-296,307-333`)

### A.2.8 Điểm đặc biệt / Rủi ro

- Đây là 1 trong nhiều Command trong `conciergesv` ghi log mức `alert` (dùng hằng số PSR-3
  `LogLevel::ALERT`, tương đương chuỗi `'alert'` mà `SendAlertLogMailCommand` quét — xem thêm ở đó) khi
  gặp lỗi nghiêm trọng (`checkValidate` thất bại, lỗi SQL, lỗi update `t_901`). Batch này **cũng nằm
  trong danh sách nguồn phát cảnh báo** cho batch đó, dù trước đây danh sách đã liệt kê ở
  `WatchNotification` chưa từng được kiểm chứng đầy đủ — grep lại cho thấy phạm vi thực tế của cơ chế
  log `alert` rộng hơn nhiều so với 8 file đã liệt kê trước đó (xem cập nhật ở `SendAlertLogMail.md`).
- Phụ thuộc trực tiếp vào `CalcTenMinutesSensorCommand` chạy trước (lệch 5 phút) — nếu batch đó lỗi/trễ,
  `s_101` chưa có dữ liệu mới, `WatchNotificationCommand` sẽ phán đoán dựa trên dữ liệu cũ hoặc thiếu,
  dễ rơi vào nhánh "không có dữ liệu"/"mất dữ liệu liên tục" một cách giả (false positive).
  - 見守り② còn phụ thuộc gián tiếp `getContinuousMissingData` (§A.2.4) chạy trước và có độ ưu tiên cao
    hơn — QUAN SÁT: 2 cơ chế báo "mất dữ liệu" chồng chéo thiết kế trong cùng 1 batch, với ngưỡng khác
    nhau (§A.2.4 cần thiếu đủ 3/3 khung; nhánh khung trống dữ liệu của ② §A.2.6 chỉ cần 1 khung thiếu).
- Không transaction toàn batch — 1 hộ ghi lỗi không ảnh hưởng hộ khác, nhưng cũng không có cách nào
  biết tổng hợp bao nhiêu hộ đã lỗi trong 1 lần chạy (chỉ có log rời rạc từng hộ).

---

# Phần B — Đối chiếu EMINEL-smart (hệ thống mới)

## B.1 Tên batch & vị trí trong code

| Batch/cơ chế | Vị trí (Lambda) | State Machine / trigger | Nguồn dữ liệu | Đích |
|---|---|---|---|---|
| Nhận sự kiện cảm biến IoT + xác định hộ cần push | `src/functions/batch-receive-data-infrared-remote/app.ts` | `BatchReceiveDataInfraredRemoteStateMachine` (`src/statemachine/batch-receive-data-infrared-remote.asl.json`) — **trigger real-time bởi event cảm biến IoT** (payload `event: SENSOR_AUTO_REPORT`/`EXECUTE_AUTOMATION`), không phải cron | Event trực tiếp từ cảm biến IoT của MUI (`payload.motion`, `payload.wbgt`, `payload.temperature`) + `TABLE_KAIIN` (GSI `gsi_house_id` — đổi `houseID` của event thành danh sách `kaiin_bango`, `app.ts:280-293`) | Ghi lịch sử `TABLE_INFRARED_REMOTE_DATA`; đẩy danh sách hộ cần push qua S3 tạm (`createDataSegment`) |
| Gửi push "room monitor" (+ điều khiển thiết bị nếu có lịch) | `src/functions/batch-control-device-and-push-notice-sensor/app.ts` | Bước `Map` (DISTRIBUTED) ngay sau bước trên trong cùng state machine | Đọc lại segment từ S3; đọc `TABLE_USER_SETTING` (cờ `flag_push_notice_room_monitor`) + `TABLE_MOBILE_TOKEN_MANAGEMENT` (token thiết bị di động, `app.ts:261-274`) | `pushNotificationFirebase()` — push trực tiếp tới thiết bị di động qua Firebase, không ghi bảng "message"/app-inbox tương đương `ConMessage` |

| Mục | Nội dung |
|---|---|
| Cách trigger | Event-driven từ cảm biến IoT MUI báo `motion` real-time — **không phải batch cron polling như bản cũ** (không có `s_101`-tương đương, không có cửa sổ 10 phút). |
| Cờ opt-in của user | `flag_push_notice_room_monitor` trong `UserSetting` — mặc định `true` khi tạo/reset tài khoản (`batch-if2241-import-tagtag-kaiin/app.ts:218`, `authorizer/app.ts:112`, `batch-reset-account/app.ts:189`), đổi qua API `api-user/update-user-setting.ts`. Tương đương về vai trò với cờ bật/tắt `c003` của `t_901`, nhưng chỉ có **1 cờ chung**, không có 2 cấu hình khung giờ riêng như bản cũ. |

## B.2 Tổng quát

| Mục | Nội dung |
|---|---|
| **Vai trò** | Khi cảm biến IoT của MUI báo phát hiện chuyển động (`motion === 1`) trong 1 sự kiện auto-report, đẩy push notification "có hoạt động trong phòng" ngay cho hộ đó (nếu đã bật cờ). |
| **Input** | Event `SENSOR_AUTO_REPORT`/`EXECUTE_AUTOMATION` gửi trực tiếp từ cảm biến IoT (không qua bảng DB trung gian kiểu `s_101`). Điều kiện kích hoạt: `payload.motion === 1` (`batch-receive-data-infrared-remote/app.ts:222`). |
| **Output** | Push Firebase, tiêu đề cố định `"お部屋みまもり"`, nội dung cố định `"お部屋での活動を検知しました。"` (`batch-control-device-and-push-notice-sensor/app.ts:110-113`) — **không có bản ghi "お知らせ"/app-inbox tương đương `ConMessage`**, không thấy field lưu "lần thông báo trước" để chống trùng (khác với nhánh 熱中症/heat-stroke trong CÙNG file có throttle `HEAT_STROKE_NOTICE_INTERVAL_MS = 29 phút`, `:35,71-73` — nhánh room-monitor không có throttle tương tự). |
| **Khái quát xử lý** | 1. Cảm biến IoT gửi event `motion`/`wbgt`/`temperature` theo thời gian thực.<br>2. Lambda nhận event, nếu `motion === 1` → đánh dấu hộ cần push `has_push_notice_room_monitor`.<br>3. Chia danh sách hộ thành segment, đẩy qua Step Functions Map (distributed).<br>4. Lambda xử lý từng segment: kiểm tra cờ `flag_push_notice_room_monitor` của user, nếu bật → lấy token thiết bị di động, gửi push Firebase ngay. |

**Khác biệt cốt lõi so với bản cũ** (đủ căn cứ file:line 2 bên, không chỉ nói chung "khác kiến trúc"):

| Khía cạnh | Bản cũ (`WatchNotificationCommand`) | Bản mới (`batch-receive-data-infrared-remote` + `batch-control-device-and-push-notice-sensor`) |
|---|---|---|
| Cơ chế trigger | Cron 10 phút, polling `s_101` đã tổng hợp trước | Event-driven real-time, thẳng từ payload cảm biến, không qua bảng tổng hợp trung gian |
| Phần cứng cảm biến | PIR chuẩn ECHONET qua HEMS-GW (`t_201.c007='001101'`) | Cảm biến riêng của MUI (kèm nhiệt độ/độ ẩm/WBGT trong cùng thiết bị) |
| Số loại thuật toán | 2 (見守り①/② khung giờ + ngưỡng khung riêng, cấu hình theo hộ) | 1 (boolean đơn giản `motion === 1`, không khung giờ, không ngưỡng số khung) |
| Trạng thái "không có người" | Có (`NO_MOTION_SENSOR`, id message 2/4) | **Không tìm thấy** |
| Trạng thái "không có dữ liệu" | Có (`NO_DATA`, id message 5) | **Không tìm thấy** |
| Trạng thái "mất dữ liệu liên tục" | Có, 2 nguồn (§A.2.4 + nhánh khung trống dữ liệu §A.2.6, id message 6) | **Không tìm thấy** |
| Chống thông báo lặp | Có — update `t_901.c006`, dùng lại ở lần chạy sau | **Không tìm thấy** cơ chế throttle cho room-monitor (khác nhánh heat-stroke cùng file có `HEAT_STROKE_NOTICE_INTERVAL_MS`) — *(suy đoán: có thể mỗi lần `motion=1` báo lại 1 lần, chưa xác minh có giới hạn ở tầng khác — vd. Firebase client-side, hoặc tần suất report tự nhiên thấp của cảm biến — ngoài phạm vi source đã đọc)* |
| Bản ghi "お知らせ" trong app | Có (`ConMessage`) | Không tìm thấy — chỉ push, không có mục tương đương trong inbox app |

---

## Tổng kết

**2 thuật toán ở hệ thống cũ khác nhau ở phạm vi thời gian xét, không phải 2 cách tính cho cùng 1 việc:**

- **見守り①** — chỉ xét **1 khung 10 phút** tại thời điểm phán đoán, chỉ báo "không có người"/"không có
  dữ liệu" **đúng lúc kết thúc khung giờ theo dõi**. Hợp tình huống "đến giờ hẹn, kiểm tra 1 lần" (vd.
  "vừa về nhà" — ただいま通知, hoặc thay phiên trông nhà — お留守番代行).
- **見守り②** — xét **cụm tối đa 3 khung 10 phút sát thời điểm phán đoán** (30 phút gần nhất, cắt theo
  khung theo dõi; frameNum = MIN(3, số khung của cửa sổ)) trước khi kết luận, để tránh báo giả từ 1 lần
  đo hụt. Hợp tình huống theo dõi liên tục kéo dài (vd. theo dõi người già cả buổi).
- Không phải hộ tự chọn "cái phù hợp hơn" — code ưu tiên cứng: **công tắc ① (`c003_01`) bật thì luôn
  chạy ①, bất kể công tắc ②**; ② chỉ chạy khi ① tắt. (`dataAssignment()`, if/elseif —
  `WatchNotificationCommand.php:343-364`)

**Hệ thống mới không phải bản gọn của 1 trong 2 thuật toán — mà là thay hẳn bằng cơ chế khác đơn giản
hơn nhiều:**

- Chỉ giữ đúng phần "có động thì báo ngay" (cảm biến báo `motion=1` → push real-time).
- Bỏ hẳn: khung giờ theo dõi (start/end), ngưỡng cụm 3 khung của ②, và cả 3 trạng thái "không có
  người"/"không có dữ liệu"/"mất dữ liệu liên tục" — việc hệ mới có phải tái hiện các phần này hay
  không vẫn là điểm treo chưa quyết (CLD-05).
- Không có cơ chế chống báo lặp lại nhiều lần (khác bản cũ luôn update `t_901.c006` sau khi báo).
- Đánh đổi: mất phần logic phán đoán phức tạp, nhưng được phản hồi real-time thay vì chờ tới chu kỳ
  cron 10 phút.

---

## Nguồn

| Phần | Nội dung | Căn cứ |
|---|---|---|
| Hệ thống cũ | Logic chính | `sources/conciergesv-develop/src/Command/WatchNotificationCommand.php` |
| Hệ thống cũ | Hằng số nghiệp vụ | `sources/conciergesv-develop/config/const.php:198,228,230,694,696,698,700,702,704,706,708,710,712,714,716` |
| Hệ thống cũ | Ý nghĩa cột `t_901` | `sources/eminel_sv_lib-develop/src/Model/Entity/ConMotionSensorNotificationSetting.php` |
| Hệ thống cũ | Ý nghĩa cột `t_201` | `sources/eminel_sv_lib-develop/src/Model/Entity/ConDevice.php` |
| Hệ thống cũ | `PushMessage`/`ConMessage` constants | `sources/eminel_sv_lib-develop/src/Model/Entity/PushMessage.php:36`, `.../ConMessage.php:33` |
| Hệ thống cũ | Lịch chạy (cron) | `docs/02_詳細設計/10_バッチ処理/mng-webap_cron設定_20241029.txt:8-10` |
| Hệ thống mới | Nhận event cảm biến + phân segment | `src/functions/batch-receive-data-infrared-remote/app.ts` |
| Hệ thống mới | Push room-monitor + heat-stroke | `src/functions/batch-control-device-and-push-notice-sensor/app.ts` |
| Hệ thống mới | Orchestrator | `src/statemachine/batch-receive-data-infrared-remote.asl.json` |
| Hệ thống mới | Cờ opt-in & luồng cập nhật | `src/functions/api-user/update-user-setting.ts`, `src/layers/common/nodejs/models/UserSetting.ts` |
