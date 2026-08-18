# Giải thích từng hạng mục trong WBS tái cấu trúc source app

> Đi kèm `wbs_app_restructure_20260819.md` — mã dòng ở hai file khớp nhau.
> Mỗi hạng mục trả lời 3 câu: **vì sao có việc này** · **làm cụ thể cái gì** · **coi là xong khi nào**.
> Bản nội bộ, tiếng Việt. Số liệu về source đếm trực tiếp trên `sources/syp-eminelstandard-app` ở commit `41ee385` (nhánh `syp-dev`), ngày 2026-08-19.

---

## Phần 0 — Vì sao WBS chia như thế này

mui giao 5 việc trong `chokkin_irai.md`, WBS này chỉ lấy **2 việc**: tái cấu trúc source app và refactor E-Smart. Ba việc còn lại (môi trường AWS riêng, chiến lược branch, điều tra batch backend) tách bảng khác vì khác loại công việc và khác người làm.

Trục chia việc: **theo giai đoạn kỹ thuật** chứ không theo tính năng. Lý do: đợt này không viết tính năng mới nào, chỉ **di chuyển code**. Rủi ro lớn nhất không phải "viết sai" mà là **"dời xong app cũ chạy khác đi"** — nên cấu trúc WBS là: dựng khung → dời từng cụm → mở app mới → hồi quy toàn bộ app cũ.

Bốn nguyên tắc chia đầu việc nhỏ nhất:
1. **Một dòng = một thứ kiểm chứng được** (một gói, một nhóm file, một lần build). Không có dòng kiểu "làm phần chung".
2. **Việc kiểm tra là dòng riêng**, không nhét vào việc làm — `analyze`, build Android, build iOS đều tách dòng, vì đó là những chỗ hay bị bỏ.
3. **Việc review là dòng riêng và do người khác làm** — người sửa không tự nghiệm thu.
4. **Việc chờ khách cũng là dòng** (MD = `-`), để nhìn ra chỗ nào đang bị chặn chứ không phải chỗ nào đang chậm.

---

## Phần A — Đề xuất cấu trúc & phản ánh review

| Mã | Vì sao có việc này | Làm cụ thể | Coi là xong khi |
|---|---|---|---|
| A-01→A-04 | Việc đã hoàn tất, giữ trong WBS để thấy công đã bỏ ra và để đối chiếu ước lượng với thực tế | Khảo sát source, viết báo cáo 8 chương, tự review và vá 3 chỗ | Đã nộp mui, commit `45ddaab` |
| A-05 | mui review đúng 17–19/08; vào họp mà chưa đọc hết tài liệu của chính họ là mất điểm và dễ nhận feedback trùng lặp | Gói chuẩn bị gồm A-06, A-07, A-08 | Cả 3 dòng con xong trước buổi review |
| A-06 | `Eminelアプリ分割について.pdf` là **tài liệu duy nhất của mui chưa đọc**; nó có thể chứa ràng buộc mà báo cáo chưa phản ánh | Đọc PDF + 2 ảnh, đối chiếu từng ý với đề xuất đã nộp, ghi ra chỗ lệch | Có danh sách "khớp / lệch / chưa nói tới" |
| A-07 | Hai câu này mui gần như chắc chắn hỏi, trả lời vo dễ sai | ① Vì sao không dùng gói dữ liệu của kurashi: khác cách xác thực (nền kurashi dùng Auth0/Cognito, E-Smart đăng nhập qua WebView) và kéo theo phải nâng cả stack. ② Vì sao app mới dùng `go_router` còn E-Smart giữ cách cũ: ưu tiên không đụng vào 30 màn hình đang chạy ổn định | Có sẵn 2 đoạn trả lời viết ra giấy, không phải nhớ trong đầu |
| A-08 | Ước lượng 25 MD không vừa 5 ngày mui đưa; vào họp mà chỉ nêu vấn đề, không kèm lựa chọn thì cuộc họp không quyết được gì | Soạn 3 phương án: giãn lịch đến giữa tháng 9 · thêm người · cắt phạm vi tuần đầu chỉ còn B1 + B3 | Có bảng 3 phương án kèm hệ quả từng phương án |
| A-09 | Feedback của khách hay bị hiểu rộng hoặc hiểu hẹp hơn nguyên văn | Trích **nguyên văn** từng ý, phân loại: sửa cục bộ / đổi thiết kế / cần hỏi lại | Mỗi ý có nhãn phân loại và người xử lý |
| A-10→A-13 | Sửa xong phải có người thứ hai đọc — đây là lỗi hay gặp: người vừa sửa tự thấy bản sửa của mình đúng | Sửa → Dev1 review → sửa nốt → nộp lại | Bản mới đã nộp, không còn ý feedback nào chưa trả lời |
| A-14 | **Dòng chặn quan trọng nhất của cả WBS**: chưa chốt phạm vi thì tuần implement dễ làm sai hướng | Họp/chốt bằng văn bản với mui về phạm vi + lịch | Có câu trả lời bằng chữ (mail/Notion), không phải hiểu ngầm |

---

## Phần B1 — Dựng workspace và dời E-Smart

| Mã | Vì sao có việc này | Làm cụ thể | Coi là xong khi |
|---|---|---|---|
| B1-01 | Hai cách quản nhiều gói trong một repo cho ra cấu hình khác hẳn nhau, chọn sai là làm lại từ đầu. Repo hiện khai `sdk: ">=3.3.3 <4.0.0"`, trong khi `pub workspace` đòi từ `3.6.0` — tức chọn nó là **kèm việc nâng ràng buộc SDK**, còn melos thì không | So 2 phương án trên đúng repo này, chọn 1, ghi lý do | Có quyết định + lý do viết ra, cả nhóm biết |
| B1-02 | Dời file mà mất lịch sử git thì sau này không truy được ai sửa gì | Tạo nhánh từ `syp-dev`; thống nhất dùng `git mv`, mỗi bước dời là 1 commit riêng | Nhánh có, quy tắc commit đã thống nhất |
| B1-03 | Khung thư mục phải có trước mới dời được | Tạo `apps/`, `packages/`, file cấu hình workspace ở gốc, `.gitignore` gốc | `flutter pub get` ở gốc chạy trót lọt |
| B1-04 | Đây là bước "dọn nhà" chính: toàn bộ 481 file Dart đổi chỗ | `git mv lib` sang `apps/e-smart-app/lib`, **không đổi cấu trúc bên trong** (`data`, `domain`, `presentation`, `server`, `utils`, `l10n` giữ nguyên) | Cây thư mục mới đúng như báo cáo đã hứa với mui |
| B1-05 | Phần Android/iOS quyết định app có lên đúng chỗ trên store hay không | Dời `android/`, `ios/`; kiểm `applicationId` vẫn lấy từ biến `APP_ID` và bundle id iOS vẫn là `$(APP_ID)` | Định danh in ra lúc build **giống hệt** trước khi dời |
| B1-06 | Tài nguyên không dời theo thì app biên dịch được nhưng chạy vỡ giao diện | Dời `asset/`, `fonts/`, `l10n.yaml`, `firebase.json`, `Gemfile` | Không còn file lạc ở gốc repo |
| B1-07 | Đường dẫn asset/font nằm trong `pubspec.yaml`, sai thì **không có lỗi biên dịch**, chỉ vỡ khi chạy | Sửa mọi đường dẫn trong `pubspec.yaml` và `l10n.yaml` | Mở app thấy đủ font, ảnh, chuỗi tiếng Nhật |
| B1-08 | Mấy file cấu hình phụ hay bị bỏ quên, để sai thì lint và tài liệu trỏ nhầm chỗ | Sửa `analysis_options.yaml`, `devtools_options.yaml`, đường dẫn trong `README`/`docs` | Không còn đường dẫn cũ khi grep |
| B1-09 | Repo **không commit file sinh** (`*.g.dart`, `*.freezed.dart`) nên bắt buộc phải sinh lại được sau khi dời | `flutter pub get` → `build_runner` → `flutter analyze` | `analyze` ra 0 lỗi |
| B1-10 / B1-11 | Biên dịch được chưa chắc build ra app được; và đây là lúc phát hiện sớm chuyện định danh app | Build Android debug + release, build iOS | Cả 2 nền tảng ra bản cài được, định danh đúng |

---

## Phần B2 — Tách 5 gói chung

**Vì sao tách đúng 5 gói này**: bám cách chia của repo mẫu mui chỉ định (`theme`, `ui_components`, `utils`, `features/common`) và thêm `data` — vì tầng dữ liệu của E-Smart hiện có khuôn giống hệt gói dữ liệu nền của mui, để chung một chỗ thì sau này muốn tách ra repo riêng chỉ việc nhấc cả gói.

**Thứ tự tách không tuỳ tiện**: đi từ gói **ít phụ thuộc nhất** đến gói **nhiều phụ thuộc nhất** — `theme` (không phụ thuộc gì) → `ui_components` (chỉ cần theme) → `utils` → `data` (nặng vì có sinh code) → `features/common` (cần cả data lẫn utils). Làm ngược thứ tự này thì mỗi bước lại phải sửa import hai lần.

| Mã | Vì sao có việc này | Làm cụ thể | Coi là xong khi |
|---|---|---|---|
| B2-02→06 | Gói `theme` là gốc của yêu cầu "mỗi app một màu" mà mui nêu thẳng trong đề bài | Dời `light_theme`/`dark_theme` + 6 file extension về màu và chữ; đổi màu viết cứng thành **token** để mỗi app tự cấp bảng màu | E-Smart hiển thị y như cũ, và đổi 1 bảng màu là đổi được toàn app |
| B2-09 | Thư mục `presentation/widgets/common/` có **30 nhóm** widget, nhưng "để trong thư mục common" không có nghĩa là dùng chung được — có nhóm dính nghiệp vụ E-Smart (ví dụ `contact`, `value_controllers`) | Lead rà từng nhóm, đánh dấu: chung / để lại trong app / cần sửa mới chung được | Có bảng phân loại 30 nhóm, làm cơ sở cho 3 đợt chuyển sau |
| B2-10→13 | Chuyển 30 nhóm một lúc thì lỗi chồng lỗi, không biết cái nào gây vỡ | Chia 3 đợt theo loại: nhập liệu → hiển thị → điều hướng/phản hồi; cộng 3 view trạng thái (`empty`, `error`, `loading`) | Sau mỗi đợt: `analyze` sạch + app cũ vẫn chạy |
| B2-14 | Đây là lỗi kinh điển khi tách gói: widget "chung" vẫn ngầm gọi chuỗi đa ngữ, ảnh hoặc màn hình của app cũ ⇒ app thứ hai kéo về là gãy | Cắt phụ thuộc ngược: chuỗi và ảnh truyền từ ngoài vào; **kiểm bằng grep import**, không đọc bằng mắt | Trong gói `ui_components` không còn import nào trỏ về app |
| B2-16 | Phần lớn `utils` là hàm thuần, dời sang gói chung là an toàn | Dời `constants`, `datetime_japan`, `string_util`, `url_util`, `preference_util`, `logger/`, `download_util`, `external_links` | `analyze` sạch |
| B2-17 | Bốn file còn lại dính UI hoặc dính điều hướng nên **không** dời máy móc được. Riêng `navigator_util` gắn với 33 chỗ gọi `Navigator.push*` — mà E-Smart đã chốt là **giữ nguyên cách điều hướng cũ** | `dialog_util`, `show_snackbar`, `show_point_badge_pop_up` xử lý theo hướng nhận tham số từ ngoài; `navigator_util` **để lại trong app** | Quyết định từng file được ghi lại, không để "tạm thế đã" |
| B2-20→24 | Gói `data` là gói nặng nhất: 20 file `server/` + 131 file `data/`, lại có sinh code (retrofit, freezed) | Dời `server/` rồi `data/`, chạy lại `build_runner` **trong gói mới**, sửa import | Sinh code lại được từ máy sạch, `analyze` 0 lỗi, app gọi API chạy thật |
| B2-23 | Tách riêng thành một dòng vì đây là **điểm dễ vỡ nhất cả đợt**: nơi sinh code và nơi gọi giờ nằm ở hai gói khác nhau | Chạy `build_runner` ở gói `data`, kiểm file sinh ra đúng chỗ, app vẫn thấy | Xoá hết file sinh rồi tạo lại từ đầu vẫn chạy |
| B2-26 | Phải có người quyết định cái gì là "chung" trước khi lập trình viên dời, nếu không sẽ dời theo cảm tính | Lead chọn usecase/state cho: đăng nhập, cài đặt, thông báo, khảo sát, push, điểm, huy hiệu, trợ giúp — theo đúng bảng §5.3 đã nộp mui | Có danh sách chốt, đúng bằng những gì đã hứa với khách |
| B2-27 | Ranh giới quan trọng nhất của cả đợt: gói chung **không chứa màn hình** | Dời `domain/usecases` + `domain/states` tương ứng, **không dời file màn hình** | Trong `features/common` không có file nào dựng giao diện |
| B2-28 | Hai app dùng chung logic nhưng phải hành xử khác nhau (ví dụ đăng nhập xong vào màn hình chính khác nhau) — nếu không có chỗ override thì sẽ phát sinh rẽ nhánh theo tên app trong gói chung, đúng thứ mui không muốn | Khai báo provider trừu tượng, app cấp bản thật lúc khởi động | E-Smart chạy đúng như cũ qua đường override |

---

## Phần B3 — Dựng vỏ app Eminel

| Mã | Vì sao có việc này | Làm cụ thể | Coi là xong khi |
|---|---|---|---|
| B3-01 | Goal 2 của mui là **build được 2 app riêng**; chưa có app thứ hai thì chưa chứng minh được gì | Tạo app Flutter mới trong `apps/e-gw-app` | Thư mục app mới build được rỗng |
| B3-02 | Định danh app quyết định app lên store là bản mới hay đè bản cũ | Đặt applicationId/bundle id riêng cho Eminel | Có định danh mui duyệt; chưa có thì dùng bản `.dev` và ghi vào mục việc treo |
| B3-03 | Đây là phép thử thật cho 5 gói vừa tách: gói chung mà app mới không dùng được thì việc tách coi như hỏng | Khai báo phụ thuộc 5 gói trong app mới | App mới biên dịch được với đủ 5 gói |
| B3-04 | App mới không có gánh nặng tương thích nên theo chuẩn mới ngay từ đầu | Dựng `go_router` + 2 route mẫu | Chạy được, chuyển màn hình được |
| B3-05 | Chỗ này là nơi hiện thực hoá "một logic, hai hành vi" | `main.dart` + nơi override provider của app Eminel | App chạy với bản override riêng |
| B3-06 | Chứng minh yêu cầu "mỗi app một màu" bằng sản phẩm chạy được, không chỉ bằng lời | Bảng màu Eminel nạp vào gói `theme` | Hai app cùng widget nhưng khác màu |
| B3-07 | Màn hình đăng nhập là ví dụ mẫu cho cách dùng đúng, và đúng chỗ mui dễ hiểu nhầm rằng "dùng lại được cả màn hình" | Dựng lại màn hình đăng nhập ở app mới, dùng logic chung | Chạy được, và nhìn vào thấy rõ: logic chung – màn hình riêng |
| B3-08 | Bằng chứng cuối cho goal 2 | Build Android + iOS, cài **cả hai app cùng lúc** trên một máy | Hai biểu tượng riêng, chạy độc lập |

---

## Phần B4 — CI/CD

| Mã | Vì sao có việc này | Làm cụ thể | Coi là xong khi |
|---|---|---|---|
| B4-01 | Pipeline hiện tại viết cho đúng một app, không rà thì sẽ vỡ ngầm | Liệt kê mọi chỗ đang cố định 1 app | Có danh sách chỗ phải sửa |
| B4-02 | Hai app hai store, phải chọn được build cái nào | Thêm tham số chọn app khi build/deploy | Chạy pipeline với tham số ra đúng app |
| B4-03 | Repo **không có test tự động nào** — lưới an toàn duy nhất còn lại là biên dịch. Nếu chỉ build 1 app mỗi PR thì sửa gói chung làm gãy app kia mà không ai biết | Bắt buộc build cả 2 app trên mỗi PR | PR nào cũng chạy 2 job build |
| B4-04 | Cấu hình chưa chạy thật thì chưa tính là xong | Chạy trọn 1 vòng | Có bản build ra từ pipeline |

---

## Phần B5 — Hồi quy E-Smart

**Vì sao mảng này to (4,25 MD)**: E-Smart đang chạy thật ngoài thị trường, đợt này lại **dời toàn bộ 481 file**. Repo không có một file test nào, nên cách duy nhất để biết app còn nguyên vẹn là **mở từng màn hình ra xem**. Chia nhóm màn hình để hai người chạy song song và không sót.

| Mã | Vì sao có việc này | Làm cụ thể | Coi là xong khi |
|---|---|---|---|
| B5-01 | Không có checklist thì mỗi người test một kiểu và không chứng minh được đã phủ hết | Lập checklist theo **23 nhóm màn hình** trong `presentation/pages/` (báo cáo đã nộp mui ghi ~30 màn hình) | Checklist được Lead duyệt |
| B5-02 | Nhóm màn hình chính là nhóm người dùng chạm nhiều nhất | Test dashboard, control, automation, device | Hành vi giống hệt trước khi dời |
| B5-03 | Nhóm này đọc dữ liệu cảm biến, dễ lộ lỗi tầng `data` vừa tách | Test sensor, room_monitoring, temperature_and_humidity, device_error | Dữ liệu lên đúng |
| B5-04 | Đăng nhập chạy qua WebView, phụ thuộc cấu hình và tài nguyên — nhóm dễ vỡ nhất khi đổi chỗ file | Test sign_in, mypage, user_detail, point, tagtag | Đăng nhập, đăng xuất, điểm đều đúng |
| B5-05 | Nhóm nội dung dùng nhiều asset và chuỗi đa ngữ | Test news, notice, survey, tip, pdf, onboarding, welcome, splash | Hiển thị đủ chữ và ảnh |
| B5-06 | Màn hình DR là nghiệp vụ riêng của E-Smart, dễ bị bỏ quên | Test màn hình DR | Chạy đúng |
| B5-07 | Font, ảnh, chuỗi, thông báo đẩy là 4 thứ hỏng âm thầm sau khi đổi đường dẫn | Kiểm chéo cả 4 | Không thiếu tài nguyên nào |
| B5-08 | Phải có ô đệm cho lỗi phát hiện trong hồi quy, nếu không WBS chỉ đúng khi mọi thứ suôn sẻ | Sửa lỗi tìm được | Hết lỗi chặn |
| B5-09 | Không có biên bản thì sau này không chứng minh được đã hồi quy | Chụp màn hình từng nhóm, ghi biên bản | Biên bản có ảnh, nộp cùng bàn giao |

---

## Phần B6 — Tài liệu và bàn giao

| Mã | Vì sao có việc này | Làm cụ thể | Coi là xong khi |
|---|---|---|---|
| B6-01 | Cấu trúc mới chỉ sống được nếu người viết tính năng biết đặt code vào đâu | `README`: thư mục nào chứa gì, thêm màn hình mới thì đặt ở đâu | Người mới đọc là biết đặt file |
| B6-02 | Đây là phần **bảo vệ goal 3 của mui** (thêm code Eminel không ảnh hưởng E-Smart) — nếu không viết thành luật thì vài tháng nữa gói chung lại thành nồi lẩu | Viết 3 kỷ luật: sửa gói chung chỉ được cộng thêm · khác biệt 2 app xử lý bằng override chứ không rẽ nhánh theo tên app · chỉ nâng lên `packages/` khi từ 2 app trở lên dùng | 3 điều nằm trong repo, không phải trong đầu người làm |
| B6-03 | Bàn giao miệng giữa chừng dễ rơi | Buổi bàn giao có mặt người sẽ viết tính năng Eminel | Người nhận tự dựng được môi trường và chạy được 2 app |

---

## Phần C — Refactor E-Smart

**Vì sao nằm sau mảng B**: mui ghi rõ refactor làm **sau khi dựng xong môi trường phát triển**; thêm nữa, có app thứ hai chạy thật rồi mới biết chỗ nào thật sự dùng chung — refactor trước là đoán mò.

| Mã | Vì sao có việc này | Làm cụ thể | Coi là xong khi |
|---|---|---|---|
| C-02 | Không có danh sách đầy đủ thì đổi tên kiểu nhặt được cái nào đổi cái đó | Liệt kê model trong `domain/models` (thư mục `domain/` có 168 file) | Có danh sách đầy đủ |
| C-03 | Đổi tên phía app mà lệch tên phía backend thì người sau đọc code càng rối | Đối chiếu tên model với tên trường API | Mỗi model có cột "tên phía BE" |
| C-04 | mui yêu cầu **review** việc đổi tên, tức là cần bảng để duyệt chứ không phải một PR đã sửa sẵn | Bảng "tên hiện tại → tên đề xuất → lý do" | Bảng gửi được cho mui, **code chưa đụng** |
| C-05 | Đổi tên là việc dễ gây tranh cãi, cần một người trong nhóm phản biện trước khi ra khách | Dev2 review bảng | Đã xử lý hết ý kiến |
| C-06 | Đổi tên hàng loạt khi chưa duyệt = xung đột merge lớn với nhánh khác | Gửi mui duyệt, phản ánh ý kiến | Có duyệt bằng văn bản |
| C-08 | Kỷ luật đã đặt ở B6-02: chỉ nâng lên gói chung khi từ 2 app trở lên dùng — giờ mới có đủ 2 app để kiểm | Rà chỗ trùng lặp giữa 2 app | Có danh sách ứng viên nâng lên |
| C-09 | Nâng xong phải chứng minh cả 2 app còn chạy | Nâng lên `packages/`, analyze, build lại 2 app | 2 app build sạch |
| C-11 | Không chốt danh mục token thì mỗi người đặt một kiểu tên | Chốt: màu, chữ, khoảng cách, bo góc | Danh mục được duyệt |
| C-12 | Màu đang viết cứng rải rác thì không đổi theme được | Gom màu cứng của E-Smart về token | Không còn màu cứng trong widget chung |
| C-13 | Cần bảng màu thứ hai mới chứng minh được theme tách thật | Bảng màu Eminel | Có bản của mui, hoặc bản tạm có ghi rõ là tạm |
| C-14 | Đây là bước biến "có gói theme" thành "đổi màu là đổi được thật" | Áp token vào widget chung | Đổi bảng màu là toàn app đổi theo |
| C-15 | Repo có sẵn cả `light_theme` lẫn `dark_theme`, sửa theme mà chỉ xem chế độ sáng là bỏ sót một nửa | Kiểm mắt 2 app ở cả 2 chế độ | Không có màn hình nào chữ chìm vào nền |

---

## Phần cuối — Ba con số nên nhớ khi đọc WBS này

| Con số | Ý nghĩa |
|---|---|
| **25 MD** | Khối lượng thật của mảng B, so với **5 ngày** mui dự kiến cho tuần implement. Chênh lệch này phải được chốt trước 24/08 |
| **0 file test** | Toàn bộ lưới an toàn của đợt này là hồi quy thủ công (B5) + build cả 2 app mỗi PR (B4-03) |
| **481 file / 30 nhóm widget / 20 file server** | Ba con số quyết định độ lớn của B1, B2 — nếu source thay đổi nhiều trước khi bắt tay làm thì phải đếm lại và điều chỉnh ước lượng |
