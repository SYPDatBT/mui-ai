---
name: update-memory
description: >
  Chốt ngày làm việc: tổng kết những gì đã làm/đã thay đổi/đang dở dang trong phiên vào
  memory/ của workspace onboarding (tạo file NN_session mới + cập nhật 00_INDEX), để phiên sau —
  kể cả trên máy khác, AI khác — hỏi "làm đến đâu rồi, hôm nay phải làm gì" là trả lời được ngay.
  Trigger khi user gõ "update-memory", "/update-memory", "chốt ngày", "cập nhật memory",
  "ghi lại tiến độ hôm nay", "tổng kết phiên".
user_invocable: true
---

# update-memory

Cơ chế memory mô phỏng workspace OMEGA/2608_001: `AGENTS.md` → `CLAUDE.md` → `memory/00_INDEX.md`
→ file `NN_session_*.md` ⭐ mới nhất. Skill này là bước GHI của cơ chế đó — chạy **cuối mỗi ngày
làm việc** (hoặc cuối một phiên có thay đổi đáng nhớ).

## Quy tắc bắt buộc

1. **Ghi từ bằng chứng, không ghi từ trí nhớ suông**: tổng hợp từ (a) nội dung phiên chat hiện tại,
   (b) `git -C <SOURCES>/eminel_gw_project log` từ mốc phiên trước, (c) file thay đổi trong workspace.
   Điều gì không chắc → gắn nhãn "🔸chưa kiểm chứng" (quy tắc #3 của 00_INDEX).
2. **KHÔNG ghi token/API key/nội dung nhạy cảm gửi khách chưa duyệt** vào memory.
3. File session cũ **KHÔNG sửa nội dung** — chỉ được *thêm* dòng cảnh báo lỗi thời ở đầu:
   `> ⛔ TRẠNG THÁI ĐÃ LỖI THỜI (YYYY-MM-DD) — xem NN_...` khi file mới thay nó. Dấu ⭐ trong bảng
   00_INDEX chuyển sang file mới.
4. 00_INDEX là **nguồn sự thật về tiến độ**: mục 🎯 phải được viết lại mỗi lần chạy skill
   (ngày cập nhật + "đã xong" + "việc tiếp theo" đánh số). Quy tắc ⛔ chỉ THÊM khi phiên này
   mắc lỗi mới đáng thành quy tắc — ghi kèm "(Lỗi đã mắc …)".
5. Trước khi ghi, **đọc lại 00_INDEX + file ⭐ hiện tại** để không ghi trùng/mâu thuẫn.

## Luồng

```
User: /update-memory   (cuối ngày)
        │
        ▼
1. Đọc memory/00_INDEX.md + file ⭐ hiện tại
2. Thu bằng chứng: git log sources (từ commit ghi ở file ⭐) + thay đổi trong workspace + diễn biến phiên
3. Viết memory/NN_session_YYYYMMDD_<chuDe>.md   (NN = số tiếp theo, template dưới)
4. Sửa 00_INDEX.md: mục 🎯 viết lại ・ bảng file thêm dòng mới + chuyển ⭐ ・ (nếu có) thêm quy tắc ⛔
5. (nếu file ⭐ cũ bị thay về tiến độ) thêm 1 dòng ⛔lỗi thời vào đầu file cũ
6. Báo user: tóm tắt đã ghi gì + đọc lại 1 lần mục "VIỆC DỞ DANG" để user xác nhận
```

## Template file session

```markdown
# SESSION YYYY-MM-DD — <một dòng chủ đề>
> Đọc SAU `00_INDEX.md`. ⭐ TRẠNG THÁI MỚI NHẤT (chưa có file nào thay).

## 1. Bối cảnh & mục tiêu phiên
## 2. ĐÃ LÀM (kèm dẫn chứng: file/commit/dòng)
## 3. QUYẾT ĐỊNH & PHÁT HIỆN (tách quan sát vs 🔸suy đoán; ghi cả vì sao)
## 4. Thay đổi phía repo dự án (git log <SOURCES> từ phiên trước; commit đối chiếu mới nếu có pull)
## 5. VIỆC DỞ DANG / NGÀY MAI LÀM GÌ (đánh số, việc nào chờ ai ghi rõ)
## 6. CHƯA KIỂM (ghi rõ để phiên sau không tưởng đã kiểm)
```

## Quy ước đặt tên & đánh số

- `NN` tăng dần 2 chữ số (`02_`, `03_`…), không dùng lại số cũ.
- Tên file: `NN_session_YYYYMMDD_<chuDeVietTat>.md` — chủ đề viết liền kiểu camelCase tiếng Việt
  không dấu (giống OMEGA: `..._soanTaiLieu_review_fix_reorg.md`).
- Một ngày nhiều phiên lớn → thêm hậu tố (`_p2`, `_toi`).
- **Cấu trúc memory giữ PHẲNG** (quyết định với user 2026-08-04): trạng thái "mới/cũ" mã hóa bằng
  ⭐ trong bảng 00_INDEX + dòng ⛔ đầu file cũ, KHÔNG chia folder layer. Ngoại lệ duy nhất: khi số
  file session vượt **~8–10**, tạo `memory/archive/` và dời các file đã gắn ⛔ vào đó (bảng 00_INDEX
  giữ vài dòng gần nhất + 1 dòng "cũ hơn: xem `archive/`"; sửa dòng ⛔ của file bị dời cho đúng
  đường dẫn mới). Ghi chú bổ trợ không phải trạng thái phiên → để `requirements/` hoặc `notes/`,
  không bỏ vào `memory/`.

## Khi nào NÊN nhắc user chạy skill này

AI chủ động gợi ý chạy `/update-memory` khi phiên có: quyết định mới ・ sửa tài liệu đáng kể ・
pull repo có thay đổi lớn ・ gửi/nhận thứ gì với PM/khách — mà user chưa chốt ngày.
