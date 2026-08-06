# Báo cáo phán định batch hệ cũ — nhóm 配信・通知系 (phát nội dung & thông báo, 4 batch) — đối chiếu e-smart & yêu cầu E-GW

> 🔰 **Người mới vào dự án**: bảng ngay dưới đây là thông tin quản lý tài liệu — đọc **mục 0** bên dưới bảng trước, rồi hãy quay lại.

| | |
|---|---|
| Ngày lập | 2026-08-06 (ngày điều tra: 2026-08-04) |
| Người lập | Bui Trong Dat (SYP) + AI hỗ trợ điều tra |
| Vị trí tài liệu | **Phân tập (分冊)** — bộ phán định batch hệ cũ (toàn bộ 11 batch, 3 nhóm) được chia thành 3 tập tương ứng 3 task điều tra trên Notion; tập này phụ trách nhóm **配信・通知系** gồm **4 batch #1–#4**. Hai tập còn lại: 外部連携・受信系（Xzilla取込） 3 batch (#5–#7) ・ CSV・ZIPエクスポート系 4 batch (#8–#11). Số hiệu batch đánh liên tục xuyên suốt 11 batch, dùng chung giữa các tập và giữa bản JP/VN |
| Nhiệm vụ | Xét 4 batch nhóm **配信・通知系** trong `legacy_eminel_docs/docs/03_API仕様/04_バッチ一覧.md` (đều thuộc server `conciergesv` của hệ cũ) — cái nào **đã có sẵn trong e-smart** (kèm trích code), cái nào phải **tạo mới**, cái nào **bỏ** (kèm các bước làm), căn cứ yêu cầu E-GW trong `eminel_gw_project/docs/eminel` |
| Repo đối chiếu | `legacy_eminel_docs` @ `ccd8f56` ・ `eminel_gw_project` @ `fbc0af0` ・ `syp-eminelstandard-backend` @ `dc39aa39` (branch `gw-syp-dev`) ・ `syp-eminelstandard-web-admin` @ `e550326` (branch `gw-syp-dev`) ・ `syp-eminelstandard-app-syp-dev` (snapshot, không có git) — tất cả trong thư mục `sources/`. ※Điều tra thực hiện tại `eminel_gw_project` @ `788b438`; ngày 2026-08-06 đã đối chiếu lại toàn bộ trích dẫn với `fbc0af0` — khác biệt chỉ nằm trong `docs/eminel/3_requirements/app/`, số dòng trích B05/D03 đã cập nhật theo `fbc0af0`; kết luận phán định không đổi |

## 0. Tài liệu này là gì? (đọc trước nếu bạn mới vào dự án)

**Bối cảnh một đoạn**: **E-GW (EMINEL Gateway)** là dự án làm hai việc cho dịch vụ EMINEL (khách hàng cuối: 北海道ガス／北ガス): **(1)** thay gateway — *gateway* (viết tắt **GW**) là chiếc hộp đặt trong nhà khách, trung chuyển dữ liệu giữa cảm biến/máy sưởi và server; hộp hiện tại của hãng Maxell sẽ được thay bằng gateway do mui Lab làm; **(2)** **chuyển phần máy chủ sang nền tảng e-smart** — hệ đang chạy thương mại của 北ガス (tên khác: **ESTA**, **EMINEL-Smart** — một hệ, ba tên). Hệ EMINEL **cũ** có vài chục "batch" chạy nền; khi làm server mới trên nền e-smart, phải trả lời: batch nào **e-smart đã có thứ tương đương** (đỡ làm — nhưng không phải 0 công, xem tiền đề §2), batch nào **phải làm mới**, batch nào **không cần nữa**.

📖 **"Batch" là gì?** Chương trình không có giao diện, hệ thống **tự chạy theo lịch** (như hẹn giờ) hoặc theo sự kiện: tính toán số liệu, gửi thông báo hàng loạt, nhận/xuất file dữ liệu… Người dùng không nhìn thấy batch, nhưng biểu đồ có số liệu, điện thoại có thông báo — là nhờ chúng.

**File này sinh ra để làm gì**: trả lời câu hỏi trên cho **4 batch nhóm 配信・通知系** (*phát nội dung & thông báo*): cấp điểm thưởng エコ暖房 (#1), phát lời khuyên tiết kiệm năng lượng 省エネアドバイス (#2), gửi push — thông báo đẩy tới điện thoại (#3), điều khiển DR (#4 — xem Chú giải nhanh bên dưới). Mỗi batch được phán định: **dùng lại của e-smart / tạo mới / bỏ**, viết rõ **BỎ gì – GIỮ gì – THAY bằng gì**. Chỗ nào nói "e-smart đã có" thì **dán trích đoạn code thật và giải thích từng nhóm code**; mỗi batch có **sơ đồ luồng hệ cũ và hệ mới** đi tới tận bảng database.

**Cách đọc**:
- Vội → đọc **§1** (bảng tóm tắt — kết quả cho cả 4 batch, mỗi batch một dòng + 2 việc cần làm ngay).
- Muốn hiểu căn cứ → **§2** (tiền đề chung + "nền batch của e-smart" kèm code) rồi **§3** (mở đầu bằng bảng đối chiếu cũ↔mới ở §3.1; sau đó §3.2–§3.5 = chi tiết từng batch theo khung cố định: *mục đích → phán định BỎ–GIỮ–THAY + vì sao đề xuất vậy → sơ đồ + code hệ cũ → e-smart có gì → E-GW cần gì → sơ đồ hệ mới → cách làm từng bước (kèm Vì sao) → kiểm thử*).
- Muốn biết việc gì còn treo, ai làm gì tiếp → **§4**. Tra nguồn → **§5**. Định **trích dẫn lại** nội dung nào → đọc mục **⚠️ Giới hạn** (ngay dưới đây) trước.

**Chú giải nhanh** (thuật ngữ dùng xuyên suốt — đọc lướt một lần; trong bài, mỗi mã hiệu xuất hiện đều được chú giải lại ngắn gọn theo ngữ cảnh):

- **e-smart = ESTA = EMINEL-Smart**: một hệ, ba tên; tên trong code là ESTA. Gồm 3 repo: `backend` (TypeScript trên AWS), `web-admin` (màn hình quản trị, Nuxt 3), `app` (Flutter).
- **Hệ cũ (旧EMINEL)** gồm 3 khối server (đều CakePHP/PostgreSQL): **`conciergesv`** — API cho app + toàn bộ batch nghiệp vụ (cả 4 batch của báo cáo này); **`eminelsv`** — màn hình quản trị vận hành; **`hemssv`** — giao tiếp với gateway. ⚠️ Đừng nhầm `hemssv` (hệ cũ) với **HEMS-SV (m2-cloud)** — thành phần MỚI do mui phát triển cho E-GW, chỉ trùng tên.
- **Stack AWS của e-smart** (gặp nhiều ở phần dẫn chứng code): **Lambda** = hàm chạy theo sự kiện, không có server thường trực; **DynamoDB** = database NoSQL; **Step Functions** = xâu nhiều Lambda thành luồng nhiều bước, mỗi luồng gọi là *state machine*; **EventBridge Scheduler** = bộ hẹn giờ kích hoạt batch; **S3** = kho file; **SFTP** = giao thức chép file mã hóa qua SSH. Hạ tầng khai báo trong `template*.yaml` (AWS SAM).
- **FCM** (Firebase Cloud Messaging) = dịch vụ của Google chuyên đẩy thông báo tới app điện thoại; muốn gửi phải có **token** — "địa chỉ nhận thông báo" riêng của từng máy, server lưu trong bảng token.
- **DR** = デマンドレスポンス (Demand Response) — bên bán năng lượng yêu cầu hộ gia đình tạm giảm/dịch giờ dùng điện lúc cao điểm (thường đổi lấy điểm thưởng); "điều khiển DR" = server tự điều chỉnh thiết bị trong nhà theo yêu cầu đó.
- **PI連携** = liên kết **PointInfinity** — hệ điểm thưởng của 北ガス. **TagTag** = nền tảng hội viên của 北ガス (cấp định danh + API dữ liệu sử dụng gas/điện).
- **劣後** = được lùi lại sau (sang 2027/4~) ・ **必須** = bắt buộc trong scope 2026 ・ **回答中** = trạng thái QA đang trả lời, chưa chốt.
- **Mã tham chiếu tài liệu**: `F-ES-xx`/`F-AD-xx` = mã chức năng trong 統合要件定義書 v1.2 (ES = server, AD = màn hình quản trị) ・ `A03/B05/D03…` = mã section bộ yêu cầu app E-GW (`3_requirements/app/`) ・ `CLD-xx` = mã vấn đề đang mở trong `20_open_issues.md` ・ **[G]** = file spec màn hình quản trị (`4_spec/admin/G_energy_advice.md` — 省エネアドバイス), `G-A-02`/`G-C-05`… = mã mục trong đó.
- Quy ước bảng 機能一覧 (`10_feature_list.md`): cột 劣後 đánh **✅ = lùi được sang 2027** (KHÔNG phải "trong scope"), ô trống = 今期必須.
- **cron** = bộ hẹn giờ chuẩn của server Linux; mỗi "dòng cron" khai báo một lịch chạy. Biểu thức dạng `cron(phút giờ ngày tháng ? năm)` — diễn giải tại chỗ khi xuất hiện.
- **Bảng QA gửi khách** = `requirements/qa_kitagas.md` trong workspace onboarding; "câu 2 / câu 3 / câu 5 / câu Dự phòng 1" = số câu trong bảng đó. Phân biệt với **QAデータベース Notion** = kênh hỏi–đáp nội bộ với mui (liệt kê ở §5).
- **Nhãn độ chắc** trong báo cáo: **確実** = tự kiểm chứng được trên tài liệu/code (với các khẳng định về e-smart: đã soi trực tiếp code backend/web-admin); ***推定*** = suy đoán có căn cứ, chưa kiểm chứng — không dùng làm quyết định cuối. Dẫn chứng viết sau ký hiệu 🔍, đường dẫn tính từ `sources/`. Trong văn xuôi, chỗ rút gọn ghi `…`; **trong khối code, các dòng/chỗ chỉ có `...` là ký hiệu lược bớt của báo cáo, không phải code** (comment tiếng Việt/Nhật trong khối cũng là chú thích của báo cáo thêm vào). Căn cứ hay gặp: "**grep X: 0 hit**" = tìm chuỗi X trong toàn bộ code không ra kết quả nào — cơ sở để khẳng định "không tồn tại trong code".

## ⚠️ Giới hạn & lưu ý xác thực (đọc trước khi trích dẫn lại)

1. Các khẳng định "e-smart có/không có X" đều đã **kiểm chứng trực tiếp trên code** `syp-eminelstandard-backend` + `syp-eminelstandard-web-admin` (branch `gw-syp-dev`). Repo app chỉ là snapshot không có git — số dòng phía app có thể trôi khi có bản mới.
2. ⚠️ Trước báo cáo này, dự án đã có bộ **tài liệu khảo sát ESTA** (`eminel_gw_project/docs/eminel-smart/`, 6 file — do mui lập khi khảo sát nền tảng e-smart). Lần này đối chiếu với code phát hiện **6 điểm tài liệu đó ghi lệch với code thực tế** (tính trên cả 3 nhóm batch); dưới đây là **3 điểm liên quan nhóm 配信・通知系** — 3 điểm còn lại (nhịp import 基幹, thời gian lock merge hội viên, vai trò bảng `CsvDownloadHistory`) nằm ở hai tập kia. Ai trích tài liệu khảo sát nên kiểm code trước:
   | Tài liệu khảo sát ghi | Code thực tế |
   |---|---|
   | Push 「最大500件/バッチ」 (`02_product_overview.md:121`) | Không có số 500 (500 bản ghi/trang là phân trang của batch HỆ CŨ); e-smart chia người nhận thành lô 10 000 user, gửi song song tối đa 100 lệnh/lúc (§3.4) |
   | 「自動化ルール実行（毎分）」 (`02_product_overview.md:85`) | Automation không chạy mỗi phút — mỗi rule có lịch tuần riêng tạo động (§2) |
   | Lambda runtime 「Node.js 20.x, arm64」 (`02_product_overview.md:49`) | `Runtime: nodejs24.x` (`template.yaml:181`; riêng CompatibleRuntimes của layer chung vẫn là nodejs20.x — dòng 3163) |
3. Ba trang QA Notion được trích (xem §5) đang ở trạng thái **回答中** và mới đọc qua ảnh chụp màn hình — trước khi trích lại phải mở trang gốc kiểm tra.
4. Phán định scope dựa trên tài liệu `eminel_gw_project` tại commit `fbc0af0` (điều tra tại `788b438`, đã đối chiếu lại toàn bộ trích dẫn ngày 2026-08-06); các điểm treo (T.B.D/QA) ghi rõ tại chỗ.

---

## 1. Kết luận tổng — tóm tắt từng batch

| # | Batch | Hệ cũ đang làm | e-smart có sẵn? | E-GW cần? | **Đề xuất** | Chi tiết |
|---|---|---|---|---|---|---|
| 1 | `DistributeMonthlyEcoPointsCommand` | Cấp 250 point エコ暖房 hàng tháng cho hộ có nhiệt độ cài đặt TB tháng ≤22℃, gọi PointInfinity (hệ điểm thưởng 北ガス) | **Một phần** — hạ tầng point/badge + gọi thẳng PointInfinity có trong code; logic phán định từ dữ liệu đo: không có | Cần (F-ES-04 エコ暖房ポイント / F-ES-09 PI連携; 必須 2026 — treo mâu thuẫn 劣後, câu 2 bảng QA gửi khách) | **BỎ code PHP batch cũ — GIỮ (dùng lại nguyên trạng) hạ tầng point/badge + PI連携 của e-smart — TẠO MỚI duy nhất phần logic phán định エコ暖房 từ dữ liệu đo** | §3.2 ・ 確実 |
| 2 | `PublishRegularEcoMissionsCommand` | Phát 19 loại 省エネアドバイス theo điều kiện phán định, cron cố định | **Không** (grep 0 hit) — Tip (nội dung admin soạn tay) là thứ gần nhất, không có advice engine | Cần, scope 2026 (F-ES-03 省エネアドバイス — 必須) | **BỎ batch + 19 dòng cron cố định + code 10 Publisher (tri thức 判定式 đã trích vào spec [G] — *spec màn quản trị 省エネアドバイス*) — GIỮ "đường ra" phát nội dung của Tip pattern (targeting + push + point) — TẠO MỚI judgment engine + schedule đặt từ màn quản trị** (chờ CLD-06 chốt gom 15種→7種) | §3.3 ・ 確実 |
| 3 | `DispatchPushMessagesCommand` | Gửi push mỗi phút từ hàng đợi DB, qua server trung gian PushCore | **Có, đầy đủ** — FCM trực tiếp + bảng token + 6 luồng push notice | Cần (Push 2026) | **BỎ batch cũ + hàng đợi DB + cron mỗi phút + server trung gian PushCore (không dựng lại) — GIỮ nghiệp vụ gửi push — THAY bằng hạ tầng FCM gửi thẳng sẵn có của e-smart**; hệ cũ chỉ để rà danh mục 通知種別 (loại thông báo) | §3.4 ・ 確実 (riêng vế PushCore→FCM là *推定*) |
| 4 | `ControlDrOperationCommand` | Mỗi phút ghi lệnh DR (giả dạng thao tác app user) vào DB cho GW poll (GW tự đến lấy) | **Có khung DR khác kiểu** — server chủ động điều khiển thiết bị nối cloud hãng, không có đường qua GW | Cần nhưng **劣後 → 2027/4以降** | **2026 KHÔNG code** — việc duy nhất là chốt "GW có giữ trạng thái DR không" (câu 5 bảng QA gửi khách); **2027 tạo mới trên khung DR e-smart** (lớp "sự kiện DR" dùng lại toàn bộ, chỉ thêm nhánh điều khiển qua GW); mẹo "giả dạng app user" tuyệt đối không kế thừa | §3.5 ・ 確実 |

**Ba lưu ý đọc kèm bảng**:
- Nhãn **確実/*推定*** (cột **Chi tiết**) chứng nhận phần **dữ kiện** (hệ cũ làm gì, e-smart có/không, scope) — phần **Đề xuất** luôn là phán đoán để team review. Cả 4 batch của tập này dữ kiện đều 確実 (riêng vế PushCore→FCM của #3 là *推定* vì code PushCore không nằm trong repo).
- Báo cáo chỉ phán định *làm gì / dùng lại gì*, **chưa ước lượng công số** — công số sẽ ước khi tách 1 batch = 1 task trên Notion (phương châm §2).
- Ngoài phạm vi 4 batch: e-smart **không tính sẵn report/集計 nào từ trước** (monthly report của app = hỏi tới đâu chuyển tiếp sang TagTag API tới đó, không lưu — 🔍 `syp-eminelstandard-backend/src/functions/api-dashboard/get-monthly-report-of-user.ts:21`) — tức nhóm batch **集計・計算系** của E-GW (nhóm khác của bảng batch, không thuộc báo cáo này) cũng sẽ không có sẵn gì để dùng lại.

**Hai việc rút ra cần làm ngay** (không chờ đủ spec):

1. **Báo mui danh sách "chức năng nên dùng tiếp hệ hiện hữu"** (hành động chung cho cả 3 tập) — đây KHÔNG phải tên trang QA mà là **câu hỏi phụ** nằm trong QA 「旧Eminel基盤継承＋EMINEL-smartサーバーは独立デプロイの確認」 (swan (mui), 回答中): *"ただし既存システムを使い続けたほうがいい機能があれば教えてほしいです"*. ⚠️ Trước khi trả lời cần xác nhận 「既存システム」 ý chỉ hệ nào; câu trả lời nên tách hai vế:
   - ① của hệ CŨ (旧EMINEL): **không có batch nào đáng dùng tiếp nguyên trạng** (kết luận xuyên suốt cả 11 batch — gồm 4 batch của tập này);
   - ② của hệ ĐANG CHẠY (e-smart): **4 ứng viên** — hạ tầng Push (FCM), hạ tầng point/badge + PI連携, luồng nhận Xzilla SFTP→S3→DynamoDB, cơ chế admin download/export (2 ứng viên đầu chính là căn cứ phán định #3/#1 của tập này; 2 ứng viên sau thuộc hai tập kia).
2. **Hai điểm treo phải bám**: CLD-06 (vấn đề đang mở: gom advice 15種→7種 — quyết định số loại advice phải làm ở #2), mâu thuẫn 必須/劣後 của ポイント (quyết scope của #1 — đã hỏi trong bảng QA gửi khách, câu 2).

---

## 2. Tiền đề chung khi phán định

**Phương châm đã chốt nội bộ mui (合宿 Day3, 2026-06-25)**: batch hiện hành 「いけてない」 — **làm lại chứ không bê nguyên** (「バッチ群（約46本…）をNotionに機能単位でタスク化…作り直す前提」), 1 batch = 1 task, đặt バッチボーン (khung rỗng) trước, chạy thật trước 結合フェーズ (*giai đoạn ghép nối chạy chung các thành phần* — mục tiêu trong tháng 9). Mảng batch/外部連携 dự kiến giao SYP. → *"Dùng lại"* trong báo cáo này nghĩa là **dùng cơ chế/hạ tầng/codebase của e-smart**, không phải copy code PHP của hệ cũ.
- 🔍 `eminel_gw_project/docs/eminel/2_management/minutes/20260625_egw_camp_day3.md` dòng 35, 51, 99–103, 147–149

**Tiền đề về nơi chạy** (3 ý):
- QA 「旧Eminel基盤継承＋EMINEL-smartサーバーは独立デプロイの確認」 (swan (mui), 回答中) trả lời tạm: *về cơ bản (基本的には) phát triển theo hướng hệ độc lập*. Vì vậy "dùng lại của e-smart" trong báo cáo = **dùng lại code/cơ chế/pattern**; nếu chốt deploy độc lập thì vẫn phải **dựng lại môi trường chạy** trên hạ tầng mới — "dùng lại" ≠ "0 công".
- Hiện trạng code: cả backend lẫn web-admin đều đã có branch `gw-syp-dev` nhưng **chưa có commit E-GW nào** (web-admin: `git log origin/main..gw-syp-dev` rỗng; backend: 15 commit gần nhất thuần e-smart) — mọi việc E-GW bắt đầu từ 0 trên nhánh này. 🔸 Cách làm nhiều khả năng là *viết thêm vào chính codebase e-smart* — suy từ trả lời tạm QA 「管理画面は独立か共通か（切替モード追加）の確認」 (masao takahashi (mui), 回答中: hướng chung source với e-smart), chưa phải quyết định thành văn.
- Lưu ý tách bạch: **"chung source" ≠ "chung môi trường chạy"** — hai câu hỏi độc lập, QA mới trả lời tạm cả hai.

**Khoảng cách công nghệ giữa hai thế hệ**:

| | Hệ cũ (`conciergesv`…) | e-smart (`syp-eminelstandard-backend`) |
|---|---|---|
| Ngôn ngữ/khung | PHP 8.0 / CakePHP 4.4 | TypeScript / AWS SAM + Lambda (Node.js 24 — `template.yaml:181`) |
| Database | PostgreSQL (partition theo ngày/tháng) | DynamoDB (PITR — backup hạ tầng — bật sẵn) |
| Cách chạy batch | cron trên server (`/etc/cron.d/eminel-mng-webap`), shell + flock chống chạy trùng | Step Functions + EventBridge (xem ngay dưới) |
| Nhận file ngoài | SFTP về đĩa server | SFTP → S3 → DynamoDB |

- 🔍 hệ cũ: `legacy_eminel_docs/docs/02_詳細設計/10_バッチ処理/cron設定概要.txt` dòng 1–37 ・ e-smart: `syp-eminelstandard-backend/template.yaml` (SAM), `02_product_overview.md` dòng 48–53

**Nền batch của e-smart trông thế nào** (điều E-GW sẽ thừa hưởng — mọi đường dẫn dưới đây tính từ `syp-eminelstandard-backend/`):

- **Chỉ có 3 lịch tĩnh** (đều `ScheduleV2`, timezone `Asia/Tokyo` — `template.yaml:9-11`): ① `BatchRunSequentiallyStateMachine` — nhập dữ liệu 基幹 (hệ nghiệp vụ lõi), `cron(5 0-7 * * ? *)` = phút :05 **mỗi giờ từ 0h–7h JST** (`template.yaml:853-888`, cron dòng 881–882); ② `BatchMigrationIntegratedDataStateMachine` — lấy dữ liệu thiết bị Rinnai/Noritz + export, `cron(0 8 * * ?)` (`template.yaml:2205-2240`, cron dòng 2233); ③ `BatchGetErrorDeviceInfoOfRinnaiStateMachine` — lỗi thiết bị, cùng 8:00 (`template.yaml:2966-2980`).
- **Mọi batch còn lại dùng lịch one-shot tạo động** (*one-shot = lịch đặt cho đúng một thời điểm, chạy xong tự xóa*). Đây là hàm dùng chung — 🔍 `src/layers/common/nodejs/services/put-schedule.ts:18-33`:

  ```ts
  const scheduler = new Scheduler();
  return await scheduler.createSchedule({
    FlexibleTimeWindow: { Mode: FlexibleTimeWindowMode.OFF },
    Name: scheduleName,
    ScheduleExpression: scheduleExpression,          // vd cron(30 14 15 8 ? 2026) — một thời điểm cụ thể
    Target: { Arn: resourceArn, RoleArn: GENERIC_LAMBDA_ROLE_ARN, Input: JSON.stringify(inputData) },
    ScheduleExpressionTimezone: timezone ?? TZ,      // "??" = vế trái rỗng thì dùng vế phải
    ActionAfterCompletion: isDeleteAfterCompletion
      ? ActionAfterCompletion.DELETE                 // chạy xong TỰ XÓA lịch
      : ActionAfterCompletion.NONE,
    ...
  ```

  Giải thích từng phần:
  - (a) `createSchedule` đăng ký một lịch với EventBridge Scheduler; `ScheduleExpression` là thời điểm phát (build tại `src/layers/common/nodejs/utils/date-utils.ts:117` theo dạng `cron(phút giờ ngày tháng ? năm)` — đúng một lần); `Target.Arn` trỏ tới state machine/Lambda cần chạy kèm `Input`; `ActionAfterCompletion.DELETE` làm lịch tự hủy sau khi chạy.
  - (b) Ví dụ vận hành: admin tạo news → API đặt lịch phát (`src/functions/api-news/common.ts:207-209`); batch phát xong lại tự đặt tiếp lịch gửi push (`src/functions/batch-send-news-complete/app.ts:72-80`).
  - (c) Automation của user (tính năng user tự đặt quy tắc tự động hóa thiết bị trong app) cũng vậy — mỗi rule một lịch tuần riêng (`src/functions/api-automation/common.ts:115`).
  - (d) Không có polling mỗi phút (grep `rate(`: 0 hit — `rate(...)` là cách khai báo lịch lặp "mỗi N phút" của EventBridge, không xuất hiện lần nào).
- 💡 **Hệ quả cho E-GW**: yêu cầu [G] G-A-02 (*mục trong spec màn quản trị 省エネアドバイス: admin đặt được 定期配信スケジュール cho advice — điều hệ cũ không làm được vì cron cố định*) có lời giải kỹ thuật **sẵn trong nền e-smart** — chính là pattern one-shot scheduler này.

**Phạm vi SYP**: theo QA 「旧EMINEL調査範囲（conciergesv/eminelsv）とhemssv対象外の確認」 (swan (mui), 回答中) — `conciergesv`/`eminelsv` là đối tượng SYP **điều tra** (đúng việc báo cáo này làm), không phải phạm vi SYP phát triển tiếp trên hệ cũ; giao tiếp GW đi qua HEMS-SV (m2-cloud) do mui làm, spec chia sẻ sau.

**Quyết định scope 2026-06-10** (đã vào 決定ログ): 必須 = 暖房機能/暖房制御/照明アドバイス※/ポイント連携/グルーピング・レポート; 劣後 (→2027/4~) = 複合制御・DR・ダッシュボード・バッジ等. ※「照明アドバイス」 nghi là lỗi ghi của 省エネアドバイス (*推定*).
- 🔍 `eminel_gw_project/docs/eminel/2_management/22_decisions.md` dòng 30–31

**Chủ thể các bước trong §3**: trừ khi ghi khác, người thực hiện là **SYP**, code viết trên branch `gw-syp-dev` — đường dẫn file không ghi tên repo = `syp-eminelstandard-backend`, phần màn hình quản trị = `syp-eminelstandard-web-admin`; các bước "chốt/hỏi" đi theo kênh ghi ở §4. Nhân sự nhắc tên trong báo cáo: **swan, masao takahashi** (đều phía mui — người trả lời QAデータベース), **kihara** (mui — lead phần cứng/firmware GW).

---

## 3. Chi tiết từng batch

*(Quy ước dẫn nguồn trong §3: đường dẫn `…/src/Command/` = `legacy_eminel_docs/sources/conciergesv-develop/src/Command/…`; "cron dòng NN" = số dòng trong `legacy_eminel_docs/docs/02_詳細設計/10_バッチ処理/mng-webap_cron設定_20241029.txt`; đường dẫn không ghi tên repo = `syp-eminelstandard-backend`. **Comment tiếng Việt/Nhật và `...` trong khối code là chú thích/ký hiệu lược bớt của báo cáo**, không phải code gốc.)*

### 3.1 Chung cả nhóm: bảng đối chiếu tương quan hệ cũ ↔ hệ mới

Nhìn một phát biết mỗi thành phần nằm ở đâu trong mỗi thế hệ. Tên bảng phía e-smart đã xác minh bằng cách grep hằng môi trường `TABLE_*` trong `app.ts` của từng handler (*handler = hàm Lambda xử lý một việc*).

| Thành phần | Hệ cũ (`conciergesv` — PHP/PostgreSQL) | Hệ mới (e-smart/E-GW — Lambda/DynamoDB) |
|---|---|---|
| Đường gửi push | Hàng đợi DB `push_message_destinations`, cron mỗi phút đọc theo trang (500 bản ghi/trang) → server trung gian PushCore (`localhost:54650`) → FCM (*推定*) | Lambda preprocessing chia người nhận thành lô 10 000 user đẩy lên S3 → `batch-push-notice` gửi **thẳng FCM bằng firebase-admin**, tối đa 100 song song (không hàng đợi DB, không server trung gian) |
| Quản lý token push | device_token/FCM topic gắn theo bản ghi `push_message_destinations` | `TABLE_MOBILE_TOKEN_MANAGEMENT` (app đăng ký qua API `user/save_mobile_token`; token chết bị tự xóa lúc gửi) |
| Cờ cho phép nhận push | — (chưa xác minh trong phạm vi điều tra này) | `TABLE_USER_SETTING` (check lúc gửi — `push-notice-to-user.ts:19, 35-60`) |
| Sổ điểm thưởng | `s_141` (`ConEcoPoints` — cộng dồn theo năm tài chính) + `ConPointLinkLogs` (lịch sử cấp — căn cứ chống trùng) | `TABLE_POINT_BADGE_STATS` (khóa chống trùng theo sự kiện) + `TABLE_USER_BADGE_SUMMARY` (tổng lũy kế) + `TABLE_SYSTEM_STATS` (counter atomic đánh số 伝票) |
| Liên kết PointInfinity | `eminel_sv_lib-develop/src/PointInfinity/PointInfinity.php` (form CP932 + XML) | Lambda `give-point-to-point-infinity` (form Shift_JIS + XML — cùng họ giao thức) + Lambda tra số dư `get-point-quantity-from-point-infinity` |
| 省エネアドバイス | 19 dòng cron cố định + 10 lớp Publisher → ghi `ConEcoMissions`/`ConEcoMissionDestinations` (advice + đích nhận) + `PushMessages`/`PushMessageDestinations` (đăng ký push) | **Chưa tồn tại (#2 tạo mới)**. Gần nhất = Tip (`TABLE_TIP_STATS`/`TABLE_TIP_USER_ACTION` + chuỗi phát one-shot) |
| Lệnh DR | `ConDrOperations` (thiết lập chỉ lệnh) → cron mỗi phút ghi `instructions` (宅外制御指示) → GW poll qua `hemssv` | `TABLE_DR` (sự kiện) + `TABLE_DR_USER_ACTION` (người tham gia + trạng thái trước DR) + `TABLE_DR_STATS` (thống kê) → server gọi thẳng cloud hãng qua `controlDevice` (không qua GW) |
| Kích hoạt batch | cron cố định trong `/etc/cron.d/eminel-mng-webap` (mỗi phút ~ hàng tháng) | 3 lịch tĩnh `ScheduleV2` + lịch one-shot/lặp tạo động (§2) |

### 3.2 #1 `DistributeMonthlyEcoPointsCommand` — cấp エコ暖房ポイント hàng tháng

**Mục đích của batch**: thưởng điểm hàng tháng cho hộ gia đình đặt nhiệt độ sưởi vừa phải (trung bình tháng ≤22℃) — tức trả "phần thưởng" tự động cho hành vi tiết kiệm năng lượng của user.

**Phán định — BỎ gì, GIỮ gì, TẠO MỚI gì**: **BỎ = code PHP của batch cũ** (không port). **GIỮ (dùng lại nguyên trạng) = ① PI直接連携 + ② luồng cấp point/badge tập trung** — kèm sẵn chống trùng, transaction, rollback. **TẠO MỚI = duy nhất ③ logic phán định từ dữ liệu đo** — đúng phương châm 差分方式 (chỉ làm phần chênh lệch). *(Số ①②③ ứng với các mục trong phần "e-smart có sẵn không" bên dưới.)*

**Vì sao đề xuất vậy**:

- e-smart đã có sẵn cả gọi thẳng PointInfinity (Lambda `give-point-to-point-infinity`) lẫn luồng cấp point tập trung (`givePointBadgeForUser` — kèm chống trùng, transaction, rollback) — cùng khuôn với phần lõi của batch cũ, đã soi code xác nhận.
- Ngược lại, logic chọn hộ từ **dữ liệu đo** không tồn tại ở bất kỳ đâu trong e-smart (grep `energy|usage` trong luồng point: 0 hit) — khoảng trống duy nhất chính là chỗ này.
- Phương châm (合宿 Day3 — §2) là làm lại chứ không bê code, nên không có lý do giữ code PHP cũ.
- Khớp luôn với nhận định camp Day3: 「ESTAサーバーに既に実装がある可能性が高い → 差分があればやる」.

**Sơ đồ luồng hệ cũ** (確実):

```
cron 17:00 ngày 1 hàng tháng (cron dòng 113–114)
    ▼
DistributeMonthlyEcoPointsCommand
    ├─ đọc: s_104 (ConSensorMonthlyValues — giá trị TB tháng của cảm biến) …lọc hộ có nhiệt độ CÀI ĐẶT TB tháng trước ≤22.0℃
    ├─ đọc: ConPointLinkLogs (lịch sử cấp điểm) …loại người đã nhận trong tháng (chống trùng)
    ├─ ghi: s_141 (ConEcoPoints — điểm eco) …cộng 250pt theo năm tài chính (mốc tháng 4)
    ├─ ghi: ConPointLinkLogs …ghi lịch sử cấp
    └─ gọi ngoài: PointInfinity API …CÙNG transaction; PI lỗi → hoàn tác khách đó, chạy tiếp khách sau
```

Câu truy vấn chọn người được cấp *(cú pháp `fn(Query $q) => …` là hàm viết ngắn của PHP: nhận `$q`, trả về `$q` đã gắn thêm điều kiện)* — 🔍 `…/src/Command/DistributeMonthlyEcoPointsCommand.php:83-104`:

```php
$query = $this->ConCustomers->find()
    ...
    ->matching('ConSensorMonthlyValues', fn(Query $q) => $q
        ->where([
            '...C_DEVICE_TYPE' => ROOM_TEMP_SETTING,        // nhiệt độ CÀI ĐẶT
            '...C_ROOM_ID' => 0,
            '...' . $sensorMonthlyValuesColName . ' <=' => 22.0,  // TB tháng trước ≤ 22.0℃
        ]))
    ->notMatching('ConPointLinkLogs', fn(Query $q) => $q
        ->where(['reason' => $pointLinkReason]))            // 'monthly_eco_points_YYYYMM' — chống cấp trùng
```

**Chi tiết hệ cũ** (確実):

- Mỗi khách được cộng **250 point** (hằng `BENEFIT_POINTS = 250` — dòng 33); gọi **PointInfinity API trong cùng transaction** (dòng 116–188; *transaction = gói thao tác "được ăn cả ngã về không"*).
- Bảng thao tác (khai báo `fetchTable` dòng 48–51): `ConCustomers`・`ConSensorMonthlyValues` (`s_104`)・`ConEcoPoints` (`s_141`)・`ConPointLinkLogs`.
- ⚠️ Code + cron chạy **hàng tháng quanh năm, không có điều kiện mùa** — trong khi A03 (bộ yêu cầu app E-GW, section "Point") mô tả hiện hành là 「12〜3月」; lệch nhỏ cần nêu khi chốt spec (bước 1).

**e-smart có sẵn không — MỘT PHẦN, dẫn chứng code** (確実; đường dẫn từ `syp-eminelstandard-backend/`):

① **Gọi thẳng PointInfinity** — Lambda riêng `src/functions/give-point-to-point-infinity/app.ts` (khai báo `template.yaml:3282`, secret dòng 3289):

```ts
// dấu } mở đầu = phần trên của lệnh đã lược; đây là "destructuring": bóc các trường từ JSON ra biến
} = JSON.parse(process.env.POINT_INFINITY_SERVER_INFO as string);   // :15 — URL + TUKA_ID/KMT_ID… từ Secrets Manager
...
const fuyoRiyuSjisArray = Encoding.convert(fuyoRiyuUnicodeArray, {  // :35-39 — FUYO_RIYU (lý do cấp điểm)
  to: 'SJIS', from: 'UNICODE',                                      //   encode Shift_JIS thủ công
});
...
const regex = /<SYORI_STS>(.*?)<\/SYORI_STS>/;                      // :50 — parse XML trả về
if (!syoriStsValue || syoriStsValue !== '000') { ... return false; } // :56 — '000' = thành công
...
method: 'POST',                                                     // :92
headers: { 'Content-Type': 'application/x-www-form-urlencoded; charset=Shift_JIS' },  // :96
```

Từng nhóm: (a) cấu hình server PI + các ID cố định lấy từ Secrets Manager; (b) `FUYO_RIYU` (lý do cấp) phải encode **Shift_JIS** trước khi gửi; (c) response là **XML**, thành công khi `<SYORI_STS>` = `000`; (d) request là POST form. → **Cùng "họ giao thức" với hệ cũ** (hệ cũ: form CP932 — biến thể Shift_JIS trên Windows — + XML, URL `if0200.do` — tên IF trong tài liệu thiết kế là IF0200 — `eminel_sv_lib-develop/src/PointInfinity/PointInfinity.php:39, 65-71, 85-98`・`Api/InterfaceCode.php:20`); chuỗi "IF0200" không xuất hiện trong backend (là tên trên tài liệu). Lambda tra số dư đi kèm: `get-point-quantity-from-point-infinity/app.ts` (GET + tag `<ZNDK>` — dòng 32, 79; secret `template.yaml:2629`).

② **Luồng cấp point/badge tập trung** — `src/layers/common/nodejs/business-logic/give-point-badge-for-user.ts`:

```ts
export const givePointBadgeForUser = async (      // :57 — MỌI nơi cấp điểm đều gọi hàm này
  userId: string,
  pointBadgeStatsSk: string,                      // khóa chống trùng, vd 'login#2026-08', 'dr#<id>'
  settingGivePoint?: ISettingGivePoint, ...
...
// Rollback transaction items if there is an error // :296-303 — PI lỗi thì hoàn tác DynamoDB
if (writeOneTransactionFlag) {
  await writeOneTransaction(transactionRollbackItems);
}
```

Từng nhóm:
- (a) chữ ký hàm nhận `pointBadgeStatsSk` — khóa duy nhất từng-sự-kiện để **chống cấp trùng** (kiểm tra tại dòng 69; ghi vào `TABLE_POINT_BADGE_STATS`);
- (b) ghi điểm/badge bằng transaction DynamoDB (`TABLE_POINT_BADGE_STATS` + `TABLE_USER_BADGE_SUMMARY`); nếu bước gọi PI thất bại thì **rollback** (đúng pattern hệ cũ);
- (c) số 伝票 (DENPYO_NO — số phiếu gửi PI) lấy từ counter atomic trên `TABLE_SYSTEM_STATS` (dòng 390–409; tên bảng tại dòng 392);
- (d) model đi kèm: `PointBadgeMaster` / `PointBadgeStats` / `UserBadgeSummary` (`src/layers/common/nodejs/models/`);
- (e) người gọi hiện tại: login tháng đầu, đọc tip (`api-tip/read-tip.ts:68`), trả survey (`api-survey/answer-survey.ts:346`), kết thúc DR (`batch-end-dr/app.ts:86`), liên kết thiết bị, sau import hội viên, đạt mốc checklist (hoàn tất đăng ký app, nhập thông tin khách, tạo automation…).

③ **Cái KHÔNG có**: logic phán định từ **dữ liệu đo** — không nguồn dữ liệu cảm biến nào tham gia điều kiện cấp điểm (grep `energy|usage` trong luồng point: 0 hit) — e-smart chưa có khái niệm "dữ liệu đo từ GW".

**E-GW yêu cầu**: F-ES-04 (エコ暖房ポイント) + F-ES-09 (liên kết PointInfinity); ポイント連携 thuộc nhóm **必須 2026** theo 決定 6/10 — nhưng 機能一覧 lại đánh ✅劣後 (mâu thuẫn đã đưa vào bảng QA gửi khách, câu 2; giá trị điểm/điều kiện cho E-GW chưa chốt — A03 要確認). Camp day3 ghi hướng: PI連携 「バッチが実態。ESTAサーバーに既に実装がある可能性が高い → 差分があればやる」 — nay xác nhận trên code là đúng.
- 🔍 `eminel_gw_project/docs/eminel/3_requirements/00_integrated_requirements_v1.2.md` dòng 409, 414, 675–691 ・ `22_decisions.md:31` ・ `10_feature_list.md:93, 95` ・ camp day3:125 ・ `A03_point.md:48-102`

**Sơ đồ luồng hệ mới (đề xuất)**:

```
GW đo (nhiệt độ cài đặt) ──qua HEMS-SV (m2-cloud — server giao tiếp GW do mui làm)──▶ bảng TB-tháng-theo-hộ (MỚI, vai trò như s_104 cũ — phối hợp nhóm 集計)
    ▼ phát lịch ngày 1 hàng tháng (ScheduleV2 tĩnh MỚI trong template.yaml)
Lambda phán định (MỚI — chính là ③) …quét bảng tháng, lọc hộ ≤ ngưỡng
    ▼ givePointBadgeForUser(userId, 'eco_heating#YYYYMM', …)
give-point-badge-for-user.ts (DÙNG LẠI — ②)
    ├─ chống trùng: TABLE_POINT_BADGE_STATS  ├─ ghi sổ: TABLE_USER_BADGE_SUMMARY  └─ số 伝票: TABLE_SYSTEM_STATS
    ▼
Lambda give-point-to-point-infinity (DÙNG LẠI — ①) ──POST──▶ PointInfinity …lỗi thì rollback transaction
```

**Cách làm từng bước**:
1. Chốt spec nghiệp vụ qua QA/A03 (bộ yêu cầu app, section Point): giá trị điểm (250 giữ không?), ngưỡng (22℃?), có giới hạn mùa 12〜3月 không (nêu điểm lệch code-vs-A03 ở trên), và kết cục mâu thuẫn 必須/劣後 (câu 2 bảng QA).
   - *Vì sao*: phần tạo mới chỉ có ③, và toàn bộ tham số nghiệp vụ của ③ nằm ở đây — chưa chốt thì Lambda phán định không có spec để viết.
2. Chờ spec HEMS-SV (m2-cloud) để biết dữ liệu nhiệt độ cài đặt từ GW về server theo đường nào; thiết kế bảng tích lũy **trung bình tháng theo hộ** trên DynamoDB (vai trò tương đương `s_104` hệ cũ — sẽ thuộc nhóm batch 集計, phối hợp với nhóm đó).
   - *Vì sao*: e-smart chưa có "chỗ chứa" dữ liệu đo từ GW (③) — thiếu bảng đầu vào thì bước 3 không chạy được; phối hợp nhóm 集計 để tránh hai nhóm thiết kế trùng một bảng.
3. Viết Lambda phán định mới (folder mới trong `src/functions/`, đặt tên theo lệ `batch-*` sẵn có): quét bảng tháng → lọc ≤ ngưỡng → gọi `givePointBadgeForUser(userId, 'eco_heating#YYYYMM', …)`; chỉ cần thêm lý do cấp (FUYO_RIYU) mới vào `src/layers/common/nodejs/variables/constants.ts` (mẫu tại dòng 1756–1762).
   - *Vì sao*: chống trùng/transaction/PI/rollback đều đã nằm trong `givePointBadgeForUser` — phần mới chỉ là lớp mỏng "phán định rồi gọi".
4. Lịch: thêm 1 lịch tĩnh `ScheduleV2` hàng tháng trong `template.yaml` (theo mẫu 3 lịch tĩnh ở §2).
   - *Vì sao*: chu kỳ cố định ngày 1 hàng tháng, không có thao tác admin nào làm mốc để đặt one-shot — lịch tĩnh là cách đơn giản, dễ bảo trì nhất.
5. Kiểm thử: dựng dữ liệu tháng giả → chạy batch 2 lần liên tiếp xác nhận **không cấp trùng**; giả lập PI trả lỗi xác nhận **rollback**; đối chiếu số điểm với kết quả chạy tay query hệ cũ trên cùng dữ liệu (phân công テスト=mui／実装=SYP).
   - *Vì sao*: rủi ro thật của batch này gói trong 2 điểm "cấp trùng" và "lệch sổ khi PI lỗi"; đối chiếu query cũ giúp phát hiện hiểu sai điều kiện (nhiệt độ cài đặt vs nhiệt độ đo).

### 3.3 #2 `PublishRegularEcoMissionsCommand` — phát 省エネアドバイス định kỳ

**Mục đích của batch**: tự soi cách dùng của từng hộ (sưởi quá tay, quên hẹn giờ…) rồi chọn đúng hộ để gửi lời khuyên tiết kiệm năng lượng phù hợp (hiện 19 loại) — tạo "cú hích" để user hành động tiết kiệm.

**Phán định — BỎ gì, GIỮ gì, TẠO MỚI gì**: **BỎ = batch cũ + 19 dòng cron cố định + code PHP 10 Publisher** (tri thức 判定式 giữ lại qua bản trích trong [G]). **GIỮ (dùng lại) = "đường ra" phát nội dung** — targeting + push + point của Tip pattern và chuỗi phát one-shot. **TẠO MỚI = tầng phán định (advice engine) + phần đặt 定期配信スケジュール từ màn quản trị (G-A-02)**.

**Vì sao đề xuất vậy**:

- Đã grep xác nhận e-smart **không có** advice engine (0 hit thật) — không có gì để dùng lại thì tầng phán định bắt buộc phải tạo mới.
- Yêu cầu E-GW (spec [G] — màn quản trị 省エネアドバイス) đòi lịch phát định kỳ **chỉnh được từ màn quản trị** — 19 dòng cron viết chết trong file của hệ cũ không cách nào đáp ứng, nên phải bỏ cả cấu trúc.
- "Đường ra" (targeting + push + point) đã hoàn chỉnh trong Tip pattern của e-smart — nhờ đó phạm vi tạo mới gói gọn ở tầng phán định.
- Tri thức 判定式 đã được trích sẵn vào [G], bỏ code cũ không mất gì (code cũ chỉ còn vai trò xác minh chéo).

**Sơ đồ luồng hệ cũ** (確実):

```
19 dòng cron (cron dòng 84–102) …ngày/giờ cố định; 15 dòng giới hạn tháng theo mùa, 4 dòng (id 1/2/3/19) chạy thông năm
    ▼ 25_PublishRegularEcoMissions_idN.sh (--eco-mission-id 1..19)
PublishRegularEcoMissionsCommand ──route──▶ 10 lớp Publisher
    ├─ phán định: điều kiện riêng từng loại (dùng quá TB, chưa bật ECO mode, quên hẹn giờ ngủ/vắng nhà, tỷ lệ sưởi, kỷ niệm hợp đồng…)
    ├─ ghi: ConEcoMissions + ConEcoMissionDestinations (advice + đích nhận từng hộ)
    └─ ghi: PushMessages + PushMessageDestinations (đăng ký push — loại có trích lọc: hẹn phát sau 1 phút)
         ▼
       gửi thật do #3 DispatchPushMessagesCommand (§3.4) quét hàng đợi mỗi phút
```

Chỗ then chốt: ghi advice và đăng ký push trong cùng transaction — 🔍 `…/src/Command/PublishRegularEcoMission/EcoMissionPublisher.php:142-150`:

```php
foreach ($this->PushMessageDestinations->createByEmsSp($emsSp) as $pd) {
    $pd->push_message_id = $pushMessage->id;
    $pd->schedule = FrozenTime::now()->addMinutes(1);   // push hẹn PHÁT SAU 1 PHÚT (gửi thật do #3)
    $pushMessageDestinations[] = $pd;
}
...
$this->ConEcoMissionDestinations->saveManyOrFail($ecoMissionDestinations);
$this->PushMessageDestinations->saveManyOrFail($pushMessageDestinations);
```

**Chi tiết hệ cũ** (確実):

- 1 command duy nhất chạy với option `--eco-mission-id` (1..19). *(Folder có 11 file nhưng 1 là lớp option; `04_バッチ一覧.md` ghi 「11種Publisher」 là đếm cả file đó.)*
- Bảng thao tác (khai báo tại `EcoMissionPublisher.php:7-13, 30-34`): `ConEcoMissions`・`ConEcoMissionDestinations`・`ConRegularEcoMissions` (master định nghĩa advice)・`PushMessages`・`PushMessageDestinations`.
- *Quan hệ ba con số: 19 = số loại advice (mission-id) hiện hành → route vào 10 lớp Publisher dùng chung; 15 = con số 「約15種」 ghi trong CLD-06 (vấn đề đang mở về gom loại advice) → phương án gom = 7種+エコ暖房ポイント.*
- 🔍 `…/src/Command/PublishRegularEcoMissionsCommand.php:54-140` ・ `…/PublishRegularEcoMission/EcoMissionPublisher.php:60-82, 112-152`

**e-smart có sẵn không — KHÔNG, dẫn chứng code** (確実): grep `advice|アドバイス|mission|ミッション|判定` toàn `src` → **0 hit thật** (mọi match là chuỗi con `permission`). Thứ gần nhất là **Tip (エコライフのコツ)** — nội dung do admin **soạn tay**, nhìn model là rõ — 🔍 `src/layers/common/nodejs/models/Tip.ts:4-22`:

```ts
export interface Tip {
  tip_id: string; ...
  target_type?: string;          // phát cho: ALL / thuộc tính / CSV — KHÔNG có "theo dữ liệu năng lượng"
  body_tip?: IBodyTipItem[];     // NỘI DUNG do admin soạn trong web-admin
  send_time?: number;            // giờ phát admin đặt (→ one-shot scheduler §2)
  has_badge?: boolean;
  point_quantity?: number;       // điểm thưởng khi đọc
  push_notice_flag?: boolean; ...
```

Từng nhóm: `body_tip` là nội dung biên tập sẵn; `target_type` chỉ có 3 kiểu targeting tĩnh (`batch-send-tip-preprocessing/app.ts:43-50`); `point_quantity` cấp điểm khi user bấm "đọc rồi" (`api-tip/read-tip.ts:68` — ghi vào `TABLE_TIP_STATS`/`TABLE_TIP_USER_ACTION`). **Không trường nào, không hàm nào đọc dữ liệu năng lượng của hộ để quyết định phát** (grep `energy|usage` trong `api-tip`: 0 hit) — tức "advice engine" phán định cá nhân hóa của hệ cũ **không tồn tại** ở e-smart.

**E-GW yêu cầu**: scope 2026 (F-ES-03 省エネアドバイス — không ✅ = 今期必須; 決定 6/10 dòng アドバイス※). Yêu cầu mới **khác hệ cũ**: [G] (spec màn quản trị 省エネアドバイス) đòi 自動配信 theo 定期配信スケジュール **chỉnh được từ 管理画面** (hiện hành cron cố định — chính là chỗ 「いけてない」); gom 15種→7種+エコ暖房ポイント chưa chốt (CLD-06 未動); 判定式 (công thức phán định) có 踏襲 nguyên không cũng T.B.D (G-C-05 — **判定式 từng loại đã được trích sẵn vào [G]**, code cũ chỉ để xác minh chéo).
- 🔍 `4_spec/admin/G_energy_advice.md:18-19, 28-29, 47` ・ `00_integrated_requirements_v1.2.md:632-647` ・ `20_open_issues.md:176-177`

**Sơ đồ luồng hệ mới (đề xuất)**:

```
[Màn quản trị web-admin] tạo advice + đặt 定期配信スケジュール (G-A-02 — UI MỚI)
    ▼ đăng ký lịch (put-schedule.ts — cơ chế lịch động sẵn có)
BatchJudgeAdvice (Lambda phán định theo loại — MỚI) …đầu vào: GW đo / TagTag / Xzilla (map ở bước 1)
    ▼ danh sách user trúng điều kiện
BatchSendAdvice (MỚI — phỏng theo chuỗi batch-send-tip) …ghi bản ghi Advice (bảng MỚI)
    ▼ phát xong tự đăng ký push one-shot (mẫu: batch-send-tip-complete)
BatchPushNotice (hạ tầng push sẵn có — §3.4) ──▶ FCM ──▶ app
```

**Cách làm từng bước**:
1. Chờ/thúc CLD-06 (gom advice 15種→7種) chốt danh mục (câu Dự phòng 1 bảng QA); song song rà bảng 判定式 trong [G] G-C-05, đánh dấu từng 判定式 cần dữ liệu đầu vào gì và dữ liệu đó trên E-GW lấy từ đâu (GW đo? TagTag? Xzilla?).
   - *Vì sao*: số loại (= số Lambda) và đường lấy dữ liệu đầu vào quyết định toàn bộ thiết kế lẫn công số — bảng mapping này chính là bảng quyết định khối lượng thật.
2. Thiết kế model `Advice` mới phỏng theo `Tip` (thêm vào `src/layers/common/nodejs/models/`, interface tương ứng vào `src/layers/common/nodejs/interfaces/`): giữ `target_type`/`point_quantity`/push flags để tái dùng đường phát + thêm "điều kiện phán định" và **lịch phát định kỳ admin đặt được** theo G-A-02.
   - *Vì sao*: cùng khuôn với Tip thì toàn bộ đường phát/push/point sẵn có (chuỗi batch-send-tip) dùng lại được — phần mới dồn hết vào tầng phán định.
3. Dựng **batch skeleton** (バッチボーン §2 — khung rỗng): state machine `BatchJudgeAdvice` (per loại) → `BatchSendAdvice` → `BatchPushNotice`, nối bằng one-shot scheduler; định nghĩa thêm vào `src/statemachine/` (mẫu: `batch-send-tip.asl.json`・`batch-push-notice-tip-new.asl.json`) + khai báo trong `template.yaml`; chuỗi news/tip hiện có (`api-news/common.ts:207-209`) là mẫu cách nối. Ban đầu judgment trả danh sách rỗng/giả.
   - *Vì sao*: đúng phương châm đặt khung rỗng trước — 判定式 chưa chốt vẫn test được đường phát, kịp 結合フェーズ (tháng 9).
4. Làm UI web-admin: form quản lý advice theo mẫu `components/tip/tip-form.vue` (đã có sẵn khối 付与ポイント/バッジ, targeting, push) + phần đặt 定期配信スケジュール (mới — [G] G-A-02).
   - *Vì sao*: phần lớn UI đã nằm sẵn trong tip-form; phần thực sự mới chỉ là khối đặt lịch định kỳ.
5. Implement từng 判定式 theo danh mục đã chốt ở bước 1; mỗi loại một Lambda judgment (folder mới trong `src/functions/`), đầu ra là danh sách user → ghi advice + enqueue push theo pattern sẵn có.
   - *Vì sao*: tách Lambda theo loại khớp nguyên tắc 1 batch = 1 task trên Notion, và chịu được biến động danh mục (CLD-06 thêm/bớt loại).
6. Kiểm thử: mỗi 判定式 một bộ dữ liệu biên (đúng/sai ngưỡng); chạy trước 結合フェーズ (mục tiêu tháng 9 — §2).
   - *Vì sao*: sai biên của 判定式 = phát nhầm/bỏ sót hộ — phải đạp cả hai phía ngưỡng mới phát hiện được.

### 3.4 #3 `DispatchPushMessagesCommand` — gửi push mỗi phút

**Mục đích của batch**: là "cửa gửi" chung — mọi thông báo sinh ra trên server hệ cũ (advice, DR, report…) đều qua batch này để đến điện thoại user dưới dạng push.

**Phán định — BỎ gì, GIỮ gì, THAY bằng gì**: **BỎ = batch cũ + hàng đợi DB `push_message_destinations` + cron mỗi phút + server trung gian PushCore** (không dựng lại bất kỳ thành phần nào). **GIỮ = nghiệp vụ gửi push** (mọi thông báo E-GW vẫn cần cửa gửi). **THAY bằng = hạ tầng FCM gửi thẳng của e-smart** (xem sơ đồ hệ mới bên dưới) — theo tiền đề deploy §2, nếu chốt độc lập thì là dựng lại đúng stack đó trên môi trường mới.

**Vì sao đề xuất vậy**:

- e-smart đã có trọn bộ: gửi FCM trực tiếp + quản lý token + fan-out theo lô (soi code xác nhận) — phủ hết mọi việc batch cũ đang làm.
- Phía yêu cầu cũng cùng hướng: D03 (bộ yêu cầu app, section PUSH通知) ghi rõ 「全要件がESTA既存のため【新規】なし」.
- Kiến trúc cũ (hàng đợi DB + cron mỗi phút + PushCore trung gian) đi ngược nguyên tắc nền e-smart "không polling mỗi phút" (§2); riêng PushCore còn không có code trong repo.
- Duy nhất phải làm với hệ cũ: rà danh mục 通知種別 (vế 「＋現行」 của D03 — bước 2).

**Sơ đồ luồng hệ cũ** (確実):

```
cron mỗi phút (cron dòng 79–80)
    ▼
DispatchPushMessagesCommand
    ├─ đọc: push_message_destinations (hàng đợi DB) …lấy bản ghi đến hạn, phân trang 500 bản ghi/trang
    ├─ validate: đúng MỘT trong device_token / FCM topic (cả hai hoặc không cái nào → STATUS_INVALID)
    └─ POST ──▶ PushCore (server trung gian localhost:54650, /v2/send-messages) ──▶ FCM (*推定* — code PushCore không nằm trong repo)
         retry 3 phút/lần, bỏ sau 5 lần
```

Chỗ then chốt: đọc hàng đợi + địa chỉ PushCore — 🔍 `…/src/Command/DispatchPushMessagesCommand.php:65-79` và `eminel_sv_lib-develop/src/StaticServices/PushMessageService.php:26, 36-39`:

```php
$limit = 500;                                        // :65 — 500 bản ghi/trang
$query = $this->PushMessageDestinations->find()      // :68 — lấy từ hàng đợi DB các bản ghi đến hạn
    ...
    ->contain('PushDeviceTokens')
    ->contain('PushFcmTopics')
    ->where(['status' => PushMessageDestination::STATUS_SCHEDULED,
             'schedule >=' => $startAt, 'schedule <=' => $endAt])
// PushMessageService.php
$this->apiUrl = $this->getPushCoreHost() . '/v2/send-messages';        // :26
return Configure::read('PushCore.Api.host', 'http://localhost:54650'); // :38
```

**Chi tiết hệ cũ** (確実): cấu hình retry tại `config/push_message.php:4-14`; bảng thao tác `PushMessageDestinations` (khai báo dòng 14, 40). 🔍 `…/src/Command/DispatchPushMessagesCommand.php:51-177` ・ cron dòng 79–80.

**e-smart có sẵn không — CÓ ĐẦY ĐỦ, dẫn chứng code** (確実):

① Bảng token — 🔍 `src/layers/common/nodejs/models/MobileTokenManagement.ts` (nguyên văn cả file; bảng thật: `TABLE_MOBILE_TOKEN_MANAGEMENT`, app đăng ký qua API `user/save_mobile_token` — handler `src/functions/api-user/save-mobile-token.ts`, đăng ký route tại `api-user/app.ts:58`):

```ts
export interface MobileTokenManagement {
  user_id: string;
  mobile_token: string;   // token FCM của máy — app đăng ký qua API user/save_mobile_token
}
```

② Gửi FCM trực tiếp bằng firebase-admin, kèm tự dọn token hỏng — 🔍 `src/layers/common/nodejs/services/push-notification-firebase.ts:87-97`:

```ts
if (isNotificationMessageValid) {
  try {
    await firebaseAdmin.messaging().send(notificationMessage);   // gửi FCM từng token
  } catch (error) {
    const errorCode = (error as any).code;
    if (errorCode === 'messaging/invalid-registration-token' ||
        errorCode === 'messaging/registration-token-not-registered' || ...) {
      await removeMobileTokenInvalid(mobileToken);               // token chết → xóa khỏi TABLE_MOBILE_TOKEN_MANAGEMENT
```

③ Batch fan-out (tỏa việc gửi) — 🔍 `src/functions/batch-push-notice/app.ts:17-34`:

```ts
const dataPushNotice: IDataPushNotice = await getDataJSONFromS3(
  BUCKET_TEMPORARY as string, `${targetFileTemp}_${segmentIndex}.json`); // đọc 1 LÔ user từ S3
const listTargetUser = dataPushNotice.list_user;
const dataPushNoticeForUser = {
  title: ..., body: ...,
  target_screen: dataPushNotice?.data?.target_screen,   // app dùng để điều hướng khi bấm thông báo
  target_id: ..., };                                    // "?." = truy cập an toàn: thiếu thì trả undefined, không lỗi
await getFirebaseAdmin();
const promisesPushNoticeForUser = listTargetUser.map((targetUser) =>   // .map = với TỪNG user tạo một lệnh gửi
  pushNoticeToUser(targetUser.user_id, dataPushNoticeForUser));
await Promise.allSettled(promisesPushNoticeForUser);    // chạy song song, chờ xong hết kể cả lệnh lỗi
```

Từng nhóm:
- (a) mỗi lần chạy xử lý **một lô** (segment) user đã được bước preprocessing chia sẵn — 10 000 user/lô (`batch-push-notice-tip-new-preprocessing/app.ts:53`); trong lô gửi song song tối đa 100 lệnh/lúc (hằng số tại `src/layers/common/nodejs/services/push-notice-to-user.ts:21`);
- (b) lúc gửi có lọc cờ opt-in của user trong `TABLE_USER_SETTING` (check tại `push-notice-to-user.ts:35-60`, khai báo env dòng 19);
- (c) `target_screen`/`target_id` khớp với code app Flutter điều hướng khi bấm thông báo (`syp-eminelstandard-app-syp-dev/lib/presentation/pages/main/bottom_navigation_view.dart:473-528`; app đăng ký token qua `user/save_mobile_token` — dòng 101–111);
- (d) có 6 state machine push notice: survey/news/tip/DR-new/DR-start/DR-end (`template.yaml:510/685/815/1889/1927/1965`).

**E-GW yêu cầu**: **D03 (bộ yêu cầu app, section "PUSH通知" — trạng thái trong file: レビュー中, chưa fix; lưu ý slide 「要件一覧」 gửi khách ghi ステータス của D3 là 「レビュー前」 — `3_requirements/app/README.md:64`)** ghi 踏襲元 = **ESTA Push基盤 ＋ 現行（通知種別の網羅 — rà đủ danh mục loại thông báo hiện hành）**, 「全要件がESTA既存のため【新規】なし」 — 🔍 `3_requirements/app/D03_push.md:5, 7, 29-31, 81-83`.

**Sơ đồ luồng hệ mới (e-smart sẵn có — E-GW dùng luôn)**:

```
Batch phát nội dung xong (news / tip / survey / DR — 6 hệ state machine)
    ▼ đăng ký one-shot (batch-send-*-complete)
batch-push-notice-*-preprocessing …trích đối tượng, chia lô 10 000 user → ghi JSON lên S3 (BUCKET_TEMPORARY)
    ▼ chạy theo từng lô
batch-push-notice …đọc lô từ S3, gửi song song tối đa 100 lệnh
    ├─ check cờ nhận: TABLE_USER_SETTING (opt-in của user)
    └─ lấy token: TABLE_MOBILE_TOKEN_MANAGEMENT (app đăng ký qua user/save_mobile_token)
    ▼ firebase-admin
FCM ──▶ app (bấm thông báo → điều hướng theo target_screen) …token chết bị tự xóa ngay lúc phát hiện
```

**Cách làm từng bước** (chủ yếu là việc "bỏ cho đúng"):
1. Đưa "hạ tầng Push (FCM)" vào danh sách trả lời câu hỏi phụ ただし của QA 独立デプロイ (§1 việc ngay #1 — danh sách chức năng nên dùng tiếp) để mui xác nhận hướng dùng chung.
   - *Vì sao*: Push là chức năng chịu ảnh hưởng lớn nhất của quyết định deploy độc lập (có phải tách Firebase project không) — phải chốt hướng trước khi làm gì khác.
2. Rà **danh mục 通知種別 (loại thông báo) của hệ cũ** (vế 「＋現行」 trong 踏襲元 của D03): liệt kê mọi loại thông báo hệ cũ đang phát (advice 19 loại, DR, 見守り — *thông báo trông nom người thân từ xa, đang treo CLD-05*, レポート…), map từng loại sang: nguồn sinh nội dung mới (§3.2/§3.3/…) + `target_screen` mới trên app E-GW. Đầu ra: bảng mapping cho D03 khi fix.
   - *Vì sao*: D03 tuyên bố kế thừa "đủ danh mục loại thông báo hiện hành" — không rà thì D03 không thể chốt; bảng này còn dùng lại cho #2 (advice) và CLD-05 (見守り).
3. Nếu deploy độc lập: dựng Firebase project riêng cho app E-GW, bảng `TABLE_MOBILE_TOKEN_MANAGEMENT` + API `user/save_mobile_token` (pattern `api-user/save-mobile-token.ts`) trên môi trường mới.
   - *Vì sao*: pattern đã có đủ — việc còn lại là cấu hình môi trường + đăng ký credential qua Secrets Manager, gần như không phải viết code mới.
4. KHÔNG lập task port `DispatchPushMessagesCommand`/PushCore — ghi rõ "bỏ, thay bằng batch-push-notice pattern" khi tách task Notion để khỏi đếm nhầm vào ~46本.
   - *Vì sao*: lọt vào mẫu số ~46 batch thì ước lượng và tiến độ méo; phán định "bỏ" chỉ có hiệu lực khi được ghi rõ trên Notion.
5. Kiểm thử: gửi thử tới thiết bị dev với token thật; thử token chết xác nhận tự xóa (②); đo giới hạn 4096 byte message (`constants.ts:223`).
   - *Vì sao*: sự cố push quy về 3 kiểu — không tới nơi, gửi mãi vào token rác, nội dung bị cắt — 3 bài test trên bắt đúng 3 kiểu đó.

### 3.5 #4 `ControlDrOperationCommand` — điều khiển chỉ lệnh DR

**Mục đích của batch**: khi có yêu cầu DR (デマンドレスポンス — bên bán năng lượng nhờ hộ dân giảm tải giờ cao điểm), server tự vận hành máy sưởi của các hộ tham gia thay cho con người — biến yêu cầu của 北ガス thành thao tác thiết bị trong nhà user.

**Phán định — BỎ gì, khi nào làm, THAY bằng gì**: **2026 KHÔNG code** — hành động duy nhất là chốt câu hỏi DR ở bước 1. **BỎ = toàn bộ kiểu cũ**: cron mỗi phút, ghi `instructions`, GW poll, và mẹo "giả dạng app user" (tuyệt đối không kế thừa). **2027 = tạo mới trên khung DR e-smart**: lớp "sự kiện DR" (model, màn quản trị, phát, point) dùng lại toàn bộ, chỉ thêm nhánh điều khiển thiết bị qua GW.

**Vì sao đề xuất vậy**:

- Theo yêu cầu E-GW, DR thuộc diện **劣後 → 2027/4以降** (quyết định 6/10; B05 — bộ yêu cầu app, section DR: 26年スコープ=なし) — không có căn cứ code trong 2026.
- e-smart đã có sẵn khung DR kiểu khác (server chủ động điều khiển thẳng cloud hãng); 2027 chỉ cần thêm 1 nhánh "qua E-GW" vào chỗ rẽ điều khiển thiết bị là xong — chi phí nhỏ nhất.
- Mẹo "giả dạng app user" vốn là cách lách ràng buộc của GW cũ (GW bỏ qua lệnh không phải từ app端末); kiến trúc mới (server chủ động, lệnh qua HEMS-SV) làm tiền đề đó biến mất — không có lý do kế thừa.
- Việc duy nhất không chờ được đến 2027: chốt "GW có giữ trạng thái DR không" (câu 5 bảng QA) — vì nó ràng buộc thiết kế firmware GW ngay trong 2026.

**Sơ đồ luồng hệ cũ** (確実):

```
cron mỗi phút (cron dòng 76–77)
    ▼
ControlDrOperationCommand (2 phase; mỗi hộ né xung đột lệnh 5 phút)
    ├─ đọc: ConDrOperations (thiết lập chỉ lệnh DR) + hems_gws (GW) + t_201 (ConDevices — thiết bị & "app端末" của user)
    ├─ ghi: ConDeviceControls (lịch sử điều khiển)
    └─ ghi: instructions (宅外制御指示 — lệnh điều khiển từ xa, mã ECHONET; EPC 80/B0 = bật-tắt/đổi nhiệt độ)
         ※ghi GIẢ DẠNG như thao tác từ app端末 của user
         ▼
       GW poll (định kỳ tự hỏi "có lệnh mới không?") qua hemssv (server GW hệ cũ) → điều khiển thiết bị trong nhà
```

Bằng chứng phải "giả dạng" — comment nguyên văn trong code — 🔍 `…/src/Command/ControlDrOperationCommand.php:171-172`:

```php
// 暖房制御ユニットとユーザのアプリ端末の情報を取得
// ユーザのアプリ端末からの操作のように見せかけないとゲートウェイが指令を無視する
```

(*"phải giả dạng như thao tác từ thiết bị app của user, nếu không gateway sẽ bỏ qua chỉ lệnh"*)

**Chi tiết hệ cũ** (確実): bảng thao tác (khai báo `fetchTable` dòng 56–61): `ConDrOperations`・`ConDevices`・`ConDeviceControls`・`ConDeviceStatuses`・`HemsGws`・`Instructions`; ghi `instructions` từ dòng 210 (`ems_sp_no`・`node_id`・`eoj` — địa chỉ thiết bị theo chuẩn ECHONET).

**e-smart có sẵn không — CÓ KHUNG DR KHÁC KIỂU, dẫn chứng code** (確実):

① Model DR event + trạng thái-trước-điều-khiển — 🔍 `src/layers/common/nodejs/models/Dr.ts:5-30` và `DrUserAction.ts:1-14` (bảng thật: `TABLE_DR` — xác minh trong `api-dr/create-dr.ts`; `TABLE_DR_USER_ACTION` — trong `batch-start-dr/app.ts`; `TABLE_DR_STATS` — trong `batch-send-dr-complete/app.ts`):

```ts
export interface Dr {
  dr_id: string; ...
  implement_start_time?: number;   // giờ bắt đầu/kết thúc DR → đặt lịch one-shot
  implement_end_time?: number;
  target_type?: string;            // targeting như news/tip
  control_setting: IControlSetting[];  // ĐIỀU KHIỂN GÌ trên thiết bị nào
  push_notice_new_dr?: IPushNotice;    // 3 mốc push: báo mới / bắt đầu / kết thúc
  has_badge?: boolean; point_quantity?: number; ...
export interface DrUserAction {
  user_id: string; dr_id: string; ...
  pre_control_status?: {           // TRẠNG THÁI THIẾT BỊ TRƯỚC KHI DR — để khôi phục
    device_id: string; server_type: string; ...
```

② Batch start/end — khối này chứng minh: DR của e-smart do **server chủ động điều khiển** thiết bị nối cloud hãng, có lưu và khôi phục trạng thái trước DR — khác hẳn kiểu server-ghi-lệnh-chờ-GW-poll của hệ cũ. 🔍 `src/functions/batch-start-dr/app.ts:55-65` và `batch-end-dr/app.ts:82-94`:

```ts
// start: điều khiển thiết bị của từng user tham gia
const promisesControlDeviceByDr =
  listDrUserAction?.map((drUserAction) =>
    handleControlDevice(drUserAction.user_id, drInfo.control_setting, drId)
      .catch(() => { listUserStartDrFail.push(drUserAction.user_id); })) ?? [];
      // "?.map(…) ?? []" = danh sách không tồn tại thì coi như mảng rỗng
await Promise.allSettled(promisesControlDeviceByDr);
// end: trả điểm cho người tham gia tới cùng, rồi khôi phục thiết bị
const isHasAward = Number(drInfo.point_quantity) > 0 || drInfo.has_badge;
for (const userId of listUserJoinedDr) {
  if (isHasAward) {
    const pointBadgeStatsSK = `dr#${drId}`;
    await givePointBadgeForUser(userId, pointBadgeStatsSK, ...);
```

Từng nhóm:
- (a) start-DR điều khiển thiết bị theo `control_setting` và **lưu `pre_control_status`** (dòng 212); end-DR cấp point (tái dùng luồng cấp điểm tập trung đã xem ở §3.2-②, khóa `dr#<id>`) rồi **khôi phục thiết bị về trạng thái trước DR** (dòng 96–190);
- (b) thiết bị điều khiển được: **Rinnai / Noritz / Daikin / điều hòa・fancon qua MUI hồng ngoại** (`batch-end-dr/app.ts:139-188`) — đều là thiết bị nối trực tiếp cloud hãng, **không có đường nào qua GW**;
- (c) phần "chạm thiết bị" nằm ở hàm chung `controlDevice` (`src/layers/common/nodejs/business-logic/control-device.ts` — rẽ 4 nhánh theo `SERVER_TYPE`: RINNAI/NORITZ/DAIKIN/MUI_CLOUD), được hàm local `handleControlDevice` (`batch-start-dr/app.ts:81`) gọi;
- (d) về lịch: lịch **phát (配信)** DR được đăng ký one-shot ngay khi admin tạo/sửa DR trên màn hình quản trị (`api-dr/create-dr.ts:111`・`update-dr.ts:149`); còn lịch **start/end** được đăng ký lúc phát xong (配信完了 — `batch-send-dr-complete/app.ts:127-143`);
- (e) web-admin có trọn màn hình DR管理 (`pages/distribution-management/dr/` + `components/dr/dr-form.vue` — 1881 dòng).

**E-GW yêu cầu**: F-ES-07 (暖房DR) / F-ES-08 (điện DR) + F-AD-08 (màn quản trị DR) — **劣後, 2027/4以降** (決定 6/10; B05 — bộ yêu cầu app, section DR: 26年スコープ=なし). Kiến trúc tương lai: DR サーバー主導, lệnh xuống GW qua **HEMS-SV (m2-cloud)**; cách kết thúc DR (án A: server phát lệnh đúng giờ vs án B: GW tự kết thúc — tức GW có giữ trạng thái không) **chưa chốt** — câu 5 bảng QA gửi khách, ràng buộc firmware 2026.
- 🔍 `22_decisions.md:30-31` ・ `B05_dr.md:8, 32-34` ・ camp day3:113-122 (DR発令 詰め込み → tách ~17項目)

**Sơ đồ luồng hệ mới (hình hài năm 2027 — 2026 KHÔNG implement)**:

```
[Màn quản trị web-admin] tạo/sửa DR (dr-form.vue — sẵn có)
    ▼ api-dr/create-dr.ts:111・update-dr.ts:149 — lưu TABLE_DR + đăng ký one-shot lịch PHÁT
BatchSendDr (batch phát — sẵn có) …tạo bản ghi nhận DR cho đối tượng + push "DR mới"
    ▼ phát xong → batch-send-dr-complete/app.ts:127-143 đăng ký one-shot start/end (cập nhật TABLE_DR_STATS)
batch-start-dr …nổ đúng giờ bắt đầu
    ├─ handleControlDevice (app.ts:81) → controlDevice (business-logic/control-device.ts)
    │    ├─ nhánh sẵn có: RINNAI / NORITZ / DAIKIN / MUI_CLOUD (gọi thẳng cloud hãng)
    │    └─ nhánh MỚI (làm năm 2027): "sưởi qua E-GW" — gọi API HEMS-SV (m2-cloud)
    └─ lưu trạng thái trước DR vào TABLE_DR_USER_ACTION (pre_control_status)
batch-end-dr …nổ đúng giờ kết thúc
    ├─ cấp điểm người tham gia tới cùng (givePointBadgeForUser — khóa 'dr#<id>')
    └─ khôi phục thiết bị theo pre_control_status
```

**Cách làm từng bước**:
1. (2026 — duy nhất) Chốt nội bộ với kihara (mui — lead phần cứng/firmware GW) rồi hỏi khách: GW có được giữ trạng thái DR không (終了方式 án A/B — câu 5 bảng QA).
   - *Vì sao*: firmware GW thiết kế/chốt trong 2026 — riêng câu này không chờ được đến kỳ phát triển DR 2027; kết quả quyết kiến trúc firmware.
2. (2027) Giữ nguyên lớp "sự kiện DR": model `Dr`/`DrUserAction`/`DrStats` (`src/layers/common/nodejs/models/`), màn hình admin (`pages/distribution-management/dr/`), targeting, 3 mốc push, cấp điểm cuối kỳ — tất cả tái dùng.
   - *Vì sao*: lớp này không phụ thuộc "điều khiển thiết bị nào bằng cách gì" — thiết bị đổi sang đường GW cũng không phải sửa.
3. (2027) Thêm loại thiết bị điều khiển mới trong `control_setting`: "sưởi qua E-GW" — thêm nhánh `SERVER_TYPE` mới trong `controlDevice` (`src/layers/common/nodejs/business-logic/control-device.ts`), gọi **API của HEMS-SV (m2-cloud)** theo spec mui sẽ cung cấp (thay cho việc ghi bảng `instructions` + chờ GW poll của hệ cũ).
   - *Vì sao*: đặt nhánh mới ngang hàng 4 nhánh sẵn có (RINNAI/NORITZ/DAIKIN/MUI_CLOUD) là thay đổi nhỏ nhất; kiểu poll mỗi phút của hệ cũ đi ngược nguyên tắc nền e-smart "không polling mỗi phút" (§2 — grep `rate(`: 0 hit).
4. (2027) Map `pre_control_status` cho thiết bị sưởi qua GW (khôi phục sau DR) — phụ thuộc kết quả bước 1 (GW giữ trạng thái hay server giữ).
   - *Vì sao*: "hết DR trả máy về như cũ" là cốt lõi trải nghiệm DR; chỗ đặt trạng thái khôi phục chính là hệ quả trực tiếp của án A/B.
5. (2027) Tách task theo day3 (~17項目 đã lập trên Notion) — không gom mọi thứ vào một batch như hệ cũ.
   - *Vì sao*: tránh lặp lại cấu trúc "nhồi tất cả vào DR発令" mà day3 đã chê.
6. Kiểm thử: (2027) trọng tâm 3 điểm — chạy hỗn hợp nhánh cũ/mới (thiết bị cloud hãng + thiết bị qua GW cùng tham gia một DR), giải ước giữa chừng, khôi phục `pre_control_status`.
   - *Vì sao*: thêm nhánh mới thì chỗ dễ vỡ nhất là chạy song song với 4 nhánh cũ và bước khôi phục — DR đụng thẳng vào nhà user nên sót khôi phục là hậu quả thấy ngay.

---

## 4. Việc cần xác nhận tiếp (tổng hợp)

| # | Việc | Liên quan | Hành động phía SYP / kênh |
|---|---|---|---|
| 1 | **Chốt kiến trúc DR 2026**: GW có được giữ trạng thái DR không (終了方式 án A/B) — ràng buộc firmware 2026 | batch #4 — bước 1 §3.5 (hành động DR duy nhất của năm 2026) | Đã có **câu 5** bảng QA gửi khách; cần **chốt nội bộ với kihara (mui) trước** rồi mới gửi |
| 2 | Mâu thuẫn ポイント 必須/劣後 + giá trị điểm E-GW | batch #1 — bước 1 §3.2 (chốt spec nghiệp vụ エコ暖房ポイント) | Đã có **câu 2** bảng QA gửi khách; riêng điểm lệch 12〜3月 vs quanh năm (§3.2) → nêu khi chốt spec A03 |
| 3 | Gom advice 15種→7種 (CLD-06) + schedule/判定式 spec [G] (màn quản trị 省エネアドバイス) | batch #2 — bước 1 §3.3 (chốt danh mục loại + map dữ liệu đầu vào 判定式) | Đã có **câu Dự phòng 1** trong bảng QA; phần schedule nêu khi review spec [G] |
| 4 | Báo mui danh sách "chức năng dùng tiếp hệ hiện hữu" (câu hỏi phụ trong QA 独立デプロイ; 2 vế — §1 việc ngay #1; **hành động chung cho cả 3 tập**) | §1 việc ngay #1 ・ batch #3 — bước 1 §3.4 (xác nhận hướng dùng chung hạ tầng Push) | SYP trả lời trực tiếp trên trang QAデータベース Notion |
| 5 | 見守り通知 làm hay không (CLD-05) | bước 2 §3.4 (rà danh mục 通知種別 — quyết 見守り có nằm trong danh sách loại thông báo mới không) | Đã có **câu 3** bảng QA gửi khách |

## 5. Nguồn chính đã dùng

- **`legacy_eminel_docs`** (@`ccd8f56`): `docs/03_API仕様/04_バッチ一覧.md`; code 4 command trong `sources/conciergesv-develop/src/Command/` (`DistributeMonthlyEcoPointsCommand.php`・`PublishRegularEcoMissionsCommand.php` + folder `PublishRegularEcoMission/`・`DispatchPushMessagesCommand.php`・`ControlDrOperationCommand.php`) + `eminel_sv_lib-develop` (PointInfinity, Push, định nghĩa bảng chung); cron: `docs/02_詳細設計/10_バッチ処理/*.txt`
- **`eminel_gw_project`** (@`fbc0af0`; điều tra tại `788b438` — trích dẫn B05/D03 đã cập nhật số dòng theo `fbc0af0`): `docs/eminel/`: 統合要件 v1.2 (F-ES-03/04/07–09, F-AD-08), `1_product/10_feature_list.md`, `2_management/22_decisions.md` (quyết định 6/10), `20_open_issues.md` (CLD-05/06), camp day3 minutes, app requirements (A03/B05/D03 + `app/README.md`), admin spec ([G]); `docs/eminel-smart/` (tài liệu khảo sát ESTA — 6 file; ⚠️ 3 điểm lệch code liên quan tập này, xem mục Giới hạn)
- **`syp-eminelstandard-backend`** (@`dc39aa39`, branch `gw-syp-dev`): `template*.yaml`, `src/functions/**`, `src/layers/common/nodejs/**`, `src/statemachine/*.asl.json`
- **`syp-eminelstandard-web-admin`** (@`e550326`, branch `gw-syp-dev`): `pages/`, `components/`, `constants/`
- **`syp-eminelstandard-app-syp-dev`** (snapshot): `lib/presentation/pages/*`
- **QAデータベース Notion** (trạng thái 回答中 khi tham chiếu 2026-08-04 — mở trang gốc kiểm tra trước khi trích lại): 「旧Eminel基盤継承＋EMINEL-smartサーバーは独立デプロイの確認」 (swan（mui）) ・ 「旧EMINEL調査範囲（conciergesv/eminelsv）とhemssv対象外の確認」 (swan（mui）) ・ 「管理画面は独立か共通か（切替モード追加）の確認」 (masao takahashi（mui）)
