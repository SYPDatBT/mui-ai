---
name: analyze-change-request
description: >
  Tiếp nhận MỌI yêu cầu sửa/feedback/phàn nàn của user về tài liệu, quy trình hay kết quả: phân tích
  bản chất yêu cầu → tổng quát hóa thành quy tắc → cho các agent CẠNH TRANH phản biện/brainstorm lẫn nhau
  → đề xuất lại GIẢI PHÁP TỔNG THỂ cho user duyệt → mới thực thi nguyên khối. Trigger: "sửa X", "thêm Y",
  "tôi thấy Z chưa ổn", "tôi thất vọng vì…", mọi feedback về deliverable. Sinh từ bài học 2026-08-06:
  chuỗi vá đuổi từng yêu cầu tạo tài liệu hổ lốn, phải làm lại từ đầu.
user_invocable: true
---

# analyze-change-request — Phân tích yêu cầu sửa & đề xuất giải pháp tổng thể

**Nguyên tắc gốc (user đặt, không thương lượng)**: *"Mỗi lần user yêu cầu sửa thì phải HIỂU và ĐỀ XUẤT LẠI
giải pháp tổng thể thông qua phân tích nội dung yêu cầu — thay vì ngay lập tức đồng thuận."*
**Đồng thuận ngay + vá ngay = lỗi quy trình** (⛔#11). Phản biện phải có dẫn chứng, không phải cãi suông;
nếu phân tích cho thấy yêu cầu dựa trên hiểu nhầm → nói thẳng kèm bằng chứng, không nịnh.

## 0. Bootstrap tối thiểu

Đọc `memory/00_INDEX.md` (⛔ 1–11) nếu chưa đọc trong phiên. Trích NGUYÊN VĂN yêu cầu của user ra trước khi phân tích.

## 1. PHÂN LOẠI yêu cầu (bắt buộc viết ra, không làm trong đầu)

| Loại | Dấu hiệu | Hướng xử lý mặc định |
|---|---|---|
| A. Fix cục bộ thật | 1 chỗ, sai rõ ràng (chính tả, số sai, link hỏng), không sinh quy tắc | Được sửa ngay (ngoại lệ mục 4) |
| B. Triệu chứng hệ thống | Cùng loại lỗi có thể tồn tại ở N chỗ khác / đã bị chê ≥2 lần cùng chủ đề | BẮT BUỘC đi đủ mục 2–4 |
| C. Thay đổi thiết kế/khẩu vị | Đụng cấu trúc, template, quy trình, cách trình bày | BẮT BUỘC đi đủ mục 2–4 |
| D. Mâu thuẫn | Xung đột với ⛔, TEMPLATE, hoặc yêu cầu trước đó của chính user | BẮT BUỘC nêu mâu thuẫn cho user trước khi làm bất cứ gì |

## 2. TỔNG QUÁT HÓA

Trả lời 3 câu, viết ra: ① Nếu yêu cầu này đúng thì QUY TẮC TỔNG QUÁT đằng sau là gì? ② Quy tắc đó áp lên
những tài liệu/quy trình/skill nào khác đang tồn tại? ③ Không sửa gốc (template/skill/⛔) mà chỉ vá tài liệu
thì lỗi có tái phát không?

## 3. TRANH BIỆN ĐA AGENT (cạnh tranh — phản biện — brainstorm)

Bắt buộc với loại B/C/D. Có subagent → chạy 3 agent SONG SONG, mỗi agent một lập trường, KHÔNG cho xem bài nhau ở vòng 1:

- **Agent MINIMAL**: thiết kế giải pháp NHỎ NHẤT thỏa đúng chữ của yêu cầu. Phải nêu: các chỗ sửa, chi phí, và rủi ro tái phát.
- **Agent HOLISTIC**: thiết kế giải pháp GỐC RỄ — sửa template/quy trình/skill rồi áp nguyên khối xuống mọi tài liệu bị ảnh hưởng. Phải nêu: phạm vi ảnh hưởng, chi phí, giá trị dài hạn.
- **Agent CRITIC**: KHÔNG đề xuất — chỉ phản biện: ① yêu cầu của user có mâu thuẫn nội tại/mâu thuẫn ⛔·TEMPLATE·yêu cầu cũ không? ② có khả năng user đang hiểu nhầm điều gì không (kèm bằng chứng)? ③ 2 giải pháp kia sai/thiếu/đắt chỗ nào? ④ có phương án C nào cả hai chưa thấy?

**Vòng 2 (brainstorm chéo)**: đưa cả 3 bài cho từng agent (hoặc 1 agent tổng hợp) — mỗi lập trường phản bác
và điều chỉnh trước lập luận của bên kia; chốt bảng so sánh. Không có subagent → tự đóng 3 vai TUẦN TỰ,
viết riêng từng vai (không trộn), rồi tự tổng hợp.

## 4. ĐỀ XUẤT cho user TRƯỚC KHI LÀM

Trình: **1 khuyến nghị chính** (nói rõ chọn Minimal hay Holistic hay phương án C, vì sao) + phương án thay thế
+ chi phí/ảnh hưởng + danh sách những gì sẽ đổi trong template/skill/⛔ nếu có + câu hỏi chốt NGẮN.
**Ngoại lệ được-làm-ngay** (đủ CẢ 3): sai rõ ràng ・ phạm vi 1 chỗ ・ không sinh quy tắc → sửa luôn nhưng
vẫn báo lại phân loại sau khi sửa. Khi user đã nói rõ "cứ quyết đi" → chọn khuyến nghị chính, ghi lại căn cứ.

## 5. THỰC THI nguyên khối (sau khi chốt)

Thứ tự bắt buộc: ① cập nhật GỐC trước (TEMPLATE.md / SKILL.md / ⛔ / memory) → ② áp xuống TOÀN BỘ tài liệu
bị ảnh hưởng theo kiểu viết-lại-khối (⛔#9 — không vá rải) → ③ chạy `3-step-review` → ④ ghi sổ
(quy tắc mới vào ⛔/TEMPLATE; bài học vào memory phiên qua `update-memory`).

## Liên hệ skill khác

- `create-investigation-report` — nơi template sống; thay đổi cấu trúc tài liệu thì sửa TEMPLATE.md ở đó trước.
- `3-step-review` — review sau thực thi; ngược lại, findings mang tính hệ thống từ review cũng phải đi qua skill này thay vì vá lẻ.
