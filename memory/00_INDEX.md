# MEMORY INDEX — Onboarding dự án EMINEL Gateway (E-GW)

## ⛔ QUY TẮC VẬN HÀNH — BẮT BUỘC, ĐỌC & TUÂN THỦ TRƯỚC MỌI VIỆC
> Sinh ra từ lỗi thật đã mắc trong workspace này. Vi phạm = lỗi nghiêm trọng. Áp dụng MỌI phiên, MỌI task.

0. 🥎 **ĐỐI ĐÁP KIỂU CATCH-BALL — QUY TẮC SỐ 0, ÁP CHO MỌI LƯỢT TRẢ LỜI** (user chốt 17/08).
   **Hỏi ngắn → trả lời ngắn (1–3 câu)**, đúng phạm vi câu hỏi rồi DỪNG; đi từ **khái quát → chi tiết**,
   chi tiết chỉ đưa khi user hỏi tiếp. Cần làm rõ thì **hỏi lại 1 câu**, không tự suy diễn.
   **CẤM: ① hallucinate** (khẳng định chưa kiểm chứng) **② hỏi ngắn – trả lời dài vô tận**
   **③ tự mở rộng phạm vi việc** khi user chưa yêu cầu. Bảng biểu/báo cáo dài chỉ khi user hỏi thẳng
   "rà soát / tổng hợp / báo cáo". Yêu cầu sửa lớn: nêu lại cách hiểu **thật ngắn** để user duyệt rồi mới làm
   (bản rút gọn của ⛔#11 — user KHÔNG muốn đọc kế hoạch dài).
   (Lỗi đã mắc 17/08: hiểu "đổi đường dẫn sang file `_ja`" thành "dịch toàn bộ ghi chú sang tiếng Nhật",
   viết lại 7 file rồi phải hoàn tác; và trả lời một câu xác nhận ngắn bằng cả bảng biểu dài.)
   **0b. CA CỤ THỂ — user gửi ảnh phiếu QA + hỏi 3 câu ("memory có nhận thức vậy không / guide có vậy không /
   cần sửa gì"): trả lời ĐÚNG 3 CÂU ĐÓ rồi DỪNG.** Có/không + chỗ nào ・ đã sửa gì. **CẤM thêm**: bảng so sánh
   phiếu này với phiếu khác, mục "N điều đáng nói", đánh giá chất lượng câu trả lời của mui, suy ra hệ quả
   nghiệp vụ, nhắc việc khác — user KHÔNG hỏi. Phát hiện phụ (nếu có giá trị thật) thì **ghi vào memory/guide**,
   không đổ vào chat. (Lỗi đã mắc 20/08: 4 lượt liền trả lời 3 câu hỏi ngắn bằng báo cáo dài có mục "Ba điều
   đáng nói" + bảng đối chiếu phiếu; user phải chặn: *"không cần đánh giá phiếu trả lời, chỉ cần làm đúng yêu cầu"*.)
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
12. **MỌI file QA sống ở `submit_folder/qa/` — tên file = mô tả nội dung hỏi + NGÀY THÁNG.** (User chỉ đạo 08-13,
   đã tự tay dời `qa_kitagas.md` từ `requirements/` và `qa_batch_csvzip.md` từ `submit_folder/2026_08_12/` vào đó.)
   Quy ước tên: `qa_<chủ-đề>_<YYYYMMDD>.md` — ví dụ `qa_batch_shukei_20260815.md`. **Không** rải file QA theo
   thư mục ngày nộp như tài liệu điều tra, **không** để trong `requirements/`. Hai file cũ giữ nguyên tên
   (chưa có ngày) vì đã bị nhiều tài liệu trích dẫn — quy ước ngày áp cho file TẠO MỚI từ 08-13.
13. **grep phủ định phải MỞ CẢ FILE NÉN** (`.tgz`/`.zip`/`.tar.gz`): giải nén ra thư mục tạm rồi grep, đừng
   grep repo trần rồi kết luận "0 hit". (Lỗi đã mắc: review 08-12 báo *"shell flock không có căn cứ, grep
   `flock` = 0"*; thực tế `flock` nằm trong `.sh` **bên trong** `cron実行用シェルスクリプト/eminel-mng-webap.20240909.tgz`
   — 08-13 giải nén thấy ngay. Suýt vá một khẳng định ĐÚNG thành SAI.) Hệ quả của ⛔#2, và: **finding do agent
   review sinh ra vẫn phải kiểm chứng lại trên nguồn trước khi vá** — agent sai thì vá làm hỏng tài liệu đúng.
14. **Trước khi tin số dòng/nội dung trên đĩa: `git log -1` chính repo đó.** Ghi chép "đã pull X" của phiên
   trước KHÔNG đủ tin. (Phát hiện 08-13: working tree `eminel_gw_project` đứng ở `788b438` suốt từ 03/08 trong
   khi memory ghi đã pull `fbc0af0`→`460c671`; reflog chỉ có 1 lần merge. Các phiên đó đọc bằng
   `git show <commit>:<path>` nên kết luận vẫn đúng — nhưng ai tin ghi chép mà đọc thẳng file trên đĩa thì sai.)
15. **Việc NẶNG (fan-out nhiều agent / phase dài) phải SỐNG SÓT được qua sập trần usage — phòng thủ 2 lớp,
   tự làm không đợi user nhắc.** ① **Chốt memory TRƯỚC khi phóng**: cập nhật 🎯 của 00_INDEX + file session ⭐
   (đã xong gì ・ đang chạy gì ・ kết quả nằm ở file/journal nào — đường dẫn cụ thể ・ bước tiếp theo đánh số),
   đủ để phiên mới bootstrap là tiếp tục ngay. ② **CHIA việc thành KHỐI NHỎ TỰ-HOÀN-CHỈNH**: mỗi khối xong là
   kết quả nằm trên ĐĨA + memory nhích theo, rồi mới sang khối sau — không dồn thành một lượt chạy dài mà kết quả
   chỉ có khi TẤT CẢ xong; khối chưa chạy phải chạy-lại-được độc lập (script/prompt lưu sẵn ra file, ghi rõ
   khối nào xong khối nào chưa); sập giữa chừng = mất tối đa 1 khối. Kết quả trung gian (findings, verdict)
   không bao giờ sống trong chat. **Định lượng (user chốt 08-16): TRƯỚC khi phóng phải ƯỚC LƯỢNG token theo
   `notes/usage_budget.md` (đơn giá hiệu chỉnh từ số thật) — ước lượng > 20% ngân sách gói Max 20x
   (= ~600k token/khối theo giả định 3M/cửa sổ 5h) → BẮT BUỘC chia khối; chạy xong ghi số thật vào ledger
   của file đó để hiệu chỉnh dần.** (Lỗi suýt mắc 08-16: trần chi tiêu tháng sập GIỮA lúc 3 workflow ~30 agent
   đang chạy — P2 một lượt 2,21M token ≈ 74% cửa sổ; vòng đối kháng chết nửa chừng; may user vừa yêu cầu chốt
   memory vài phút trước nên không mất gì. Cùng họ với bài học 78 findings 08-12 chỉ nằm trong chat → MẤT.)

---

## 🎯 TIẾN ĐỘ — HỎI "LÀM ĐẾN ĐÂU / HÔM NAY LÀM GÌ" LÀ ĐỌC Ở ĐÂY
> Cập nhật lần cuối: **2026-08-20 — ✅ PHẠM VI SYP ĐÃ CHỐT (QA Notion No. 10, 完了) → guide có bảng 担当 chính thức**. (19/08: chốt bản nộp báo cáo tái cấu trúc source app. 18/08: guide lên v1.3, đối chiếu mốc `1100487`.) Đợt review tài liệu team `2026_08_13/` đã đóng từ 17/08 (bàn giao sẵn sàng, phần còn lại thuộc user/member — xem khối [08-17]).

**[08-20] ✅ CHỐT PHẠM VI ĐỐI ỨNG CỦA SYP — nguồn: Notion QAデータベース trang 「SYP開発範囲の確認」 (No. 10):**
- **担当 đã được mui xác nhận** (回答者 **swan (mui)**, 回答 **2026-08-13**, ステータス **完了**; 質問者 **Nguyen Van Tung (SYP)**, 起票 08-12; 回答内容 nguyên văn 「認識に相違ないです。」):
  **mui Lab** = 7-1 E-GW機能（ファームウェア） ・ 7-2 GW管理クラウド機能 │ **SYP** = 7-3 EMINEL-smartサーバー機能 ・ 7-4 管理画面機能 ・ **モバイルアプリ**.
- ⚠️ **GW管理クラウド là của mui Lab, KHÔNG phải SYP** — chỗ dễ hiểu sai nhất, vì v1.2 §1-2 gộp nó chung một hàng với EMINEL-smartサーバー ("(GW管理クラウド含む)"). Phải tách: **対象範囲** (dự án có làm gì) ≠ **担当** (ai làm).
- **Guide vá 6 chỗ, `+93/−13` dòng** (0 liên kết hỏng ・ 70 fence chẵn ・ bảng khớp cột): §1.6 tách bảng ①対象範囲 / **②担当 (mới)** + đóng đoạn "chưa chốt" ・ **§6.1 bảng 4 nhóm mã thêm cột 「7-x」+「担当」** (F-GW/F-MC = mui, F-ES/F-AD = SYP; app dùng mã **F-AP**, ngoài 7-1〜7-4 nhưng vẫn SYP làm) ・ §9.4 thêm khối ✅ chốt + hạ nhãn 🔸 (đánh giá 「関与が薄そう」 camp 6/25 nay chỉ còn giá trị lịch sử) ・ §1.3 + Phụ lục E.2.
- ⚠️ **[08-20 lượt 15] Phiếu QA No. 25 「エコ暖房ポイントの実施範囲、およびDR終了方式の確定について」 — `回答中`, 回答内容 「１．対応範囲内 ２．後回し」.** 質問者 Bui Trong Dat, 起票 08-17 13:24 (**cùng lúc với No. 24**), cập nhật 08-19 18:07, 回答者 trống.
  - 🔴 **CÂU 2 「後回し」 LÀ LOẠI CÂU TRẢ LỜI NGUY HƠN "CHƯA TRẢ LỜI"** — nó **đóng cửa việc chờ mà không gỡ được phụ thuộc kỹ thuật**. Phương án kết thúc DR (Phụ lục C **#5**) quyết định **firmware 2026 có phải xây năng lực lưu trạng thái hay không**: phương án A (server ra lệnh) lo **mất mạng không gửi được lệnh kết thúc**; phương án B (GW tự kết thúc) đòi **GW lưu trạng thái** — mà tài liệu ghi rõ 「GW側で保存はしたくない」 (`11_business_process/readme.md:839`, đã kiểm 08-20).
    → **Việc ĐỔI CHỦ THỂ, không mất đi**: từ *"chờ 北ガス chọn A/B"* thành **"nội bộ mui/SYP tự quyết tư thế firmware"** — xây sẵn năng lực lưu trạng thái (giữ đường mở cho B) hay không xây (khoá vào A). **Chốt với kihara**, đây là việc số 7 của hàng đợi, nay càng cấp.
    → 🔸 **Hai cách đọc, CHƯA biết cách nào đúng**: ① firmware thực ra không cần biết ngay ⇒ lập luận "chặn 2026" của guide quá thận trọng ② 「後回し」 được đưa ra **mà chưa để ý phụ thuộc firmware** ⇒ **rủi ro phải nêu lại trước tuần implement**.
  - 🟡 **CÂU 1 「対応範囲内」 chỉ đóng MỘT NỬA Phụ lục B.2.** エコ暖房ポイント = cơ chế cấp điểm riêng cho sưởi tiết kiệm (hệ cũ: **250 điểm/tháng** cho hộ có nhiệt độ cài đặt TB tháng **≤22℃**), trong tài liệu quản lý nó đi kèm nhóm **tư vấn tiết kiệm** (CLD-06: 「7種**＋エコ暖房ポイント**」), **không** đi kèm nhóm điểm thưởng chung. ⇒ củng cố cột **tư vấn tiết kiệm** của B.2 (nghiêng về 必須 của `22_decisions`, tức bảng chức năng mới là cái lỗi thời), **KHÔNG** trả lời cột **điểm thưởng** (`A03`).
  - 🔸 **CHỖ CẦN LÀM RÕ (chưa kiểm chứng)**: bảng 劣後 của phiếu No. 12 có dòng **`A3 ポイント` = 全部 劣後**, đặt cạnh 「エコ暖房ポイント＝対応範囲内」 thì **nhìn như lệch**. Giả thuyết: **hai thứ khác nhau** — `A3` là chức năng điểm tổng quát trên app, エコ暖房ポイント là khoản thưởng thuộc mạch tư vấn (`C05`). Chưa ai xác nhận, và phiếu No. 12 chưa được trả lời nên chưa đóng được. **Khi giải thích cho người khác: đừng nói gộp "điểm thưởng đã trong phạm vi".**
  - → guide: **Phụ lục B.2 thêm mục 🟡** + hạ 🔴→🟠 ở bảng tóm tắt ・ **Phụ lục C #5 viết lại** + **khối ⚠️ MỚI dưới bảng** (bảng 2 phương án A/B + nguyên văn dòng 839 + bảng "trước/sau khi có 後回し" + 2 cách đọc) ・ §0.3 (14→**15 phiếu**) ・ §9.4 bảng nhịp thêm No. 25.
- ⭐ **[08-20 lượt 14] Phiếu QA No. 24 「見守り通知の実装要否、およびXzillaへのアプリログ送信の継続要否について」 — `回答中`, ĐÁP ĐỦ CẢ 2 CÂU, dứt khoát.** 質問者 Bui Trong Dat, 起票 08-17 13:24, cập nhật 08-19 18:06, 回答者 trống. 回答内容: 「**１．実装する必要 ２．継続・利用しません**」.
  - ✅ **CÂU 1 ĐÓNG MỘT MỤC 🔴 CAO**: 見守り通知 = **PHẢI LÀM**. Đóng cả **Phụ lục B.3** (mâu thuẫn 🔴 Cao) lẫn **CLD-05** (chênh **0–1 người-tháng**). Quan trọng hơn con số: **logic phán đoán trông nom nằm ở GATEWAY** ⇒ nếu câu "không làm" đến muộn thì firmware đã viết sẽ thành công bỏ. Nay hết rủi ro đó. Phần "Nghi ngờ" cũ của B.3 (*bảng chức năng + requirement giả định "sẽ làm"*) **được xác nhận là đúng**.
  - ⛔ **CÂU 2 — QUYẾT ĐỊNH LOẠI BỎ**: **BỎ chiều gửi log app lên Xzilla** (hệ cũ chạy bằng `PutLogFileCommand`, cron 00:00). ⇒ **không port**, không dựng đường SFTP xuất log, **trừ hạng mục này khi đếm số batch phải làm**. Đây là chiều **NGƯỢC** với mọi chỗ khác trong guide (mọi chỗ khác là **nhận** từ Xzilla) — guide trước đó **không có một dòng nào** về chiều này.
  - 💡 **Nguyên tắc ghi vào guide**: phải ghi lại cả quyết định "**không làm**", kẻo người sau điều tra hệ cũ, thấy luồng đó, rồi **tưởng mình bỏ sót** → điều tra lần hai vô ích. Cùng họ với quyết định bỏ `EMS-SP番号` (phiếu No. 8).
  - → guide: **§4.4③ viết lại** (thêm khối ✅ PHẢI LÀM + khối ✅ BỎ chiều gửi log) ・ **Phụ lục B.3 thêm mục "ĐÃ ĐÓNG"** + hạ 🔴 ở bảng tóm tắt ・ bảng CLD ở §8.x ghi 「đã trả lời, nhưng giấy chưa cập nhật」 ・ dòng **E2** trong bảng spec ・ §0.3 (13→**14 phiếu**) ・ §9.4 bảng nhịp thêm No. 24.
  - ⚠️ **Giữ B.3 trong bảng mâu thuẫn** dù đã có câu trả lời: phiếu còn `回答中`, và `CLD-05` trong `20_open_issues.md` **chưa cập nhật trên giấy** — ai đọc riêng file đó vẫn thấy 🔴.
- 🔴 **[08-20 lượt 13] Phiếu QA No. 19 「エネアドバイス（全19種）を「7種＋エコ暖房ポイント」へ統廃合する件」 — `確認中`, ô trả lời TRỐNG.** 質問者 Nguyen Van Tung, 起票 08-13 17:22, cập nhật 08-19 18:02, 回答者 trống. Đây là **Phụ lục C #8** của guide.
  - ⭐ **PHÁT HIỆN MÂU THUẪN MỚI → Phụ lục B.6 (mục MỚI): code 19 ↔ tài liệu quản lý ~15.** Guide trước ghi **15 loại** ở 2 chỗ lời của chính guide (theo CLD-06 「約15種」). **Đếm trực tiếp trên code, kiểm 08-20: 19 loại** — `PublishRegularEcoMissionsCommand.php` dòng 74–135 có `case 1`→`case 19`, và `ConRegularEcoMissionsSeed.php` dòng 24–301 có **đúng 19 bản ghi**. Repo `legacy_eminel_docs` @ `ccd8f56`.
  - **Lệch 4 loại.** Chữ 「**約**」 (khoảng) cho thấy CLD-06 là số ước lượng ⇒ không hẳn là lỗi, nhưng **không được lấy tài liệu quản lý làm căn cứ**. Nguy hiểm: ai lập kế hoạch theo 15 sẽ **bỏ sót 4 loại**. **B.6 là mục mâu thuẫn ĐẦU TIÊN thuộc loại "tài liệu ↔ CODE"**, 5 mục cũ đều là "tài liệu ↔ tài liệu".
  - ⚠️ **Bẫy đáng ghi**: phiếu nêu rõ requirement `C05_energy_advice.md` có ô 「要確認事項」 = 「なし」 và **không tìm thấy tài liệu nào định nghĩa 7 loại mới** ⇒ **ô 要確認事項 trống KHÔNG đồng nghĩa đã chốt**. Trên giấy trông như xong, thực tế còn trống.
  - **3 câu của phiếu, đều không tự suy ra được**: ① danh sách 7 loại mới (tên・điều kiện phát・câu chữ・điểm) ② trong 19 loại: loại nào bỏ, loại nào gộp vào đâu, **tiêu chí gộp** ③ các loại dựa trên so sánh nhóm hộ (gom theo loại nhà/loại hợp đồng, **tối thiểu 10 hộ/nhóm**) có giữ ngưỡng cũ không.
  - → guide: **§4.4② viết lại** (19 thay 15 + dẫn nguồn code + khối phiếu No. 19) ・ **Phụ lục B.6 MỚI** + bảng tóm tắt đầu Phụ lục B ・ **Phụ lục C #8 viết lại** ・ §0.3 (12→**13 phiếu**) ・ §9.4 bảng nhịp thêm No. 19 + gộp nhóm `確認中` thành 2 phiếu.
- 🟡 **[08-20 lượt 12] Phiếu QA No. 14 「過去データダウンロードの必要遡及期間についてご確認」 — `回答中`, 回答内容 「24か月です」.** 質問者 Bui Trong Dat, 起票 08-13 12:29, cập nhật 08-19 18:02 (🔸 suy từ nhãn "Wednesday"), **回答者 trống**. **Guide trước đó gần như KHÔNG có gì** về chủ đề này (chỉ 1 chỗ nhắc `データ保持期間` trong danh sách phi chức năng SVC-03).
  - ⭐ **Nội dung kiến trúc đáng nhớ nhất**: hệ **cũ** làm sẵn ZIP định kỳ đẩy ra server và **không có quy trình xoá ZIP** ⇒ thực tế truy ngược được **nhiều năm**, dù DB gốc xoá rất sớm (機器状態情報 **8 ngày** ・ 1時間値 **14 ngày** ・ 1日値 + 1日値平均 **2 tháng**). Hệ **mới** (`F-AD-09`) **sinh file từ DB lúc bấm**, không làm sẵn ⇒ **thời hạn lưu của DB thành TRẦN CỨNG**. Muốn xa hơn thì phải **thiết kế thêm cơ chế archive riêng** ⇒ đây là **tiền đề chốt spec**, không phải tham số chỉnh sau.
  - ⚠️ **Đừng đọc 「24か月」 là đã xong**: ① trạng thái mới `回答中` ② con số 24 tháng **vốn do SYP tự đề xuất** kèm nhãn T.B.C — câu trả lời là **xác nhận giá trị tạm**, không phải số tính ra từ nghiệp vụ ③ **phiếu hỏi 3 câu, chỉ câu 1 được đáp**.
  - → guide **§7.4⑦ (mục MỚI)** + **Phụ lục C #11b (hàng MỚI)** + §0.3 (11→**12 phiếu**) + §9.4 bảng nhịp thêm hàng No. 14 + sửa nhóm "ngoài đợt" thành 3 phiếu.
- 🟡 **[08-20 lượt 11] Phiếu QA No. 8 「GW-IDと顧客・契約情報の連携方法について」 — `回答中`, comment masao 08-19, NỘI DUNG NGHIỆP VỤ MỚI.** 起票 08-05 16:03; ô `回答内容` chỉ ghi 「**コメントに記載**」 (ca mạnh nhất của bẫy ⑤ — chính ô trả lời trỏ sang Comments); **回答者 trống**.
  - ✅ **CHỐT cách gắn GW với khách**: **`GW-ID` ↔ `TagTag ID`**, gắn **đúng lúc pairing + đăng ký GW** từ app đã đăng nhập TagTag, do **EMINEL-smartサーバー** giữ và v1.2 L124 gọi thẳng là **マスター** (= việc của SYP).
  - ⛔ **QUYẾT ĐỊNH LOẠI BỎ**: **KHÔNG dùng `EMS-SP番号` + mật khẩu** để xác thực/gắn kết. Đây là cách của **hệ cũ** ⇒ thiết kế onboarding **không được** mang bước đó sang. Khớp chủ trương camp 6/25 「レガシーのやり方をそのまま写さず」. Guide: **Phụ lục A** entry `EMS-SP番号` đã thêm ⛔.
  - 📌 masao dẫn **5 dòng** làm căn cứ (v1.2 L124/L86/L531/L117 + `11_business_process/readme.md` L83) — **đã kiểm lại tại `1100487`, khớp cả 5**. Đáng học: đây là kiểu trả lời QA tốt nhất từng nhận (kết luận + dẫn chứng file:dòng).
  - → §5.2 thêm mục ✅ 「Điểm này ĐÃ ĐƯỢC CHỐT — cách gắn GW với khách hàng」: nguyên văn comment + dịch + bảng 3 điều rút ra + bảng 5 dòng căn cứ + **sơ đồ ASCII luồng đăng ký**. §0.3: 10→**11 phiếu**.
- 📊 **[08-20] BẢNG 47 BATCH × PHÁN ĐỊNH e-smart**: `submit_folder/2026_08_20/bang_47batch_phandinh_esmart_vn.md` — giữ nguyên cấu trúc `04_バッチ一覧.md` (theo server + nhóm, giữ tên class và 概要), thêm 3 cột: **e-smart có sẵn / phán định / lý do**. Kiểm: 47/47 dòng, 5 cột đều nhau, tổng ký hiệu khớp.
  - **Kết quả: chỉ 9/47 batch e-smart đã có thứ tương đương.** ✅ dùng lại nguyên trạng **3** (`DispatchPushMessages` ・ `SendAlertLogMail` ・ `HashPassword`) │ 🔶 có nhưng phải sửa **2** (`ControlDrOperation` — thêm nhánh E-GW, nhưng DR là 劣後 2027 ・ `WatchNotification` — chỉ còn "có chuyển động thì thông báo ngay") │ ⚠️ có mà **KHÔNG dùng lại được 4** (`DeleteLogicalDeletedDevices` cơ chế khác hẳn ・ `RankingCreation` trùng tên bản chất khác ・ `TerminateOutdatedDeviceControlJobs` mất 1 bảo đảm UX ・ `DeleteData` thiếu cơ chế hạn lưu) │ ⭕ vấn đề tự tiêu biến **3** │ ❌ phải làm mới **25** │ 🔻 bỏ vì đổi cách làm **4** │ 🚫 **2** │ — ngoài phạm vi SYP **4**.
  - ⚠️ **Cạm bẫy đã ghi rõ trong bảng**: nhóm ⚠️ có cột "chức năng tương ứng ở hệ mới" **không trống** nên đọc nhanh tưởng đã có sẵn — nhưng phán định là **không dùng được**. Và `通知監視` (`WatchNotification`) **≠** `見守り` — đừng vì thấy cái trước "đã có một phần" mà tưởng 見守り cũng có (見守り vừa chốt **PHẢI LÀM**, phiếu No. 24).
  - ⭐ **PHỤ CHÚ GIẢI ĐƯỢC MỘT CÂU ĐỐ SỐ LIỆU**: ba nguồn ghi ba con số cho cùng một thứ, và **không mâu thuẫn — đếm ba thứ khác nhau**: **19** = số mã mission (`case 1`→`19` + 19 bản ghi seed) ・ **11** = số **FILE** Publisher mà `04_バッチ一覧.md` đếm, trong đó **2 file là nền** (`EcoMissionPublisher` lớp cơ sở + `...Option`) ⇒ **9 lớp thật sự phát tư vấn** ・ **約15** = ước lượng của CLD-06. ⇒ **Khi trích dùng 19 + dẫn nguồn code** (đã thành Phụ lục B.6 của guide).
- 📄 **[08-20] BÁO CÁO NGÀY**: `submit_folder/2026_08_20/report_20260820_10phieuQA_capNhatTaiLieu_vn.md` — 8 mục, gom toàn bộ đợt rà 10 phiếu QA + bảng nhịp làm việc của mui + 5 cái bẫy QAデータベース + 3 mục mới Phụ lục C + danh sách 11 commit. ⚠️ **File NỘI BỘ tiếng Việt** — nộp cả thư mục là lộ đồ nội bộ (⛔#4); muốn gửi mui thì soạn bản JP riêng.
- 🟡 **[08-20 lượt 10] Phiếu QA No. 6 「エラー種別（重篤／軽微）の判定条件についてご教示ください」 — `回答中`, và đây là phiếu ĐÁNG GIÁ NHẤT trong 10 phiếu.** 質問者 Bui Trong Dat, 起票 08-03 17:33; 回答内容 chỉ ghi 「**要仕様検討中**」; **回答者 trống**; 更新日時 **2026-08-19 10:43** (mới nhất trong tất cả).
  - ⭐ **CÂU TRẢ LỜI THẬT NẰM Ở PHẦN `Comments`** — lần đầu gặp Comments có nội dung. masao takahashi (mui), **08-19**: 「まだ、エラー内容を洗い出せていないですので、**結構後になる**かと思います。」 (*chưa liệt kê được nội dung lỗi nên sẽ khá muộn*). Đọc riêng ô 回答内容 thì KHÔNG biết điều này → thành **bẫy ⑤** của Phụ lục E.2: **phải đọc cả Comments**, và **tên người trả lời có thể chỉ có trong Comments** khi ô 回答者 trống.
  - 🔴 **ĐẢO một giả định của guide**: Phụ lục C **#1** (mục chặn việc SỐ MỘT) trước ghi 「Hỏi ai: 北ガス」. Thực tế **điểm nghẽn ở chính mui** — họ chưa lập được danh mục lỗi. ⇒ Không gộp câu này vào bảng QA gửi khách nữa. Việc cần làm: **bàn phương án làm trước phần không phụ thuộc phân loại lỗi**, vì màn hình **C (quản lý E-GW) thuộc phạm vi 2026** mà đang bị chặn.
  - → Vá 4 chỗ: **§7.4 thêm mục ⏳「Đã hỏi rồi — và mui trả lời là 'còn lâu'」** (nguyên văn comment + 3 điều rút ra) ・ **Phụ lục E.2 bẫy ⑤** ・ **Phụ lục C #1** (thêm phiếu No. 6 + đổi cột "Hỏi ai" thành 「mui trước, rồi 北ガス」) ・ §0.3 (9→**10 phiếu**).
- 🔶 **[08-20 lượt 9] Phiếu QA No. 12 「2027年劣後機能の確認」 — CHƯA CÓ TRẢ LỜI**, ステータス **確認中**, ô 回答内容 **trống** (質問者 Nguyen Van Tung, 起票 08-12 17:41, 更新 08-12 17:46; kiểm 08-20 vẫn vậy).
  - ⚠️ **GIÁ TRỊ ステータス THỨ TƯ: `確認中`** — guide chỉ có 回答中/回答済/完了. Khác `回答中` ở chỗ: `回答中` **đã có nội dung** để đọc tham khảo, `確認中` **trống hoàn toàn** = chưa ai bên mui chạm vào. Đã thêm vào bảng Phụ lục E.2.
  - 🔴 **NGOẠI LỆ của kết luận "mui dọn QA theo đợt"**: phiếu này lập **08-12**, tức **TRƯỚC** đợt mui đóng 8 phiếu ngày 08-13 — nhưng bị **để lại**. Không phải "chưa tới lượt" mà là **bỏ qua có chọn lọc** ⇒ phải **thúc**, đừng chờ.
  - → **Phụ lục C thêm 3 hàng #13–#15** + bảng phân loại "kiểu bị chặn": #13 đã hỏi đang chờ (No. 12) ・ #14 mức độ độc lập server (phiếu No. 2 đóng mà không nói ⇒ mở phiếu MỚI) ・ #15 vế `ただし` (**SYP** phải trả lời). Ba câu này **không phải hỏi 北ガス** như 12 câu cũ.
  - → Phụ lục **B.1** thêm khối 「Diễn biến 08-12」: No. 12 hỏi **toàn bộ danh sách 劣後 2027**, rộng hơn câu huy hiệu của No. 5.
- **[08-20 lượt 8] Phiếu QA No. 9 「設計書の最終成果物のファイル形式について」 完了** (質問者 Nguyen Van Tung, 起票 08-10 17:06, chốt 08-13 12:34; **回答者 để trống**). 回答内容: 「**画面：excel / API：markdown**」. → **Guide có mục MỚI §7.7 「設計書 — định dạng file của bản giao nộp」** + bản đồ 6 tầng (§7.1) thêm cảnh báo: sáu tầng đó là **trong repo**, còn **設計書 là thứ SYP GIAO NỘP và không nộp bằng markdown trong repo**. ⚠️ **Không suy rộng**: câu trả lời chỉ nói về 設計書, `3_requirements`/`4_spec` vẫn là markdown trong git.
- **[08-20 lượt 7] Phiếu QA No. 7** — xem khối [08-18] (task tái cấu trúc app), không thuộc guide.
- **[08-20 lượt 6] Phiếu QA No. 5 「バッジ・ランクは2026年度対応スコープでしょうか」 đã 完了** (chốt 08-13 12:28, 回答者 masao takahashi, 起票 08-03 17:33; 回答内容 「今の所、2026年スコープ外です」 — không đổi một chữ). Đây là **câu 1 của `qa_kitagas.md`**. Vá **4 chỗ**: §6.x (mục huy hiệu A4) ・ **Phụ lục B bảng mâu thuẫn hàng B.1** (🔴 Cao → 🟠 Vừa, ghi phiếu No. 5 完了) ・ **Phụ lục B.1 phần Diễn biến** ・ §0.3 bảng mốc kiểm (5→**6 phiếu**).
  - ⚠️ **KHÔNG xoá B.1 khỏi bảng mâu thuẫn**, dù phiếu đã đóng. Hai lý do phải giữ: ① chữ 「**今の所**」 (*hiện tại thì*) nằm trong nguyên văn — mốc thời điểm, không phải kết luận vĩnh viễn (cùng loại 「基本的には」 của phiếu No. 2) ② đây là trả lời của **mui**, **không phải 北ガス xác nhận** — mà người quyết phạm vi là 北ガス. Chữ trên giấy `A04_badge_rank.md` vẫn viết toàn bộ vào 「26年対応スコープ」.
  - 📌 **Nguyên tắc rút ra, đã ghi vào §0.3**: **phiếu 完了 ≠ hết dè dặt.** Đóng phiếu không thêm chữ nào vào câu trả lời ⇒ chữ nhượng bộ và chuyện "mui trả lời ≠ khách xác nhận" vẫn còn nguyên.
- **[08-20 lượt 5] Phiếu QA No. 4 「旧EMINEL調査範囲（conciergesv/eminelsv）とhemssv対象外の確認」 đã 完了** (chốt 08-13 12:28, 回答者 swan; `回答内容` **không đổi một chữ**, không có vế `ただし`). Vá **5 chỗ**: §4.2 dòng 🔍 (thêm No. 4, 回答中→完了) ・ §0.3 bảng mốc kiểm (4→**5 phiếu**) ・ §9.4 bảng hàng 4 ・ §9.4 đoạn dưới bảng (bỏ "phiếu ? cuối cùng", đổi thành khối 📌 **nhịp làm việc của mui** + bảng 5 phiếu × 起票/chốt) ・ §7.x bản nháp admin (dòng 「Hướng chung với E-Smart… (còn 回答中)」 → ✅ **chốt qua phiếu No. 3**).
  - ⇒ **BẢNG 4 PHIẾU CỦA §9.4 NAY SẠCH — cả bốn 完了.** Bốn kết luận đều là **kết luận đã đóng**: app là 開発対象 ・ server hướng độc lập (kèm 「基本的には」) ・ admin chung source+deploy ・ phạm vi điều tra hệ cũ = conciergesv+eminelsv, hemssv ngoài phạm vi.
  - 🔸 **Vẫn giữ nhãn giả thuyết** (đóng phiếu không thêm thông tin): "m2-cloud" có phải tên hiện thực của `GW管理クラウド` hay không — §4.2 vẫn ghi CHƯA kiểm chứng, cần hỏi.
- **[08-20 lượt 4] Phiếu QA No. 3 「管理画面は独立か共通か（切替モード追加）の確認」 đã 完了** (chốt 08-13 12:28, 回答者 masao takahashi; `回答内容` **không đổi một chữ**, **không có vế `ただし`**). Vá **6 chỗ**, trong đó **1 chỗ NGOÀI guide**: `requirements/self_study_plan.md` dòng 83 (Hạng mục 3) còn ghi 「回答中」 → đã sửa thành phiếu No. 3 完了.
  - ✅ **管理画面 = chung source code + chung deploy với E-Smart, ĐÃ CHỐT** — lý do mui nêu: **cùng một lớp người vận hành dùng**. Câu trả lời này **không kèm chữ nhượng bộ nào**, khác hẳn phiếu No. 2 (có 「基本的には」). ⇒ **Thêm màn hình E-GW vào chính repo `syp-eminelstandard-web-admin`**, không repo mới, không deploy riêng.
  - ⚠️ **Đè lên ghi chú camp 6/25**: camp ghi 「環境変数／ビルド設定で切り替え」 (hai bản deploy tách nhau, chuyển bằng biến môi trường) — cách hiểu đó **SAI với 管理画面**; phần nói về **app** của ghi chú camp thì vẫn đúng (build 2 app riêng, nay là nền cho task tái cấu trúc source app).
  - 📌 **Nhịp đóng phiếu, nay 4 mẫu**: No. 1 (起票 08-03 **17:30** → chốt **12:27**) ・ No. 2 (**17:31** → **12:28**) ・ No. 3 (**17:32** → **12:28**) ・ No. 10 (08-12 16:17 → **12:28**). Dat lập 3 phiếu **liên tiếp từng phút** chiều 08-03; mui **để nguyên 10 ngày rồi đóng cả loạt trong 2 phút**.
- **[08-20 lượt 3] Phiếu QA No. 2 「旧Eminel基盤継承＋…独立デプロイの確認」 đã 完了** (chốt 08-13 12:28, 回答者 swan). Guide vá **8 chỗ**: §0.2 ・ §0.3 ・ §1.2 ・ §8.x tiền đề 「同一コードベース」 ・ §9.4 (bảng + cảnh báo + điểm 2 viết lại 3 tầng + **mục mới**).
  - ✅ **Hướng làm server E-GW thành hệ ĐỘC LẬP với E-Smart = ĐÃ CHỐT.** ⚠️ Nhưng chữ 「基本的には」 (*về cơ bản là*) vẫn nguyên trong nguyên văn — đóng phiếu không xoá nó, **cấm đọc thành "độc lập tuyệt đối"** (⛔#8). ❌ **Mức độ** độc lập (chung library/source?) vẫn chưa ai nói → xem việc **6b**.
  - 🔴 **MỘT CÂU HỎI CỦA MUI ĐÃ RƠI MẤT**: vế `ただし` của phiếu này là mui hỏi ngược lại SYP; ô `回答内容` kiểm 08-20 **không thêm gì** ⇒ SYP không đáp, mui tự đóng. Việc số **6** đã viết lại hẳn theo phát hiện này — **cần user quyết kênh mới**.
  - 📌 **Nhịp đóng phiếu của mui (3 mẫu, đủ kết luận)**: No. 1 → 08-13 **12:27** ・ No. 2 → **12:28** ・ No. 10 → **12:28**. **3 phiếu trong 2 phút** ⇒ mui dọn QA theo đợt; 2 phiếu §9.4 còn lại rất có thể cũng đã 完了.
- **[08-20 lượt 2] Phiếu QA No. 1 「担当範囲…とアプリ対象外の確認」 cũng đã 完了** (chốt 08-13 12:27; 回答者 masao takahashi; nội dung 「モバイルアプリは開発対象です。」 thì có từ 08-03/04). Guide sửa thêm **6 chỗ, +40/−13**: §0.3 bảng mốc kiểm ・ §1.6 dòng 🔍 No. 1 + bảng "chỗ hở" ・ §9.4 bảng 4 QA **thêm cột ステータス** (No.1 ✅完了, 3 phiếu còn lại 🔸chưa kiểm) ・ Phụ lục E.2.
- ⭐ **BÀI HỌC VỀ QAデータベース — quan trọng cho mọi lần trích sau này:**
  - **ステータス có BA giá trị**: `回答中` (chưa dùng làm căn cứ được) / `回答済` / **`完了`** (≡ 回答済). Guide trước chỉ liệt kê 2 → **grep `回答済` là sót phiếu đã đóng**.
  - **`更新日時` KHÔNG phải ngày viết câu trả lời** — là ngày sửa gần nhất, thường chỉ là lúc *đổi trạng thái*. Phiếu No. 1: nội dung có từ 08-03/04 nhưng 更新日時 = 08-13, **lệch 10 ngày**. Trích thì ghi cả hai mốc.
  - **mui đóng phiếu theo ĐỢT**: No. 1 chốt 12:27, No. 10 chốt 12:28 cùng ngày 08-13 ⇒ **trạng thái đọc từ lâu là vô giá trị**; thấy 1 phiếu vừa 完了 thì mở luôn các phiếu cùng chủ đề.
  - **`質問内容` có thể Empty** dù câu hỏi vẫn tồn tại — nội dung nằm ở **body trang** (cả No. 1 và No. 10 đều vậy). Đừng kết luận "phiếu rỗng".
  - **Ngày hiển thị kiểu tương đối** ("Last Thursday") — trỏ chuột lấy ngày tuyệt đối trước khi trích.
  - Bốn điều trên đã viết thành mục 「⚠️ Bốn cái bẫy của QAデータベース」 trong **Phụ lục E.2** của guide.
- ⚠️ **Lỗ hổng quy trình**: câu trả lời có từ ~13/08 nhưng đợt nâng guide v1.3 ngày 18/08 bỏ sót, vì quy trình đó lấy **`git diff` repo tài liệu** làm phạm vi — **Notion nằm ngoài**. Đề xuất (CHƯA áp, phải qua ⛔#11): mọi đợt cập nhật guide thêm **bước 0 = rà QAデータベース** các phiếu đổi sang 完了/回答済 kể từ mốc trước.
- **質問者 không phải Bui Trong Dat** → SYP có nhiều người cùng đăng QA; đọc QAデータベース đừng lọc theo một người hỏi.
- **Chưa làm**: commit ・ review vùng sửa (⛔#5) ・ quyết có lên v1.4 không. Nhật ký: memory `09_...`.

**[08-19] ✅ CHỐT BẢN NỘP `CLIENT_REPORT_APP_RESTRUCTURE_ja.md` (task tái cấu trúc source app):**
- **Tiêu chí user chốt 19/08 — áp cho MỌI đợt hoàn thiện tài liệu**: *chỉ sửa cái sai đến mức **đổi quyết định của người đọc**, còn lại kệ*. "Đừng bắt từng con kiến trong miếng bánh" — rà đến khi hết lỗi thì không bao giờ nộp được.
- Sửa 3 chỗ: §2.2/§8.1 **23件** requirement (không phải 24) ・ §4.1 **481 file viết tay/~74.000 dòng** làm số chính (881 = sau khi sinh code) ・ §5.3 ghi chú 「共通」の範囲 (chung = logic/state/data/部品; `features/common` **không chứa màn hình** ⇒ màn hình đăng nhập/お知らせ vẫn dựng lại từng app).
- Đóng vĩnh viễn: **lệch Riverpod kurashi 3.x ↔ E-Smart 2.x KHÔNG phải việc** (kurashi chỉ là repo mẫu cấu trúc; đã chốt không dùng `kurashi_data`). Không đưa vào bản nộp: 2 kỷ luật goal 3 + CI build 2 app/PR (nội bộ).
- Việc còn treo của task rút còn **3 mục** — `submit_folder/2026_08_18/output_schedule.md` mục 7. Nhật ký phiên: memory `08_...` mục **7b**.

**[08-18] ✅ GUIDE → **v1.3** (đối chiếu `1100487`, 2026-08-12) — quy trình 4 bước do user chốt:**
- **Quy trình (nên tái dùng)**: rà+mapping → **review chính bản mapping** → sửa → **review CHỈ vùng sửa** (lấy `git diff` làm phạm vi, không quét lại cả guide). Chạy toàn bộ trong main loop, **không phóng agent/workflow**. Bước 2 bắt **5 lỗi của chính mapping** trước khi chúng kịp vào guide; bước 4 bắt **3 lỗi do đợt sửa sinh ra**.
- ⚠️ **Bẫy mốc lặp lại**: máy này đang ở `460c671` trong khi memory ghi `1100487` (đó là trạng thái **máy cũ** `C:\Users\a\...`). Đã `git pull` → `1100487`. 4 nguồn còn lại khớp origin.
- **Ba thay đổi nội dung lớn nhất**: ① **§7.3 tiểu mục B6 viết lại** — từ *"app chỉ gợi ý, người dùng tự tắt"* sang **"tự động điều khiển, app chỉ cài ngưỡng"** (先方確認 08-07; 手動制御・Push = 対象外), câu hỏi `F-GW-07` cũ đã đóng, thay bằng 3 câu treo mới (`GW-04` エネファーム ・ ngưỡng chung/riêng ・ dải-mặc định-đơn vị `GW-07`) ② **§7.5 MỚI 「機能仕様 app」** (5 ký hiệu tab a–e ・ kế hoạch **30 doc, mới viết 2** ・ **thang trạng thái thứ ba** ・ 4 kỷ luật viết ・ **nguồn ưu tiên #2 = comment trong pptx đối khách, NẰM NGOÀI REPO**) — kéo theo 「Bản thiết kế nháp」 thành §7.6 ③ **Phụ lục B.5 MỚI** マルチセンサー (B01 đã gỡ ↔ 統合要件 v1.2 vẫn giữ) + Phụ lục A thêm 人感センサー / Web API連携機器.
- **Kiểm cơ học sau khi vá**: 270 heading ・ **0 liên kết hỏng** ・ 70 dấu ``` (chẵn).
- ⚠️ **6 phát hiện Ở NGUỒN (N1–N6)** — lỗi/điểm mờ của chính repo `1100487`, **chưa hỏi mui/北ガス**: A04 tự mâu thuẫn ポイント数↔バッジ数 ・ E01 nhảy số 1→3→4 và còn 6 hàng 備考 trỏ tới requirement đã xoá ・ `4_spec/app/README.md` ghi 「24セクション」 (thực tế 23) ・ B01 人感センサー định nghĩa trống ・ A04 関連項目 hàng C5 trống ・ B01 bỏ 2 câu 要確認事項 nhưng 備考 vẫn trỏ 「要確認事項参照」. Chi tiết: `notes/guide_v13_mapping.md` mục E.

**[08-17] ✅ ĐỢT REVIEW `2026_08_13/` — KẾT QUẢ CUỐI:**
- Verdict 43/43: 妥当 6 ・ 妥当だが根拠不足 19 ・ 要修正 14 ・ 要業務確認 4 ・ 189 findings ・ đối kháng mọi [cao]+要修正 = **0 REFUTED**.
- Bản sửa nằm ở `new/` từng thư mục nhóm (file gốc + xlsx không đụng): 43/43 batch có bản vá, 24 file dịch JA mới, 3 nhóm có `new/batch_decision.md` (G1 7 sheet ・ G2 3 ・ G4 3), bản sửa summary 15 mục (nay ở `submit_folder/2026_08_13/summary_batch_migration/summary_batch_migration_ja.md` — user tách thư mục riêng 17/08, KHÔNG dùng `new/`; file tên có ngày `20260813_...` là bản GỐC member).
- 4 câu QA gộp từ 9 mục 要業務確認 (theo nhóm batch, có dẫn chứng file:dòng + khối JP paste được): `submit_folder/qa/qa_review_20260813_20260817.md` — **CHƯA GỬI**.
- Chi phí: fable ~3,3M ・ opus ~2,7M ・ sonnet ~0,9M — ledger + đơn giá hiệu chỉnh ở `notes/usage_budget.md` §2/§4 (dịch JA thật ~120k/file, checker ~144k/agent).
- Phát hiện đã áp vào workspace: **repo app là git thật** `syp-eminelstandard-app@41ee385` (`syp-dev`) — CLAUDE.md/README/SKILL/self_study_plan đã sửa; SKILL `3-step-review` mục 4a = baseline đợt này.
- **[17/08 chiều] Quy ước mới về `new/batch_decision.md` (user chốt sau tranh biện ⛔#11 3 lập trường), commit `b59f1b1`**: **mọi nhóm có xlsx đều có file này** — 修正版 (G1/G2/G4 thay ô; **G3 đặc thù**: ô xlsx chỉ trỏ TÊN FILE nên thêm dòng 「レビュー結果」 ngoài xlsx, hành động của member là **thay 2 file md `current-eminelsmart_DistributeMonthlyEcoPoints{,_ja}.md`, KHÔNG sửa ô**) và レビュー確認版 trùng khít bản gốc (G5/G6/G7 — 0 sheet 要修正, để phân biệt "đã review" với "chưa review"). Mỗi file thêm dòng 【メンバーの作業】 tiếng Nhật + verdict từng sheet + mã QA-0x. **Đính chính bản nộp: có 6 sheet 根拠不足 (không phải 5) có sẵn văn bản JP** — 4 câu thay thế (G1 CalcYearlyRoomTemperature ・ G2 CreateGroupSummary ・ G2 RankingCreation ・ G5 SendAlertLogMail) + 2 câu nối thêm (G1 CalcDailyAverageData ・ CalcWeeklySavingReportEffect); tất cả nay nằm ở mục 付録【提案・未適用】 của file nhóm. Sửa kèm: verdict QA-04 (`DistributeMonthlyEcoPoints` 根拠不足→**要修正**) ・ meta 7 file trỏ `../batch_decision.xlsx` ・ bỏ cặp 「」 thừa ở ô G4 RcvCntctCancellation ・ đồng bộ `review_summary` (P8/§3.G6/7-A1/7-A2) + `review_plan` §4.3,P8 + SKILL 4a.
- **[17/08 chiều, tiếp] `new/` LÀ BỘ TÀI LIỆU NỘP → PHẢI ĐỦ FILE dù có sửa hay không** (user chốt; thay quy ước cũ `review_plan` §4.3 "file không có finding thì không copy"), commit `618d44c`: đã copy nguyên văn (md5 khớp) 8 file vào `new/` — G6 4 file `legacy-batch_CreateCsvAndZip*_ja` (trùng bản 2026_08_12, plan bỏ qua review lại) ・ G8 `report_C05_energy_advice_{ja,vn}` (C5 sạch 0 finding) ・ G1 `legacy-batch_CalcYearlyAverageData{,_ja}` (0 finding). Lý do: người nhận chỉ mở `new/`, thiếu file = không phân biệt được "không đổi" với "bỏ sót". Quy ước đã sửa tận gốc ở `review_plan` §4.3 + `review_summary` (P8, ghi chú CalcYearlyAverageData) + SKILL 4a. **Rà 9/9 thư mục: đủ bộ.** Ngoại lệ do user tự xếp 17/08: **`summary_batch_migration/` KHÔNG dùng `new/`** — `summary_batch_migration_ja.md` = bản ĐÃ SỬA, `20260813_summary_batch_migration_ja.md` = bản GỐC member (tên có ngày = bản cũ, dễ nhầm ngược); mọi đường dẫn cũ trỏ `2026_08_13/new/summary…` đã sửa (review_summary 7-A3, usage_budget ledger, memory).

**[08-16] Diễn biến đợt review (giữ để tra ngược):**
- Đối tượng: 75 file điều tra + 43 sheet phán định (`batch_decision.xlsx`) + summary 47 dòng trong `submit_folder/2026_08_13/`. Plan = `review_plan_20260813.md` (user duyệt 16/08); kết quả tích lũy = `review_summary.md`; mốc bàn giao = commit local `312d6d0`.
- ✅ P0 (commit mốc ・ 5 repo khớp origin ・ convert 7 xlsx→`batch_decision.md` 43/43 sheet 0 lỗi) ・ ✅ P1 G8 app C1–C5 (12 findings, 1 [cao] CONFIRMED 2/2; C5 sạch; bảng nhu cầu dữ liệu app → `app_data_needs_ref.md`) ・ ✅ P6 G6 CSV/ZIP (妥当2・根拠不足1・**要業務確認1**: s_113 平均 liên hộ không có đích trong 別表① — câu hỏi JP chờ gộp).
- ✅ P2/P3/P4/P5 (39 batch) + P7 XONG, gom đủ vào `review_summary.md`: tổng **189 findings**, **43/43 verdict: 妥当6・根拠不足19・要修正14・要業務確認4**; đối kháng đầy đủ mọi [cao]+要修正 = **0 REFUTED** (§3c). P7: summary 08_13 chỉ điền mới, KHÔNG đè dòng SYP; 10 lệch + 15 dòng summary cần sửa (§3b).
- ✅ P8 vá xong **NHÓM G1** (18/18 batch → 36 file `new/` + `new/batch_decision.md` G1/G2/G4) — **commit local `f5a299b`**. Còn (theo thứ tự, chi tiết file ⭐ mục 5 items 1e+1f+4b): vá G4+G5 → G3 → G2+G7 → G8 → dịch JA 24 file → sửa summary (15 dòng P7-B + lỗi HTML/link) → re-review `new/` → gộp 9 câu 要業務確認 trình user → commit cuối + SKILL mục 4 + 4 file "app snapshot" + chốt memory. Fixspec + tư liệu: `C:\Users\a\.claude\projects\d--SYP-Home-mui-eminelGW\handoff_20260816\`.
- Quy ước user chốt: file gốc member không đụng ・ bản sửa/dịch vào `new/` từng folder ・ xlsx không sửa ・ JA ngắn gọn y phong cách member, chỉ review TÍNH CHÍNH XÁC ・ truy luồng data đến tận bảng (đã vào SKILL `3-step-review` #7 + Vòng 1).
- Phát hiện phiên: repo app là **git thật** `syp-eminelstandard-app@41ee385` (syp-dev) — CLAUDE.md/README/SKILL/self_study_plan ghi "snapshot" là LỖI THỜI, P8 sửa ・ spec [I]:200 nội bộ là **5 loại** không phải 4 bảng ・ header C0x còn レビュー中 nhưng README ghi レビュー済, `tasks/app_requirements_plan.md` không tồn tại trong repo.

**[08-13] Trạng thái mới nhất:**
- **`eminel_gw_project` = `1100487`** (working tree đã pull thật, kiểm bằng `git log -1`). So với mốc guide v1.2 (`460c671`): **thư mục `docs/eminel/4_spec/app/` MỚI xuất hiện** — 機能仕様 app bắt đầu được viết (`README` 195 dòng ・ `c02_グラフ` ・ `c03_レポート` ・ `Z_コントロールタブ構成検討`) + 11 file requirement app bị sửa (A01–A04, B01, B04, **B06**, **E01 −140 dòng**, E04, README). → **guide v1.2 đã lệch mốc, phải rà §7.3 + các mục trích A0x/B0x/E0x.** 3 repo còn lại không đổi.
- **`new_2/` ĐÃ VÁ XONG** (6 file, +71/−49) — user upload lại. Vá theo KHỐI: 4 [cao] + nhóm [vừa] (xem file ⭐ mục 2.2), mỗi finding kiểm lại trên code trước khi sửa. Kiểm chứng sau vá: 0 tàn dư ・ fence chẵn ・ heading JA↔VN khớp 3/3 cặp ・ cặp Xzilla trùng khít 324 dòng.
  ⚠️ **Danh sách chi tiết 78 findings của 08-12 đã MẤT** (không lưu ra đĩa) — chỉ vá được phần có ghi nhận trong memory; phần [thấp] còn lại chưa dựng lại được.
- **1 finding của review agent đã bị BÁC BỎ** khi kiểm lại: "shell flock không có căn cứ" là SAI (flock nằm trong `.sh` bên trong file `.tgz`) → thành ⛔#13.
- **3 tập báo cáo batch ĐÃ NỘP cả 3** (hạn 14/08). Bản chuẩn duy nhất = `submit_folder/2026_08_06/new_2/`. (Thư mục `new/`: user đã xoá 08-13 — xem như chưa từng tồn tại.)
- **Bảng tổng hợp 47 batch** `submit_folder/2026_08_12/summary_batch_migration_ja.md`: **6/47 dòng có kết luận** — 4 dòng CSV/ZIP của SYP (đã có link Notion) + 2 dòng 集計 của thành viên khác. **7 dòng 配信・通知系 + Xzilla đã điều tra xong từ 08-06 nhưng CHƯA điền.**
- **Mọi file QA nay ở `submit_folder/qa/`** (⛔#12) — `qa_kitagas.md` ・ `qa_batch_csvzip.md`.
- **[08-12] Guide → v1.2** (đối chiếu `460c671`): viết lại §5.5 (設定値運転 bị gỡ → 室温制御の有無 + 温度レベル), §5.6, §7.3 (bảng 23 section + mục B6), Phụ lục B.3/B.4, §0.3. Review 6 agent = 142 findings, phần guide vá hết.
- **[08-12] Bộ 4 batch `CSV/ZIPエクスポート系` theo FORMAT MỚI** → `submit_folder/2026_08_12/` (8 file JP+VN). Format user chỉ đạo, khác TEMPLATE v4: **1 batch = 1 file, chỉ điều tra hệ CŨ**; phán định để ở bảng tổng hợp. Mẫu: `legacy-batch_CalcTenMinutesSensor_ja.md` của thành viên khác.
- **3 phát hiện lật giả định (08-12, đã áp vào `new_2/` ngày 08-13)**: ① hệ cũ CÓ chiều gửi SFTP Xzilla (`PutLogFileCommand`, cron 00:00) ② spec [I] còn giữ 4 bảng của batch #5–#7 làm loại download nội bộ ③ **e-smart CÓ 3 bảng tích luỹ `DeviceAccumulated/DailyUsage/MonthlyUsageHistoryTable`** → "集計・計算系 không có gì dùng lại" đã bị bác.
- **Bài học vá tài liệu**: vá theo FILE làm vỡ nhất quán → **vá theo KHỐI** (1 bản chuẩn/khối → áp đồng loạt → `grep -c`/`diff` chứng minh). Chi tiết `05_session…` mục 8.3.
- Bộ skill: `create-investigation-report` (TEMPLATE v4) ・ `analyze-change-request` (⛔#11) ・ `3-step-review` ・ `notion-connect` ・ `slack-connect` ・ `update-memory`.
- `requirements/self_study_plan.md`: 4 hạng mục — **hạng mục 1 mới xong bước 1** (§8-3 F-ES của v1.2).

**Đã xong (tích lũy):** bộ tài liệu học v1.1 (10 chương + 7 phụ lục, đối chiếu `788b438`, đã qua review nhiều vòng)
・ `qa_kitagas.md` (8+4 câu; **câu 1 đã đăng QAデータベース Notion = phiếu No. 5, mui trả lời 「今の所、2026年スコープ外です」, ステータス 完了 chốt 08-13 — nhưng ⚠️ vẫn là trả lời của mui, 北ガス CHƯA xác nhận, và chữ 「今の所」 còn nguyên**)
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

**[08-18 chiều→tối] 🔄 TASK ĐANG CHẠY — TÁI CẤU TRÚC SOURCE APP** (nhật ký đầy đủ + việc còn treo: **`submit_folder/2026_08_18/output_schedule.md`** — phiên sau đọc file đó là làm tiếp được ngay).
- ✅ **[phát hiện 08-20] CÁCH HIỂU ĐỀ BÀI ĐÃ ĐƯỢC MUI XÁC NHẬN** — QA Notion phiếu **No. 7** 「「依頼: モバイルアプリ構成の変更」について確認」, 質問者 Bui Trong Dat, 起票 **08-03 19:22** (cùng ngày nhận đề bài), 回答内容 「**認識に相違ない**」, ステータス **完了** chốt **08-13 12:34**. ⚠️ Ô **回答者 để trống** (mui quên điền — user xác nhận) ⇒ **không gán tên ai khi trích**. Đây là chốt phần **hiểu đề**, KHÔNG phải chốt bản đề xuất. 🔸 Body phiếu **chưa đọc** (`質問内容` trống) — chưa biết chính xác "cách hiểu" gồm những gì. Chi tiết: `submit_folder/2026_08_18/output_schedule.md` mục 1.
- **Đề bài mui** (`2026_08_18/requirements/app_source_change.md`): nhét app Eminel (E-GW) vào **cùng repo** `syp-eminelstandard-app` với E-Smart — tách tầng app/tầng chung, build ra **2 app riêng**, thêm code bên này **không ảnh hưởng phát triển** bên kia. Lịch: đề xuất 8/3–8/14 → mui review 8/17–8/19 → phản ánh 8/20–21 → implement tuần 8/24–28. `chokkin_irai.md` (chiến lược branch) **đã xong, không cần quan tâm**.
- **Đã nộp**: `2026_08_18/CLIENT_REPORT_APP_RESTRUCTURE_ja.md` (bản nháp để mui review, 8 chương).
- **Nguồn tham khảo mới trong `sources/`**: `kurashi-for-energy` (repo mẫu mui chỉ định) + `kurashi-data-package` (gói tầng dữ liệu của nền Kurashi).
- **Kết luận đã chốt**: ① theo cách chia của `kurashi-for-energy` (**`apps/` + `packages/`**) là được ② **KHÔNG** dùng gói `kurashi_data` và **KHÔNG** tách tầng dữ liệu ra repo riêng → làm **`packages/data`** trong repo, giữ đúng khuôn của gói đó để sau này nhấc nguyên gói ra được ③ dùng chung tầng dữ liệu **không vi phạm** goal 3 (mui yêu cầu phải CÓ tầng chung; goal 3 nói về ảnh hưởng **phát triển**, không phải cấm liên quan).
- ⚠️ **Bẫy**: `submit_folder/2026_08_18/` đang chứa **cả file nội bộ tiếng Việt** (`output_schedule.md`) lẫn đề bài của mui — nộp cả thư mục là lộ đồ nội bộ (⛔#4).

**Việc tiếp theo (theo thứ tự):**
-1. ✅ **XONG 17/08: đợt review team `2026_08_13/`** (P0→P9 + bổ sung mặt phẳng copy-paste — xem khối [08-17] trên). Việc còn lại **không thuộc AI**: ① user gửi 4 câu QA (`submit_folder/qa/qa_review_20260813_20260817.md`) qua PM mui; ② member cập nhật **13 sheet** `batch_decision.xlsx` theo `new/batch_decision.md` (G1 7 ・ G2 3 ・ G4 3) **và thay 2 file md của G3** (`current-eminelsmart_DistributeMonthlyEcoPoints{,_ja}.md` — nhóm này KHÔNG đụng xlsx), tùy chọn thêm **6 câu 付録【提案・未適用】** cho sheet 根拠不足; ③ member điền URL Notion còn thiếu ở summary dòng 63/66.
0. ✅ Xong 08-13: vá `new_2/` (user upload lại) ・ pull `1100487` ・ ⛔#12 QA folder ・ 4 link Notion vào bảng tổng hợp.
1. ✅ **XONG 18/08: guide → v1.3 theo `1100487`** (§7.3 B6 viết lại ・ §7.5 mới về `4_spec/app/` ・ Phụ lục B.5 ・ 9 chỗ mốc đối chiếu). **Còn lại của hạng mục này**: ① quyết định có hỏi 6 phát hiện nguồn N1–N6 không ② Phụ lục C chưa thêm `GW-04` ③ Phụ lục D chưa trỏ `4_spec/app/` ④ `requirements/README.md` + `self_study_plan.md` chưa rà theo tầng spec app ⑤ **chưa đọc nội dung `c02_グラフ`/`c03_レポート` và skill `draft-app-spec`** (user chọn mức "Vừa" cho §7.5).
1b. **Đuôi của đợt vá 08-20** (11 lượt vá theo 11 phiếu QA): ① 🔴 **CHƯA làm — review CHỈ vùng sửa** (⛔#5 bắt buộc kể cả sửa nhỏ; phạm vi = `git diff 432867d..HEAD -- requirements/onboarding_guide.md`, **đừng quét lại 4.500 dòng**; quy trình 4 bước của 18/08 chứng minh bước này bắt được lỗi do chính đợt sửa sinh ra) ② **CHƯA quyết** guide có lên **v1.4** không — bảng meta đầu guide (dòng 8) vẫn ghi `1.3` ③ ✅ commit XONG (13 commit) ・ 🔴 **push CHƯA** — auto mode chặn `git push`, user tự chạy `git push origin main` ④ **CHƯA rà** `requirements/README.md` + `notes/guide_v13_mapping.md` theo bảng 担当 mới (`self_study_plan.md` đã sửa 1 chỗ ngày 08-20, nhưng **dòng 54 vẫn còn câu sai** — xem việc 4).
1c. ✅ **XONG 20/08 — CẢ 4 PHIẾU của bảng §9.4 + phiếu No. 10 đều đã kiểm, TẤT CẢ 完了.** No. 1 担当範囲…とアプリ対象外 (起票 08-03 17:30 → chốt 08-13 **12:27**) ・ No. 2 独立デプロイ (17:31 → **12:28**) ・ No. 3 管理画面は独立か共通か (17:32 → **12:28**) ・ No. 4 旧EMINEL調査範囲…hemssv対象外 (17:32 → **12:28**) ・ No. 10 SYP開発範囲 (08-12 16:17 → **12:28**). Guide + `self_study_plan.md` đã sửa hết. **Nhịp mui: lập 4 phiếu trong 3 phút, mui để 10 ngày rồi đóng cả loạt trong 2 phút** — thấy 1 phiếu đổi trạng thái thì mở luôn phiếu cùng chủ đề. Nhớ: `完了` cũng là "đã trả lời" — **grep `回答済` sẽ sót**. ⬜ **Chưa kiểm**: các phiếu QA **ngoài** nhóm phạm vi (vd 「バッジ・ランクは2026年度対応スコープでしょうか」) — xem việc số 8.
1e. **[08-20, user sửa yêu cầu] QA đã soạn xong, CHỜ DUYỆT + ĐĂNG**: `submit_folder/qa/qa_dokuritsu_deploy_20260820.md`.
   ⛔ **ĐÍNH CHÍNH MỘT KHẲNG ĐỊNH SAI CỦA AI**: bản đầu ghi *"phiếu No. 2 đã `完了` nên không trả lời vào đó được nữa, phải lập phiếu mới"* — **SAI**. Phần `Comments` của Notion **không bị khoá theo `ステータス`**; phiếu `完了` vẫn nhận comment (bằng chứng: No. 6 và No. 8 đều có comment của mui). `完了` = **mui coi việc trao đổi đã xong**, không phải "trang bị đóng".
   → **Cách làm đúng (user chốt)**: **ghi thêm vào BODY của chính phiếu No. 2, ngay dưới câu hỏi gốc, mở đầu bằng dòng ngày** (「【2026/08/20 SYP追記】」), KHÔNG lập phiếu mới — để mạch hội thoại nằm một chỗ.
   → **Phạm vi cũng rút lại (user chốt)**: phần trả lời giữ nguyên (#15); phần hỏi lại **chỉ MỘT câu** = *"4 chức năng đó **bê sang E-GW chạy độc lập** hay **làm package dùng chung**?"*. **Bỏ** 2 câu của bản nháp trước (chung repo hay tách / có chia sẻ library chung) — câu hỏi mới cụ thể hơn và buộc chọn giữa hai cách làm có khối lượng công khác nhau rõ rệt.
   Có bản VN để duyệt + khối JP dán được nguyên vẹn, đã rà sạch mã nội bộ. **Trạng thái 08-20 (user chốt)**: ⏸ **CHỜ XÁC NHẬN NỘI BỘ trước khi đăng** — không phải chờ soạn, nội dung đã xong. Người duyệt đọc **mục 2** của file (bản tiếng Việt), khối JP ở **mục 3** dán được nguyên vẹn. Sau khi đăng: ghi số phiếu Notion vào mục 5 của file → đóng Phụ lục C **#15**, chuyển **#14** sang "đã hỏi, đang chờ".
1f. **[08-20] Phiếu No. 12 — GIẢ THUYẾT CỦA AI ĐÃ SAI, chỉ cần THÚC.** Đã đọc body: câu hỏi **viết đúng chuẩn rồi** — bảng **12 dòng** (領域 × 機能 × 劣後の範囲) + 「内容に相違がないかご確認をお願いいたします」, mui chỉ cần đáp đúng/sai. Trước đó AI ngờ nó "hỏi kiểu mở nên bị bỏ lại" → **sai**. ⇒ **KHÔNG soạn lại câu hỏi**, chỉ thúc.
   - → Bảng 12 dòng đã vào guide **§6.4** dưới nhãn 🔸 「Bảng SYP tự lập — mui CHƯA trả lời」. Nó **chi tiết hơn** bảng cũ (lấy từ `10_feature_list.md`) ở 3 điểm: có **mã requirement/chức năng** ・ có cột **範囲 (全部/一部/要確認)** ・ **chỉ ra 2 chỗ chính SYP cũng chưa chắc**.
   - ⚠️ **2 mục còn mở lộ ra từ bảng này**: **#6** 制御状態確認 (`F-AD-02` mở rộng) = **一部**, chưa phân định phần nào lùi ・ **#12** 家電操作 (`B4`) = **要確認**, chưa biết 2026 hay 2027 (đáng chú ý vì B4 đã được viết nội dung requirement).
   - 📌 **Bảng KHÔNG có dòng firmware nào** — không phải bỏ sót: firmware là **7-1, 担当 mui Lab**, nên bảng xin xác nhận của SYP chỉ gồm **3 khối SYP làm**. Đây là bằng chứng SYP đã dùng bảng 担当 đúng cách.
   - **Trạng thái 08-20 (user chốt)**: ⏸ **việc thúc cũng CHỜ XÁC NHẬN NỘI BỘ**. Không cần soạn gì thêm — chỉ là một comment nhắc trên phiếu No. 12.
   - 🔵 **`git push`: user tự làm CUỐI BUỔI** — auto mode chặn AI chạy `git push`. User **đã push tới `8ed8b89`** (báo cáo ngày) trong buổi; còn **5 commit** chưa lên: `38be179` (QA No.8) ・ `225bf94` (rà hàng đợi) ・ `89c6766` (review 3 vòng) ・ `ea8f50f` (phiếu A) ・ `11f2bd0`. Phiên sau kiểm `git log origin/main..HEAD --oneline`; còn commit thì nhắc user.
1d. Áp đề xuất **"bước 0 = rà Notion"** vào `skillAI/3-step-review` (hoặc skill cập nhật guide) — theo ⛔#11 phải qua `analyze-change-request` trước, sửa gốc SKILL rồi mới áp. 🔸 CHƯA làm.
2. **Điền 7 dòng 配信・通知系 (#1–#4) + Xzilla (#5–#7) vào `summary_batch_migration_ja.md`** — kết luận đã có sẵn trong `new_2/`; cần quyết: có tách thành file `legacy-batch_<Command>_{ja,vi}.md` theo format mới không.
3. **Điều tra nhóm 集計・計算系** (17/19 dòng còn lại của nhóm; SYP còn ~30/43 batch chưa điều tra). ⚠️ Giả định cũ "e-smart không có gì dùng lại" **đã bị bác** — e-smart CÓ 3 bảng history (`template-dynamodb.yaml:1113/1145/1177`), ghi bởi 5 batch `batch-import-rinnai/noritz-*`. Dùng skill `create-investigation-report`.
4. **`requirements/self_study_plan.md`** — hạng mục 1 tiếp bước 2–6; **sửa dòng 54** ("集計・計算系 — e-smart không có gì dùng lại") theo phát hiện trên (CHƯA làm).
5. Findings [thấp]/[vừa] còn lại của 78 (đã mất danh sách) — user quyết có chạy lại một lượt review để dựng lại không.
6. ⚠️ **VIỆC NÀY ĐỔI BẢN CHẤT (phát hiện 08-20) — phiếu đã ĐÓNG mà SYP CHƯA trả lời.** Phiếu **No. 2** 独立デプロイ
   (完了, chốt 08-13 12:28) có vế `ただし` = **mui hỏi ngược lại SYP**: 「ただし既存システムを使い続けたほうがいい機能が
   あれば教えてほしいです」. Kiểm ô `回答内容` ngày 08-20: **không có nội dung nào thêm** ⇒ mui tự đóng, SYP không đáp.
   Treo suốt từ 08-04 qua 5 phiên (`03_`→`06_`) nên đã rơi mất.
   → **Nội dung trả lời thì đã soạn xong từ lâu**, nằm ở `submit_folder/2026_08_04/report_batch_3nhom_doichieu_esmart_egw.md`
   **dòng 103** (mục 「Ba việc rút ra cần làm ngay」 #1), bản JP ở `2026_08_05/旧EMINELバッチ移行判定報告書_3グループ11本.md` §2.2-1:
   **① hệ CŨ (旧EMINEL) = không batch nào đáng dùng tiếp nguyên trạng ② hệ ĐANG CHẠY (e-smart) = 4 ứng viên**:
   hạ tầng Push (FCM) ・ hạ tầng point/badge + PI連携 ・ luồng nhận Xzilla SFTP→S3→DynamoDB ・ cơ chế admin download/export.
   Tiền đề kèm theo (cùng báo cáo dòng 115): "dùng lại" = dùng lại **code/cơ chế/pattern**, deploy độc lập thì **vẫn phải
   dựng lại môi trường chạy** — "dùng lại" ≠ "0 công".
   → **CẦN USER QUYẾT**: phiếu cũ đã đóng nên phải chọn kênh mới — ⓐ mở **phiếu QA mới** trên QAデータベース, hay
   ⓑ nêu khi trình thiết kế. Kèm cách gỡ điểm treo cũ: thay vì chờ xác nhận nghĩa 「既存システム」, **trả lời luôn cả hai vế**
   + một câu mở đầu nói rõ "chúng tôi hiểu 「既存システム」 gồm cả hai nên xin trả lời cả hai" → đỡ mất một vòng hỏi lại.
6b. **Mức độ độc lập của server E-GW vẫn CHƯA có ai nói** (chung library/source hay không). Phiếu No. 2 đã đóng mà không
   nói ⇒ **chờ tiếp là chờ vô ích**, muốn biết phải mở phiếu QA mới. Lưu ý chữ 「基本的には」 (*về cơ bản là*) trong nguyên
   văn là chữ nhượng bộ — đóng phiếu không xoá nó, **không được đọc thành "độc lập tuyệt đối"** (⛔#8).
7. 🔴 **NAY CẤP HƠN (phát hiện 08-20)** — chốt nội bộ với **kihara** về Q5 (GW giữ trạng thái DR — báo cáo batch #4 cũng treo
   vào đây) → gửi `qa_kitagas.md` qua PM mui (quyết kèm Dự phòng 3/4 không).
   **Lý do cấp hơn**: phiếu QA **No. 25** đáp 「**後回し**」 cho phương án kết thúc DR ⇒ **北ガス sẽ không chọn A/B lúc này**,
   nhưng firmware **vẫn phải viết trong 2026** và hai phương án đòi hai năng lực khác nhau (B đòi GW lưu trạng thái, mà tài
   liệu ghi 「GW側で保存はしたくない」). ⇒ **mui/SYP phải tự quyết tư thế firmware**: xây sẵn năng lực lưu trạng thái (giữ
   đường mở cho B) hay không xây (khoá vào A). Chi tiết + 2 cách đọc: guide Phụ lục C #5, khối ⚠️ dưới bảng.
8. **Theo dõi QAデータベース — trạng thái thật sau đợt rà 08-20** (thay hẳn ghi chú cũ "5 trang 回答中"):
   - ✅ **8 phiếu 完了, đã vào tài liệu**: No. 1 ・ 2 ・ 3 ・ 4 ・ 5 ・ 7 ・ 9 ・ 10.
   - 🟡 **No. 6** 「エラー種別（重篤／軽微）判定条件」 — `回答中`, comment masao 08-19: **「結構後になる」**, mui chưa liệt kê được danh mục lỗi. Nội dung đã vào guide §7.4③ + Phụ lục C #1. Theo dõi tiếp.
   - 🟡 **No. 8** 「GW-IDと顧客・契約情報の連携方法」 — `回答中`, comment masao 08-19 **đã đủ nội dung dùng được** (GW-ID↔TagTag ID, bỏ EMS-SP番号), đã vào guide §5.2. **Mở lại kiểm trước khi trích vào bản gửi ra ngoài.**
   - 🔶 **No. 12** 「2027年劣後機能の確認」 — `確認中`, **trống hoàn toàn**, bị bỏ qua có chọn lọc ⇒ **phải thúc** (Phụ lục C #13).
   - ✅ **ĐÃ RÀ HẾT DÃY (user xác nhận 08-20)**: **12 phiếu** = No. 1–10 · 12 · 14. **No. 11 và No. 13 KHÔNG tồn tại** trên QAデータベース hiện tại — 🔸 user nhận định *"có vẻ đã bị xoá"*. ⇒ **Đừng đi tìm hai số đó nữa**; số phiếu có lỗ ≠ thiếu sót của mình.
   - 📌 Bài học 08-20 vẫn giữ: phiếu chưa mở có thể chứa thứ **không có ở đâu khác** — No. 9 sinh ra guide §7.7 ・ No. 6 đảo Phụ lục C #1 ・ No. 8 chốt cách gắn GW ・ No. 14 sinh ra §7.4⑦. Nên **khi có phiếu mới thì mở màn hình DANH SÁCH**, đừng mở lẻ từng trang.
   - ⚠️ Khi lọc: **`完了` cũng là "đã trả lời"** — grep riêng `回答済` sẽ sót. Và **phải đọc cả `Comments`** (bẫy ⑤, Phụ lục E.2).
9. Hỏi mui xác nhận **đích của luồng export SFTP `/EST`** trong backend e-smart (≒「EMINELデータの共有」 F-ES-10?) — xem báo cáo batch §6.
10. Khi **IF-01/CLD-07** (định nghĩa 入出力 Xzilla) có spec → rà lại nhóm Xzilla của báo cáo batch (§4, gồm cả
   chiều xuất); danh sách việc-cần-xác-nhận đầy đủ: bảng §6 của báo cáo batch (8 mục).
   ✅ **[08-20] Phần 保持期間 của spec [I] KHÔNG CÒN là "chưa có trong bảng QA"** — ghi chú cũ đã lạc hậu. Đã hỏi bằng
   **phiếu No. 14** 「過去データダウンロードの必要遡及期間についてご確認」 (起票 08-13 12:29) và **có trả lời: 「24か月です」**
   (`回答中`, cập nhật 08-19 18:02, 回答者 trống). ⚠️ Nhưng **phiếu hỏi 3 câu, chỉ câu 1 được đáp** — còn: ② có quy định
   nội bộ đòi lưu **quá 24 tháng** không (kiểm toán / bảo hành thiết bị) ③ **ZIP quá khứ đã tích trên server cũ** có
   phải di trú sang hệ mới, hay giữ tiếp môi trường cũ. → Đã vào guide **§7.4⑦** + **Phụ lục C #11b**.
11. **B06 マイホーム発電**: phần cập nhật guide §7.3 ✅ đã làm ở v1.2 (đã có mục B6). Còn lại: rà các mục guide trích **B04/B05/C01–C03** theo `1100487` (B04/B06 vừa bị sửa tiếp ngày 12/08); cân nhắc bổ sung guide 0.7 (`legacy_eminel_docs` đã có local).
12. Bối cảnh: hạn **tháng 9/2026 fix design+spec** vẫn treo trên 23/23 section chưa chốt + 10/10 spec admin DRAFT;
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
| `05_session_20260812_guideV12_review6agent.md` | [2026-08-12] Pull `460c671` → **guide v1.2** (viết lại §5.5 mô hình sưởi mới, §5.6, §7.3 + mục B6, Phụ lục B.3/B.4) → **review 6 agent** (3 vòng guide + 3 cặp `new_2/`) = 142 findings, guide vá hết / `new_2/` chờ quyết → **3 phát hiện lật giả định**: hệ cũ có chiều gửi SFTP Xzilla ・ spec [I] giữ 4 bảng batch #5–#7 ・ e-smart CÓ bảng tích luỹ `TABLE_DEVICE_*_HISTORY` |
| `06_session_20260813_pullSpecApp_vaNew2_ruleQA.md` | [2026-08-13] Pull **`1100487`** — `4_spec/app/` (機能仕様 app) xuất hiện + 11 file requirement app đổi → **guide v1.2 lệch mốc** ・ **vá `new_2/` để nộp lại** (6 file, 4 [cao] + nhóm [vừa]; danh sách 78 findings gốc đã mất) ・ **bác bỏ 1 finding sai** (flock nằm trong `.tgz`) → ⛔#13 ・ phát hiện working tree cũ 10 ngày → ⛔#14 ・ **⛔#12 mọi file QA về `submit_folder/qa/`** ・ điền 4 link Notion vào bảng tổng hợp (6/47 dòng) |
| `07_session_20260816_reviewTaiLieuTeam_p0p1p6.md` | [2026-08-16→17] **Đợt review tài liệu team `2026_08_13/` — HOÀN TẤT P0→P9** (bàn giao sẵn sàng; QA chờ user gửi). Chi tiết gốc: (75 file + 43 sheet phán định): plan duyệt → **P0–P7 XONG** (mốc `312d6d0`; 189 findings; 43/43 verdict 妥当6・根拠不足19・要修正14・要業務確認4; đối kháng 0 REFUTED; P7: 10 lệch + 15 dòng summary cần sửa) → **P8 vá xong G1** 18/18 batch → `new/` + commit **`f5a299b`** ・ hàng đợi còn lại + handoff `handoff_20260816/` + 9 câu 要業務確認: mục 5 items 1e/1f/4b ・ SKILL +#7 & truy-bảng ・ cơ chế ước lượng token `notes/usage_budget.md` (⛔#15) ・ app repo = git thật `41ee385` ・ spec [I]:200 = 5 loại |
| `08_session_20260818_guideV13_theoMoc1100487.md` | [2026-08-18] **Guide → v1.3** theo mốc `1100487`: quy trình 4 bước (mapping → review mapping → sửa → review vùng sửa) ・ 13 mục sửa (+194/−49) ・ **§7.3 B6 đảo kết luận** ・ **§7.5 mới: tầng `4_spec/app/`** ・ **Phụ lục B.5 マルチセンサー** ・ 0 liên kết hỏng ・ **6 phát hiện ở nguồn N1–N6 chưa hỏi** ・ bẫy: máy này từng ở `460c671` dù memory ghi `1100487` (trạng thái máy cũ) |
| ⭐ `09_session_20260820_qaSypScopeNo10_guideBangTanto.md` | [2026-08-20, **2 lượt vá**] **Phạm vi SYP CHỐT** qua QA Notion No. 10 「SYP開発範囲の確認」 (回答者 swan, chốt 08-13, **完了**): mui Lab = 7-1 ファームウェア + 7-2 GW管理クラウド │ SYP = 7-3 EMINEL-smartサーバー + 7-4 管理画面 + **モバイルアプリ**. **Lượt 2**: phiếu **No. 1** 「担当範囲…とアプリ対象外の確認」 cũng **完了** → guide tổng cộng vá **12 chỗ, +133/−26** (§0.3 ・ §1.3 ・ §1.6 tách 対象範囲 vs **担当** ・ §6.1 bảng mã thêm cột 担当 ・ §9.4 bảng QA thêm cột ステータス ・ Phụ lục E.2 「4 cái bẫy」) ・ **5 bài học về QAデータベース** (3 giá trị ステータス ・ 更新日時 ≠ ngày trả lời ・ mui đóng theo đợt ・ 質問内容 Empty ・ ngày tương đối) ・ **lỗ hổng: đợt v1.3 chỉ rà git, không rà Notion** ・ 2 lỗi tự mắc & tự sửa trong phiên: checker anchor báo 62 link hỏng = SAI (họ ⛔#13, mục 2.4) và quy nạp 更新日時 từ **1 mẫu** (mục 3.4) |
