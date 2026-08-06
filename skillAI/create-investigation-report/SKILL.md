---
name: create-investigation-report
description: >
  Tạo bộ tài liệu điều tra (batch/chức năng/nhóm) chuẩn nhà theo TEMPLATE.md v4: cặp JP (nộp) + VN
  (đọc/trình bày), 2 PHẦN (đối ngoại 5 phút + kỹ thuật), 12 tiêu chí tự-chứa, code-first. Trigger khi
  user yêu cầu "điều tra batch X", "soạn báo cáo điều tra", "tạo tài liệu phán định", "làm báo cáo
  như mẫu CalcTenMinutesSensor". Đã gọi skill là phải ra được tài liệu đạt chuẩn không cần user nhắc tiêu chí.
user_invocable: true
---

# create-investigation-report — Tạo báo cáo điều tra chuẩn nhà (template v4)

**Lời hứa của skill**: user chỉ cần nêu ĐỐI TƯỢNG điều tra; mọi tiêu chí, cấu trúc, quy trình kiểm chứng
đã đóng gói ở đây. Ra tài liệu KHÔNG cần user nhắc lại quy tắc.

**Quy ước chung**: đường dẫn tính từ gốc workspace (thư mục chứa `AGENTS.md`). Trao đổi tiếng Việt;
trích tiếng Nhật nguyên văn. Template + 12 tiêu chí = `TEMPLATE.md` cùng thư mục (nguồn sự thật duy nhất
về cấu trúc — KHÔNG chép template vào chỗ khác, chỗ khác chỉ trỏ về đây).

## 0. Bootstrap (bắt buộc, trước khi làm)

1. Đọc theo thứ tự: `AGENTS.md` → `CLAUDE.md` → `memory/00_INDEX.md` (⛔ 1–11) → file `memory/NN_session_*.md` ⭐ mới nhất.
2. Kiểm repo nguồn như skill `3-step-review` mục 0-3 (đủ 5 nguồn; `git fetch` + so origin — ⛔#1; thiếu repo nào → báo rõ phần không kiểm chứng được).
3. Đọc `TEMPLATE.md` cùng thư mục.

## 1. Quy trình 6 bước

1. **Chốt phạm vi & người nhận**: đối tượng điều tra (1 batch hay nhóm), câu hỏi trung tâm (vd "có cần port không"), người nhận bản JP (mui? khách? — quyết mức nội bộ CLD-xx được phép xuất hiện), có phân tập không (nếu bộ nhiều nhóm: số hiệu đối tượng xuyên suốt giữa các tập). Tên file: JP theo kiểu 「<チーム名/主題>報告書_<phạm vi>.md」, VN `report_<chủ đề>.md`, cùng thư mục giao nộp `submit_folder/<YYYY_MM_DD>/`.
2. **Thu thập & kiểm chứng dữ kiện (code-first)**: mở file/grep trực tiếp — path phải tồn tại thật; bảng DB lấy từ hằng/schema trong code; tài liệu khảo sát chỉ dùng làm nhãn/bối cảnh (vênh → CODE THẮNG, ghi vào bảng lệch); mọi khẳng định phủ định ("không có X") phải grep nhiều dạng viết (⛔#2); nhãn 確実/*推定* ngay từ lúc ghi chép; nguồn sống (QA/Notion) ghi 参照日 + trạng thái.
3. **Dựng tài liệu theo `TEMPLATE.md`** — đúng thứ tự cấu trúc, đủ mục; JP↔VN khớp 1-1 (kết luận, con số, số bước); viết bản nào trước cũng được nhưng phải đối chiếu chéo trước khi sang bước 4.
4. **Tự kiểm 12 tiêu chí** trong `TEMPLATE.md` — từng điểm, từng file; sót điểm nào quay lại bước 3.
5. **Chạy `3-step-review`** (bắt buộc — ⛔#5, kể cả tài liệu "nhỏ"): nếu có subagent thì reviewer phải là agent ĐỘC LẬP (không phải người soạn); vá findings; review hẹp lại sau vá.
6. **Bàn giao**: tóm tắt kết luận + trạng thái kiểm (số dẫn chứng đã xác thực, findings đã vá) + việc treo; cập nhật baseline mục 4 của `3-step-review/SKILL.md`; cuối ngày chốt phiên bằng `update-memory`.

## 2. Phân việc khi có subagent

- 1 agent/nhóm tài liệu (soạn cả cặp JP+VN để giữ fidelity) + reviewer độc lập theo `3-step-review`.
- Prompt cho agent soạn PHẢI đính kèm đường dẫn `TEMPLATE.md` + phạm vi dữ kiện đã kiểm; cấm agent tự bịa dữ kiện mới không kiểm chứng.

## 3. Khi user gửi yêu cầu sửa giữa chừng

KHÔNG vá ngay. Chuyển sang skill `analyze-change-request` (phân tích → tổng quát hóa → tranh biện đa agent
→ đề xuất giải pháp tổng thể → mới thực thi). Đây là ⛔#11 — vá đuổi từng yêu cầu là lỗi quy trình.

## Liên hệ skill khác

- `analyze-change-request` — tiếp nhận mọi yêu cầu sửa/feedback (bắt buộc đi qua trước khi sửa).
- `3-step-review` — review 3 vòng sau khi soạn/sửa (bước 5).
- `update-memory` — chốt phiên.
