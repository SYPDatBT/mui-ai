# Hệ thống hiện tại — EMINEL-smart（Push通知送信）

## Tóm tắt

Khác với 3 batch đã điều tra trước (`DistributeMonthlyEcoPointsCommand`, `PublishRegularEcoMissionsCommand`, và các batch Xzilla) — phần này **EMINEL-smart đã có sẵn cơ chế gửi Push notification hoàn chỉnh**, gọi trực tiếp Firebase Admin SDK (không qua service trung gian như `PushCore` của hệ cũ). Kiến trúc khác cơ bản: hệ cũ có 1 **bảng lịch gửi chung** (`PushMessageDestinations`) và 1 **dispatcher chạy mỗi phút** quét bảng đó; hệ mới **không có bảng lịch/dispatcher chung** — mỗi loại nội dung (Tip/News/Survey/DR) tự chạy state machine riêng, build danh sách người nhận rồi gọi gửi **ngay**, không polling theo lịch cố định.

## Tên batch/hàm liên quan & vị trí trong code

| Hàm/Lambda | Vị trí (`src/functions/`) | Vai trò |
|---|---|---|
| `batch-push-notice` | `batch-push-notice/app.ts` | Nhận 1 segment người nhận (từ S3, do preprocessing tạo sẵn), gọi gửi cho từng user |
| `pushNoticeToUser` | `src/layers/common/nodejs/services/push-notice-to-user.ts` | Kiểm tra **cờ bật/tắt thông báo theo từng loại** (`TARGET_SCREEN_PUSH_NOTICE`) của user, lấy toàn bộ mobile token (nhiều thiết bị/user), gửi song song tối đa 100 request cùng lúc (`p-limit`) |
| `pushNotificationFirebase` / `getFirebaseAdmin` | `src/layers/common/nodejs/services/push-notification-firebase.ts` | Gọi trực tiếp `firebaseAdmin.messaging().send()` — 1 request/1 token; tự cắt ngắn nội dung nếu vượt giới hạn byte của FCM; xoá token khỏi DB nếu FCM báo token không hợp lệ/hết hạn |
| `batch-push-notice-tip-new-preprocessing` / `-dr-*-preprocessing` / `-news-new-preprocessing` / `-survey-new-preprocessing` | `batch-push-notice-*-preprocessing/app.ts` | Build danh sách người nhận cho từng loại nội dung, chia segment lên S3, kích hoạt `BatchPushNoticeMap` |

**State machine điều phối** (ví dụ `batch-push-notice-tip-new.asl.json`): `Preprocessing → Map (MaxConcurrency=5, DISTRIBUTED) → BatchPushNotice` cho từng segment. Không có bước "Retry" khai báo trong state machine, và code Lambda cũng chỉ log lỗi (`logErrorBatch`) rồi bỏ qua — không tự đặt lại lịch gửi lại như hệ cũ.

## Tổng quát

| Mục | Nội dung |
|---|---|
| **Vai trò** | Gửi Push notification thật qua Firebase, cho từng loại nội dung (Tip/News/Survey/DR...), có kiểm tra cờ bật/tắt theo loại và dọn token không hợp lệ. |
| **Input** | Danh sách người nhận + nội dung đã build sẵn trên S3 (do preprocessing của từng loại nội dung tạo) ＋ `TABLE_MOBILE_TOKEN_MANAGEMENT` (token theo user, nhiều thiết bị) ＋ `TABLE_USER_SETTING` (cờ bật/tắt thông báo theo `target_screen`: Tip/Survey/News/DR/lỗi thiết bị/giám sát phòng/cảnh báo sốc nhiệt). |
| **Output** | Gọi Firebase Admin SDK gửi từng message tới từng token; xoá `TABLE_MOBILE_TOKEN_MANAGEMENT` nếu token không hợp lệ. **Không có** bảng trạng thái gửi kiểu `PushMessageDestinations` (thành công/thất bại/số lần thử) — thành/bại chỉ thể hiện qua log. |
| **Khái quát xử lý** | 1. Mỗi loại nội dung (Tip/News/Survey/DR) tự có state machine riêng: preprocessing build danh sách người nhận → chia segment → gọi `batch-push-notice` song song.<br>2. Với mỗi user trong segment: kiểm tra cờ bật/tắt theo loại nội dung, bỏ qua nếu tắt.<br>3. Lấy tất cả token của user, gửi Firebase trực tiếp cho từng token, giới hạn 100 request đồng thời toàn hệ thống.<br>4. Lỗi từng token: nếu do token hết hạn/không hợp lệ → xoá token; lỗi khác → chỉ log, **không retry lại**. |

### So sánh nhanh với `DispatchPushMessagesCommand` (hệ cũ)

| | Hệ cũ | Hệ mới |
|---|---|---|
| Nơi gửi thật | Qua service nội bộ `PushCore` (HTTP) | Gọi trực tiếp Firebase Admin SDK |
| Cơ chế trigger | 1 dispatcher chung, polling mỗi phút theo bảng lịch (`PushMessageDestinations`) | Mỗi loại nội dung tự trigger ngay khi preprocessing xong (không polling theo lịch cố định) |
| Retry khi gửi thất bại | Có — tối đa 5 lần, cách nhau 3 phút, lưu trạng thái từng đích | **Không có** — lỗi chỉ log, không gửi lại |
| Bật/tắt theo loại thông báo | Không thấy trong code đã đọc | **Có** — `TABLE_USER_SETTING` theo từng `target_screen` |
| Dọn token chết | Không thấy | **Có** — tự xoá token khi Firebase báo không hợp lệ |
| Đa thiết bị/user | Có (`push_device_token` theo `ems_sp`) | Có (`TABLE_MOBILE_TOKEN_MANAGEMENT` theo `user_id`) |

---

## Nguồn

| Nội dung | Căn cứ |
|---|---|
| Lambda gửi chính | `syp-eminelstandard-backend-main/src/functions/batch-push-notice/app.ts` |
| Logic chọn user, kiểm tra cờ bật/tắt, đa thiết bị | `syp-eminelstandard-backend-main/src/layers/common/nodejs/services/push-notice-to-user.ts` |
| Gọi Firebase Admin SDK + dọn token chết | `syp-eminelstandard-backend-main/src/layers/common/nodejs/services/push-notification-firebase.ts` |
| State machine điều phối (ví dụ Tip) | `syp-eminelstandard-backend-main/src/statemachine/batch-push-notice-tip-new.asl.json` |
| Yêu cầu tương ứng ở E-GW | `eminel_gw_project-main/docs/eminel/3_requirements/app/D03_push.md` (受信の制御 — bật/tắt theo loại, khớp đúng cơ chế đã có ở hệ mới), `00_integrated_requirements_v1.2.md` — `[F-AD-07] Push通知管理` |
