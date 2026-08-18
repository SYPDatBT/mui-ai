# WBS — Tái cấu trúc source app E-Smart / Eminel + Refactor E-Smart

Nội bộ SYP · lập 2026-08-19 · MD = người-ngày · ngày làm việc T2–T6 (đã trừ 02/09 Quốc khánh)
Phạm vi: tái cấu trúc source app (đề xuất → mui review → implement) + refactor E-Smart. Không gồm môi trường AWS, chiến lược branch, điều tra batch backend.
Giải thích từng dòng: `wbs_app_restructure_20260819_giaithich.md`

| № | Hạng mục | PT | MD dự kiến | MD thực tế | % | Dự kiến BĐ | Dự kiến KT | Thực tế BĐ | Thực tế KT | Ghi chú |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **Đề xuất cấu trúc & phản ánh review của mui** | | 4,0 | | 60 | 15/08 | 21/08 | 15/08 | | |
| 2 | 　Bản đề xuất cấu trúc thư mục | | 3,0 | 3,0 | 100 | 15/08 | 19/08 | 15/08 | 19/08 | Đã nộp `CLIENT_REPORT_APP_RESTRUCTURE_ja.md` |
| 3 | 　　Khảo sát source E-Smart + repo mẫu của mui | Lead | 1,5 | 1,5 | 100 | 15/08 | 17/08 | 15/08 | 17/08 | |
| 4 | 　　Viết báo cáo đề xuất (8 chương) | Lead | 1,0 | 1,0 | 100 | 18/08 | 18/08 | 18/08 | 18/08 | |
| 5 | 　　Tự review + vá 3 chỗ | Lead | 0,5 | 0,5 | 100 | 19/08 | 19/08 | 19/08 | 19/08 | commit `45ddaab` |
| 6 | 　Chuẩn bị cho buổi review của mui | | 1,0 | | 0 | 19/08 | 19/08 | | | |
| 7 | 　　Đọc `Eminelアプリ分割について.pdf` + 2 ảnh | Lead | 0,5 | | 0 | 19/08 | 19/08 | | | Tài liệu duy nhất của mui còn chưa đọc |
| 8 | 　　Soạn câu trả lời 2 câu mui dễ hỏi | Lead | 0,25 | | 0 | 19/08 | 19/08 | | | Vì sao không dùng gói dữ liệu kurashi · vì sao chỉ app mới dùng `go_router` |
| 9 | 　　Soạn phương án cho lệch lịch 5 ngày ↔ 25 MD | Lead | 0,25 | | 0 | 19/08 | 19/08 | | | 3 lựa chọn: giãn lịch · thêm người · tuần đầu chỉ làm dòng 16–27 và 57–65 |
| 10 | 　Nhận & phân loại feedback của mui | Lead | 0,5 | | 0 | 20/08 | 20/08 | | | Trích nguyên văn từng ý rồi mới sửa |
| 11 | 　Phản ánh feedback vào báo cáo | | 1,0 | | 0 | 20/08 | 21/08 | | | |
| 12 | 　　Sửa nội dung theo feedback | Lead | 0,5 | | 0 | 20/08 | 21/08 | | | |
| 13 | 　　Review nội bộ bản sửa | Dev1 | 0,25 | | 0 | 21/08 | 21/08 | | | Người thứ hai đọc, không phải người vừa sửa |
| 14 | 　　Sửa sau review nội bộ + nộp lại | Lead | 0,25 | | 0 | 21/08 | 21/08 | | | |
| 15 | 　Chốt phạm vi + lịch tuần implement với mui | Lead, mui | - | | 0 | 21/08 | 21/08 | | | Chặn toàn bộ phần implement; cần trả lời bằng văn bản |
| 16 | **Dựng workspace + chuyển E-Smart vào `apps/e-smart-app`** | | 4,0 | | 0 | 24/08 | 26/08 | | | |
| 17 | 　Chọn công cụ workspace: melos hay pub workspace | Dev1 | 0,5 | | 0 | 24/08 | 24/08 | | | Repo đang khai `sdk: ">=3.3.3"`; pub workspace đòi ≥3.6 nên kèm việc nâng SDK |
| 18 | 　Tạo nhánh từ `syp-dev` + thống nhất quy tắc commit | Dev1 | 0,25 | | 0 | 24/08 | 24/08 | | | Dời file bằng `git mv` để giữ lịch sử |
| 19 | 　Tạo khung `apps/` + `packages/` + cấu hình workspace ở gốc | Dev1 | 0,5 | | 0 | 24/08 | 24/08 | | | |
| 20 | 　Chuyển `lib/` sang `apps/e-smart-app/lib/` | Dev1 | 0,5 | | 0 | 24/08 | 25/08 | | | 481 file, giữ nguyên cấu trúc bên trong |
| 21 | 　Chuyển `android/` + `ios/` | Dev1 | 0,5 | | 0 | 25/08 | 25/08 | | | Giữ nguyên applicationId lấy từ `APP_ID` |
| 22 | 　Chuyển `asset/`, `fonts/`, `l10n.yaml`, `firebase.json`, `Gemfile` | Dev1 | 0,25 | | 0 | 25/08 | 25/08 | | | |
| 23 | 　Sửa đường dẫn assets/fonts trong `pubspec.yaml` + `l10n.yaml` | Dev1 | 0,5 | | 0 | 25/08 | 25/08 | | | Sai đường dẫn không báo lỗi biên dịch, chỉ vỡ khi chạy |
| 24 | 　Sửa `analysis_options.yaml`, `devtools_options.yaml`, `README`/`docs` | Dev2 | 0,25 | | 0 | 25/08 | 25/08 | | | |
| 25 | 　`pub get` + `build_runner` + `flutter analyze` = 0 lỗi | Dev1 | 0,5 | | 0 | 26/08 | 26/08 | | | File sinh không commit nên phải sinh lại được |
| 26 | 　Build Android (debug + release) | Dev1 | 0,25 | | 0 | 26/08 | 26/08 | | | So applicationId với bản trước khi dời |
| 27 | 　Build iOS | Dev2 | 0,25 | | 0 | 26/08 | 26/08 | | | Bundle id `jp.co.hokkaido-gas.esta` không đổi |
| 28 | **Tách 5 gói chung ra khỏi app E-Smart** | | 10,25 | | 0 | 26/08 | 04/09 | | | Thứ tự: ít phụ thuộc → nhiều phụ thuộc |
| 29 | 　Gói `packages/theme` | | 1,75 | | 0 | 26/08 | 27/08 | | | |
| 30 | 　　Tạo gói + `pubspec.yaml` | Dev1 | 0,25 | | 0 | 26/08 | 26/08 | | | |
| 31 | 　　Chuyển `light_theme.dart` + `dark_theme.dart` | Dev1 | 0,25 | | 0 | 26/08 | 26/08 | | | |
| 32 | 　　Chuyển 6 file extension về màu và chữ | Dev1 | 0,5 | | 0 | 27/08 | 27/08 | | | `app_colors` · `app_text_themes` · `color` · `primitive_color` · `theme_color` · `theme` |
| 33 | 　　Trừu tượng hoá token để mỗi app tự đặt bảng màu | Dev1 | 0,5 | | 0 | 27/08 | 27/08 | | | Yêu cầu "mỗi app một màu" của mui |
| 34 | 　　Sửa import + analyze | Dev1 | 0,25 | | 0 | 27/08 | 27/08 | | | |
| 35 | 　Gói `packages/ui_components` | | 3,0 | | 0 | 27/08 | 31/08 | | | |
| 36 | 　　Tạo gói + pubspec | Dev1 | 0,25 | | 0 | 27/08 | 27/08 | | | |
| 37 | 　　Rà 30 nhóm widget trong `widgets/common/`, phân loại chung / để lại | Lead | 0,5 | | 0 | 27/08 | 28/08 | | | Nhóm dính nghiệp vụ (contact, value_controllers) để lại trong app |
| 38 | 　　Chuyển nhóm nhập liệu (7 nhóm) | Dev1 | 0,75 | | 0 | 28/08 | 28/08 | | | buttons · textboxs · checkboxes · radio_buttons · switches · dropdowns · selectors |
| 39 | 　　Chuyển nhóm hiển thị (9 nhóm) | Dev1 | 0,75 | | 0 | 31/08 | 31/08 | | | lists · card · boxes · banners · badges · chips · dividers · icons · images |
| 40 | 　　Chuyển nhóm điều hướng & phản hồi (6 nhóm) | Dev2 | 0,5 | | 0 | 31/08 | 31/08 | | | top_app_bars · navigation_bars · tabs · snack_bars · action_sheet · steppers |
| 41 | 　　Chuyển `empty_view` · `error_view` · `loading_view` | Dev2 | 0,25 | | 0 | 31/08 | 31/08 | | | |
| 42 | 　　Cắt phụ thuộc ngược của widget chung | Dev1 | 0,5 | | 0 | 31/08 | 31/08 | | | Không import chuỗi/asset/màn hình của app; kiểm bằng grep import |
| 43 | 　Gói `packages/utils` | | 1,25 | | 0 | 01/09 | 01/09 | | | |
| 44 | 　　Chuyển nhóm không dính UI | Dev2 | 0,5 | | 0 | 01/09 | 01/09 | | | constants · datetime_japan · string_util · url_util · preference_util · logger · download_util · external_links |
| 45 | 　　Xử lý 4 file dính UI / điều hướng | Dev1 | 0,5 | | 0 | 01/09 | 01/09 | | | `navigator_util` gắn 33 chỗ `Navigator.push*` ⇒ giữ lại trong app |
| 46 | 　　Sửa import + analyze | Dev2 | 0,25 | | 0 | 01/09 | 01/09 | | | |
| 47 | 　Gói `packages/data` | | 2,75 | | 0 | 03/09 | 03/09 | | | 02/09 nghỉ lễ; tràn thì lấn 04/09 |
| 48 | 　　Tạo gói + pubspec (dio, retrofit, freezed) | Dev1 | 0,25 | | 0 | 03/09 | 03/09 | | | |
| 49 | 　　Chuyển `server/` (20 file, 15 rest client) | Dev1 | 0,75 | | 0 | 03/09 | 03/09 | | | Giữ nguyên khuôn để sau tách repo là nhấc cả gói |
| 50 | 　　Chuyển `data/entities` + `datastores` + `repositories` (131 file) | Dev1 | 1,0 | | 0 | 03/09 | 03/09 | | | |
| 51 | 　　Chạy lại `build_runner` trong gói mới | Dev1 | 0,5 | | 0 | 03/09 | 03/09 | | | Điểm dễ vỡ nhất cả đợt |
| 52 | 　　Sửa import + analyze | Dev2 | 0,25 | | 0 | 03/09 | 03/09 | | | |
| 53 | 　Gói `packages/features/common` | | 1,5 | | 0 | 04/09 | 04/09 | | | |
| 54 | 　　Chốt danh sách usecase/state dùng chung | Lead | 0,5 | | 0 | 04/09 | 04/09 | | | Đăng nhập · cài đặt · thông báo · khảo sát · push · điểm · huy hiệu · trợ giúp |
| 55 | 　　Chuyển `domain/usecases` + `domain/states` tương ứng | Dev1 | 0,75 | | 0 | 04/09 | 04/09 | | | Không mang màn hình lên gói chung |
| 56 | 　　Khai báo provider trừu tượng để app override | Dev1 | 0,25 | | 0 | 04/09 | 04/09 | | | |
| 57 | **Khởi tạo app Eminel `apps/e-gw-app`** | | 3,0 | | 0 | 07/09 | 08/09 | | | |
| 58 | 　Tạo app Flutter mới | Dev1 | 0,25 | | 0 | 07/09 | 07/09 | | | |
| 59 | 　Đặt applicationId / bundle id riêng cho Eminel | Dev1 | 0,25 | | 0 | 07/09 | 07/09 | | | Chờ mui chốt tên; chưa có thì dùng tạm bản `.dev` |
| 60 | 　Nối 5 gói chung vào app mới | Dev1 | 0,25 | | 0 | 07/09 | 07/09 | | | Phép thử thật cho việc tách gói |
| 61 | 　Dựng `go_router` + 2 route mẫu | Dev1 | 0,5 | | 0 | 07/09 | 07/09 | | | |
| 62 | 　`main.dart` + nơi override provider | Dev1 | 0,5 | | 0 | 08/09 | 08/09 | | | |
| 63 | 　Bảng màu / theme riêng cho Eminel | Dev2 | 0,5 | | 0 | 08/09 | 08/09 | | | |
| 64 | 　Dựng lại màn hình đăng nhập từ logic chung | Dev1 | 0,5 | | 0 | 08/09 | 08/09 | | | Làm mẫu: logic chung – màn hình riêng |
| 65 | 　Build Android + iOS, cài song song 2 app | Dev2 | 0,25 | | 0 | 08/09 | 08/09 | | | Bằng chứng cho goal 2 của mui |
| 66 | **Cập nhật CI/CD cho 2 app** | | 2,0 | | 0 | 09/09 | 09/09 | | | |
| 67 | 　Rà pipeline, liệt kê chỗ đang cố định 1 app | Dev2 | 0,5 | | 0 | 09/09 | 09/09 | | | |
| 68 | 　Thêm tham số chọn app khi build / deploy | Dev2 | 0,75 | | 0 | 09/09 | 09/09 | | | |
| 69 | 　Bắt buộc build cả 2 app trên mỗi PR | Dev2 | 0,5 | | 0 | 09/09 | 09/09 | | | Bù cho việc repo không có test tự động |
| 70 | 　Chạy thử pipeline trọn 1 vòng | Dev2 | 0,25 | | 0 | 09/09 | 09/09 | | | |
| 71 | **Hồi quy toàn bộ app E-Smart** | | 4,25 | | 0 | 09/09 | 11/09 | | | Toàn bộ thủ công vì repo 0 file test |
| 72 | 　Lập checklist 23 nhóm màn hình trong `presentation/pages/` | Lead | 0,5 | | 0 | 09/09 | 09/09 | | | |
| 73 | 　Test nhóm chính: dashboard, control, automation, device | Dev2 | 0,75 | | 0 | 10/09 | 10/09 | | | |
| 74 | 　Test nhóm cảm biến: sensor, room_monitoring, nhiệt-ẩm, device_error | Dev2 | 0,5 | | 0 | 10/09 | 10/09 | | | |
| 75 | 　Test nhóm người dùng: sign_in, mypage, user_detail, point, tagtag | Dev1 | 0,5 | | 0 | 10/09 | 10/09 | | | Đăng nhập qua WebView, dễ vỡ nhất |
| 76 | 　Test nhóm nội dung: news, notice, survey, tip, pdf, onboarding, welcome, splash | Dev2 | 0,5 | | 0 | 11/09 | 11/09 | | | |
| 77 | 　Test màn hình DR | Dev1 | 0,25 | | 0 | 11/09 | 11/09 | | | |
| 78 | 　Kiểm font, ảnh, chuỗi đa ngữ, thông báo đẩy | Dev1 | 0,5 | | 0 | 11/09 | 11/09 | | | |
| 79 | 　Sửa lỗi phát hiện trong hồi quy | Dev1 | 0,5 | | 0 | 11/09 | 11/09 | | | Ô đệm |
| 80 | 　Ghi biên bản hồi quy (ảnh chụp màn hình) | Dev2 | 0,25 | | 0 | 11/09 | 11/09 | | | |
| 81 | **Tài liệu + bàn giao cấu trúc mới** | | 1,5 | | 0 | 11/09 | 11/09 | | | |
| 82 | 　Viết `README` cấu trúc mới | Lead | 0,5 | | 0 | 11/09 | 11/09 | | | Thêm màn hình mới thì đặt ở đâu |
| 83 | 　Viết 3 kỷ luật giữ goal 3 của mui | Lead | 0,5 | | 0 | 11/09 | 11/09 | | | Chỉ cộng thêm · override thay vì rẽ nhánh theo app · ≥2 app mới nâng lên `packages/` |
| 84 | 　Buổi bàn giao cấu trúc cho người viết tính năng Eminel | Lead, Dev1 | 0,5 | | 0 | 11/09 | 11/09 | | | |
| 85 | **Refactor E-Smart** | | 9,0 | | 0 | 14/09 | 25/09 | | | mui yêu cầu làm sau khi có môi trường dev riêng |
| 86 | 　Review đổi tên model | | 3,5 | | 0 | 14/09 | 17/09 | | | |
| 87 | 　　Liệt kê model trong `domain/models` | Dev1 | 0,5 | | 0 | 14/09 | 14/09 | | | `domain/` có 168 file |
| 88 | 　　Đối chiếu tên model với tên trường API backend | Dev1 | 1,0 | | 0 | 14/09 | 15/09 | | | |
| 89 | 　　Lập bảng "tên hiện tại → tên đề xuất → lý do" | Lead | 1,0 | | 0 | 15/09 | 16/09 | | | Bảng để mui duyệt, chưa đụng code |
| 90 | 　　Review nội bộ bảng đổi tên | Dev2 | 0,5 | | 0 | 16/09 | 16/09 | | | |
| 91 | 　　Gửi mui duyệt + phản ánh ý kiến | Lead | 0,5 | | 0 | 17/09 | 17/09 | | | Chưa duyệt mà đổi hàng loạt = xung đột merge lớn |
| 92 | 　Tách nốt phần chung còn sót sau đợt tách gói (dòng 28–56) | | 2,0 | | 0 | 18/09 | 21/09 | | | |
| 93 | 　　Rà chỗ trùng lặp giữa 2 app | Dev1 | 1,0 | | 0 | 18/09 | 18/09 | | | |
| 94 | 　　Nâng phần đủ điều kiện lên `packages/` + build lại 2 app | Dev1 | 1,0 | | 0 | 21/09 | 21/09 | | | |
| 95 | 　Theme riêng từng app | | 3,5 | | 0 | 22/09 | 25/09 | | | |
| 96 | 　　Chốt danh mục token (màu, chữ, khoảng cách, bo góc) | Lead | 0,5 | | 0 | 22/09 | 22/09 | | | |
| 97 | 　　Bảng màu E-Smart: gom màu viết cứng về token | Dev1 | 1,0 | | 0 | 22/09 | 23/09 | | | |
| 98 | 　　Bảng màu Eminel | Dev2 | 0,5 | | 0 | 23/09 | 23/09 | | | Chờ thiết kế của mui, chưa có thì làm bản tạm |
| 99 | 　　Áp token vào widget chung, bỏ màu cứng | Dev1 | 1,0 | | 0 | 24/09 | 24/09 | | | |
| 100 | 　　Kiểm mắt 2 app ở chế độ sáng và tối | Dev2 | 0,5 | | 0 | 25/09 | 25/09 | | | |
| | **Tổng** | | **38,0** | | | 15/08 | 25/09 | | | Riêng phần implement (dòng 16–84) = 25,0 MD |

**■ Vấn đề tồn đọng**

| # | Nội dung | Chờ ai |
|---|---|---|
| 1 | Phần implement (dòng 16–84) cần 25 MD, mui chỉ dành 5 ngày (24–28/08) — phải chốt giãn lịch, thêm người hay cắt phạm vi | mui (dòng 15) |
| 2 | Chưa chốt applicationId/bundle id của app Eminel | mui (câu hỏi 2 trong báo cáo) |
| 3 | Firebase project, keystore, bản ghi app trên store cho Eminel — ai làm, bao giờ | mui (câu hỏi 5 trong báo cáo) |
| 4 | Môi trường dev riêng chưa xong ⇒ phần refactor (dòng 85–100) chưa có ngày chắc chắn | SYP/mui, ngoài phạm vi WBS này |
| 5 | Chưa có thiết kế màu/giao diện Eminel ⇒ dòng 98 chỉ làm được bản tạm | mui |
