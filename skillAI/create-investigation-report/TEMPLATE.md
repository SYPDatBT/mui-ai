# TEMPLATE v4 — Chuẩn báo cáo điều tra (batch / chức năng / nhóm chức năng)

> Khuôn nhà chính thức, hợp nhất từ: tài liệu mẫu `CalcTenMinutesSensor` (summary-report + technical-details, thành viên team soạn) + bộ tiêu chí tự-chứa user chốt 2026-08-06 (= ⛔#10 trong `memory/00_INDEX.md`).
> Mỗi đối tượng điều tra = 1 file/ngôn ngữ (JP để nộp, VN để đọc/trình bày), chia 2 PHẦN trong cùng file. Bản JP mirror cấu trúc, gloss ngắn gọn kiểu JP (「CLD-07（…の未決事項）」), bản VN gloss đầy đủ hơn.

## CẤU TRÚC BẮT BUỘC (đúng thứ tự)

```
# Báo cáo điều tra: <đối tượng> — <câu hỏi trung tâm, vd "có cần port sang hệ mới không?">
[Bảng meta]: Đối tượng | Phạm vi (repo + HEAD từng repo, ghi chú commit gốc nếu đã fetch tiến lên) |
             Ngày điều tra / ngày lập | Vị trí phân tập (nếu bộ nhiều tập; số hiệu xuyên suốt) | Tài liệu liên quan
[Mục lục có anchor]

## KẾT LUẬN
> Blockquote to, đứng riêng ngay đầu: 1 dòng/đối-tượng-con — nhãn (BỎ BATCH–GIỮ NGHIỆP VỤ / TẠO MỚI /
> BỎ, THAY BẰNG… / KHÔNG CẦN PORT) + nửa câu bản chất.
> + câu: "Có N điểm cần xác nhận trước khi chốt (→ §3)".

═══ PHẦN I — BÁO CÁO (đọc 5 phút, cho PM / người không cần chi tiết code) ═══
§1 Vì sao kết luận như vậy
   - Bảng "bản chất đầu vào / cơ chế: hệ cũ ↔ hệ mới" (3–5 hàng, chỉ cái quyết định kết luận)
   - Bảng "M xử lý cốt lõi của hệ cũ → hệ mới còn cần không?" (xử lý | ❌/✅ + vì sao nửa câu)
§2 Hệ mới xử lý ở đâu / sẽ xử lý thế nào
   - Bảng: việc hệ cũ làm | hệ mới thực hiện ở (path) | loại (Lambda-webhook / API / batch / CHƯA CÓ — phải tạo)
   - 1 sơ đồ ASCII luồng mới (rút gọn từ Phần II)
   - Khác biệt tư tưởng thiết kế (nếu có) + "cách nhớ" ví von 1 câu
   - Bẫy hiểu nhầm đặt tên/kiến trúc (nếu có — mọi con số PHẢI tự đếm trên repo của mình, cấm chép từ tài liệu khác)
§3 Điểm chênh lệch / cần xác nhận trước khi chốt
   - Bảng: # | chênh lệch/điểm treo | hệ cũ | hệ mới/kế hoạch | mức 🔴🟡🟢
   - **Câu chữ soạn sẵn** để hỏi (khách qua PM / đối tác trực tiếp) — blockquote, kèm điều kiện tiền đề nếu có
§4 Điểm dễ bị hiểu sai khi trình bày (bảng: hiểu sai | đúng phải là — 2–4 điểm)
§5 Việc tiếp theo (bảng # | nội dung | phụ trách) + "Phương châm rút ra" 1 blockquote

═══ PHẦN II — CHI TIẾT KỸ THUẬT (cho dev / người review code) ═══
§6 Từng đối tượng con (lặp cho mỗi batch/chức năng):
   6.x.1 Mục đích (1–2 câu tiếng người thường)
   6.x.2 Phán định + "Vì sao đề xuất vậy" (3–4 gạch)
   6.x.3 Flow hệ cũ: sơ đồ ASCII (trigger → xử lý → bảng dữ liệu) + thông tin cơ bản (class/cron/lệnh/tham số)
         + TRÍCH CODE then chốt (3–8 dòng nguyên văn, chú thích; `...` = lược) + bảng xử lý giá trị bất thường
         nếu có + hằng số nếu có
   6.x.4 Hệ mới đã có gì / yêu cầu hệ mới là gì (dẫn chứng file:dòng, nhãn 確実/推定)
   6.x.5 Flow hệ mới đề xuất: sơ đồ ASCII + các bước thực hiện (code path đầy đủ từng layer/file + *Vì sao*
         mỗi bước) + kiểm thử
§7 Luồng/hạ tầng chung của nhóm (nếu điều tra theo nhóm): luồng nhận/gửi + BẢNG CHI TIẾT từng kênh dữ liệu
   (nguồn → trường chính lấy TỪ CODE → bảng đích → tác dụng nghiệp vụ 1 câu)
§8 Đối chiếu dữ liệu cũ ↔ mới
   - Bảng đối chiếu theo CỘT/bảng dữ liệu chính (✅ có / ⚠️ khác bản chất-cần xác nhận / ❌ không có + ĐẾM tổng)
   - Bảng đối chiếu cơ chế (đường nhận, chống trùng, lịch chạy, bảng từng đối tượng)
§9 (nếu có lựa chọn thiết kế) So sánh phương án A/B/C: bảng tiêu chí (khối lượng, chi phí, chạy lại được,
   rủi ro mất dữ liệu…) + căn cứ chọn + **điều kiện xem xét lại** (khi nào mở lại phương án thua).
   Không có lựa chọn → bỏ mục, ghi chú 1 dòng.
§10 Danh sách QA đầy đủ — nhóm theo ĐỐI TƯỢNG HỎI: A khách/PM (nghiệp vụ) / B đối tác kỹ thuật /
   C bên bàn giao hệ cũ / D team app (nhóm nào không có thì ghi chú bỏ). Mỗi câu: # | câu hỏi | vì sao cần |
   mức 🔴🟡🟢. Cuối mục: sơ đồ "thứ tự xử lý đề xuất" (dependency giữa các câu).
   KHÔNG giữ bảng "việc cần xác nhận" trùng lặp ở chỗ khác — gộp hết về đây, Phần I §3 chỉ giữ bản rút gọn.
   Nếu tách các câu này thành **file QA riêng** (kiểu `qa_batch_csvzip.md`): file đó nằm ở
   `submit_folder/qa/`, tên = mô tả nội dung hỏi + ngày tháng — `qa_<chủ-đề>_<YYYYMMDD>.md` (⛔#12).
§11 Căn cứ & độ chắc chắn
   - Bảng nguồn dẫn: nội dung | nguồn (path đầy đủ + dòng)
   - Bảng ĐỘ CHẮC CHẮN 3 mức: ✅ đã xác minh / ⚠️ suy đoán (*推定* — liệt kê ĐÍCH DANH) / ❓ chưa xác minh
     (liệt kê ĐÍCH DANH)
   - Nguồn sống (QA/Notion): ghi 参照日 + trạng thái; các khẳng định phụ thuộc mốc repo: ghi rõ commit
   - Bảng lệch tài-liệu-khảo-sát ↔ code (phần liên quan tài liệu này)
```

## 12 TIÊU CHÍ BẮT BUỘC (tự kiểm khi soạn; review kiểm lại từng điểm)

1. Gloss mọi mã hiệu tại MỖI lần xuất hiện, theo ngữ cảnh lần đó (CLD-xx, IF-NN, IF 4 số, SVC-xx, F-ES-xx, spec [G]/[I], mã 契約種別, tên QA, tên bảng…).
2. Con trỏ (§, #N, tập khác) kèm tóm tắt nội dung đích; trỏ chéo tập phải ghi đúng số mục CỦA BẢN NGÔN NGỮ ĐÓ.
3. Bước làm: code path đầy đủ từng layer/file (đã kiểm tồn tại bằng ls/Glob) + *Vì sao*/理由 mỗi bước.
4. Phán định BỎ–GIỮ–THAY tường minh, đứng đầu mục (sau Mục đích); cấm nhãn cụt.
5. Luồng xuống tận DB (bảng đích — grep xác minh); kênh dữ liệu có bảng nguồn→trường(từ code)→đích→tác dụng.
6. Sơ đồ ASCII fenced cho luồng chung + TỪNG đối tượng con (cũ và mới); trích code then chốt nguyên văn (`...` = lược, khai quy ước ở đầu file).
7. Bảng đối chiếu cũ↔mới (cơ chế + cột dữ liệu, có đếm trạng thái).
8. Mục đích 1–2 câu đầu mỗi mục con.
9. Bố cục khoa học: đoạn ≤ ~5–6 dòng, bullet/bảng/heading; mục lục anchor; fence chẵn; bảng không vỡ.
10. Viết cho NGƯỜI: câu đầy đủ, ví von khi giúp nhớ; không nén ký hiệu.
11. Các mục đặc trưng mẫu: KẾT LUẬN blockquote đầu file; bảng "xử lý cốt lõi→còn cần?"; câu chữ soạn sẵn hỏi khách/đối tác; "điểm dễ hiểu sai"; QA theo đối tượng + mức + thứ tự; độ chắc chắn 3 mức; "phương châm rút ra".
12. DỮ KIỆN: code-first (mở file/grep, không đoán); tài liệu khảo sát chỉ làm nhãn — vênh thì CODE THẮNG và ghi vào bảng lệch; nhãn 確実/*推定* nhất quán; grep-phủ-định phải tự tái hiện được; JP↔VN khớp 1-1 về con số/kết luận/số bước.
