# MEMORY INDEX — Onboarding dự án EMINEL Gateway (E-GW)

## ⛔ QUY TẮC VẬN HÀNH — BẮT BUỘC, ĐỌC & TUÂN THỦ TRƯỚC MỌI VIỆC
> Sinh ra từ lỗi thật đã mắc trong workspace này. Vi phạm = lỗi nghiêm trọng. Áp dụng MỌI phiên, MỌI task.

1. **`git fetch` + so `origin/main` TRƯỚC khi fact-check trích dẫn.** (Lỗi đã mắc 08-04: repo local cũ 11 ngày
   → review kết luận nhầm "file A04 không tồn tại", "số dòng B02 lệch hàng loạt" — thực ra tài liệu ĐÚNG,
   local SAI. Suýt bắt sửa hàng loạt chỗ không sai.)
2. **Grep tài liệu Nhật phải thử NHIỀU dạng viết.** (Lỗi đã mắc 08-04: grep "9月" sót "2026/9" trong bảng
   lịch trại tập trung → kết luận nhầm "hạn tháng 9 không có nguồn"; nguồn nằm ở day2 dòng 148.)
   Cùng lý do: tìm theo CẢ mã lẫn tên (F-ES-05 ↔ 見守り通知), センサ ↔ センサー.
3. **Tách QUAN SÁT khỏi SUY ĐOÁN; không bịa nguyên nhân.** Suy đoán gắn nhãn "🔸giả thuyết — CHƯA kiểm chứng".
   Trong guide, box 💡 = diễn giải sư phạm, KHÔNG phải căn cứ — đừng trích 💡 làm bằng chứng với ai.
4. **Khối tiếng Nhật gửi khách phải SẠCH đồ nội bộ**: không CLD-xx/GW-xx, không đường dẫn repo, không 🔴,
   không xin thứ khách ĐÃ cung cấp (kiểm `old_eminel/00_sources.md` trước khi xin tài liệu).
5. **Sửa tài liệu xong PHẢI chạy review theo `requirements/README.md` §8 (3 vòng)** — kể cả "sửa nhỏ". Đợt 08-04 vòng review
   sau-sửa bắt được 13 lỗi do chính đợt sửa để sót (tàn dư "22 section", câu dẫn "Hai câu" khi đã 4 câu…).
6. **Đường dẫn khi fact-check**: `eminel_gw_project/...` trong tài liệu = `<SOURCES>/eminel_gw_project/...`
   (mặc định `../sources/`). Số dòng ứng với **commit ghi ở bảng meta đầu guide** (dòng 10) — đọc ở đó,
   đừng nhớ theo memory. Tài liệu khác (báo cáo điều tra) khai mốc riêng ở bảng 「Repo đối chiếu」 của chính nó.
7. **CẤM ghi token** (Notion/Slack/API) vào memory, log, output — hỏi user mỗi lần.
8. **Trích QA/Notion phải bám NGUYÊN VĂN + đủ định danh.** (Lỗi đã mắc 08-04: biến 「基本的には独立…方向」+vế ただし
   thành "không chung component" — diễn giải vượt nguồn; ghi "takahashi" trần gây nhầm với 高橋 phía 北ガス.)
   Chuẩn: nguyên văn trong 「」, người trả lời ghi đầy đủ "masao takahashi (mui)"/"swan (mui)", kèm ngày đọc
   trạng thái (回答中 là dữ liệu sống). KHÔNG push git khi user chưa yêu cầu (user dặn 08-04).
9. **Tài liệu knowledge base: cập nhật = VIẾT LẠI liền mạch, không chắp vá.** (User chỉnh 08-04 khi làm báo cáo
   batch.) Không thêm mục "bổ sung ngày X" cuối file, không rải mốc ngày giờ cập nhật, không giữ "nhãn cũ làm
   vết lịch sử" — thông tin mới thì reformat toàn bộ (hoặc ít nhất phần sửa) như viết mới với hiểu biết hiện tại,
   rồi chạy review 3 vòng (chi tiết dẫn chứng ・ chính xác ・ xác thực ・ dễ hiểu cho người mới đọc lần đầu).
10. **Tài liệu TỰ CHỨA — TUYỆT ĐỐI không bắt người đọc tra ngược; viết cho NGƯỜI, không phải cho máy.**
   (User chỉ đạo 08-06 khi tách báo cáo batch 3 tập.) Cụ thể: mã hiệu (CLD-xx/IF-NN/IF-4số/SVC-xx/spec…)
   chú giải tại chỗ MỖI lần xuất hiện theo ngữ cảnh lần đó; con trỏ §/#N kèm tóm tắt nội dung đích; bước làm
   ghi code đến từng layer/file (path đã kiểm tồn tại) + dòng "Vì sao/理由"; phán định nói rõ BỎ gì–GIỮ gì–
   THAY bằng gì; luồng xử lý đi từ code xuống tận bảng DB (grep `TABLE_*` xác minh, không đoán) và vẽ SƠ ĐỒ
   ASCII trong code block thay vì đoạn văn; kênh dữ liệu/IF nhắc đến phải có bảng chi tiết nguồn →
   trường chính (từ interface/schema trong code) → bảng đích → tác dụng nghiệp vụ; có bảng đối chiếu hệ cũ↔mới; **mỗi batch trong phần chi tiết theo
   template chuẩn (kết luận trước)**: Mục đích (1–2 câu) → Đề xuất BỎ–GIỮ–THAY đặt ngay đầu mục + khối
   "Vì sao đề xuất vậy" (3–4 gạch lý do) → sơ đồ luồng CŨ + trích code then chốt 3–8 dòng → chi tiết (bullet)
   → yêu cầu E-GW → sơ đồ luồng MỚI → cách làm từng bước (code + Vì sao) → kiểm thử;
   bố cục khoa học (heading/bullet/bảng, đoạn ≤5 dòng). Checklist 10 điểm nằm trong skill `3-step-review`
   Vòng 3; cấu trúc đầy đủ = `skillAI/create-investigation-report/TEMPLATE.md`. Áp cho CẢ bản JP lẫn VN.
11. **User gửi yêu cầu sửa/feedback → BẮT BUỘC đi qua skill `analyze-change-request` TRƯỚC khi sửa**:
   trích nguyên văn yêu cầu → phân loại (fix cục bộ / triệu chứng hệ thống / đổi thiết kế / mâu thuẫn)
   → tổng quát hóa thành quy tắc → tranh biện đa agent (MINIMAL vs HOLISTIC vs CRITIC, brainstorm chéo)
   → ĐỀ XUẤT giải pháp tổng thể cho user duyệt → thực thi nguyên khối (sửa gốc template/skill trước, áp
   xuống tài liệu sau). **Đồng thuận ngay + vá ngay = lỗi quy trình.** (Bài học 08-06: chuỗi vá đuổi theo
   từng yêu cầu tạo tài liệu "nồi lẩu", phải đập làm lại từ đầu theo template mẫu.)

---

## 🎯 TIẾN ĐỘ — HỎI "LÀM ĐẾN ĐÂU / HÔM NAY LÀM GÌ" LÀ ĐỌC Ở ĐÂY
> Cập nhật lần cuối: **2026-08-12 (guide v1.2 theo `460c671` + review 6 agent)** (chi tiết + việc dở dang: file ⭐ dưới bảng).

**[08-12] Trạng thái mới nhất:**
- **3 tập báo cáo batch ĐÃ NỘP cả 3** (hạn 14/08). Bản dùng = `submit_folder/2026_08_06/new_2/`. ⚠️ Thư mục `new/` (thế hệ 2 v4) **không còn trên đĩa** — chưa rõ cố ý hay nhầm; baseline mục 4 của skill `3-step-review` vẫn đang trỏ vào đó.
- `eminel_gw_project` pull **`fbc0af0` → `460c671`** (chỉ E02/E03 của app). **`onboarding_guide.md` → v1.2**, đối chiếu `460c671`: viết lại §5.5 (設定値運転 bị gỡ → 室温制御の有無 + 温度レベル), §5.6 (基本制御 → 冷房スケジュール中), §7.3 (bảng 23 section theo ステータス/劣後 đối khách, C1–C5 レビュー済, thêm mục B6), Phụ lục B.3/B.4, §0.3 (hai mốc kiểm).
- **Review 6 agent (⛔#5): 142 findings.** Guide đã vá hết (fence chẵn, 94 anchor/0 hỏng, 0 tàn dư). **`new_2/` còn 78 findings CHƯA vá — chờ user quyết** (4 [cao], đã có sẵn câu chữ thay thế).
- **3 phát hiện lật giả định** (chi tiết file ⭐): ① hệ cũ CÓ chiều gửi SFTP Xzilla (`PutLogFileCommand`, cron 00:00) → củng cố giả thuyết đích `/EST` ② spec [I] còn giữ 4 bảng của batch #5–#7 làm loại download nội bộ ③ **e-smart CÓ bảng tích luỹ `TABLE_DEVICE_*_HISTORY`** → kết luận "集計・計算系 không có gì dùng lại" phải xem lại trước khi điều tra.
- Bộ skill: `create-investigation-report` (TEMPLATE v4) ・ `analyze-change-request` (⛔#11) ・ `3-step-review` ・ `notion-connect` ・ `slack-connect` ・ `update-memory`.
- **[08-12 đợt 2] Bộ 4 batch `CSV/ZIPエクスポート系` theo FORMAT MỚI** → `submit_folder/2026_08_12/` (8 file: 4 batch × JP+VN). Format do user chỉ đạo, khác TEMPLATE v4: **1 batch = 1 file, chỉ điều tra hệ CŨ**, phán định để ở `requirements/summary_batch_migration_ja.md` (đã điền 4 dòng, chừa cột link Notion). Mẫu tham chiếu: `legacy-batch_CalcTenMinutesSensor_ja.md` của thành viên khác.
- **Bài học quy trình lớn nhất phiên này**: vá findings **theo FILE** làm vỡ tính nhất quán (lượt review 2 sinh thêm 50 findings, 14 [cao], trong đó 3 lỗi sai sự thật MỚI). Cách đúng = **vá theo KHỐI** (1 bản chuẩn/khối → viết lại toàn bộ file → `grep -c` + `diff` chứng minh đồng nhất). Chi tiết file ⭐ mục 8.3.
- `requirements/self_study_plan.md`: kế hoạch tự học 4 hạng mục — **hạng mục 1 mới xong bước 1** (§8-3 F-ES của v1.2).

**Đã xong (tích lũy):** bộ tài liệu học v1.1 (10 chương + 7 phụ lục, đối chiếu `788b438`, đã qua review nhiều vòng)
・ `qa_kitagas.md` (8+4 câu; **câu 1 đã đăng QAデータベース Notion, có trả lời tạm của mui: badge ngoài scope 2026, 回答中**)
・ **5 QA Notion đầu tiên (08-03→04) đã đọc & cập nhật vào guide/qa_kitagas + review §8 xong** — nội dung 5 QA: bảng ở guide 9.4
・ **báo cáo phán định 11 batch legacy (3 nhóm) vs e-smart/E-GW**: `submit_folder/2026_08_04/report_batch_3nhom_doichieu_esmart_egw.md`
— tối 04/08 nâng cấp: user clone `syp-eminelstandard-backend` (@dc39aa39) + `-web-admin` (@e550326), đều branch
`gw-syp-dev` (chưa có commit E-GW nào); điều tra code trực tiếp → báo cáo **viết lại hoàn chỉnh** (quy tắc ⛔#9),
mọi kết luận e-smart đã kiểm trên code; phát hiện **5 điểm tài liệu khảo sát `docs/eminel-smart/` lệch code**
(xem mục Giới hạn của báo cáo). Chuẩn cuối của báo cáo (user đặt): tóm tắt từng batch theo 3 nhóm ở đầu ・
chỗ "e-smart đã có" dán **trích code thật + giải thích từng nhóm** (16 khối, review xác nhận 16/16) ・
chỗ "tạo mới/bỏ" có **"Cách làm từng bước"** ・ đã qua nhiều lượt review 3 vòng, findings vá hết
・ **skill mới `skillAI/3-step-review/`** (quy trình review 3 vòng + thủ tục máy mới; đã tự review 2 agent
và viết lại; CLAUDE.md mục SOURCES đã cập nhật 4 repo git + 1 snapshot)
・ 3 skill cũ + workspace AGENTS folder (phiên 1)
・ **[08-05] Bản tiếng Nhật báo cáo batch cho mui**: `submit_folder/2026_08_05/旧EMINELバッチ移行判定報告書_3グループ11本.md` — bố cục 結論先出し, bỏ khối code (thay 🔍 ref), 対応ステップ đánh số khớp bản VN để đọc song song; review 2 lượt `3-step-review` (8+3 agent), vá 46 findings; **phát hiện 6 điểm nội dung bản VN còn dính** (ゆ抜く→ゆーぬっく, Node 20→24, 4/19 cron thông năm, DR schedule lúc 配信完了, #6 chỉ 7 loại 契約種別, emn_confirm append-only — chi tiết session 03 mục 3); 付録A = 6 điểm lệch tài liệu khảo sát.

**Việc tiếp theo (theo thứ tự):**
0. **Quyết định về 78 findings của `new_2/`**: vá vào bản đã nộp hay chỉ áp bài học cho tập sau. Kèm: xác nhận số phận thư mục `new/` → sửa baseline `3-step-review` mục 4.
0b. **Điều tra tiếp ~35/46 batch còn lại** — nhóm **集計・計算系**. ⚠️ **Trước khi bắt đầu phải kiểm lại 3 bảng `TABLE_DEVICE_{MONTHLY,DAILY,ACCUMULATED}_*_HISTORY`** (`template-dynamodb.yaml:105-111`): giả định cũ "e-smart không có gì dùng lại" đã bị code bác bỏ. Dùng skill `create-investigation-report`.
0c. ✅ Xong 08-12: guide v1.2 theo `460c671` (đã review 3 vòng + vá findings).
0d. **`requirements/self_study_plan.md`** — hạng mục 1 tiếp bước 2–6; đồng thời sửa mục "集計・計算系 e-smart không có gì dùng lại" theo phát hiện 08-12.
1. **Trả lời vế ただし của QA 独立デプロイ trên Notion** — danh sách "chức năng nên dùng tiếp": hệ cũ = không có;
   ESTA = push/point-PI/Xzilla-import/data-export (xem báo cáo batch §1; xác nhận trước nghĩa 「既存システム」).
2. Chốt nội bộ với **kihara** về Q5 (GW giữ trạng thái DR — báo cáo batch #4 cũng treo vào đây) → gửi `qa_kitagas.md`
   qua PM mui (quyết kèm Dự phòng 3/4 không).
3. **Theo dõi 5 trang QA đang 回答中** → khi 回答済: cập nhật các chỗ đánh dấu trong guide (grep "回答中") + B.1 theo README §9.
4. Hỏi mui xác nhận **đích của luồng export SFTP `/EST`** trong backend e-smart (≒「EMINELデータの共有」 F-ES-10?) — xem báo cáo batch §6.
5. Khi **IF-01/CLD-07** (định nghĩa 入出力 Xzilla) có spec → rà lại nhóm Xzilla của báo cáo batch (§4, gồm cả
   chiều xuất); khi review **spec [I]** → nêu 保持期間/loại dữ liệu download (**chưa có trong bảng QA — cân nhắc
   thêm câu hỏi**); danh sách việc-cần-xác-nhận đầy đủ: bảng §6 của báo cáo batch (8 mục).
6. **B06 マイホーム発電 ĐÃ ĐƯỢC VIẾT** tại `788b438` (kèm B04/B05/C01/C02/C03 có sửa) → cập nhật guide 7.3 + rà các mục guide trích B04/B05/C01–C03; cân nhắc guide 0.7 (legacy_eminel_docs đã có local).
7. Bối cảnh: hạn **tháng 9/2026 fix design+spec** vẫn treo trên 23/23 section chưa chốt + 10/10 spec admin DRAFT;
   3 vấn đề chặn SYP = CLD-01 / CLD-02 / GW-01.

---

> Folder ký ức để agent KHÔNG quên giữa các phiên. Đọc theo thứ tự khi bắt đầu lại.
> Cập nhật bằng skill `skillAI/update-memory/` cuối mỗi ngày làm việc.

| File (trong `memory/`) | Nội dung |
|---|---|
| `00_INDEX.md` | File này — QUY TẮC + tiến độ + địa chỉ (ĐỌC ĐẦU TIÊN) |
| `01_session_20260803_04_soanTaiLieu_review_fix_reorg.md` | [2026-08-03→04 sáng] Soạn guide v1.0 → review 13 agent → phát hiện repo local cũ & pull `788b438` → sửa toàn diện v1.1 → qa 8+4 câu → skill notion/slack → tái tổ chức AGENTS folder |
| `02_session_20260804_qaNotion_capNhatTaiLieu_baoCaoBatch.md` | [2026-08-04 chiều→tối] 5 QA Notion đầu → cập nhật guide/qa_kitagas + review §8 (21 findings) → báo cáo phán định 11 batch (điều tra cả code backend/web-admin e-smart, viết lại nhiều lượt theo chuẩn: trích code + cách làm từng bước + tóm tắt 3 nhóm) → skill `3-step-review` → quy tắc ⛔#8, ⛔#9 |
| `03_session_20260805_soanBaoCaoBatchJP_review2luot.md` | [2026-08-05 sáng→trưa] Soạn bản tiếng Nhật báo cáo batch cho mui (`submit_folder/2026_08_05/`) → review 2 lượt 3-step-review (8+3 agent, 46 findings vá hết) → 6 điểm nội dung bản VN còn dính + F-ES-10=Xzilla連携 + B06 đã được viết ở `788b438` |
| `04_session_20260806_tach3tap_templateV4_boSkillMoi.md` | [2026-08-06] Pull `fbc0af0` + phân tích 6 commit (app 13 file) → tách báo cáo thành **3 tập × JP+VN**, 3 thế hệ (`2026_08_06/` → `new/` v4 → **`new_2/` bản dùng**) → review độc lập bắt 2 lỗi [cao] (前々月, path bịa) → **bộ skill mới** `create-investigation-report` (TEMPLATE v4) + `analyze-change-request` (⛔#11) + sửa `3-step-review` → `requirements/self_study_plan.md` |
| ⭐ `05_session_20260812_guideV12_review6agent.md` | [2026-08-12] Pull `460c671` → **guide v1.2** (viết lại §5.5 mô hình sưởi mới, §5.6, §7.3 + mục B6, Phụ lục B.3/B.4) → **review 6 agent** (3 vòng guide + 3 cặp `new_2/`) = 142 findings, guide vá hết / `new_2/` chờ quyết → **3 phát hiện lật giả định**: hệ cũ có chiều gửi SFTP Xzilla ・ spec [I] giữ 4 bảng batch #5–#7 ・ e-smart CÓ bảng tích luỹ `TABLE_DEVICE_*_HISTORY` |
