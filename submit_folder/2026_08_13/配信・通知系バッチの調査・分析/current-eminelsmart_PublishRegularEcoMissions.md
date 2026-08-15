# Hệ thống hiện tại — EMINEL-smart（省エネアドバイス配信）

## Tóm tắt

Backend EMINEL-smart hiện tại (`syp-eminelstandard-backend`) **không có bất kỳ batch nào tự động tính điều kiện từ dữ liệu đo/sử dụng để phát lời khuyên tiết kiệm năng lượng** — không có logic nào tương đương "nhiệt độ cài đặt cao", "vẫn còn để sưởi", "dùng gas/điện nhiều hơn trung bình nhóm", "CO2 giảm/không giảm so với năm trước". Cái có sẵn là **hạ tầng phân phối nội dung do admin tự soạn** (`Tip`/`News`/`Survey`) — nhắm đối tượng theo thuộc tính tĩnh hoặc danh sách CSV, không nhắm theo điều kiện tính toán động. Có 1 dấu hiệu cho thấy tính năng "CO2 giảm" từng được dự kiến nhưng chưa triển khai: hằng số `POINT_ACTION.CO2_REDUCTION` được định nghĩa nhưng không được dùng ở bất kỳ đâu khác trong code.

## Tên batch/hàm liên quan & vị trí trong code

| Hàm/Lambda | Vị trí (`src/functions/`) | Vai trò hiện tại | Có phải nghiệp vụ "tính điều kiện từ dữ liệu đo" không |
|---|---|---|---|
| `batch-send-tip-preprocessing` / `batch-send-tip` / `batch-send-tip-complete` | `batch-send-tip*/app.ts` | Gửi 1 "Tip" (エコライフのコツ) do admin đã tạo sẵn tới danh sách người dùng đích | Không — `Tip` là nội dung tĩnh, không có bước tính điều kiện từ dữ liệu đo |
| `batch-send-news*`, `batch-send-survey*` | tương tự, cho News/Survey | Cùng khuôn 3 giai đoạn (preprocessing → send → complete) | Không |
| `checkUserMatchesConditionAttribute` | `business-logic/check-user-matches-condition-attribute.ts` | Lọc đối tượng nhận Tip/News theo **thuộc tính tĩnh**: số người trong hộ, có/không điều hòa, có/không pin mặt trời, hình thức sở hữu nhà, loại hợp đồng (gas/điện/bảo trì), loại tòa nhà, thiết bị đang sở hữu | Không — toàn bộ là thuộc tính khai báo/tra cứu 1 lần, không có ngưỡng tính từ số liệu đo theo thời gian |
| `givePointBadgeForUser` + `POINT_BADGE_FOR.TIP` | `api-user/give-point-badge.ts`, `constants.ts:1340-1358` | Cấp điểm/badge khi user xem 1 Tip | Không |
| `POINT_ACTION.CO2_REDUCTION` | `constants.ts:1306-1311` | Hằng số được định nghĩa (`'co2_reduction'`) nhưng **không có nơi nào khác tham chiếu tới** — dấu hiệu tính năng dự kiến nhưng chưa xây | — |

## Tổng quát

| Mục | Nội dung |
|---|---|
| **Vai trò hiện tại** | Phân phối nội dung **do admin tự soạn** (Tip/News/Survey) tới người dùng theo thuộc tính tĩnh hoặc danh sách CSV — không có nghiệp vụ tự động phát hiện "khách hàng nào cần được nhắc gì" từ dữ liệu đo/sử dụng. |
| **Input** | `TABLE_TIP`/`TABLE_NEWS`/`TABLE_SURVEY` (nội dung do admin nhập tay qua màn hình quản trị) ＋ danh sách đối tượng (toàn bộ / theo thuộc tính tĩnh / CSV chỉ định). Không đọc dữ liệu cảm biến, không đọc lịch sử sử dụng gas/điện, không có bảng trung bình theo nhóm tương đương `ConSensorMonthlyAveValues`. |
| **Output** | Gửi Push notification qua pipeline chung, cấp điểm/badge khi user xem nội dung (`POINT_BADGE_FOR.TIP`...). Không có bảng "nhiệm vụ theo từng khách hàng" (`ConEcoMissionDestinations`) — trạng thái xem lưu theo `TipUserAction`. |
| **Khái quát** | Muốn triển khai lại 19 mission của batch cũ ở E-GW (`F-ES-03`), cần xây **mới hoàn toàn phần tính điều kiện** cho từng loại (đọc dữ liệu đo/nhóm hóa, so sánh ngưỡng/trung bình) — nhưng có thể **tái sử dụng khung phân phối nội dung + cấp điểm/badge đã có** (`Tip`/push pipeline/`givePointBadgeForUser`) làm lớp gửi thông báo cuối cùng, không cần viết lại từ đầu. |

---

## Nguồn

| Nội dung | Căn cứ |
|---|---|
| Pipeline gửi Tip (3 giai đoạn) | `syp-eminelstandard-backend-main/src/functions/batch-send-tip-preprocessing/app.ts`, `batch-send-tip/app.ts`, `batch-send-tip-complete/app.ts` |
| Lọc đối tượng theo thuộc tính tĩnh | `syp-eminelstandard-backend-main/src/layers/common/nodejs/business-logic/check-user-matches-condition-attribute.ts` |
| Cấp điểm/badge khi xem Tip | `syp-eminelstandard-backend-main/src/functions/api-user/give-point-badge.ts`, `src/layers/common/nodejs/variables/constants.ts:1340-1358` (`POINT_BADGE_FOR`) |
| Hằng số "CO2 giảm" chưa dùng tới | `syp-eminelstandard-backend-main/src/layers/common/nodejs/variables/constants.ts:1306-1311` (`POINT_ACTION.CO2_REDUCTION`) — grep toàn repo không thấy nơi nào khác tham chiếu |
| Yêu cầu tương ứng ở E-GW | `eminel_gw_project-main/docs/eminel/3_requirements/00_integrated_requirements_v1.2.md` — `[F-ES-03] 省エネアドバイス` |
