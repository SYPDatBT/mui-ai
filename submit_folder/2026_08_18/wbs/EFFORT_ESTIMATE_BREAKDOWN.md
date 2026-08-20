# Ước lượng công số chi tiết — Tái cấu trúc `syp-eminelstandard-app`

### Task 1 — Setup workspace + move E-Smart vào `apps/e-smart-app`

| # | Đầu mục con | Công số (md) |
|---|---|---|
| 1.1 | Tạo cấu trúc gốc: `apps/`, `packages/`, `melos.yaml` (glob theo kurashi), `.fvm/fvm_config.json` ở root | 0.15 |
| 1.2 | Move toàn bộ `lib/`, `android/`, `ios/`, `pubspec.yaml`, `test/` hiện tại vào `apps/e-smart-app/`, giữ nguyên cấu trúc bên trong | 0.15 |
| 1.3 | Sửa `pubspec.yaml` (giữ tên package `eminel_standard_app`, thêm path dependency tới `packages/*`) | 0.1 |
| 1.4 | Rà + sửa path trong các file cấu hình liên quan: `analysis_options.yaml`, `.gitignore`, `.github/workflows/deploy-app.yml` (working-directory), `android/fastlane/Fastfile`, `.vscode/launch.json` | 0.3 |
| 1.5 | Build lại + `fvm flutter analyze` (0 lỗi) + `flutter build apk --debug`, đối chiếu với bản build trước khi refactor để xác nhận không phát sinh lỗi | 0.3 |
| | **Tổng task 1** | **1** |

### Task 2 — Tách `packages/theme`, `utils`, `ui_components`

| # | Đầu mục con | Công số (md) |
|---|---|---|
| 2.1 | `packages/theme`: move `light_theme.dart`, `dark_theme.dart`, `app_typography.dart`, các file `*_extension.dart` (~15 file); chuyển token màu (`SemanticColors`...) sang `abstract class extends ThemeExtension` để mỗi app cung cấp bộ giá trị riêng | 1.5 |
| 2.2 | `packages/utils`: move networking (`ApiEndpoint`/Dio/interceptors, ~20 file), logger, SharedPreferences wrapper, datetime/url util thuần túy | 0.5 |
| 2.3 | `packages/ui_components`: move widget dùng chung; xử lý các widget đang gọi trực tiếp `L10n.of(context)` (đổi sang nhận string đã dịch qua constructor); xác nhận lại các hằng số như `IconSvg`/`DayOfWeek` có đúng là "từ vựng UI" hay là business logic trước khi move | 1 |
| | **Tổng task 2** | **3** |

### Task 3 — Tách `packages/features/common` + DI, chia theo tính năng dùng chung

| # | Tính năng | Việc cụ thể | Công số (md) |
|---|---|---|---|
| 3.1 | Đăng nhập / Auth | Tách 8 method từ `UserUseCase` (`getTagTagToken`, `refreshToken`, `logoutTagTag`, `logoutTagTagDemo`, `saveMobileToken`, `removeMobileToken`, `getUserInfoForStartApp`, `agreeTermsOfUse`) → `AuthUseCase`+`AuthRepository`; sửa 3 file state; tách config riêng theo app (client_id Keycloak, redirect scheme) | 1 |
| 3.2 | Cài đặt tài khoản / Account settings | Tách 5 method từ `UserUseCase` (`getUserSetting`, `updateUserSetting`, `getUserDetail`, `updateAppUserInfo`, `updateDeviceOrderForDisplay`) → `AccountUseCase`+`AccountRepository`; sửa 3 file state | 0.5 |
| 3.3 | Điểm thưởng / huy hiệu (Point & Badge) | Move `PointUseCase` (3 method, đã sạch) — cần chốt riêng việc tách 3 method point/badge đang kẹt trong `UserUseCase` | 0.5 |
| 3.4 | Thông báo (News/Tip/Survey/Contact) | Move nguyên khối 4 usecase đã sạch + repository tương ứng | 0.5 |
| 3.5 | Lỗi thiết bị (Device Error) | Tách 5 method từ `DeviceUseCase` → `DeviceErrorUseCase`+`DeviceErrorRepository`; sửa 4 file state | 1 |
| 3.6 | TagTag (link portal) | Tách `external_links.dart` — phân loại URL Chung vs riêng app; move `TagtagUrlState` | 0.5 |
| 3.7 | App state (kiểm tra version/demo mode, file download) | Move nguyên khối `MobileAppUseCase` + `S3UseCase` | 0.5 |
| 3.8 | DI wiring tổng | `providers.dart` khai abstract `UsecaseProvider` cho từng nhóm + override tại `main.dart` mỗi app | 0.5 |
| | **Tổng task 3** | | **5** |

### Task 4 — Dựng `apps/e-gw-app` rỗng

| # | Đầu mục con | Công số (md) |
|---|---|---|
| 4.1 | `flutter create` project mới, xóa boilerplate mặc định, thêm path dependency tới `packages/*` | 0.1 |
| 4.2 | Setup Android: `applicationId` mới, `namespace`, gắn `google-services.json` (chờ project Firebase mới tạo xong) | 0.2 |
| 4.3 | Setup iOS: bundle id mới, `GoogleService-Info.plist`, Info.plist scheme | 0.2 |
| 4.4 | `main.dart`: khởi tạo `ProviderScope`, khởi tạo `go_router` rỗng (route Splash/Home placeholder) | 0.2 |
| 4.5 | Build thử + chạy emulator, xác nhận app khởi động độc lập, không đụng `e-smart-app` | 0.2 |
| | **Tổng task 4** | **0.9** |

### Task 5 — Cập nhật CI/CD

| # | Đầu mục con | Công số (md) |
|---|---|---|
| 5.1 | Thêm input `app` (choice: esmart/eminel) vào `deploy-app.yml`, sửa `working-directory` theo app được chọn | 0.1 |
| 5.2 | Tách/nhân bản Fastlane `Fastfile`/`Appfile` theo app (hoặc thêm lane phân biệt) trong `android/fastlane/` | 0.1 |
| 5.4 | Trigger thử workflow, xác nhận build đúng app được chọn | 0.1 |
| | **Tổng task 5** | **0.3** |

### Task 6 — Regression test `apps/e-smart-app` (mở rộng phạm vi)

| # | Đầu mục con | Công số (md) |
|---|---|---|
| 6.1 | Lập checklist chi tiết toàn bộ ~30 route + luồng nghiệp vụ chính, ghi rõ input/expected output từng luồng | 0.3 |
| 6.2 | Test tay luồng đăng nhập/auth (login, logout, refresh token, demo mode) — rủi ro cao nhất vì vừa tách khỏi `UserUseCase` | 1 |
| 6.3 | Test tay luồng cài đặt tài khoản (cập nhật thông tin user, cài đặt thông báo) | 0.5 |
| 6.4 | Test tay luồng điểm thưởng/huy hiệu (nhận điểm, xem huy hiệu, ranking) | 0.5 |
| 6.5 | Test tay luồng thông báo (news, tip, survey, contact) | 0.5 |
| 6.6 | Test tay luồng lỗi thiết bị (danh sách lỗi, chi tiết lỗi, ẩn lỗi trên dashboard) | 0.5 |
| 6.7 | Test tay các luồng E-Smart-riêng còn lại để xác nhận move file không gây lỗi (điều khiển thiết bị, automation, dr, integration, sensor, room_monitoring...) | 1.5 |
| 6.8 | Đối chiếu kết quả test với hành vi thực tế của app trước khi refactor (đã ghi nhận sẵn từ trước), phát hiện và ghi nhận nếu có sai khác | 0.5 |
| 6.9 | Ghi nhận + xử lý vấn đề phát sinh (fix lỗi phát hiện trong quá trình test) | 1 |
| | **Tổng task 6** | **6.3** |

---

## Tổng hợp toàn bộ 6 task

| Task | Công số (md) |
|---|---|
| 1. Setup workspace + move E-Smart | 1 |
| 2. Tách theme/utils/ui_components | 3 |
| 3. Tách features/common + DI (theo tính năng) | 5 |
| 4. Dựng e-gw-app rỗng | 0.9 |
| 5. Cập nhật CI/CD | 0.3 |
| 6. Regression test e-smart-app (mở rộng) | 6.3 |
| **Tổng** | **16.5** |

---

## Phương án triển khai

### Phase 1 — Hạ tầng workspace + package dùng chung sạch

| Task | Công số (md) |
|---|---|
| 1. Setup workspace + move E-Smart | 1 |
| 2. Tách theme/utils/ui_components | 3 |
| 4. Dựng e-gw-app rỗng | 0.9 |
| 5. Cập nhật CI/CD | 0.3 |
| **Tổng Phase 1** | **5.2** |

### Phase 2 — Auth (tối thiểu để `e-gw-app` đăng nhập được) + test tương ứng

| # | Đầu mục | Công số (md) |
|---|---|---|
| 3.1 | Đăng nhập / Auth | 1 |
| 3.8 | DI wiring (cho Auth) | 0.5 |
| 6.1 | Lập checklist chi tiết toàn bộ ~30 route + luồng nghiệp vụ chính | 0.3 |
| 6.2 | Test tay luồng đăng nhập/auth (login, logout, refresh token, demo mode) | 1 |
| 6.7 | Test tay các luồng E-Smart-riêng còn lại để xác nhận move file không gây lỗi | 1.5 |
| 6.8 | Đối chiếu kết quả test với hành vi thực tế của app trước khi refactor | 0.5 |
| 6.9 | Ghi nhận + xử lý vấn đề phát sinh | 1 |
| | **Tổng Phase 2** | **5.8** |

→ Phase 1 + Phase 2 = 11 md, chia 2 người làm song song trong 1 tuần.

### Phase 3 — Các chức năng dùng chung còn lại + test tương ứng

| Nội dung | Công số (md) |
|---|---|
| Task 3 còn lại: account settings (3.2), point/badge (3.3), notification (3.4), device error (3.5), tagtag (3.6), app state (3.7) | 3.5 |
| Task 6 còn lại: test account settings, point/badge, notification, device error tương ứng | 2 |
| **Tổng Phase 3** | **5.5** |
