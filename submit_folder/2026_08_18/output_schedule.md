# Task tái cấu trúc source app — nhật ký điều tra & trạng thái (chốt 2026-08-18, cập nhật 2026-08-19)

> Mục đích của file: phiên sau (hoặc người khác) đọc file này là **làm tiếp được ngay**, không phải điều tra lại.
> Tài liệu nộp khách là `CLIENT_REPORT_APP_RESTRUCTURE_ja.md` (tiếng Nhật). File này là **ghi chú nội bộ**.

---

## 1. Đề bài của mui

Nguồn: `requirements/app_source_change.md` — yêu cầu đổi cấu trúc thư mục repo **`syp-eminelstandard-app`** để nhét app Eminel (E-GW) vào sống chung với app E-Smart (ESTA) hiện có.

**Ba mục tiêu (nguyên văn):**

| # | Nguyên văn | Nghĩa |
|---|---|---|
| 1 | 「アプリ層と共通層に分け、複数のアプリの管理を1つのrepositoryで行えること」 | Tách **tầng app** và **tầng chung**, quản nhiều app trong **một** repo; dễ thêm code về sau |
| 2 | 「ESTAアプリとEMINELアプリをそれぞれ別アプリとしてビルドできること」 | Build ra **2 app riêng** (khác applicationId, lên 2 store khác nhau) |
| 3 | 「EMINELアプリのコードを付け足す際に、ESTAアプリの開発に影響がないこと」 | Thêm code cho Eminel **không ảnh hưởng việc phát triển** ESTA (và ngược lại) |

**Bối cảnh (背景)**: 「共通要素を**使いまわしたい**」 — UI要素 · ログイン · ESTAとの共通ロジック; và 「アプリストアは別なので、アプリビルドの**出し分け**を行いたい」.

⚠️ **Đọc kỹ chỗ này**: mui **không** yêu cầu "2 app không liên quan gì nhau". Mui yêu cầu **phải có tầng chung** và **muốn dùng lại**. Cái phải độc lập là **bản build** (goal 2) và **việc phát triển** (goal 3).

### ✅ Cách hiểu đề bài đã được mui xác nhận (QA Notion, phát hiện 2026-08-20)

🔍 Nguồn: Notion — QAデータベース, phiếu **No. 7** 「「依頼: モバイルアプリ構成の変更」について確認」
→ 質問者 Bui Trong Dat (SYP), 起票 **2026-08-03 19:22** — tức **cùng ngày** mui giao đề bài
→ nguyên văn (回答内容): 「**認識に相違ない**」 (*cách hiểu không có gì sai lệch*)
→ ステータス **完了**, chốt **2026-08-13 12:34** (更新日時)
→ ⚠️ ô **回答者 để trống** — Notion không ghi ai trả lời (theo user: phía mui quên điền). Nên khi trích **không gán tên ai**; trọng lượng câu này thấp hơn các phiếu có tên người trả lời.

**Nghĩa**: phần **hiểu đề bài** đã được chốt — không phải chốt bản đề xuất. Bản `CLIENT_REPORT_APP_RESTRUCTURE_ja.md` nộp 18/08 vẫn đang ở bước ② của lịch (mui review 17–19/8 → phản ánh 20–21/8).

🔸 **CHƯA kiểm chứng**: ô `質問内容` của phiếu để trống, nội dung "cách hiểu" nằm ở **body trang** mà chưa đọc. Nhiều khả năng nó trùng với 3 goal + ghi chú ⚠️ ở mục 1 này — nhưng **chưa đối chiếu**, đừng coi là đã xác minh từng câu.

**Lịch mui đưa ra:** ① đề xuất cấu trúc (SYP) 8/3–8/14 → ② mui review 8/17–8/19, phản ánh 8/20–8/21 → ③ implement (SYP) tuần 8/24–8/28. Ta đang ở **cuối bước ①/đầu bước ②**.

**File `requirements/chokkin_irai.md`** = chiến lược chia branch cho phase này — **đã làm xong, không cần quan tâm trong task này**.

**Chưa đọc**: `requirements/Eminelアプリ分割について.pdf` và 2 ảnh trong `requirements/images/`.

---

## 2. Bản đã nộp cho mui

`CLIENT_REPORT_APP_RESTRUCTURE_ja.md` — bản nháp để review, 8 chương: ① bối cảnh & yêu cầu ② cách tiếp cận & 3 nguồn điều tra ③ bộ tiêu chí dẫn đường ④ phân tích & căn cứ chọn kiến trúc ⑤ giải pháp đề xuất (phần lõi) ⑥ rủi ro ⑦ câu hỏi gửi khách ⑧ phụ lục.

Lõi của đề xuất: **monorepo hai tầng** — `apps/{e-smart-app, e-gw-app}` + `packages/{theme, ui_components, utils, data, features/common}`; E-Smart **bê nguyên trạng** sang `apps/e-smart-app`; chỉ tách phần **thật sự dùng chung**, không tách nhỏ từng feature.

---

## 3. Nguồn tham khảo đang có trên máy (`sources/`)

| Thư mục | Là gì | Dùng để làm gì |
|---|---|---|
| `kurashi-for-energy` | **Repo mẫu do chính mui chỉ định** trong đề bài — app năng lượng khác của mui, đang chạy thật | Chuẩn kiến trúc app: cách chia `apps/` + `packages/`, quy tắc trong `.claude/*.md` |
| `kurashi-data-package` | Gói **tầng dữ liệu** của nền Kurashi (repo riêng, private) | Hiểu mô hình "tầng dữ liệu nằm ngoài repo app" |
| `syp-eminelstandard-app-syp-dev` | Source E-Smart hiện tại — **đối tượng bị tái cấu trúc** | Khảo sát hiện trạng |
| `eminel_gw_project` | Tài liệu dự án E-GW (requirement app 23 section) | Căn cứ phân loại chung / riêng |

---

## 4. Sự thật đã kiểm chứng (số liệu tự đếm trên đĩa, không lấy từ báo cáo)

### 4.1. E-Smart hiện tại — `syp-eminelstandard-app-syp-dev`

| Hạng mục | Con số / sự thật |
|---|---|
| Quy mô | **481 file Dart** trong repo, **73.720 dòng** viết tay (`.g.dart`/`.freezed.dart` bị gitignore ở `.gitignore:49-50`, nên báo cáo ghi "881 file" là con số **sau khi chạy build_runner**) |
| Cách tổ chức | Theo **tầng**, không theo feature: `lib/{data, domain, presentation, server, utils}` |
| Chi tiết tầng | `data` 131 file / 5.088 dòng · `server` 20 / 3.769 · `domain` 168 / 9.597 · `presentation` 127 / 37.760 · `utils` 30 / 6.530 |
| Điều hướng | **Chưa dùng `go_router`**; 33 chỗ gọi `Navigator.push*` trực tiếp + `utils/navigator_util.dart` |
| Test | **Không có thư mục `test/`, 0 file test** |
| Build | Chỉ 1 project Android/iOS; `applicationId` truyền lúc build: `android/app/build.gradle:63` → `applicationId dartEnvironmentVariables.APP_ID`; iOS → `PRODUCT_BUNDLE_IDENTIFIER = "$(APP_ID)"`. **Không dùng Gradle flavor** |
| Mã định danh thật | iOS prod = **`jp.co.hokkaido-gas.esta`**, dev = `jp.co.hokkaido-gas.esta.dev` (`lib/firebase_options.dart:79/96`, `.vscode/launch.json:28`). Phía **Android lấy từ `.env` không commit** → chỉ có `.sample.env` |
| Firebase | Đã đa môi trường sẵn: project `esta-dev-1` và `esta-prod` |
| Stack | `hooks_riverpod ^2.5.1`, `riverpod ^2.6.1`, `retrofit ^4.1`, `dio ^5.4`, `flutter_hooks`; đăng nhập qua **WebView** (`webview_flutter`), **không** dùng Auth0/Amplify |
| Màn hình hiện có | `presentation/pages/`: automation · control · dashboard · device · device_error · dr · main · mypage · news · notice · onboarding · pdf · point · room_monitoring · sensor · sign_in · splash · survey · tagtag · temperature_and_humidity · tip · user_detail · welcome |
| REST client | `lib/server/rest_client/` 15 file: user 171 dòng · device 226 · automation 81 · dashboard 74 · tip 48 · dr 46 · news 41 · survey 40 · point 38 · mobile_app 35 · audit_log 34 · integration 33 · s3 31 · contact 26 |
| 見守り | **Không có** trong E-Smart (grep `見守り`/`mimamori` = 0) |

### 4.2. Repo mẫu — `kurashi-for-energy`

- Cấu trúc thật: `apps/energy_shizgas` + `packages/{theme, ui_components, utils, features/common}` — **trùng đúng tên** với đề xuất của mình.
- `melos.yaml` quản workspace theo glob: `apps/*`, `packages/*`, `packages/**`.
- Tài liệu chuẩn nội bộ ở `.claude/`: `architecture.md` (339 dòng) · `routing.md` (340) · `design-system.md` · `error-handling.md` · `storage.md` · `CONTRIBUTING.md`.
- **`packages/features/common/lib/`** đang chứa: `announcement`, `survey`, `contact`, `faq`, `app_state`, `document_download` — và **0 file nào import `material.dart`** ⇒ package chung **không chứa UI**.
- `packages/ui_components/lib/`: buttons · charts · **error** (`error_view.dart`, `async_value_builder.dart`) · image_viewer · inputs · lists · modals · tags.
- `apps/energy_shizgas/lib/` **không có thư mục `data/`** — toàn bộ tầng dữ liệu đến từ gói ngoài.
- Quy tắc trong `architecture.md:11`: `apps/` = màn hình · `packages/feature-*` = domain + state (**không UI**) · **datapackage (thư viện ngoài)** = repository実装 · Auth · API client.
- Cơ chế DI: gom toàn bộ provider trừu tượng vào **một file `providers.dart`**, app override lúc khởi động (`architecture.md` mục providers.dart パターン).

### 4.3. Gói dữ liệu nền — `kurashi-data-package`

- README tự khai: *"the data layer of the **Kurashi platform** and the API client"*.
- Quy mô **511 file Dart / 79.886 dòng** — lớn hơn cả app E-Smart.
- `lib/server/` có **nhiều REST client theo brand**: `rest_client`, `rest_common_client`, `rest_client_shizgas`, `rest_client_cems`.
- Deps: `hooks_riverpod ^3.1.0`, sdk `>=3.9.0`, `freezed 3.x`, `retrofit ^4.9`, `dio ^5.9`, **`amplify_auth_cognito`**, **`auth0_flutter`**.
- ⭐ **Phát hiện quan trọng**: E-Smart và gói này **cùng một khuôn nhà** — cùng có `server/mui_service.dart`, `server/mui_api_endpoint.dart`, `server/rest_client/`, `data/{entities, datastores}`; mở 2 file `mui_service.dart` ra thấy cùng lối viết, cùng thứ tự import.

---

## 5. Kết luận đã chốt trong phiên (kèm lý do)

**① Theo cách chia của `kurashi-for-energy`: ĐƯỢC.** `apps/` + `packages/{theme, ui_components, utils, features/common}` áp thẳng cho E-Smart/E-GW, đúng cái đề xuất đang theo.

**② KHÔNG dùng gói `kurashi_data`, và KHÔNG tách tầng dữ liệu ra repo riêng ở phase này** → làm **`packages/data`** ngay trong repo.
- Không dùng `kurashi_data` vì: đó là tầng dữ liệu của **nền Kurashi** (API shizgas/cems), xác thực bằng Auth0+Cognito trong khi E-Smart đăng nhập qua WebView TagTag; và kéo theo phải nâng cả stack (sdk 3.9 / riverpod 3.x / freezed 3.x).
- Không tách repo riêng vì: repo riêng chỉ đáng khi cần dùng chung **giữa nhiều repo**, ở đây 2 app **cùng một repo**; tách ra là thêm repo + quyền + version + CI + PR hai nơi, trong khi ước lượng đã 15–27 người-ngày so với lịch ~5 ngày; và E-Smart **không có test nào** để làm lưới an toàn.
- Vẫn giữ **đúng khuôn** của `kurashi_data` (`data/{entities,datastores,providers}` + `domain/{models,repositories}` + `server/{rest_client,...}`) ⇒ sau này muốn tách ra ngoài thì **nhấc nguyên gói**.

**③ KHÔNG hỏi mui về "kế hoạch đưa ESTA/E-GW lên nền dùng chung".** Từng định hỏi, sau đó tự rút: căn cứ chỉ là **tên một nhánh git** (`feature-saas-standard-app`) — quá mỏng; giải pháp `packages/data` đã tự chống rủi ro đó; và dù mui trả lời "có" thì tuần implement cũng không đổi hướng kịp.

**④ Dùng chung tầng dữ liệu KHÔNG vi phạm goal 3.** Vì mui yêu cầu **phải có** tầng chung (goal 1) và muốn dùng lại (背景); goal 3 nói về **ảnh hưởng tới việc phát triển**, không phải "cấm liên quan". Hai app vẫn build/chạy/phát hành độc lập: package được **biên dịch vào từng binary**, mỗi app có `android/`+`ios/`, `applicationId`, Firebase riêng.
Bốn kỷ luật để giữ goal 3 (áp cho **mọi** package chung, không riêng `data`):
1. Sửa package chung phải **cộng thêm, không đổi hành vi cũ**. *(chưa viết vào báo cáo)*
2. Khác biệt giữa 2 app xử lý bằng **inject/override ở tầng app**, cấm `if (app == …)` bên trong package. *(đã có ở §5.4)*
3. Cái gì chỉ 1 app cần thì **để trong app đó**, chỉ nâng lên `packages/` khi thật sự ≥2 app dùng. *(chưa viết vào báo cáo)*
3. **CI build cả 2 app trên mỗi PR** — bù cho việc không có test. *(§5.5 mới nói CI có tham số chọn app, chưa nói "build cả hai mỗi PR")*

---

## 6. Đã sửa gì trong báo cáo ngày 18/08

| Vị trí | Nội dung sửa |
|---|---|
| §4.3 | Thêm **6 hàng căn cứ** phân loại cho: 設定(A2) · ヘルプ(E3) · アプリログ(E2) · システムエラー(E1) · DR(B5) · 非機能(E4) |
| §5.3 | Viết lại bảng: 3 nhóm → **5 nhóm** (chung-logic / chung-UI / chung-hạ tầng / E-Smart riêng / Eminel riêng). Bỏ hàng 「本構成の分類対象外」 **và** bỏ luôn câu 「A〜E全セクションを漏れなく…」 (theo chỉ thị) |
| §5.1 · §5.2 | Thêm **`packages/data`** vào sơ đồ và cây thư mục; gỡ "REST client dùng chung" khỏi `utils`; thêm đoạn giải thích **vì sao tách `packages/data`**; căn thẳng cột chú thích trong cây |
| §7 câu 2 | Chỉ hỏi **applicationId phía Android**, nêu rõ iOS đã tự xác nhận từ repo |
| §2.2 · §8.1 *(19/08)* | 「24件」 → **23件** tài liệu requirement; §8.1 liệt kê rõ A01–A04 · B01–B06 · C01–C05 · D01–D04 · E01–E04 (đếm trực tiếp `docs/eminel/3_requirements/app/` tại `1100487`) |
| §4.1 *(19/08)* | Ô 「規模」 viết lại lấy **481 file viết tay / ~74.000 dòng** làm số chính, 881 chỉ là số **sau khi chạy sinh code** (file sinh ra không commit) — để mui tự clone đếm ra cùng con số |
| §5.3 *(19/08)* | Thêm ghi chú 「共通」の範囲について: chung = **logic/state/data/部品 UI**, `features/common` **không có màn hình**, nên màn hình đăng nhập/お知らせ **vẫn dựng lại ở từng app** — chặn cách hiểu "dùng lại được cả màn hình" |

---

## 7. Việc còn treo — làm tiếp từ đây

1. **Hai kỷ luật bảo vệ goal 3** (mục 5-④: "sửa chỉ cộng thêm" và "chỉ nâng lên `packages/` khi ≥2 app dùng") + "CI build cả 2 app mỗi PR" — **quyết định 19/08: KHÔNG đưa vào bản nộp**, đây là kỷ luật nội bộ lúc implement, không đổi quyết định của người đọc.
2. **Chưa đọc**: `requirements/Eminelアプリ分割について.pdf` + 2 ảnh; nội dung 2 bản nháp spec `c02_グラフ.md`/`c03_レポート.md` bên `eminel_gw_project`; skill `draft-app-spec`.
3. **Chưa quyết**: thư mục `2026_08_18/` này có nộp nguyên cho mui không.

> **Đã đóng 19/08 — không mở lại:**
> - *Lệch phiên bản Riverpod (kurashi 3.x ↔ E-Smart 2.5/2.6)*: **không phải việc**. Kurashi chỉ là repo mẫu về cách chia thư mục; đã chốt không dùng `kurashi_data` (mục 5-②) nên E-GW cứ dùng nguyên stack E-Smart (`hooks_riverpod ^2.5.1`). Báo cáo không nhắc chữ riverpod nào — không có gì phải vá. (Ghi chú cũ diễn đạt sai rằng nó "ảnh hưởng ước lượng 15–27 người-ngày"; **15–27 người-ngày là ước lượng CẢ đợt tái cấu trúc**, §5.7 báo cáo.)
> - *Tiêu chí user chốt 19/08*: **chỉ sửa cái sai đến mức đổi quyết định của người đọc**; rà đến khi hết lỗi thì không bao giờ nộp được.

---

## 8. Cảnh báo cho phiên sau

- **File này viết bằng tiếng Việt và đang nằm trong `submit_folder/`** — nếu nộp cả thư mục cho mui thì **phải bỏ file này ra** (và cả `requirements/` nếu không muốn gửi lại đề bài của chính họ).
- Báo cáo `CLIENT_REPORT_APP_RESTRUCTURE_ja.md` là **tiếng Nhật gửi khách**: không đưa ký hiệu nội bộ, đường dẫn repo cá nhân hay dấu 🔴 vào.
- `kurashi-for-energy` và `kurashi-data-package` là **repo của mui — chỉ đọc, không sửa**.
- Mọi con số ở mục 4 đều đếm trực tiếp trên đĩa ngày **2026-08-18**; nếu mui cập nhật source thì phải đếm lại trước khi trích.
