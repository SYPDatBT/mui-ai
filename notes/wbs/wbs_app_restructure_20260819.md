# WBS — Tái cấu trúc source app E-Smart / Eminel (E-GW) + Refactor E-Smart

> Bản nội bộ SYP · lập ngày **2026-08-19** · đơn vị **MD (người-ngày)** · ngày làm việc **T2–T6**
> Phạm vi: **① Tái cấu trúc source app** (đề xuất → mui review → implement) và **② Refactor E-Smart**.
> **Ngoài phạm vi bản này**: dựng môi trường AWS `dev-phẩy`, chiến lược branch BE/màn hình quản trị, điều tra danh sách batch backend.
> Bản giải thích từng hạng mục: `wbs_app_restructure_20260819_giaithich.md`.

---

## 0. Quy ước đọc bảng

| Cột | Ý nghĩa |
|---|---|
| № | Số thứ tự dòng, dùng để trích dẫn khi họp ("dòng B2-07") |
| Hạng mục | 3 cấp: **cấp 1** = giai đoạn/sản phẩm · **cấp 2** = công việc · **cấp 3** (dấu └) = đầu việc nhỏ nhất, thường là 1 gói / 1 nhóm file / 1 lần review |
| PT | Người phụ trách. **Lead** = thiết kế · review · đối khách; **Dev1** = lập trình chính; **Dev2** = lập trình phụ + hồi quy; **mui** = phía khách |
| MD | Ước lượng công. 1 MD = 1 người làm 1 ngày. `-` = việc của khách hoặc thời gian chờ, không tính công SYP |
| % | Tiến độ, điền tay khi chạy thật |
| Bắt đầu / Kết thúc | Ngày **dự kiến**. Ngày thực tế điền vào cột trống bên phải khi làm xong |
| Ghi chú | Điều kiện hoàn thành · phụ thuộc · cảnh báo |

**Ngày nghỉ đã trừ**: T7, CN và **02/09 (T4) Quốc khánh**.
**Mốc do mui chốt**: mui review đề xuất 17–19/08 → SYP phản ánh 20–21/08 → tuần implement 24–28/08.

---

## 1. Bảng tổng quan

| Mảng | Nội dung | MD | Dự kiến |
|---|---|---|---|
| **A** | Đề xuất cấu trúc + phản ánh review của mui | 4,0 | 19/08 – 21/08 |
| **B1** | Dựng workspace + chuyển E-Smart vào `apps/e-smart-app` | 4,0 | 24/08 – 26/08 |
| **B2** | Tách 5 gói chung (`theme`, `ui_components`, `utils`, `data`, `features/common`) | 10,25 | 26/08 – 04/09 |
| **B3** | Khởi tạo `apps/e-gw-app` (vỏ app rỗng, `go_router`) | 3,0 | 07/09 – 08/09 |
| **B4** | CI/CD build tách 2 app | 2,0 | 09/09 |
| **B5** | Hồi quy E-Smart sau khi dời chỗ | 4,25 | 09/09 – 11/09 |
| **B6** | Tài liệu + bàn giao cấu trúc | 1,5 | 11/09 |
| **C** | Refactor E-Smart (đổi tên model · theme riêng từng app) | 9,0 | 14/09 – 25/09 (**chờ môi trường dev riêng**) |
| | **Tổng B1–B6** — khớp ước lượng 15–27 MD ở §5.7 báo cáo đã nộp | **25,0** | 24/08 – 11/09 |
| | **Tổng toàn bộ** | **38,0** | |

⚠️ **Lệch lịch phải chốt với mui**: mui dành **5 ngày** (24–28/08) cho implement, khối lượng thật là **25 MD**; hai lập trình viên toàn thời gian vẫn cần **khoảng 3 tuần**. Đây đúng là câu hỏi số 5 trong báo cáo đã nộp — cần câu trả lời trước 24/08 (dòng A-08, A-14).

---

## 2. Mảng A — Đề xuất cấu trúc & phản ánh review (19/08 – 21/08)

| № | Hạng mục | PT | MD | % | Bắt đầu | Kết thúc | Ghi chú |
|---|---|---|---|---|---|---|---|
| A-01 | **Bản đề xuất cấu trúc thư mục** | | 3,0 | 100 | 15/08 | 19/08 | Đã nộp: `CLIENT_REPORT_APP_RESTRUCTURE_ja.md` |
| A-02 | └ Khảo sát source E-Smart + repo mẫu của mui | Lead | 1,5 | 100 | 15/08 | 17/08 | Số liệu gốc ở `2026_08_18/output_schedule.md` mục 4 |
| A-03 | └ Viết báo cáo đề xuất (8 chương) | Lead | 1,0 | 100 | 18/08 | 18/08 | |
| A-04 | └ Tự review + vá (23 section, 481 file, phạm vi "chung") | Lead | 0,5 | 100 | 19/08 | 19/08 | commit `45ddaab` |
| A-05 | **Chuẩn bị cho buổi review của mui** | | 1,0 | 0 | 19/08 | 19/08 | |
| A-06 | └ Đọc `Eminelアプリ分割について.pdf` + 2 ảnh, đối chiếu với đề xuất đã nộp | Lead | 0,5 | 0 | 19/08 | 19/08 | Tài liệu duy nhất của mui còn chưa đọc |
| A-07 | └ Soạn sẵn câu trả lời cho 2 câu mui dễ hỏi | Lead | 0,25 | 0 | 19/08 | 19/08 | ① vì sao không dùng gói dữ liệu của kurashi ② vì sao `e-gw-app` dùng `go_router` mà E-Smart thì không |
| A-08 | └ Soạn phương án cho lệch lịch 5 ngày ↔ 25 MD | Lead | 0,25 | 0 | 19/08 | 19/08 | 3 lựa chọn: giãn lịch · tăng người · cắt phạm vi tuần đầu còn B1 + B3 |
| A-09 | **Nhận & phân loại feedback của mui** | Lead | 0,5 | 0 | 20/08 | 20/08 | Trích nguyên văn từng ý → phân loại sửa cục bộ / đổi thiết kế trước khi sửa |
| A-10 | **Phản ánh feedback vào báo cáo** | | 1,0 | 0 | 20/08 | 21/08 | |
| A-11 | └ Sửa nội dung theo feedback | Lead | 0,5 | 0 | 20/08 | 21/08 | |
| A-12 | └ Review nội bộ bản sửa | Dev1 | 0,25 | 0 | 21/08 | 21/08 | Người thứ hai đọc, không phải người vừa sửa |
| A-13 | └ Sửa sau review nội bộ + nộp lại | Lead | 0,25 | 0 | 21/08 | 21/08 | |
| A-14 | **Chốt phạm vi + lịch tuần implement với mui** | Lead, mui | - | 0 | 21/08 | 21/08 | **Chặn mảng B**. Không có câu trả lời thì 24/08 vẫn khởi động B1 vì đó là việc chắc chắn phải làm |

---

## 3. Mảng B — Implement tái cấu trúc (24/08 – 11/09)

### B1. Dựng workspace + chuyển E-Smart vào `apps/e-smart-app` — 4,0 MD (24/08 – 26/08)

| № | Hạng mục | PT | MD | % | Bắt đầu | Kết thúc | Ghi chú |
|---|---|---|---|---|---|---|---|
| B1-01 | Chọn công cụ quản workspace: **melos** hay **pub workspace** | Dev1 | 0,5 | 0 | 24/08 | 24/08 | `pubspec.yaml` đang ràng buộc `sdk: ">=3.3.3 <4.0.0"`; `pub workspace` đòi `^3.6.0` ⇒ chọn nó là phải nâng ràng buộc SDK. Repo mẫu của mui dùng melos |
| B1-02 | Tạo nhánh làm việc từ `syp-dev` + thống nhất quy tắc commit | Dev1 | 0,25 | 0 | 24/08 | 24/08 | Dời file bằng `git mv` để giữ lịch sử |
| B1-03 | Tạo khung `apps/` + `packages/` + file cấu hình workspace ở gốc | Dev1 | 0,5 | 0 | 24/08 | 24/08 | Đầu ra: `melos.yaml` (hoặc `pubspec.yaml` gốc) + `.gitignore` gốc |
| B1-04 | Chuyển `lib/` sang `apps/e-smart-app/lib/` | Dev1 | 0,5 | 0 | 24/08 | 25/08 | 481 file, giữ nguyên `data / domain / presentation / server / utils / l10n` |
| B1-05 | Chuyển `android/` và `ios/` sang `apps/e-smart-app/` | Dev1 | 0,5 | 0 | 25/08 | 25/08 | Giữ nguyên `applicationId dartEnvironmentVariables.APP_ID` và `PRODUCT_BUNDLE_IDENTIFIER = "$(APP_ID)"` |
| B1-06 | Chuyển tài nguyên: `asset/`, `fonts/`, `l10n.yaml`, `firebase.json`, `Gemfile` | Dev1 | 0,25 | 0 | 25/08 | 25/08 | |
| B1-07 | Sửa đường dẫn assets/fonts trong `pubspec.yaml` và `l10n.yaml` | Dev1 | 0,5 | 0 | 25/08 | 25/08 | Sai đường dẫn asset **không báo lỗi biên dịch**, chỉ vỡ lúc chạy ⇒ bắt buộc mở app xem |
| B1-08 | Sửa `analysis_options.yaml`, `devtools_options.yaml`, đường dẫn trong `README`/`docs` | Dev2 | 0,25 | 0 | 25/08 | 25/08 | |
| B1-09 | `flutter pub get` + `build_runner` + `flutter analyze` = 0 lỗi | Dev1 | 0,5 | 0 | 26/08 | 26/08 | File sinh (`*.g.dart`, `*.freezed.dart`) không commit nên phải sinh lại được từ đầu |
| B1-10 | Build thật Android (debug + release) | Dev1 | 0,25 | 0 | 26/08 | 26/08 | So `applicationId` in ra với bản trước khi dời |
| B1-11 | Build thật iOS | Dev2 | 0,25 | 0 | 26/08 | 26/08 | Kiểm bundle id `jp.co.hokkaido-gas.esta` không đổi |

### B2. Tách 5 gói chung — 10,25 MD (26/08 – 04/09)

| № | Hạng mục | PT | MD | % | Bắt đầu | Kết thúc | Ghi chú |
|---|---|---|---|---|---|---|---|
| B2-01 | **Gói `packages/theme`** | | 1,75 | 0 | 26/08 | 27/08 | |
| B2-02 | └ Tạo gói + `pubspec.yaml` + khai báo phụ thuộc | Dev1 | 0,25 | 0 | 26/08 | 26/08 | |
| B2-03 | └ Chuyển `utils/themes/light_theme.dart` + `dark_theme.dart` | Dev1 | 0,25 | 0 | 26/08 | 26/08 | |
| B2-04 | └ Chuyển 6 file extension về màu và chữ | Dev1 | 0,5 | 0 | 27/08 | 27/08 | `app_colors_extension` · `app_text_themes_extension` · `color_extensions` · `primitive_color` · `theme_color` · `theme_extension` |
| B2-05 | └ Trừu tượng hoá token để mỗi app tự đặt bảng màu | Dev1 | 0,5 | 0 | 27/08 | 27/08 | Đáp thẳng yêu cầu của mui: mỗi app một theme, màu khác nhau |
| B2-06 | └ Sửa import nơi dùng + `flutter analyze` | Dev1 | 0,25 | 0 | 27/08 | 27/08 | |
| B2-07 | **Gói `packages/ui_components`** | | 3,0 | 0 | 27/08 | 31/08 | |
| B2-08 | └ Tạo gói + pubspec | Dev1 | 0,25 | 0 | 27/08 | 27/08 | |
| B2-09 | └ Rà 30 nhóm widget trong `presentation/widgets/common/`, đánh dấu cái nào thật sự dùng chung | Lead | 0,5 | 0 | 27/08 | 28/08 | Nhóm dính nghiệp vụ E-Smart (ví dụ `contact`, `value_controllers`) thì để lại trong app |
| B2-10 | └ Chuyển nhóm nhập liệu: buttons, textboxs, checkboxes, radio_buttons, switches, dropdowns, selectors | Dev1 | 0,75 | 0 | 28/08 | 28/08 | |
| B2-11 | └ Chuyển nhóm hiển thị: lists, card, boxes, banners, badges, chips, dividers, icons, images | Dev1 | 0,75 | 0 | 31/08 | 31/08 | |
| B2-12 | └ Chuyển nhóm điều hướng & phản hồi: top_app_bars, navigation_bars, tabs, snack_bars, action_sheet, steppers | Dev2 | 0,5 | 0 | 31/08 | 31/08 | |
| B2-13 | └ Chuyển `empty_view` · `error_view` · `loading_view` | Dev2 | 0,25 | 0 | 31/08 | 31/08 | Báo cáo đã hứa với mui rằng phần hiển thị lỗi nằm ở gói chung |
| B2-14 | └ Cắt phụ thuộc ngược: widget chung không được import chuỗi đa ngữ, asset hay màn hình của app | Dev1 | 0,5 | 0 | 31/08 | 31/08 | Chuỗi và ảnh truyền từ ngoài vào; **kiểm bằng grep import**, không tin mắt |
| B2-15 | **Gói `packages/utils`** | | 1,25 | 0 | 01/09 | 01/09 | |
| B2-16 | └ Chuyển nhóm không dính UI | Dev2 | 0,5 | 0 | 01/09 | 01/09 | `constants` · `datetime_japan` · `string_util` · `url_util` · `preference_util` · `logger/` · `download_util` · `external_links` |
| B2-17 | └ Xử lý nhóm dính UI: `dialog_util`, `show_snackbar`, `show_point_badge_pop_up`, `navigator_util` | Dev1 | 0,5 | 0 | 01/09 | 01/09 | `navigator_util` gắn với 33 chỗ gọi `Navigator.push*` ⇒ **giữ lại trong app**, không nâng lên gói chung |
| B2-18 | └ Sửa import + analyze | Dev2 | 0,25 | 0 | 01/09 | 01/09 | |
| B2-19 | **Gói `packages/data`** | | 2,75 | 0 | 03/09 | 03/09 | 02/09 nghỉ lễ nên dồn vào 03/09; nếu tràn thì lấn sang 04/09 |
| B2-20 | └ Tạo gói + pubspec (dio, retrofit, freezed, json_annotation) | Dev1 | 0,25 | 0 | 03/09 | 03/09 | |
| B2-21 | └ Chuyển `server/` — 20 file: `mui_service`, `mui_api_endpoint`, 15 rest client… | Dev1 | 0,75 | 0 | 03/09 | 03/09 | Giữ nguyên khuôn để sau này muốn tách ra repo riêng thì nhấc cả gói |
| B2-22 | └ Chuyển `data/entities`, `data/datastores`, `data/repositories` — 131 file | Dev1 | 1,0 | 0 | 03/09 | 03/09 | |
| B2-23 | └ Chạy lại `build_runner` cho retrofit/freezed trong gói mới | Dev1 | 0,5 | 0 | 03/09 | 03/09 | Điểm dễ vỡ nhất cả đợt: nơi sinh code khác nơi gọi |
| B2-24 | └ Sửa import + analyze | Dev2 | 0,25 | 0 | 03/09 | 03/09 | |
| B2-25 | **Gói `packages/features/common`** | | 1,5 | 0 | 04/09 | 04/09 | |
| B2-26 | └ Chọn usecase/state dùng chung: đăng nhập, cài đặt, thông báo, khảo sát, push, điểm, huy hiệu, trợ giúp | Lead | 0,5 | 0 | 04/09 | 04/09 | Bám bảng phân loại §5.3 của báo cáo đã nộp |
| B2-27 | └ Chuyển `domain/usecases` + `domain/states` tương ứng | Dev1 | 0,75 | 0 | 04/09 | 04/09 | **Không mang màn hình lên** — đúng ghi chú "phạm vi chung" đã hứa với mui |
| B2-28 | └ Khai báo provider trừu tượng để mỗi app tự override | Dev1 | 0,25 | 0 | 04/09 | 04/09 | Ví dụ: đăng nhập xong, mỗi app vào một màn hình chính khác nhau |

### B3. Khởi tạo `apps/e-gw-app` — 3,0 MD (07/09 – 08/09)

| № | Hạng mục | PT | MD | % | Bắt đầu | Kết thúc | Ghi chú |
|---|---|---|---|---|---|---|---|
| B3-01 | Tạo app Flutter mới trong `apps/e-gw-app` | Dev1 | 0,25 | 0 | 07/09 | 07/09 | |
| B3-02 | Đặt định danh app (applicationId / bundle id) riêng cho Eminel | Dev1 | 0,25 | 0 | 07/09 | 07/09 | **Chờ mui chốt tên** (câu hỏi 2 trong báo cáo); chưa có thì dùng tạm bản `.dev` |
| B3-03 | Nối 5 gói chung vào app mới | Dev1 | 0,25 | 0 | 07/09 | 07/09 | |
| B3-04 | Dựng `go_router` + 2 route mẫu | Dev1 | 0,5 | 0 | 07/09 | 07/09 | Khác cách của E-Smart — đã ghi rõ trong báo cáo là ngoại lệ có chủ ý |
| B3-05 | `main.dart` + nơi override provider của riêng app | Dev1 | 0,5 | 0 | 08/09 | 08/09 | |
| B3-06 | Bảng màu / theme riêng cho Eminel | Dev2 | 0,5 | 0 | 08/09 | 08/09 | |
| B3-07 | Dựng lại màn hình đăng nhập từ logic chung | Dev1 | 0,5 | 0 | 08/09 | 08/09 | Làm mẫu cho cách dùng đúng; cũng là chỗ mui dễ hiểu nhầm thành "dùng lại cả màn hình" |
| B3-08 | Build Android + iOS, cài song song 2 app trên cùng 1 máy | Dev2 | 0,25 | 0 | 08/09 | 08/09 | Bằng chứng cho goal 2 của mui |

### B4. CI/CD cho 2 app — 2,0 MD (09/09)

| № | Hạng mục | PT | MD | % | Bắt đầu | Kết thúc | Ghi chú |
|---|---|---|---|---|---|---|---|
| B4-01 | Rà pipeline hiện có, liệt kê chỗ đang cố định 1 app | Dev2 | 0,5 | 0 | 09/09 | 09/09 | |
| B4-02 | Thêm tham số chọn app khi build / deploy | Dev2 | 0,75 | 0 | 09/09 | 09/09 | |
| B4-03 | Bắt buộc **build cả 2 app trên mỗi PR** | Dev2 | 0,5 | 0 | 09/09 | 09/09 | Bù cho việc repo **không có test tự động nào** |
| B4-04 | Chạy thử pipeline trọn 1 vòng | Dev2 | 0,25 | 0 | 09/09 | 09/09 | |

### B5. Hồi quy E-Smart — 4,25 MD (09/09 – 11/09)

| № | Hạng mục | PT | MD | % | Bắt đầu | Kết thúc | Ghi chú |
|---|---|---|---|---|---|---|---|
| B5-01 | Lập checklist hồi quy: 23 nhóm màn hình trong `presentation/pages/` (~30 màn hình) | Lead | 0,5 | 0 | 09/09 | 09/09 | Repo **0 file test** ⇒ hồi quy hoàn toàn thủ công |
| B5-02 | Test nhóm chính: dashboard, control, automation, device | Dev2 | 0,75 | 0 | 10/09 | 10/09 | |
| B5-03 | Test nhóm dữ liệu & cảm biến: sensor, room_monitoring, temperature_and_humidity, device_error | Dev2 | 0,5 | 0 | 10/09 | 10/09 | |
| B5-04 | Test nhóm người dùng: sign_in, mypage, user_detail, point, tagtag | Dev1 | 0,5 | 0 | 10/09 | 10/09 | Đăng nhập chạy qua WebView — dễ vỡ khi dời tài nguyên |
| B5-05 | Test nhóm nội dung: news, notice, survey, tip, pdf, onboarding, welcome, splash | Dev2 | 0,5 | 0 | 11/09 | 11/09 | |
| B5-06 | Test màn hình DR | Dev1 | 0,25 | 0 | 11/09 | 11/09 | |
| B5-07 | Kiểm tài nguyên: font, ảnh, chuỗi đa ngữ, thông báo đẩy | Dev1 | 0,5 | 0 | 11/09 | 11/09 | Lỗi đường dẫn asset chỉ lộ khi chạy thật |
| B5-08 | Sửa lỗi phát hiện trong hồi quy | Dev1 | 0,5 | 0 | 11/09 | 11/09 | Ô đệm; vượt thì lấn tuần sau |
| B5-09 | Ghi biên bản hồi quy (ảnh chụp màn hình từng nhóm) | Dev2 | 0,25 | 0 | 11/09 | 11/09 | |

### B6. Tài liệu + bàn giao — 1,5 MD (11/09)

| № | Hạng mục | PT | MD | % | Bắt đầu | Kết thúc | Ghi chú |
|---|---|---|---|---|---|---|---|
| B6-01 | Viết `README` cấu trúc mới: thư mục nào chứa gì, thêm màn hình mới thì đặt ở đâu | Lead | 0,5 | 0 | 11/09 | 11/09 | |
| B6-02 | Viết 3 kỷ luật giữ goal 3 của mui | Lead | 0,5 | 0 | 11/09 | 11/09 | ① sửa gói chung chỉ được cộng thêm ② khác biệt 2 app xử lý bằng override, cấm rẽ nhánh theo tên app trong gói chung ③ chỉ nâng lên `packages/` khi từ 2 app trở lên dùng |
| B6-03 | Buổi bàn giao cấu trúc cho người viết tính năng Eminel | Lead, Dev1 | 0,5 | 0 | 11/09 | 11/09 | |

---

## 4. Mảng C — Refactor E-Smart (14/09 – 25/09, **chờ môi trường dev riêng**)

> mui ghi rõ: refactor E-Smart làm **sau khi dựng xong môi trường phát triển**. Ngày dưới đây giả định môi trường xong trước 14/09; môi trường trễ thì cả mảng trượt theo, **không chặn mảng B**.

| № | Hạng mục | PT | MD | % | Bắt đầu | Kết thúc | Ghi chú |
|---|---|---|---|---|---|---|---|
| C-01 | **Review đổi tên model** | | 3,5 | 0 | 14/09 | 17/09 | Yêu cầu "モデル名リファクタのレビュー" của mui |
| C-02 | └ Liệt kê toàn bộ model hiện có trong `domain/models` | Dev1 | 0,5 | 0 | 14/09 | 14/09 | `domain/` có 168 file |
| C-03 | └ Đối chiếu tên model với tên trường phía API backend | Dev1 | 1,0 | 0 | 14/09 | 15/09 | Tránh đổi tên xong lệch với BE |
| C-04 | └ Lập bảng "tên hiện tại → tên đề xuất → lý do" | Lead | 1,0 | 0 | 15/09 | 16/09 | Đầu ra là bảng để mui duyệt, **chưa đụng code** |
| C-05 | └ Review nội bộ bảng đổi tên | Dev2 | 0,5 | 0 | 16/09 | 16/09 | |
| C-06 | └ Gửi mui duyệt + phản ánh ý kiến | Lead | 0,5 | 0 | 17/09 | 17/09 | Đổi tên hàng loạt khi chưa duyệt = xung đột merge lớn |
| C-07 | **Tách nốt phần chung còn sót sau B2** | | 2,0 | 0 | 18/09 | 21/09 | Có app thứ hai chạy thật mới lộ chỗ nào thật sự dùng chung |
| C-08 | └ Rà chỗ trùng lặp giữa 2 app | Dev1 | 1,0 | 0 | 18/09 | 18/09 | Áp kỷ luật "từ 2 app dùng mới nâng lên" |
| C-09 | └ Nâng phần đủ điều kiện lên `packages/` + analyze + build lại 2 app | Dev1 | 1,0 | 0 | 21/09 | 21/09 | |
| C-10 | **Theme riêng từng app** | | 3,5 | 0 | 22/09 | 25/09 | Yêu cầu "mỗi app có theme riêng, màu khác nhau" |
| C-11 | └ Chốt danh mục token: màu, chữ, khoảng cách, bo góc | Lead | 0,5 | 0 | 22/09 | 22/09 | |
| C-12 | └ Bảng màu E-Smart: gom màu đang viết cứng về token | Dev1 | 1,0 | 0 | 22/09 | 23/09 | |
| C-13 | └ Bảng màu Eminel | Dev2 | 0,5 | 0 | 23/09 | 23/09 | Chờ thiết kế của mui; chưa có thì làm bản tạm |
| C-14 | └ Áp token vào widget chung, bỏ hết màu cứng | Dev1 | 1,0 | 0 | 24/09 | 24/09 | |
| C-15 | └ Kiểm mắt 2 app ở chế độ sáng và tối | Dev2 | 0,5 | 0 | 25/09 | 25/09 | Repo có sẵn `light_theme` và `dark_theme` |

---

## 5. Lịch theo từng ngày

| Ngày | Việc trong ngày | Ai |
|---|---|---|
| **19/08 T4** | A-06 đọc PDF của mui · A-07 soạn 2 câu trả lời · A-08 phương án lệch lịch | Lead |
| **20/08 T5** | A-09 nhận & phân loại feedback · A-11 bắt đầu sửa | Lead |
| **21/08 T6** | A-11 sửa xong · A-12 review nội bộ · A-13 nộp lại · A-14 chốt lịch với mui | Lead, Dev1 |
| **24/08 T2** | B1-01 chọn melos/pub workspace · B1-02 nhánh · B1-03 khung thư mục · B1-04 bắt đầu dời `lib/` | Dev1 |
| **25/08 T3** | B1-04 xong · B1-05 android/ios · B1-06 tài nguyên · B1-07 pubspec + l10n · B1-08 file cấu hình | Dev1, Dev2 |
| **26/08 T4** | B1-09 analyze · B1-10 build Android · B1-11 build iOS · B2-02→03 mở gói `theme` | Dev1, Dev2 |
| **27/08 T5** | B2-04→06 xong `theme` · B2-08 mở `ui_components` · B2-09 rà 30 nhóm widget | Dev1, Lead |
| **28/08 T6** | B2-09 xong · B2-10 chuyển nhóm widget nhập liệu | Dev1, Lead |
| **31/08 T2** | B2-11 nhóm hiển thị · B2-12 nhóm điều hướng · B2-13 view lỗi/rỗng · B2-14 cắt phụ thuộc ngược | Dev1, Dev2 |
| **01/09 T3** | B2-16→18 gói `utils` | Dev1, Dev2 |
| **02/09 T4** | **Nghỉ Quốc khánh** | — |
| **03/09 T5** | B2-20→24 gói `data`: server + entities + datastores + chạy lại build_runner | Dev1, Dev2 |
| **04/09 T6** | B2-26→28 gói `features/common` | Lead, Dev1 |
| **07/09 T2** | B3-01→04 dựng vỏ `e-gw-app` + `go_router` | Dev1 |
| **08/09 T3** | B3-05→08 main · theme · màn hình đăng nhập · build 2 app | Dev1, Dev2 |
| **09/09 T4** | B4-01→04 CI/CD · B5-01 lập checklist hồi quy | Dev2, Lead |
| **10/09 T5** | B5-02→04 hồi quy nhóm chính, cảm biến, người dùng | Dev1, Dev2 |
| **11/09 T6** | B5-05→09 hồi quy nốt + sửa lỗi + biên bản · B6-01→03 tài liệu & bàn giao | Cả nhóm |
| **14–17/09** | C-01→06 review đổi tên model | Lead, Dev1 |
| **18–21/09** | C-07→09 tách nốt phần chung | Dev1 |
| **22–25/09** | C-10→15 theme riêng từng app | Dev1, Dev2 |

---

## 6. Phụ thuộc & rủi ro

| # | Nội dung | Mức | Cách xử lý |
|---|---|---|---|
| 1 | **25 MD không vừa 5 ngày mui đưa ra** | Cao | A-08 / A-14 chốt trước 24/08. Nếu buộc phải xong trong tuần 24–28/08 thì cắt còn B1 + B3 (có cấu trúc + vỏ app chạy được), B2 lùi lại |
| 2 | **Repo không có test tự động** | Cao | Hồi quy thủ công B5 + bắt buộc build cả 2 app mỗi PR (B4-03) |
| 3 | `build_runner` sinh code xuyên gói (B2-23) | Cao | Làm gói `data` gọn trong một mạch, không để dở dang qua đêm |
| 4 | Chưa chốt định danh app Eminel (B3-02) | Vừa | Đã hỏi trong báo cáo (câu 2); chưa có thì dùng tạm rồi đổi |
| 5 | Môi trường dev riêng chưa xong → mảng C trượt | Vừa | Mảng C không chặn mảng B; cứ chạy B trước |
| 6 | Đổi tên model xung đột với nhánh khác đang sửa | Vừa | C-06 duyệt trước, gom vào một nhánh ngắn, merge ngay |
| 7 | Widget chung còn dính chuỗi/asset của E-Smart | Vừa | B2-14 kiểm bằng grep import, không tin mắt |

---

## 7. Việc chưa đủ dữ kiện để xếp lịch (điền sau)

1. **Firebase / keystore / bản ghi app trên store cho Eminel** — mui chưa trả lời ai làm (câu hỏi 5 trong báo cáo). Mỗi thứ có thời gian chờ riêng, phải khởi động song song ngay khi có câu trả lời.
2. **Phạm vi tuần 24–28/08**: chỉ tái cấu trúc thư mục, hay gồm cả tính năng Eminel đầu tiên (câu hỏi 3 trong báo cáo).
3. **Thiết kế màu/giao diện Eminel** — chưa có thì C-13 chỉ làm được bản tạm.
