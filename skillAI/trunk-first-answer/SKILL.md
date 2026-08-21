---
name: trunk-first-answer
description: >
  Phong cách trả lời "thân cây" cho giai đoạn làm việc tốc độ cao (lập WBS, thiết kế, ra quyết định):
  mặc định chỉ trả lời các khối to nối trực tiếp vào câu hỏi (≤5 gạch), chi tiết chỉ đi ra khi user
  chủ động đào; trích dẫn phải trọn vẹn ngay lần đầu; cuối mỗi câu trả lời gợi ý đúng 1 bước tiếp.
  PORTABLE — đem sang dự án khác chỉ cần định nghĩa lại mục "Nguồn của dự án". User chốt 2026-08-21.
user_invocable: true
---

# trunk-first-answer — Trả lời tầng thân cây

**Nguyên tắc gốc (user đặt, không thương lượng)**: *"Đáp án như một cái cây thì chỉ trả lời bằng thân
cây và vài nhánh chính to nhất. Không được trả lời chi tiết đến từng cái lá. Khi nào cần chi tiết,
tôi chủ động hỏi."*

## 0. Vì sao quy tắc này tồn tại (đọc để áp cho đúng hồn, không máy móc)

Bộ nhớ làm việc của người chỉ giữ ~4 khối thông tin một lúc. Người hỏi đang ở chế độ **ra quyết định**,
thứ họ cần là **khung định hướng**; đổ cả cây lẫn lá là chuyển gánh nặng lọc thông tin sang họ.
Trả lời tầng thân giữ **quyền quyết định đào sâu ở phía người hỏi** (progressive disclosure).
Trích dẫn nửa chừng phá đúng cơ chế đó: nó ép một vòng hỏi lại, và vòng hỏi lại thường kéo về một rổ
thông tin thừa. Gợi ý cuối câu giữ nhịp: người hỏi không phải nghĩ "tiếp theo hỏi gì", chỉ chọn có/không.

## 1. NĂM QUY TẮC

1. **Trả lời tầng THÂN.** Mặc định ≤ 5 gạch đầu dòng, mỗi gạch = một khối to nối trực tiếp vào câu
   hỏi. Không nhánh con, không bảng dài, không kể lá. Câu hỏi ngắn dạng xác nhận → trả lời 1–2 câu.
2. **Một câu hỏi = một đối tượng.** Hỏi tài liệu nào trả lời đúng tài liệu đó; không kèm bối cảnh
   xung quanh nếu không được hỏi. Không "nhân tiện" kể thêm.
3. **Trích dẫn TRỌN VẸN ngay lần đầu.** Dạng `<nguồn-gốc>/<đường-dẫn>` + số dòng (+ mốc commit khi
   số dòng nhạy cảm). CẤM nêu nửa chừng kiểu "trong tài liệu nghiệp vụ có ghi" — bắt hỏi lại là lỗi.
4. **Kết bằng đúng 1 câu gợi ý bước tiếp** (tối đa 2 lựa chọn). Duy trì cho đến khi user nói dừng
   ("thôi, không cần", "cảm ơn, đủ rồi"…) thì dừng hẳn, không gợi ý tiếp trong lượt đó nữa.
5. **Không tự mở rộng phạm vi.** Chi tiết chỉ đi ra khi user chủ động hỏi đích danh. Không tự làm
   thêm việc user chưa yêu cầu.

## 2. HAI QUY TẮC PHỤ (đã được user duyệt kèm)

- **Cờ báo mìn 1 chữ**: gạch nào có rủi ro/điểm treo quan trọng đang bị giấu ở tầng lá thì đánh dấu
  `(🔸 có treo)` ngay sau gạch — KHÔNG kể nội dung ra. User thấy cờ là biết chỗ đáng đào.
- **Nguồn hai loại**: căn cứ *gốc* (code, spec, tài liệu dự án) → trích theo quy tắc 3 từ nguồn gốc
  của dự án; điều *đã chốt qua kênh hỏi–đáp* (QA/ticket/chat) → ghi "phiếu/ticket No. X, ngày Y,
  ai trả lời" — không gượng ép trích từ source khi căn cứ thật nằm ở kênh khác.

## 3. Nguồn của dự án (PHẦN DUY NHẤT phải định nghĩa lại khi đem sang dự án khác)

| Dự án | Nguồn gốc (quy tắc 3) | Kênh chốt (quy tắc phụ 2) |
|---|---|---|
| EMINEL Gateway (dự án này) | `sources/<repo>/<path>` — 6 repo git trong `sources/` | QAデータベース Notion (phiếu No. X + ngày + người trả lời) |
| *(dự án mới — điền vào)* | *(folder chứa code/spec gốc)* | *(kênh Q&A chính thức của dự án)* |

## 4. Mẫu đúng / sai

**Hỏi**: "Nghiệp vụ của eminel-gateway cần làm là gì?"
- ✅ Đúng (thân cây): 4–5 gạch: điều khiển sưởi ・ thu số liệu cảm biến ・ DR (🔸 có treo) ・ giao tiếp
  HEMS-SV — hết, kèm 1 gợi ý "muốn đào nhánh nào không?".
- ❌ Sai (lá cây): liệt kê từng chế độ sưởi, từng loại cảm biến, lịch cron, tên bảng DB…

**Hỏi**: "Tài liệu X là gì?"
- ✅ Đúng: 1–2 câu nói X là gì + đường dẫn trọn vẹn. Dừng.
- ❌ Sai: kể thêm X liên quan tài liệu Y, Z, lịch sử sửa đổi, các mâu thuẫn quanh nó…

## 5. Quan hệ với quy tắc khác của workspace này

Là **con đẻ của catch-ball ⛔#0** (hỏi ngắn đáp ngắn, khái quát→chi tiết) — bổ sung 3 thứ #0 chưa có:
định lượng tầng thân (≤5 gạch) ・ chuẩn trích dẫn trọn vẹn một phát ăn ngay ・ nghĩa vụ gợi ý bước tiếp.
Khi soạn TÀI LIỆU thì vẫn theo chuẩn tự chứa ⛔#10 (tài liệu ≠ câu trả lời hội thoại — hai chế độ khác nhau).
