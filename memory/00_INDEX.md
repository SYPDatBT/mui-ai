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
   (mặc định `../sources/`). Số dòng ứng với commit ghi ở đầu guide — hiện `788b438` (2026-08-03).
7. **CẤM ghi token** (Notion/Slack/API) vào memory, log, output — hỏi user mỗi lần.
8. **Trích QA/Notion phải bám NGUYÊN VĂN + đủ định danh.** (Lỗi đã mắc 08-04: biến 「基本的には独立…方向」+vế ただし
   thành "không chung component" — diễn giải vượt nguồn; ghi "takahashi" trần gây nhầm với 高橋 phía 北ガス.)
   Chuẩn: nguyên văn trong 「」, người trả lời ghi đầy đủ "masao takahashi (mui)"/"swan (mui)", kèm ngày đọc
   trạng thái (回答中 là dữ liệu sống). KHÔNG push git khi user chưa yêu cầu (user dặn 08-04).
9. **Tài liệu knowledge base: cập nhật = VIẾT LẠI liền mạch, không chắp vá.** (User chỉnh 08-04 khi làm báo cáo
   batch.) Không thêm mục "bổ sung ngày X" cuối file, không rải mốc ngày giờ cập nhật, không giữ "nhãn cũ làm
   vết lịch sử" — thông tin mới thì reformat toàn bộ (hoặc ít nhất phần sửa) như viết mới với hiểu biết hiện tại,
   rồi chạy review 3 vòng (chi tiết dẫn chứng ・ chính xác ・ xác thực ・ dễ hiểu cho người mới đọc lần đầu).

---

## 🎯 TIẾN ĐỘ — HỎI "LÀM ĐẾN ĐÂU / HÔM NAY LÀM GÌ" LÀ ĐỌC Ở ĐÂY
> Cập nhật lần cuối: **2026-08-05 (trưa — soạn & review bản tiếng Nhật báo cáo batch)** (chi tiết + việc dở dang: file ⭐ dưới bảng).

**Đã xong:** bộ tài liệu học v1.1 (10 chương + 7 phụ lục, đối chiếu `788b438`, đã qua review nhiều vòng)
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
0. **Chiều 05/08: user làm việc trực tiếp với mui** — dùng bản JP (batch #1–#11 + số bước 対応ステップ khớp
   bản VN để đối chiếu song song); diễn biến mới (QA 回答済, quyết định, feedback) → cập nhật tài liệu + memory.
   (Việc cũ "review bản VN trên máy khác" khi cần vẫn chạy skill **`skillAI/3-step-review/`** — baseline mục 4b.)
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
| ⭐ `03_session_20260805_soanBaoCaoBatchJP_review2luot.md` | [2026-08-05 sáng→trưa] Soạn bản tiếng Nhật báo cáo batch cho mui (`submit_folder/2026_08_05/`) → review 2 lượt 3-step-review (8+3 agent, 46 findings vá hết) → 6 điểm nội dung bản VN còn dính + F-ES-10=Xzilla連携 + B06 đã được viết ở `788b438` |
