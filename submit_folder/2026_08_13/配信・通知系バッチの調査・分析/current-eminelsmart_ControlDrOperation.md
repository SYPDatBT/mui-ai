# Hệ thống hiện tại — EMINEL-smart（DR 機器制御）

## Tóm tắt

Khác với các batch Xzilla/EcoMission/EcoPoints đã điều tra (không có gì tương đương), **EMINEL-smart đã có sẵn 1 nghiệp vụ DR điều khiển thiết bị hoàn chỉnh và rộng hơn** `ControlDrOperationCommand` về số loại thiết bị: Eco Jozu (Rinnai/Noritz — qua API cloud hãng), điều hòa (qua MUI hồng ngoại **hoặc** Daikin cloud), quạt sưởi/fan convector (MUI hồng ngoại) — so với batch cũ chỉ điều khiển đúng 1 loại (đơn vị điều khiển sưởi qua ECHONET Lite/GW). Khác biệt kiến trúc quan trọng: **e-smart điều khiển thiết bị bằng cách gọi trực tiếp API cloud của hãng** (Rinnai/Noritz/Daikin) hoặc dịch vụ hồng ngoại MUI — **không đi qua GW nội bộ nào cả**, vì thiết bị e-smart hỗ trợ kết nối thẳng lên cloud hãng qua Wi-Fi. Thiết bị của **E-GW** (multi sensor, đơn vị điều khiển sưởi qua Wi-SUN HAN/ECHONET Lite) thì buộc phải đi qua **GW quản lý cloud** (IF-02/07) — nên phần "gửi lệnh xuống thiết bị" của e-smart không áp dụng thẳng được, nhưng **toàn bộ phần điều phối DR (lưu trạng thái trước → điều khiển → khôi phục sau khi hết hạn → cấp điểm/badge → thông báo)** là khung có sẵn, có thể mở rộng thêm 1 nhánh thiết bị mới thay vì viết lại từ đầu.

## Tên batch/hàm liên quan & vị trí trong code

| Hàm/Lambda | Vị trí (`src/functions/`) | Vai trò |
|---|---|---|
| `batch-start-dr` (+ `-preprocessing`) | `batch-start-dr/app.ts` | Tại thời điểm DR bắt đầu: với từng user tham gia, **lưu lại trạng thái thiết bị trước khi điều khiển** rồi gửi lệnh điều khiển theo cấu hình DR (`control_setting`) |
| `batch-end-dr` (+ `-preprocessing`) | `batch-end-dr/app.ts` | Tại thời điểm DR kết thúc: **khôi phục thiết bị về trạng thái đã lưu** (tắt trước, mở sau — theo đúng thứ tự `offDevices` rồi `onDevices`); cấp điểm/badge tham gia DR nếu cấu hình có (`givePointBadgeForUser`, khớp `POINT_BADGE_FOR.DR`) |
| `controlDevice` (dùng chung DR + Automation) | `src/layers/common/nodejs/business-logic/control-device.ts` | Hàm điều khiển thiết bị thực tế — switch theo `server_type`: `RINNAI`/`NORITZ`/`DAIKIN` (gọi API cloud hãng qua token riêng từng user) hoặc `MUI_CLOUD` (qua dịch vụ hồng ngoại nội bộ MUI) |
| `create-dr.ts` / `update-dr.ts` | `src/functions/api-dr/` | Tạo/sửa lịch DR — **tự đăng ký EventBridge Scheduler bắn đúng giờ bắt đầu/kết thúc** (one-shot), không polling mỗi phút như hệ cũ |

**Thiết bị được hỗ trợ điều khiển DR hiện tại**: Eco Jozu (sàn/panel heater qua Rinnai hoặc Noritz), điều hòa (qua Daikin cloud hoặc qua MUI hồng ngoại), fan convector (MUI hồng ngoại). **Chưa thấy**: Koremo, pin lưu điện, Eco-Cute, máy nước nóng hybrid (đều có trong danh sách yêu cầu F-ES-07/08 nhưng ngoài phạm vi 3 nhóm trên).

## Tổng quát

| Mục | Nội dung |
|---|---|
| **Vai trò hiện tại** | Điều khiển bật/tắt/đổi nhiệt độ thiết bị sưởi/điều hòa theo lịch DR, khôi phục trạng thái sau khi hết hạn, cấp điểm/badge, thông báo push (`batch-push-notice-dr-*`). |
| **Input** | `TABLE_DR` (cấu hình DR: `control_setting` theo từng loại thiết bị, `point_quantity`, `has_badge`) ＋ `TABLE_DEVICE`/`TABLE_MUI_DEVICE` (thiết bị của user) ＋ token tích hợp riêng từng hãng (Rinnai/Noritz/Daikin, `getIntegrationSettingInfo`). |
| **Output** | Gọi API cloud hãng (Rinnai/Noritz/Daikin) hoặc dịch vụ hồng ngoại MUI để điều khiển thật ＋ `TABLE_DR_USER_ACTION.pre_control_status` (trạng thái trước điều khiển, dùng để khôi phục) ＋ điểm/badge qua `givePointBadgeForUser`. |
| **Khái quát xử lý** | 1. Tạo/sửa DR qua `api-dr` → tự đăng ký EventBridge Scheduler bắn đúng giờ bắt đầu/kết thúc (không polling).<br>2. Lúc bắt đầu (`batch-start-dr`): với mỗi user, lấy thiết bị theo loại (Eco Jozu/điều hòa/fan convector), **lưu trạng thái hiện tại**, rồi điều khiển theo `control_setting` (ON/OFF/đổi nhiệt độ).<br>3. Lúc kết thúc (`batch-end-dr`): đọc lại trạng thái đã lưu, **khôi phục** thiết bị (tắt trước, mở sau), cấp điểm/badge nếu có cấu hình. |

### So sánh nhanh với `ControlDrOperationCommand` (hệ cũ)

| | Hệ cũ | Hệ mới |
|---|---|---|
| Phạm vi thiết bị | Chỉ 1 loại: đơn vị điều khiển sưởi (ECHONET Lite, qua GW) | 3 nhóm: Eco Jozu (Rinnai/Noritz), điều hòa (Daikin/MUI hồng ngoại), fan convector (MUI hồng ngoại) — chưa có Koremo/pin lưu điện/Eco-Cute |
| Đường truyền lệnh | ECHONET Lite → `Instructions` → `hemssv` → GW → thiết bị | Gọi trực tiếp API cloud hãng (Rinnai/Noritz/Daikin) hoặc dịch vụ hồng ngoại MUI — **không qua GW nào** |
| Cách kết thúc | Phase 2 riêng (ON/OFF) hoặc nhúng sẵn giờ kết thúc vào lệnh ECHONET (CHANGE_TEMP) | Lưu trạng thái trước → khôi phục đúng trạng thái đó lúc kết thúc (không nhúng giờ vào lệnh thiết bị) |
| Cơ chế trigger | Polling mỗi phút, so `start_at`/`end_at` | EventBridge Scheduler bắn đúng giờ (one-shot), không polling |
| Cấp điểm/thông báo | `ConMessages` (category=DR, chỉ báo "đã bắt đầu") | `givePointBadgeForUser` (điểm/badge) + `batch-push-notice-dr-*` (thông báo bắt đầu/kết thúc riêng) |
| **Có áp dụng được cho thiết bị E-GW không?** | — | **Không trực tiếp** — thiết bị E-GW đi qua GW quản lý cloud (IF-02/07, MQTT), không phải API cloud hãng/MUI hồng ngoại. Cần thêm 1 nhánh `server_type` mới trong `controlDevice()` gọi qua GW quản lý cloud, tái dùng phần lưu/khôi phục trạng thái + điểm/badge + thông báo sẵn có |

---

## Nguồn

| Nội dung | Căn cứ |
|---|---|
| Điều khiển lúc bắt đầu DR | `syp-eminelstandard-backend-main/src/functions/batch-start-dr/app.ts` |
| Khôi phục + cấp điểm lúc kết thúc DR | `syp-eminelstandard-backend-main/src/functions/batch-end-dr/app.ts` |
| Hàm điều khiển thiết bị dùng chung (DR + Automation) | `syp-eminelstandard-backend-main/src/layers/common/nodejs/business-logic/control-device.ts` |
| Tạo lịch DR + đăng ký EventBridge Scheduler | `syp-eminelstandard-backend-main/src/functions/api-dr/create-dr.ts`, `update-dr.ts` |
| Yêu cầu tương ứng ở E-GW | `eminel_gw_project-main/docs/eminel/3_requirements/00_integrated_requirements_v1.2.md` — `[F-ES-07/08] 機器制御DR`, UC-05 01-3 |
