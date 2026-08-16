# Hệ thống hiện tại — EMINEL-smart（エコ暖房ポイント）

## Tóm tắt

Backend EMINEL-smart hiện tại (`syp-eminelstandard-backend`) **không có batch nào đánh giá nhiệt độ cài đặt sưởi trung bình hàng tháng để cấp điểm** — không có bảng, không có logic tổng hợp nhiệt độ theo tháng, không có lý do cấp điểm (`POINT_BADGE_FOR`) nào theo ngưỡng nhiệt độ cài đặt (chỉ có mục checklist thao tác/kết nối thiết bị sưởi như 「暖房機器の操作」). Tuy nhiên, phần **hạ tầng gọi Point Infinity để cấp điểm thật** (tương đương `PointInfinity::givePoints()` của batch cũ) **đã có sẵn** dưới dạng 1 Lambda dùng chung (`give-point-to-point-infinity`), hiện đang được luồng cấp điểm/badge dùng chung `givePointBadgeForUser` và các batch (hoàn thành DR, v.v.) gọi tới — không luồng nào tính theo nhiệt độ.

## Tên hàm liên quan & vị trí trong code

| Hàm/Lambda | Vị trí (`src/functions/`) | Vai trò hiện tại | Có phải nghiệp vụ eco-heating không |
|---|---|---|---|
| `GivePointToPointInfinityFunction` | `give-point-to-point-infinity/app.ts` | Lambda dùng chung, nhận `event` chứa các field ghi đè (`JIYU_CD`, `JIYU_DET_CD`, `FUYO_PT`, `FUYO_RIYU`...) rồi gọi API Point Infinity — tương đương `sendToPointInfinity()` của batch cũ | Không — chỉ là hạ tầng gọi API, không tự quyết định điều kiện cấp điểm |
| `GetPointQuantityFromPointInfinityFunction` | `get-point-quantity-from-point-infinity/app.ts` | Lấy số điểm hiện có từ Point Infinity | Không liên quan |
| `give-point-badge.ts` (`api-user`) + `givePointBadgeForUser` | `api-user/give-point-badge.ts` | Cấp điểm/badge theo `POINT_BADGE_FOR` (đăng nhập, tham gia DR, xem tip, trả khảo sát, ký hợp đồng gas/điện/bảo trì, hoàn thành checklist...) — ghi bảng nội bộ (`PointBadgeStats`/`UserBadgeSummary`) **và** gọi Point Infinity cấp điểm thật qua Lambda dùng chung, có rollback khi PI lỗi | Không — không có lý do nào cấp điểm theo ngưỡng nhiệt độ cài đặt |

**Nơi gọi `GivePointToPointInfinityFunction` hiện tại**: Lambda được invoke từ luồng cấp điểm/badge dùng chung `givePointBadgeForUser` (layer `give-point-badge-for-user.ts:364-367`) — dùng cho toàn bộ API stack (give-point-badge, read-tip, answer-survey, first-login-in-month, action-tip...; `template.yaml:3123` truyền ARN vào nested stack, `template-api.yaml:202` gán biến `LAMBDA_GIVE_POINT_TO_POINT_INFINITY`) — và 2 batch `BatchEndDrFunction` (cấp điểm khi hoàn thành DR), `BatchUpdateSelectingPlaceNoFunction` cũng gọi **gián tiếp** qua chính layer này. Không luồng nào liên quan tới nhiệt độ cài đặt sưởi.

## Tổng quát

| Mục | Nội dung |
|---|---|
| **Vai trò hiện tại** | Không có nghiệp vụ "cấp điểm theo nhiệt độ cài đặt sưởi trung bình tháng". Chỉ có hạ tầng cấp điểm Point Infinity dùng chung cho các lý do khác. |
| **Input** | Không có — không có bảng nào lưu nhiệt độ cài đặt sưởi trung bình theo tháng ở EMINEL-smart hiện tại. |
| **Output** | Không có bảng sổ điểm nội bộ tương đương `ConEcoPoints` (`s_141`) của hệ cũ. Điểm/badge hiện tại lưu theo `POINT_BADGE_FOR` (không có mục theo ngưỡng nhiệt độ). |
| **Khái quát** | Muốn triển khai lại nghiệp vụ này ở E-GW (theo yêu cầu `F-ES-04`), chỉ cần xây **mới**: batch tổng hợp nhiệt độ cài đặt sưởi trung bình theo tháng và logic xét ngưỡng. Chống cấp trùng theo tháng (khoá `pointBadgeStatsSk` qua `checkUserHasReceivedPoint`), sổ điểm nội bộ (`PointBadgeStats`/`UserBadgeSummary`) và rollback khi PI lỗi **đã có sẵn** trong luồng dùng chung `givePointBadgeForUser` — có thể **tái sử dụng** cùng `GivePointToPointInfinityFunction` làm bước gọi Point Infinity cuối cùng, không cần viết lại. Lưu ý theo `10_feature_list`, khối ポイント管理・PI連携 (`F-ES-09`) và ポイント・省エネアドバイス phía app đang 劣後 (✅) — thời điểm triển khai cần xác nhận ưu tiên với mui/Kitagas. |

---

## Nguồn

| Nội dung | Căn cứ |
|---|---|
| Lambda cấp điểm Point Infinity dùng chung | `syp-eminelstandard-backend/src/functions/give-point-to-point-infinity/app.ts` |
| Nơi gọi Lambda này hiện tại | `syp-eminelstandard-backend/template.yaml:3123`, `template-api.yaml:202`, `src/layers/common/nodejs/business-logic/give-point-badge-for-user.ts:364-367` (biến `LAMBDA_GIVE_POINT_TO_POINT_INFINITY`) |
| Danh sách lý do cấp điểm/badge nội bộ hiện có (`POINT_BADGE_FOR`) | `syp-eminelstandard-backend/src/layers/common/nodejs/variables/constants.ts:1340-1358` |
| Logic cấp điểm/badge theo hợp đồng (không liên quan nhiệt độ) | `syp-eminelstandard-backend/src/functions/api-user/give-point-badge.ts` |
| Yêu cầu tương ứng ở E-GW | `eminel_gw_project/docs/eminel/3_requirements/00_integrated_requirements_v1.2.md` — `[F-ES-04] エコ暖房ポイント`, `[F-ES-09]` (ví dụ hành động cấp điểm "目標値の達成（暖房設定温度が推奨温度以下等）") |
| Trạng thái ưu tiên (劣後 ✅) của khối point | `eminel_gw_project/docs/eminel/1_product/10_feature_list.md:93,95,130` |
