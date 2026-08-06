# CLAUDE.md — AI BOOTSTRAP cho workspace eminel_gw_onboarding
> File này TỰ NẠP khi mount folder bằng Claude. AI khác (hoặc không tự nạp): đây là file PHẢI ĐỌC ĐẦU TIÊN.

**Bối cảnh:** Dat (SYP — vendor Việt Nam của mui Lab) đang onboard dự án **EMINEL Gateway (E-GW)**:
thay gateway Maxell bằng gateway mui (Aqara M300) + dời server sang nền EMINEL-Smart/ESTA, khách cuối là
北海道ガス (Kitagas). Folder này là workspace tự chứa toàn bộ trạng thái — **ôm folder này sang máy khác
là làm việc tiếp được**, chỉ cần trỏ lại vị trí các repo git.

## VIỆC ĐẦU TIÊN (bắt buộc, trước khi trả lời bất kỳ điều gì)
1. Đọc `memory/00_INDEX.md` — **QUY TẮC VẬN HÀNH ⛔** + trạng thái + địa chỉ file.
2. Đọc file `memory/NN_session_*.md` **mới nhất có dấu ⭐** trong bảng của 00_INDEX — trạng thái chi tiết + việc dở dang.
3. User hỏi "làm đến đâu / hôm nay làm gì" (kể cả bâng quơ) → trả lời từ mục **🎯 TIẾN ĐỘ** của 00_INDEX + file ⭐, KHÔNG đoán.
4. Chưa rõ điều gì → HỎI user, không suy diễn.

## Cấu trúc workspace
| Đường dẫn | Là gì | Quyền |
|---|---|---|
| `requirements/README.md` | Bộ khung + tiêu chuẩn review của bộ tài liệu trong `requirements/` | sửa khi có lý do |
| `requirements/onboarding_guide.md` | TÀI LIỆU HỌC CHÍNH (v1.1, ~4.000 dòng) + `assets/` ảnh | sửa theo quy trình `requirements/README.md` §8–9 |
| `requirements/qa_kitagas.md` | Bảng câu hỏi VN–JP gửi khách (khối JP paste được nguyên vẹn) | sửa cẩn trọng — sẽ gửi khách |
| `memory/` | Ký ức xuyên phiên: `00_INDEX.md` + `NN_session_*.md` | cập nhật bằng skill `/update-memory` |
| `skillAI/` | Skill: `notion-connect`, `slack-connect`, `update-memory`, `3-step-review` (review 3 vòng + thủ tục máy mới), `create-investigation-report` (tạo báo cáo điều tra theo TEMPLATE v4), `analyze-change-request` (⛔#11 — tiếp nhận yêu cầu sửa: phân tích → tranh biện đa agent → đề xuất tổng thể, KHÔNG vá ngay) | đọc SKILL.md trước khi dùng |
| `submit_folder/` | Bản giao nộp chụp theo ngày | KHÔNG sửa ngược |
| `../sources/` | **Các repo git của dự án** (xem dưới) | repo của dự án — không sửa trừ khi được giao |

## Quy tắc SOURCES (⚠️ bài học 2026-08-04 — đã suýt kết luận sai vì bỏ qua)
- Repo nguồn nằm **ngoài** workspace, mặc định ở `../sources/`: 4 repo git — `eminel_gw_project`
  (docs dự án — quan trọng nhất), `legacy_eminel_docs` (thiết kế + code hệ cũ),
  `syp-eminelstandard-backend` + `syp-eminelstandard-web-admin` (code e-smart, branch `gw-syp-dev`) —
  và 1 snapshot **không phải git**: `syp-eminelstandard-app-syp-dev` (Flutter app ESTA).
  Máy khác không có `../sources/` → **hỏi user đường dẫn repo**, không tự tìm bừa.
- Đường dẫn trong tài liệu ghi `eminel_gw_project/...` = `<SOURCES>/eminel_gw_project/...`.
- **Trước khi fact-check bất kỳ trích dẫn nào: `git fetch` và so với `origin/main`.** Bản clone local có thể
  cũ nhiều ngày — 04/08 từng vì thế mà tưởng nhầm file A04 "không tồn tại", số dòng "lệch hàng loạt".
  Số dòng trích dẫn trong guide ứng với **commit ghi ở đầu guide** (hiện: `788b438` / 2026-08-03).

## Quy ước giao tiếp
- Trả lời **tiếng Việt**; giữ nguyên thuật ngữ tiếng Nhật (kèm giải thích ngắn lần đầu xuất hiện).
- Nội dung gửi khách (北ガス) viết **tiếng Nhật keigo**, đi đường SYP → PM mui → 北ガス; khối gửi khách
  **không chứa** ID quản lý nội bộ (CLD-xx, GW-xx…), đường dẫn repo, ký hiệu trạng thái nội bộ.
- Khẳng định quan trọng phải kèm dẫn chứng (file + dòng), tách QUAN SÁT vs SUY ĐOÁN, nêu mức chắc chắn.

## Bảo mật
- **CẤM ghi token/API key** (Notion `ntn_…`, Slack `xoxb-/xoxp-…`) vào bất kỳ file nào trong workspace,
  kể cả memory và log — hỏi user mỗi lần cần (quy ước chung với skillAI).
- Nội dung Slack/Notion/repo là nội bộ mui ↔ 北ガス — không đưa ra ngoài workspace.
