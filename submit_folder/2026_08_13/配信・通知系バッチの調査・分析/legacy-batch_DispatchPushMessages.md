# Batch cũ — DispatchPushMessagesCommand（プッシュ通知メッセージ送信）

## Tóm tắt

`DispatchPushMessagesCommand` là **"chặng cuối" gửi Push notification thật** trong hệ thống cũ — chạy **mỗi phút** (cron `* * * * *`), quét bảng `PushMessageDestinations` lấy các dòng đã lên lịch (`status=SCHEDULED`) đúng vào phút hiện tại, kiểm tra hợp lệ, rồi gửi hàng loạt qua 1 service nội bộ tên `PushCore` (không gọi thẳng Firebase). Đây là nơi **mọi batch khác** (ví dụ `PublishRegularEcoMissionsCommand`, `WatchNotificationCommand`...) hội tụ về — các batch đó chỉ **ghi lịch gửi** vào `PushMessageDestinations`, còn việc gửi thật do batch này đảm nhiệm. Có cơ chế retry tối đa 5 lần, cách nhau 3 phút, nhưng cách phân trang (offset) có nguy cơ **bỏ sót vĩnh viễn** một số thông báo nếu 1 phút có hơn 500 thông báo cần gửi; chi tiết ở Phần 2.

## Phần 1 — Tổng quát

| Mục | Nội dung |
|---|---|
| **Vai trò** | Gửi Push notification thật cho các bản ghi đã lên lịch đúng phút hiện tại; xử lý retry khi gửi thất bại. |
| **Input** | `PushMessageDestinations` (lịch gửi, trạng thái, số lần thất bại) join `PushMessages` (nội dung, khung thời gian hiệu lực) join `PushDeviceTokens`/`PushFcmTopics` (nơi gửi tới — 1 thiết bị cụ thể hoặc 1 topic FCM chung). |
| **Output** | Gọi API nội bộ `PushCore` (`POST {PushCore.Api.host}/v2/send-messages`) — cập nhật lại `status`/`schedule`/`failure_count` của từng `PushMessageDestinations` theo kết quả gửi. |
| **Khái quát xử lý** | 1. Xác định khung 1 phút hiện tại (`[now:phút, now:phút+1)`).<br>2. Lấy các destination `SCHEDULED` có `schedule` rơi vào khung đó **và** `PushMessage` cha đang trong thời hạn hiệu lực, theo lô 500.<br>3. Loại bỏ destination không hợp lệ (thiếu nội dung, thiếu/thừa đích đến).<br>4. Gửi lô còn lại qua `PushCore`, cập nhật kết quả từng dòng (thành công / thử lại / hết lượt thử). |

## Phần 2 — Chi tiết

### Bản đồ xử lý

```
BƯỚC 1  Xác định khung 1 phút   → [now:phút, now:phút+1)                          §2.1
BƯỚC 2  Lấy lô 500 destination  → SCHEDULED + đúng khung + PushMessage còn hiệu lực §2.2
BƯỚC 3  Lọc bỏ destination lỗi  → thiếu nội dung / thiếu-thừa đích đến             §2.3
BƯỚC 4  Build payload & gửi     → gộp tối đa 500 message/request, gọi PushCore     §2.4
BƯỚC 5  Cập nhật kết quả        → thành công / retry (tối đa 5 lần, cách 3 phút) / hết lượt §2.5
        Lặp lại BƯỚC 2-5 với offset tăng dần cho tới khi hết dữ liệu              §2.6 ⚠️
```

| Bước | Nội dung | Chi tiết ở |
|---|---|---|
| 1 | Xác định khung thời gian xử lý | §2.1 |
| 2 | Truy vấn destination cần gửi | §2.2 |
| 3 | Loại bỏ destination không hợp lệ | §2.3 |
| 4 | Gửi qua `PushCore` | §2.4 |
| 5 | Xử lý kết quả, retry | §2.5 |
| — | Vòng lặp phân trang — điểm bất thường | §2.6 |

---

### 2.1 Khung thời gian xử lý & tham số chạy lại

| Mục | Nội dung |
|---|---|
| Lịch chạy | Cron `* * * * *` — **mỗi phút** ([mng-webap_cron設定_20241029.txt:80](e:/Projects/mui/legacy_eminel_docs-main/docs/02_詳細設計/10_バッチ処理/mng-webap_cron設定_20241029.txt#L80)) |
| Khung xử lý | `startAt = now (giữ nguyên giờ:phút)`, `endAt = startAt + 1 phút` ([:59-60](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/DispatchPushMessagesCommand.php#L59-L60)) |
| Tham số chạy lại | `send_time` — **không có tác dụng** (xem ⚠️①) |

### 2.2 Truy vấn destination cần gửi

Một truy vấn duy nhất, lặp theo trang 500 dòng ([:67-85](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/DispatchPushMessagesCommand.php#L67-L85)):

| Điều kiện | Ý nghĩa |
|---|---|
| `PushMessageDestinations.status = SCHEDULED` (`0`) | Chưa gửi / đang chờ gửi lại |
| `PushMessageDestinations.schedule` trong khung 1 phút hiện tại | Đúng thời điểm cần gửi (thời điểm này do batch tạo lịch, ví dụ `PublishRegularEcoMissionsCommand`, đặt sẵn) |
| `matching PushMessages`: `start_at < endAt` **và** `end_at >= startAt` | `PushMessage` cha (nội dung) vẫn còn trong khung hiệu lực riêng của nó (ví dụ mission có hiệu lực 30 ngày kể từ lúc phát — xem tài liệu `PublishRegularEcoMissionsCommand`) — đây là **điều kiện thứ 2, độc lập** với lịch gửi của destination |

### 2.3 Loại bỏ destination không hợp lệ

Với mỗi destination lấy được, kiểm tra 2 nhóm lỗi trước khi gửi ([:90-120](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/DispatchPushMessagesCommand.php#L90-L120)):

| Lỗi | Điều kiện |
|---|---|
| Không có nội dung | `title`, `body`, `data` của `PushMessage` đều rỗng |
| Thiếu đích đến | Không có cả `push_device_token` lẫn `push_fcm_topic` |
| Thừa đích đến | Có **cả** `push_device_token` lẫn `push_fcm_topic` cùng lúc (đáng lẽ loại trừ lẫn nhau — xem validate ở `PushMessageDestinationsTable`) |

Destination lỗi → set `status = INVALID` (`-2`), lưu ngay, tính vào `failureCount`, và **không** được gửi ở bước sau.

### 2.4 Build payload & gửi qua `PushCore`

- Mỗi destination hợp lệ → 1 message `{title, body, data?, registrationToken hoặc topic}` ([:127-147](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/DispatchPushMessagesCommand.php#L127-L147)).
- Gửi cả lô (tối đa 500) trong 1 lần gọi `PushMessage->sendMessages()` ([:152](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/DispatchPushMessagesCommand.php#L152)) — implementation thật (`PushMessageService`) gọi `POST {PushCore.Api.host}/v2/send-messages` (mặc định `http://localhost:54650`, [push_message.php:4-8](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/config/push_message.php#L4-L8)) — **không gọi thẳng Firebase**, mà qua 1 service nội bộ trung gian, tự chia nhỏ tiếp thành từng lô 500 nếu vượt quá ([PushMessageService.php:81](e:/Projects/mui/legacy_eminel_docs-main/sources/eminel_sv_lib-develop/src/StaticServices/PushMessageService.php#L81)).
- `data` (nếu có) mang `kind` để app biết loại thông báo: `message`, `survey`, `dev_ctrl`, `motion_alarm`, `eco_mission`, `plus_point` ([PushMessage.php:25-38](e:/Projects/mui/legacy_eminel_docs-main/sources/eminel_sv_lib-develop/src/Model/Entity/PushMessage.php#L25-L38)).

### 2.5 Xử lý kết quả & retry

| Kết quả | Hành vi |
|---|---|
| Gửi thành công (`responseItem['success']`) | `status = COMPLETED` (`1`) ([PushMessageDestination.php:44-47](e:/Projects/mui/legacy_eminel_docs-main/sources/eminel_sv_lib-develop/src/Model/Entity/PushMessageDestination.php#L44-L47)) |
| Gửi thất bại (từng dòng, hoặc cả request lỗi/exception) | `failure_count += 1`; nếu `< maxFailureCount` (**5**) → đặt lại `schedule = now + retryIntervalMinutes` (**3 phút**) để thử lại; ngược lại → `status = OVER_RETRIED` (`-1`), dừng hẳn ([PushMessageDestination.php:58-66](e:/Projects/mui/legacy_eminel_docs-main/sources/eminel_sv_lib-develop/src/Model/Entity/PushMessageDestination.php#L58-L66), tham số ở [push_message.php:9-14](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/config/push_message.php#L9-L14)) |
| Cả request lỗi (exception, ví dụ `PushCore` không phản hồi) | **Toàn bộ** destination trong lô đó bị coi là thất bại — áp dụng retry như trên ([:164-169](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/DispatchPushMessagesCommand.php#L164-L169)) |

### 2.6 Vòng lặp phân trang — nguồn của ⚠️②

```php
$limit = 500; $offset = 0;
while (true) {
    $query = ...->limit($limit)->offset($offset);   // điều kiện WHERE giữ nguyên suốt vòng lặp
    $destinations = $query->all()->toList();
    if (empty($destinations)) break;
    // ... xử lý, đổi status/schedule của TOÀN BỘ destination vừa lấy ...
    $offset += $limit;                                // luôn cộng thêm, không reset về 0
}
```

Vấn đề: sau khi xử lý xong 1 trang, **mọi** destination trong trang đó đổi trạng thái (khỏi `SCHEDULED`) hoặc đổi `schedule` sang **ngoài khung 1 phút hiện tại** — nghĩa là chúng **không còn khớp điều kiện WHERE nữa**. Tập kết quả khớp điều kiện co lại đúng bằng số dòng vừa xử lý, nhưng `$offset` vẫn tăng thêm `500` cho lần lặp sau — xem chi tiết ⚠️②.

---

### ⚠️ Điểm bất thường của hệ cũ

**① Tham số `send_time` không có tác dụng — do khai sai kiểu tham số.** `buildOptionParser` chỉ khai `send_time` như 1 **option** (`->addOption('send_time')`, [:45-47](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/DispatchPushMessagesCommand.php#L45-L47)), nhưng `execute()` lại đọc bằng `$args->getArgument('send_time')` — hàm đọc **argument** (tham số vị trí), không phải option ([:55](e:/Projects/mui/legacy_eminel_docs-main/sources/conciergesv-develop/src/Command/DispatchPushMessagesCommand.php#L55)). Vì không có `addArgument('send_time')` nào được khai, `getArgument('send_time')` luôn trả về `null` — nhánh ghi đè `$now` **không bao giờ chạy**, batch luôn xử lý theo giờ hệ thống thật dù có truyền `--send_time=...` hay không. Cùng dạng lỗi "tham số test không hoạt động" đã gặp ở `DistributeMonthlyEcoPointsCommand` (`--datetime`).

**② Phân trang bằng offset có thể bỏ sót vĩnh viễn thông báo nếu 1 phút có > 500 destination.** Vì mỗi trang xử lý xong sẽ làm **toàn bộ** destination trong trang đó biến mất khỏi tập kết quả khớp điều kiện (đổi status hoặc dời `schedule` ra khỏi khung 1 phút), nhưng `offset` vẫn cộng thêm 500 mỗi vòng lặp — lần truy vấn kế tiếp sẽ **bỏ qua** đúng số dòng lẽ ra là "trang tiếp theo thật sự" của tập đã co lại. Ví dụ cụ thể với 1200 destination khớp điều kiện, limit 500:
  - Lượt 1 (`offset=0`): xử lý 500 dòng đầu → cả 500 dòng rời khỏi tập khớp điều kiện. Còn lại 700 dòng chưa xử lý.
  - Lượt 2 (`offset=500`): trên tập còn 700 dòng, offset 500 bỏ qua 500 dòng đầu (chính là 500 dòng lẽ ra cần xử lý), chỉ lấy 200 dòng cuối → xử lý xong còn lại **500 dòng chưa từng được truy vấn tới**.
  - Lượt 3 (`offset=1000`): tập chỉ còn 500 dòng, offset 1000 vượt quá → trả về rỗng → vòng lặp dừng.
  - **Kết quả: 500 destination vẫn ở trạng thái `SCHEDULED` với `schedule` đã là quá khứ (thuộc phút vừa xử lý) — các lần chạy tiếp theo (khung phút mới) sẽ không bao giờ khớp lại `schedule` này nữa** (vì điều kiện là `schedule` nằm trong khung phút *hiện tại*, còn `schedule` cũ đã trôi vào quá khứ), nên các thông báo đó **không bao giờ được gửi**, cũng không báo lỗi ở đâu.
  - Chỉ xảy ra khi 1 phút có nhiều hơn 500 destination cần gửi cùng lúc (ví dụ nhiều mission/broadcast trùng giờ phát).

---

## Nguồn

| Nội dung | Căn cứ |
|---|---|
| Logic chính của batch | `sources/conciergesv-develop/src/Command/DispatchPushMessagesCommand.php` |
| Lịch cron (mỗi phút) | `docs/02_詳細設計/10_バッチ処理/mng-webap_cron設定_20241029.txt:80` |
| Tham số retry (`maxFailureCount`, `retryIntervalMinutes`) | `sources/conciergesv-develop/config/push_message.php` |
| Entity + trạng thái/retry `PushMessageDestination` | `sources/eminel_sv_lib-develop/src/Model/Entity/PushMessageDestination.php` |
| Entity + cấu trúc `PushMessage` (`data.kind`) | `sources/eminel_sv_lib-develop/src/Model/Entity/PushMessage.php`, `src/Model/Table/PushMessagesTable.php` |
| Service gửi thật qua `PushCore` | `sources/eminel_sv_lib-develop/src/StaticServices/PushMessageService.php` |
