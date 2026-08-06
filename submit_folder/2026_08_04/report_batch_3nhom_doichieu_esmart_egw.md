# Báo cáo phán định 11 batch hệ cũ (3 nhóm) — đối chiếu e-smart & yêu cầu E-GW

> 🔰 **Người mới vào dự án**: bảng ngay dưới đây là thông tin quản lý tài liệu — đọc **mục 0** bên dưới bảng trước, rồi hãy quay lại.

| | |
|---|---|
| Ngày lập | 2026-08-04 |
| Người lập | Bui Trong Dat (SYP) + AI hỗ trợ điều tra |
| Nhiệm vụ | Xét 3 nhóm batch trong `legacy_eminel_docs/docs/03_API仕様/04_バッチ一覧.md` — **配信・通知系**, **外部連携・受信系（Xzilla取込）**, **CSV/ZIPエクスポート系** (11 batch, đều thuộc server `conciergesv` của hệ cũ) — cái nào **đã có sẵn trong e-smart** (kèm trích code), cái nào phải **tạo mới**, cái nào **bỏ** (kèm các bước làm), căn cứ yêu cầu E-GW trong `eminel_gw_project/docs/eminel` |
| Repo đối chiếu | `legacy_eminel_docs` @ `ccd8f56` ・ `eminel_gw_project` @ `788b438` ・ `syp-eminelstandard-backend` @ `dc39aa39` (branch `gw-syp-dev`) ・ `syp-eminelstandard-web-admin` @ `e550326` (branch `gw-syp-dev`) ・ `syp-eminelstandard-app-syp-dev` (snapshot, không có git) — tất cả trong thư mục `sources/`, các repo git đều = origin tại thời điểm điều tra |

## 0. Tài liệu này là gì? (đọc trước nếu bạn mới vào dự án)

**Bối cảnh một đoạn**: **E-GW (EMINEL Gateway)** là dự án làm hai việc cho dịch vụ EMINEL (khách hàng cuối: 北海道ガス／北ガス): **(1)** thay gateway — *gateway* (viết tắt **GW**) là chiếc hộp đặt trong nhà khách, trung chuyển dữ liệu giữa cảm biến/máy sưởi và server; hộp hiện tại của hãng Maxell sẽ được thay bằng gateway do mui Lab làm; **(2)** **chuyển phần máy chủ sang nền tảng e-smart** — hệ đang chạy thương mại của 北ガス (tên khác: **ESTA**, **EMINEL-Smart** — một hệ, ba tên). Hệ EMINEL **cũ** có vài chục "batch" chạy nền; khi làm server mới trên nền e-smart, phải trả lời: batch nào **e-smart đã có thứ tương đương** (đỡ làm — nhưng không phải 0 công, xem tiền đề §2), batch nào **phải làm mới**, batch nào **không cần nữa**.

📖 **"Batch" là gì?** Chương trình không có giao diện, hệ thống **tự chạy theo lịch** (như hẹn giờ) hoặc theo sự kiện: tính toán số liệu, gửi thông báo hàng loạt, nhận/xuất file dữ liệu… Người dùng không nhìn thấy batch, nhưng biểu đồ có số liệu, điện thoại có thông báo — là nhờ chúng.

**File này sinh ra để làm gì**: trả lời câu hỏi trên cho **11 batch thuộc 3 nhóm được giao điều tra**:

- **配信・通知系** (*phát nội dung & thông báo*): cấp điểm thưởng, phát lời khuyên tiết kiệm năng lượng, gửi push (thông báo đẩy tới điện thoại), điều khiển DR (xem Chú giải nhanh bên dưới);
- **外部連携・受信系（Xzilla取込）** (*nhận dữ liệu từ bên ngoài*): nhận file từ **Xzilla** — hệ **基幹** (hệ thống nghiệp vụ lõi quản lý khách hàng/hợp đồng) của 北ガス: thông tin hủy hợp đồng, người trả tiền, điện lực 30 phút;
- **CSV/ZIPエクスポート系** (*xuất dữ liệu ra file CSV/ZIP*).

Mỗi batch được phán định: **dùng lại của e-smart / tạo mới / bỏ**. Chỗ nào nói "e-smart đã có" thì **dán trích đoạn code thật và giải thích từng nhóm code**; chỗ nào "tạo mới/bỏ" thì ghi **các bước làm cụ thể**.

**Cách đọc**:
- Vội → đọc **§1** (3 bảng tóm tắt theo nhóm — kết quả cho đủ 11 batch, mỗi batch một dòng + việc cần làm ngay).
- Muốn hiểu căn cứ → **§2** (tiền đề chung + "nền batch của e-smart" kèm code) rồi **§3–§5** (chi tiết từng batch, theo 5 khối: *hệ cũ đang làm gì → e-smart có sẵn không (kèm code) → E-GW yêu cầu gì → phán định → cách làm từng bước*; vài mục gộp khối khi nội dung chung cho cả nhóm — riêng nhóm CSV/ZIP §5 viết gộp toàn bộ, khác biệt từng batch xem bảng 1.3).
- Muốn biết việc gì còn treo, ai làm gì tiếp → **§6**. Tra nguồn → **§7**. Định **trích dẫn lại** nội dung nào → đọc mục **⚠️ Giới hạn** (ngay dưới đây) trước.

**Chú giải nhanh** (thuật ngữ dùng xuyên suốt — đọc lướt một lần):

- **e-smart = ESTA = EMINEL-Smart**: một hệ, ba tên; tên trong code là ESTA. Gồm 3 repo: `backend` (TypeScript trên AWS), `web-admin` (màn hình quản trị, Nuxt 3), `app` (Flutter).
- **Hệ cũ (旧EMINEL)** gồm 3 khối server (đều CakePHP/PostgreSQL): **`conciergesv`** — API cho app + toàn bộ batch nghiệp vụ (cả 11 batch của báo cáo này); **`eminelsv`** — màn hình quản trị vận hành; **`hemssv`** — giao tiếp với gateway. ⚠️ Đừng nhầm `hemssv` (hệ cũ) với **HEMS-SV (m2-cloud)** — thành phần MỚI do mui phát triển cho E-GW, chỉ trùng tên.
- **Stack AWS của e-smart** (gặp nhiều ở phần dẫn chứng code): **Lambda** = hàm chạy theo sự kiện, không có server thường trực; **DynamoDB** = database NoSQL; **Step Functions** = xâu nhiều Lambda thành luồng nhiều bước, mỗi luồng gọi là *state machine*; **EventBridge Scheduler** = bộ hẹn giờ kích hoạt batch; **S3** = kho file; **SFTP** = giao thức chép file mã hóa qua SSH. Hạ tầng khai báo trong `template*.yaml` (AWS SAM).
- **FCM** (Firebase Cloud Messaging) = dịch vụ của Google chuyên đẩy thông báo tới app điện thoại; muốn gửi phải có **token** — "địa chỉ nhận thông báo" riêng của từng máy, server lưu trong bảng token.
- **IF** = "kênh trao đổi file" được định nghĩa và đánh mã số giữa hai hệ thống (vd IF2249 = file thông tin hủy hợp đồng do Xzilla gửi sang; DM1040 = file danh sách hợp đồng). "E-smart không có IF này" = không có kênh nhận loại file đó. **IF-01** = bản định nghĩa kênh liên kết MỚI giữa E-GW và Xzilla — nội dung vào/ra chưa chốt (chính là điểm treo **CLD-07**). **T.B.D** = chưa quyết định.
- **port** = bê nguyên code hệ cũ sang chạy trên hệ mới; "không bê nguyên (port)" = bỏ code, chỉ giữ lại tri thức nghiệp vụ.
- **DR** = デマンドレスポンス (Demand Response) — bên bán năng lượng yêu cầu hộ gia đình tạm giảm/dịch giờ dùng điện lúc cao điểm (thường đổi lấy điểm thưởng); "điều khiển DR" = server tự điều chỉnh thiết bị trong nhà theo yêu cầu đó.
- **PI連携** = liên kết **PointInfinity** — hệ điểm thưởng của 北ガス. **TagTag** = nền tảng hội viên của 北ガス (cấp định danh + API dữ liệu sử dụng gas/điện).
- **劣後** = được lùi lại sau (sang 2027/4~) ・ **必須** = bắt buộc trong scope 2026 ・ **速報値/確報値** = giá trị sơ bộ/giá trị chốt ・ **買電/売電** = điện mua vào/bán ra ・ **回答中** = trạng thái QA đang trả lời, chưa chốt.
- **Mã tham chiếu tài liệu**: `F-ES-xx`/`F-AD-xx`/`F-GW-xx` = mã chức năng trong 統合要件定義書 v1.2 (ES = server, AD = màn hình quản trị, GW = gateway) ・ `A03/B05/C05/D03…` = mã section bộ yêu cầu app E-GW (`3_requirements/app/`) ・ `CLD-xx/SVC-xx/GW-xx` = mã vấn đề đang mở trong `20_open_issues.md` ・ **[G] [I]** = file spec màn hình quản trị (`4_spec/admin/G_energy_advice.md`, `I_data_download.md`), `G-A-02`… = mã mục trong đó.
- Quy ước bảng 機能一覧 (`10_feature_list.md`): cột 劣後 đánh **✅ = lùi được sang 2027** (KHÔNG phải "trong scope"), ô trống = 今期必須.
- **cron** = bộ hẹn giờ chuẩn của server Linux; mỗi "dòng cron" khai báo một lịch chạy. Biểu thức dạng `cron(phút giờ ngày tháng ? năm)` — diễn giải tại chỗ khi xuất hiện.
- **Bảng QA gửi khách** = `requirements/qa_kitagas.md` trong workspace onboarding; "câu 2 / câu 5 / câu Dự phòng 1" = số câu trong bảng đó. Phân biệt với **QAデータベース Notion** = kênh hỏi–đáp nội bộ với mui (liệt kê ở §7).
- **Nhãn độ chắc** trong báo cáo: **確実** = tự kiểm chứng được trên tài liệu/code (với các khẳng định về e-smart: đã soi trực tiếp code backend/web-admin); ***推定*** = suy đoán có căn cứ, chưa kiểm chứng — không dùng làm quyết định cuối. Dẫn chứng viết sau ký hiệu 🔍, đường dẫn tính từ `sources/`. Trong văn xuôi, chỗ rút gọn ghi `…`; **trong khối code, các dòng/chỗ chỉ có `...` là ký hiệu lược bớt của báo cáo, không phải code** (comment tiếng Việt trong khối cũng là chú thích của báo cáo thêm vào). Căn cứ hay gặp: "**grep X: 0 hit**" = tìm chuỗi X trong toàn bộ code không ra kết quả nào — cơ sở để khẳng định "không tồn tại trong code".

## ⚠️ Giới hạn & lưu ý xác thực (đọc trước khi trích dẫn lại)

1. Các khẳng định "e-smart có/không có X" đều đã **kiểm chứng trực tiếp trên code** `syp-eminelstandard-backend` + `syp-eminelstandard-web-admin` (branch `gw-syp-dev`). Repo app chỉ là snapshot không có git — số dòng phía app có thể trôi khi có bản mới.
2. ⚠️ Trước báo cáo này, dự án đã có bộ **tài liệu khảo sát ESTA** (`eminel_gw_project/docs/eminel-smart/`, 6 file — do mui lập khi khảo sát nền tảng e-smart). Lần này đối chiếu với code phát hiện **5 chỗ tài liệu đó ghi lệch với code thực tế** — liệt kê để ai trích tài liệu khảo sát biết chỗ phải kiểm code trước:
   | Tài liệu khảo sát ghi | Code thực tế |
   |---|---|
   | Push 「最大500件/バッチ」 (`02_product_overview.md:121`) | Không có số 500; chia người nhận thành lô 10 000 user, gửi song song tối đa 100 lệnh/lúc (§3.3) |
   | Import 基幹 「日次・深夜〜早朝」 (`02_product_overview.md:30, 63-64`) | `cron(5 0-7 * * ? *)` — mỗi giờ một lượt, 0h–7h JST (§2) |
   | Lock hội viên khi merge 「6分」 (`02_product_overview.md:73, 78`) | `UPDATE_LOCK_TTL_MINUTES = 5` (§4) |
   | `CsvDownloadHistory` = 「CSVダウンロード履歴」 gợi ý lịch sử download (`03_backend_models.md:107`) | Là lịch sử **tải file TỪ SFTP về** (chiều nhận, chống tải trùng) — không liên quan admin download (§5) |
   | 「自動化ルール実行（毎分）」 (`02_product_overview.md:85`) | Automation không chạy mỗi phút — mỗi rule có lịch tuần riêng tạo động (§2) |
3. Ba trang QA Notion được trích (xem §7) đang ở trạng thái **回答中** và mới đọc qua ảnh chụp màn hình — trước khi trích lại phải mở trang gốc kiểm tra.
4. Phán định scope dựa trên tài liệu `eminel_gw_project` tại commit `788b438`; các điểm treo (T.B.D/QA) ghi rõ tại chỗ.

---

## 1. Kết luận tổng — tóm tắt từng batch theo nhóm

### 1.1 Nhóm 配信・通知系 (phát nội dung & thông báo) — 4 batch

| # | Batch | Hệ cũ đang làm | e-smart có sẵn? | E-GW cần? | **Đề xuất** | Chi tiết |
|---|---|---|---|---|---|---|
| 1 | `DistributeMonthlyEcoPointsCommand` | Cấp 250 point エコ暖房 hàng tháng cho hộ có nhiệt độ cài đặt TB tháng ≤22℃, gọi PointInfinity | **Một phần** — hạ tầng point/badge + gọi thẳng PointInfinity có trong code; logic phán định từ dữ liệu đo: không có | Cần (F-ES-04/09; 必須 2026 — treo mâu thuẫn 劣後, câu 2 QA) | **Dùng lại hạ tầng point + PI; tạo mới phần logic phán định エコ暖房** | §3.1 ・ 確実 |
| 2 | `PublishRegularEcoMissionsCommand` | Phát 19 loại 省エネアドバイス theo điều kiện phán định, cron cố định theo mùa | **Không** (grep 0 hit) — Tip chỉ là nội dung admin soạn sẵn, không có advice engine | Cần, scope 2026 (F-ES-03 必須) | **Tạo mới** judgment engine + schedule đặt từ admin (spec [G]; chờ chốt gom 15種→7種) | §3.2 ・ 確実 |
| 3 | `DispatchPushMessagesCommand` | Gửi push mỗi phút từ hàng đợi DB, qua server trung gian PushCore | **Có, đầy đủ** — FCM + bảng token + 6 luồng push notice | Cần (Push 2026) | **Bỏ bản cũ, dùng hạ tầng push e-smart**; hệ cũ chỉ để rà danh mục 通知種別 | §3.3 ・ 確実 |
| 4 | `ControlDrOperationCommand` | Mỗi phút ghi lệnh DR (giả dạng thao tác app user) vào DB cho GW poll (GW tự đến lấy) | **Có khung DR khác kiểu** — điều khiển thiết bị nối trực tiếp hãng, không có đường qua GW | Cần nhưng **劣後 → 2027/4以降** | **Không code 2026** *(chỉ chốt "GW có giữ trạng thái DR không" — câu 5 QA)*; 2027 tạo mới trên khung DR e-smart | §3.4 ・ 確実 |

### 1.2 Nhóm 外部連携・受信系（Xzilla取込 — nhận dữ liệu từ hệ 基幹) — 3 batch

| # | Batch | Hệ cũ đang làm | e-smart có sẵn? | E-GW cần? | **Đề xuất** | Chi tiết |
|---|---|---|---|---|---|---|
| 5 | `RcvCntctCancellationCommand` (IF2249) | Mỗi 5 phút nhận CSV 解約 điện, bật cờ dừng tính 買電売電 | **Không có IF này** (grep 0 hit) — nhưng có sẵn luồng nhận SFTP→S3→DynamoDB (8 IF khác) + hậu xử lý hết hạn hợp đồng | **Gián tiếp cần** — cờ dừng tính phục vụ #7 (vô hiệu GW sau 解約 là thao tác thủ công) | **Không bê nguyên (port).** IF-01 có luồng 解約 → gộp vào import 基幹 sẵn có; không có → nêu yêu cầu bổ sung ngay. Chờ CLD-07 chốt | §4.1 ・ đề xuất *推定*, vế e-smart 確実 |
| 6 | `RcvEmsPlsCntrPayerCommand` (IF2264) | Mỗi 5 phút nạp-lại-toàn-bộ master (bảng dữ liệu gốc) 支払者 + áp 契約終了判定 3 điều kiện | **Không có IF này** (grep 0 hit) — đã có import 契約/顧客 master (IF2023/2024/DM1040, DM1040 lọc sẵn vai trò 支払者) | Không nhắc riêng; gián tiếp phục vụ グルーピング (必須 2026) | **Không bê nguyên (port); mở rộng import hợp đồng sẵn có theo IF-01; trích 契約終了判定 thành spec** | §4.2 ・ đề xuất *推定*, vế e-smart 確実 |
| 7 | `RcvHalfHourElectricPowerCommand` (IF1156) | Mỗi 10 phút nhận 電力30分値 (速報/確報), gộp 30分→1時間, tính 買電売電 theo cấu hình nhà | **Không** (grep 0 hit) — điện/gas của e-smart đi TagTag API, không có đường Xzilla | **Cần, minh văn, scope 2026** (「電力30分値はCルート（Xzilla経由）で取得」) | **Tạo mới** theo pattern import e-smart; kế thừa logic nghiệp vụ từ code cũ. Batch nặng nhất | §4.3 ・ 確実 |

### 1.3 Nhóm CSV/ZIPエクスポート系 (xuất file CSV/ZIP) — 4 batch

Cả 4 batch đều là **backup-trước-khi-xóa** — không phải chức năng tải dữ liệu cho người vận hành. **Phán định chung: bỏ cả 4**, thay bằng chính sách giữ dữ liệu (retention) mới + 2 cơ chế xuất sẵn có của e-smart: admin download (17 endpoint + 7 loại) và export định kỳ ra SFTP (§5 ・ 確実). Lý do: yêu cầu E-GW đã **đổi bản chất** ([I]: tải 集計データ từ admin, giữ **24ヶ月** T.B.D — không còn kiểu giữ-ngắn-rồi-xóa), còn e-smart không có cơ chế backup-rồi-xóa. Khác nhau giữa 4 batch chỉ ở dữ liệu và chu kỳ:

| # | Batch | Backup dữ liệu gì (bảng hệ cũ) | Chu kỳ hệ cũ |
|---|---|---|---|
| 8 | `CreateCsvAndZipConDeviceStatusesCommand` | 機器状態 (trạng thái thiết bị — `t_202`), partition đủ 8 ngày tuổi | 05:15 hằng ngày; thứ Hai nén ZIP tuần |
| 9 | `CreateCsvAndZipConSensorHourlyValuesCommand` | 時間値 (giá trị giờ — `s_102`), partition đủ 8 ngày tuổi | 05:15 hằng ngày; thứ Hai nén ZIP tuần |
| 10 | `CreateCsvAndZipConSensorDailyValuesCommand` | 日値 (giá trị ngày — `s_103`), partition tháng trước | 05:15 ngày 1 hằng tháng, nén ZIP luôn |
| 11 | `CreateCsvAndZipConSensorDailyAveValuesCommand` | 日平均値 (bình quân ngày toàn hệ — `s_113`), partition tháng trước — 1 file chung, không chia theo hộ | 05:15 ngày 1 hằng tháng, nén ZIP luôn |

*(partition = ngăn dữ liệu — bảng lớn được chia sẵn thành ngăn theo ngày/tháng, xóa được nguyên ngăn một lần rất nhanh; giải thích kỹ ở §5.)*

**Ba lưu ý đọc kèm bảng**:
- Nhãn **確実/*推定*** (nằm ở cột **Chi tiết** của bảng 1.1/1.2, và ở đoạn dẫn của bảng 1.3) chứng nhận phần **dữ kiện** (hệ cũ làm gì, e-smart có/không, scope) — phần **Đề xuất** luôn là phán đoán để team review; riêng #5/#6 phán đoán dựa suy luận nhiều hơn nên tách nhãn *推定* riêng.
- Báo cáo chỉ phán định *làm gì / dùng lại gì*, **chưa ước lượng công số** — công số sẽ ước khi tách 1 batch = 1 task trên Notion (phương châm §2); riêng #7 là batch nặng nghiệp vụ nhất.
- Ngoài phạm vi 11 batch: e-smart **không tính sẵn report/集計 nào từ trước** (monthly report của app = hỏi tới đâu chuyển tiếp sang TagTag API tới đó, không lưu — 🔍 `syp-eminelstandard-backend/src/functions/api-dashboard/get-monthly-report-of-user.ts:21`) — tức nhóm batch **集計・計算系** của E-GW (nhóm khác của bảng batch, không thuộc báo cáo này) cũng sẽ không có sẵn gì để dùng lại.

**Ba việc rút ra cần làm ngay** (không chờ đủ spec):

1. **Báo mui danh sách "chức năng nên dùng tiếp hệ hiện hữu"** — QA 「旧Eminel基盤継承＋独立デプロイ」 (swan, 回答中) có vế: *"ただし既存システムを使い続けたほうがいい機能があれば教えてほしいです"*. ⚠️ Trước khi trả lời cần xác nhận 「既存システム」 ý chỉ hệ nào; câu trả lời nên tách hai vế: **① của hệ CŨ (旧EMINEL): không có batch nào đáng dùng tiếp nguyên trạng** (kết luận của báo cáo này); **② của hệ ĐANG CHẠY (e-smart): 4 ứng viên** — hạ tầng Push (FCM), hạ tầng point/badge + PI連携, luồng nhận Xzilla SFTP→S3→DynamoDB, cơ chế admin download/export.
2. **Xác nhận đích của luồng export SFTP `/EST`** (§4): e-smart đang đẩy 6 loại CSV thiết bị lên SFTP hằng ngày, nhưng đích có phải Xzilla/DWH (kho dữ liệu phân tích) hay không thì **không tự xác nhận được từ repo** — địa chỉ kết nối nằm trong secret (kho cấu hình mật ngoài code) → phải hỏi mui. Liên quan trực tiếp yêu cầu 「EMINELデータの共有」 của F-ES-10.
3. **Ba điểm treo phải bám**: CLD-07 (định nghĩa 入出力 Xzilla IF-01), CLD-06 (gom advice 15種→7種), mâu thuẫn 必須/劣後 của ポイント (đã hỏi trong bảng QA gửi khách, câu 2).

---

## 2. Tiền đề chung khi phán định

**Phương châm đã chốt nội bộ mui (合宿 Day3, 2026-06-25)**: batch hiện hành 「いけてない」 — **làm lại chứ không bê nguyên** (「バッチ群（約46本…）をNotionに機能単位でタスク化…作り直す前提」), 1 batch = 1 task, đặt バッチボーン (khung rỗng) trước, chạy thật trước 結合フェーズ (*giai đoạn ghép nối chạy chung các thành phần* — mục tiêu trong tháng 9). Mảng batch/外部連携 dự kiến giao SYP. → *"Dùng lại"* trong báo cáo này nghĩa là **dùng cơ chế/hạ tầng/codebase của e-smart**, không phải copy code PHP của hệ cũ.
- 🔍 `eminel_gw_project/docs/eminel/2_management/minutes/20260625_egw_camp_day3.md` dòng 35, 51, 99–103, 147–149

**Tiền đề về nơi chạy** (3 ý):
- QA 「旧Eminel基盤継承＋EMINEL-smartサーバーは独立デプロイの確認」 (swan, 回答中) trả lời tạm: *về cơ bản (基本的には) phát triển theo hướng hệ độc lập*. Vì vậy "dùng lại của e-smart" trong báo cáo = **dùng lại code/cơ chế/pattern**; nếu chốt deploy độc lập thì vẫn phải **dựng lại môi trường chạy** trên hạ tầng mới — "dùng lại" ≠ "0 công".
- Hiện trạng code: cả backend lẫn web-admin đều đã có branch `gw-syp-dev` nhưng **chưa có commit E-GW nào** (web-admin: `git log origin/main..gw-syp-dev` rỗng; backend: 15 commit gần nhất thuần e-smart) — mọi việc E-GW bắt đầu từ 0 trên nhánh này. 🔸 Cách làm nhiều khả năng là *viết thêm vào chính codebase e-smart* — suy từ trả lời QA 「管理画面は独立か共通か」 (chung source, 回答中), chưa phải quyết định thành văn.
- Lưu ý tách bạch: **"chung source" ≠ "chung môi trường chạy"** — hai câu hỏi độc lập, QA mới trả lời tạm cả hai.

**Khoảng cách công nghệ giữa hai thế hệ**:

| | Hệ cũ (`conciergesv`…) | e-smart (`syp-eminelstandard-backend`) |
|---|---|---|
| Ngôn ngữ/khung | PHP 8.0 / CakePHP 4.4 | TypeScript / AWS SAM + Lambda (Node 20) |
| Database | PostgreSQL (partition theo ngày/tháng) | DynamoDB (PITR — backup hạ tầng — bật sẵn) |
| Cách chạy batch | cron trên server (`/etc/cron.d/eminel-mng-webap`), shell + flock chống chạy trùng | Step Functions + EventBridge (xem ngay dưới) |
| Nhận file ngoài | SFTP về đĩa server | SFTP → S3 → DynamoDB |

- 🔍 hệ cũ: `legacy_eminel_docs/docs/02_詳細設計/10_バッチ処理/cron設定概要.txt` dòng 1–37 ・ e-smart: `syp-eminelstandard-backend/template.yaml` (SAM), `02_product_overview.md` dòng 48–53

**Nền batch của e-smart trông thế nào** (điều E-GW sẽ thừa hưởng — mọi đường dẫn dưới đây tính từ `syp-eminelstandard-backend/`):

- **Chỉ có 3 lịch tĩnh** (đều `ScheduleV2`, timezone `Asia/Tokyo` — `template.yaml:9-11`): ① `BatchRunSequentiallyStateMachine` — nhập dữ liệu 基幹, `cron(5 0-7 * * ? *)` = phút :05 **mỗi giờ từ 0h–7h JST** (`template.yaml:853-888`, cron dòng 881–882); ② `BatchMigrationIntegratedDataStateMachine` — lấy dữ liệu thiết bị Rinnai/Noritz + export, `cron(0 8 * * ?)` (`template.yaml:2205-2240`, cron dòng 2233); ③ `BatchGetErrorDeviceInfoOfRinnaiStateMachine` — lỗi thiết bị, cùng 8:00 (`template.yaml:2966-2980`).
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

  Giải thích từng phần: `createSchedule` đăng ký một lịch với EventBridge Scheduler; `ScheduleExpression` là thời điểm phát (build tại `src/layers/common/nodejs/utils/date-utils.ts:117` theo dạng `cron(phút giờ ngày tháng ? năm)` — đúng một lần); `Target.Arn` trỏ tới state machine/Lambda cần chạy kèm `Input`; `ActionAfterCompletion.DELETE` làm lịch tự hủy sau khi chạy. Khi admin tạo news → API đặt lịch phát (`src/functions/api-news/common.ts:207-209`); batch phát xong lại tự đặt tiếp lịch gửi push (`src/functions/batch-send-news-complete/app.ts:72-80`). Automation của user (tính năng user tự đặt quy tắc tự động hóa thiết bị trong app) cũng vậy — mỗi rule một lịch tuần riêng (`src/functions/api-automation/common.ts:115`), không có polling mỗi phút (grep `rate(`: 0 hit — `rate(...)` là cách khai báo lịch lặp "mỗi N phút" của EventBridge, không xuất hiện lần nào).
- 💡 **Hệ quả cho E-GW**: yêu cầu [G] G-A-02 (*admin đặt được 定期配信スケジュール cho advice — điều hệ cũ không làm được vì cron cố định*) có lời giải kỹ thuật **sẵn trong nền e-smart** — chính là pattern one-shot scheduler này.

**Phạm vi SYP**: theo QA 「旧EMINEL調査範囲（conciergesv/eminelsv）とhemssv対象外の確認」 (swan, 回答中) — `conciergesv`/`eminelsv` là đối tượng SYP **điều tra** (đúng việc báo cáo này làm), không phải phạm vi SYP phát triển tiếp trên hệ cũ; giao tiếp GW đi qua HEMS-SV (m2-cloud) do mui làm, spec chia sẻ sau.

**Quyết định scope 2026-06-10** (đã vào 決定ログ): 必須 = 暖房機能/暖房制御/照明アドバイス※/ポイント連携/グルーピング・レポート; 劣後 (→2027/4~) = 複合制御・DR・ダッシュボード・バッジ等. ※「照明アドバイス」 nghi là lỗi ghi của 省エネアドバイス (*推定*, đã ghi chú trong onboarding_guide).
- 🔍 `eminel_gw_project/docs/eminel/2_management/22_decisions.md` dòng 30–31

**Chủ thể các bước trong §3–§5**: trừ khi ghi khác, người thực hiện là **SYP**, code viết trên branch `gw-syp-dev` — đường dẫn file không ghi tên repo = `syp-eminelstandard-backend`, phần màn hình quản trị = `syp-eminelstandard-web-admin`; các bước "chốt/hỏi" đi theo kênh ghi ở §6. Nhân sự nhắc tên trong báo cáo: **swan, masao takahashi** (đều phía mui — người trả lời QAデータベース), **kihara** (mui — lead phần cứng/firmware GW).

---

## 3. Chi tiết nhóm 配信・通知系 (4 batch)

### 3.1 `DistributeMonthlyEcoPointsCommand` — cấp エコ暖房ポイント hàng tháng

**Hệ cũ đang làm gì** (確実): cron 17:00 ngày 1 hàng tháng (🔍 `legacy_eminel_docs/docs/02_詳細設計/10_バッチ処理/mng-webap_cron設定_20241029.txt:113-114`). Câu truy vấn chọn người được cấp *(cú pháp `fn(Query $q) => …` là hàm viết ngắn của PHP: nhận `$q`, trả về `$q` đã gắn thêm điều kiện)* — 🔍 `legacy_eminel_docs/sources/conciergesv-develop/src/Command/DistributeMonthlyEcoPointsCommand.php:83-104`:

```php
$query = $this->ConCustomers->find()
    ->matching('ConSensorMonthlyValues', fn(Query $q) => $q
        ->where([
            '...C_DEVICE_TYPE' => ROOM_TEMP_SETTING,        // nhiệt độ CÀI ĐẶT
            '...C_ROOM_ID' => 0,
            '...' . $sensorMonthlyValuesColName . ' <=' => 22.0,  // TB tháng trước ≤ 22.0℃
        ]))
    ->notMatching('ConPointLinkLogs', fn(Query $q) => $q
        ->where(['reason' => $pointLinkReason]))            // 'monthly_eco_points_YYYYMM' — chống cấp trùng
```

Từng nhóm: khối `matching` lọc khách có nhiệt độ **cài đặt** trung bình tháng trước ≤ 22.0℃ (bảng `s_104`); khối `notMatching` loại người đã nhận trong tháng. Sau đó mỗi khách được cộng **250 point** (hằng `BENEFIT_POINTS = 250` — dòng 33) vào `s_141` theo năm tài chính (từ tháng 4), và **gọi API PointInfinity trong cùng transaction** (dòng 116–188; *transaction = gói thao tác "được ăn cả ngã về không"* — PI lỗi thì hoàn tác khách đó, chạy tiếp khách sau). Lưu ý: code + cron chạy **hàng tháng quanh năm, không có điều kiện mùa** — trong khi tài liệu A03 của E-GW mô tả hiện hành là 「12〜3月」; lệch nhỏ cần nêu khi chốt spec.

**e-smart có sẵn không — MỘT PHẦN, dẫn chứng code** (確実; đường dẫn từ `syp-eminelstandard-backend/`):

① **Gọi thẳng PointInfinity** — Lambda riêng `src/functions/give-point-to-point-infinity/app.ts` (khai báo `template.yaml:3282`, secret dòng 3289):

```ts
// dấu } mở đầu = phần trên của lệnh đã lược; đây là "destructuring": bóc các trường từ JSON ra biến
} = JSON.parse(process.env.POINT_INFINITY_SERVER_INFO as string);   // :15 — URL + TUKA_ID/KMT_ID… từ Secrets Manager
...
const fuyoRiyuSjisArray = Encoding.convert(fuyoRiyuUnicodeArray, {  // :35-39 — lý do cấp điểm
  to: 'SJIS', from: 'UNICODE',                                      //   encode Shift_JIS thủ công
});
...
const regex = /<SYORI_STS>(.*?)<\/SYORI_STS>/;                      // :50 — parse XML trả về
if (!syoriStsValue || syoriStsValue !== '000') { ... return false; } // :56 — '000' = thành công
...
method: 'POST',                                                     // :92
headers: { 'Content-Type': 'application/x-www-form-urlencoded; charset=Shift_JIS' },  // :96
```

Từng nhóm: (a) cấu hình server PI + các ID cố định lấy từ Secrets Manager; (b) `FUYO_RIYU` (lý do cấp) phải encode **Shift_JIS** trước khi gửi; (c) response là **XML**, thành công khi `<SYORI_STS>` = `000`; (d) request là POST form. → **Cùng "họ giao thức" với hệ cũ** (hệ cũ: form CP932 — biến thể Shift_JIS trên Windows — + XML, URL `IF0200.do` — `eminel_sv_lib-develop/src/PointInfinity/PointInfinity.php:39, 65-71, 98`); chuỗi "IF0200" không xuất hiện trong backend (là tên tài liệu). Lambda tra số dư đi kèm: `get-point-quantity-from-point-infinity/app.ts` (GET + tag `<ZNDK>` — dòng 32, 79; secret `template.yaml:2629`).

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

Từng nhóm: chữ ký hàm nhận `pointBadgeStatsSk` — khóa duy nhất từng-sự-kiện để **chống cấp trùng** (kiểm tra tại dòng 69); ghi điểm/badge bằng transaction DynamoDB; nếu bước gọi PI thất bại thì **rollback** (đúng pattern hệ cũ). Số 伝票 (DENPYO_NO) lấy từ counter atomic (dòng 390–409). Model đi kèm: `PointBadgeMaster` / `PointBadgeStats` / `UserBadgeSummary` (`src/layers/common/nodejs/models/`). Người gọi hiện tại: login tháng đầu, đọc tip (`api-tip/read-tip.ts:68`), trả survey (`api-survey/answer-survey.ts:346`), kết thúc DR (`batch-end-dr/app.ts:86`), liên kết thiết bị, sau import hội viên.

③ **Cái KHÔNG có**: logic phán định từ **dữ liệu đo** — không nguồn dữ liệu cảm biến nào tham gia điều kiện cấp điểm (grep `energy|usage` trong luồng point: 0 hit) — e-smart chưa có khái niệm "dữ liệu đo từ GW".

**E-GW yêu cầu**: F-ES-04 エコ暖房ポイント + F-ES-09 PI連携; ポイント連携 thuộc nhóm **必須 2026** theo 決定 6/10 — nhưng 機能一覧 lại đánh ✅劣後 (mâu thuẫn đã đưa vào bảng QA gửi khách, câu 2; giá trị điểm/điều kiện cho E-GW chưa chốt — A03 要確認). Camp day3 ghi hướng: PI連携 「バッチが実態。ESTAサーバーに既に実装がある可能性が高い → 差分があればやる」 — nay xác nhận trên code là đúng.
- 🔍 `eminel_gw_project/docs/eminel/3_requirements/00_integrated_requirements_v1.2.md` dòng 409, 414, 675–691 ・ `22_decisions.md:31` ・ `10_feature_list.md:93, 95` ・ camp day3:125 ・ `A03_point.md:48-102`

**Phán định**: **dùng lại ①② nguyên trạng, tạo mới duy nhất ③** — đúng phương châm 差分方式.

**Cách làm từng bước**:
1. Chốt spec nghiệp vụ qua QA/A03: giá trị điểm (250 giữ không?), ngưỡng (22℃?), có giới hạn mùa 12〜3月 không (nêu điểm lệch code-vs-A03 ở trên), và kết cục mâu thuẫn 必須/劣後 (câu 2 bảng QA).
2. Chờ spec HEMS-SV (m2-cloud) để biết dữ liệu nhiệt độ cài đặt từ GW về server theo đường nào; thiết kế bảng tích lũy **trung bình tháng theo hộ** trên DynamoDB (vai trò tương đương `s_104` hệ cũ — sẽ thuộc nhóm batch 集計, phối hợp với nhóm đó).
3. Viết Lambda phán định mới: quét bảng tháng → lọc ≤ ngưỡng → gọi `givePointBadgeForUser(userId, 'eco_heating#YYYYMM', …)` — **tái dùng nguyên** cơ chế chống trùng/transaction/PI sẵn có; chỉ cần thêm lý do cấp (FUYO_RIYU) mới vào `constants.ts` (mẫu tại dòng 1756–1762).
4. Lịch: thêm 1 lịch tĩnh `ScheduleV2` hàng tháng trong `template.yaml` (theo mẫu 3 lịch tĩnh ở §2) — không cần one-shot vì đây là chu kỳ cố định.
5. Kiểm thử: dựng dữ liệu tháng giả → chạy batch 2 lần liên tiếp xác nhận **không cấp trùng**; giả lập PI trả lỗi xác nhận **rollback**; đối chiếu số điểm với kết quả chạy tay query hệ cũ trên cùng dữ liệu (phân công テスト=mui／実装=SYP).

### 3.2 `PublishRegularEcoMissionsCommand` — phát 省エネアドバイス định kỳ

**Hệ cũ đang làm gì** (確実): 1 command duy nhất, chạy với option `--eco-mission-id` (1..19); lịch là **19 dòng cron riêng**, ngày/giờ cố định theo mùa (🔍 cron dòng 82–102). Command route sang **10 lớp Publisher** — mỗi loại advice một điều kiện phán định (dùng quá trung bình, chưa bật ECO mode, quên hẹn giờ ngủ/vắng nhà, tỷ lệ sưởi, kỷ niệm hợp đồng…). *(Folder có 11 file nhưng 1 là lớp option; `04_バッチ一覧.md` ghi 「11種Publisher」 là đếm cả file đó.)* Publisher tạo bản ghi advice **và** đăng ký push (hẹn sau 1 phút) — việc gửi thật do batch §3.3 làm. *Quan hệ ba con số: 19 = số loại advice (mission-id) hiện hành → route vào 10 lớp Publisher dùng chung; 15 = con số 「約15種」 ghi trong CLD-06 khi bàn gom loại → 7種+エコ暖房ポイント.*
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

Từng nhóm: `body_tip` là nội dung biên tập sẵn; `target_type` chỉ có 3 kiểu targeting tĩnh (`batch-send-tip-preprocessing/app.ts:43-50`); `point_quantity` cấp điểm khi user bấm "đọc rồi" (`api-tip/read-tip.ts:68`). **Không trường nào, không hàm nào đọc dữ liệu năng lượng của hộ để quyết định phát** (grep `energy|usage` trong `api-tip`: 0 hit) — tức "advice engine" phán định cá nhân hóa của hệ cũ **không tồn tại** ở e-smart.

**E-GW yêu cầu**: scope 2026 (F-ES-03 không ✅ = 今期必須; 決定 6/10 dòng アドバイス※). Yêu cầu mới **khác hệ cũ**: [G] đòi 自動配信 theo 定期配信スケジュール **chỉnh được từ 管理画面** (hiện hành cron cố định — chính là chỗ 「いけてない」); gom 15種→7種+エコ暖房ポイント chưa chốt (CLD-06 未動); 判定式 có 踏襲 nguyên không cũng T.B.D (G-C-05 — **判定式 từng loại đã được trích sẵn vào [G]**, code cũ chỉ để xác minh chéo).
- 🔍 `4_spec/admin/G_energy_advice.md:18-19, 28-29, 47` ・ `00_integrated_requirements_v1.2.md:632-647` ・ `20_open_issues.md:176-177`

**Phán định**: **Tạo mới** — dùng "đường ra" sẵn có (targeting + push + point của Tip pattern), viết mới tầng phán định.

**Cách làm từng bước**:
1. Chờ/thúc CLD-06 chốt danh mục 7種 (câu Dự phòng 1 bảng QA); song song rà bảng 判定式 trong [G] G-C-05, đánh dấu từng 判定式 cần dữ liệu đầu vào gì và dữ liệu đó trên E-GW lấy từ đâu (GW đo? TagTag? Xzilla?) — đây là bảng quyết định khối lượng thật.
2. Thiết kế model `Advice` mới phỏng theo `Tip` (giữ `target_type`/`point_quantity`/push flags để tái dùng đường phát) + thêm phần "điều kiện phán định" và **định期 schedule admin đặt được** theo G-A-02.
3. Dựng **batch skeleton** (バッチボーン §2): state machine `BatchJudgeAdvice` (per loại) → `BatchSendAdvice` → `BatchPushNotice` — nối bằng one-shot scheduler như chuỗi news/tip hiện có (`api-news/common.ts:207-209` là mẫu); ban đầu judgment trả danh sách rỗng/giả để các phần khác test được.
4. Làm UI web-admin: form quản lý advice theo mẫu `components/tip/tip-form.vue` (đã có sẵn khối 付与ポイント/バッジ, targeting, push) + phần đặt 定期配信スケジュール (mới — [G] G-A-02).
5. Implement từng 判定式 theo danh mục đã chốt ở bước 1; mỗi loại một Lambda judgment, đầu ra là danh sách user → ghi advice + enqueue push theo pattern sẵn có.
6. Kiểm thử: mỗi 判定式 một bộ dữ liệu biên (đúng/sai ngưỡng); chạy trước 結合フェーズ (mục tiêu tháng 9 — §2).

### 3.3 `DispatchPushMessagesCommand` — gửi push mỗi phút

**Hệ cũ đang làm gì** (確実): chạy mỗi phút, lấy `push_message_destinations` đến hạn (đọc theo trang, mỗi trang 500 bản ghi), validate (đúng một trong device_token/FCM topic), POST sang **PushCore** (server trung gian `localhost:54650`) → PushCore đẩy tiếp FCM (*suy đoán* — code PushCore không nằm trong repo); retry 3 phút/lần, bỏ sau 5 lần.
- 🔍 `…/src/Command/DispatchPushMessagesCommand.php:51-125` ・ `eminel_sv_lib…/StaticServices/PushMessageService.php:26, 36-39` ・ `config/push_message.php:4-14` ・ cron dòng 79–80

**e-smart có sẵn không — CÓ ĐẦY ĐỦ, dẫn chứng code** (確実):

① Bảng token — 🔍 `src/layers/common/nodejs/models/MobileTokenManagement.ts` (nguyên văn cả file):

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
      await removeMobileTokenInvalid(mobileToken);               // token chết → xóa khỏi bảng
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

Từng nhóm: mỗi lần chạy xử lý **một lô** (segment) user đã được bước preprocessing chia sẵn — 10 000 user/lô (`batch-push-notice-tip-new-preprocessing/app.ts:53`); trong lô gửi song song tối đa 100 lệnh/lúc (`src/layers/common/nodejs/services/push-notice-to-user.ts:21` — có lọc cờ opt-in của user); `target_screen`/`target_id` khớp với code app Flutter điều hướng khi bấm thông báo (`syp-eminelstandard-app-syp-dev/lib/presentation/pages/main/bottom_navigation_view.dart:473-528`; app đăng ký token qua `user/save_mobile_token` — dòng 101–111). Có 6 state machine push notice: survey/news/tip/DR-new/DR-start/DR-end (`template.yaml:510/685/815/1889/1927/1965`).

**E-GW yêu cầu**: **D03 (trạng thái レビュー中 — chưa fix)** ghi 踏襲元 = **ESTA Push基盤 ＋ 現行（通知種別の網羅 — rà đủ danh mục loại thông báo hiện hành）**, 「全要件がESTA既存のため【新規】なし」 — 🔍 `3_requirements/app/D03_push.md:7, 32-34, 84-86`.

**Phán định**: **Bỏ batch cũ** (không dựng lại PushCore + hàng đợi DB + cron mỗi phút), **dùng hạ tầng push e-smart** — theo tiền đề deploy §2, nếu chốt độc lập thì là dựng lại stack đó trên môi trường mới.

**Cách làm từng bước** (chủ yếu là việc "bỏ cho đúng"):
1. Đưa "hạ tầng Push (FCM)" vào danh sách trả lời vế ただし của QA 独立デプロイ (§1 việc ngay #1) để mui xác nhận hướng dùng chung.
2. Rà **danh mục 通知種別 (loại thông báo) của hệ cũ** (vế 「＋現行」 của D03): liệt kê mọi loại thông báo hệ cũ đang phát (advice 19 loại, DR, 見守り — *thông báo trông nom người thân từ xa, đang treo CLD-05*, レポート…), map từng loại sang: nguồn sinh nội dung mới (§3.1/§3.2/…) + `target_screen` mới trên app E-GW. Đầu ra: bảng mapping cho D03 khi fix.
3. Nếu deploy độc lập: dựng Firebase project riêng cho app E-GW, bảng `MobileTokenManagement` + API `user/save_mobile_token` trên môi trường mới (pattern có sẵn, việc là cấu hình + credential qua Secrets Manager).
4. KHÔNG lập task port `DispatchPushMessagesCommand`/PushCore — ghi rõ "bỏ, thay bằng batch-push-notice pattern" khi tách task Notion để khỏi đếm nhầm vào ~46本.
5. Kiểm thử: gửi thử tới thiết bị dev với token thật; thử token chết xác nhận tự xóa (②); đo giới hạn 4096 byte message (`constants.ts:223`).

### 3.4 `ControlDrOperationCommand` — điều khiển chỉ lệnh DR

**Hệ cũ đang làm gì** (確実): chạy mỗi phút, 2 phase; với mỗi hộ tham gia DR: né xung đột lệnh (5 phút), ghi lệnh vào bảng `instructions` — lệnh 宅外制御指示 (*điều khiển từ ngoài nhà*) mã hóa theo **ECHONET** (*chuẩn giao tiếp thiết bị gia dụng của Nhật*; EPC 80/B0 = mã lệnh bật-tắt/đổi nhiệt độ) — và phải **giả dạng như thao tác từ app user**. Comment nguyên văn trong code — 🔍 `…/src/Command/ControlDrOperationCommand.php:171-172`:

```php
// 暖房制御ユニットとユーザのアプリ端末の情報を取得
// ユーザのアプリ端末からの操作のように見せかけないとゲートウェイが指令を無視する
```

(*"phải giả dạng như thao tác từ thiết bị app của user, nếu không gateway sẽ bỏ qua chỉ lệnh"* — DR hệ cũ = server ghi lệnh vào DB, GW **poll** — định kỳ tự hỏi "có lệnh mới không?" — qua hemssv.)

**e-smart có sẵn không — CÓ KHUNG DR KHÁC KIỂU, dẫn chứng code** (確実):

① Model DR event + trạng thái-trước-điều-khiển — 🔍 `src/layers/common/nodejs/models/Dr.ts:5-30` và `DrUserAction.ts:1-14`:

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

Từng nhóm: start-DR điều khiển thiết bị theo `control_setting` và **lưu `pre_control_status`** (dòng 212); end-DR cấp point (tái dùng §3.1-②) rồi **khôi phục thiết bị về trạng thái trước DR** (dòng 96–190). Thiết bị điều khiển được: **Rinnai / Noritz / Daikin / điều hòa・fancon qua MUI hồng ngoại** (`batch-end-dr/app.ts:139-188`) — đều là thiết bị nối trực tiếp cloud hãng, **không có đường nào qua GW**. Lịch start/end đặt one-shot khi admin tạo DR (`batch-send-dr-complete/app.ts:127-143`, `api-dr/update-dr.ts:149`); web-admin có trọn màn hình DR管理 (`pages/distribution-management/dr/` + `components/dr/dr-form.vue` — 1881 dòng).

**E-GW yêu cầu**: F-ES-07/08 + F-AD-08 — **劣後, 2027/4以降** (決定 6/10; B05: 26年スコープ=なし). Kiến trúc tương lai: DR サーバー主導, lệnh xuống GW qua **HEMS-SV (m2-cloud)**; cách kết thúc DR (server phát lệnh đúng giờ vs GW tự kết thúc — GW有状態か) **chưa chốt** — câu 5 bảng QA gửi khách, ràng buộc firmware 2026.
- 🔍 `22_decisions.md:30-31` ・ `B05_dr.md:8, 33-37` ・ camp day3:113-122 (DR発令 詰め込み → tách ~17項目)

**Phán định**: **Không code 2026.** 2027: tạo mới trên khung DR e-smart; tuyệt đối không kế thừa mẹo "giả dạng app user".

**Cách làm từng bước**:
1. (2026 — duy nhất) Chốt nội bộ với kihara rồi hỏi khách: GW có được giữ trạng thái DR không (終了方式 án A/B — câu 5 bảng QA). Kết quả quyết thiết kế firmware, KHÔNG chờ được đến 2027.
2. (2027) Giữ nguyên lớp "sự kiện DR": model `Dr`/`DrUserAction`/`DrStats`, màn hình admin, targeting, 3 mốc push, cấp điểm cuối kỳ — tất cả tái dùng.
3. (2027) Thêm loại thiết bị điều khiển mới trong `control_setting`: "sưởi qua E-GW" — implement `handleControlDevice` nhánh mới gọi **API của HEMS-SV (m2-cloud)** theo spec mui sẽ cung cấp (thay cho việc ghi bảng `instructions` + chờ GW poll của hệ cũ).
4. (2027) Map `pre_control_status` cho thiết bị sưởi qua GW (khôi phục sau DR) — phụ thuộc kết quả bước 1 (GW giữ trạng thái hay server giữ).
5. (2027) Tách task theo day3 (~17項目 đã lập trên Notion) — không gom mọi thứ vào một batch như hệ cũ.

---

## 4. Chi tiết nhóm 外部連携・受信系（Xzilla取込） (3 batch)

**Hệ cũ nhận thế nào**: file CSV từ Xzilla qua **SFTP vào 中間サーバ** (server trung gian), mỗi 5–10 phút một lượt.

**e-smart nhận thế nào — dẫn chứng code** (確実): luồng **SFTP → S3 → DynamoDB**, chạy **mỗi giờ một lượt từ 0h–7h JST** (`cron(5 0-7 * * ? *)` — §2), điều phối bởi state machine `src/statemachine/batch_run_sequentially.asl.json` (chống chạy chồng dòng 5–38 → dọn temp → list file → 8 nhánh forward song song → import → 3 hậu xử lý). Danh mục thư mục IF trên SFTP nằm ngay trong code — 🔍 `src/functions/batch-get-list-file-name-from-sftp-server/app.ts:149-169`:

```ts
const DEFAULT_FOLDER_CSV = {
  IF2241: `${folderTemp}/IF2241/`,   // hội viên TagTag       DM1040: danh sách hợp đồng
  DM1040: ..., IF2242: ...,          // IF2242: thuộc tính hội viên
  IF2016: ..., IF2023: ...,          // IF2016: 供給地点 / IF2023: 使用契約
  IF2024: ..., IF2029: ..., IF2223: ...,  // 顧客 / 建物 / 機器
};
const DEFAULT_FILE_NAME_METADATA = {
  IF2241: `${folderTemp}/IF2241/END/IF22410001_{%1}.dat`,  // file .dat trong END/ = "chuyến hàng đã chốt"
  ...
```

Từng nhóm: mỗi IF một thư mục CSV + một file metadata `.dat` trong `END/` (đọc `.dat` để biết danh sách file CSV thực của chuyến — dòng 52–66); chống tải trùng bằng bảng `CsvDownloadHistory` (dòng 69–87 — vai trò thật của bảng này, xem §5); file được chia gói 50 000 dòng đẩy lên S3 (`batch-forward-csv-from-sftp-server-to-s3/app.ts:56-64`) rồi các handler `batch-ifXXXX-import-*` ghi DynamoDB bằng transaction. Thứ tự import: IF2241 → DM1040 → IF2242 tuần tự (phụ thuộc dữ liệu), 5 IF còn lại song song (asl dòng 493–794). Khi merge hội viên "fake" (đăng ký app trước khi có data Xzilla), có **lock 5 phút** — 🔍 `batch-if2241-import-tagtag-kaiin/app.ts:69, 102-111`:

```ts
const UPDATE_LOCK_TTL_MINUTES = 5;
...
const kaiinUpdatingItem = {
  kaiin_bango: kaiinBangoFake,
  ttl: dayjs().add(UPDATE_LOCK_TTL_MINUTES, 'minute').unix(),  // lock tự hết hạn bằng TTL
};
await putDataToDBWrap(TABLE_KAIIN_UPDATING as string, kaiinUpdatingItem);
```

(39 API handler kiểm lock này qua `check-kaiin-updating.ts:10-15` để chặn thao tác khi đang merge.) **3 hậu xử lý** sau import: ① phát lại nội dung đang chạy cho hội viên mới (`batch-send-contents-to-updated-user/app.ts:79-132`); ② cập nhật nơi-ở-đang-chọn khi hợp đồng gas hết hiệu lực + cấp badge khi xuất hiện hợp đồng sưởi ゆ抜く (code: YUNUKKU, mã `PG003` — `batch-update-selecting-place-no/app.ts:89-143, 283-296`; `constants.ts:1909`); ③ xóa liên kết + thiết bị khi hết hợp đồng gas (`batch-remove-integration-expired/app.ts:44-79`).

**Ba IF của hệ cũ đều KHÔNG tồn tại trong e-smart** (確実): grep toàn backend `IF1156`・`IF2249`・`IF2264`・`30分`・`HalfHour`・`half_hour`・`速報`・`確報`・`electric_power`・`cntct` = **0 hit**. (Từ `payer` chỉ xuất hiện dưới dạng hằng lọc vai trò 支払者 khi import DM1040 — `batch-dm1040-import-user-contract-list-preprocessing/app.ts:54, 63` — củng cố rằng thông tin người trả tiền đã được xử lý trong luồng DM1040, không có IF riêng.)

**Chiều GỬI (e-smart → 基幹) có thật** (確実) — 🔍 `src/layers/common/nodejs/services/upload-data-backup-to-sftp.ts:22-43, 52-57`:

```ts
const pathExport = '/EST';                       // thư mục đích trên SFTP
switch (dataType) {
  case DEVICE_DATA_TYPE.INFRARED_REMOTE:
    prefixFileName = `sekigaisenrimokon_${...}`; // remote hồng ngoại
  case DEVICE_DATA_TYPE.USAGE_DAILY:
    prefixFileName = `kyutoki_usage_daily_${...}`; // kyutoki = 給湯器 (máy nước nóng)
  ...
await connectSftpWithRetry(sftp, {
  host: serverInfo.host, port: serverInfo.port,
  username: serverInfo.username_for_upload,      // user RIÊNG cho chiều upload
  private_key: serverInfo.private_key_for_upload,
});
```

Từng nhóm: 6 loại CSV dữ liệu thiết bị (5 kyutoki + remote hồng ngoại) được đẩy lên thư mục `/EST` của **cùng SFTP server** bằng tài khoản upload riêng, chạy hằng ngày 8:00 trong `BatchMigrationIntegratedDataStateMachine` (`template.yaml:2215-2226`). 🔸 *Giả thuyết — CHƯA kiểm chứng: đích `/EST` là Xzilla/DWH (kho dữ liệu phân tích) — địa chỉ nằm trong secret ngoài code, phải hỏi mui. Nếu đúng, đây là hiện thực sẵn có của* 「EMINELデータの共有」 *(F-ES-10 chiều xuất — `00_integrated_requirements_v1.2.md:696`).* Khi lập danh mục task Xzilla phải **thêm mục chiều xuất này**, đừng chỉ đếm theo batch cũ. Ghi chú: camp day3 dòng 126 nhắc アプリログ gửi 基幹 "có thể đã có ở ESTA" — đã kiểm: backend **không** có đường đẩy app log ra SFTP, chỉ có download cho admin.

### 4.1 `RcvCntctCancellationCommand` — nhận 解約 điện (IF2249)

- **Hệ cũ** (確実): mỗi 5 phút SFTP lấy CSV hôm nay; lọc 契約種別 PE624/625 (dòng 242–243); upsert (*có thì cập nhật, chưa có thì thêm*) vào `ipf_cntct_cancellations`; **bật cờ dừng tính 買電売電** (`t_101.c065=1`) cho khách đã hủy; xong gọi 顧客情報登録完了通知API. 🔍 `RcvCntctCancellationCommand.php:30, 99-113, 209-217, 242-243, 306-334` ・ cron dòng 107–108
- **E-GW**: không có yêu cầu riêng cho luồng 解約 tự động; flow nghiệp vụ ghi rõ vô hiệu hóa GW sau giải ước là **thao tác thủ công trên 管理画面**; IF-01 còn treo (CLD-07 ~10 mục 要確認). 🔍 `1_product/11_business_process/readme.md:938-941` ・ `20_open_issues.md:181-182`
- **Phán định** (*推定*): **không bê nguyên**, nhưng **nghiệp vụ không biến mất**: chừng nào E-GW còn tính 買電売電 từ 30分値 (mà có — §4.3) thì vẫn phải có cái gì đó bật cờ "dừng tính" khi khách hủy hợp đồng điện (flow thủ công chỉ nói vô hiệu GW, KHÔNG nói dừng tính).
- **Cách làm từng bước**:
  1. Khi CLD-07/IF-01 định hình: xác nhận có luồng dữ liệu 解約 không. **Nếu không có → nêu yêu cầu bổ sung ngay qua CLD-07/QA** (không được lặng lẽ bỏ vì #7 cần cờ dừng tính).
  2. Nếu có: KHÔNG tạo batch 5-phút riêng — thêm 1 loại IF vào luồng import sẵn có, các bước kỹ thuật theo đúng pattern: thêm thư mục vào `DEFAULT_FOLDER_CSV`/`DEFAULT_FILE_NAME_METADATA` (trích code đầu §4), thêm định nghĩa cột `LIST_COL_*` vào `constants.ts`, thêm Map-branch forward trong `batch_run_sequentially.asl.json`, viết handler `batch-ifXXXX-import-*` theo mẫu IF2016 (Put đơn giản).
  3. Logic nghiệp vụ "dừng tính": implement thành **hậu xử lý ④** sau import (theo mẫu 3 hậu xử lý sẵn có) — bật cờ trên bản ghi hộ tương ứng; nhịp cửa sổ 0–7h mỗi-giờ của e-smart đủ cho nghiệp vụ giải ước (*推定* — xác nhận với nghiệp vụ khi chốt IF-01).
  4. Kiểm thử: dựng CSV giả có/không PE624/625; xác nhận cờ dừng tính phản ánh vào tính 買電売電 của #7.

### 4.2 `RcvEmsPlsCntrPayerCommand` — nhận master 支払者 (IF2264)

- **Hệ cũ** (確実): mỗi 5 phút; **xóa toàn bộ rồi nạp lại** bảng `ipf_ems_pls_cntr_payers` từ CSV (memory_limit 4096M — dòng 63); áp **契約終了判定 3 điều kiện** (comment spec ngay trong code, dòng 373–385) để cập nhật các số liên kết + cờ dừng tính trên `t_101`. 🔍 `RcvEmsPlsCntrPayerCommand.php:63, 170-177, 245-363, 371-626` ・ cron dòng 105–106
- **E-GW**: không có chức năng "payer" riêng trong toàn bộ docs/eminel (đã grep); phạm trù gần nhất là F-ES-10 契約情報取得, và グルーピング (必須 2026) cần 建物種別/料金メニュー/アンペア数 từ Xzilla. 🔍 `00_integrated_requirements_v1.2.md:415, 619, 692-696`
- **Phán định** (*推定*): **không bê nguyên** (full-reload 5 phút/lần là điển hình 「いけてない」); dùng luồng import hợp đồng sẵn có (IF2023/2024/DM1040 — DM1040 của e-smart đã lọc sẵn vai trò 支払者).
- **Cách làm từng bước**:
  1. **Trích logic 契約終了判定 3 điều kiện từ comment trong code cũ thành 1 trang spec** (tri thức nghiệp vụ đáng bảo tồn — nguồn: `RcvEmsPlsCntrPayerCommand.php:373-385`) — làm ngay được, không chờ IF-01.
  2. Khi IF-01 định hình: đối chiếu các trường payer hệ cũ dùng (供給地点特定番号, IPF使用契約番号, 受電地点特定番号, お客様番号) với dữ liệu IF2023/2024/DM1040 sẵn có của e-smart — thiếu trường nào thì yêu cầu bổ sung vào IF-01, KHÔNG yêu cầu nguyên một IF payer riêng nếu không cần.
  3. Implement phần thiếu như mở rộng handler import hợp đồng hiện có (thêm cột/thêm xử lý), áp spec 契約終了判定 từ bước 1 làm hậu xử lý.
  4. Kiểm thử: 3 điều kiện kết thúc hợp đồng × (đúng/sai) trên dữ liệu giả; so kết quả cờ/số liên kết với chạy tay logic hệ cũ.

### 4.3 `RcvHalfHourElectricPowerCommand` — nhận 電力30分値 (IF1156)

- **Hệ cũ** (確実): mỗi 10 phút; nạp lại `emn_all/fast/confirm_electric_powers` (速報値/確報値); rồi **tính 買電・売電**: gộp cặp 30 phút → giá trị giờ, ghi `s_102`; điều kiện rẽ nhánh: nhà có 太陽光 (điện mặt trời) → 売電 tính từ số liệu GW (batch tích lũy ngày làm), nhà コージェネ (đồng phát) có 受電地点特定番号 → tính từ số liệu Xzilla. 🔍 `RcvHalfHourElectricPowerCommand.php:107-122, 449-583, 734-1050` (điều kiện rẽ nhánh 875–893) ・ cron dòng 109–110
- **e-smart**: **không có** (確実) — grep 0 hit (đầu §4); dữ liệu sử dụng điện/gas của e-smart lấy qua **TagTag API** (`02_product_overview.md:119`).
- **E-GW**: **cần, minh văn, 2026**: 「電力30分値はCルート（Xzilla経由）で取得する」 (mục 3-2); F-ES-10 định nghĩa lấy 速報値・確報値; nuôi グラフ (F-ES-01), グルーピング・レポート (必須). 連携テスト(Xzilla) không ✅ = giữ trong 今期. 🔍 `00_integrated_requirements_v1.2.md:84, 692-696` ・ `10_feature_list.md:148`
- **Phán định** (確実): **tạo mới** — batch nặng nghiệp vụ nhất trong 11 cái.
- **Cách làm từng bước**:
  1. Chốt IF-01 cho 30分値: format file, nhịp cấp (hệ cũ 10 phút/lượt; nền e-smart hiện chỉ quen cửa sổ 0–7h — nhịp gần-real-time sẽ là điểm mới, phải thống nhất với 北ガス), 認証 (CLD-07).
  2. Dựng đường nhận theo pattern import §4 (SFTP→S3→handler); nếu nhịp dày hơn cửa sổ 0–7h → lịch riêng (`ScheduleV2` mới) thay vì nhét vào `BatchRunSequentially`.
  3. Thiết kế bảng DynamoDB cho 30分値: tách 速報値 (đổ đè) / 確報値 (chốt) — vai trò tương đương `emn_fast/confirm_electric_powers` hệ cũ; cân nhắc TTL cho dữ liệu thô theo 保持期間 (SVC-03).
  4. Port **logic nghiệp vụ** (không port code): quy tắc gộp 2×30分 → 1時間値; bảng điều kiện tính 買電/売電 theo cấu hình nhà (太陽光/コージェネ/受電地点特定番号 — nguồn: dòng 875–893 code cũ) — **map lại theo 9 pattern lắp đặt của E-GW** (*9 kiểu tổ hợp thiết bị lắp trong nhà — định nghĩa ở 統合要件 v1.2 mục 3-5; diễn giải dễ hiểu: onboarding_guide Chương 2*; cấu hình mới có thể thêm nhánh).
  5. Nối đầu ra vào nhóm batch 集計 (グラフ/グルーピング/レポート — ngoài báo cáo này) + cờ dừng tính từ §4.1.
  6. Kiểm thử: bộ dữ liệu 30分値 giả phủ các nhánh (solar/コージェネ/thường, 速報→確報 ghi đè, thiếu cặp 30 phút) — đối chiếu kết quả giờ với chạy tay logic hệ cũ trên cùng input.

---

## 5. Chi tiết nhóm CSV/ZIPエクスポート系 (4 batch)

**Bản chất hệ cũ** (確実 — dễ hiểu nhầm nếu chỉ đọc tên): 4 batch này **không phải chức năng "tải dữ liệu" cho người vận hành**, mà là **backup-trước-khi-xóa** phục vụ chính sách giữ dữ liệu ngắn trong DB. Lịch chạy lúc 05:15: #8/#9 hằng ngày (thứ Hai nén ZIP tuần), #10/#11 chỉ ngày 1 hằng tháng (nén ZIP luôn) — chu kỳ từng batch xem bảng 1.3. Cron nằm ở mục 「#12.DBデータ削除」 trong file cron (đừng nhầm với đánh số batch 1–11 của báo cáo); shell dùng `set -eu` — gặp lỗi là dừng ngay, nên CSV hỏng thì bước xóa **không** chạy. Nội dung: xuất các **partition** (*ngăn dữ liệu — bảng lớn được chia sẵn thành ngăn theo ngày/tháng, xóa được nguyên ngăn một lần rất nhanh*) đủ 8 ngày tuổi (`t_202` 機器状態, `s_102` 時間値) / tháng trước (`s_103` 日値, `s_113` 日平均値) ra CSV rồi ZIP, sau đó `DeleteData` xóa partition. File nằm trên đĩa server, người vận hành tải qua màn hình quản trị hệ cũ.
- 🔍 4 file `CreateCsvAndZip*Command.php` (mỗi file dòng ~39: partition −8 ngày / −32 ngày) ・ `CreateZipsTrait.php:23-72` ・ cron dòng 39–41 + `cron設定概要.txt` 補足1 「CSV作成後に問題なければデータを消去」

**e-smart có sẵn không — cơ chế "backup rồi xóa" KHÔNG có; nhu cầu xuất dữ liệu được giải bằng 2 đường, dẫn chứng code** (確実):

① **Admin download on-demand** — router 17 endpoint (*mỗi endpoint = một "cửa" API tải một loại dữ liệu*) — 🔍 `src/functions/api-download/app.ts:23-46` (trích):

```ts
const APIs = { POST: {
  [`/${END_POINT}/download_list_dr`]: downloadListDr,
  [`/${END_POINT}/download_list_news`]: downloadListNews,
  [`/${END_POINT}/download_dr_stats`]: downloadDrStats, ...
  [`/${END_POINT}/download_access_log`]: downloadAccessLog,
  [`/${END_POINT}/download_user_info`]: downloadUserInfo,
  [`/${END_POINT}/download_point_award_history`]: downloadPointAwardHistory,
  [`/${END_POINT}/download_gas_equipment_data`]: downloadGasEquipmentData, ...
```

Loại nặng được đẩy sang chạy nền (invoke **bất đồng bộ**) qua `BatchDownloadFunction` (`api-download/download-user-info.ts:17-25`; `template.yaml:475-493` — MemorySize 5120, Timeout 900) → nén zip lên S3 `BUCKET_DOWNLOAD` (`template.yaml:233`) → admin tải qua **presigned URL** (link tải có chữ ký, tự hết hạn 600 giây — `api-s3/get-presigned-url-for-download.ts:67`). Trang web-admin tương ứng — 🔍 `syp-eminelstandard-web-admin/constants/common.ts:614-622` (7 loại dữ liệu của trang `pages/other/data-management/`):

```ts
export const DOWNLOAD_DATA_MANAGEMENT_TYPE = {
  USER_INFO: 'user_info',            ACCESS_LOG: 'access_log',
  MUI_SENSOR_HISTORY: 'mui_sensor_history', GAS_DEVICE_HISTORY: 'gas_device_history',
  POINT_AWARD_HISTORY: 'point_award_history', BADGE_EARNED_HISTORY: 'badge_earned_history',
  GAS_DEVICE_RAW_HISTORY: 'gas_device_raw_history',
}
```

② **Export định kỳ ra SFTP `/EST`** (trích code ở §4) — tiền lệ trực tiếp nếu 北ガス muốn nhận file đổ sẵn định kỳ.

⚠️ Đính chính một hiểu nhầm dễ mắc từ tài liệu khảo sát: bảng `CsvDownloadHistory` (「CSVダウンロード履歴」) **thuộc chiều NHẬN** — lịch sử tải file từ SFTP về để chống tải trùng (`models/CsvDownloadHistory.ts:1-6`; ghi tại `batch-forward-csv…:80-93`) — không phải lịch sử download của admin. DB không có mô hình "xóa sau N ngày, giữ ZIP"; DynamoDB bật PITR và có TTL từng bảng khi cần (*TTL = bản ghi tự xóa khi quá hạn*).

**E-GW yêu cầu** — **bản chất yêu cầu đã đổi**: spec [I] (DRAFT) định nghĩa データダウンロード từ admin cho: các loại kế thừa E-Smart (顧客情報, アプリアクセスログ, ポイント付与履歴… — đều 🔴T.B.D cho E-GW) + 3 loại **E-GW mới**: GW・連携デバイスデータ, 連携デバイスエラー履歴, **連携機器別計測値集計データ (10分/1時間/1日/1ヶ月値)** — xuất CSV(ZIP), **保持期間 24ヶ月 (T.B.D)**. Đồng thời SVC-03: yêu cầu 保持期間/backup của hệ mới **chưa được định nghĩa**.
- 🔍 `4_spec/admin/I_data_download.md:16-19, 43-52, 200-204` ・ `20_open_issues.md:87` (SVC-03)

**Phán định** (確実 về hướng, chi tiết chờ T.B.D): **bỏ cả 4 batch ở dạng hiện tại** — tiền đề của chúng (DB chỉ giữ ~8 ngày dữ liệu hạt mịn) mâu thuẫn với "giữ 24 tháng, tải bất kỳ lúc nào".

**Cách làm từng bước**:
1. Chốt spec [I] (loại dữ liệu E-GW + 保持期間 24ヶ月?) và SVC-03 (retention/backup tổng thể) — nêu khi review spec [I]; **chưa có trong bảng QA, cân nhắc thêm câu hỏi** (§6#6).
2. Thiết kế retention thay thế: dữ liệu hạt mịn để trong DynamoDB theo 保持期間 chốt ở bước 1 (dùng TTL), hoặc chuyển bớt sang S3 (nơi lưu rẻ hơn) nếu giữ 24 tháng trong DB quá tốn — quyết theo dung lượng ước tính của nhóm 集計.
3. Mở rộng cơ chế download sẵn có cho loại dữ liệu E-GW mới, theo đúng pattern ①: thêm endpoint vào `api-download/app.ts` → viết handler trong `batch-download/` (mẫu: `download-user-info.ts`) → thêm loại vào `DOWNLOAD_DATA_MANAGEMENT_TYPE` + form trong web-admin (`components/data-management/`).
4. Nếu 北ガス muốn giữ thói quen "file ZIP tuần/tháng đổ sẵn": làm 1 batch export định kỳ theo pattern ② — quyết định thuộc [I] 未決事項.
5. Format cột CSV: nên giữ tương thích định dạng cũ vì người vận hành 北ガス đã quen (*推定* về thói quen). Danh mục cột hiện hành **đã được trích sẵn vào [I]** (mục 現行EMINEL, từ `DownloadController::getCsvHeadersOnSelection()`) — header trong 4 batch cũ chỉ dùng **xác minh chéo**, đừng lập task trích lại.
6. Khi tách task Notion: ghi rõ 4 batch cũ = "bỏ, thay bằng retention + download/export" để khỏi đếm nhầm vào ~46本.

---

## 6. Việc cần xác nhận tiếp (tổng hợp)

| # | Việc | Liên quan | Hành động phía SYP / kênh |
|---|---|---|---|
| 1 | **Chốt kiến trúc DR 2026**: GW có được giữ trạng thái DR không (終了方式 án A/B) — ràng buộc firmware 2026 | batch #4 (§3.4 bước 1) | Đã có **câu 5** bảng QA gửi khách; cần **chốt nội bộ với kihara trước** rồi mới gửi |
| 2 | Định nghĩa 入出力 + 認証 IF-01 Xzilla (CLD-07) — gồm cả **chiều xuất** (EMINELデータの共有) | batch #5–#7 (§4) | Chờ 北ガス qua PM mui; trong lúc chờ, SYP soạn sẵn danh mục trường cần thiết (rút từ code cũ — §4.2 bước 1–2) để đối chiếu nhanh khi spec về |
| 3 | **Xác nhận đích SFTP `/EST`** có phải Xzilla/DWH không (secret ngoài repo) | chiều xuất (§4) + việc ngay #2 (§1) | SYP hỏi mui (kênh QAデータベース Notion hoặc khi nhận spec HEMS-SV) |
| 4 | Mâu thuẫn ポイント 必須/劣後 + giá trị điểm E-GW | batch #1 (§3.1 bước 1) | Đã có **câu 2** bảng QA gửi khách; riêng điểm lệch 12〜3月 vs quanh năm (§3.1) → nêu khi chốt spec A03 |
| 5 | Gom advice 15種→7種 (CLD-06) + schedule/判定式 spec [G] | batch #2 (§3.2 bước 1) | Đã có **câu Dự phòng 1** trong bảng QA; phần schedule nêu khi review spec [G] |
| 6 | 保持期間・loại dữ liệu download spec [I] + SVC-03 | batch #8–11 (§5 bước 1) | SYP nêu khi review spec [I] — **chưa có trong bảng QA, cân nhắc thêm câu hỏi** |
| 7 | Báo mui danh sách "chức năng dùng tiếp hệ hiện hữu" (2 vế — §1) | §1 việc ngay #1 ・ §3.3 bước 1 | SYP trả lời trực tiếp trên trang QAデータベース Notion |
| 8 | 見守り通知 làm hay không (CLD-05) | danh mục batch **sinh nội dung push** mới (§3.3 bước 2) | Đã có **câu 3** bảng QA gửi khách |

## 7. Nguồn chính đã dùng

- **`legacy_eminel_docs`** (@`ccd8f56`): `docs/03_API仕様/04_バッチ一覧.md`; code 11 command trong `sources/conciergesv-develop/src/Command/` + `eminel_sv_lib-develop` (PI, Push, bảng); cron: `docs/02_詳細設計/10_バッチ処理/*.txt` (+ shell trong tgz)
- **`eminel_gw_project`** (@`788b438`): `docs/eminel/`: 統合要件 v1.2 (F-ES-03/04/07–10, F-AD-08/09, mục 3-2), `1_product/10_feature_list.md`, `1_product/11_business_process/readme.md`, `2_management/22_decisions.md` (quyết định 6/10), `20_open_issues.md` (CLD-05/06/07, SVC-03), camp day3 minutes, app requirements (A03/B05/D03), admin spec ([G]/[I]); `docs/eminel-smart/` (tài liệu khảo sát ESTA — 6 file; ⚠️ 5 điểm lệch code, xem mục Giới hạn)
- **`syp-eminelstandard-backend`** (@`dc39aa39`, branch `gw-syp-dev`): `template*.yaml`, `src/functions/**`, `src/layers/common/nodejs/**`, `src/statemachine/*.asl.json`
- **`syp-eminelstandard-web-admin`** (@`e550326`, branch `gw-syp-dev`): `pages/`, `components/`, `services/`, `stores/`, `constants/`, `locales/`
- **`syp-eminelstandard-app-syp-dev`** (snapshot): `pubspec.yaml`, `lib/server/rest_client/*`, `lib/presentation/pages/*`, l10n
- **QAデータベース Notion** (trạng thái 回答中 khi tham chiếu — mở trang gốc kiểm tra trước khi trích lại): 「旧Eminel基盤継承＋EMINEL-smartサーバーは独立デプロイの確認」 (swan) ・ 「旧EMINEL調査範囲（conciergesv/eminelsv）とhemssv対象外の確認」 (swan) ・ 「管理画面は独立か共通か（切替モード追加）の確認」 (masao takahashi)
