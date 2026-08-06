# Báo cáo phán định batch hệ cũ — nhóm CSV・ZIPエクスポート系 (4 batch #8–#11)

> 🔰 **Người mới vào dự án**: bảng ngay dưới đây là thông tin quản lý tài liệu — đọc **mục 0** bên dưới bảng trước, rồi hãy quay lại.

| | |
|---|---|
| Ngày lập | 2026-08-06 (ngày điều tra: 2026-08-04) |
| Người lập | Bui Trong Dat (SYP) + AI hỗ trợ điều tra |
| Vị trí tài liệu | Bộ phán định 11 batch hệ cũ (3 nhóm) được tách thành **3 tập theo 3 task trên Notion**; tập này = nhóm **CSV・ZIPエクスポート系 (xuất dữ liệu ra file CSV/ZIP), 4 batch #8–#11**. Hai tập kia: 配信・通知系 (#1–#4) và 外部連携・受信系（Xzilla取込） (#5–#7). Số batch #1–#11 là số xuyên suốt, dùng chung giữa các tập và giữa bản Nhật–Việt |
| Nhiệm vụ | Với 4 batch nhóm CSV/ZIP trong `legacy_eminel_docs/docs/03_API仕様/04_バッチ一覧.md` (đều thuộc server `conciergesv` hệ cũ): cái nào **đã có sẵn trong e-smart** (kèm trích code), cái nào phải **tạo mới**, cái nào **bỏ** (kèm các bước làm), căn cứ yêu cầu E-GW trong `eminel_gw_project/docs/eminel` |
| Repo đối chiếu | `legacy_eminel_docs` @ `ccd8f56` ・ `eminel_gw_project` @ `fbc0af0` (điều tra thực hiện tại `788b438` — xem Giới hạn #4) ・ `syp-eminelstandard-backend` @ `dc39aa39` (branch `gw-syp-dev`) ・ `syp-eminelstandard-web-admin` @ `e550326` (branch `gw-syp-dev`) — tất cả trong thư mục `sources/`, đều = origin tại 2026-08-06 |
| Bản tiếng Nhật | `旧EMINELバッチ移行判定報告書_CSV・ZIPエクスポート系4本.md` (cùng thư mục) — bản nộp mui; kết luận, con số, số bước 対応ステップ khớp 1-1 với bản này |

## 0. Tài liệu này là gì? (đọc trước nếu bạn mới vào dự án)

**Bối cảnh một đoạn**: **E-GW (EMINEL Gateway)** là dự án làm hai việc cho dịch vụ EMINEL (khách hàng cuối: 北海道ガス／北ガス): **(1)** thay gateway trong nhà khách (hộp Maxell → gateway do mui Lab làm); **(2)** chuyển phần máy chủ sang nền tảng **e-smart** — hệ đang chạy thương mại của 北ガス (tên khác: **ESTA**, **EMINEL-Smart** — một hệ, ba tên). Hệ EMINEL cũ có vài chục "batch" chạy nền; khi làm server mới phải trả lời: batch nào e-smart **đã có thứ tương đương**, batch nào **phải làm mới**, batch nào **không cần nữa**.

📖 **"Batch" là gì?** Chương trình không có giao diện, hệ thống tự chạy theo lịch hoặc theo sự kiện: tính toán số liệu, nhận/xuất file dữ liệu, gửi thông báo hàng loạt… Người dùng không nhìn thấy batch, nhưng biểu đồ có số liệu, file có sẵn để tải — là nhờ chúng.

**Nhóm của tập này — CSV・ZIPエクスポート系** (*xuất dữ liệu ra file CSV/ZIP*): 4 batch `CreateCsvAndZip…Command` (#8–#11). Tên nghe như "chức năng xuất file cho vận hành" nhưng điều tra code cho thấy bản chất là **backup-trước-khi-xóa** (chi tiết §3). Cả 4 được phán định gộp một lần vì chỉ khác nhau ở loại dữ liệu và chu kỳ.

**Cách đọc**:
- Vội → đọc **§1** (kết luận BỎ–GIỮ–THAY + bảng 4 batch).
- Muốn hiểu căn cứ → **§2** (tiền đề chung) rồi **§3** (chi tiết cả nhóm theo trình tự: *mục đích → đề xuất phán định + lý do → luồng hệ cũ (sơ đồ + code) → e-smart có gì (code) → E-GW yêu cầu gì → bảng đối chiếu cũ–mới → luồng hệ mới (sơ đồ) → cách làm từng bước → kiểm thử/việc chờ*).
- Việc còn treo → **§4**. Tra nguồn → **§5**. Định **trích dẫn lại** → đọc mục **⚠️ Giới hạn** trước.

**Chú giải nhanh** (thuật ngữ dùng trong tập này):

- **e-smart = ESTA = EMINEL-Smart**: một hệ, ba tên; tên trong code là ESTA. Tập này đối chiếu 2 repo của nó: `backend` (TypeScript trên AWS) và `web-admin` (màn hình quản trị, Nuxt 3).
- **Hệ cũ (旧EMINEL)**: 3 khối server CakePHP/PostgreSQL — **`conciergesv`** (API cho app + batch nghiệp vụ; cả 4 batch của tập này thuộc đây); **`eminelsv`** (màn hình quản trị vận hành — nơi người vận hành tải các file backup nói ở §3); **`hemssv`** (giao tiếp gateway). ⚠️ Đừng nhầm `hemssv` (hệ cũ) với **HEMS-SV (m2-cloud)** — thành phần MỚI do mui phát triển cho E-GW, chỉ trùng tên.
- **Stack AWS của e-smart**: **Lambda** = hàm chạy theo sự kiện, không có server thường trực; **DynamoDB** = database NoSQL; **Step Functions** = xâu nhiều Lambda thành luồng nhiều bước (*state machine*); **EventBridge Scheduler** = bộ hẹn giờ kích hoạt batch; **S3** = kho file; **SFTP** = giao thức chép file mã hóa. Hạ tầng khai báo trong `template*.yaml` (AWS SAM). **Presigned URL** = link tải S3 có chữ ký, tự hết hạn sau thời gian đặt trước.
- **partition** = ngăn dữ liệu — bảng lớn trong PostgreSQL được chia sẵn thành ngăn theo ngày/tháng (tên bảng mang hậu tố ngày, vd `t_202_20260729`); xóa được nguyên ngăn một lệnh DROP rất nhanh, thay vì xóa từng dòng.
- **retention** = chính sách giữ dữ liệu bao lâu rồi xóa; **TTL** = bản ghi DynamoDB tự xóa khi quá hạn; **PITR** = backup mức hạ tầng của DynamoDB (khôi phục về một thời điểm bất kỳ).
- **Bốn bảng dữ liệu hệ cũ của nhóm này**: `t_202` = 機器状態 (trạng thái thiết bị) ・ `s_102` = 時間値 (giá trị đo theo giờ) ・ `s_103` = 日値 (giá trị theo ngày) ・ `s_113` = 日平均値 (bình quân ngày toàn hệ). **EMS-SP-NO** = mã định danh điểm lắp đặt (≈ một hộ) — đơn vị chia file CSV.
- **劣後** = lùi sang 2027/4~ ・ **必須** = bắt buộc scope 2026 ・ **T.B.D** = chưa quyết định ・ **回答中** = QA đang trả lời, chưa chốt.
- **Mã tham chiếu**: **spec [I]** = file spec màn hình quản trị `4_spec/admin/I_data_download.md` (định nghĩa chức năng download dữ liệu — DRAFT) ・ `SVC-xx` = mã vấn đề mở trong `2_management/20_open_issues.md` (riêng **SVC-03** = "các yêu cầu 性能・可用性・運用・移行 — hiệu năng, tính sẵn sàng, vận hành, chuyển đổi — chưa được ghi", `20_open_issues.md:86`; trong danh sách thiếu đó có 保持期間/backup — dòng 87) ・ `F-ES-xx` = mã chức năng server trong 統合要件定義書 v1.2 (riêng **F-ES-10** = 「Xzilla連携」).
- **Bảng QA gửi khách** (質問表) = `requirements/qa_kitagas.md` trong workspace onboarding — câu hỏi gửi 北ガス. Phân biệt với **QAデータベース Notion** = kênh hỏi–đáp nội bộ với mui (danh sách trang: §5).
- **Nhãn độ chắc**: **確実** = tự kiểm chứng trên tài liệu/code (khẳng định về e-smart: đã soi trực tiếp code); ***推定*** = suy đoán có căn cứ, chưa kiểm chứng — không dùng làm quyết định cuối. Dẫn chứng sau ký hiệu 🔍, đường dẫn tính từ `sources/`. Trong khối code, dòng/cụm chỉ có `...` là ký hiệu lược bớt của báo cáo, không phải code; comment tiếng Việt = chú thích thêm của báo cáo. "**grep X: 0 hit**" = tìm chuỗi X toàn bộ code không ra kết quả — cơ sở khẳng định "không tồn tại".

## ⚠️ Giới hạn & lưu ý xác thực (đọc trước khi trích dẫn lại)

1. Các khẳng định "e-smart có/không có X" đều đã **kiểm chứng trực tiếp trên code** `syp-eminelstandard-backend` + `syp-eminelstandard-web-admin` (branch `gw-syp-dev`).
2. ⚠️ Bộ **tài liệu khảo sát ESTA** có sẵn của dự án (`eminel_gw_project/docs/eminel-smart/`, 6 file — do mui lập khi khảo sát nền e-smart) có **6 chỗ lệch với code thực tế** (phát hiện khi đối chiếu code trong cuộc điều tra 11 batch); 3 chỗ liên quan tập này liệt kê dưới — 3 chỗ còn lại (số lượng gửi Push, chu kỳ import 基幹, phút lock merge hội viên) xem hai tập kia. Ai trích tài liệu khảo sát phải kiểm code trước:
   | Tài liệu khảo sát ghi | Code thực tế |
   |---|---|
   | `CsvDownloadHistory` = 「CSVダウンロード履歴」 gợi ý lịch sử download của admin (`03_backend_models.md:107`) | Là lịch sử **tải file TỪ SFTP về** (chiều nhận, chống tải trùng) — không liên quan admin download (§3.3 phần ⚠️) |
   | 「自動化ルール実行（毎分）」 (`02_product_overview.md:85`) | Không chạy mỗi phút — mỗi rule một lịch tuần tạo động (§2; grep `rate(`: 0 hit) |
   | Lambda runtime 「Node.js 20.x, arm64」 (`02_product_overview.md:49`) | `Runtime: nodejs24.x` (`template.yaml:181`; riêng CompatibleRuntimes của common layer vẫn nodejs20.x — dòng 3163) |
3. Ba trang QA Notion được trích (§5) ở trạng thái **回答中**, tham chiếu ngày 2026-08-04 qua ảnh chụp màn hình — trước khi trích lại phải mở trang gốc kiểm tra.
4. **Về cập nhật repo yêu cầu 788b438 → fbc0af0** (6 commit, tối 03/08 → tối 05/08): thay đổi chỉ nằm ở `docs/eminel/3_requirements/app/` (13 file yêu cầu app) + 1 dòng skill — **các tài liệu tập này trích (spec [I] `I_data_download.md`, `20_open_issues.md`, 統合要件 v1.2, 決定ログ, 議事録 camp, tài liệu khảo sát ESTA) không đổi**, đã xác nhận 2026-08-06. Kết luận và số dòng trích dẫn của tập này giữ nguyên giá trị ở cả hai commit.

---

## 1. Kết luận

Cả 4 batch đều là **backup-trước-khi-xóa** (chi tiết §3) — không phải chức năng tải dữ liệu cho người vận hành. **Phán định (確実): bỏ cả 4** — nhưng "bỏ" phải hiểu theo 3 vế:

- **BỎ gì**: cơ chế "xuất CSV/ZIP để giữ lại, rồi xóa partition (*ngăn dữ liệu — xem Chú giải §0*)" — cơ chế này sinh ra vì DB hệ cũ chỉ giữ dữ liệu hạt mịn **8–14 ngày tùy bảng** (`t_202` trạng thái thiết bị: 8 ngày, `s_102` giá trị giờ: 14 ngày — §3.1), thiết kế đó không mang sang E-GW.
- **GIỮ gì**: nhu cầu "người vận hành lấy được dữ liệu ra file (CSV/ZIP)" — phía E-GW, spec [I] (*file spec màn hình quản trị `4_spec/admin/I_data_download.md`, DRAFT*) đã định nghĩa lại nhu cầu này thành chức năng download trên màn hình quản trị.
- **THAY bằng gì**: chính sách retention (*giữ dữ liệu bao lâu*) mới — DynamoDB TTL (*bản ghi tự xóa khi quá hạn*) + chuyển bớt sang S3 nếu giữ trong DB quá tốn; chờ spec [I] + SVC-03 (*vấn đề mở: yêu cầu 性能・可用性・運用・移行 chưa được ghi — `20_open_issues.md:86`; 保持期間/backup nằm trong đó — dòng 87*) chốt — kết hợp 2 đường xuất sẵn có của e-smart: **đường ①** admin download on-demand (17 endpoint / 7 loại dữ liệu) ・ **đường ②** export định kỳ ra SFTP `/EST` (đều ở §3.3).

Lý do phán định: yêu cầu E-GW đã **đổi bản chất** (spec [I]: tải 集計データ/dữ liệu tổng hợp từ màn hình quản trị, giữ **24ヶ月** T.B.D — không còn kiểu giữ-ngắn-rồi-xóa), còn e-smart không có cơ chế backup-rồi-xóa nào. Khác nhau giữa 4 batch chỉ ở dữ liệu và chu kỳ:

| # | Batch | Backup dữ liệu gì (bảng hệ cũ) | Chu kỳ hệ cũ |
|---|---|---|---|
| 8 | `CreateCsvAndZipConDeviceStatusesCommand` | 機器状態 (trạng thái thiết bị — `t_202`), partition đủ 8 ngày tuổi | 05:15 hằng ngày; thứ Hai nén ZIP tuần |
| 9 | `CreateCsvAndZipConSensorHourlyValuesCommand` | 時間値 (giá trị giờ — `s_102`), partition đủ 8 ngày tuổi | 05:15 hằng ngày; thứ Hai nén ZIP tuần |
| 10 | `CreateCsvAndZipConSensorDailyValuesCommand` | 日値 (giá trị ngày — `s_103`), partition **tháng trước nữa (前々月)** — đủ ~2 tháng tuổi, trùng kỳ hạn xóa 2 tháng của `DeleteData` (§3.2) | 05:15 ngày 1 hằng tháng, nén ZIP luôn |
| 11 | `CreateCsvAndZipConSensorDailyAveValuesCommand` | 日平均値 (bình quân ngày toàn hệ — `s_113`), partition **tháng trước nữa (前々月)** như trên — 1 file chung, không chia theo hộ | 05:15 ngày 1 hằng tháng, nén ZIP luôn |

**Ba lưu ý đọc kèm**:
- Nhãn **確実/*推定*** chứng nhận phần **dữ kiện** (hệ cũ làm gì, e-smart có/không, scope) — phần **phán định** luôn là phán đoán để team review; nhóm này hướng "bỏ cả 4" là 確実, còn chi tiết (giá trị 保持期間, có cần export định kỳ không) chờ spec [I]・SVC-03 chốt (§3.7 bước 1).
- Báo cáo chỉ phán định *làm gì / dùng lại gì*, **chưa ước lượng công số** — công số ước khi tách 1 batch = 1 task trên Notion (phương châm §2).
- Ngoài phạm vi 4 batch: e-smart **không tính sẵn report/集計 nào từ trước** (monthly report của app = hỏi tới đâu chuyển tiếp sang TagTag API — *nền tảng hội viên 北ガス, nguồn dữ liệu điện/gas hiện tại của e-smart* — tới đó, không lưu — 🔍 `syp-eminelstandard-backend/src/functions/api-dashboard/get-monthly-report-of-user.ts:21`).
  - Tức nhóm batch **集計・計算系** của E-GW (nhóm khác của bảng batch, ngoài bộ báo cáo này) cũng không có sẵn gì để dùng lại.
  - Mà loại dữ liệu 「連携機器別計測値集計データ」 (*giá trị đo tổng hợp theo thiết bị: 10 phút/1 giờ/1 ngày/1 tháng* — §3.4) nhóm này phải cho tải lại chính là đầu ra nhóm 集計 đó sẽ phải dựng mới.

---

## 2. Tiền đề chung khi phán định

**Phương châm đã chốt nội bộ mui (合宿 Day3, 2026-06-25)**: batch hiện hành 「いけてない」 — **làm lại chứ không bê nguyên** (「バッチ群（約46本…）をNotionに機能単位でタスク化…作り直す前提」), 1 batch = 1 task, đặt バッチボーン (khung rỗng) trước, chạy thật trước 結合フェーズ (*giai đoạn ghép nối chạy chung* — mục tiêu tháng 9). Mảng batch/外部連携 dự kiến giao SYP. → *"Dùng lại"* = **dùng cơ chế/hạ tầng/codebase của e-smart**, không phải copy code PHP hệ cũ.
- 🔍 `eminel_gw_project/docs/eminel/2_management/minutes/20260625_egw_camp_day3.md` dòng 35, 51, 99–103, 147–149

**Tiền đề về nơi chạy** (3 ý):
- QA 「旧Eminel基盤継承＋EMINEL-smartサーバーは独立デプロイの確認」 (swan (mui), 回答中, tham chiếu 2026-08-04) trả lời tạm: *về cơ bản (基本的には) phát triển theo hướng hệ độc lập*. Vì vậy "dùng lại của e-smart" = **dùng lại code/cơ chế/pattern**; nếu chốt deploy độc lập thì vẫn phải **dựng lại môi trường chạy** — "dùng lại" ≠ "0 công".
- Hiện trạng code: cả backend lẫn web-admin đều có branch `gw-syp-dev` nhưng **chưa có commit E-GW nào** (web-admin: `git log origin/main..gw-syp-dev` rỗng; backend: 15 commit gần nhất thuần e-smart) — mọi việc E-GW bắt đầu từ 0 trên nhánh này. *推定*: cách làm nhiều khả năng là *viết thêm vào chính codebase e-smart* — suy từ trả lời tạm QA 「管理画面は独立か共通か（切替モード追加）の確認」 (masao takahashi (mui), 回答中: hướng chung source), chưa phải quyết định thành văn.
- **"Chung source" ≠ "chung môi trường chạy"** — hai câu hỏi độc lập, cả hai QA đều mới trả lời tạm.

**Khoảng cách công nghệ giữa hai thế hệ**:

| | Hệ cũ (`conciergesv`…) | e-smart (`syp-eminelstandard-backend`) |
|---|---|---|
| Ngôn ngữ/khung | PHP 8.0 / CakePHP 4.4 | TypeScript / AWS SAM + Lambda (Node.js 24 — `template.yaml:181`) |
| Database | PostgreSQL (partition theo ngày/tháng) | DynamoDB (PITR — backup hạ tầng, khôi phục theo thời điểm — bật sẵn) |
| Cách chạy batch | cron trên server (`/etc/cron.d/eminel-mng-webap`; *cron = bộ hẹn giờ chuẩn của Linux*), shell + flock chống chạy trùng | Step Functions + EventBridge Scheduler |
| Nhận file ngoài | SFTP về đĩa server | SFTP → S3 → DynamoDB |

- 🔍 hệ cũ: `legacy_eminel_docs/docs/02_詳細設計/10_バッチ処理/cron設定概要.txt` dòng 1–37 ・ e-smart: `syp-eminelstandard-backend/template.yaml` (SAM), `eminel_gw_project/docs/eminel-smart/02_product_overview.md` dòng 48–53

**Nền batch của e-smart** (điều E-GW sẽ thừa hưởng — đường dẫn tính từ `syp-eminelstandard-backend/`):

- Chỉ có **3 lịch tĩnh** (`ScheduleV2`, timezone `Asia/Tokyo` — `template.yaml:9-11`): ① `BatchRunSequentiallyStateMachine` — nhập dữ liệu 基幹, `cron(5 0-7 * * ? *)` = phút :05 mỗi giờ 0h–7h JST (`template.yaml:853-888`, cron dòng 881–882); ② `BatchMigrationIntegratedDataStateMachine` — dữ liệu thiết bị Rinnai/Noritz + export, `cron(0 8 * * ?)` (`template.yaml:2205-2240`, cron dòng 2233) — **đường ② của tập này (`/EST` export — §3.3) chạy trong state machine này**; ③ `BatchGetErrorDeviceInfoOfRinnaiStateMachine` — lỗi thiết bị, 8:00 (`template.yaml:2966-2980`).
- **Mọi batch còn lại dùng lịch tạo động qua EventBridge Scheduler** — phần lớn one-shot (*lịch một thời điểm, chạy xong tự xóa nhờ `ActionAfterCompletion.DELETE`* — hàm chung `src/layers/common/nodejs/services/put-schedule.ts:18-33`); ngoại lệ duy nhất là automation rule của user — mỗi rule một lịch tuần lặp tạo động, không tự xóa (`src/functions/api-automation/common.ts:115, 167-175`); không có polling mỗi phút (grep `rate(`: 0 hit).

**Phạm vi SYP**: theo QA 「旧EMINEL調査範囲（conciergesv/eminelsv）とhemssv対象外の確認」 (swan (mui), 回答中) — `conciergesv`/`eminelsv` là đối tượng SYP **điều tra**, không phải phạm vi phát triển tiếp trên hệ cũ; giao tiếp GW đi qua HEMS-SV (m2-cloud) do mui làm, spec chia sẻ sau.

**Quyết định scope 2026-06-10** (đã vào 決定ログ): 必須 = 暖房機能/暖房制御/照明アドバイス※/ポイント連携/グルーピング・レポート; 劣後 (→2027/4~) = 複合制御・DR・ダッシュボード・バッジ等. ※「照明アドバイス」 nghi là lỗi ghi của 省エネアドバイス (*推定*).
- 🔍 `eminel_gw_project/docs/eminel/2_management/22_decisions.md` dòng 30–31 ・ quy ước bảng 機能一覧 (`10_feature_list.md`): cột 劣後 đánh **✅ = lùi được sang 2027**, ô trống = 今期必須.

**Chủ thể các bước trong §3**: trừ khi ghi khác, người thực hiện là **SYP**, code viết trên branch `gw-syp-dev`; đường dẫn không ghi tên repo = `syp-eminelstandard-backend`, phần màn hình quản trị = `syp-eminelstandard-web-admin`. Các bước "chốt/hỏi" đi theo kênh §4. Nhân sự nhắc tên: **swan, masao takahashi** (đều phía mui — người trả lời QAデータベース).

---

## 3. Chi tiết nhóm CSV・ZIPエクスポート系 (4 batch, phán định gộp)

*(Quy ước dẫn nguồn trong §3: đường dẫn `CreateCsvAndZip…Command.php`/`DeleteDataCommand.php` = `legacy_eminel_docs/sources/conciergesv-develop/src/Command/…`; "cron dòng NN" = số dòng trong `legacy_eminel_docs/docs/02_詳細設計/10_バッチ処理/mng-webap_cron設定_20241029.txt`.)*

**Mục đích của 4 batch này**: chúng tồn tại để **backup dữ liệu hạt mịn (trạng thái thiết bị, giá trị giờ/ngày/bình quân) ra CSV/ZIP trước khi xóa partition** — nhờ đó DB hệ cũ chỉ phải giữ 8–14 ngày dữ liệu hạt mịn mà người vận hành vẫn truy được số liệu cũ (mở ZIP đã sơ tán) khi cần. **Đây KHÔNG phải chức năng download cho vận hành** — tải file được chỉ là hệ quả, mục đích chính là sơ tán dữ liệu trước khi xóa; đọc mỗi tên batch rất dễ hiểu nhầm.

### 3.1 Đề xuất phán định (確実 về hướng, chi tiết chờ T.B.D)

**Bỏ cả 4 batch ở dạng hiện tại — nhưng giữ việc "lấy được dữ liệu ra file".** Rành mạch ba vế:

- **BỎ**: cơ chế "backup-trước-khi-xóa" (4 batch + shell + `DeleteDataCommand`). Tiền đề của nó — DB chỉ giữ dữ liệu hạt mịn **8–14 ngày tùy bảng** (`t_202` 8 ngày, `s_102` 14 ngày — 🔍 `DeleteDataCommand.php:47-50`, code trích ở §3.2) — mâu thuẫn với "giữ 24 tháng, tải bất kỳ lúc nào" của spec [I].
- **GIỮ**: nhu cầu người vận hành lấy dữ liệu ra CSV/ZIP — hiện thực bằng chức năng download màn hình quản trị theo spec [I] (tương thích cột với format cũ: §3.7 bước 5).
- **THAY**: kỳ hạn giữ quản bằng DynamoDB TTL (+ S3 nếu cần — §3.7 bước 2); lấy file mặc định qua đường ① (on-demand), nếu vận hành muốn nhận file định kỳ thì thêm đường ② (export định kỳ — §3.7 bước 3–4).

**Vì sao đề xuất vậy (3 điểm)**:

- ① Bản chất 4 batch đúng như "Mục đích" ở trên — backup-trước-khi-xóa, gắn liền với kỳ hạn giữ 8–14 ngày của DB hệ cũ (code then chốt ở §3.2). Tiền đề kỳ hạn thay đổi thì cả cơ chế mất lý do tồn tại.
- ② Yêu cầu E-GW đã đổi bản chất: spec [I] (*spec màn hình quản trị データダウンロード*) định nghĩa **giữ 24ヶ月 (T.B.D) + download bất kỳ lúc nào** (§3.4) — không đứng chung được với kiểu "giữ ngắn rồi xóa".
- ③ e-smart không có cơ chế backup-rồi-xóa nào, nhưng **2 đường xuất dữ liệu đã hoàn chỉnh sẵn** (admin download on-demand / export SFTP định kỳ — §3.3) — vì vậy bỏ cả 4, thay bằng retention mới + 2 đường sẵn có là cấu hình gọn nhất.

### 3.2 Hệ cũ đang làm gì (確実) — sơ đồ, code then chốt, chi tiết

```
【HỆ CŨ】 luồng thật của 4 batch (05:15 hằng ngày hoặc ngày 1 hằng tháng)

  cron 05:15 (mục 「#12.DBデータ削除」 trong file cron — cron dòng 39–41)
    │  hằng ngày: day2to31.sh (chạy 2 batch #8/#9)
    │  ngày 1: day1.sh (chạy CẢ 4 batch #8–#11 — #10/#11 chỉ có mặt ở đây)
    ▼
  CreateCsvAndZip*Command (4 batch — chỉ khác bảng dữ liệu và chu kỳ)
    │  đọc từ partition PostgreSQL có hậu tố ngày
    │  (t_202_YYYYMMDD trạng thái thiết bị・s_102 giá trị giờ: 8 ngày trước
    │   s_103 giá trị ngày・s_113 bình quân ngày: tháng trước nữa 前々月, ~2 tháng tuổi
    │   — vì sao là 前々月: xem chú thích dưới khối code)
    ▼
  Sinh file CSV (chia theo hộ = EMS-SP-NO; riêng #11 gộp 1 file toàn hệ)
    │  ghi ra đĩa server (thư mục theo biến môi trường CON_DEVICE_CSV_FILES_PATH…)
    ▼
  Nén ZIP (ZipArchive của PHP; tên file trong ZIP đổi sang mã SJIS — CreateZipsTrait.php:23-72)
    │  (#8/#9: ZIP tuần chỉ nén vào thứ Hai — isMonday,
    │   CreateCsvAndZipConDeviceStatusesCommand.php:182 / #10/#11: nén ZIP luôn)
    ▼
  DeleteDataCommand DROP các partition đã quá kỳ hạn giữ (xóa nguyên ngăn một lệnh = rất nhanh)
    │  #8/#9: xóa partition 9 ngày / 15 ngày tuổi — dropDailyTable nhắm keepDays+1 ngày trước
    │   (DeleteDataCommand.php:85) → đều đã được export từ các lượt chạy trước
    │  #10/#11: đúng partition vừa export (kỳ hạn 2 tháng — cùng file, dòng 110–112)
    ※ shell chạy với set -eu (gặp lỗi là dừng ngay)
      → CSV sinh lỗi thì KHÔNG chạy tới bước xóa = dữ liệu không mất (van an toàn)
    ▼
  Người vận hành: tải CSV/ZIP trên đĩa qua màn hình quản trị hệ cũ (eminelsv)
```

**Code then chốt (2 chỗ)** — căn cứ "đối tượng + chu kỳ" của 4 batch và kỳ hạn giữ dữ liệu:

Chỉ định partition đối tượng — cả 4 file **cùng ở dòng 39** (🔍 mỗi `CreateCsvAndZip*Command.php:39`):

```php
$partitionTableName = 't_202_' . $dateTime->subDays(8)->format('Ymd');   // #8 trạng thái thiết bị: partition NGÀY, 8 ngày trước
$partitionTableName = 's_102_' . $dateTime->subDays(8)->format('Ymd');   // #9 giá trị giờ: partition NGÀY, 8 ngày trước
$partitionTableName = 's_103_' . $dateTime->subDays(32)->format('Ym');   // #10 giá trị ngày: partition THÁNG — luôn rơi vào tháng trước nữa (前々月)
$partitionTableName = 's_113_' . $dateTime->subDays(32)->format('Ym');   // #11 bình quân ngày: partition THÁNG — luôn rơi vào tháng trước nữa (前々月)
```

*(Vì sao −32 ngày = "tháng trước nữa": shell không truyền `--datetime` nên lệnh luôn chạy với default `'now'` = thời điểm thực thi (`buildOptionParser` của từng command — vd `CreateCsvAndZipConSensorDailyValuesCommand.php:28`); chạy 05:15 ngày 1 hằng tháng thì −32 ngày luôn rơi vào tháng −2 — vd 01/08 − 32 ngày = 30/06 → `s_103_202606`; khớp với phía xóa `dropMonthlyTable(…, 2)` = `subMonths(2)` — `DeleteDataCommand.php:110-112`.)*

Kỳ hạn giữ ở phía xóa — 🔍 `DeleteDataCommand.php:46-50` (phần xóa theo ngày; `s_103`/`s_113` xóa theo tháng ở dòng 53–54, kỳ hạn 2 tháng):

```php
// 日単位削除処理                                    // xử lý xóa theo đơn vị ngày
$this->dropDailyTable('t_202', $dateTimeForDay, 8);    // trạng thái thiết bị: xóa sau 8 ngày
$this->dropDailyTable('s_101', $dateTimeForDay, 8);
$this->dropDailyTable('s_102', $dateTimeForDay, 14);   // giá trị giờ: xóa sau 14 NGÀY (khác t_202!)
$this->dropDailyTable('s_112', $dateTimeForDay, 8);
```

*(Đọc kèm bảng §1 cho khỏi vênh: batch export lấy partition đủ 8 ngày tuổi cho cả `t_202` lẫn `s_102`; còn bước xóa DROP `t_202` sau 8 ngày, `s_102` sau 14 ngày — nên nói "DB giữ 8–14 ngày tùy bảng".)*

**Chi tiết còn lại (5 gạch)**:

- **Kích hoạt**: cron 05:15, mục 「#12.DBデータ削除」 (hệ đánh số riêng của file cron, đừng nhầm với #1–#11 của bộ báo cáo); 2 shell, cả hai đều kết bằng lệnh `DeleteData` (đã mở shell thật trong tgz xác nhận): `12_CreateCsvAndDeleteData_day2to31.sh` (cron `15 5 * * *` = hằng ngày) chạy **2 batch #8/#9**; `12_CreateCsvAndDeleteData_day1.sh` (cron `15 5 1 * *` = ngày 1 hằng tháng) chạy **cả 4 batch #8–#11** (#10/#11 chỉ có mặt trong shell này) — 🔍 cron dòng 39–41.
- **File CSV**: chia theo hộ (EMS-SP-NO — *mã điểm lắp đặt*); riêng #11 (`s_113` bình quân toàn hệ) 1 file chung. Ghi ra đĩa server (biến môi trường `CON_DEVICE_CSV_FILES_PATH`… — `CreateCsvAndZipConDeviceStatusesCommand.php:58`).
- **Nén ZIP**: `ZipArchive` của PHP, tên file trong ZIP convert sang SJIS (🔍 `CreateZipsTrait.php:23-72`). ZIP tuần của #8/#9 chỉ nén vào thứ Hai (kiểm tra `isMonday` — `CreateCsvAndZipConDeviceStatusesCommand.php:182`).
- **Xóa**: CSV/ZIP thành công thì `DeleteDataCommand` DROP partition. Shell `set -eu` — **CSV lỗi thì không xóa** (🔍 `cron設定概要.txt` dòng 26–37, 補足1 「CSV作成後に問題なければデータを消去」).
- **Lấy file**: file nằm lại trên đĩa, người vận hành tải qua màn hình quản trị hệ cũ (`eminelsv`).

### 3.3 e-smart có gì (確実) — KHÔNG có cơ chế "backup rồi xóa"; nhu cầu xuất dữ liệu giải bằng 2 đường

**Đường ①: admin download on-demand** (sinh file khi admin bấm yêu cầu):

- Cửa vào là router 17 endpoint (*mỗi endpoint = một "cửa" API tải một loại dữ liệu*) — 🔍 `src/functions/api-download/app.ts:23-46` (trích):

```ts
const APIs = {
  POST: {
    ...                                    // entry đầu (download_list_device_error_mst) đã lược
  [`/${END_POINT}/download_list_dr`]: downloadListDr,
  [`/${END_POINT}/download_list_news`]: downloadListNews,
  [`/${END_POINT}/download_dr_stats`]: downloadDrStats, ...
  [`/${END_POINT}/download_access_log`]: downloadAccessLog,
  [`/${END_POINT}/download_user_info`]: downloadUserInfo,
  [`/${END_POINT}/download_point_award_history`]: downloadPointAwardHistory,
  [`/${END_POINT}/download_gas_equipment_data`]: downloadGasEquipmentData, ...
```

- Loại dữ liệu nặng được đẩy sang chạy nền: handler `api-download` invoke **bất đồng bộ** Lambda `BatchDownloadFunction` (`InvocationType: 'Event'` — `src/functions/api-download/download-user-info.ts:17-25`; khai báo hàm tại `template.yaml:475-493` — MemorySize 5120, Timeout 900 = cấu hình hạng nặng).
- `BatchDownloadFunction` (code thật ở `src/functions/batch-download/`) **đọc từ các bảng DynamoDB nguồn** (biến môi trường `TABLE_APP_ACCESS_LOG`, `TABLE_DR`… — `template.yaml:483-492`; vd 顧客情報 đọc bảng hội viên `TABLE_KAIIN` — `batch-download/download-user-info.ts:579, 590`) → sinh CSV → nén bằng JSZip (cùng file, dòng 563–568).
- Thành phẩm đưa lên S3 bucket `BUCKET_DOWNLOAD` (*bucket riêng chứa file cho admin tải* — định nghĩa `template.yaml:233`); admin tải qua **presigned URL** (*link có chữ ký, tự hết hạn* — 600 giây, `src/functions/api-s3/get-presigned-url-for-download.ts:67`).
- Phía web-admin: trang `pages/other/data-management/index.vue` + form `components/data-management/form-download-data-management.vue` + danh sách kết quả `list-download-data-management.vue`; 7 loại dữ liệu khai trong hằng `DOWNLOAD_DATA_MANAGEMENT_TYPE` — 🔍 `syp-eminelstandard-web-admin/constants/common.ts:614-622`:

```ts
export const DOWNLOAD_DATA_MANAGEMENT_TYPE = {
  USER_INFO: 'user_info',            ACCESS_LOG: 'access_log',
  MUI_SENSOR_HISTORY: 'mui_sensor_history', GAS_DEVICE_HISTORY: 'gas_device_history',
  POINT_AWARD_HISTORY: 'point_award_history', BADGE_EARNED_HISTORY: 'badge_earned_history',
  GAS_DEVICE_RAW_HISTORY: 'gas_device_raw_history',
}
```

- Luồng end-to-end của đường ① vẽ ở sơ đồ §3.6.

**Đường ②: export định kỳ ra SFTP `/EST`** (đẩy file sẵn theo lịch):

- e-smart đẩy 6 loại CSV dữ liệu thiết bị (5 loại 給湯器/máy nước nóng + remote hồng ngoại) lên thư mục `/EST` của SFTP server hằng ngày 8:00, bằng tài khoản upload riêng — chạy trong `BatchMigrationIntegratedDataStateMachine` (*lịch tĩnh ② của §2*) — 🔍 `src/layers/common/nodejs/services/upload-data-backup-to-sftp.ts:22-43, 52-57`・`template.yaml:2215-2226`.
- Đây là tiền lệ trực tiếp nếu 北ガス muốn nhận file đổ sẵn định kỳ.
- 🔸 *Đích `/EST` có phải Xzilla/DWH (kho dữ liệu phân tích) không thì chưa xác nhận được — địa chỉ nằm trong secret ngoài code (§4 #2).*
- Chi tiết đường xuất này (trích code đầy đủ + quan hệ với 「EMINELデータの共有」 của F-ES-10 Xzilla連携) nằm ở tập 外部連携・受信系（Xzilla取込）, mục **§3.1** của tập đó (bản JP của tập đó: §4.1) — mục "Chung cả nhóm: cách nhận cũ–mới và chiều gửi `/EST`".

⚠️ Đính chính hai hiểu nhầm dễ mắc từ tài liệu khảo sát:

- Bảng `CsvDownloadHistory` (「CSVダウンロード履歴」) **thuộc chiều NHẬN** — lịch sử tải file từ SFTP về để chống tải trùng (`src/layers/common/nodejs/models/CsvDownloadHistory.ts:1-6`; ghi tại `src/functions/batch-forward-csv-from-sftp-server-to-s3/app.ts:80-93`) — không phải lịch sử download của admin.
- DynamoDB không có mô hình "xóa sau N ngày, giữ ZIP" — backup là PITR (khôi phục theo thời điểm, mức hạ tầng), kỳ hạn là TTL từng bảng khi cần (khai trong `template-dynamodb.yaml`).

### 3.4 E-GW yêu cầu gì — bản chất yêu cầu đã đổi

Spec [I] (*file spec màn hình quản trị `4_spec/admin/I_data_download.md`, DRAFT*) định nghĩa データダウンロード từ màn hình quản trị:

- **Loại kế thừa E-Smart**: 顧客情報 (thông tin khách hàng), アプリアクセスログ (log truy cập app), ポイント付与履歴 (lịch sử cấp điểm)… — đều 🔴T.B.D cho E-GW.
- **3 loại E-GW mới**: GW・連携デバイスデータ (dữ liệu GW & thiết bị liên kết), 連携デバイスエラー履歴 (lịch sử lỗi thiết bị), **連携機器別計測値集計データ** (*giá trị đo tổng hợp theo thiết bị: 10分/1時間/1日/1ヶ月値*) — xuất CSV(ZIP).
- **保持期間 (kỳ hạn giữ): 24ヶ月 (T.B.D)** — khác hẳn tiền đề "8–14 ngày rồi xóa" của hệ cũ.
- Đồng thời SVC-03 (*mục trong danh sách vấn đề mở, `20_open_issues.md:86`*): **các yêu cầu 性能・可用性・運用・移行 (hiệu năng, tính sẵn sàng, vận hành, chuyển đổi) chưa được ghi** — danh sách thiếu liệt kê ở dòng 87 bao gồm データ保持期間 và 監視/バックアップ, tức yêu cầu giữ dữ liệu/backup của hệ mới chưa được định nghĩa.

- 🔍 `4_spec/admin/I_data_download.md:16-19, 43-52, 200-204` ・ `20_open_issues.md:87` (SVC-03)

### 3.5 Bảng đối chiếu tương quan hệ cũ ↔ hệ mới (phạm vi nhóm này)

| Khía cạnh | Hệ cũ (4 batch — PHP/PostgreSQL) | e-smart/E-GW (thay thế — Lambda/DynamoDB) |
|---|---|---|
| Nơi lưu dữ liệu | Partition ngày/tháng của PostgreSQL (`t_202` trạng thái thiết bị・`s_102` giá trị giờ・`s_103` giá trị ngày・`s_113` bình quân ngày) | Các bảng DynamoDB (bảng đo đạc của E-GW sẽ dựng mới — phối hợp thiết kế với nhóm 集計・計算系, ngoài bộ báo cáo này) |
| Kỳ hạn giữ | `t_202`: 8 ngày・`s_102`: 14 ngày (`DeleteDataCommand.php:47-50`); `s_103`/`s_113`: 2 tháng (cùng file, dòng 53–54) | Spec [I]: **24ヶ月 (T.B.D)**. Quản bằng DynamoDB TTL; quá tốn thì sơ tán bớt sang S3 (§3.7 bước 2) |
| Cách lấy file | Batch sinh SẴN CSV/ZIP → đĩa server → tải qua màn quản trị cũ (`eminelsv`) | Sinh KHI CẦN theo yêu cầu admin (đường ① — S3 `BUCKET_DOWNLOAD` + presigned URL) / đẩy định kỳ lên SFTP `/EST` (đường ②) |
| Cách xóa | CSV thành công rồi `DeleteDataCommand` DROP partition (`set -eu` làm van an toàn) | TTL tự xóa khi quá hạn — không cần "sơ tán trước khi xóa" nữa vì trong kỳ hạn giữ dữ liệu luôn tải được |
| Backup | Chính file CSV/ZIP đã sơ tán kiêm vai trò backup | PITR (khôi phục theo thời điểm, mức hạ tầng) + chờ phương án tổng thể SVC-03 |

### 3.6 Sơ đồ luồng hệ mới (đường ① + nhánh đường ②)

```
【e-smart/E-GW】 đường ①: admin download on-demand (đường thay thế chính cho 4 batch cũ)

  Admin chọn loại dữ liệu + khoảng thời gian trên màn 「データ管理」 của web-admin
  (pages/other/data-management/index.vue + components/data-management/form-download-data-management.vue)
    │  POST /download_user_info … (17 endpoint — api-download/app.ts:23-46)
    ▼
  Handler tương ứng trong api-download (vd download-user-info.ts)
    │  loại nặng: invoke bất đồng bộ BatchDownloadFunction (InvocationType: 'Event' — cùng file, dòng 17–25)
    ▼
  batch-download (MemorySize 5120 / Timeout 900 — template.yaml:475-493)
    │  đọc bảng DynamoDB nguồn
    │  (vd 顧客情報 = TABLE_KAIIN — batch-download/download-user-info.ts:579;
    │   bảng nguồn cho loại dữ liệu E-GW mới sẽ dựng ở §3.7 bước 2–3)
    ▼
  Sinh CSV → nén ZIP bằng JSZip (cùng file, dòng 563–568)
    ▼
  Upload lên S3 bucket BUCKET_DOWNLOAD (định nghĩa template.yaml:233)
    ▼
  Admin tải về trình duyệt qua presigned URL (link ký sẵn, hạn 600 giây —
  api-s3/get-presigned-url-for-download.ts:67)

【nhánh đường ②: nếu vận hành muốn nhận file định kỳ — §3.7 bước 4】

  Lịch tĩnh (mẫu sẵn có chạy 8:00 hằng ngày: BatchMigrationIntegratedDataStateMachine — template.yaml:2205-2240)
    │  code mẫu: upload-data-backup-to-sftp.ts (đang gửi 6 loại CSV thiết bị)
    ▼
  Sinh CSV → upload lên thư mục /EST của SFTP server (đích /EST cần xác nhận — §4 #2)

  ※ CẢ HAI đường đều không có bước xóa dữ liệu — kỳ hạn giữ do DynamoDB TTL đảm nhận,
    công đoạn "sơ tán trước khi xóa" biến mất hoàn toàn (xem bảng đối chiếu §3.5)
```

### 3.7 Cách làm từng bước

1. Chốt spec [I] (loại dữ liệu E-GW + 保持期間 24ヶ月?) và SVC-03 (phương án retention/backup tổng thể) — nêu khi review spec [I]; **chưa có trong bảng QA gửi khách, cân nhắc thêm câu hỏi** (§4 #1).
   - *Vì sao*: mọi giá trị thiết kế của bước 2 trở đi (giá trị TTL, có cần sơ tán sang S3 không, danh sách loại dữ liệu) đều phụ thuộc 2 điểm này — làm trước khi chốt là làm lại.
2. Thiết kế retention thay thế: dữ liệu hạt mịn giữ trong DynamoDB theo 保持期間 chốt ở bước 1 — khai TTL cho các bảng liên quan trong `template-dynamodb.yaml` (*file định nghĩa các bảng DynamoDB*); nếu giữ 24 tháng trong DB quá tốn → chuyển bớt sang S3 — quyết theo ước tính dung lượng của nhóm 集計・計算系 (ngoài bộ báo cáo này).
   - *Vì sao*: "không cần backup-trước-khi-xóa nữa" chỉ đúng khi dữ liệu trong kỳ hạn giữ luôn nằm sẵn trong DB để tải — thiết kế TTL chính là tiền đề đó; còn bài toán chi phí cần số liệu dung lượng (thuộc nhóm 集計).
3. Mở rộng cơ chế download sẵn có cho loại dữ liệu E-GW mới, đúng pattern đường ① — file phải sửa theo từng lớp:
   - Backend cửa vào: thêm endpoint vào `src/functions/api-download/app.ts` + thêm handler ủy thác cùng thư mục (mẫu: `api-download/download-user-info.ts` — khuôn invoke bất đồng bộ);
   - Backend sinh file: viết handler trong `src/functions/batch-download/` (mẫu: `batch-download/download-user-info.ts` — khuôn đọc DynamoDB → CSV → JSZip → S3);
   - Hạ tầng: thêm biến môi trường `TABLE_*` của bảng mới vào `BatchDownloadFunction` trong `template.yaml` (dòng 475–493);
   - Web-admin: thêm loại vào `DOWNLOAD_DATA_MANAGEMENT_TYPE` (`constants/common.ts:614-622`) + cập nhật `pages/other/data-management/index.vue`, `components/data-management/form-download-data-management.vue` (form chọn kỳ), `list-download-data-management.vue` (danh sách kết quả).
   - *Vì sao*: 17 endpoint / 7 loại hiện hữu đều đúng một pattern — bám theo thì không phải viết lại tầng sinh file, nén ZIP, presigned URL, màn hình.
4. Nếu 北ガス muốn giữ thói quen "file ZIP tuần/tháng đổ sẵn": làm 1 batch export định kỳ theo đường ② — code mẫu `src/layers/common/nodejs/services/upload-data-backup-to-sftp.ts`, lịch thêm 1 `ScheduleV2` tĩnh (theo khuôn 3 lịch tĩnh §2) — chờ chốt như 未決事項 của spec [I].
   - *Vì sao*: đường ① là "cần thì đến lấy", khác hẳn thói quen vận hành "file luôn được đổ sẵn định kỳ"; mà chính nhu cầu này có tồn tại không thì spec [I] chưa chốt — chưa chốt thì chưa làm.
5. Format cột CSV: nên giữ tương thích định dạng cũ vì người vận hành 北ガス đã quen (*推定* về thói quen). Danh mục cột hiện hành **đã được trích sẵn vào spec [I]** (mục 現行EMINEL, nguồn `DownloadController::getCsvHeadersOnSelection()` phía `eminelsv`) — header trong 4 batch cũ chỉ dùng **xác minh chéo**, đừng lập task trích lại.
   - *Vì sao*: thông tin gốc về cột đã có một chỗ chuẩn (spec [I]) — trích lại lần nữa là tạo quản lý trùng; giữ tương thích giúp vận hành đỡ công kiểm khi chuyển hệ.
6. Khi tách task Notion: ghi rõ 4 batch cũ = "bỏ, thay bằng retention + download/export" để khỏi đếm nhầm vào ~46本.
   - *Vì sao*: theo phương châm 1 batch = 1 task (§2), batch bị bỏ rất dễ bị lập nhầm thành "task port"; sai mẫu số là lệch toàn bộ ước lượng.

### 3.8 Kiểm thử & việc chờ

**Góc kiểm thử** (khi làm bước 3–4 của §3.7 — đề xuất):

- End-to-end đường ①: chọn loại dữ liệu mới trên form web-admin → `batch-download` sinh file → vào `BUCKET_DOWNLOAD` → tải được qua presigned URL (600 giây) — đủ mọi chặng của sơ đồ §3.6.
- Tương thích cột: so cột CSV sinh ra với danh mục cột 現行EMINEL trong spec [I] (nguồn của bước 5).
- Biên TTL: bản ghi quá 保持期間 tự mất, bản ghi trong hạn vẫn tải được — đúng thiết kế bước 2.
- Đường ② (nếu làm bước 4): file đến `/EST` cùng khuôn với 6 loại CSV thiết bị hiện hữu (`upload-data-backup-to-sftp.ts`).

**Việc chờ bên ngoài** (chặn khởi công): spec [I] chốt loại dữ liệu + 保持期間 24ヶ月, SVC-03 chốt phương án tổng thể (§4 #1); đích SFTP `/EST` (§4 #2).

---

## 4. Việc cần xác nhận tiếp

| # | Việc | Liên quan | Hành động phía SYP / kênh |
|---|---|---|---|
| 1 | Chốt spec [I] (*spec màn hình quản trị データダウンロード, DRAFT*) — loại dữ liệu E-GW cho tải + 保持期間 24ヶ月 (T.B.D) — và SVC-03 (*vấn đề mở: yêu cầu 性能・可用性・運用・移行 chưa được ghi — `20_open_issues.md:86`; retention/backup nằm trong đó — dòng 87*) | Tiền đề của toàn bộ thiết kế thay thế cho #8–#11 (§3.7 bước 1–2) — chưa chốt thì chưa định được giá trị TTL, chưa biết có cần sơ tán sang S3 hay export định kỳ không | SYP nêu khi review spec [I] — **chưa có trong bảng QA gửi khách, cân nhắc thêm câu hỏi** |
| 2 | **Xác nhận đích SFTP `/EST`** — nơi e-smart đẩy 6 loại CSV thiết bị mỗi ngày 8:00 — có phải Xzilla/DWH (kho dữ liệu phân tích) không; địa chỉ nằm trong secret nên không tự đọc được từ repo | Tiền đề của đường ② (export định kỳ — phương tiện thực hiện §3.7 bước 4); chi tiết đường xuất nằm ở tập 外部連携・受信系, mục **§3.1** của tập đó (bản JP: §4.1) — mục "Chung cả nhóm: cách nhận cũ–mới và chiều gửi `/EST`" | SYP hỏi mui (kênh QAデータベース Notion, hoặc khi nhận spec HEMS-SV) |
| 3 | Góp danh sách 「既存システムを使い続けたほうがいい機能」 (chức năng nên dùng tiếp của hệ hiện hữu) vào câu trả lời QA 独立デプロイ — vế phụ *"ただし既存システムを使い続けたほうがいい機能があれば教えてほしいです"*; ⚠️ trước khi trả lời cần xác nhận 「既存システム」 chỉ hệ nào. Trả lời 2 vế: ① hệ cũ 旧EMINEL: không batch nào đáng dùng tiếp nguyên trạng (kết luận chung 11 batch) ・ ② e-smart: 4 ứng viên (chung cả 3 tập). Ứng viên từ nhóm này: **cơ chế admin download/export** (đường ①② của §3.3) | Chính là 2 đường "THAY bằng gì" của §1 | SYP trả lời trực tiếp trên trang QAデータベース Notion |

## 5. Nguồn chính đã dùng

- **`legacy_eminel_docs`** (@`ccd8f56`): `docs/03_API仕様/04_バッチ一覧.md`; code 4 command `sources/conciergesv-develop/src/Command/CreateCsvAndZip*Command.php` + `CreateZipsTrait.php` + `DeleteDataCommand.php`; cron: `docs/02_詳細設計/10_バッチ処理/*.txt` (`cron設定概要.txt` — cấu trúc shell và `set -eu`; `mng-webap_cron設定_20241029.txt` — các dòng cron; shell gốc trong `cron実行用シェルスクリプト/eminel-mng-webap.20240909.tgz` cùng thư mục)
- **`eminel_gw_project`** (@`fbc0af0`; điều tra tại `788b438` — các file nhóm này trích giống nhau ở cả 2 commit, xem Giới hạn #4): `docs/eminel/4_spec/admin/I_data_download.md` (spec [I]), `2_management/20_open_issues.md` (SVC-03), `3_requirements/00_integrated_requirements_v1.2.md`; tiền đề: `2_management/22_decisions.md` (quyết định 6/10), `2_management/minutes/20260625_egw_camp_day3.md`, `1_product/10_feature_list.md`; `docs/eminel-smart/` (tài liệu khảo sát ESTA — 6 file; ⚠️ các điểm lệch code: mục Giới hạn #2)
- **`syp-eminelstandard-backend`** (@`dc39aa39`, branch `gw-syp-dev`): `template.yaml`・`template-dynamodb.yaml`, `src/functions/api-download/**`・`batch-download/**`・`api-s3/**`, `src/layers/common/nodejs/**` (`upload-data-backup-to-sftp.ts`, `put-schedule.ts`, `models/CsvDownloadHistory.ts`…)
- **`syp-eminelstandard-web-admin`** (@`e550326`, branch `gw-syp-dev`): `constants/common.ts`, `pages/other/data-management/index.vue`, `components/data-management/form-download-data-management.vue`・`list-download-data-management.vue`
- **QAデータベース Notion** (trạng thái 回答中, tham chiếu 2026-08-04 — mở trang gốc kiểm tra trước khi trích lại): 「旧Eminel基盤継承＋EMINEL-smartサーバーは独立デプロイの確認」 (swan (mui)) ・ 「旧EMINEL調査範囲（conciergesv/eminelsv）とhemssv対象外の確認」 (swan (mui)) ・ 「管理画面は独立か共通か（切替モード追加）の確認」 (masao takahashi (mui))
