# Báo cáo phán định batch hệ cũ — nhóm 外部連携・受信系（Xzilla取込） (3 batch #5–#7)

> 🔰 **Người mới vào dự án**: bảng ngay dưới đây là thông tin quản lý tài liệu — đọc **mục 0** bên dưới bảng trước, rồi hãy quay lại.

| | |
|---|---|
| Ngày lập | 2026-08-06 (ngày điều tra: 2026-08-04) |
| Người lập | Bui Trong Dat (SYP) + AI hỗ trợ điều tra |
| Vị trí tài liệu | Bộ phán định 11 batch hệ cũ (3 nhóm) được tách thành **3 tập theo 3 task trên Notion**; tập này = nhóm **外部連携・受信系（Xzilla取込）, 3 batch #5–#7**. Hai tập kia: 配信・通知系 (#1–#4) và CSV・ZIPエクスポート系 (#8–#11). Số batch #1–#11 là số xuyên suốt, dùng chung giữa các tập và giữa bản Nhật–Việt |
| Nhiệm vụ | Với 3 batch nhóm Xzilla取込 trong `legacy_eminel_docs/docs/03_API仕様/04_バッチ一覧.md` (đều thuộc server `conciergesv` hệ cũ): cái nào **đã có sẵn trong e-smart** (kèm trích code), cái nào phải **tạo mới**, cái nào **bỏ** (kèm các bước làm), căn cứ yêu cầu E-GW trong `eminel_gw_project/docs/eminel` |
| Repo đối chiếu | `legacy_eminel_docs` @ `ccd8f56` ・ `eminel_gw_project` @ `fbc0af0` (điều tra thực hiện tại `788b438` — xem Giới hạn #4) ・ `syp-eminelstandard-backend` @ `dc39aa39` (branch `gw-syp-dev`) ・ `syp-eminelstandard-web-admin` @ `e550326` (branch `gw-syp-dev`) — tất cả trong thư mục `sources/`, đều = origin tại 2026-08-06 |
| Bản tiếng Nhật | `旧EMINELバッチ移行判定報告書_外部連携・受信系（Xzilla取込）3本.md` (cùng thư mục) — bản nộp mui; kết luận, con số, số bước 対応ステップ khớp 1-1 với bản này |

## 0. Tài liệu này là gì? (đọc trước nếu bạn mới vào dự án)

**Bối cảnh một đoạn**: **E-GW (EMINEL Gateway)** là dự án làm hai việc cho dịch vụ EMINEL (khách hàng cuối: 北海道ガス／北ガス): **(1)** thay gateway trong nhà khách (hộp Maxell → gateway do mui Lab làm); **(2)** chuyển phần máy chủ sang nền tảng **e-smart** — hệ đang chạy thương mại của 北ガス (tên khác: **ESTA**, **EMINEL-Smart** — một hệ, ba tên). Hệ EMINEL cũ có vài chục "batch" chạy nền; khi làm server mới phải trả lời: batch nào e-smart **đã có thứ tương đương**, batch nào **phải làm mới**, batch nào **không cần nữa**.

📖 **"Batch" là gì?** Chương trình không có giao diện, hệ thống tự chạy theo lịch hoặc theo sự kiện: tính toán số liệu, nhận/xuất file dữ liệu, gửi thông báo hàng loạt… Người dùng không nhìn thấy batch, nhưng biểu đồ có số liệu là nhờ chúng.

**Nhóm của tập này — 外部連携・受信系（Xzilla取込）** (*nhận dữ liệu từ bên ngoài*): nhận file từ **Xzilla** — hệ **基幹** (hệ thống nghiệp vụ lõi quản lý khách hàng/hợp đồng) của 北ガス: thông tin hủy hợp đồng điện (#5), master (*bảng dữ liệu gốc dùng chung*) người trả tiền (#6), điện lực 30 phút (#7). Mỗi batch được phán định: **dùng lại của e-smart / tạo mới / bỏ**; chỗ "e-smart đã có" thì dán trích code thật kèm giải thích, chỗ "tạo mới/bỏ" thì ghi các bước làm cụ thể.

**Cách đọc**:
- Vội → đọc **§1** (bảng tóm tắt 3 batch + việc cần làm ngay).
- Muốn hiểu căn cứ → **§2** (tiền đề chung) rồi **§3** (chi tiết từng batch theo trình tự cố định: *mục đích → phán định + vì sao đề xuất vậy → hệ cũ đang làm gì (sơ đồ + trích code) → e-smart có sẵn không (vế này của #5/#6 nằm chung ở §3.1) → E-GW yêu cầu gì → sơ đồ luồng mới đề xuất → cách làm từng bước*).
- Việc còn treo → **§4**. Tra nguồn → **§5**. Định **trích dẫn lại** → đọc mục **⚠️ Giới hạn** trước.

**Chú giải nhanh** (thuật ngữ dùng trong tập này):

- **e-smart = ESTA = EMINEL-Smart**: một hệ, ba tên; tên trong code là ESTA. Gồm 3 repo: `backend` (TypeScript trên AWS), `web-admin` (màn hình quản trị), `app` (Flutter).
- **Hệ cũ (旧EMINEL)**: 3 khối server CakePHP/PostgreSQL — **`conciergesv`** (API cho app + gần như toàn bộ batch nghiệp vụ — riêng batch vận hành GW nằm bên `hemssv`; cả 3 batch của tập này đều thuộc `conciergesv`); `eminelsv` (màn quản trị); `hemssv` (giao tiếp gateway). ⚠️ Đừng nhầm `hemssv` (hệ cũ) với **HEMS-SV (m2-cloud)** — thành phần MỚI do mui phát triển cho E-GW, chỉ trùng tên.
- **Stack AWS của e-smart**: **Lambda** = hàm chạy theo sự kiện, không có server thường trực; **DynamoDB** = database NoSQL; **Step Functions** = xâu nhiều Lambda thành luồng nhiều bước (*state machine*); **EventBridge Scheduler** = bộ hẹn giờ; **S3** = kho file; **SFTP** = giao thức chép file mã hóa. Hạ tầng khai báo trong `template*.yaml` (AWS SAM).
- **IF** = "kênh trao đổi file" đánh mã số giữa hai hệ thống (vd IF2249 = file hủy hợp đồng điện Xzilla gửi sang; DM1040 = file danh sách hợp đồng). "E-smart không có IF này" = không có kênh nhận loại file đó. **IF-01** = bản định nghĩa kênh liên kết MỚI giữa E-GW và Xzilla — nội dung vào/ra chưa chốt (= điểm treo **CLD-07**). **T.B.D** = chưa quyết định.
- **port** = bê nguyên code hệ cũ sang hệ mới; "không bê nguyên (port)" = bỏ code, chỉ giữ tri thức nghiệp vụ.
- **Ba nhãn phán định** (dùng ở §1 và §3): **dùng lại** = dùng cơ chế/hạ tầng e-smart sẵn có (≠ 0 công — xem §2) ・ **tạo mới** = làm mới cho E-GW ・ **bỏ (廃止)** = không bê code hệ cũ sang; nghiệp vụ (nếu còn) gộp vào cơ chế sẵn có hoặc phương án mới — vì thế mục "bỏ" vẫn có "cách làm từng bước".
- **速報値/確報値** = giá trị sơ bộ/giá trị chốt ・ **買電/売電** = điện mua vào/bán ra ・ **解約** = hủy hợp đồng ・ **支払者** = người trả tiền ・ **契約種別** = loại hợp đồng ・ **回答中** = QA đang trả lời, chưa chốt ・ **劣後** = lùi sang 2027/4~ ・ **必須** = bắt buộc scope 2026.
- **TagTag** = nền tảng hội viên của 北ガス (cấp định danh + API dữ liệu sử dụng gas/điện) — nguồn dữ liệu năng lượng hiện tại của e-smart (đối lập với đường Xzilla mà E-GW sẽ cần).
- **Mã tham chiếu**: `F-ES-xx` = mã chức năng server trong 統合要件定義書 v1.2 (riêng **F-ES-10** tên chính thức = 「Xzilla連携」) ・ `CLD-xx/SVC-xx` = mã vấn đề mở trong `20_open_issues.md`.
- **cron** = bộ hẹn giờ chuẩn của server Linux; biểu thức `cron(phút giờ ngày tháng ? năm)` diễn giải tại chỗ khi xuất hiện.
- **QAデータベース Notion** = kênh hỏi–đáp nội bộ với mui (danh sách trang: §5) — nguồn các câu trả lời tạm 回答中 được trích trong tập này.
- **Nhãn độ chắc**: **確実** = tự kiểm chứng trên tài liệu/code (khẳng định về e-smart: đã soi trực tiếp code backend/web-admin); ***推定*** = suy đoán có căn cứ, chưa kiểm chứng — không dùng làm quyết định cuối; 🔸 = giả thuyết chưa kiểm chứng (tương ứng *推定（未確認）* trong bản JP). Dẫn chứng sau ký hiệu 🔍, đường dẫn tính từ `sources/`. Trong khối code, dòng chỉ có `...` — và cụm `...` nằm bên trong dòng (vd `${...}`, `DM1040: ...`) — đều là ký hiệu lược bớt của báo cáo, không phải code; comment tiếng Việt = chú thích thêm của báo cáo. "**grep X: 0 hit**" = tìm chuỗi X toàn bộ code không ra kết quả — cơ sở khẳng định "không tồn tại".

## ⚠️ Giới hạn & lưu ý xác thực (đọc trước khi trích dẫn lại)

1. Các khẳng định "e-smart có/không có X" đều đã **kiểm chứng trực tiếp trên code** `syp-eminelstandard-backend` + `syp-eminelstandard-web-admin` (branch `gw-syp-dev`).
2. ⚠️ Bộ **tài liệu khảo sát ESTA** có sẵn của dự án (`eminel_gw_project/docs/eminel-smart/`, 6 file) có **6 chỗ lệch với code thực tế** (phát hiện khi đối chiếu code); 5 chỗ liên quan tập này — ai trích tài liệu khảo sát phải kiểm code trước:
   | Tài liệu khảo sát ghi | Code thực tế |
   |---|---|
   | Import 基幹 「日次・深夜〜早朝」 (`02_product_overview.md:30, 63-64`) | `cron(5 0-7 * * ? *)` — **mỗi giờ một lượt**, 0h–7h JST (§2) |
   | Lock hội viên khi merge 「6分」 (`02_product_overview.md:73, 78`) | `UPDATE_LOCK_TTL_MINUTES = 5` (§3.1) |
   | `CsvDownloadHistory` = 「CSVダウンロード履歴」 gợi ý lịch sử admin download (`03_backend_models.md:107`) | Là lịch sử **tải file TỪ SFTP về** (chiều nhận, chống tải trùng) — không liên quan admin download (§3.1) |
   | 「自動化ルール実行（毎分）」 (`02_product_overview.md:85`) | Không chạy mỗi phút — mỗi rule một lịch tuần tạo động (§2; grep `rate(`: 0 hit) |
   | Lambda runtime 「Node.js 20.x, arm64」 (`02_product_overview.md:49`) | `Runtime: nodejs24.x` (`template.yaml:181`; riêng CompatibleRuntimes của common layer vẫn nodejs20.x — dòng 3163) |
   *(điểm lệch thứ 6 — số lượng gửi Push — thuộc tập 配信・通知系)*
3. Ba trang QA Notion được trích (§5) ở trạng thái **回答中**, tham chiếu ngày 2026-08-04 qua ảnh chụp màn hình — trước khi trích lại phải mở trang gốc kiểm tra.
4. **Về cập nhật repo yêu cầu 788b438 → fbc0af0** (6 commit, tối 03/08 → tối 05/08): thay đổi chỉ nằm ở `docs/eminel/3_requirements/app/` (13 file yêu cầu app) + 1 dòng skill — **các tài liệu tập này trích (統合要件 v1.2, 機能一覧, 業務プロセス, 未決事項, 決定ログ, 議事録 camp, tài liệu khảo sát ESTA) không đổi**, đã xác nhận 2026-08-06. Kết luận phán định và số dòng trích dẫn của tập này giữ nguyên giá trị ở cả hai commit. (Riêng tập 配信・通知系 có trích 2 file app bị sửa — B05/D03 — nên số dòng trích dẫn được cập nhật trong tập đó.)

---

## 1. Kết luận tổng — tóm tắt 3 batch

| # | Batch | Hệ cũ đang làm | e-smart có sẵn? | E-GW cần? | **Đề xuất** | Chi tiết |
|---|---|---|---|---|---|---|
| 5 | `RcvCntctCancellationCommand` (IF2249) | Mỗi 5 phút nhận CSV 解約 điện, bật cờ dừng tính 買電売電 | **Không có IF này** (grep 0 hit) — nhưng có sẵn luồng nhận SFTP→S3→DynamoDB (8 IF khác) + hậu xử lý hết hạn hợp đồng | Không có yêu cầu trực tiếp (flow chỉ định: vô hiệu GW sau 解約 = thao tác thủ công trên màn quản trị); **gián tiếp cần** — cờ dừng tính phục vụ #7 | **Bỏ BATCH (code cũ không bê sang) — GIỮ NGHIỆP VỤ** "bật cờ dừng tính khi khách hủy hợp đồng", chạy nhờ luồng nhận Xzilla sẵn có của e-smart. IF-01 (kênh Xzilla mới) có dữ liệu 解約 → thêm 1 loại file vào luồng đó; không có → nêu yêu cầu bổ sung ngay. Chờ CLD-07 (*vấn đề mở về định nghĩa vào/ra + xác thực của IF-01*) chốt | §3.2 ・ đề xuất *推定*, vế e-smart 確実 |
| 6 | `RcvEmsPlsCntrPayerCommand` (IF2264) | Mỗi 5 phút **xóa toàn bộ rồi nạp lại master 支払者 — chỉ nạp các 契約種別 đối tượng (PE624/625/650/651/652・PG077/079)** + áp 契約終了判定 3 điều kiện | **Không có IF này** (grep 0 hit) — đã có import 契約/顧客 master (IF2023/2024/DM1040, DM1040 lọc sẵn vai trò 支払者) | Không nhắc riêng; gián tiếp phục vụ グルーピング (*tính năng gộp nhóm hộ gia đình để so sánh/làm báo cáo* — 必須 2026) | **Bỏ BATCH (bỏ kiểu "5 phút xóa hết nạp lại") — GIỮ DỮ LIỆU VÀ TRI THỨC**: dữ liệu người trả tiền nhận qua luồng import hợp đồng e-smart đã có (mở rộng theo IF-01); 契約終了判定 3 điều kiện trích ra giữ thành spec | §3.3 ・ đề xuất *推定*, vế e-smart 確実 |
| 7 | `RcvHalfHourElectricPowerCommand` (IF1156) | Mỗi 10 phút nhận 電力30分値: 速報値 nạp-lại-toàn-bộ, **確報値 ghi bổ sung (tích lũy)**; gộp 30分→1時間, tính 買電売電 theo cấu hình nhà | **Không** (grep 0 hit) — điện/gas của e-smart đi TagTag API, không có đường Xzilla | **Cần, minh văn, scope 2026** (「電力30分値はCルート（Xzilla経由）で取得する」) | **Tạo mới** theo pattern import e-smart; kế thừa logic nghiệp vụ từ code cũ. Batch nặng nhất trong cả 11 | §3.4 ・ 確実 |

**Ba lưu ý đọc kèm bảng**:
- Nhãn **確実/*推定*** chứng nhận phần **dữ kiện** (hệ cũ làm gì, e-smart có/không, scope) — phần **Đề xuất** luôn là phán đoán để team review; #5/#6 phán đoán dựa suy luận nhiều hơn nên tách nhãn *推定* riêng.
- Báo cáo chỉ phán định *làm gì / dùng lại gì*, **chưa ước lượng công số** — công số ước khi tách 1 batch = 1 task trên Notion (phương châm §2); #7 là batch nặng nghiệp vụ nhất trong toàn bộ 11 batch.
- **Đừng đếm task chỉ theo số batch cũ**: chiều GỬI (e-smart → 基幹, thư mục `/EST`) đã có sẵn 1 luồng — khi lập danh mục task Xzilla phải thêm mục chiều gửi này (§3.1).

**Ba việc rút ra cần làm ngay** (không chờ đủ spec):

1. **Xác nhận đích của luồng export SFTP `/EST`** (§3.1): e-smart đang đẩy 6 loại CSV thiết bị lên SFTP hằng ngày, nhưng đích có phải Xzilla/DWH (kho dữ liệu phân tích) không thì **không tự xác nhận được từ repo** — địa chỉ nằm trong secret (kho cấu hình mật ngoài code) → hỏi mui (§4#2). Liên quan trực tiếp 「EMINELデータの共有」 của F-ES-10.
2. **Bám CLD-07 (định nghĩa 入出力 IF-01 Xzilla)** — cả 3 batch đều phụ thuộc IF-01. Trong lúc chờ: soạn sẵn danh mục trường cần thiết từ code cũ (§3.3 bước 1 + chuẩn bị dữ liệu đối chiếu cho bước 2 — làm ngay được).
3. **Góp danh sách 「既存システムを使い続けたほうがいい機能」** — câu hỏi phụ nằm trong QA 「旧Eminel基盤継承＋EMINEL-smartサーバーは独立デプロイの確認」 (swan (mui), 回答中): câu trả lời đầy đủ gồm 2 vế (① hệ cũ 旧EMINEL: không có batch nào đáng dùng tiếp nguyên trạng ・ ② e-smart: 4 ứng viên), chung cho cả 3 tập; từ nhóm này, ứng viên là **luồng nhận Xzilla SFTP→S3→DynamoDB** (§4#3).

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
| Database | PostgreSQL (partition theo ngày/tháng) | DynamoDB (PITR — backup hạ tầng — bật sẵn) |
| Cách chạy batch | cron trên server (`/etc/cron.d/eminel-mng-webap`), shell + flock chống chạy trùng | Step Functions + EventBridge Scheduler |
| Nhận file ngoài | SFTP về đĩa server | SFTP → S3 → DynamoDB |

- 🔍 hệ cũ: `legacy_eminel_docs/docs/02_詳細設計/10_バッチ処理/cron設定概要.txt` dòng 1–37 (flock nằm trong các file `.sh` thuộc `cron実行用シェルスクリプト/eminel-mng-webap.20240909.tgz` cùng thư mục) ・ e-smart: `syp-eminelstandard-backend/template.yaml` (SAM), `eminel_gw_project/docs/eminel-smart/02_product_overview.md` dòng 48–53

**Nền batch của e-smart** (điều E-GW sẽ thừa hưởng — đường dẫn tính từ `syp-eminelstandard-backend/`):

- Chỉ có **3 lịch tĩnh** (`ScheduleV2`, timezone `Asia/Tokyo` — `template.yaml:9-11`):
  - ① `BatchRunSequentiallyStateMachine` — nhập dữ liệu 基幹, `cron(5 0-7 * * ? *)` = phút :05 **mỗi giờ từ 0h–7h JST** (`template.yaml:853-888`, cron dòng 881–882) — **luồng nhận của nhóm này nằm ở đây**;
  - ② `BatchMigrationIntegratedDataStateMachine` — dữ liệu thiết bị Rinnai/Noritz + export, `cron(0 8 * * ?)` (*= 8:00 hằng ngày* — `template.yaml:2205-2240`, cron dòng 2233) — **chiều gửi `/EST` nằm ở đây**;
  - ③ `BatchGetErrorDeviceInfoOfRinnaiStateMachine` — lỗi thiết bị, 8:00 (`template.yaml:2966-2980`).
- **Mọi batch còn lại dùng lịch tạo động qua EventBridge Scheduler** — phần lớn là one-shot (lịch một thời điểm, chạy xong tự xóa — hàm chung `src/layers/common/nodejs/services/put-schedule.ts:18-33`); ngoại lệ duy nhất là automation rule của user (quy tắc tự động hóa thiết bị đặt trong app) — mỗi rule một lịch tuần lặp lại tạo động, không tự xóa (`src/functions/api-automation/common.ts:115, 167-175`).
- **Không có polling** (*hỏi lặp định kỳ*) **mỗi phút** (grep `rate(`: 0 hit) — tiền đề quan trọng khi nghĩ chỗ "đặt" các batch 5 phút/10 phút của hệ cũ.

**Phạm vi SYP**: theo QA 「旧EMINEL調査範囲（conciergesv/eminelsv）とhemssv対象外の確認」 (swan (mui), 回答中) — `conciergesv`/`eminelsv` là đối tượng SYP **điều tra**, không phải phạm vi phát triển tiếp trên hệ cũ; giao tiếp GW đi qua HEMS-SV (m2-cloud) do mui làm, spec chia sẻ sau.

**Quyết định scope 2026-06-10** (đã vào 決定ログ): 必須 = 暖房機能/暖房制御/照明アドバイス※/ポイント連携/グルーピング・レポート; 劣後 (→2027/4~) = 複合制御・DR・ダッシュボード・バッジ等. ※「照明アドバイス」 nghi là lỗi ghi của 省エネアドバイス (*推定*).
- 🔍 `eminel_gw_project/docs/eminel/2_management/22_decisions.md` dòng 30–31 ・ quy ước bảng 機能一覧 (`10_feature_list.md`): cột 劣後 đánh **✅ = lùi được sang 2027**, ô trống = 今期必須.

**Chủ thể các bước trong §3**: trừ khi ghi khác, người thực hiện là **SYP**, code viết trên branch `gw-syp-dev`; đường dẫn không ghi tên repo = `syp-eminelstandard-backend`. Các bước "chốt/hỏi" đi theo kênh §4.

---

## 3. Chi tiết nhóm 外部連携・受信系（Xzilla取込）

*(Quy ước dẫn nguồn trong §3: đường dẫn `RcvXxx…Command.php` = `legacy_eminel_docs/sources/conciergesv-develop/src/Command/…`; "cron dòng NN" = số dòng trong `legacy_eminel_docs/docs/02_詳細設計/10_バッチ処理/mng-webap_cron設定_20241029.txt`; đường dẫn không ghi tên repo = `syp-eminelstandard-backend`.)*

### 3.1 Chung cả nhóm: cách nhận cũ–mới và chiều gửi `/EST`

#### Luồng nhận của hệ cũ

File CSV từ Xzilla qua **SFTP vào 中間サーバ** (server trung gian), mỗi 5–10 phút một lượt:

```
Xzilla ──SFTP (5–10 phút/lượt)──▶ [đĩa 中間サーバ] ──▶ PHP Command (cron + flock) ──▶ [PostgreSQL]
                                                        · RcvCntctCancellation…  ──▶ ipf_cntct_cancellations + cờ t_101.c065
                                                        · RcvEmsPlsCntrPayer…    ──▶ ipf_ems_pls_cntr_payers + t_101
                                                        · RcvHalfHourElectric…   ──▶ emn_all/emn_fast/emn_confirm + s_102
```

#### Luồng nhận của e-smart (確実 — dẫn chứng code)

Luồng **SFTP → S3 → DynamoDB**:

```
Xzilla ──SFTP──▶ [SFTP server: 8 thư mục IF + END/*.dat]     (.dat = danh sách file đã chốt của "chuyến hàng")
                   │
                   │ ① batch-get-list-file-name-from-sftp-server/
                   │    · đọc .dat lấy danh sách file (app.ts:52-66)
                   │    · chống tải trùng: bảng CsvDownloadHistory (app.ts:69-87)
                   ▼
                 [S3] file chia gói 50 000 dòng               ② batch-forward-csv-from-sftp-server-to-s3/ (app.ts:56-64)
                   ▼
                 ③ 8 handler batch-ifXXXX-import-* ──ghi transaction──▶ [DynamoDB]
                   ·  IF2241 → DM1040 → IF2242 (TUẦN TỰ)  ──────────▶ TABLE_KAIIN (bảng hội viên)
                   ·  IF2016/2023/2024/2029/2223 (SONG SONG) ───────▶ bảng riêng từng kênh (TABLE_IF2016_SERVICE_POINT_NO_INFO…)
                   ▼
                 ④ 3 hậu xử lý ①②③ (nghiệp vụ phái sinh sau import)
  ⏰ Lịch: cron(5 0-7 * * ? *) = phút :05 mỗi giờ 0–7h JST — state machine batch_run_sequentially.asl.json
```

Chi tiết từng khâu:

- **Điều phối**: state machine `src/statemachine/batch_run_sequentially.asl.json` — trình tự: chống chạy chồng (dòng 5–38) → dọn temp → list file → 8 nhánh forward song song → import → 3 hậu xử lý; chạy **mỗi giờ một lượt từ 0h–7h JST** (`cron(5 0-7 * * ? *)` — §2).
- **Danh mục thư mục IF trên SFTP** nằm ngay trong code — 🔍 `src/functions/batch-get-list-file-name-from-sftp-server/app.ts:149-169`:

```ts
const DEFAULT_FOLDER_CSV = {         // `${x}` = cú pháp chèn giá trị biến x vào chuỗi (TypeScript)
  IF2241: `${folderTemp}/IF2241/`,   // hội viên TagTag       DM1040: danh sách hợp đồng
  DM1040: ..., IF2242: ...,          // IF2242: thuộc tính hội viên
  IF2016: ..., IF2023: ...,          // IF2016: 供給地点 / IF2023: 使用契約
  IF2024: ..., IF2029: ..., IF2223: ...,  // 顧客 / 建物 / 機器
};
const DEFAULT_FILE_NAME_METADATA = {
  IF2241: `${folderTemp}/IF2241/END/IF22410001_{%1}.dat`,  // file .dat trong END/ = "chuyến hàng đã chốt"
  ...
```

- **Mỗi IF** = một thư mục CSV + một file metadata `.dat` trong `END/` (đọc `.dat` để biết danh sách file CSV thực của chuyến — dòng 52–66); **chống tải trùng** bằng bảng `CsvDownloadHistory` (dòng 69–87 — vai trò thật của bảng này, xem Giới hạn #2).
- **Chia gói & ghi DB**: file chia gói 50 000 dòng đẩy lên S3 (`batch-forward-csv-from-sftp-server-to-s3/app.ts:56-64`) rồi các handler (*handler = hàm Lambda đảm nhận xử lý một loại file*) `batch-ifXXXX-import-*` ghi DynamoDB bằng transaction (*gói thao tác "được ăn cả ngã về không"*).
- **Điểm đến cuối cùng trong database** (bảng DynamoDB — xác nhận theo hằng `TABLE_*` trong `app.ts` của từng handler):
  - IF2241/IF2242/DM1040 → cùng bồi đắp **bảng hội viên `TABLE_KAIIN`** (đây chính là lý do 3 kênh này phải import **tuần tự** IF2241 → DM1040 → IF2242);
  - 5 kênh sau mỗi kênh một bảng riêng nên chạy song song được (asl dòng 493–794): IF2016 → `TABLE_IF2016_SERVICE_POINT_NO_INFO` (供給地点); IF2023 → `TABLE_IF2023_USE_CNTR_INFO` (使用契約); IF2024 → `TABLE_IF2024_CUSTOMER_INFO` (顧客); IF2029 → `TABLE_IF2029_BUILDING_INFO` (建物); IF2223 → `TABLE_IF2223_EQUIPMENT` (機器).

**Chi tiết từng kênh IF** (mỗi IF một hàng — để thấy database phía sau từng kênh). Trường lấy từ interface trong code backend (`src/layers/common/nodejs/interfaces/IData*.ts` — mapped type trỏ về enum cột thật `LIST_COL_*`, `constants.ts:468-565` — nguồn 一次); bảng nguồn 基幹 + nhãn theo bảng IF của tài liệu khảo sát ESTA (`eminel_gw_project/docs/eminel-smart/02_product_overview.md:68-75`, đối chiếu `03_backend_models.md:90-97`) — chỗ nào hai nguồn vênh thì theo code (xem Giới hạn #2). Nghĩa trong ngoặc suy từ tên trường + tài liệu khảo sát — coi là *推定* trừ chỗ có nguồn minh văn; "x/y cột" = liệt kê x cột tiêu biểu trong tổng y cột code dùng:

| IF | Nguồn phía 基幹 | Trường chính (từ interface trong code) | Bảng đích DynamoDB | Tác dụng nghiệp vụ |
|---|---|---|---|---|
| IF2241 | `TAG_KAIIN` (hội viên TagTag) | 5/11 cột: `kaiinBango` (số hội viên — khóa), `custShikibetsuBango` (số định danh khách), `status` (trạng thái hội viên), `loginId` (ID đăng nhập), `yubinBango` (mã bưu điện) | `TABLE_KAIIN` (tài liệu khảo sát: 「KaiinTable + 16関連」 — :73) | Xương sống danh tính hội viên — điểm khởi đầu merge tài khoản app ↔ khách 北ガス; IF2242/DM1040 phải chờ kênh này import xong (直列) |
| DM1040 | `MRT_TAGTAGAPI` (TagTag API) | 5/14 cột: `roles` (vai trò trên hợp đồng — chỗ lọc 支払者), `kaiinbango` (số hội viên), `oc_z_customer_no` (お客様番号), `oc_j_supply_place_no` (số điểm cung cấp), `curd_flg` (cờ thêm/sửa/xóa) | `TABLE_KAIIN` — mảng `list_contract` | Danh sách hợp đồng của từng hội viên — nối hội viên ↔ hợp đồng/điểm cung cấp; vai trò người trả tiền có sẵn ở đây (§3.3) |
| IF2242 | `tag_kaiinzokusei` (thuộc tính hội viên) | 3/3 cột: `kaiinBango`, `zokuseiId` (ID thuộc tính), `kaitouCd` (mã câu trả lời) | `TABLE_KAIIN` — mảng `list_zokusei` | Gắn thuộc tính (câu trả lời khảo sát) vào hội viên — nền targeting nội dung |
| IF2016 | `ipf_sp_history` (lịch sử 供給地点) | 5/7 cột: `source_sp_num` (số điểm cung cấp — PK), `reg_start_ymd`/`reg_end_ymd` (hiệu lực từ/đến), `cis_use_cntr_num` (số hợp đồng sử dụng CIS), `use_type_code` (mã loại sử dụng) | `TABLE_IF2016_SERVICE_POINT_NO_INFO` | Danh mục điểm cung cấp năng lượng — nối địa điểm ↔ hợp đồng sử dụng |
| IF2023 | `ipf_use_cntr_history` (lịch sử hợp đồng sử dụng) | 6/14 cột: `source_use_cntr_num` (số hợp đồng — PK), `reg_start_ymd` (hiệu lực bản ghi), `cntr_clsfy_code` (契約種別 — chính là mã PE/PG mà #5/#6 lọc), `cntr_start_ymd`/`cntr_end_ymd` (thời hạn hợp đồng), `cntr_watt` (công suất hợp đồng) | `TABLE_IF2023_USE_CNTR_INFO` | Hợp đồng sử dụng + loại/thời hạn hợp đồng — hậu xử lý ③ đọc bảng này để biết hợp đồng hết hạn |
| IF2024 | `ipf_cus_meigi` (danh nghĩa khách) | 5/8 cột: `source_cus_meigi_num` (số danh nghĩa khách — PK), `links_cus_num` (số khách liên kết), `sex` (giới tính), `birth_yyyy` (năm sinh), `household_num` (số người trong hộ) | `TABLE_IF2024_CUSTOMER_INFO` | Nhân khẩu của khách — phục vụ targeting/thống kê theo hộ |
| IF2029 | `ipf_bld` (tòa nhà) | 4/5 cột: `source_bldno` (số tòa nhà — khi ghi đổi tên thành `bld_no`, `batch-if2029-import-building-info/app.ts:30`), `bld_divcod_1` (建物種別 — phân loại tòa nhà), `bld_use_type` (loại sử dụng), `newbldno_area` (khu vực) | `TABLE_IF2029_BUILDING_INFO` | Thông tin tòa nhà — nguồn 建物種別 mà グルーピング (必須 2026) cần (§3.3) |
| IF2223 | `lnk_ot_pgedgkk` (thiết bị sở hữu) | CSV 130+ cột (`02_product_overview.md:72`) — code chỉ dùng 13; tiêu biểu: `oc_z_gas_sp_no` (điểm cung cấp gas — thành PK `gas_sp_no`), `oc_j_gkiki_clsfy_code`＋`oc_h_estkk_mno` (ghép thành SK `equipment_code` — `batch-if2223-import-equipment/app.ts:49`), `oc_z_kiki_hinmok_code` (mã phẩm mục thiết bị), `oc_z_remove_date` (ngày tháo dỡ) | `TABLE_IF2223_EQUIPMENT` | Thiết bị gas lắp tại nhà khách (kèm bảo hành, ngày lắp/tháo) — nền dữ liệu cho chức năng thiết bị |

- **Lock 5 phút** khi merge hội viên "fake" (đăng ký app trước khi có data Xzilla) — 🔍 `batch-if2241-import-tagtag-kaiin/app.ts:69, 102-111`:

```ts
const UPDATE_LOCK_TTL_MINUTES = 5;
...
const kaiinUpdatingItem = {
  kaiin_bango: kaiinBangoFake,
  ttl: dayjs().add(UPDATE_LOCK_TTL_MINUTES, 'minute').unix(),  // lock tự hết hạn bằng TTL (bản ghi tự xóa khi quá hạn)
};
await putDataToDBWrap(TABLE_KAIIN_UPDATING as string, kaiinUpdatingItem);
```

(39 API handler kiểm lock này qua `src/layers/common/nodejs/business-logic/check-kaiin-updating.ts:10-15` để chặn thao tác khi đang merge.)

**3 hậu xử lý** sau import (khối ④ trong sơ đồ):

- ① phát lại nội dung đang chạy cho hội viên mới (`batch-send-contents-to-updated-user/app.ts:79-132`);
- ② cập nhật nơi-ở-đang-chọn khi hợp đồng gas hết hiệu lực + cấp badge khi xuất hiện hợp đồng sưởi **「ゆーぬっく」**. Chi tiết định danh: hằng code YUNUKKU, mã hợp đồng `PG003`, tên đầy đủ trong bảng hằng số backend là **「ゆーぬっく２４ネオ」** (`constants.ts:1065`); chỗ xử lý: `batch-update-selecting-place-no/app.ts:89-143, 283-296` + `constants.ts:1909`;
- ③ xóa liên kết + thiết bị khi hết hợp đồng gas (`batch-remove-integration-expired/app.ts:44-79` — đọc `TABLE_IF2023_USE_CNTR_INFO` để biết hợp đồng hết hạn, rồi xóa trên `TABLE_KAIIN`, `TABLE_MUI_DEVICE`, `TABLE_MUI_SENSOR`).

*(Hậu xử lý ② thao tác trên `TABLE_KAIIN` + `TABLE_IF2023_USE_CNTR_INFO` — cùng cách tra hằng `TABLE_*` như trên.)*

#### Ba IF của hệ cũ đều KHÔNG tồn tại trong e-smart (確実)

Grep toàn backend `IF1156`・`IF2249`・`IF2264`・`30分`・`HalfHour`・`half_hour`・`速報`・`確報`・`electric_power`・`cntct` = **0 hit**. (Biến thể camelCase `ElectricPower` chỉ có 1 chỗ — `src/layers/common/nodejs/services/daikin.ts:73`, thuộc tính công suất tức thời của điều hòa Daikin, không liên quan 電力30分値. Từ `payer` chỉ xuất hiện dưới dạng hằng lọc vai trò 支払者 khi import DM1040 — `batch-dm1040-import-user-contract-list-preprocessing/app.ts:54, 63` — củng cố rằng thông tin người trả tiền đã được xử lý trong luồng DM1040, không có IF riêng.)

#### Chiều GỬI (e-smart → 基幹) qua `/EST` — có thật (確実)

```
[dữ liệu thiết bị lấy về trong ngày] ──▶ BatchMigrationIntegratedDataStateMachine (8:00 hằng ngày — template.yaml:2215-2226)
        ──▶ 6 file CSV (5 loại 給湯器 + remote hồng ngoại) ──SFTP, tài khoản upload riêng──▶ [/EST]  đích = Xzilla/DWH? 🔸 chưa xác nhận — hỏi mui
```

Dẫn chứng code — 🔍 `src/layers/common/nodejs/services/upload-data-backup-to-sftp.ts:22-43, 52-57`:

```ts
const pathExport = '/EST';                       // thư mục đích trên SFTP
switch (dataType) {
  case DEVICE_DATA_TYPE.INFRARED_REMOTE:
    prefixFileName = `sekigaisenrimokon_${...}`; // remote hồng ngoại (${...} = tem thời gian, đã lược)
    ...                                          // break; — mỗi case đều có, đã lược
  case DEVICE_DATA_TYPE.USAGE_DAILY:
    prefixFileName = `kyutoki_usage_daily_${...}`; // kyutoki = 給湯器 (máy nước nóng)
    ...
await connectSftpWithRetry(sftp, {
  host: serverInfo.host, port: serverInfo.port,
  username: serverInfo.username_for_upload,      // user RIÊNG cho chiều upload
  private_key: serverInfo.private_key_for_upload,
});
```

Chi tiết:

- **Nội dung gửi**: 6 loại CSV dữ liệu thiết bị (5 kyutoki + remote hồng ngoại) đẩy lên thư mục `/EST` của **cùng SFTP server** bằng tài khoản upload riêng, chạy hằng ngày 8:00 trong `BatchMigrationIntegratedDataStateMachine` (`template.yaml:2215-2226`).
- 🔸 *Giả thuyết — CHƯA kiểm chứng: đích `/EST` là Xzilla/DWH (kho dữ liệu phân tích) — địa chỉ nằm trong secret ngoài code, phải hỏi mui. Nếu đúng, đây là hiện thực sẵn có của* 「EMINELデータの共有」 *(F-ES-10 chiều xuất — `00_integrated_requirements_v1.2.md:696`).*
- Khi lập danh mục task Xzilla phải **thêm mục chiều xuất này**.
- Ghi chú: camp day3 dòng 126 nhắc アプリログ gửi 基幹 "có thể đã có ở ESTA" — đã kiểm: backend **không** có đường đẩy app log ra SFTP, chỉ có download cho admin.

#### Bảng đối chiếu tương quan hệ cũ ↔ hệ mới

(Phạm vi nhóm này — để nhìn một phát biết cái gì ở đâu trong mỗi thế hệ.)

| Thành phần | Hệ cũ (`conciergesv` — PHP/PostgreSQL) | Hệ mới (e-smart/E-GW — Lambda/DynamoDB) |
|---|---|---|
| Đường nhận file Xzilla | SFTP kéo về đĩa 中間サーバ (server trung gian), cron mỗi 5–10 phút | SFTP → S3 → DynamoDB, cửa sổ 0–7h mỗi giờ (state machine `batch_run_sequentially.asl.json`) |
| Chống chạy trùng / tải trùng | shell `flock` (khóa file trên server) | khối chống-đa-khởi-động trong asl (dòng 5–38) + bảng `CsvDownloadHistory` chống tải trùng file |
| #5 dữ liệu hủy hợp đồng điện | bảng `ipf_cntct_cancellations` + cờ dừng tính `t_101.c065` | *(tương lai — chờ IF-01)* thêm 1 loại file vào luồng nhận + hậu xử lý ④ bật cờ trên bảng hộ của E-GW (§3.2 bước 2–3) |
| #6 master người trả tiền | bảng `ipf_ems_pls_cntr_payers` — 5 phút xóa-nạp toàn bộ | KHÔNG có bảng riêng — dữ liệu nằm trong `TABLE_KAIIN` + `TABLE_IF2023_USE_CNTR_INFO`/`TABLE_IF2024_CUSTOMER_INFO` (3 kênh hợp đồng sẵn có, mở rộng trường theo IF-01 — §3.3 bước 2) |
| #7 điện 30 phút | `emn_all`/`emn_fast_electric_powers` (速報 — xóa-nạp lại) + `emn_confirm_electric_powers` (確報 — tích lũy); kết quả giờ ghi bảng `s_102` | bảng mới tách 速報/確報, khai trong `template-dynamodb.yaml` (§3.4 bước 3); kết quả giờ nối sang nhóm batch 集計 |
| Lịch chạy | cron cố định trên server (`/etc/cron.d/eminel-mng-webap`) | 3 lịch tĩnh `ScheduleV2` + lịch one-shot tạo động (§2) |

### 3.2 #5 `RcvCntctCancellationCommand` — nhận 解約 điện (IF2249)

**Mục đích của batch** (đọc trước để định vị): đồng bộ trạng thái *hủy hợp đồng điện* từ hệ 基幹 (Xzilla) vào EMINEL. Nó lo 3 việc: lưu thông tin hủy; **ngừng tính 買電売電** cho khách đã hủy (không ngừng thì số liệu điện của khách đó sai từ ngày hủy); và gọi API báo "đăng ký thông tin khách hoàn tất" khi dữ liệu trong ngày đã đủ.

**Phán định** (*推定*): **BỎ BATCH — GIỮ NGHIỆP VỤ.** Nói rõ để không hiểu nhầm:

- Cái bị bỏ là *code PHP + kiến trúc "batch riêng chạy mỗi 5 phút"* của hệ cũ.
- Cái phải giữ là *việc nghiệp vụ* — khi khách hủy hợp đồng điện phải bật cờ "dừng tính 買電売電" — vì E-GW vẫn tính 買電売電 từ 30分値 (#7, §3.4), không có cờ này thì khách đã hủy vẫn bị tính tiếp.
- Nghiệp vụ đó sẽ chạy nhờ **luồng nhận Xzilla sẵn có của e-smart** (thêm 1 loại file + 1 hậu xử lý — bước 2–3), không dựng batch mới.
- (Flow thủ công trong tài liệu nghiệp vụ chỉ định nghĩa "vô hiệu GW sau 解約", KHÔNG nói gì đến dừng tính — nên không thể coi việc này đã có chỗ khác lo.)

*Vì sao đề xuất vậy* (tóm từ dữ kiện bên dưới):

- e-smart **không có IF2249** (grep 0 hit — §3.1) nhưng **có sẵn** luồng nhận Xzilla SFTP→S3→DynamoDB (8 IF) + chỗ đặt hậu xử lý sau import — thêm 1 loại file là chạy được.
- Phương châm camp Day3 (§2): batch hiện hành 「いけてない」 — làm lại chứ không bê nguyên code PHP.
- Nghiệp vụ "bật cờ dừng tính" vẫn bắt buộc vì #7 cần cờ này khi tính 買電売電, mà flow thủ công (vô hiệu GW trên 管理画面) không cover → bỏ batch, giữ nghiệp vụ, gộp vào luồng sẵn có.

**Hệ cũ** (確実) — luồng:

```
[cron */5 phút] ──▶ RcvCntctCancellationCommand.php
    │ ① SFTP lấy CSV 解約 hôm nay
    │ ② lọc 契約種別 PE624/625 (:242-243)
    ▼
[PostgreSQL] upsert ──▶ ipf_cntct_cancellations
    │ ③ bật cờ dừng tính: t_101.c065 = 1 (:306-334)
    ▼
    ④ nếu IF2264 hôm nay đã nhập xong ──▶ gọi 顧客情報登録完了通知API (:193-217)
```

Trích code then chốt (khâu ② — điều kiện lọc đối tượng) — 🔍 `RcvCntctCancellationCommand.php:242-245`:

```php
// 契約種別が'PE624'または'PE625'以外は、登録しない    ← chỉ nhận 2 loại hợp đồng điện đối tượng
if ($line[58] != 'PE624' && $line[58] != 'PE625') {
    continue;
}
```

Chi tiết hệ cũ:

- Mỗi 5 phút SFTP lấy CSV hôm nay; lọc 契約種別 PE624/625 (dòng 242–243).
- Upsert (*có thì cập nhật, chưa có thì thêm*) vào `ipf_cntct_cancellations`.
- **Bật cờ dừng tính 買電売電** (`t_101.c065=1`) cho khách đã hủy.
- **Chỉ khi** phần nhập dữ liệu 支払者 (IF2264) của ngày hôm đó đã hoàn tất mới gọi 顧客情報登録完了通知API.
- 🔍 `RcvCntctCancellationCommand.php:30, 99-113, 193-217, 242-243, 306-334` ・ cron dòng 107–108

**E-GW**: không có yêu cầu riêng cho luồng 解約 tự động; flow nghiệp vụ ghi rõ vô hiệu hóa GW sau giải ước là **thao tác thủ công trên 管理画面**; IF-01 còn treo (CLD-07 ~10 mục 要確認). 🔍 `1_product/11_business_process/readme.md:938-941, 945-952` ・ `20_open_issues.md:181-182`

**Luồng mới đề xuất** (hiện thực của phán định trên):

```
IF-01 (chờ CLD-07 chốt) ──▶ luồng nhận sẵn có (§3.1) + 1 loại file mới
        ▼
   handler import mới ──▶ [DynamoDB] bảng 解約 (thiết kế theo IF-01)
        ▼
   hậu xử lý ④ ──▶ bật cờ "dừng tính" trên bảng hộ E-GW ──▶ #7 đọc cờ khi tính 買電売電
```

**Cách làm từng bước**:
  1. Khi CLD-07 (*vấn đề đang mở: phần định nghĩa vào/ra + xác thực của IF-01 chưa được viết*) / IF-01 (*kênh liên kết E-GW⇔Xzilla mới — dòng 1 bảng IF一覧 của 統合要件 v1.2 §4-1, đi qua 北ガスクラウド*) định hình: xác nhận có luồng dữ liệu 解約 (hủy hợp đồng điện) không. **Nếu không có → nêu yêu cầu bổ sung ngay qua CLD-07 hoặc QAデータベース (kênh QA nội bộ với mui).**
     - *Vì sao*: #7 (batch điện 30 phút) cần cờ dừng tính; nếu lặng lẽ bỏ batch này mà IF-01 cũng không có dữ liệu 解約 thì không ai bật cờ → khách đã hủy vẫn bị tính 買電売電.
  2. Nếu có luồng 解約: KHÔNG tạo batch 5-phút riêng — thêm 1 loại IF (*kênh file với Xzilla*) vào luồng import sẵn có. Các file code phải sửa, theo đúng pattern của 8 IF hiện hữu (§3.1):
     - `src/functions/batch-get-list-file-name-from-sftp-server/app.ts` (*Lambda liệt kê file trên SFTP*): thêm thư mục của IF mới vào `DEFAULT_FOLDER_CSV`/`DEFAULT_FILE_NAME_METADATA`;
     - `src/layers/common/nodejs/variables/constants.ts` (*layer hằng số dùng chung cho mọi Lambda*): thêm định nghĩa cột `LIST_COL_*`; kèm interface dữ liệu mới trong `src/layers/common/nodejs/interfaces/` (*mẫu: `IDataIF2016.ts`*);
     - `src/statemachine/batch_run_sequentially.asl.json` (*file định nghĩa luồng Step Functions*): thêm 1 nhánh forward (khối Map — *nhánh chạy song song*);
     - Lambda handler mới `src/functions/batch-ifXXXX-import-*/` — làm theo mẫu `batch-if2016-import-service-point-no/` (*handler của IF2016 供給地点/điểm cung cấp — đơn giản nhất: chỉ Put ghi thẳng DynamoDB, không logic phụ*).
     - *Vì sao*: nhịp 5 phút của hệ cũ chỉ là "gần real-time" trên kiến trúc cron cũ, nghiệp vụ hủy hợp đồng không cần nhanh vậy; đi chung luồng sẵn có thì được thừa hưởng miễn phí cơ chế chống-tải-trùng (`CsvDownloadHistory`), chống chạy chồng và chia gói 50 000 dòng.
  3. Logic "dừng tính": implement thành **hậu xử lý ④** sau import — Lambda mới đặt cạnh 3 hậu xử lý hiện có (`batch-send-contents-to-updated-user/`, `batch-update-selecting-place-no/`, `batch-remove-integration-expired/` — đều trong `src/functions/`), bật cờ trên bản ghi hộ tương ứng.
     - *Vì sao*: 3 hậu xử lý hiện có chính là "chỗ chuẩn" của e-smart cho việc *áp nghiệp vụ phái sinh sau khi import xong* — đặt vào đúng chỗ giữ kiến trúc nhất quán. Nhịp 0–7h mỗi-giờ đủ cho nghiệp vụ giải ước (*推定* — xác nhận với phía nghiệp vụ khi chốt IF-01 (*kênh Xzilla mới ở bước 1*)).
  4. Kiểm thử: dựng CSV giả có/không PE624/625 (*mã 契約種別 — loại hợp đồng điện mà batch cũ lọc làm đối tượng*); xác nhận cờ dừng tính phản ánh vào phần tính 買電売電 của #7 (batch điện 30 phút).
     - *Vì sao*: 2 rủi ro thật của batch này là "lọc sai loại hợp đồng" và "cờ không truyền tới #7" — bộ test phải chọc đúng 2 điểm đó.

### 3.3 #6 `RcvEmsPlsCntrPayerCommand` — nhận master 支払者 (IF2264)

**Mục đích của batch**: duy trì trong EMINEL bản sao luôn-khớp của master 支払者 (*danh sách "ai trả tiền cho hợp đồng nào"*) lấy từ 基幹, và áp phán định 契約終了 (kết thúc hợp đồng) để cập nhật số liên kết + cờ dừng tính — bảo đảm số liệu điện gắn đúng người, đúng hợp đồng, và hợp đồng đã kết thúc thì không bị xử lý tiếp.

**Phán định** (*推定*): **BỎ BATCH — GIỮ DỮ LIỆU VÀ TRI THỨC NGHIỆP VỤ.**

- Cái bị bỏ là cách làm cũ "cứ 5 phút xóa toàn bộ bảng rồi nạp lại" (điển hình 「いけてない」).
- Dữ liệu người trả tiền thì E-GW vẫn cần (phục vụ グルーピング — *tính năng gộp nhóm hộ gia đình, 必須 2026*), nhưng sẽ nhận qua 3 kênh mà e-smart ĐÃ nhận sẵn mỗi ngày: IF2023 (使用契約 — hợp đồng sử dụng), IF2024 (顧客 — khách hàng), DM1040 (danh sách hợp đồng — đã lọc sẵn vai trò 支払者); chỉ mở rộng thêm trường theo IF-01 nếu thiếu (bước 2).
- Tri thức 契約終了判定 3 điều kiện được trích ra giữ thành spec (bước 1).
- Nhịp cập nhật theo cửa sổ import sẵn có (0–7h mỗi giờ) — master 支払者 biến động chậm nên đủ dùng (*推定* — xác nhận cùng lúc chốt IF-01, như #5).

*Vì sao đề xuất vậy* (tóm từ dữ kiện bên dưới):

- e-smart **không có IF2264** (grep 0 hit — §3.1) nhưng **đã nhận sẵn mỗi ngày** dữ liệu hợp đồng/khách hàng qua IF2023/IF2024/DM1040 — DM1040 còn lọc sẵn vai trò 支払者.
- Kiểu "5 phút xóa toàn bộ nạp lại" (từng ngốn memory_limit 4096M) là điển hình 「いけてない」 mà phương châm camp Day3 (§2) chủ trương làm lại.
- E-GW không có yêu cầu "payer" riêng — nhu cầu thật là dữ liệu phục vụ グルーピング (必須 2026), 3 kênh sẵn có đáp ứng được (mở rộng theo IF-01 nếu thiếu).
- Tri thức 契約終了判定 3 điều kiện hiện CHỈ nằm trong comment code sắp bỏ → phải trích ra giữ, không thì mất theo code.

**Hệ cũ** (確実) — luồng:

```
[cron */5 phút] ──▶ RcvEmsPlsCntrPayerCommand.php   (memory_limit 4096M — :63)
    │ ① DELETE toàn bộ ipf_ems_pls_cntr_payers (:170-177)
    │ ② nạp lại từ CSV — chỉ 契約種別 PE624/625/650/651/652・PG077/079 (:319-329)
    ▼
    ③ áp 契約終了判定 3 điều kiện (spec trong comment :373-385)
    ▼
[PostgreSQL] cập nhật t_101 (số liên kết + cờ dừng tính)
```

Trích code then chốt (khâu ③ — chính là "1 trang spec" mà bước 1 nói tới, nguyên văn comment trong code cũ) — 🔍 `RcvEmsPlsCntrPayerCommand.php:373-385`:

```php
/*
 * ＜契約終了判定の仕様について＞
 * 契約終了を判定するポイントは以下の３つ
 * 　① サービスポイント＿適用終了年月日が99991231以外
 * 　② 契約終了年月日が99991231以外
 * 　③ 契約種別が電気（PE624またはPE625）の場合に供給地点特定番号またはIPF使用契約番号がNULL
 * ...
 */
```

(`99991231` = ngày 9999-12-31, trị quy ước "chưa có ngày kết thúc"; đoạn diễn giải cách gộp nhóm hợp đồng và cách cập nhật khi thỏa/không thỏa — dòng 380–384 — lược bằng `...`.)

Chi tiết hệ cũ:

- Mỗi 5 phút; **xóa toàn bộ bảng `ipf_ems_pls_cntr_payers` rồi nạp lại từ CSV — nhưng chỉ nạp các dòng thuộc 契約種別 đối tượng: PE624/625/650/651/652・PG077/079** (điều kiện loại trừ dòng 319–329; memory_limit 4096M — dòng 63).
- Áp **契約終了判定 3 điều kiện** (spec nằm trong comment code, dòng 373–385 — trích trên) để cập nhật số liên kết + cờ dừng tính trên `t_101`.
- 🔍 `RcvEmsPlsCntrPayerCommand.php:63, 170-177, 245-363, 371-626` ・ cron dòng 105–106

**E-GW**: không có chức năng "payer" riêng trong toàn bộ docs/eminel (đã grep); phạm trù gần nhất là F-ES-10 (Xzilla連携) phần 顧客情報・契約情報取得; グルーピング (必須 2026) cần 建物種別 (ghi rõ lấy từ Xzilla — dòng 619) + 料金メニュー/アンペア数 từ thông tin hợp đồng. 🔍 `00_integrated_requirements_v1.2.md:415, 619, 692-696`

**Luồng mới đề xuất** (hiện thực của phán định trên):

```
IF2023/IF2024/DM1040 (đang chạy hằng ngày) ──▶ [DynamoDB] TABLE_KAIIN・TABLE_IF2023_USE_CNTR_INFO・TABLE_IF2024_CUSTOMER_INFO
        │  + mở rộng trường theo IF-01 (nếu thiếu 4 trường payer)
        ▼
   hậu xử lý mới: áp spec 契約終了判定 (trích ở bước 1)
```

**Cách làm từng bước**:
  1. **Trích 契約終了判定 3 điều kiện** (*quy tắc nghiệp vụ: khi nào một hợp đồng bị coi là kết thúc*) từ comment trong code cũ thành 1 trang spec — nguồn: `RcvEmsPlsCntrPayerCommand.php:373-385` (*repo `legacy_eminel_docs`, tầng Command của CakePHP — nơi chứa code batch hệ cũ*). Làm ngay được, không chờ IF-01 (*kênh liên kết E-GW⇔Xzilla mới, nội dung đang treo ở CLD-07*).
     - *Vì sao*: spec này hiện CHỈ tồn tại dưới dạng comment trong code sắp bị bỏ — không trích ra thì tri thức nghiệp vụ mất theo code; và đây là việc duy nhất của #6 không phụ thuộc IF-01.
  2. Khi IF-01 (*kênh Xzilla mới nói trên*) định hình: đối chiếu 4 trường người-trả-tiền hệ cũ dùng (供給地点特定番号, IPF使用契約番号, 受電地点特定番号, お客様番号) với dữ liệu 3 kênh e-smart đã nhận sẵn: IF2023 (*使用契約 — handler `src/functions/batch-if2023-import-contract-info/`*), IF2024 (*顧客 — `src/functions/batch-if2024-import-user-info/`*), DM1040 (*danh sách hợp đồng — `src/functions/batch-dm1040-import-user-contract-list/`; phần lọc vai trò 支払者 nằm ở bước tiền xử lý `batch-dm1040-import-user-contract-list-preprocessing/app.ts:54, 63`*). Thiếu trường nào thì yêu cầu bổ sung vào IF-01; KHÔNG xin nguyên một kênh payer riêng nếu không cần.
     - *Vì sao*: nếu 4 trường đã nằm sẵn trong 3 kênh trên thì khỏi phải đàm phán thêm một IF mới với 北ガス — thu hẹp tối đa phạm vi phải chốt của IF-01.
  3. Implement phần thiếu như MỞ RỘNG handler import hợp đồng hiện có: thêm cột trong `src/layers/common/nodejs/variables/constants.ts` (*layer hằng số dùng chung*) + interface tương ứng trong `src/layers/common/nodejs/interfaces/` + xử lý trong handler; áp spec 契約終了判定 (trích ở bước 1) làm hậu xử lý sau import.
     - *Vì sao*: mở rộng luồng sẵn có thì dữ liệu cập nhật theo từng chuyến file, tránh lặp lại kiểu "xóa toàn bộ nạp lại" từng ngốn memory_limit 4096M của hệ cũ.
  4. Kiểm thử: 契約終了判定 3 điều kiện × (thỏa/không thỏa) trên dữ liệu giả; so kết quả cờ/số liên kết với chạy tay logic hệ cũ.
     - *Vì sao*: 契約終了判定 là logic phái sinh phức tạp nhất của batch này — chỉ đối chiếu với kết quả chạy logic cũ mới chứng minh được bản spec trích ra không làm méo nghiệp vụ.

### 3.4 #7 `RcvHalfHourElectricPowerCommand` — nhận 電力30分値 (IF1156)

**Mục đích của batch**: đưa số liệu điện 30 phút (công tơ thông minh đo, 基幹/Xzilla cung cấp) vào EMINEL rồi tính 買電/売電 (điện mua/bán) theo giờ cho từng hộ — đây là **nguồn số liệu** nuôi biểu đồ/レポート năng lượng mà người dùng nhìn thấy trên app; vì vậy đây là batch quan trọng và nặng nghiệp vụ nhất nhóm.

**Phán định** (確実 — yêu cầu minh văn + e-smart chắc chắn không có, nên đề xuất này gần như tất định): **tạo mới** — batch nặng nghiệp vụ nhất trong toàn bộ 11 batch.

*Vì sao đề xuất vậy* (tóm từ dữ kiện bên dưới):

- E-GW yêu cầu **minh văn, scope 2026**: 「電力30分値はCルート（Xzilla経由）で取得する」 — không thể bỏ.
- e-smart **hoàn toàn không có** đường Xzilla cho 30分値 (grep 0 hit — §3.1); điện/gas của e-smart hiện đi TagTag API — không có sẵn thứ để dùng lại nguyên khối.
- Code cũ PHP/CakePHP không chạy trên stack Lambda/TypeScript → tạo mới theo pattern import e-smart (§3.1), chỉ kế thừa **logic nghiệp vụ** từ code cũ.

**Hệ cũ** (確実) — luồng:

```
[cron */10 phút] ──▶ RcvHalfHourElectricPowerCommand.php
    │ ① 速報値: xóa-nạp lại emn_all / emn_fast_electric_powers (:449-583)
    │ ② 確報値 (fixed_div=1): ghi bổ sung emn_confirm_electric_powers (:591-725)
    ▼
    ③ gộp 2×30分 → 1時間値; rẽ nhánh theo cấu hình nhà (太陽光/コージェネ/受電地点特定番号 — :875-893)
    ▼
[PostgreSQL] kết quả giờ ──▶ s_102 ──▶ đồ thị / report
```

Trích code then chốt (khâu ③ — điều kiện rẽ nhánh tính 売電) — 🔍 `RcvHalfHourElectricPowerCommand.php:875-882`:

```php
// 【売電量算出条件①】GWからの計測データによる売電量算出条件
$calcFromGw = $record['has_solar_cell'] == 1;      // nhà có 太陽光 → 売電 tính từ số liệu GW
// 【売電量算出条件②】Xzillaからの30分電力量データによる売電量算出条件
$calcFromXzilla = (
    $record['has_solar_cell'] != 1 &&
    $record['gas_cogeneration'] == 1 &&            // nhà コージェネ (đồng phát)
    !empty($record['juden_point_number'])          // và có 受電地点特定番号
);
```

Chi tiết hệ cũ:

- Mỗi 10 phút. **速報値**: xóa-nạp-lại toàn bộ `emn_all`/`emn_fast_electric_powers`. **確報値** (fixed_div=1): **ghi bổ sung (append) vào `emn_confirm_electric_powers` — bảng tích lũy, không xóa-nạp lại**.
- Rồi **tính 買電・売電**: gộp cặp 30 phút → giá trị giờ, ghi `s_102`.
- Điều kiện rẽ nhánh (trích trên): nhà có 太陽光 (điện mặt trời) → 売電 tính từ số liệu GW (do batch tích lũy theo ngày đảm nhận — ngoài nhóm này), nhà コージェネ (đồng phát) có 受電地点特定番号 → tính từ số liệu Xzilla.
- 🔍 `RcvHalfHourElectricPowerCommand.php:107-122, 192-233, 449-583, 591-725, 734-1050` (điều kiện rẽ nhánh 875–893) ・ cron dòng 109–110

**e-smart**: **không có** (確実) — grep 0 hit (§3.1); dữ liệu sử dụng điện/gas của e-smart lấy qua **TagTag API** (`eminel_gw_project/docs/eminel-smart/02_product_overview.md:119`).

**E-GW**: **cần, minh văn, 2026**: 「電力30分値はCルート（Xzilla経由）で取得する」 (統合要件 mục 3-2); F-ES-10 định nghĩa lấy 速報値・確報値; nuôi グラフ (F-ES-01), グルーピング・レポート (必須). Hàng 「連携テスト(Xzilla/TagTag)」 trong 機能一覧 không ✅ = giữ trong 今期. 🔍 `00_integrated_requirements_v1.2.md:84, 692-696` ・ `10_feature_list.md:148`

**Luồng mới đề xuất** (số bước khớp mục "Cách làm từng bước" bên dưới):

```
IF-01 30分値 (format/nhịp/認証 — bước 1) ──▶ SFTP→S3→handler mới (bước 2; lịch ScheduleV2 riêng nếu nhịp cao)
        ▼
[DynamoDB] bảng 速報 (ghi đè) / bảng 確報 (tích lũy) — template-dynamodb.yaml (bước 3)
        ▼
   Lambda tính: gộp 2×30分→1時間 + bảng điều kiện 買電/売電 map theo 9 pattern lắp đặt (bước 4) + cờ dừng tính từ #5
        ▼
   nhóm batch 集計 (グラフ/グルーピング/レポート)
```

**Cách làm từng bước**:
  1. Chốt IF-01 (*kênh liên kết E-GW⇔Xzilla mới — dòng 1 bảng IF一覧 của 統合要件 v1.2 §4-1, đi qua 北ガスクラウド*) cho phần 30分値: format file, nhịp cấp (hệ cũ: 10 phút/lượt), cách 認証/xác thực (*thuộc CLD-07 — vấn đề mở về định nghĩa vào/ra + xác thực của chính IF-01*).
     - *Vì sao*: toàn bộ thiết kế bước 2–3 đổ theo 3 tham số này; riêng nhịp cấp là điểm gắt nhất — e-smart hiện chỉ quen cửa sổ 0–7h nên "gần real-time" là yêu cầu mới, phải được 北ガス đồng ý cung cấp.
  2. Dựng đường nhận theo pattern §3.1: `src/functions/batch-get-list-file-name-from-sftp-server/` (*liệt kê file trên SFTP*) → `src/functions/batch-forward-csv-from-sftp-server-to-s3/` (*chuyển file lên S3, chia gói 50 000 dòng*) → handler import mới (*tạo mới trong `src/functions/`*). Nếu nhịp dày hơn cửa sổ 0–7h → khai lịch riêng `ScheduleV2` (*lịch tĩnh của EventBridge Scheduler*) trong `template.yaml` (*file khai báo hạ tầng AWS SAM — nơi 3 lịch tĩnh hiện hữu được khai, xem §2*), KHÔNG nhét vào `BatchRunSequentially` (*state machine nhập dữ liệu 基幹 chạy mỗi giờ 0–7h*).
     - *Vì sao*: `BatchRunSequentially` chạy tuần tự có khóa chống-chạy-chồng — nhét thêm luồng nhịp cao vào sẽ nghẽn cả chuỗi 8 IF hiện hữu; lịch riêng còn giúp cô lập sự cố.
  3. Thiết kế bảng DynamoDB mới (*khai trong `template-dynamodb.yaml` — file định nghĩa các bảng*): tách 速報値 (*giá trị sơ bộ — đổ đè liên tục*) / 確報値 (*giá trị chốt — ghi bổ sung, tích lũy*) — vai trò tương đương cặp bảng `emn_fast`/`emn_confirm_electric_powers` hệ cũ; cân nhắc TTL (*bản ghi tự xóa khi quá hạn*) cho dữ liệu thô theo 保持期間/kỳ hạn lưu (*SVC-03 — vấn đề mở: chính sách lưu trữ + backup của hệ mới chưa được định nghĩa*).
     - *Vì sao*: 速報 bị ghi đè liên tục còn 確報 phải giữ nguyên vẹn làm căn cứ chốt số liệu — hai tính chất ngược nhau, trộn một bảng sẽ hoặc mất lịch sử 確報 hoặc phình vô hạn; hệ cũ cũng tách 2 bảng vì đúng lý do này (速報 `:449-583` / 確報 `:591-725`).
  4. Kế thừa **logic nghiệp vụ** (KHÔNG port code PHP): quy tắc gộp 2×30分 → 1時間値; bảng điều kiện tính 買電/売電 theo cấu hình nhà (太陽光/コージェネ/受電地点特定番号 — nguồn: `RcvHalfHourElectricPowerCommand.php:875-893`) — **map lại theo 9 pattern lắp đặt của E-GW** (*9 kiểu tổ hợp thiết bị lắp trong nhà — định nghĩa ở 統合要件 v1.2 mục 3-5*; cấu hình mới có thể phải thêm nhánh).
     - *Vì sao*: code PHP/CakePHP không chạy được trên stack Lambda/TypeScript, nhưng các điều kiện rẽ nhánh là nghiệp vụ đã vận hành thương mại nhiều năm — giữ nghiệp vụ, bỏ hiện thực; phải map lại vì tổ hợp thiết bị của E-GW không trùng hệ cũ.
  5. Nối đầu ra vào nhóm batch 集計 (*nhóm batch tính toán tổng hợp cho グラフ/グルーピング/レポート — nhóm khác, ngoài phạm vi bộ báo cáo 11 batch*) + áp cờ dừng tính từ #5 (§3.2).
     - *Vì sao*: #7 chỉ là "cửa nhập nguyên liệu" — giá trị phát sinh khi nhóm 集計 tiêu thụ được đầu ra; và cờ #5 phải áp ngay tại bước tính để khách đã hủy hợp đồng không bị tính tiếp.
  6. Kiểm thử: bộ dữ liệu 30分値 giả phủ đủ các nhánh (太陽光/コージェネ/thường, 速報→確報 ghi đè, thiếu cặp 30 phút) — đối chiếu kết quả giờ với chạy tay logic hệ cũ trên cùng input.
     - *Vì sao*: các nhánh theo cấu hình nhà là phần phức tạp nhất của code cũ (`:734-1050`) — sót nhánh nào là sai số liệu của đúng nhóm khách dùng cấu hình đó.

---

## 4. Việc cần xác nhận tiếp

| # | Việc | Liên quan | Hành động phía SYP / kênh |
|---|---|---|---|
| 1 | Định nghĩa 入出力 (dữ liệu vào/ra) + 認証 (cách xác thực) của IF-01 (*kênh liên kết E-GW⇔Xzilla mới*) — tức chốt vấn đề mở CLD-07; gồm cả **chiều xuất** (「EMINELデータの共有」 — E-GW gửi dữ liệu ngược về 基幹) | Cả 3 batch của tập này đều phụ thuộc: #5 (nhận hủy hợp đồng), #6 (master người trả tiền), #7 (điện 30 phút) — chi tiết §3 | Chờ 北ガス trả lời qua PM mui; trong lúc chờ, SYP soạn sẵn danh mục trường cần thiết rút từ code cũ (= §3.3 bước 1: trích spec 契約終了判定, + chuẩn bị bảng đối chiếu 4 trường payer cho bước 2) |
| 2 | **Xác nhận đích của thư mục SFTP `/EST`** — nơi e-smart đang đẩy 6 loại CSV thiết bị mỗi ngày 8:00 — có phải Xzilla/DWH (kho dữ liệu phân tích) không; địa chỉ kết nối nằm trong secret nên không tự đọc được từ repo | Chiều xuất e-smart→基幹 mô tả ở §3.1; đây cũng chính là "việc cần làm ngay" số 1 của §1 | SYP hỏi mui (kênh QAデータベース Notion, hoặc khi nhận spec HEMS-SV) |
| 3 | Góp danh sách 「既存システムを使い続けたほうがいい機能」 (các chức năng nên dùng tiếp của hệ hiện hữu) vào câu trả lời QA 独立デプロイ — trả lời gồm 2 vế: ① hệ cũ 旧EMINEL: không có batch nào đáng dùng tiếp nguyên trạng ・ ② e-smart: 4 ứng viên (chung cho cả 3 tập). Ứng viên từ nhóm này: **luồng nhận Xzilla SFTP→S3→DynamoDB** | = "việc cần làm ngay" số 3 của §1 | SYP trả lời trực tiếp trên trang QAデータベース Notion |

## 5. Nguồn chính đã dùng

- **`legacy_eminel_docs`** (@`ccd8f56`): `docs/03_API仕様/04_バッチ一覧.md`; code 3 command trong `sources/conciergesv-develop/src/Command/` (`RcvCntctCancellationCommand.php`, `RcvEmsPlsCntrPayerCommand.php`, `RcvHalfHourElectricPowerCommand.php`); cron: `docs/02_詳細設計/10_バッチ処理/*.txt`
- **`eminel_gw_project`** (@`fbc0af0`; điều tra tại `788b438` — các file nhóm này trích giống nhau ở cả 2 commit): `docs/eminel/`: 統合要件 v1.2 (mục 3-2, F-ES-01/10), `1_product/10_feature_list.md`, `1_product/11_business_process/readme.md`, `2_management/22_decisions.md` (quyết định 6/10), `2_management/20_open_issues.md` (CLD-07, SVC-03), camp day3 minutes; `docs/eminel-smart/` (tài liệu khảo sát ESTA — 6 file; ⚠️ các điểm lệch code: mục Giới hạn #2)
- **`syp-eminelstandard-backend`** (@`dc39aa39`, branch `gw-syp-dev`): `template*.yaml`, `src/functions/**`, `src/layers/common/nodejs/**`, `src/statemachine/*.asl.json`
- **`syp-eminelstandard-web-admin`** (@`e550326`, branch `gw-syp-dev`): chỉ dùng kiểm "chưa có commit E-GW" (`git log`)
- **QAデータベース Notion** (trạng thái 回答中, tham chiếu 2026-08-04 — mở trang gốc kiểm tra trước khi trích lại): 「旧Eminel基盤継承＋EMINEL-smartサーバーは独立デプロイの確認」 (swan (mui)) ・ 「旧EMINEL調査範囲（conciergesv/eminelsv）とhemssv対象外の確認」 (swan (mui)) ・ 「管理画面は独立か共通か（切替モード追加）の確認」 (masao takahashi (mui))
